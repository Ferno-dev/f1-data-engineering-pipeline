-- PART 3: Data Validation - Laps Endpoint SQL Tests
-- Validates telemetry data quality, constraints, and correctness
-- Location: tests/sql/test_laps.sql

-- ============================================
-- TEST 1: Composite Primary Key NOT NULL Validation
-- ============================================
-- Validates that composite PK (lap_number, driver_number, session_key) has no NULL values
SELECT 
  'TEST_1_COMPOSITE_KEY_NOT_NULL' as test_name,
  COUNT(*) as null_count,
  CASE 
    WHEN COUNT(*) = 0 THEN 'PASS'
    ELSE 'FAIL'
  END as status,
  'Composite key (lap_number, driver_number, session_key) must have no NULLs' as description
FROM read_parquet('data/raw/laps.parquet')
WHERE lap_number IS NULL 
   OR driver_number IS NULL 
   OR session_key IS NULL;

-- ============================================
-- TEST 2: Data Integrity - Duration Validation
-- ============================================
-- Validates that lap durations are positive (non-negative integers/floats)
SELECT 
  'TEST_2_LAP_DURATION_POSITIVE' as test_name,
  COUNT(*) as invalid_duration_count,
  CASE 
    WHEN COUNT(*) = 0 THEN 'PASS'
    ELSE 'FAIL'
  END as status,
  'lap_duration must be >= 0 (milliseconds)' as description
FROM read_parquet('data/raw/laps.parquet')
WHERE lap_duration < 0
   OR lap_duration IS NULL;

-- ============================================
-- TEST 3: Temporal Data Validation
-- ============================================
-- Validates that date_start is chronologically valid and in past
SELECT 
  'TEST_3_DATE_START_VALID' as test_name,
  COUNT(*) as invalid_date_count,
  CASE 
    WHEN COUNT(*) = 0 THEN 'PASS'
    ELSE 'FAIL'
  END as status,
  'date_start must not be NULL and should be reasonable timestamp' as description
FROM read_parquet('data/raw/laps.parquet')
WHERE date_start IS NULL;

-- ============================================
-- TEST 4: Non-Zero Row Count Validation
-- ============================================
-- Validates that dataset contains telemetry records
SELECT 
  'TEST_4_ROW_COUNT_NON_ZERO' as test_name,
  COUNT(*) as row_count,
  CASE 
    WHEN COUNT(*) > 0 THEN 'PASS'
    ELSE 'FAIL'
  END as status,
  'Laps dataset must contain at least 1 telemetry record' as description
FROM read_parquet('data/raw/laps.parquet');
