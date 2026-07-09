import React, { useEffect } from 'react';
import { ExclamationTriangleIcon, TrashIcon, InformationCircleIcon } from '@heroicons/react/24/outline';

/**
 * Reusable confirmation modal component for destructive Super Admin actions
 */
const AdminActionModal = ({
  isOpen,
  onClose,
  onConfirm,
  title,
  message,
  confirmText = "Confirm",
  cancelText = "Cancel",
  type = "warning", // 'warning', 'danger', 'info'
  loading = false,
  children = null
}) => {
  // Handle escape key to close modal
  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      document.body.style.overflow = 'hidden'; // Prevent background scrolling
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const typeStyles = {
    warning: {
      iconBg: 'bg-yellow-100',
      iconColor: 'text-yellow-600',
      icon: <ExclamationTriangleIcon className="w-6 h-6" />,
      confirmBtn: 'bg-yellow-500 hover:bg-yellow-600 focus:ring-yellow-500'
    },
    danger: {
      iconBg: 'bg-red-100',
      iconColor: 'text-red-600',
      icon: <TrashIcon className="w-6 h-6" />,
      confirmBtn: 'bg-red-500 hover:bg-red-600 focus:ring-red-500'
    },
    info: {
      iconBg: 'bg-blue-100',
      iconColor: 'text-blue-600',
      icon: <InformationCircleIcon className="w-6 h-6" />,
      confirmBtn: 'bg-orange-500 hover:bg-orange-600 focus:ring-orange-500'
    }
  };

  const styles = typeStyles[type] || typeStyles.warning;

  const handleSubmit = (e) => {
    e.preventDefault();
    if (onConfirm && !loading) {
      if (children) {
        const formData = new FormData(e.target);
        const data = Object.fromEntries(formData.entries());
        onConfirm(data);
      } else {
        onConfirm();
      }
    }
  };

  const handleBackdropClick = (e) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <div 
      className="fixed inset-0 bg-black bg-opacity-50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
      onClick={handleBackdropClick}
    >
      <div 
        className="bg-white rounded-2xl shadow-xl max-w-md w-full max-h-screen overflow-y-auto"
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-title"
      >
        <form onSubmit={handleSubmit}>
          <div className="p-6">
            {/* Icon and Title */}
            <div className="flex items-start gap-4 mb-4">
              <div className={`w-12 h-12 ${styles.iconBg} ${styles.iconColor} rounded-xl flex items-center justify-center flex-shrink-0`}>
                {styles.icon}
              </div>
              <div className="flex-1 min-w-0">
                <h3 id="modal-title" className="text-lg font-semibold text-gray-900 mb-2">
                  {title}
                </h3>
                {message && (
                  <p className="text-sm text-gray-600 leading-relaxed">
                    {message}
                  </p>
                )}
              </div>
            </div>

            {/* Custom Content */}
            {children && (
              <div className="mb-6">
                {children}
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex items-center gap-3 justify-end">
              <button
                type="button"
                onClick={onClose}
                disabled={loading}
                className="px-4 py-2 text-sm font-medium text-gray-600 bg-gray-100 border border-gray-200 rounded-lg hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {cancelText}
              </button>
              <button
                type="submit"
                disabled={loading}
                className={`
                  px-4 py-2 text-sm font-medium text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors
                  ${styles.confirmBtn}
                `}
              >
                {loading ? (
                  <div className="flex items-center gap-2">
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    Processing...
                  </div>
                ) : (
                  confirmText
                )}
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AdminActionModal;