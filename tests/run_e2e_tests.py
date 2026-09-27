#!/usr/bin/env python3
"""Master E2E Test Runner for Kinh thánh Chấn thương Chỉnh hình (Campbell 13th Ed).

Executes the complete opaque-box requirement-driven test suite across all 4 tiers:
- Tier 1: Feature & Catalog Coverage
- Tier 2: Boundary & Corner Cases
- Tier 3: Cross-Feature Integration
- Tier 4: Real-World Clinical Workload Scenarios

Usage:
    python tests/run_e2e_tests.py
    python tests/run_e2e_tests.py --tier 1
    python tests/run_e2e_tests.py --live-url http://localhost:8000
    python tests/run_e2e_tests.py --json test_results.json
"""

import argparse
import json
import os
import sys
import time
import unittest

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Import test suites
from tests.test_e2e_guidemap import TestE2EGuidemap
from tests.test_e2e_search import TestE2ESearch
from tests.test_e2e_viewer import TestE2EViewer
from tests.test_e2e_classifications import TestE2EClassifications
from tests.test_e2e_audit import TestE2EAudit
from tests.test_e2e_clinical_scenarios import TestE2EClinicalScenarios


ALL_TEST_CLASSES = [
    TestE2EGuidemap,
    TestE2ESearch,
    TestE2EViewer,
    TestE2EClassifications,
    TestE2EAudit,
    TestE2EClinicalScenarios
]


def classify_tier(test_name: str) -> str:
    """Classify test into Tier 1, 2, 3, or 4 based on naming convention."""
    lower = test_name.lower()
    if "tier1" in lower:
        return "Tier 1: Feature Coverage"
    elif "tier2" in lower:
        return "Tier 2: Boundary & Corner Cases"
    elif "tier3" in lower:
        return "Tier 3: Cross-Feature Combinations"
    elif "tier4" in lower or "clinical_scenario" in lower:
        return "Tier 4: Clinical Workload Scenarios"
    return "Tier 1: Feature Coverage"


class TierTestResult(unittest.TestResult):
    """Custom TestResult collecting detailed tier metrics and execution stats."""

    def __init__(self):
        super().__init__()
        self.results_by_tier = {
            "Tier 1: Feature Coverage": {"passed": 0, "failed": 0, "skipped": 0, "tests": []},
            "Tier 2: Boundary & Corner Cases": {"passed": 0, "failed": 0, "skipped": 0, "tests": []},
            "Tier 3: Cross-Feature Combinations": {"passed": 0, "failed": 0, "skipped": 0, "tests": []},
            "Tier 4: Clinical Workload Scenarios": {"passed": 0, "failed": 0, "skipped": 0, "tests": []}
        }
        self.test_timings = {}
        self._current_test_start = None

    def startTest(self, test):
        super().startTest(test)
        self._current_test_start = time.perf_counter()

    def addSuccess(self, test):
        super().addSuccess(test)
        duration_ms = (time.perf_counter() - self._current_test_start) * 1000.0
        tier = classify_tier(test._testMethodName)
        self.results_by_tier[tier]["passed"] += 1
        self.results_by_tier[tier]["tests"].append({
            "name": f"{test.__class__.__name__}.{test._testMethodName}",
            "status": "PASSED",
            "duration_ms": round(duration_ms, 2)
        })

    def addFailure(self, test, err):
        super().addFailure(test, err)
        duration_ms = (time.perf_counter() - self._current_test_start) * 1000.0
        tier = classify_tier(test._testMethodName)
        self.results_by_tier[tier]["failed"] += 1
        self.results_by_tier[tier]["tests"].append({
            "name": f"{test.__class__.__name__}.{test._testMethodName}",
            "status": "FAILED",
            "error": str(err[1]),
            "duration_ms": round(duration_ms, 2)
        })

    def addError(self, test, err):
        super().addError(test, err)
        duration_ms = (time.perf_counter() - self._current_test_start) * 1000.0
        tier = classify_tier(test._testMethodName)
        self.results_by_tier[tier]["failed"] += 1
        self.results_by_tier[tier]["tests"].append({
            "name": f"{test.__class__.__name__}.{test._testMethodName}",
            "status": "ERROR",
            "error": str(err[1]),
            "duration_ms": round(duration_ms, 2)
        })

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        tier = classify_tier(test._testMethodName)
        self.results_by_tier[tier]["skipped"] += 1
        self.results_by_tier[tier]["tests"].append({
            "name": f"{test.__class__.__name__}.{test._testMethodName}",
            "status": "SKIPPED",
            "reason": reason,
            "duration_ms": 0.0
        })


