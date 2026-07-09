-- Migration: Add currency column to gyms table
-- Description: Add currency support per gym for multi-tenant currency isolation
-- Date: 2026-07-09

ALTER TABLE gyms 
ADD COLUMN currency VARCHAR(3) DEFAULT 'INR' AFTER logo;

-- Update existing gyms to have default currency
UPDATE gyms SET currency = 'INR' WHERE currency IS NULL;

-- Add index for faster queries
CREATE INDEX idx_gyms_currency ON gyms(currency);
