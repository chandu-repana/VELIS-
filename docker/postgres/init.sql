-- VELIS Database Initialization
-- This runs once when the PostgreSQL container first starts

-- Enable UUID extension for future use
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Set timezone
SET timezone = 'UTC';
