import { useState } from 'react';
import './Pricing.css';
import { API_BASE_URL } from '../lib/api';

const PLANS = [
  {
    id: 'starter',
    name: 'Starter',
    price: 49,
    tagline: 'Perfect for small operations',
    features: [
      'Up to 3 drivers',
      'AI route optimization',
      'Dispatch dashboard',
      'DOT compliance tools',
      'Email support',
    ],
    highlight: false,
  },
  {
    id: 'professional',
    name: 'Professional',
    price: 149,
    tagline: 'The full AI suite for growing fleets',
    features: [
      'Up to 15 drivers',
      'Everything in Starter',
      'AI driver analytics',
      'Predictive maintenance',
      'Operations center',
      'Priority support',
    ],
    highlight: true,
  },
  {
    id: 'enterprise',
    name: 'Enterprise',
    price: 399,
    tagline: 'Unlimited scale with white-glove service',
    features: [
      'Unlimited drivers',
      'Everything in Professional',
      'Dedicated onboarding',
      'Custom integrations',
      'SLA guarantee',
      'Phone & chat support',
    ],
    highlight: false,
  },
];

function Pricing({ onSubscribed }) {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(null);
  const [error, setError] = useState('');

  const handleSubscribe = async (planId) => {
    if (!email.trim()) {
      setError('Please enter your email address before subscribing.');
      return;
    }
    setError('');
    setLoading(planId);

    try {
      const successUrl = `${window.location.origin}?subscribed=true&plan=${planId}&email=${encodeURIComponent(email)}`;
      const cancelUrl = window.location.href;

      const subscriptionsRes = await fetch(`${API_BASE_URL}/subscriptions/checkout`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          plan: planId,
          email: email.trim(),
          success_url: successUrl,
          cancel_url: cancelUrl,
        }),
      });
      const subscriptionsData = await subscriptionsRes.json().catch(() => ({}));
      const subscriptionsUrl = subscriptionsData?.url || subscriptionsData?.checkout_url;

      const needsBillingFallback =
        !subscriptionsRes.ok ||
        !subscriptionsUrl ||
        subscriptionsUrl.includes('checkout.stripe.com/pay/cs_test_mock_');

      if (!needsBillingFallback) {
        window.location.href = subscriptionsUrl;
        return;
      }

      const billingRes = await fetch(`${API_BASE_URL}/api/billing/checkout-session`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          plan: planId,
          customer_email: email.trim(),
          success_url: successUrl,
          cancel_url: cancelUrl,
        }),
      });
      const billingData = await billingRes.json().catch(() => ({}));
      const billingUrl = billingData?.checkout?.checkout_url || billingData?.checkout_url || billingData?.url;

      if (!billingRes.ok || !billingUrl) {
        throw new Error(
          billingData?.detail ||
          subscriptionsData?.detail ||
          'Failed to start checkout.'
        );
      }

      window.location.href = billingUrl;
    } catch (err) {
      setError(err.message || 'Something went wrong. Please try again.');
      setLoading(null);
    }
  };

  return (
    <div className="pricing-wrap">
      <div className="pricing-header">
        <h1>Start your Highway Pilot subscription</h1>
        <p className="pricing-sub">
          AI-powered logistics automation. Cancel any time. No contracts.
        </p>
      </div>

      <div className="pricing-email-row">
        <input
          type="email"
          className="pricing-email-input"
          placeholder="your@email.com"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
      </div>

      {error && <p className="pricing-error">{error}</p>}

      <div className="pricing-cards">
        {PLANS.map((plan) => (
          <div
            key={plan.id}
            className={`pricing-card${plan.highlight ? ' pricing-card--highlight' : ''}`}
          >
            {plan.highlight && <span className="pricing-badge">Most Popular</span>}
            <h2 className="pricing-plan-name">{plan.name}</h2>
            <p className="pricing-tagline">{plan.tagline}</p>
            <div className="pricing-amount">
              <span className="pricing-dollar">$</span>
              <span className="pricing-number">{plan.price}</span>
              <span className="pricing-period">/mo</span>
            </div>
            <ul className="pricing-features">
              {plan.features.map((f) => (
                <li key={f}>
                  <span className="pricing-check">✓</span> {f}
                </li>
              ))}
            </ul>
            <button
              className={`pricing-btn${plan.highlight ? ' pricing-btn--primary' : ''}`}
              onClick={() => handleSubscribe(plan.id)}
              disabled={loading !== null}
            >
              {loading === plan.id ? 'Redirecting…' : `Subscribe — $${plan.price}/mo`}
            </button>
          </div>
        ))}
      </div>

      <p className="pricing-secure">
        🔒 Payments processed securely by Stripe. SSL encrypted.
      </p>
    </div>
  );
}

export default Pricing;
