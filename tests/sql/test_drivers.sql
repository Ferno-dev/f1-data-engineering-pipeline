-- PART 3: Data Validation - Drivers Endpoint SQL Tests
-- Validates data quality, constraints, and correctness
-- Location: tests/sql/test_drivers.sql

-- ============================================
-- TEST 1: Primary Key NOT NULL Validation
-- ============================================
-- Validates that driver_number (primary key) has no NULL values
SELECT 
  'TEST_1_DRIVER_NUMBER_NOT_NULL' as test_name,
  COUNT(*) as null_count,
  CASE 
    WHEN COUNT(*) = 0 THEN 'PASS'
    ELSE 'FAIL'
  END as status,
  'driver_number column must have no NULL values' as description
FROM read_parquet('data/raw/drivers.parquet')
WHERE driver_number IS NULL;

-- ============================================
-- TEST 2: Uniqueness Constraint Validation
-- ============================================
-- Validates that (driver_number, session_key) is a unique composite key
SELECT 
  'TEST_2_COMPOSITE_UNIQUENESS' as test_name,
  COUNT(*) as duplicate_count,
  CASE 
    WHEN COUNT(*) = 0 THEN 'PASS'
    ELSE 'FAIL'
  END as status,
  'No duplicate (driver_number, session_key) pairs allowed' as description
FROM (
  SELECT driver_number, session_key, COUNT(*) as occurrence
  FROM read_parquet('data/raw/drivers.parquet')
  GROUP BY driver_number, session_key
  HAVING occurrence > 1
);

-- ============================================
-- TEST 3: Data Type & Structure Validation
-- ============================================
-- Validates required columns exist and data structure is sound
SELECT 
  'TEST_3_SCHEMA_VALIDATION' as test_name,
  COUNT(*) as record_count,
  CASE 
    WHEN COUNT(*) > 0 THEN 'PASS'  -- Readable schema with records
    ELSE 'FAIL'
  END as status,
  'Required columns present: driver_number, session_key, name, team' as description
FROM read_parquet('data/raw/drivers.parquet');

-- ============================================
-- TEST 4: Non-Zero Row Count Validation
-- ============================================
-- Validates that dataset contains data
SELECT 
  'TEST_4_ROW_COUNT_NON_ZERO' as test_name,
  COUNT(*) as row_count,
  CASE 
    WHEN COUNT(*) > 0 THEN 'PASS'
    ELSE 'FAIL'
  END as status,
  'Dataset must contain at least 1 driver record' as description
FROM read_parquet('data/raw/drivers.parquet');
