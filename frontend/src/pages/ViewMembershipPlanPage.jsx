import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../services/api';
import {
  ArrowLeftIcon,
  CreditCardIcon,
  DocumentTextIcon,
  ChartBarIcon,
  ClockIcon,
  ShieldCheckIcon
} from '@heroicons/react/24/outline';

export default function ViewMembershipPlanPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [plan, setPlan] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchPlan();
  }, [id]);

  const fetchPlan = async () => {
    try {
      const response = await api.get(`/api/membership-plans/${id}`);
      setPlan(response.data.membership_plan);
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.error || 'Failed to fetch membership plan details');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Not provided';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatPrice = (price) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(price);
  };

  const formatDuration = (days) => {
    if (days === 7) return '1 Week';
    if (days === 30) return '1 Month';
    if (days === 90) return '3 Months';
    if (days === 180) return '6 Months';
    if (days === 365) return '1 Year';
    if (days < 30) return `${days} Days`;
    if (days % 30 === 0) return `${days / 30} Months`;
    return `${days} Days`;
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'Active':
        return 'bg-green-50 text-green-700 border-green-200';
      case 'Inactive':
        return 'bg-gray-50 text-gray-600 border-gray-200';
      default:
        return 'bg-gray-50 text-gray-600 border-gray-200';
    }
  };

  if (loading) {
    return (
      <div className="space-y-8">
        <div className="flex items-center justify-center py-12">
          <div className="text-gray-600">Loading membership plan details...</div>
        </div>
      </div>
    );
  }

  if (error || !plan) {
    return (
      <div className="space-y-8">
        <div className="bg-red-50 border border-red-200 text-red-700 text-sm p-4 rounded-xl">
          {error || 'Membership plan not found'}
        </div>
        <button
          onClick={() => navigate('/membership-plans')}
          className="bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2 rounded-xl text-sm font-medium transition-colors flex items-center gap-2"
        >
          <ArrowLeftIcon className="w-4 h-4" /> Back to Plans
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
            {plan.plan_name}
          </h1>
          <p className="text-sm text-gray-600">Membership Plan Details</p>
        </div>
        <div className="flex flex-wrap gap-3">
          <button
            onClick={() => navigate(`/membership-plans/${id}/edit`)}
            className="bg-orange-600 hover:bg-orange-700 text-white px-4 py-2 rounded-xl text-sm font-medium transition-colors"
          >
            Edit Plan
          </button>
          <button
            onClick={() => navigate('/membership-plans')}
            className="bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2 rounded-xl text-sm font-medium transition-colors flex items-center gap-2"
          >
            <ArrowLeftIcon className="w-4 h-4" /> Back to Plans
          </button>
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-8">
        {/* Main Information */}
        <div className="lg:col-span-2 space-y-6">
          {/* Plan Details */}
          <div className="bg-white border border-gray-200 p-6 rounded-2xl shadow-sm">
            <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
              <CreditCardIcon className="w-5 h-5 text-orange-500" /> Plan Information
            </h2>
            <div className="grid md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <div>
                  <label className="text-xs uppercase font-semibold tracking-wider text-gray-600">Plan Name</label>
                  <p className="text-gray-900 font-medium text-lg">{plan.plan_name}</p>
                </div>
                <div>
                  <label className="text-xs uppercase font-semibold tracking-wider text-gray-600">Duration</label>
                  <p className="text-gray-900 font-medium">
                    {formatDuration(plan.duration)} 
                    <span className="text-gray-500 text-sm ml-2">({plan.duration} days)</span>
                  </p>
                </div>
              </div>
              <div className="space-y-4">
                <div>
                  <label className="text-xs uppercase font-semibold tracking-wider text-gray-600">Price</label>
                  <p className="text-gray-900 font-bold text-2xl text-orange-600">{formatPrice(plan.price)}</p>
                </div>
                <div>
                  <label className="text-xs uppercase font-semibold tracking-wider text-gray-600">Status</label>
                  <div className="mt-1">
                    <span className={`inline-flex px-3 py-1 rounded-full text-sm font-semibold border ${getStatusColor(plan.status)}`}>
                      {plan.status}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Description */}
          {plan.description && (
            <div className="bg-white border border-gray-200 p-6 rounded-2xl shadow-sm">
              <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                <DocumentTextIcon className="w-5 h-5 text-orange-500" /> Description
              </h2>
              <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">{plan.description}</p>
            </div>
          )}
        </div>

        {/* Sidebar Information */}
        <div className="space-y-6">
          {/* Quick Stats */}
          <div className="bg-white border border-gray-200 p-6 rounded-2xl shadow-sm">
            <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
              <ChartBarIcon className="w-5 h-5 text-orange-500" /> Quick Stats
            </h2>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-gray-600 text-sm">Price per Day</span>
                <span className="text-gray-900 font-medium">
                  {formatPrice(plan.price / plan.duration)}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600 text-sm">Price per Week</span>
                <span className="text-gray-900 font-medium">
                  {formatPrice((plan.price / plan.duration) * 7)}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600 text-sm">Price per Month</span>
                <span className="text-gray-900 font-medium">
                  {formatPrice((plan.price / plan.duration) * 30)}
                </span>
              </div>
            </div>
          </div>

          {/* Timestamps */}
          <div className="bg-white border border-gray-200 p-6 rounded-2xl shadow-sm">
            <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
              <ClockIcon className="w-5 h-5 text-orange-500" /> Timestamps
            </h2>
            <div className="space-y-3">
              <div>
                <label className="text-xs uppercase font-semibold tracking-wider text-gray-600">Created At</label>
                <p className="text-gray-900 text-sm">{formatDate(plan.created_at)}</p>
              </div>
              <div>
                <label className="text-xs uppercase font-semibold tracking-wider text-gray-600">Last Updated</label>
                <p className="text-gray-900 text-sm">{formatDate(plan.updated_at)}</p>
              </div>
            </div>
          </div>

          {/* Plan Icon */}
          <div className="bg-white border border-gray-200 p-6 rounded-2xl shadow-sm">
            <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
              <ShieldCheckIcon className="w-5 h-5 text-orange-500" /> Plan Icon
            </h2>
            <div className="w-32 h-32 bg-orange-100 border-2 border-orange-200 rounded-xl flex items-center justify-center mx-auto text-orange-600">
              <CreditCardIcon className="w-16 h-16" />
            </div>
            <p className="text-xs text-gray-500 text-center mt-2">Visual representation</p>
          </div>
        </div>
      </div>
    </div>
  );
}