def run_e2e_suite(tier_filter=None, live_url=None, json_report_path=None, verbose=False):
    """Run all tests or filtered tier tests, print formatted summary, export JSON if requested."""
    if live_url:
        os.environ["CAMBELL_BASE_URL"] = live_url
        print(f"[*] Target mode: LIVE HTTP Server at {live_url}")
    else:
        print("[*] Target mode: IN-PROCESS ASGI via FastAPI TestClient")

    suite = unittest.TestSuite()
    loader = unittest.TestLoader()

    for test_class in ALL_TEST_CLASSES:
        tests = loader.loadTestsFromTestCase(test_class)
        for t in tests:
            t_tier = classify_tier(t._testMethodName)
            if tier_filter is not None:
                tier_num = f"Tier {tier_filter}"
                if tier_num not in t_tier:
                    continue
            suite.addTest(t)

    total_tests = suite.countTestCases()
    print(f"[*] Discovered {total_tests} E2E test cases across 6 test modules.")
    print("=" * 75)

    result = TierTestResult()
    start_time = time.perf_counter()
    suite.run(result)
    total_duration_sec = time.perf_counter() - start_time

    # Display report per Tier
    print(f"\n{'='*75}")
    print("           CAMPBELL 13TH ED - E2E TEST EXECUTION REPORT")
    print(f"{'='*75}\n")

    grand_passed = 0
    grand_failed = 0
    grand_skipped = 0

    for tier_name, tier_data in result.results_by_tier.items():
        if tier_filter and f"Tier {tier_filter}" not in tier_name:
            continue
        p = tier_data["passed"]
        f = tier_data["failed"]
        s = tier_data["skipped"]
        t = p + f + s
        grand_passed += p
        grand_failed += f
        grand_skipped += s

        status_flag = "[PASS]" if f == 0 else "[FAIL]"
        print(f"--- {tier_name} ({t} tests) {status_flag} ---")
        print(f"    Passed: {p} | Failed: {f} | Skipped (Pending): {s}")

        if verbose or f > 0:
            for item in tier_data["tests"]:
                st = item["status"]
                name = item["name"]
                dur = item["duration_ms"]
                if st == "PASSED" and verbose:
                    print(f"      + {st:7s} ({dur:6.1f} ms) {name}")
                elif st == "SKIPPED":
                    print(f"      * {st:7s} {name} -> {item.get('reason')}")
                elif st in ("FAILED", "ERROR"):
                    print(f"      ! {st:7s} ({dur:6.1f} ms) {name}")
                    err_lines = item.get("error", "").split("\n")
                    for el in err_lines[:3]:
                        print(f"          {el}")
        print()

    print(f"{'='*75}")
    print(f"GRAND TOTAL: {result.testsRun} tests run in {total_duration_sec:.2f}s")
    print(f"PASSED: {grand_passed} | FAILED: {grand_failed} | SKIPPED: {grand_skipped}")
    pass_rate = (grand_passed / result.testsRun * 100.0) if result.testsRun > 0 else 0.0
    print(f"SUCCESS RATE: {pass_rate:.1f}%")
    print(f"{'='*75}\n")

    if json_report_path:
        report_payload = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "total_duration_seconds": round(total_duration_sec, 3),
            "total_tests_run": result.testsRun,
            "grand_passed": grand_passed,
            "grand_failed": grand_failed,
            "grand_skipped": grand_skipped,
            "success_rate_percent": round(pass_rate, 2),
            "tiers": result.results_by_tier
        }
        with open(json_report_path, "w", encoding="utf-8") as jf:
            json.dump(report_payload, jf, indent=2, ensure_ascii=False)
        print(f"[+] JSON report saved to: {json_report_path}")

    return 0 if grand_failed == 0 else 1


def main():
    parser = argparse.ArgumentParser(description="Kinh thánh Chấn thương Chỉnh hình E2E Test Runner")
    parser.add_argument("--tier", type=int, choices=[1, 2, 3, 4], help="Run tests for specific tier only")
    parser.add_argument("--live-url", type=str, help="Target a live running server (e.g. http://localhost:8000)")
    parser.add_argument("--json", type=str, dest="json_path", help="Path to write JSON test report")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose test case logging")
    args = parser.parse_args()

    exit_code = run_e2e_suite(
        tier_filter=args.tier,
        live_url=args.live_url,
        json_report_path=args.json_path,
        verbose=args.verbose
    )
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
