"""Adversarial Frontend & Mobile Challenger (Challenger 2) Test Suite for Milestone 1.

Tests:
1. API Portal Filtering & Pagination Stress Testing:
   - Query /api/techniques with portal=spine-pelvis, general, upper, lower, invalid portals.
   - Verify non-empty, proper chapters, valid pagination bounds, edge cases.
2. Playwright Mobile Test on Viewport 390x844:
   - Verify modal opens for 6-2 (FAI), 6-4 (PAO), 55-1 (Femoral neck), 56-1 (Stoppa), 54-1 (Lateral malleolus).
   - Verify correct clinical content and absence of swapped/hallucinated content.
   - Verify 0 console errors and 0 page exceptions.
3. Micro-JSON Fetch Latency Benchmark (<50ms SLA):
   - Measure fetch latency across 20 random techniques in browser and HTTP client.
"""

import os
import sys
import time
import json
import random
import subprocess
import socket
import requests
from typing import Dict, Any, List

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

PORT = 8092
BASE_URL = f"http://127.0.0.1:{PORT}"
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

def wait_for_server(url: str, timeout: int = 15) -> bool:
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = requests.get(url, timeout=1)
            if r.status_code in [200, 404]:
                return True
        except Exception:
            time.sleep(0.3)
    return False

# ----------------------------------------------------------------------
# 1. API Portal Filtering & Pagination Stress Tests
# ----------------------------------------------------------------------
def test_portal_filtering_and_pagination():
    print("\n" + "=" * 70)
    print("TASK 1: API Portal Filtering & Pagination Stress Tests")
    print("=" * 70)

    # Load ground truth catalogs
    with open(os.path.join(ROOT_DIR, "data", "techniques_catalog.json"), "r", encoding="utf-8") as f:
        catalog = json.load(f)
    print(f"Loaded ground truth catalog: {len(catalog)} techniques")

    expected_portals = {
        "spine-pelvis": [37, 38, 39, 40, 41, 42, 43, 44, 55, 56],
        "general": [1, 2, 20, 21, 22, 23, 24, 25, 26, 27, 28, 48, 80],
        "upper": [12, 13, 14, 46, 47, 52, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79],
        "lower": [3, 4, 5, 6, 7, 8, 9, 10, 11, 45, 50, 51, 54, 55, 56, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89]
    }

    results = {}

    for portal_name, allowed_chapters in expected_portals.items():
        print(f"\n--- Testing portal='{portal_name}' ---")
        expected_chaps_set = set(allowed_chapters)
        expected_total = sum(1 for t in catalog if t["chapter"] in expected_chaps_set)
        print(f"Ground truth techniques for chapters {allowed_chapters}: {expected_total}")

        # Page 1
        res = requests.get(f"{BASE_URL}/api/techniques?portal={portal_name}&page=1&limit=25")
        assert res.status_code == 200, f"Expected 200, got {res.status_code}"
        data = res.json()

        total = data["total"]
        pages = data["pages"]
        items = data["items"]
        limit = data["limit"]
        page = data["page"]

        print(f"Response: total={total}, pages={pages}, page={page}, limit={limit}, items_len={len(items)}")

        assert total > 0, f"Expected non-empty for portal={portal_name}, got total=0"
        assert total == expected_total, f"Total mismatch for {portal_name}: got {total}, expected {expected_total}"
        assert len(items) == min(25, total), f"Item count mismatch on page 1: {len(items)}"
        assert pages == (total + 25 - 1) // 25, f"Pages calculation mismatch: {pages}"

        # Fetch and verify ALL pages to ensure zero chapter leakage
        collected_ids = []
        offending_chapters = []

        for p in range(1, pages + 1):
            page_res = requests.get(f"{BASE_URL}/api/techniques?portal={portal_name}&page={p}&limit=50")
            assert page_res.status_code == 200
            page_data = page_res.json()
            for it in page_data["items"]:
                collected_ids.append(it["tech_id"])
                if it["chapter"] not in expected_chaps_set:
                    offending_chapters.append((it["tech_id"], it["chapter"]))

        print(f"Scanned all {len(collected_ids)} techniques across {pages} pages for {portal_name}.")
        assert len(offending_chapters) == 0, f"Offending chapters leaked in {portal_name}: {offending_chapters}"
        assert len(collected_ids) == total, f"Total items collected ({len(collected_ids)}) != total ({total})"

        # Edge case: page beyond last page
        beyond_res = requests.get(f"{BASE_URL}/api/techniques?portal={portal_name}&page={pages + 5}&limit=25")
        assert beyond_res.status_code == 200
        beyond_data = beyond_res.json()
        assert beyond_data["items"] == [], f"Expected empty items beyond last page, got {len(beyond_data['items'])}"
        assert beyond_data["total"] == total

        results[portal_name] = {
            "total": total,
            "chapters": sorted(list(set(it["chapter"] for it in [t for t in catalog if t["chapter"] in expected_chaps_set]))),
            "status": "PASS"
        }

    # Case insensitivity and whitespace trimming tests for portals
    print("\n--- Testing Case and Whitespace Robustness ---")
    res_upper_case = requests.get(f"{BASE_URL}/api/techniques?portal=SPINE-PELVIS")
    assert res_upper_case.status_code == 200
    assert res_upper_case.json()["total"] == results["spine-pelvis"]["total"]
    print("  [+] portal=SPINE-PELVIS (uppercase) passed")

    res_spaces = requests.get(f"{BASE_URL}/api/techniques?portal=%20%20general%20%20")
    assert res_spaces.status_code == 200
    assert res_spaces.json()["total"] == results["general"]["total"]
    print("  [+] portal='  general  ' (spaces) passed")

    # Invalid portals test
    print("\n--- Testing Invalid Portals ---")
    invalid_cases = [
        "invalid_portal_xyz",
        "unknown_specialty",
        "null",
        "12345"
    ]
    for inv in invalid_cases:
        inv_res = requests.get(f"{BASE_URL}/api/techniques?portal={inv}")
        assert inv_res.status_code == 200, f"Invalid portal {inv} returned {inv_res.status_code}"
        inv_data = inv_res.json()
        # Should gracefully return all techniques without crashing
        assert inv_data["total"] == len(catalog), f"Expected total={len(catalog)} for invalid portal fallback, got {inv_data['total']}"
        assert len(inv_data["items"]) == 25, f"Expected 25 items on page 1, got {len(inv_data['items'])}"
        assert inv_data["pages"] == (len(catalog) + 25 - 1) // 25
        print(f"  [+] portal='{inv}' gracefully handled: total={inv_data['total']}, pages={inv_data['pages']}")

    # Pagination validation constraints test (FastAPI boundary checks)
    print("\n--- Testing Boundary and Invalid Pagination Params ---")
    # page = 0 should return 422
    p0_res = requests.get(f"{BASE_URL}/api/techniques?page=0")
    assert p0_res.status_code == 422, f"Expected 422 for page=0, got {p0_res.status_code}"
    print("  [+] page=0 correctly rejected with 422")

    # limit = 0 should return 422
    l0_res = requests.get(f"{BASE_URL}/api/techniques?limit=0")
    assert l0_res.status_code == 422, f"Expected 422 for limit=0, got {l0_res.status_code}"
    print("  [+] limit=0 correctly rejected with 422")

    # limit = 201 (le=200 constraint) should return 422
    l201_res = requests.get(f"{BASE_URL}/api/techniques?limit=201")
    assert l201_res.status_code == 422, f"Expected 422 for limit=201, got {l201_res.status_code}"
    print("  [+] limit=201 correctly rejected with 422")

    # limit = 1 boundary check
    l1_res = requests.get(f"{BASE_URL}/api/techniques?limit=1")
    assert l1_res.status_code == 200
    l1_data = l1_res.json()
    assert len(l1_data["items"]) == 1
    assert l1_data["pages"] == l1_data["total"]
    print(f"  [+] limit=1 boundary test passed (pages={l1_data['pages']})")

    # limit = 200 boundary check
    l200_res = requests.get(f"{BASE_URL}/api/techniques?limit=200")
    assert l200_res.status_code == 200
    l200_data = l200_res.json()
    assert len(l200_data["items"]) == 200
    print(f"  [+] limit=200 boundary test passed (items={len(l200_data['items'])})")

    print("\n[SUCCESS] TASK 1: All API Portal Filtering & Pagination Stress Tests PASSED!")
    return results

