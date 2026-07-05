-- Migration: Create Super Admin tables
-- Date: 2026-07-05
-- Description: Add SystemSettings, ActivityLog, and GymSubscription tables for Super Admin functionality

-- Create system_settings table
CREATE TABLE system_settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    setting_key VARCHAR(100) NOT NULL UNIQUE,
    setting_value TEXT NOT NULL,
    setting_type VARCHAR(20) NOT NULL,
    description TEXT,
    category VARCHAR(50) NOT NULL DEFAULT 'general',
    updated_by INT NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (updated_by) REFERENCES users(id),
    INDEX idx_setting_category (category),
    INDEX idx_setting_key (setting_key)
);

-- Create activity_logs table
CREATE TABLE activity_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    gym_id INT,
    action_type VARCHAR(50) NOT NULL,
    entity_type VARCHAR(50),
    entity_id INT,
    description TEXT NOT NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    request_method VARCHAR(10),
    request_path VARCHAR(255),
    extra_data JSON,
    severity VARCHAR(20) NOT NULL DEFAULT 'info',
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (gym_id) REFERENCES gyms(id),
    INDEX idx_timestamp (timestamp),
    INDEX idx_user_id_timestamp (user_id, timestamp),
    INDEX idx_gym_id_timestamp (gym_id, timestamp),
    INDEX idx_action_type_timestamp (action_type, timestamp),
    INDEX idx_entity_type_timestamp (entity_type, timestamp),
    INDEX idx_severity_timestamp (severity, timestamp)
);

-- Create gym_subscriptions table
CREATE TABLE gym_subscriptions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    gym_id INT NOT NULL UNIQUE,
    plan_name VARCHAR(100) NOT NULL,
    monthly_price DECIMAL(10,2) NOT NULL,
    max_members INT NOT NULL DEFAULT 100,
    max_trainers INT NOT NULL DEFAULT 5,
    features JSON,
    billing_cycle_start DATE NOT NULL,
    billing_cycle_end DATE NOT NULL,
    next_billing_date DATE NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'Active',
    auto_renew BOOLEAN DEFAULT TRUE,
    last_payment_date DATE,
    last_payment_amount DECIMAL(10,2),
    payment_method VARCHAR(50),
    created_by INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (gym_id) REFERENCES gyms(id),
    FOREIGN KEY (created_by) REFERENCES users(id),
    INDEX idx_status (status),
    INDEX idx_next_billing_date (next_billing_date),
    INDEX idx_billing_cycle (billing_cycle_start, billing_cycle_end)
);

-- Insert default system settings
INSERT INTO system_settings (setting_key, setting_value, setting_type, description, category, updated_by) VALUES
('max_gyms_per_month', '50', 'number', 'Maximum number of new gym registrations allowed per month', 'limits', 1),
('platform_maintenance_mode', 'false', 'boolean', 'Enable platform-wide maintenance mode', 'system', 1),
('default_trial_period_days', '30', 'number', 'Default trial period for new gym registrations', 'billing', 1),
('support_email', 'support@flexigym.com', 'string', 'Platform support contact email', 'contact', 1),
('require_gym_approval', 'true', 'boolean', 'Require Super Admin approval for new gym registrations', 'security', 1);