import React from 'react';
import { ArrowTrendingUpIcon, ArrowTrendingDownIcon, ArrowRightIcon } from '@heroicons/react/24/outline';

/**
 * Reusable metric card component for Super Admin dashboard displays
 */
const AdminMetricCard = ({
  title,
  value,
  subtitle = null,
  icon = null,
  trend = null,
  trendDirection = null, // 'up', 'down', 'neutral'
  color = 'orange',
  loading = false,
  onClick = null,
  className = ""
}) => {
  const colorClasses = {
    orange: {
      bg: 'bg-orange-50',
      border: 'border-orange-200',
      icon: 'text-orange-600',
      value: 'text-orange-700',
      trend: {
        up: 'text-green-600 bg-green-50',
        down: 'text-red-600 bg-red-50',
        neutral: 'text-gray-600 bg-gray-50'
      }
    },
    blue: {
      bg: 'bg-blue-50',
      border: 'border-blue-200',
      icon: 'text-blue-600',
      value: 'text-blue-700',
      trend: {
        up: 'text-green-600 bg-green-50',
        down: 'text-red-600 bg-red-50',
        neutral: 'text-gray-600 bg-gray-50'
      }
    },
    green: {
      bg: 'bg-green-50',
      border: 'border-green-200',
      icon: 'text-green-600',
      value: 'text-green-700',
      trend: {
        up: 'text-green-600 bg-green-50',
        down: 'text-red-600 bg-red-50',
        neutral: 'text-gray-600 bg-gray-50'
      }
    },
    red: {
      bg: 'bg-red-50',
      border: 'border-red-200',
      icon: 'text-red-600',
      value: 'text-red-700',
      trend: {
        up: 'text-green-600 bg-green-50',
        down: 'text-red-600 bg-red-50',
        neutral: 'text-gray-600 bg-gray-50'
      }
    }
  };

  const styles = colorClasses[color] || colorClasses.orange;

  const renderTrendIcon = () => {
    if (!trendDirection) return null;
    
    const icons = {
      up: <ArrowTrendingUpIcon className="w-3 h-3" />,
      down: <ArrowTrendingDownIcon className="w-3 h-3" />,
      neutral: <ArrowRightIcon className="w-3 h-3" />
    };
    
    return icons[trendDirection];
  };

  return (
    <div
      className={`
        ${styles.bg} ${styles.border} border rounded-2xl p-6 
        ${onClick ? 'cursor-pointer hover:shadow-md transform hover:scale-105' : ''} 
        transition-all duration-200 ${className}
      `}
      onClick={onClick}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-medium text-gray-600">{title}</h3>
        {icon && (
          <div className={`w-10 h-10 ${styles.bg} ${styles.border} border rounded-xl flex items-center justify-center ${styles.icon}`}>
            {typeof icon === 'string' ? (
              <span className="text-lg">{icon}</span>
            ) : (
              icon
            )}
          </div>
        )}
      </div>

      {/* Value */}
      <div className="mb-2">
        {loading ? (
          <div className="h-8 bg-gray-200 rounded animate-pulse"></div>
        ) : (
          <p className={`text-2xl font-bold ${styles.value}`}>
            {typeof value === 'number' ? value.toLocaleString() : value}
          </p>
        )}
      </div>

      {/* Subtitle and Trend */}
      <div className="flex items-center justify-between">
        {subtitle && (
          <p className="text-sm text-gray-500">{subtitle}</p>
        )}
        
        {trend && trendDirection && (
          <div className={`
            inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium
            ${styles.trend[trendDirection]}
          `}>
            <span>{renderTrendIcon()}</span>
            <span>{trend}</span>
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminMetricCard;