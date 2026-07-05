-- Migration: Enhance Gym model for Super Admin operations
-- Date: 2026-07-05
-- Description: Add status, subscription, approval, and metadata fields to gyms table

-- Add new columns to gyms table
ALTER TABLE gyms 
ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'Pending',
ADD COLUMN subscription_id INT,
ADD COLUMN approved_at DATETIME,
ADD COLUMN approved_by INT,
ADD COLUMN business_license VARCHAR(100),
ADD COLUMN owner_name VARCHAR(100),
ADD COLUMN website VARCHAR(255),
ADD COLUMN description TEXT,
ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;

-- Add foreign key constraints
ALTER TABLE gyms 
ADD CONSTRAINT fk_gym_subscription 
    FOREIGN KEY (subscription_id) REFERENCES gym_subscriptions(id),
ADD CONSTRAINT fk_gym_approved_by 
    FOREIGN KEY (approved_by) REFERENCES users(id);

-- Add indexes for performance
CREATE INDEX idx_gym_status ON gyms (status);
CREATE INDEX idx_gym_created_at ON gyms (created_at);
CREATE INDEX idx_gym_approved_at ON gyms (approved_at);

-- Update existing gyms to 'Active' status (assuming they were already operating)
-- In a real migration, this would depend on your business rules
UPDATE gyms SET status = 'Active' WHERE status = 'Pending';