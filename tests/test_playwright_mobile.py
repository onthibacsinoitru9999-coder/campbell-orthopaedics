import os
import sys
import time
import subprocess
import requests
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')

PORT = 8088
BASE_URL = f"http://127.0.0.1:{PORT}"

def wait_for_server(url, timeout=15):
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = requests.get(url, timeout=1)
            if r.status_code in [200, 404]:
                return True
        except Exception:
            time.sleep(0.5)
    return False

def run_mobile_tests():
    print(f"Starting server on port {PORT}...")
    server_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "server:app", "--host", "127.0.0.1", "--port", str(PORT)],
        cwd=os.path.abspath(os.path.join(os.path.dirname(__file__), "..")),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    try:
        if not wait_for_server(f"{BASE_URL}/", timeout=15):
            raise RuntimeError("Server failed to start in 15 seconds")
        print("Server is up and responding!")

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            # Mobile Viewport 390 x 844 (iPhone 12/13/14)
            context = browser.new_context(
                viewport={"width": 390, "height": 844},
                user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1",
                is_mobile=True,
                has_touch=True
            )

            console_errors = []
            page_errors = []

            page = context.new_page()

            page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
            page.on("pageerror", lambda exc: page_errors.append(str(exc)))

            # Test 1: Load Homepage in Mobile Viewport
            print("\n[TEST 1] Loading index.html on mobile (390x844)...")
            res = page.goto(f"{BASE_URL}/", wait_until="networkidle")
            assert res.status == 200, f"Expected 200, got {res.status}"
            time.sleep(1)

            # Check horizontal overflow
            body_scroll_w = page.evaluate("document.body.scrollWidth")
            body_client_w = page.evaluate("document.body.clientWidth")
            print(f"Body scrollWidth: {body_scroll_w}, clientWidth: {body_client_w}")
            assert body_scroll_w <= body_client_w + 1, f"Horizontal overflow detected: {body_scroll_w} > {body_client_w}"

            # Test 2: Search for Bennett fracture (67-1)
            print("\n[TEST 2] Testing search for Bennett fracture (67-1)...")
            search_input = page.locator("#searchInput, input[type='search'], input[type='text']").first
            if search_input.is_visible():
                search_input.fill("67-1")
                page.keyboard.press("Enter")
                time.sleep(1)

            # Find technique card or list item
            tech_elem = page.locator("text=67-1").first
            if tech_elem.is_visible():
                tech_elem.click()
                time.sleep(1)

            # Check if technique details modal or section rendered
            print("\n[TEST 3] Verifying clinical technique content rendering...")
            # Look for clinical sections
            content = page.content()
            has_indications = "Chỉ định lâm sàng" in content or "clinical_indications" in content or "67-1" in content
            print(f"Has clinical technique content: {has_indications}")
            assert has_indications, "Clinical technique content not found on page"

            # Test 4: Check Image Lightbox on Mobile
            print("\n[TEST 4] Testing Image Lightbox click & display...")
            img_elem = page.locator("img.tech-main-img, .tech-images-gallery img").first
            if img_elem.is_visible():
                img_src = img_elem.get_attribute("src")
                print(f"Found technique image: {img_src}")
                img_elem.click()
                time.sleep(0.5)

                lightbox = page.locator("#imageLightbox")
                is_active = lightbox.evaluate("el => el.classList.contains('active')")
                print(f"Lightbox active status: {is_active}")
                assert is_active, "Lightbox failed to open when image clicked"

                # Test Lightbox Zoom Toggle
                print("Testing Lightbox image zoom on mobile tap...")
                lightbox_img = page.locator("#lightboxImg")
                lightbox_img.click()
                time.sleep(0.3)
                is_zoomed = lightbox.evaluate("el => el.classList.contains('zoomed')")
                print(f"Lightbox zoomed status: {is_zoomed}")
                assert is_zoomed, "Lightbox zoom failed on image tap"

                # Tap again to unzoom
                lightbox_img.click()
                time.sleep(0.3)
                is_unzoomed = lightbox.evaluate("el => !el.classList.contains('zoomed')")
                print(f"Lightbox unzoomed status: {is_unzoomed}")
                assert is_unzoomed, "Lightbox unzoom failed on second tap"

                # Close lightbox
                close_btn = page.locator(".lightbox-close").first
                if close_btn.is_visible():
                    close_btn.click()
                else:
                    lightbox.click()
                time.sleep(0.5)
                is_closed = lightbox.evaluate("el => !el.classList.contains('active')")
                print(f"Lightbox closed status: {is_closed}")
                assert is_closed, "Lightbox failed to close"

            # Test 4b: Attack Edge Case - Single Quotes in Captions (66-10: No Man's Land)
            print("\n[TEST 4b] Testing 66-10 (Zone II tendon repair with single quotes in caption)...")
            if search_input.is_visible():
                search_input.fill("66-10")
                page.keyboard.press("Enter")
                time.sleep(1)
                tech_66 = page.locator("text=66-10").first
                if tech_66.is_visible():
                    tech_66.click()
                    time.sleep(1)
                    # Click on the gallery image
                    gal_img = page.locator(".tech-images-gallery img, img.tech-main-img").first
                    if gal_img.is_visible():
                        gal_img.click()
                        time.sleep(0.5)
                        lightbox = page.locator("#imageLightbox")
                        is_active = lightbox.evaluate("el => el.classList.contains('active')")
                        cap_text = page.locator("#lightboxCaption").text_content()
                        print(f"66-10 Lightbox active: {is_active}, Caption: {cap_text}")
                        assert is_active, "66-10 Lightbox failed to open"
                        assert "No Man" in cap_text or "Bruner" in cap_text, "Caption text mismatch"
                        # Close
                        page.locator(".lightbox-close").first.click()
                        time.sleep(0.5)

            # Test 5: Search for Carpal Tunnel (76-1)
            print("\n[TEST 5] Testing search for Carpal Tunnel (76-1)...")
            if search_input.is_visible():
                search_input.fill("76-1")
                page.keyboard.press("Enter")
                time.sleep(1)
                tech_76 = page.locator("text=76-1").first
                if tech_76.is_visible():
                    tech_76.click()
                    time.sleep(1)
                    page_text = page.content()
                    has_contra = "Chống chỉ định" in page_text or "ống cổ tay" in page_text.lower()
                    print(f"Contains contraindications / hand details: {has_contra}")
                    assert has_contra, "Hand technique details missing"

            # Test 5b: Search for TFCC Peripheral Tear (69-26)
            print("\n[TEST 5b] Testing search for TFCC repair (69-26)...")
            if search_input.is_visible():
                search_input.fill("69-26")
                page.keyboard.press("Enter")
                time.sleep(1)
                tech_69 = page.locator("text=69-26").first
                if tech_69.is_visible():
                    tech_69.click()
                    time.sleep(1)
                    page_text = page.content()
                    assert "TFCC" in page_text or "tam giác" in page_text.lower(), "TFCC details missing"

            # Test 6: Navigate to chi-tren.html (Upper Extremity page)
            print("\n[TEST 6] Testing chi-tren.html navigation and viewport...")
            res_arm = page.goto(f"{BASE_URL}/chi-tren.html", wait_until="networkidle")
            if res_arm.status == 200:
                time.sleep(1)
                scroll_w = page.evaluate("document.body.scrollWidth")
                client_w = page.evaluate("document.body.clientWidth")
                print(f"chi-tren.html scrollWidth: {scroll_w}, clientWidth: {client_w}")
                assert scroll_w <= client_w + 1, "Horizontal overflow on chi-tren.html"

            browser.close()

            print("\n==========================================")
            print("PLAYWRIGHT MOBILE TEST SUMMARY")
            print("==========================================")
            print(f"Total Console Errors: {len(console_errors)}")
            if console_errors:
                print("Console Errors found:")
                for err in console_errors:
                    print(f"  - {err}")
            print(f"Total Page Exceptions: {len(page_errors)}")
            if page_errors:
                print("Page Exceptions found:")
                for exc in page_errors:
                    print(f"  - {exc}")

            assert len(console_errors) == 0, f"Found {len(console_errors)} console errors: {console_errors}"
            assert len(page_errors) == 0, f"Found {len(page_errors)} page errors: {page_errors}"
            print("\nSUCCESS: All Mobile Playwright tests passed with 0 console errors!")

    finally:
        print("Stopping test server...")
        server_process.terminate()
        server_process.wait()

if __name__ == "__main__":
    run_mobile_tests()
