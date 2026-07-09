-- Migration: Add logo field to gyms table
-- This migration adds a logo column to store gym logo file paths

ALTER TABLE gyms ADD COLUMN logo VARCHAR(500) NULL;

-- Add comment for clarity
ALTER TABLE gyms MODIFY COLUMN logo VARCHAR(500) NULL COMMENT 'Path to gym logo image file';