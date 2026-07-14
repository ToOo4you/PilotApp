import logging
import os
from datetime import datetime, timezone

import stripe
from fastapi import APIRouter, Header, HTTPException, Request
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import text

from backend.database.db import SessionLocal
from backend.database.models import BillingSupportRequest, Subscription

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Pricing plans — price IDs come from environment variables so they can be
# configured for both test and live Stripe modes without code changes.
# ---------------------------------------------------------------------------

PLANS = {
    "starter": {
        "name": "Starter",
        "price_usd": 49,
        "description": "Up to 3 drivers · Core dispatch & routing",
        "price_id_env": "STRIPE_PRICE_ID_STARTER",
    },
    "professional": {
        "name": "Professional",
        "price_usd": 149,
        "description": "Up to 15 drivers · Full AI suite · Priority support",
        "price_id_env": "STRIPE_PRICE_ID_PROFESSIONAL",
    },
    "enterprise": {
        "name": "Enterprise",
        "price_usd": 399,
        "description": "Unlimited drivers · Dedicated onboarding · SLA",
        "price_id_env": "STRIPE_PRICE_ID_ENTERPRISE",
    },
}


def _stripe_client() -> stripe.StripeClient:
    secret_key = os.getenv("STRIPE_SECRET_KEY", "")
    if not secret_key:
        raise HTTPException(
            status_code=503,
            detail="Payment system not configured. Set STRIPE_SECRET_KEY.",
        )
    return stripe.StripeClient(secret_key)


def _price_id(plan: str) -> str:
    env_var = PLANS[plan]["price_id_env"]
    price_id = os.getenv(env_var, "")
    if not price_id:
        raise HTTPException(
            status_code=503,
            detail=f"Price ID for plan '{plan}' not configured. Set {env_var}.",
        )
    return price_id


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------


class CheckoutRequest(BaseModel):
    plan: str
    email: EmailStr
    success_url: str
    cancel_url: str


class BillingSupportRequestBody(BaseModel):
    email: EmailStr
    transaction_ids: list[str] = Field(min_length=1, max_length=3)
    transaction_dates: list[str] = Field(min_length=1, max_length=3)
    transaction_statuses: list[str] = Field(min_length=1, max_length=3)
    issue: str = Field(min_length=10, max_length=2000)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get("/plans")
def list_plans():
    """Return all available subscription plans (no auth required)."""
    return [
        {
            "id": plan_id,
            "name": info["name"],
            "price_usd": info["price_usd"],
            "description": info["description"],
        }
        for plan_id, info in PLANS.items()
    ]


@router.post("/checkout")
def create_checkout_session(body: CheckoutRequest):
    """
    Create a Stripe Checkout session for the requested plan.
    Returns { url } which the frontend redirects to.
    """
    plan = body.plan.lower()
    if plan not in PLANS:
        raise HTTPException(status_code=400, detail=f"Unknown plan '{plan}'.")

    client = _stripe_client()
    price_id = _price_id(plan)

    try:
        session = client.checkout.sessions.create(
            params={
                "mode": "subscription",
                "customer_email": body.email,
                "line_items": [{"price": price_id, "quantity": 1}],
                "success_url": body.success_url,
                "cancel_url": body.cancel_url,
                "metadata": {"plan": plan, "email": body.email},
                "subscription_data": {"metadata": {"plan": plan, "email": body.email}},
            }
        )
    except stripe.StripeError as exc:
        logger.exception("Stripe checkout session creation failed: %s", exc)
        raise HTTPException(status_code=502, detail="Payment provider error. Please try again.")

    return {"url": session.url}


@router.post("/webhook")
async def stripe_webhook(request: Request, stripe_signature: str = Header(None)):
    """
    Handle Stripe webhook events to activate/cancel subscriptions.
    Configure the webhook endpoint in your Stripe Dashboard to send:
      - checkout.session.completed
      - invoice.paid
      - invoice.payment_failed
      - customer.subscription.deleted
    """
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    if not webhook_secret:
        raise HTTPException(status_code=503, detail="Webhook secret not configured.")

    payload = await request.body()
    try:
        event = stripe.Webhook.construct_event(
            payload, stripe_signature, webhook_secret
        )
    except stripe.errors.SignatureVerificationError as exc:
        logger.warning("Stripe webhook signature verification failed: %s", exc)
        raise HTTPException(status_code=400, detail="Invalid webhook signature.")
    except Exception as exc:
        logger.exception("Webhook payload parse failed: %s", exc)
        raise HTTPException(status_code=400, detail="Invalid webhook payload.")

    _handle_event(event)
    return {"received": True}


