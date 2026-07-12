import { useState } from 'react';
import { API_BASE_URL } from '../lib/api';
import './BillingSupport.css';

function BillingSupport({ defaultEmail = '' }) {
  const [email, setEmail] = useState(defaultEmail);
  const [transactions, setTransactions] = useState([
    { id: '', date: '', status: 'unknown' },
    { id: '', date: '', status: 'unknown' },
  ]);
  const [issue, setIssue] = useState('I was charged twice for the Professional plan.');
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const updateTransaction = (index, field, value) => {
    setTransactions((current) => current.map((transaction, transactionIndex) => (
      transactionIndex === index ? { ...transaction, [field]: value } : transaction
    )));
  };

  const submitRequest = async (event) => {
    event.preventDefault();
    setError('');
    setResult(null);
    setLoading(true);

    const providedTransactions = transactions.filter((transaction) => transaction.id.trim());
    try {
      const response = await fetch(`${API_BASE_URL}/subscriptions/support`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: email.trim(),
          transaction_ids: providedTransactions.map((transaction) => transaction.id.trim()),
          transaction_dates: providedTransactions.map((transaction) => transaction.date),
          transaction_statuses: providedTransactions.map((transaction) => transaction.status),
          issue: issue.trim(),
        }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Unable to submit billing case.');
      setResult(data);
    } catch (submissionError) {
      setError(submissionError.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="billing-support">
      <h1>Billing support</h1>
      <p className="subtitle">
        Check whether each charge is pending or completed. Submit transaction IDs only—never include card or bank details.
      </p>
      <form onSubmit={submitRequest}>
        <label>
          Checkout email
          <input type="email" required value={email} onChange={(event) => setEmail(event.target.value)} />
        </label>
        <div className="billing-transactions">
          {transactions.map((transaction, index) => (
            <fieldset key={index}>
              <legend>Transaction {index + 1}</legend>
              <label>
                Transaction ID
                <input
                  required={index === 0}
                  value={transaction.id}
                  onChange={(event) => updateTransaction(index, 'id', event.target.value)}
                  placeholder="ch_… or payment reference"
                />
              </label>
              <label>
                Date
                <input
                  required={Boolean(transaction.id.trim())}
                  type="date"
                  value={transaction.date}
                  onChange={(event) => updateTransaction(index, 'date', event.target.value)}
                />
              </label>
              <label>
                Status
                <select value={transaction.status} onChange={(event) => updateTransaction(index, 'status', event.target.value)}>
                  <option value="unknown">Unknown</option>
                  <option value="pending">Pending</option>
                  <option value="completed">Completed</option>
                </select>
              </label>
            </fieldset>
          ))}
        </div>
        <label>
          What happened?
          <textarea required minLength="10" maxLength="2000" value={issue} onChange={(event) => setIssue(event.target.value)} />
        </label>
        {error && <p className="billing-error">{error}</p>}
        {result && <p className="billing-success">Case {result.case_id} submitted. Keep this ID for follow-up.</p>}
        <button className="primary-button" type="submit" disabled={loading}>
          {loading ? 'Submitting…' : 'Submit billing case'}
        </button>
      </form>
    </section>
  );
}

export default BillingSupport;
