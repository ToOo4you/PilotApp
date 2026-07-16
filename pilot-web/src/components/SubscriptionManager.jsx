import React, { useEffect, useMemo, useState } from 'react';
import { API_BASE_URL } from '../lib/api';
import './SubscriptionManager.css';

const DEFAULT_PLANS = [
  {
    id: 'starter',
    name: 'Starter',
    price_usd: 49,
    description: 'Up to 3 drivers · Core dispatch & routing',
    features: ['AI chat', 'Route optimization', 'Basic analytics']
  },
  {
    id: 'professional',
    name: 'Professional',
    price_usd: 149,
    description: 'Up to 15 drivers · Full AI suite · Priority support',
    features: ['Everything in Starter', 'Auto-dispatch', 'Predictive maintenance']
  },
  {
    id: 'enterprise',
    name: 'Enterprise',
    price_usd: 399,
    description: 'Unlimited drivers · Dedicated onboarding · SLA',
    features: ['Everything in Growth', 'Priority support', 'Custom integrations']
  }
];

const SubscriptionManager = () => {
  const [email, setEmail] = useState('');
  const [selectedPlan, setSelectedPlan] = useState('professional');
  const [plans, setPlans] = useState(DEFAULT_PLANS);
  const [plansLoaded, setPlansLoaded] = useState(false);
  const [subscriptionState, setSubscriptionState] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    const loadPlans = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/subscriptions/plans`);
        if (!response.ok) {
          return;
        }
        const data = await response.json();
        if (Array.isArray(data) && data.length > 0) {
          setPlans(data);
          setPlansLoaded(true);
        }
      } catch (err) {
        console.error('Unable to fetch billing plans', err);
      }
    };

    loadPlans();
  }, []);

  const selectedPlanInfo = useMemo(
    () => plans.find((plan) => plan.id === selectedPlan),
    [plans, selectedPlan]
  );

  const onSubscribe = async () => {
    setError('');
    if (!email.trim()) {
      setError('Please enter a valid work email.');
      return;
    }

    try {
      setLoading(true);
      const currentUrl = window.location.origin;
      const successUrl = `${currentUrl}?subscribed=true&plan=${selectedPlan}&email=${encodeURIComponent(email.trim())}`;
      const subscriptionsResponse = await fetch(`${API_BASE_URL}/subscriptions/checkout`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          plan: selectedPlan,
          email: email.trim(),
          success_url: successUrl,
          cancel_url: window.location.href
        })
      });
      const subscriptionsData = await subscriptionsResponse.json().catch(() => ({}));
      const subscriptionsUrl = subscriptionsData?.url || subscriptionsData?.checkout_url;

      const needsBillingFallback =
        !subscriptionsResponse.ok ||
        !subscriptionsUrl ||
        subscriptionsUrl.includes('checkout.stripe.com/pay/cs_test_mock_');

      if (!needsBillingFallback) {
        window.location.assign(subscriptionsUrl);
        return;
      }

      const billingResponse = await fetch(`${API_BASE_URL}/api/billing/checkout-session`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          plan: selectedPlan,
          customer_email: email.trim(),
          success_url: successUrl,
          cancel_url: window.location.href,
        }),
      });

      const billingData = await billingResponse.json().catch(() => ({}));
      const billingUrl = billingData?.checkout?.checkout_url || billingData?.checkout_url || billingData?.url;

      if (!billingResponse.ok || !billingUrl) {
        throw new Error(
          billingData?.detail ||
          subscriptionsData?.detail ||
          'Unable to create subscription checkout session.'
        );
      }

      window.location.assign(billingUrl);
    } catch (err) {
      setError(err.message || 'Subscription checkout failed.');
    } finally {
      setLoading(false);
    }
  };

  const checkStatus = async () => {
    setError('');
    if (!email.trim()) {
      setError('Enter your billing email to check subscription status.');
      return;
    }

    try {
      const response = await fetch(
        `${API_BASE_URL}/subscriptions/status?email=${encodeURIComponent(email.trim())}`
      );
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data?.detail || 'Unable to load subscription status.');
      }
      setSubscriptionState(data || null);
    } catch (err) {
      setError(err.message || 'Unable to load subscription status.');
    }
  };

  return (
    <div className="subscription-view">
      <div className="subscription-header">
        <h1>Subscription & Billing</h1>
        <p>Activate a paid plan to unlock the full Highway Pilot platform.</p>
      </div>

      <div className="billing-health">
        <span>Plan source:</span>
        <strong>
          {plansLoaded ? 'Backend Live Plans' : 'Default Plans'}
        </strong>
      </div>

      <div className="plan-grid">
        {plans.map((plan) => {
          const isActive = plan.id === selectedPlan;
          return (
            <button
              type="button"
              key={plan.id}
              className={`plan-card ${isActive ? 'active' : ''}`}
              onClick={() => setSelectedPlan(plan.id)}
            >
              <h3>{plan.name}</h3>
              <p className="price">${plan.price_usd}/mo</p>
              <p>{plan.description}</p>
              <ul>
                {(plan.features || []).map((feature) => (
                  <li key={`${plan.id}-${feature}`}>{feature}</li>
                ))}
              </ul>
            </button>
          );
        })}
      </div>

      <div className="checkout-box">
        <h2>Start Subscription</h2>
        <p>
          Selected plan: <strong>{selectedPlanInfo?.name || selectedPlan}</strong>
        </p>
        <input
          type="email"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          placeholder="you@company.com"
          autoComplete="email"
        />
        {error && <p className="error-msg">{error}</p>}
        <button type="button" onClick={onSubscribe} disabled={loading}>
          {loading ? 'Preparing checkout...' : 'Continue to Checkout'}
        </button>
        <button type="button" className="secondary-btn" onClick={checkStatus}>
          Check Subscription Status
        </button>
        {subscriptionState && (
          <div className="status-box">
            <p><strong>Subscribed:</strong> {subscriptionState.subscribed ? 'Yes' : 'No'}</p>
            <p><strong>Status:</strong> {subscriptionState.status || 'inactive'}</p>
            <p><strong>Plan:</strong> {subscriptionState.plan}</p>
            <p><strong>Period End:</strong> {subscriptionState.current_period_end || 'N/A'}</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default SubscriptionManager;
