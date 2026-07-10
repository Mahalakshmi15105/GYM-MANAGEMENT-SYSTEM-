-- Migration: Add attendance_qr to gyms table
-- Date: 2026-07-10
-- Description: Add unique attendance QR code column for gym attendance system

-- Add attendance_qr column to gyms table
ALTER TABLE gyms 
ADD COLUMN attendance_qr VARCHAR(255) UNIQUE;

-- Add index for performance
CREATE INDEX idx_gym_attendance_qr ON gyms(attendance_qr);
