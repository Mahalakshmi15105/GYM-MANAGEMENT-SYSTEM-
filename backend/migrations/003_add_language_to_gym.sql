-- Add language field to gym table
-- Migration: 003_add_language_to_gym.sql
-- Date: 2026-07-09
-- Purpose: Add language support for multi-language gym portal

-- Add language column to gym table
ALTER TABLE gym ADD COLUMN language VARCHAR(5) DEFAULT 'en';

-- Create index for language field for better performance
CREATE INDEX idx_gym_language ON gym(language);

-- Update existing gyms to have default language
UPDATE gym SET language = 'en' WHERE language IS NULL;

-- Add constraint to ensure only supported languages
ALTER TABLE gym ADD CONSTRAINT chk_gym_language 
    CHECK (language IN ('en', 'ta', 'hi', 'ja', 'fr', 'de', 'es', 'ar', 'zh', 'ko', 'pt', 'it', 'ru'));