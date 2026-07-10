import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import api from "../services/api";
import { useCurrency } from "../utils/currency";
import {
  ArrowLeftIcon,
  DocumentTextIcon,
  CreditCardIcon,
  ClipboardDocumentListIcon,
  ClockIcon,
  CurrencyDollarIcon,
  BanknotesIcon,
  DevicePhoneMobileIcon,
  BuildingOfficeIcon,
} from "@heroicons/react/24/outline";

export default function ViewPaymentPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const { formatCurrency, setCurrencyCode } = useCurrency(user?.gym_id);
  const [payment, setPayment] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showReceipt, setShowReceipt] = useState(false);
  const [receiptData, setReceiptData] = useState(null);

  useEffect(() => {
    fetchPayment();
  }, [id]);

  const fetchPayment = async () => {
    try {
      const response = await api.get(`/api/payments/${id}`);
      setPayment(response.data.payment || response.data);
      if (response.data?.currency) {
        setCurrencyCode(response.data.currency);
      }
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.error || "Failed to fetch payment details");
    } finally {
      setLoading(false);
    }
  };

  const generateReceipt = async () => {
    try {
      const response = await api.get(`/api/payments/receipt/${id}`);
      setReceiptData(response.data);
      if (response.data?.currency) {
        setCurrencyCode(response.data.currency);
      }
      setShowReceipt(true);
    } catch (err) {
      console.error(err);
      setError("Failed to generate receipt");
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return "Not provided";
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "long",
      day: "numeric",
    });
  };

  const formatDateTime = (dateString) => {
    if (!dateString) return "Not provided";
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "long",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
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
        return <BanknotesIcon className="w-8 h-8" />;
      case "UPI":
        return <DevicePhoneMobileIcon className="w-8 h-8" />;
      case "Card":
        return <CreditCardIcon className="w-8 h-8" />;
      case "Bank Transfer":
        return <BuildingOfficeIcon className="w-8 h-8" />;
      default:
        return <CurrencyDollarIcon className="w-8 h-8" />;
    }
  };

  if (loading) {
    return (
      <div className="space-y-8">
        <div className="flex items-center justify-center py-12">
          <div className="text-gray-600">Loading payment details...</div>
        </div>
      </div>
    );
  }

  if (error || !payment) {
    return (
      <div className="space-y-8">
        <div className="bg-red-50 border border-red-200 text-red-700 text-sm p-4 rounded-xl">
          {error || "Payment not found"}
        </div>
        <button
          onClick={() => navigate("/payments")}
          className="bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2 rounded-xl text-sm font-medium transition-colors flex items-center gap-2"
        >
          <ArrowLeftIcon className="w-4 h-4" /> Back to Payments
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 mb-1">
            Payment Details
          </h1>
          <p className="text-sm text-gray-600">
            Transaction ID: {payment.transaction_id || "N/A"}
          </p>
        </div>
        <div className="flex flex-wrap gap-3">
          <button
            onClick={generateReceipt}
            className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-xl text-sm font-medium transition-colors flex items-center gap-2"
          >
            <DocumentTextIcon className="w-4 h-4" /> Generate Receipt
          </button>
          <button
            onClick={() => navigate(`/payments/${id}/edit`)}
            className="bg-orange-600 hover:bg-orange-700 text-white px-4 py-2 rounded-xl text-sm font-medium transition-colors"
          >
            Edit Payment
          </button>
          <button
            onClick={() => navigate("/payments")}
            className="bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2 rounded-xl text-sm font-medium transition-colors flex items-center gap-2"
          >
            <ArrowLeftIcon className="w-4 h-4" /> Back to Payments
          </button>
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-8">
        {/* Main Information */}
        <div className="lg:col-span-2 space-y-6">
          {/* Payment Details */}
          <div className="bg-white border border-gray-200 p-6 rounded-2xl shadow-sm">
            <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
              <CreditCardIcon className="w-5 h-5 text-orange-500" /> Payment
              Information
            </h2>
            <div className="grid md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <div>
                  <label className="text-xs uppercase font-semibold tracking-wider text-gray-600">
                    Member
                  </label>
                  <p className="text-gray-900 font-medium text-lg">
                    {payment.member_name}
                  </p>
                  <p className="text-gray-500 text-sm font-mono">
                    {payment.member_phone}
                  </p>
                </div>
                <div>
                  <label className="text-xs uppercase font-semibold tracking-wider text-gray-600">
                    Payment Amount
                  </label>
                  <p className="text-gray-900 font-bold text-2xl text-orange-600">
                    {formatCurrency(payment.payment_amount)}
                  </p>
                </div>
                <div>
                  <label className="text-xs uppercase font-semibold tracking-wider text-gray-600">
                    Payment Date
                  </label>
                  <p className="text-gray-900 font-medium">
                    {formatDate(payment.payment_date)}
                  </p>
                </div>
              </div>
              <div className="space-y-4">
                <div>
                  <label className="text-xs uppercase font-semibold tracking-wider text-gray-600">
                    Payment Method
                  </label>
                  <div className="flex items-center gap-2 mt-1 text-orange-600">
                    {getMethodIcon(payment.payment_method)}
                    <span className="text-gray-900 font-medium">
                      {payment.payment_method}
                    </span>
                  </div>
                </div>
                <div>
                  <label className="text-xs uppercase font-semibold tracking-wider text-gray-600">
                    Status
                  </label>
                  <div className="mt-1">
                    <span
                      className={`inline-flex px-3 py-1 rounded-full text-sm font-semibold border ${getStatusColor(payment.payment_status)}`}
                    >
                      {payment.payment_status}
                    </span>
                  </div>
                </div>
                <div>
                  <label className="text-xs uppercase font-semibold tracking-wider text-gray-600">
                    Transaction ID
                  </label>
                  <p className="text-gray-900 font-mono bg-gray-50 px-2 py-1 rounded text-sm">
                    {payment.transaction_id || "Not provided"}
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Membership Plan Details */}
          {payment.membership_plan_name && (
            <div className="bg-white border border-gray-200 p-6 rounded-2xl shadow-sm">
              <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                <ClipboardDocumentListIcon className="w-5 h-5 text-orange-500" />{" "}
                Membership Plan
              </h2>
              <div className="bg-orange-50 border border-orange-200 p-4 rounded-xl">
                <p className="text-orange-800 font-medium text-lg">
                  {payment.membership_plan_name}
                </p>
                <p className="text-orange-600 text-sm">
                  Associated with this payment
                </p>
              </div>
            </div>
          )}

          {/* Notes */}
          {payment.notes && (
            <div className="bg-white border border-gray-200 p-6 rounded-2xl shadow-sm">
              <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                <DocumentTextIcon className="w-5 h-5 text-orange-500" /> Notes
              </h2>
              <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">
                {payment.notes}
              </p>
            </div>
          )}
        </div>

        {/* Sidebar Information */}
        <div className="space-y-6">
          {/* Timestamps */}
          <div className="bg-white border border-gray-200 p-6 rounded-2xl shadow-sm">
            <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
              <ClockIcon className="w-5 h-5 text-orange-500" /> Timestamps
            </h2>
            <div className="space-y-3">
              <div>
                <label className="text-xs uppercase font-semibold tracking-wider text-gray-600">
                  Recorded At
                </label>
                <p className="text-gray-900 text-sm">
                  {formatDateTime(payment.created_at)}
                </p>
              </div>
              <div>
                <label className="text-xs uppercase font-semibold tracking-wider text-gray-600">
                  Last Updated
                </label>
                <p className="text-gray-900 text-sm">
                  {formatDateTime(payment.updated_at)}
                </p>
              </div>
            </div>
          </div>

          {/* Payment Icon */}
          <div className="bg-white border border-gray-200 p-6 rounded-2xl shadow-sm">
            <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
              <CurrencyDollarIcon className="w-5 h-5 text-orange-500" /> Payment
              Icon
            </h2>
            <div className="w-32 h-32 bg-orange-100 border-2 border-orange-200 rounded-xl flex items-center justify-center mx-auto text-orange-600">
              {getMethodIcon(payment.payment_method)}
            </div>
            <p className="text-xs text-gray-500 text-center mt-2">
              {payment.payment_method} Payment
            </p>
          </div>
        </div>
      </div>

      {/* Receipt Modal */}
      {showReceipt && receiptData && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white border border-gray-200 rounded-2xl p-8 max-w-md w-full shadow-lg max-h-[90vh] overflow-y-auto">
            <div className="text-center mb-6">
              {receiptData.logo_url && (
                <img
                  src={`${process.env.REACT_APP_API_URL || 'http://localhost:5000'}${receiptData.logo_url}`}
                  alt="Gym Logo"
                  className="w-20 h-20 mx-auto object-contain mb-4 rounded-lg"
                />
              )}
              <h3 className="text-xl font-bold text-gray-900 mb-2">
                Payment Receipt
              </h3>
              <p className="text-sm text-gray-600">
                Receipt #{receiptData.receipt_number}
              </p>
            </div>

            <div className="space-y-4 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Gym:</span>
                <span className="font-medium">{receiptData.gym_name}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Member:</span>
                <span className="font-medium">
                  {receiptData.payment.member_name}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Phone:</span>
                <span className="font-mono">
                  {receiptData.payment.member_phone}
                </span>
              </div>
              {receiptData.payment.membership_plan_name && (
                <div className="flex justify-between">
                  <span className="text-gray-600">Plan:</span>
                  <span className="font-medium">
                    {receiptData.payment.membership_plan_name}
                  </span>
                </div>
              )}
              <hr className="border-gray-200" />
              <div className="flex justify-between">
                <span className="text-gray-600">Amount:</span>
                <span className="font-bold text-lg">
                  {formatCurrency(receiptData.payment.payment_amount)}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Method:</span>
                <span className="font-medium">
                  {receiptData.payment.payment_method}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Date:</span>
                <span className="font-medium">
                  {formatDate(receiptData.payment.payment_date)}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Transaction ID:</span>
                <span className="font-mono text-xs">
                  {receiptData.payment.transaction_id}
                </span>
              </div>
              <hr className="border-gray-200" />
              <div className="flex justify-between">
                <span className="text-gray-600">Status:</span>
                <span
                  className={`font-semibold ${receiptData.payment.payment_status === "Paid" ? "text-green-600" : "text-yellow-600"}`}
                >
                  {receiptData.payment.payment_status}
                </span>
              </div>
              <div className="text-center text-xs text-gray-500 mt-4">
                Generated on {formatDateTime(receiptData.generated_at)}
              </div>
            </div>

            <div className="flex gap-3 mt-6">
              <button
                onClick={() => window.print()}
                className="flex-1 bg-orange-600 hover:bg-orange-700 text-white px-4 py-2 rounded-xl text-sm font-medium transition-colors"
              >
                Print Receipt
              </button>
              <button
                onClick={() => setShowReceipt(false)}
                className="flex-1 bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2 rounded-xl text-sm font-medium transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
