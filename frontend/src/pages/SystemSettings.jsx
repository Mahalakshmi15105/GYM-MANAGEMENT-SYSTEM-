import React, { useState, useEffect } from "react";
import { AdminActionModal, AdminMetricCard } from "../components/admin";
import api from "../services/api";
import {
  CheckCircleIcon,
  XCircleIcon,
  Cog6ToothIcon,
  ChartBarIcon,
  BellIcon,
} from "@heroicons/react/24/outline";

const SystemSettings = () => {
  const [settings, setSettings] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [modalState, setModalState] = useState({
    isOpen: false,
    setting: null,
  });
  const [editValues, setEditValues] = useState({});

  const settingsCategories = {
    features: {
      label: "Platform Features",
      icon: <Cog6ToothIcon className="w-6 h-6" />,
      color: "blue",
    },
    limits: {
      label: "System Limits",
      icon: <ChartBarIcon className="w-6 h-6" />,
      color: "orange",
    },
    notifications: {
      label: "Notifications",
      icon: <BellIcon className="w-6 h-6" />,
      color: "green",
    },
  };

  const mockSettings = {
    "features.gym_approval_required": {
      value: "true",
      type: "boolean",
      category: "features",
      description: "Require admin approval for new gyms",
    },
    "limits.max_members_per_gym": {
      value: "1000",
      type: "number",
      category: "limits",
      description: "Maximum members per gym",
    },
    "notifications.email_enabled": {
      value: "true",
      type: "boolean",
      category: "notifications",
      description: "Enable email notifications",
    },
  };

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      setLoading(true);
      setSettings(mockSettings);
      setError(null);
    } catch (err) {
      setError(err.response?.data?.error || "Failed to load settings");
    } finally {
      setLoading(false);
    }
  };

  const handleSaveSetting = async (key, value) => {
    try {
      await api.put(`/api/admin/settings/${key}`, { setting_value: value });
      setSettings((prev) => ({ ...prev, [key]: { ...prev[key], value } }));
      setModalState({ isOpen: false, setting: null });
    } catch (err) {
      setError(err.response?.data?.error || "Failed to update setting");
    }
  };

  const renderSettingValue = (setting) => {
    if (setting.type === "boolean") {
      return (
        <span className="flex items-center gap-1">
          {setting.value === "true" ? (
            <>
              <CheckCircleIcon className="w-4 h-4 text-green-600" />
              Enabled
            </>
          ) : (
            <>
              <XCircleIcon className="w-4 h-4 text-red-600" />
              Disabled
            </>
          )}
        </span>
      );
    }
    return setting.value;
  };

  const renderEditForm = (key, setting) => {
    if (setting.type === "boolean") {
      return (
        <select
          value={editValues[key] || setting.value}
          onChange={(e) =>
            setEditValues((prev) => ({ ...prev, [key]: e.target.value }))
          }
          className="w-full p-2 border border-gray-300 rounded-md"
        >
          <option value="true">Enabled</option>
          <option value="false">Disabled</option>
        </select>
      );
    }

    return (
      <input
        type={setting.type === "number" ? "number" : "text"}
        value={editValues[key] || setting.value}
        onChange={(e) =>
          setEditValues((prev) => ({ ...prev, [key]: e.target.value }))
        }
        className="w-full p-2 border border-gray-300 rounded-md"
      />
    );
  };

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-7xl mx-auto">
          <div className="bg-red-50 border border-red-200 rounded-2xl p-8 text-center">
            <h2 className="text-xl font-semibold text-red-900 mb-2">
              Error Loading Settings
            </h2>
            <p className="text-red-700 mb-4">{error}</p>
            <button
              onClick={fetchSettings}
              className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600"
            >
              Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        <div className="bg-white rounded-2xl border border-gray-200 p-6 shadow-sm">
          <h1 className="text-3xl font-bold text-gray-900 mb-2 flex items-center gap-2">
            <Cog6ToothIcon className="w-8 h-8" />
            System Settings
          </h1>
          <p className="text-gray-600">
            Configure platform-wide settings and system parameters
          </p>
        </div>

        {/* Categories Overview */}
        <section>
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Settings Categories
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            {Object.entries(settingsCategories).map(([category, config]) => {
              const categorySettings = Object.entries(settings).filter(
                ([_, setting]) => setting.category === category,
              );
              return (
                <AdminMetricCard
                  key={category}
                  title={config.label}
                  value={categorySettings.length}
                  subtitle="settings"
                  icon={config.icon}
                  color={config.color}
                />
              );
            })}
          </div>
        </section>

        {/* Settings by Category */}
        {Object.entries(settingsCategories).map(([category, config]) => {
          const categorySettings = Object.entries(settings).filter(
            ([_, setting]) => setting.category === category,
          );

          if (categorySettings.length === 0) return null;

          return (
            <section key={category}>
              <div className="flex items-center gap-3 mb-4">
                {config.icon}
                <h2 className="text-xl font-semibold text-gray-900">
                  {config.label}
                </h2>
              </div>

              <div className="bg-white rounded-2xl border border-gray-200 shadow-sm">
                <div className="divide-y divide-gray-200">
                  {categorySettings.map(([key, setting]) => (
                    <div
                      key={key}
                      className="p-6 flex items-center justify-between"
                    >
                      <div className="flex-1">
                        <h3 className="text-sm font-medium text-gray-900 mb-1">
                          {key
                            .split(".")
                            .pop()
                            .replace(/_/g, " ")
                            .replace(/\b\w/g, (l) => l.toUpperCase())}
                        </h3>
                        <p className="text-sm text-gray-600 mb-2">
                          {setting.description}
                        </p>
                        <div className="text-sm font-mono bg-gray-100 px-2 py-1 rounded">
                          {renderSettingValue(setting)}
                        </div>
                      </div>
                      <button
                        onClick={() =>
                          setModalState({
                            isOpen: true,
                            setting: { key, ...setting },
                          })
                        }
                        className="ml-4 px-3 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 text-sm"
                      >
                        Edit
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            </section>
          );
        })}
      </div>

      {/* Edit Setting Modal */}
      <AdminActionModal
        isOpen={modalState.isOpen}
        onClose={() => setModalState({ isOpen: false, setting: null })}
        onConfirm={() =>
          handleSaveSetting(
            modalState.setting?.key,
            editValues[modalState.setting?.key] || modalState.setting?.value,
          )
        }
        title="Edit Setting"
        message={`Update ${modalState.setting?.key?.split(".").pop()?.replace(/_/g, " ")}`}
        confirmText="Save Changes"
        type="info"
      >
        {modalState.setting && (
          <div className="mt-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {modalState.setting.description}
            </label>
            {renderEditForm(modalState.setting.key, modalState.setting)}
          </div>
        )}
      </AdminActionModal>
    </div>
  );
};

export default SystemSettings;