def _handle_event(event):
    db = SessionLocal()
    try:
        event_type = event["type"]
        data = event["data"]["object"]

        if event_type == "checkout.session.completed":
            email = data.get("customer_email") or (data.get("metadata") or {}).get("email", "")
            plan = (data.get("metadata") or {}).get("plan", "starter")
            customer_id = data.get("customer")
            subscription_id = data.get("subscription")

            sub = db.query(Subscription).filter(Subscription.email == email).first()
            if sub is None:
                sub = Subscription(email=email)
                db.add(sub)

            sub.plan = plan
            sub.status = "active"
            sub.stripe_customer_id = customer_id
            sub.stripe_subscription_id = subscription_id
            sub.updated_at = datetime.now(timezone.utc)
            db.commit()
            logger.info("Subscription activated: email=%s plan=%s", email, plan)

        elif event_type == "invoice.paid":
            sub_id = data.get("subscription")
            if sub_id:
                sub = db.query(Subscription).filter(
                    Subscription.stripe_subscription_id == sub_id
                ).first()
                if sub:
                    sub.status = "active"
                    sub.updated_at = datetime.now(timezone.utc)
                    # Store current period end from the subscription object if available
                    period_end = data.get("lines", {}).get("data", [{}])[0].get(
                        "period", {}
                    ).get("end")
                    if period_end:
                        sub.current_period_end = datetime.fromtimestamp(
                            period_end, tz=timezone.utc
                        )
                    db.commit()
                    logger.info("Invoice paid, subscription renewed: %s", sub_id)

        elif event_type == "invoice.payment_failed":
            sub_id = data.get("subscription")
            if sub_id:
                sub = db.query(Subscription).filter(
                    Subscription.stripe_subscription_id == sub_id
                ).first()
                if sub:
                    sub.status = "past_due"
                    sub.updated_at = datetime.now(timezone.utc)
                    db.commit()
                    logger.warning("Invoice payment failed for subscription: %s", sub_id)

        elif event_type == "customer.subscription.deleted":
            sub_id = data.get("id")
            if sub_id:
                sub = db.query(Subscription).filter(
                    Subscription.stripe_subscription_id == sub_id
                ).first()
                if sub:
                    sub.status = "cancelled"
                    sub.updated_at = datetime.now(timezone.utc)
                    db.commit()
                    logger.info("Subscription cancelled: %s", sub_id)

    except Exception as exc:
        db.rollback()
        logger.exception("Error handling Stripe event %s: %s", event.get("type"), exc)
    finally:
        db.close()


@router.get("/status")
def get_subscription_status(email: str):
    """Return the subscription status for the given email address."""
    if not email:
        raise HTTPException(status_code=400, detail="email query parameter is required.")

    db = SessionLocal()
    try:
        normalized_email = email.strip().lower()
        rows = db.execute(text("SELECT * FROM subscriptions")).mappings().all()

        for row in rows:
            row_email = (row.get("email") or row.get("customer_email") or "").strip().lower()
            if row_email != normalized_email:
                continue

            status_value = (row.get("status") or "inactive").strip().lower()
            plan_value = row.get("plan") or row.get("plan_key")
            period_end = row.get("current_period_end")

            return {
                "subscribed": status_value == "active",
                "plan": plan_value,
                "status": status_value,
                "current_period_end": period_end.isoformat() if period_end else None,
            }

        return {"subscribed": False, "plan": None, "status": "inactive"}
    finally:
        db.close()


@router.post("/support", status_code=201)
def create_billing_support_request(body: BillingSupportRequestBody):
    """Create a support case for duplicate or unresolved billing charges."""
    if not (
        len(body.transaction_ids)
        == len(body.transaction_dates)
        == len(body.transaction_statuses)
    ):
        raise HTTPException(
            status_code=400,
            detail="Provide one date and status for each transaction ID.",
        )
    if (
        any(not item.strip() for item in body.transaction_ids)
        or any(not item.strip() for item in body.transaction_dates)
        or any(not item.strip() for item in body.transaction_statuses)
    ):
        raise HTTPException(
            status_code=400,
            detail="Each transaction must include an ID, date, and status.",
        )

    statuses = {"pending", "completed", "unknown"}
    normalized_statuses = [status.strip().lower() for status in body.transaction_statuses]
    if any(status not in statuses for status in normalized_statuses):
        raise HTTPException(
            status_code=400,
            detail="Transaction status must be pending, completed, or unknown.",
        )

    db = SessionLocal()
    try:
        support_request = BillingSupportRequest(
            email=body.email,
            transaction_ids=[item.strip() for item in body.transaction_ids],
            transaction_dates=[item.strip() for item in body.transaction_dates],
            transaction_statuses=normalized_statuses,
            issue=body.issue.strip(),
        )
        db.add(support_request)
        db.commit()
        db.refresh(support_request)
        return {
            "case_id": f"BILL-{support_request.id:06d}",
            "status": support_request.status,
            "message": "Your billing case was received. Support will review the transaction IDs provided.",
        }
    finally:
        db.close()
