"""
Subscription billing service with Stripe and explicit development mock mode.
"""
import logging
import os
import uuid
from dataclasses import dataclass
from typing import Dict, Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

try:
    import stripe
except Exception:
    stripe = None

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Plan:
    key: str
    name: str
    monthly_price_usd: int
    features: list[str]


class BillingService:
    def __init__(self):
        self.stripe_secret_key = os.getenv("STRIPE_SECRET_KEY", "").strip()
        self.stripe_publishable_key = os.getenv("STRIPE_PUBLISHABLE_KEY", "").strip()

        # Keep checkout testable by default in development, but fail closed in production.
        default_mock = "false" if os.getenv("APP_ENV", "development").lower() == "production" else "true"
        self.mock_mode = os.getenv("BILLING_MOCK_MODE", default_mock).lower() == "true"

        self.plan_aliases = {
            "starter": "starter",
            "growth": "professional",
            "professional": "professional",
            "enterprise": "enterprise",
        }

        self.plan_price_ids = {
            "starter": os.getenv("STRIPE_PRICE_ID_STARTER", os.getenv("STRIPE_PRICE_STARTER", "")).strip(),
            "professional": os.getenv(
                "STRIPE_PRICE_ID_PROFESSIONAL",
                os.getenv("STRIPE_PRICE_GROWTH", ""),
            ).strip(),
            "enterprise": os.getenv(
                "STRIPE_PRICE_ID_ENTERPRISE",
                os.getenv("STRIPE_PRICE_ENTERPRISE", ""),
            ).strip(),
        }

        self.catalog = {
            "starter": Plan(
                key="starter",
                name="Starter",
                monthly_price_usd=49,
                features=["AI chat", "Route optimization", "Basic analytics"],
            ),
            "professional": Plan(
                key="professional",
                name="Professional",
                monthly_price_usd=149,
                features=["Everything in Starter", "Auto-dispatch", "Predictive maintenance"],
            ),
            "enterprise": Plan(
                key="enterprise",
                name="Enterprise",
                monthly_price_usd=399,
                features=["Everything in Growth", "Priority support", "Custom integrations"],
            ),
        }

        if stripe is not None and self.stripe_secret_key:
            stripe.api_key = self.stripe_secret_key
        elif not self.mock_mode:
            logger.error("Stripe is not configured and billing mock mode is disabled")

    def _is_stripe_ready(self) -> bool:
        return stripe is not None and bool(self.stripe_secret_key)

    def get_public_status(self) -> Dict[str, Any]:
        return {
            "stripe_ready": self._is_stripe_ready(),
            "mock_mode": self.mock_mode,
            "publishable_key_configured": bool(self.stripe_publishable_key),
            "plans": [plan.__dict__ for plan in self.catalog.values()],
        }

    def create_checkout_session(
        self,
        plan_key: str,
        customer_email: str,
        success_url: str,
        cancel_url: str,
    ) -> Dict[str, Any]:
        normalized_plan_key = self.plan_aliases.get(plan_key, plan_key)

        if normalized_plan_key not in self.catalog:
            raise ValueError("Unknown plan")

        if self._is_stripe_ready() and self.plan_price_ids.get(normalized_plan_key):
            session = stripe.checkout.Session.create(
                mode="subscription",
                customer_email=customer_email,
                line_items=[{"price": self.plan_price_ids[normalized_plan_key], "quantity": 1}],
                success_url=success_url,
                cancel_url=cancel_url,
                allow_promotion_codes=True,
            )
            return {
                "checkout_url": session.url,
                "session_id": session.id,
                "provider": "stripe",
                "mock": False,
            }

        if not self.mock_mode:
            raise RuntimeError("Stripe checkout is not configured for this plan")

        token = str(uuid.uuid4())
        split_url = urlsplit(success_url)
        query = dict(parse_qsl(split_url.query, keep_blank_values=True))
        query.update(
            {
                "mock_checkout": "1",
                "session_id": token,
                "plan": normalized_plan_key,
            }
        )
        mock_url = urlunsplit(
            (
                split_url.scheme,
                split_url.netloc,
                split_url.path,
                urlencode(query),
                split_url.fragment,
            )
        )
        return {
            "checkout_url": mock_url,
            "session_id": token,
            "provider": "mock",
            "mock": True,
        }

    def create_portal_session(self, customer_id: str, return_url: str) -> Dict[str, Any]:
        if self._is_stripe_ready():
            session = stripe.billing_portal.Session.create(
                customer=customer_id,
                return_url=return_url,
            )
            return {
                "portal_url": session.url,
                "provider": "stripe",
                "mock": False,
            }

        if not self.mock_mode:
            raise RuntimeError("Stripe billing portal is not configured")

        return {
            "portal_url": return_url,
            "provider": "mock",
            "mock": True,
        }


billing_service = BillingService()
