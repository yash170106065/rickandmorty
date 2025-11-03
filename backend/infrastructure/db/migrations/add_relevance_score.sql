-- Migration: Add relevance_score column to existing tables
-- Run this migration to add the new scoring metric

-- Add relevance_score to generated_content table
ALTER TABLE generated_content ADD COLUMN relevance_score REAL;

-- Add relevance_score to generations table
ALTER TABLE generations ADD COLUMN relevance_score REAL;

