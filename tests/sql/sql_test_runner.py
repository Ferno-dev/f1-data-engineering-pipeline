"""
SQL Test Runner for F1 Data Pipeline

Executes SQL validation tests against Parquet data files using DuckDB.
Validates data quality, constraints, and correctness.

Part 3: Data Validation with SQL
"""

import logging
import re
from pathlib import Path
from typing import Dict, List, Any

try:
    import duckdb
except ImportError:
    raise ImportError("DuckDB is required for SQL tests. Install with: uv add duckdb")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent.parent
TESTS_SQL_DIR = PROJECT_ROOT / "tests" / "sql"
DATA_RAW_DIR = PROJECT_ROOT / "data" / "raw"


def _extract_test_name_from_query(query: str) -> str | None:
    """
    Extract test name from SQL query's SELECT statement.
    
    Looks for pattern: 'TEST_*' as test_name
    
    Args:
        query: SQL query string
        
    Returns:
        Extracted test name or None
    """
    # Match: 'TEST_*' as test_name
    match = re.search(r"'(TEST_[A-Z0-9_]+)'\s+as\s+test_name", query, re.IGNORECASE)
    if match:
        return match.group(1)
    return None


class SQLTestRunner:
    """Executes SQL test files against Parquet datasets using DuckDB."""

    def __init__(self, test_dir: Path = TESTS_SQL_DIR, data_dir: Path = DATA_RAW_DIR):
        self.test_dir = test_dir
        self.data_dir = data_dir
        self.conn = duckdb.connect(":memory:")
        self.results: List[Dict[str, Any]] = []

    def run_test_file(self, filename: str) -> List[Dict[str, Any]]:
        """
        Execute all tests in a SQL file.

        Args:
            filename: Name of SQL test file (e.g., 'test_drivers.sql')

        Returns:
            List of test results with pass/fail status
        """
        test_file = self.test_dir / filename
        if not test_file.exists():
            logger.error(f"Test file not found: {test_file}")
            return []

        logger.info(f"Running SQL tests from {filename}")
        test_results = []

        with open(test_file, "r") as f:
            content = f.read()

        # Split SQL file by test sections (comments with TEST N:)
        test_queries = self._parse_test_queries(content)

        for test_name, query in test_queries:
            try:
                result = self.conn.execute(query).fetchall()
                
                # Extract test result
                if result:
                    row = result[0]
                    # Convert to dict if tuple
                    if isinstance(row, tuple):
                        row_dict = self._result_tuple_to_dict(row, query)
                    else:
                        row_dict = row

                    test_status = "PASS" if "PASS" in str(row_dict.get("status", "")) else "FAIL"
                    test_result = {
                        "test_name": test_name,
                        "file": filename,
                        "status": test_status,
                        "details": row_dict,
                    }
                    test_results.append(test_result)
                    logger.info(f"  {test_name}: {test_status}")
                else:
                    test_result = {
                        "test_name": test_name,
                        "file": filename,
                        "status": "PASS",  # Empty result set = no violations
                        "details": {"message": "No violations found"},
                    }
                    test_results.append(test_result)
                    logger.info(f"  {test_name}: PASS (no violations)")

            except Exception as e:
                logger.error(f"  {test_name}: ERROR - {str(e)}")
                test_result = {
                    "test_name": test_name,
                    "file": filename,
                    "status": "ERROR",
                    "details": {"error": str(e)},
                }
                test_results.append(test_result)

        return test_results

    def run_all_tests(self) -> Dict[str, Any]:
        """
        Execute all SQL test files.

        Returns:
            Summary with pass/fail counts and detailed results
        """
        logger.info("=" * 70)
        logger.info("PART 3: Data Validation - SQL Test Suite")
        logger.info("=" * 70)

        all_results = []
        test_files = ["test_drivers.sql", "test_laps.sql"]

        for test_file in test_files:
            file_path = self.test_dir / test_file
            if file_path.exists():
                results = self.run_test_file(test_file)
                all_results.extend(results)
            else:
                logger.warning(f"Skipping missing test file: {test_file}")

        # Calculate summary
        passed = sum(1 for r in all_results if r["status"] == "PASS")
        failed = sum(1 for r in all_results if r["status"] == "FAIL")
        errors = sum(1 for r in all_results if r["status"] == "ERROR")
        total = len(all_results)

        summary = {
            "total_tests": total,
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "success_rate": f"{(passed / total * 100):.1f}%" if total > 0 else "0%",
            "results": all_results,
        }

        logger.info("=" * 70)
        logger.info(f"Test Results: {passed}/{total} passed, {failed} failed, {errors} errors")
        logger.info(f"Success Rate: {summary['success_rate']}")
        logger.info("=" * 70)

        return summary

    @staticmethod
    def _parse_test_queries(content: str) -> List[tuple]:
        """
        Parse SQL file into individual test queries.

        Splits on '-- TEST N:' comments to identify separate tests,
        and extracts test name from the SELECT statement.

        Args:
            content: Full SQL file content

        Returns:
            List of (test_name, query) tuples
        """
        tests = []
        lines = content.split("\n")
        current_test = None
        current_query = []
        test_counter = 0

        for line in lines:
            # Detect test marker
            if "-- TEST" in line and ":" in line:
                # Save previous test
                if current_test and current_query:
                    query_text = "\n".join(current_query).strip()
                    if query_text:
                        # Extract test name from query if available
                        extracted_name = _extract_test_name_from_query(query_text)
                        test_name = extracted_name or current_test
                        tests.append((test_name, query_text))

                # Start new test - extract number from "-- TEST N:"
                test_counter += 1
                current_test = f"TEST_{test_counter}"  # Fallback name
                current_query = []
            elif current_test:
                # Include all lines except comment-only header lines
                if line.strip() and not line.strip().startswith("--"):
                    current_query.append(line)
                elif line.strip().startswith("--") and "=====" not in line and "TEST" not in line:
                    # Include descriptive comments but not section headers
                    current_query.append(line)

        # Don't forget the last test
        if current_test and current_query:
            query_text = "\n".join(current_query).strip()
            if query_text:
                extracted_name = _extract_test_name_from_query(query_text)
                test_name = extracted_name or current_test
                tests.append((test_name, query_text))

        return tests

    @staticmethod
    def _result_tuple_to_dict(row: tuple, query: str) -> Dict[str, Any]:
        """Convert DuckDB result tuple to dictionary using column names."""
        try:
            # Extract column names from SELECT clause
            if "SELECT" in query.upper():
                select_part = query[query.upper().find("SELECT"):query.upper().find("FROM")]
                columns = [col.strip().split(" as ")[-1].strip() 
                          for col in select_part.replace("SELECT", "").split(",")]
                return dict(zip(columns, row))
        except Exception:
            pass
        
        # Fallback: return as generic dict
        return {"value": row}


def run_sql_tests() -> bool:
    """
    Execute all SQL tests and return True if all pass.

    Returns:
        True if all tests passed, False otherwise
    """
    runner = SQLTestRunner()
    summary = runner.run_all_tests()
    
    # Return True if no failures or errors
    return summary["failed"] == 0 and summary["errors"] == 0


if __name__ == "__main__":
    # Direct execution
    success = run_sql_tests()
    exit(0 if success else 1)
