import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useTranslation } from "../utils/i18n";
import api from "../services/api";
import { useCurrency } from "../utils/currency";
import {
  PlusIcon,
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
  const [payments, setPayments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState("All");
  const [methodFilter, setMethodFilter] = useState("All");
  const [dateRange, setDateRange] = useState({ start: "", end: "" });
  const [deleteModal, setDeleteModal] = useState({
    isOpen: false,
    payment: null,
  });

  useEffect(() => {
    fetchPayments();
  }, []);

  const fetchPayments = async () => {
    try {
      const params = new URLSearchParams();
      if (statusFilter !== "All") params.append("status", statusFilter);
      if (methodFilter !== "All") params.append("method", methodFilter);
      if (dateRange.start) params.append("start_date", dateRange.start);
      if (dateRange.end) params.append("end_date", dateRange.end);
      if (searchQuery.trim()) params.append("q", searchQuery.trim());

      const response = await api.get(`/api/payments?${params.toString()}`);
      setPayments(response.data.payments || []);
      if (response.data?.currency) {
        setCurrencyCode(response.data.currency);
      }
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.error || "Failed to fetch payments");
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (query) => {
    setSearchQuery(query);
    if (!query.trim()) {
      fetchPayments();
      return;
    }

    try {
      const response = await api.get(
        `/api/payments/search?q=${encodeURIComponent(query)}`,
      );
      setPayments(response.data.payments || []);
      if (response.data?.currency) {
        setCurrencyCode(response.data.currency);
      }
    } catch (err) {
      console.error(err);
      setError("Search failed");
    }
  };

  const handleFilterChange = () => {
    fetchPayments();
  };

  const handleDelete = async (paymentId) => {
    try {
      await api.delete(`/api/payments/${paymentId}`);
      setPayments(payments.filter((p) => p.id !== paymentId));
      setDeleteModal({ isOpen: false, payment: null });
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.error || "Failed to delete payment");
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
        <Link
          to="/payments/add"
          className="bg-orange-600 hover:bg-orange-700 text-white font-bold px-6 py-3 rounded-xl transition-all duration-200 self-start md:self-auto text-center shadow-sm flex items-center gap-2"
        >
          <PlusIcon className="w-4 h-4" /> {t('payments.addPayment')}
        </Link>
      </div>

      {/* Filters */}
      <div className="bg-white border border-gray-200 p-6 rounded-2xl shadow-sm">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          <div className="lg:col-span-2">
            <input
              type="text"
              placeholder={t('payments.searchPayments')}
              value={searchQuery}
              onChange={(e) => handleSearch(e.target.value)}
              className="w-full bg-gray-50 border border-gray-200 focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 rounded-xl px-4 py-3 text-sm text-gray-900 placeholder-gray-500 focus:outline-none transition-all duration-200"
            />
          </div>
          <div>
            <select
              value={statusFilter}
              onChange={(e) => {
                setStatusFilter(e.target.value);
                handleFilterChange();
              }}
              className="w-full bg-gray-50 border border-gray-200 focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 rounded-xl px-4 py-3 text-sm text-gray-900 focus:outline-none transition-all duration-200"
            >
              <option value="All">{t('common.status')}</option>
              <option value="Paid">{t('payments.paid')}</option>
              <option value="Pending">{t('payments.unpaid')}</option>
              <option value="Failed">{t('payments.overdue')}</option>
            </select>
          </div>
          <div>
            <select
              value={methodFilter}
              onChange={(e) => {
                setMethodFilter(e.target.value);
                handleFilterChange();
              }}
              className="w-full bg-gray-50 border border-gray-200 focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 rounded-xl px-4 py-3 text-sm text-gray-900 focus:outline-none transition-all duration-200"
            >
              <option value="All">{t('common.filter')}</option>
              <option value="Cash">{t('payments.cash')}</option>
              <option value="UPI">{t('payments.online')}</option>
              <option value="Card">{t('payments.card')}</option>
              <option value="Bank Transfer">{t('payments.bank')}</option>
            </select>
          </div>
          <div>
            <input
              type="date"
              value={dateRange.start}
              onChange={(e) => {
                setDateRange((prev) => ({ ...prev, start: e.target.value }));
                handleFilterChange();
              }}
              className="w-full bg-gray-50 border border-gray-200 focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 rounded-xl px-4 py-3 text-sm text-gray-900 focus:outline-none transition-all duration-200"
              placeholder={t('reports.fromDate')}
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
        ) : payments.length === 0 ? (
          <div className="p-8 text-center text-gray-500">
            {searchQuery ? t('payments.noPaymentsFound') : t('empty.noPaymentsDesc')}
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
                {payments.map((payment) => (
                  <tr
                    key={payment.id}
                    className="border-b border-gray-100 hover:bg-gray-50"
                  >
                    <td className="px-6 py-4">
                      <div>
                        <p className="text-sm text-gray-900 font-medium">
                          {payment.member_name}
                        </p>
                        <p className="text-xs text-gray-500 font-mono">
                          {payment.member_phone}
                        </p>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-700">
                      {payment.membership_plan_name || "-"}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900 font-semibold">
                      {formatCurrency(payment.payment_amount)}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-700">
                      {formatDate(payment.payment_date)}
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2 text-orange-600">
                        {getMethodIcon(payment.payment_method)}
                        <span className="text-sm text-gray-700">
                          {payment.payment_method}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span
                        className={`inline-flex px-2 py-1 rounded-full text-xs font-semibold border ${getStatusColor(payment.payment_status)}`}
                      >
                        {payment.payment_status}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-700 font-mono">
                      {payment.transaction_id || "-"}
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        <Link
                          to={`/payments/${payment.id}`}
                          className="bg-gray-100 hover:bg-gray-200 text-gray-700 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors"
                        >
                          View
                        </Link>
                        <Link
                          to={`/payments/${payment.id}/edit`}
                          className="bg-orange-600 hover:bg-orange-700 text-white px-3 py-1.5 rounded-lg text-xs font-medium transition-colors"
                        >
                          Edit
                        </Link>
                        <button
                          onClick={() =>
                            setDeleteModal({ isOpen: true, payment })
                          }
                          className="bg-red-600 hover:bg-red-700 text-white px-3 py-1.5 rounded-lg text-xs font-medium transition-colors"
                        >
                          Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {deleteModal.isOpen && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white border border-gray-200 rounded-2xl p-6 max-w-md w-full shadow-lg">
            <h3 className="text-lg font-bold text-gray-900 mb-2">
              Delete Payment
            </h3>
            <p className="text-sm text-gray-600 mb-6">
              Are you sure you want to delete payment{" "}
              <strong className="text-gray-900">
                {deleteModal.payment?.transaction_id}
              </strong>
              ? This action cannot be undone.
            </p>
            <div className="flex gap-3">
              <button
                onClick={() => handleDelete(deleteModal.payment.id)}
                className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-xl text-sm font-medium transition-colors"
              >
                Delete
              </button>
              <button
                onClick={() => setDeleteModal({ isOpen: false, payment: null })}
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
