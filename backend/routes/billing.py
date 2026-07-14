import os
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Header, Request
from pydantic import BaseModel, EmailStr, Field

from backend.database.db import SessionLocal
from backend.database.models import Subscription
from backend.services.billing_service import billing_service

try:
    import stripe
except Exception:
    stripe = None

router = APIRouter(prefix="/api/billing", tags=["Billing"])


class CheckoutRequest(BaseModel):
    plan: str = Field(min_length=3, max_length=32)
    customer_email: EmailStr
    success_url: str = Field(min_length=8)
    cancel_url: str = Field(min_length=8)


class PortalRequest(BaseModel):
    customer_id: str = Field(min_length=3)
    return_url: str = Field(min_length=8)


@router.get("/plans")
def get_plans():
    status = billing_service.get_public_status()
    return {
        "status": "success",
        "billing": status,
    }


@router.post("/checkout-session")
def create_checkout_session(payload: CheckoutRequest):
    db = SessionLocal()
    try:
        result = billing_service.create_checkout_session(
            plan_key=payload.plan.lower(),
            customer_email=payload.customer_email,
            success_url=payload.success_url,
            cancel_url=payload.cancel_url,
        )

        existing = (
            db.query(Subscription)
            .filter(Subscription.customer_email == payload.customer_email)
            .order_by(Subscription.id.desc())
            .first()
        )

        if existing is None:
            existing = Subscription(
                customer_email=payload.customer_email,
                provider=result.get("provider", "stripe"),
                plan_key=payload.plan.lower(),
                status="pending",
            )
            db.add(existing)
        else:
            existing.provider = result.get("provider", "stripe")
            existing.plan_key = payload.plan.lower()
            existing.status = "pending"

        db.commit()

        return {
            "status": "success",
            "checkout": result,
        }
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Unable to create checkout session: {exc}") from exc
    finally:
        db.close()


@router.post("/portal-session")
def create_portal_session(payload: PortalRequest):
    try:
        result = billing_service.create_portal_session(
            customer_id=payload.customer_id,
            return_url=payload.return_url,
        )
        return {
            "status": "success",
            "portal": result,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Unable to create billing portal session: {exc}") from exc


@router.get("/subscription-status")
def get_subscription_status(email: EmailStr):
    db = SessionLocal()
    try:
        subscription = (
            db.query(Subscription)
            .filter(Subscription.customer_email == email)
            .order_by(Subscription.id.desc())
            .first()
        )

        if subscription is None:
            return {"status": "success", "subscription": None}

        return {
            "status": "success",
            "subscription": {
                "email": subscription.customer_email,
                "plan": subscription.plan_key,
                "state": subscription.status,
                "provider": subscription.provider,
                "current_period_end": subscription.current_period_end.isoformat() if subscription.current_period_end else None,
                "cancel_at_period_end": subscription.cancel_at_period_end,
            },
        }
    finally:
        db.close()


@router.post("/webhook")
async def billing_webhook(request: Request, stripe_signature: str = Header(default="", alias="stripe-signature")):
    payload = await request.body()

    event = None
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET", "").strip()
    if stripe is not None and stripe_signature and webhook_secret:
        try:
            event = stripe.Webhook.construct_event(payload=payload, sig_header=stripe_signature, secret=webhook_secret)
        except Exception as exc:
            raise HTTPException(status_code=400, detail=f"Invalid webhook signature: {exc}") from exc
    elif stripe is not None:
        try:
            event = stripe.Event.construct_from(await request.json(), stripe.api_key)
        except Exception as exc:
            raise HTTPException(status_code=400, detail=f"Invalid webhook payload: {exc}") from exc
    else:
        return {"status": "ignored", "reason": "stripe-unavailable"}

    db = SessionLocal()
    try:
        event_type = event.get("type") if isinstance(event, dict) else getattr(event, "type", "")
        data_object = event.get("data", {}).get("object", {}) if isinstance(event, dict) else event.data.object

        if event_type in {"customer.subscription.created", "customer.subscription.updated", "customer.subscription.deleted"}:
            customer_id = data_object.get("customer")
            subscription_id = data_object.get("id")
            status = data_object.get("status", "unknown")
            cancel_at_period_end = bool(data_object.get("cancel_at_period_end", False))
            plan_key = None

            items = data_object.get("items", {}).get("data", [])
            if items:
                plan_key = items[0].get("price", {}).get("nickname") or items[0].get("price", {}).get("id")

            period_end = data_object.get("current_period_end")
            period_end_dt = datetime.fromtimestamp(period_end, tz=timezone.utc) if period_end else None

            subscription = (
                db.query(Subscription)
                .filter(Subscription.provider_subscription_id == subscription_id)
                .first()
            )

            if subscription is None:
                subscription = (
                    db.query(Subscription)
                    .filter(Subscription.provider_customer_id == customer_id)
                    .order_by(Subscription.id.desc())
                    .first()
                )

            if subscription is None:
                subscription = Subscription(
                    customer_email=data_object.get("customer_email", "unknown@unknown"),
                    provider="stripe",
                    plan_key=plan_key or "unknown",
                    status=status,
                )
                db.add(subscription)

            subscription.provider = "stripe"
            subscription.provider_customer_id = customer_id
            subscription.provider_subscription_id = subscription_id
            if plan_key:
                subscription.plan_key = plan_key
            subscription.status = status
            subscription.current_period_end = period_end_dt
            subscription.cancel_at_period_end = cancel_at_period_end
            db.commit()

        return {"status": "success"}
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Webhook processing failed: {exc}") from exc
    finally:
        db.close()