# ----------------------------------------------------------------------
# 2. Playwright Mobile Viewport (390x844) Edge Cases Test
# ----------------------------------------------------------------------
def test_playwright_mobile_modal_edge_cases():
    print("\n" + "=" * 70)
    print("TASK 2: Playwright Mobile Viewport 390x844 & Modal Edge Cases")
    print("=" * 70)

    from playwright.sync_api import sync_playwright

    console_errors = []
    page_errors = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 390, "height": 844},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1",
            is_mobile=True,
            has_touch=True
        )

        page = context.new_page()

        page.on("console", lambda msg: console_errors.append(f"[{msg.type}] {msg.text}") if msg.type == "error" else None)
        page.on("pageerror", lambda exc: page_errors.append(str(exc)))

        # 1. Load Main Index on Mobile
        print("\n[Mobile Viewport] Loading index.html (390x844)...")
        res = page.goto(f"{BASE_URL}/", wait_until="networkidle")
        assert res.status == 200, f"Expected 200, got {res.status}"
        time.sleep(1)

        # Check for horizontal overflow
        scroll_w = page.evaluate("document.body.scrollWidth")
        client_w = page.evaluate("document.body.clientWidth")
        print(f"Index scrollWidth: {scroll_w}, clientWidth: {client_w}")
        assert scroll_w <= client_w + 1, f"Horizontal overflow on index.html: {scroll_w} > {client_w}"

        # 2. Test specialized portals on mobile: cot-song.html and dai-cuong.html
        print("\n[Mobile Viewport] Checking cot-song.html (Spine-Pelvis Portal)...")
        res_cs = page.goto(f"{BASE_URL}/cot-song.html", wait_until="networkidle")
        if res_cs.status == 200:
            time.sleep(0.5)
            cs_scroll = page.evaluate("document.body.scrollWidth")
            cs_client = page.evaluate("document.body.clientWidth")
            print(f"cot-song.html scrollWidth: {cs_scroll}, clientWidth: {cs_client}")
            assert cs_scroll <= cs_client + 1, "Horizontal overflow on cot-song.html"

        print("\n[Mobile Viewport] Checking dai-cuong.html (General Portal)...")
        res_dc = page.goto(f"{BASE_URL}/dai-cuong.html", wait_until="networkidle")
        if res_dc.status == 200:
            time.sleep(0.5)
            dc_scroll = page.evaluate("document.body.scrollWidth")
            dc_client = page.evaluate("document.body.clientWidth")
            print(f"dai-cuong.html scrollWidth: {dc_scroll}, clientWidth: {dc_client}")
            assert dc_scroll <= dc_client + 1, "Horizontal overflow on dai-cuong.html"

        # Return to main index for modal verification
        page.goto(f"{BASE_URL}/", wait_until="networkidle")
        time.sleep(0.5)

        # Helper to open modal and verify
        def verify_modal(tech_id: str, expected_includes: List[str], prohibited_terms: List[str]):
            print(f"\n--- Testing Modal for Technique {tech_id} ---")
            # Open via openTechniqueModal
            page.evaluate(f"openTechniqueModal('{tech_id}')")
            page.wait_for_selector("#techModal.active .clinical-card-wrapper", timeout=6000)
            time.sleep(0.5)

            # Check visibility
            is_active = page.locator("#techModal").evaluate("el => el.classList.contains('active')")
            assert is_active, f"Modal did not open for {tech_id}"

            modal_text = page.locator("#techModal").inner_text()

            # Check expected terms
            for term in expected_includes:
                assert term.lower() in modal_text.lower(), f"Technique {tech_id} missing expected term: '{term}'"
                print(f"  [+] Found expected term: '{term}'")

            # Check prohibited terms (anti-hallucination / anti-cross-swap)
            for term in prohibited_terms:
                assert term.lower() not in modal_text.lower(), f"Technique {tech_id} CONTAINS PROHIBITED TERM: '{term}'"
                print(f"  [+] Verified absence of prohibited term: '{term}'")

            # Close modal
            close_btn = page.locator("#modalCloseBtn, .modal-close").first
            if close_btn.is_visible():
                close_btn.click()
            else:
                page.evaluate("document.getElementById('techModal').classList.remove('active')")
            page.wait_for_selector("#techModal:not(.active)", timeout=4000)
            time.sleep(0.3)
            print(f"  [+] Modal for {tech_id} closed cleanly")

        # 1. 6-2 (FAI Clohisy)
        verify_modal(
            tech_id="6-2",
            expected_includes=["6-2", "Clohisy", "Osteochondroplasty", "FAI"],
            prohibited_terms=["Bernese", "Periacetabular Osteotomy", "Ganz", "Matheney"]
        )

        # 2. 6-4 (PAO Bernese)
        verify_modal(
            tech_id="6-4",
            expected_includes=["6-4", "Bernese", "Periacetabular"],
            prohibited_terms=["Clohisy", "chuôi Stem", "Doa ổ cối & Đặt Cup"]
        )

        # 3. 55-1 (Femoral neck cannulated screws)
        verify_modal(
            tech_id="55-1",
            expected_includes=["55-1", "cổ xương đùi", "vít"],
            prohibited_terms=["bánh chè", "patellectomy", "hút tủy"]
        )

        # 4. 56-1 (Stoppa approach acetabulum)
        verify_modal(
            tech_id="56-1",
            expected_includes=["56-1", "Stoppa", "ổ cối", "Corona Mortis"],
            prohibited_terms=["bánh chè", "hút tủy", "RIA"]
        )

        # 5. 54-1 (Lateral malleolus fibula ORIF)
        verify_modal(
            tech_id="54-1",
            expected_includes=["54-1", "mắt cá", "mác"],
            prohibited_terms=["thần kinh ngồi", "bó mạch đùi"]
        )

        # Verify modal opening via search input as well (user interaction flow)
        print("\n--- Verifying User Search & Click Flow on Mobile ---")
        search_input = page.locator("#searchInput, input[type='search'], input[type='text']").first
        if search_input.is_visible():
            search_input.fill("55-1")
            page.keyboard.press("Enter")
            time.sleep(1)
            tech_card = page.locator("text=55-1").first
            if tech_card.is_visible():
                tech_card.click()
                page.wait_for_selector("#techModal.active", timeout=5000)
                assert page.locator("#techModal").evaluate("el => el.classList.contains('active')")
                print("  [+] Search and card click successfully opened modal on mobile!")
                close_btn = page.locator("#modalCloseBtn, .modal-close").first
                if close_btn.is_visible():
                    close_btn.click()
                time.sleep(0.5)

        # Check console errors and page exceptions
        print(f"\nTotal Console Errors recorded: {len(console_errors)}")
        if console_errors:
            for err in console_errors:
                print(f"  [ERROR] {err}")
        print(f"Total Page Exceptions recorded: {len(page_errors)}")
        if page_errors:
            for exc in page_errors:
                print(f"  [EXCEPTION] {exc}")

        assert len(console_errors) == 0, f"Found {len(console_errors)} console errors: {console_errors}"
        assert len(page_errors) == 0, f"Found {len(page_errors)} page exceptions: {page_errors}"

        browser.close()

    print("\n[SUCCESS] TASK 2: Playwright Mobile Viewport 390x844 & Modal Tests PASSED with 0 errors!")
    return True

