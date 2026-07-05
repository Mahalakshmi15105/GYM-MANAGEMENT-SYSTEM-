import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../services/api';

export default function EditPaymentPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [members, setMembers] = useState([]);
  const [membershipPlans, setMembershipPlans] = useState([]);
  const [selectedMember, setSelectedMember] = useState(null);
  const [selectedPlan, setSelectedPlan] = useState(null);
  const [formData, setFormData] = useState({
    member_id: '',
    membership_plan_id: '',
    payment_amount: '',
    payment_date: '',
    payment_method: 'Cash',
    payment_status: 'Paid',
    transaction_id: '',
    notes: ''
  });

  useEffect(() => {
    fetchPayment();
    fetchMembers();
    fetchMembershipPlans();
  }, [id]);

  const fetchPayment = async () => {
    try {
      const response = await api.get(`/api/payments/${id}`);
      const payment = response.data;
      
      setFormData({
        member_id: payment.member_id.toString(),
        membership_plan_id: payment.membership_plan_id ? payment.membership_plan_id.toString() : '',
        payment_amount: payment.payment_amount.toString(),
        payment_date: payment.payment_date,
        payment_method: payment.payment_method,
        payment_status: payment.payment_status,
        transaction_id: payment.transaction_id || '',
        notes: payment.notes || ''
      });
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.error || 'Failed to fetch payment details');
    } finally {
      setLoading(false);
    }
  };

  const fetchMembers = async () => {
    try {
      const response = await api.get('/api/payments/members');
      setMembers(response.data.members || []);
    } catch (err) {
      console.error('Failed to fetch members:', err);
    }
  };

  const fetchMembershipPlans = async () => {
    try {
      const response = await api.get('/api/payments/membership-plans');
      setMembershipPlans(response.data.membership_plans || []);
    } catch (err) {
      console.error('Failed to fetch membership plans:', err);
    }
  };

  const handleMemberChange = (memberId) => {
    const member = members.find(m => m.id.toString() === memberId);
    setSelectedMember(member);
    setFormData(prev => ({ ...prev, member_id: memberId }));
  };

  const handlePlanChange = (planId) => {
    const plan = membershipPlans.find(p => p.id.toString() === planId);
    setSelectedPlan(plan);
    
    setFormData(prev => ({
      ...prev,
      membership_plan_id: planId,
      payment_amount: plan && !prev.payment_amount ? plan.price.toString() : prev.payment_amount
    }));
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validation
    if (!formData.member_id || !formData.payment_amount || !formData.payment_date) {
      setError('Please fill in all required fields.');
      return;
    }

    // Amount validation
    if (parseFloat(formData.payment_amount) <= 0) {
      setError('Payment amount must be positive.');
      return;
    }

    setSaving(true);
    setError('');

    try {
      await api.put(`/api/payments/${id}`, formData);
      navigate(`/payments/${id}`);
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.error || 'Failed to update payment. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  const paymentMethods = ['Cash', 'UPI', 'Card', 'Bank Transfer'];
  const paymentStatuses = ['Paid', 'Pending', 'Failed'];

  // Set selected member and plan once data is loaded
  useEffect(() => {
    if (members.length > 0 && formData.member_id) {
      const member = members.find(m => m.id.toString() === formData.member_id);
      setSelectedMember(member);
    }
  }, [members, formData.member_id]);

  useEffect(() => {
    if (membershipPlans.length > 0 && formData.membership_plan_id) {
      const plan = membershipPlans.find(p => p.id.toString() === formData.membership_plan_id);
      setSelectedPlan(plan);
    }
  }, [membershipPlans, formData.membership_plan_id]);

  if (loading) {
    return (
      <div className="space-y-8">
        <div className="flex items-center justify-center py-12">
          <div className="text-gray-600">Loading payment details...</div>
        </div>
      </div>
    );
  }

  if (error && !formData.member_id) {
    return (
      <div className="space-y-8">
        <div className="bg-red-50 border border-red-200 text-red-700 text-sm p-4 rounded-xl">
          {error}
        </div>
        <button
          onClick={() => navigate('/payments')}
          className="bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2 rounded-xl text-sm font-medium transition-colors"
        >
          ← Back to Payments
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 mb-1">Edit Payment</h1>
          <p className="text-sm text-gray-600">Update payment information</p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={() => navigate(`/payments/${id}`)}
            className="bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2 rounded-xl text-sm font-medium transition-colors"
          >
            Cancel
          </button>
        </div>
      </div>

      {/* Form */}
      <div className="bg-white border border-gray-200 p-6 rounded-2xl shadow-sm">
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 text-sm p-4 rounded-xl mb-6">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Member Selection */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Member & Plan</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-gray-600 mb-2">
                  Select Member *
                </label>
                <select
                  name="member_id"
                  required
                  value={formData.member_id}
                  onChange={(e) => handleMemberChange(e.target.value)}
                  className="w-full bg-gray-50 border border-gray-200 focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 rounded-xl px-4 py-3 text-sm text-gray-900 focus:outline-none transition-all duration-200"
                >
                  <option value="">Select a member</option>
                  {members.map((member) => (
                    <option key={member.id} value={member.id}>
                      {member.name} - {member.phone}
                    </option>
                  ))}
                </select>
                {selectedMember && (
                  <p className="text-xs text-gray-500 mt-1">
                    Current plan: {selectedMember.membership_plan_name || 'No plan assigned'}
                  </p>
                )}
              </div>
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-gray-600 mb-2">
                  Membership Plan
                </label>
                <select
                  name="membership_plan_id"
                  value={formData.membership_plan_id}
                  onChange={(e) => handlePlanChange(e.target.value)}
                  className="w-full bg-gray-50 border border-gray-200 focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 rounded-xl px-4 py-3 text-sm text-gray-900 focus:outline-none transition-all duration-200"
                >
                  <option value="">Select a plan (optional)</option>
                  {membershipPlans.map((plan) => (
                    <option key={plan.id} value={plan.id}>
                      {plan.plan_name} - ${plan.price}
                    </option>
                  ))}
                </select>
                {selectedPlan && (
                  <p className="text-xs text-gray-500 mt-1">
                    Duration: {selectedPlan.duration} days
                  </p>
                )}
              </div>
            </div>
          </div>

          {/* Payment Details */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Payment Details</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-gray-600 mb-2">
                  Payment Amount (USD) *
                </label>
                <input
                  type="number"
                  name="payment_amount"
                  required
                  min="0"
                  step="0.01"
                  value={formData.payment_amount}
                  onChange={handleInputChange}
                  placeholder="e.g., 49.99"
                  className="w-full bg-gray-50 border border-gray-200 focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 rounded-xl px-4 py-3 text-sm text-gray-900 placeholder-gray-500 focus:outline-none transition-all duration-200"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-gray-600 mb-2">
                  Payment Date *
                </label>
                <input
                  type="date"
                  name="payment_date"
                  required
                  value={formData.payment_date}
                  onChange={handleInputChange}
                  className="w-full bg-gray-50 border border-gray-200 focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 rounded-xl px-4 py-3 text-sm text-gray-900 focus:outline-none transition-all duration-200"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-gray-600 mb-2">
                  Payment Method *
                </label>
                <select
                  name="payment_method"
                  required
                  value={formData.payment_method}
                  onChange={handleInputChange}
                  className="w-full bg-gray-50 border border-gray-200 focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 rounded-xl px-4 py-3 text-sm text-gray-900 focus:outline-none transition-all duration-200"
                >
                  {paymentMethods.map((method) => (
                    <option key={method} value={method}>{method}</option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          {/* Additional Information */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Additional Information</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-gray-600 mb-2">
                  Payment Status
                </label>
                <select
                  name="payment_status"
                  value={formData.payment_status}
                  onChange={handleInputChange}
                  className="w-full bg-gray-50 border border-gray-200 focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 rounded-xl px-4 py-3 text-sm text-gray-900 focus:outline-none transition-all duration-200"
                >
                  {paymentStatuses.map((status) => (
                    <option key={status} value={status}>{status}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-gray-600 mb-2">
                  Transaction ID / Receipt Number
                </label>
                <input
                  type="text"
                  name="transaction_id"
                  value={formData.transaction_id}
                  onChange={handleInputChange}
                  placeholder="Transaction or receipt number"
                  className="w-full bg-gray-50 border border-gray-200 focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 rounded-xl px-4 py-3 text-sm text-gray-900 placeholder-gray-500 focus:outline-none transition-all duration-200"
                />
              </div>
            </div>
            <div className="mt-4">
              <label className="block text-xs font-semibold uppercase tracking-wider text-gray-600 mb-2">
                Notes
              </label>
              <textarea
                name="notes"
                value={formData.notes}
                onChange={handleInputChange}
                rows="3"
                placeholder="Additional notes about this payment..."
                className="w-full bg-gray-50 border border-gray-200 focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 rounded-xl px-4 py-3 text-sm text-gray-900 placeholder-gray-500 focus:outline-none transition-all duration-200 resize-none"
              />
            </div>
          </div>

          {/* Submit Buttons */}
          <div className="flex flex-col sm:flex-row gap-3 pt-4">
            <button
              type="submit"
              disabled={saving}
              className="bg-orange-600 hover:bg-orange-700 text-white font-bold py-3 px-6 rounded-xl transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {saving ? 'Updating Payment...' : 'Update Payment'}
            </button>
            <button
              type="button"
              onClick={() => navigate(`/payments/${id}`)}
              className="bg-gray-100 hover:bg-gray-200 text-gray-700 font-medium py-3 px-6 rounded-xl transition-colors"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}