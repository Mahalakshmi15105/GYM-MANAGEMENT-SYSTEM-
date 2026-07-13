import { useState, useEffect } from "react";
import { useAuth } from "../context/AuthContext";
import { useTranslation } from "../utils/i18n";
import api from "../services/api";
import { useCurrency } from "../utils/currency";
import {
  BanknotesIcon,
  DevicePhoneMobileIcon,
  CreditCardIcon,
  BuildingOfficeIcon,
  CurrencyDollarIcon,
} from "@heroicons/react/24/outline";

export default function PaymentsPage() {
  const { user } = useAuth();
  const { t } = useTranslation(user?.gym_id);
  const { formatCurrency, setCurrencyCode } = useCurrency(user?.gym_id);
  const [members, setMembers] = useState([]);
  const [membershipPlans, setMembershipPlans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [paymentModal, setPaymentModal] = useState({
    isOpen: false,
    member: null,
  });
  const [paymentForm, setPaymentForm] = useState({
    membership_plan_id: "",
    payment_amount: "",
    payment_date: new Date().toISOString().split('T')[0],
    payment_method: "Cash",
  });

  useEffect(() => {
    fetchMembers();
    fetchMembershipPlans();
  }, []);

  const fetchMembers = async () => {
    try {
      const response = await api.get('/api/payments/members-with-payments');
      setMembers(response.data.members || []);
      if (response.data?.currency) {
        setCurrencyCode(response.data.currency);
      }
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.error || 'Failed to fetch members');
    } finally {
      setLoading(false);
    }
  };

  const fetchMembershipPlans = async () => {
    try {
      const response = await api.get('/api/membership-plans');
      setMembershipPlans(response.data.membership_plans || []);
    } catch (err) {
      console.error(err);
      console.error('Failed to fetch membership plans');
    }
  };

  const handleSearch = async (query) => {
    setSearchQuery(query);
    if (!query.trim()) {
      fetchMembers();
      return;
    }

    try {
      const response = await api.get(`/api/members/search?q=${encodeURIComponent(query)}`);
      setMembers(response.data.members || []);
    } catch (err) {
      console.error(err);
      setError('Search failed');
    }
  };

  const isDueTomorrow = (endDate) => {
    if (!endDate) return false;
    const dueDate = new Date(endDate);
    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);
    return dueDate.toDateString() === tomorrow.toDateString();
  };

  const openPaymentModal = (member) => {
    setPaymentModal({ isOpen: true, member });
    // Find the current plan by name to get its ID
    const currentPlan = membershipPlans.find(p => p.plan_name === member.membership_plan_name);
    setPaymentForm({
      membership_plan_id: currentPlan ? currentPlan.id.toString() : '',
      payment_amount: currentPlan ? currentPlan.price : '',
      payment_date: new Date().toISOString().split('T')[0],
      payment_method: 'Cash',
    });
  };

  const closePaymentModal = () => {
    setPaymentModal({ isOpen: false, member: null });
    setPaymentForm({
      membership_plan_id: '',
      payment_amount: '',
      payment_date: new Date().toISOString().split('T')[0],
      payment_method: 'Cash',
    });
  };

  const handlePlanChange = (planId) => {
    const plan = membershipPlans.find(p => p.id === parseInt(planId));
    if (plan) {
      setPaymentForm({
        ...paymentForm,
        membership_plan_id: planId,
        payment_amount: plan.price,
      });
    }
  };

  const handlePaymentSubmit = async () => {
    if (!paymentModal.member) return;

    try {
      const response = await api.post('/api/payments', {
        member_id: paymentModal.member.id,
        membership_plan_id: paymentForm.membership_plan_id || null,
        payment_amount: paymentForm.payment_amount,
        payment_date: paymentForm.payment_date,
        payment_method: paymentForm.payment_method,
        payment_status: 'Paid',
      });
      
      closePaymentModal();
      fetchMembers();
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.error || 'Failed to process payment');
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return "-";
    return new Date(dateString).toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
    });
  };

  const getStatusColor = (status) => {
    switch (status) {
      case "Paid":
        return "bg-green-50 text-green-700 border-green-200";
      case "Pending":
        return "bg-yellow-50 text-yellow-700 border-yellow-200";
      case "Failed":
        return "bg-red-50 text-red-700 border-red-200";
      default:
        return "bg-gray-50 text-gray-600 border-gray-200";
    }
  };

  const getMethodIcon = (method) => {
    switch (method) {
      case "Cash":
        return <BanknotesIcon className="w-5 h-5" />;
      case "UPI":
        return <DevicePhoneMobileIcon className="w-5 h-5" />;
      case "Card":
        return <CreditCardIcon className="w-5 h-5" />;
      case "Bank Transfer":
        return <BuildingOfficeIcon className="w-5 h-5" />;
      default:
        return <CurrencyDollarIcon className="w-5 h-5" />;
    }
  };

  return (
    <div className="space-y-8">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 mb-1">{t('payments.title')}</h1>
          <p className="text-sm text-gray-600">
            Manage member payments - Gym ID: {user?.gym_id}
          </p>
        </div>
      </div>

      {/* Search */}
      <div className="bg-white border border-gray-200 p-6 rounded-2xl shadow-sm">
        <div className="grid grid-cols-1 gap-4">
          <div>
            <input
              type="text"
              placeholder={t('payments.searchPayments')}
              value={searchQuery}
              onChange={(e) => handleSearch(e.target.value)}
              className="w-full bg-gray-50 border border-gray-200 focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 rounded-xl px-4 py-3 text-sm text-gray-900 placeholder-gray-500 focus:outline-none transition-all duration-200"
            />
          </div>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 text-sm p-4 rounded-xl">
          {error}
        </div>
      )}

      <div className="bg-white border border-gray-200 rounded-2xl overflow-hidden shadow-sm">
        {loading ? (
          <div className="p-8 text-center text-gray-500">
            {t('common.loading')}
          </div>
        ) : members.length === 0 ? (
          <div className="p-8 text-center text-gray-500">
            {searchQuery ? t('members.noMembersFound') : t('empty.noMembersDesc')}
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200 bg-gray-50">
                  <th className="text-left px-6 py-4 text-xs font-semibold uppercase tracking-wider text-gray-600">
                    Member
                  </th>
                  <th className="text-left px-6 py-4 text-xs font-semibold uppercase tracking-wider text-gray-600">
                    Plan
                  </th>
                  <th className="text-left px-6 py-4 text-xs font-semibold uppercase tracking-wider text-gray-600">
                    Amount
                  </th>
                  <th className="text-left px-6 py-4 text-xs font-semibold uppercase tracking-wider text-gray-600">
                    Date
                  </th>
                  <th className="text-left px-6 py-4 text-xs font-semibold uppercase tracking-wider text-gray-600">
                    Method
                  </th>
                  <th className="text-left px-6 py-4 text-xs font-semibold uppercase tracking-wider text-gray-600">
                    Status
                  </th>
                  <th className="text-left px-6 py-4 text-xs font-semibold uppercase tracking-wider text-gray-600">
                    Transaction ID
                  </th>
                  <th className="text-left px-6 py-4 text-xs font-semibold uppercase tracking-wider text-gray-600">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody>
                {members.map((member) => (
                  <tr
                    key={member.id}
                    className="border-b border-gray-100 hover:bg-gray-50"
                  >
                    <td className="px-6 py-4">
                      <div>
                        <p className={`text-sm font-medium ${isDueTomorrow(member.membership_end_date) ? 'text-red-600' : 'text-gray-900'}`}>
                          {member.first_name} {member.last_name}
                        </p>
                        <p className="text-xs text-gray-500 font-mono">
                          {member.phone}
                        </p>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-700">
                      {member.membership_plan_name || "-"}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900 font-semibold">
                      {member.last_payment ? formatCurrency(member.last_payment.payment_amount) : '-'}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-700">
                      {member.last_payment ? formatDate(member.last_payment.payment_date) : '-'}
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2 text-orange-600">
                        {member.last_payment ? getMethodIcon(member.last_payment.payment_method) : null}
                        <span className="text-sm text-gray-700">
                          {member.last_payment ? member.last_payment.payment_method : '-'}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`inline-flex px-2 py-1 rounded-full text-xs font-semibold border ${member.last_payment ? getStatusColor(member.last_payment.payment_status) : 'bg-gray-50 text-gray-600 border-gray-200'}`}>
                        {member.last_payment ? member.last_payment.payment_status : '-'}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-700 font-mono">
                      {member.last_payment ? (member.last_payment.transaction_id || '-') : '-'}
                    </td>
                    <td className="px-6 py-4">
                      <button
                        onClick={() => openPaymentModal(member)}
                        className="bg-orange-600 hover:bg-orange-700 text-white px-3 py-1.5 rounded-lg text-xs font-medium transition-colors"
                      >
                        Pay
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {paymentModal.isOpen && paymentModal.member && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white border border-gray-200 rounded-2xl p-6 max-w-md w-full shadow-lg">
            <h3 className="text-lg font-bold text-gray-900 mb-4">
              Record Payment
            </h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Member Name
                </label>
                <input
                  type="text"
                  value={`${paymentModal.member.first_name} ${paymentModal.member.last_name}`}
                  readOnly
                  className="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 text-sm text-gray-900"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Membership Plan
                </label>
                <select
                  value={paymentForm.membership_plan_id}
                  onChange={(e) => handlePlanChange(e.target.value)}
                  className="w-full bg-gray-50 border border-gray-200 focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 rounded-xl px-4 py-3 text-sm text-gray-900 focus:outline-none transition-all duration-200"
                >
                  <option value="">Select a plan</option>
                  {membershipPlans.map((plan) => (
                    <option key={plan.id} value={plan.id}>
                      {plan.plan_name} - {formatCurrency(plan.price)}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Payment Amount
                </label>
                <input
                  type="text"
                  value={paymentForm.payment_amount ? formatCurrency(paymentForm.payment_amount) : ''}
                  readOnly
                  className="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 text-sm text-gray-900"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Payment Date
                </label>
                <input
                  type="date"
                  value={paymentForm.payment_date}
                  onChange={(e) => setPaymentForm({ ...paymentForm, payment_date: e.target.value })}
                  className="w-full bg-gray-50 border border-gray-200 focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 rounded-xl px-4 py-3 text-sm text-gray-900 focus:outline-none transition-all duration-200"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Payment Method
                </label>
                <select
                  value={paymentForm.payment_method}
                  onChange={(e) => setPaymentForm({ ...paymentForm, payment_method: e.target.value })}
                  className="w-full bg-gray-50 border border-gray-200 focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 rounded-xl px-4 py-3 text-sm text-gray-900 focus:outline-none transition-all duration-200"
                >
                  <option value="Cash">Cash</option>
                  <option value="UPI">UPI</option>
                  <option value="Card">Card</option>
                  <option value="Bank Transfer">Bank Transfer</option>
                  <option value="Other">Other</option>
                </select>
              </div>
            </div>
            <div className="flex gap-3 mt-6">
              <button
                onClick={handlePaymentSubmit}
                disabled={!paymentForm.membership_plan_id || !paymentForm.payment_amount}
                className="bg-orange-600 hover:bg-orange-700 disabled:bg-gray-300 disabled:cursor-not-allowed text-white px-4 py-2 rounded-xl text-sm font-medium transition-colors"
              >
                Submit Payment
              </button>
              <button
                onClick={closePaymentModal}
                className="bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2 rounded-xl text-sm font-medium transition-colors"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