# ----------------------------------------------------------------------
# 3. Micro-JSON Fetch Latency SLA Benchmark (<50ms)
# ----------------------------------------------------------------------
def test_fetch_latency_20_random_techniques():
    print("\n" + "=" * 70)
    print("TASK 3: Measure Fetch Latency Across 20 Random Micro-JSONs (<50ms SLA)")
    print("=" * 70)

    # List all available micro-JSON files in data/techniques
    tech_dir = os.path.join(ROOT_DIR, "data", "techniques")
    files = [f for f in os.listdir(tech_dir) if f.endswith(".json")]
    print(f"Found {len(files)} micro-JSON files in {tech_dir}")

    # Set deterministic seed for reproducibility while picking 20 diverse techniques
    random.seed(42)
    selected_files = random.sample(files, 20)
    selected_ids = [os.path.splitext(f)[0] for f in selected_files]
    print(f"Selected 20 random techniques for benchmark:\n{selected_ids}")

    from playwright.sync_api import sync_playwright

    browser_latencies = []
    http_latencies = []

    # 1. Measure Browser fetch latency (the true end-user mobile experience)
    print("\n--- 1. Mobile Browser In-situ fetch() Latencies ---")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 390, "height": 844},
            is_mobile=True,
            has_touch=True
        )
        page = context.new_page()
        page.goto(f"{BASE_URL}/", wait_until="networkidle")

        for idx, tid in enumerate(selected_ids, 1):
            js_code = f"""async () => {{
                const t0 = performance.now();
                const res = await fetch('data/techniques/{tid}.json');
                const ok = res.ok;
                const status = res.status;
                const json = await res.json();
                const t1 = performance.now();
                return {{
                    latency_ms: t1 - t0,
                    ok: ok,
                    status: status,
                    tech_id: json.tech_id || ''
                }};
            }}"""
            result = page.evaluate(js_code)
            lat = result["latency_ms"]
            browser_latencies.append(lat)
            print(f"  [{idx:02d}/20] {tid}.json -> {lat:.2f} ms (Status: {result['status']}, Tech ID: {result['tech_id']})")
            assert result["ok"], f"Failed to fetch data/techniques/{tid}.json: status {result['status']}"
            assert lat < 50.0, f"SLA VIOLATION: {tid}.json latency {lat:.2f} ms >= 50ms"

        browser.close()

    # 2. Measure Direct HTTP GET latencies
    print("\n--- 2. Direct HTTP GET Latencies ---")
    session = requests.Session()
    for idx, tid in enumerate(selected_ids, 1):
        url = f"{BASE_URL}/data/techniques/{tid}.json"
        t0 = time.perf_counter()
        resp = session.get(url)
        t1 = time.perf_counter()
        lat_ms = (t1 - t0) * 1000.0
        http_latencies.append(lat_ms)
        assert resp.status_code == 200, f"Failed HTTP get for {url}"
        print(f"  [{idx:02d}/20] HTTP GET {tid}.json -> {lat_ms:.2f} ms")
        assert lat_ms < 50.0, f"SLA VIOLATION: HTTP GET {tid}.json latency {lat_ms:.2f} ms >= 50ms"

    # Compute Statistics
    def compute_stats(arr):
        s = sorted(arr)
        avg = sum(s) / len(s)
        p95 = s[int(len(s) * 0.95)]
        return {
            "min": min(s),
            "max": max(s),
            "avg": avg,
            "median": s[len(s) // 2],
            "p95": p95
        }

    b_stats = compute_stats(browser_latencies)
    h_stats = compute_stats(http_latencies)

    print("\n" + "=" * 50)
    print("BENCHMARK SUMMARY (<50ms SLA)")
    print("=" * 50)
    print(f"Browser fetch() [N=20]: Min={b_stats['min']:.2f}ms, Max={b_stats['max']:.2f}ms, Mean={b_stats['avg']:.2f}ms, Median={b_stats['median']:.2f}ms, P95={b_stats['p95']:.2f}ms")
    print(f"Direct HTTP GET [N=20]: Min={h_stats['min']:.2f}ms, Max={h_stats['max']:.2f}ms, Mean={h_stats['avg']:.2f}ms, Median={h_stats['median']:.2f}ms, P95={h_stats['p95']:.2f}ms")

    assert b_stats["max"] < 50.0, f"Browser fetch max {b_stats['max']:.2f}ms >= 50ms SLA"
    assert h_stats["max"] < 50.0, f"Direct HTTP GET max {h_stats['max']:.2f}ms >= 50ms SLA"
    print("\n[SUCCESS] TASK 3: Micro-JSON fetch latency for all 20 techniques strictly conforms to <50ms SLA!")
    return {
        "selected_techniques": selected_ids,
        "browser_stats": b_stats,
        "http_stats": h_stats
    }

# ----------------------------------------------------------------------
# Runner
# ----------------------------------------------------------------------
def main():
    print(f"Starting server for Adversarial Challenger 2 tests on port {PORT}...")
    server_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "server:app", "--host", "127.0.0.1", "--port", str(PORT)],
        cwd=ROOT_DIR,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    try:
        if not wait_for_server(f"{BASE_URL}/", timeout=15):
            raise RuntimeError(f"Server failed to start on port {PORT} within 15 seconds")
        print("Server is up and healthy!")

        # Execute tests
        task1_res = test_portal_filtering_and_pagination()
        task2_res = test_playwright_mobile_modal_edge_cases()
        task3_res = test_fetch_latency_20_random_techniques()

        print("\n" + "=" * 70)
        print("ALL ADVERSARIAL CHALLENGER 2 TESTS COMPLETED SUCCESSFULLY!")
        print("=" * 70)

    finally:
        print("Shutting down test server...")
        server_process.terminate()
        server_process.wait()
        print("Server stopped.")

if __name__ == "__main__":
    main()
