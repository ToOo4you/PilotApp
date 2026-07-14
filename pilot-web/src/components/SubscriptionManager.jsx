import React, { useEffect, useMemo, useState } from 'react';
import { API_BASE_URL } from '../lib/api';
import './SubscriptionManager.css';

const DEFAULT_PLANS = [
  {
    key: 'starter',
    name: 'Starter',
    monthly_price_usd: 49,
    features: ['AI chat', 'Route optimization', 'Basic analytics']
  },
  {
    key: 'growth',
    name: 'Growth',
    monthly_price_usd: 149,
    features: ['Everything in Starter', 'Auto-dispatch', 'Predictive maintenance']
  },
  {
    key: 'enterprise',
    name: 'Enterprise',
    monthly_price_usd: 399,
    features: ['Everything in Growth', 'Priority support', 'Custom integrations']
  }
];

const SubscriptionManager = () => {
  const [email, setEmail] = useState('');
  const [selectedPlan, setSelectedPlan] = useState('growth');
  const [plans, setPlans] = useState(DEFAULT_PLANS);
  const [billingStatus, setBillingStatus] = useState(null);
  const [subscriptionState, setSubscriptionState] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    const loadPlans = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/billing/plans`);
        if (!response.ok) {
          return;
        }
        const data = await response.json();
        if (data?.status === 'success') {
          const apiPlans = data.billing?.plans;
          if (Array.isArray(apiPlans) && apiPlans.length > 0) {
            setPlans(apiPlans);
          }
          setBillingStatus(data.billing || null);
        }
      } catch (err) {
        console.error('Unable to fetch billing plans', err);
      }
    };

    loadPlans();
  }, []);

  const selectedPlanInfo = useMemo(
    () => plans.find((plan) => plan.key === selectedPlan),
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
      const response = await fetch(`${API_BASE_URL}/api/billing/checkout-session`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          plan: selectedPlan,
          customer_email: email.trim(),
          success_url: `${currentUrl}/?billing=success`,
          cancel_url: `${currentUrl}/?billing=cancelled`
        })
      });

      const data = await response.json();
      if (!response.ok || data?.status !== 'success') {
        throw new Error(data?.detail || 'Unable to create subscription checkout session.');
      }

      const checkoutUrl = data.checkout?.checkout_url;
      if (!checkoutUrl) {
        throw new Error('Checkout URL missing in billing response.');
      }

      window.location.assign(checkoutUrl);
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
        `${API_BASE_URL}/api/billing/subscription-status?email=${encodeURIComponent(email.trim())}`
      );
      const data = await response.json();
      if (!response.ok || data?.status !== 'success') {
        throw new Error(data?.detail || 'Unable to load subscription status.');
      }
      setSubscriptionState(data.subscription || null);
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
        <span>Billing provider:</span>
        <strong>
          {billingStatus?.stripe_ready ? 'Stripe Live' : billingStatus?.mock_mode ? 'Mock Mode' : 'Unavailable'}
        </strong>
      </div>

      <div className="plan-grid">
        {plans.map((plan) => {
          const isActive = plan.key === selectedPlan;
          return (
            <button
              type="button"
              key={plan.key}
              className={`plan-card ${isActive ? 'active' : ''}`}
              onClick={() => setSelectedPlan(plan.key)}
            >
              <h3>{plan.name}</h3>
              <p className="price">${plan.monthly_price_usd}/mo</p>
              <ul>
                {(plan.features || []).map((feature) => (
                  <li key={`${plan.key}-${feature}`}>{feature}</li>
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
            <p><strong>State:</strong> {subscriptionState.state}</p>
            <p><strong>Plan:</strong> {subscriptionState.plan}</p>
            <p><strong>Provider:</strong> {subscriptionState.provider}</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default SubscriptionManager;
