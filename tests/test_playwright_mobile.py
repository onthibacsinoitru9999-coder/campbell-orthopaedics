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

            # Test 7: Navigate to chi-duoi.html (Lower Extremity page)
            print("\n[TEST 7] Testing chi-duoi.html navigation and viewport (390x844)...")
            res_leg = page.goto(f"{BASE_URL}/chi-duoi.html", wait_until="networkidle")
            assert res_leg.status == 200, f"Expected 200 on chi-duoi.html, got {res_leg.status}"
            time.sleep(1)
            scroll_leg = page.evaluate("document.body.scrollWidth")
            client_leg = page.evaluate("document.body.clientWidth")
            print(f"chi-duoi.html scrollWidth: {scroll_leg}, clientWidth: {client_leg}")
            assert scroll_leg <= client_leg + 1, f"Horizontal overflow on chi-duoi.html: {scroll_leg} > {client_leg}"

            # Test 8: Search for Tibial Plateau Fracture (54-14)
            print("\n[TEST 8] Testing search for Tibial Plateau Fracture (54-14)...")
            leg_search = page.locator("#searchInput, #globalSearch, input[type='text']").first
            if leg_search.is_visible():
                leg_search.fill("54-14")
                page.keyboard.press("Enter")
                time.sleep(1)
                tech_54 = page.locator("text=54-14").first
                if tech_54.is_visible():
                    tech_54.click()
                    time.sleep(1)
                    page_text = page.content()
                    assert "54-14" in page_text, "Technique 54-14 content missing"
                    assert "Schatzker" in page_text or "mâm chày" in page_text.lower(), "Schatzker details missing"
                    assert "mác chung" in page_text or "thần kinh" in page_text.lower(), "Danger zone missing"
                    
                    # Test Lightbox on 54-14 image
                    gal_54 = page.locator(".tech-images-gallery img, img.tech-main-img").first
                    if gal_54.is_visible():
                        gal_54.click()
                        time.sleep(0.5)
                        lightbox = page.locator("#imageLightbox")
                        assert lightbox.evaluate("el => el.classList.contains('active')"), "54-14 Lightbox failed to open"
                        # Zoom toggle
                        page.locator("#lightboxImg").click()
                        time.sleep(0.3)
                        assert lightbox.evaluate("el => el.classList.contains('zoomed')"), "54-14 Lightbox zoom failed"
                        page.locator("#lightboxImg").click()
                        time.sleep(0.3)
                        assert lightbox.evaluate("el => !el.classList.contains('zoomed')"), "54-14 Lightbox unzoom failed"
                        # Close lightbox
                        page.locator(".lightbox-close").first.click()
                        time.sleep(0.5)

                    # Close technique modal
                    close_modal_btn = page.locator("#modalCloseBtn, .modal-close").first
                    if close_modal_btn.is_visible():
                        close_modal_btn.click()
                        page.wait_for_selector("#techModal:not(.active)", timeout=5000)
                        time.sleep(0.5)

            # Test 9: Search for Stoppa Approach Acetabular Fracture (56-1)
            print("\n[TEST 9] Testing search for Stoppa Approach Acetabulum (56-1)...")
            page.evaluate("openTechniqueModal('56-1')")
            page.wait_for_selector("#techModal.active .clinical-card-wrapper", timeout=5000)
            modal_text = page.locator("#techModal").inner_text()
            assert "Stoppa" in modal_text or "ổ cối" in modal_text.lower(), "Stoppa details missing"
            assert "corona mortis" in modal_text.lower(), "Corona Mortis danger zone missing"
            assert "Pfannenstiel" in modal_text, "Pfannenstiel approach missing"
            close_modal_btn = page.locator("#modalCloseBtn, .modal-close").first
            if close_modal_btn.is_visible():
                close_modal_btn.click()
                page.wait_for_selector("#techModal:not(.active)", timeout=5000)
                time.sleep(0.5)

            # Test 10: Calcaneal Fracture ORIF (88-1) & verify no Lisfranc nonsense
            print("\n[TEST 10] Testing Sanders Calcaneal Fracture ORIF (88-1)...")
            if leg_search.is_visible():
                leg_search.fill("88-1")
                page.keyboard.press("Enter")
                time.sleep(1)
                tech_88 = page.locator("text=88-1").first
                if tech_88.is_visible():
                    tech_88.click()
                    time.sleep(1)
                    page_text = page.content()
                    assert "88-1" in page_text, "88-1 technique ID missing"
                    assert "Sanders" in page_text or "xương gót" in page_text.lower(), "Sanders calcaneus details missing"
                    assert "No-Touch" in page_text, "No-Touch flap technique missing"
                    assert "Böhler" in page_text or "Bohler" in page_text, "Böhler angle restoration missing"
                    # ADVERSARIAL CHECK: must NOT have Lisfranc home-run screw in calcaneus!
                    assert "Home-Run từ xương chêm trong sang nền xương bàn 2" not in page_text, "Calcaneus has Lisfranc error!"
                    
                    # Test Lightbox on 88-1 image
                    gal_88 = page.locator(".tech-images-gallery img, img.tech-main-img").first
                    if gal_88.is_visible():
                        gal_88.click()
                        time.sleep(0.5)
                        lb = page.locator("#imageLightbox")
                        assert lb.evaluate("el => el.classList.contains('active')"), "88-1 Lightbox failed"
                        page.locator(".lightbox-close").first.click()
                        time.sleep(0.5)

                    # Close modal
                    close_modal_btn = page.locator("#modalCloseBtn, .modal-close").first
                    if close_modal_btn.is_visible():
                        close_modal_btn.click()
                        time.sleep(0.5)

            # Test 11: Bernese PAO (6-2) - verify pelvic osteotomy & no THA stem/cup nonsense
            print("\n[TEST 11] Testing Bernese Periacetabular Osteotomy (6-2)...")
            if leg_search.is_visible():
                leg_search.fill("6-2")
                page.keyboard.press("Enter")
                time.sleep(1)
                tech_6 = page.locator("text=6-2").first
                if tech_6.is_visible():
                    tech_6.click()
                    time.sleep(1)
                    page_text = page.content()
                    assert "6-2" in page_text, "6-2 technique ID missing"
                    assert "Bernese" in page_text or "Ganz" in page_text or "PAO" in page_text, "Bernese PAO missing"
                    assert "Wiberg" in page_text or "loạn sản" in page_text.lower(), "DDH Wiberg angle missing"
                    # ADVERSARIAL CHECK: PAO is joint-preserving, must NOT contain prosthetic stem or total hip cup!
                    assert "chuôi Stem" not in page_text, "PAO erroneously contains THA stem replacement!"
                    assert "Doa ổ cối & Đặt Cup" not in page_text, "PAO erroneously contains THA cup reaming!"
                    # Close modal
                    close_modal_btn = page.locator("#modalCloseBtn, .modal-close").first
                    if close_modal_btn.is_visible():
                        close_modal_btn.click()
                        time.sleep(0.5)

            # Test 12: High Tibial Osteotomy (9-1) - verify Fujisawa & TomoFix, no TKA
            print("\n[TEST 12] Testing High Tibial Osteotomy (9-1)...")
            if leg_search.is_visible():
                leg_search.fill("9-1")
                page.keyboard.press("Enter")
                time.sleep(1)
                tech_9 = page.locator("text=9-1").first
                if tech_9.is_visible():
                    tech_9.click()
                    time.sleep(1)
                    page_text = page.content()
                    assert "Fujisawa" in page_text, "Fujisawa point missing"
                    assert "TomoFix" in page_text or "nẹp khóa" in page_text.lower(), "HTO fixation missing"
                    assert "bản lề" in page_text.lower() or "lateral hinge" in page_text.lower(), "Lateral hinge missing"
                    # Close modal
                    close_modal_btn = page.locator("#modalCloseBtn, .modal-close").first
                    if close_modal_btn.is_visible():
                        close_modal_btn.click()
                        time.sleep(0.5)

            # Test 13: Open Meniscal Repair (45-1) - verify no ACL tunnel drilling
            print("\n[TEST 13] Testing Open Meniscal Repair (45-1)...")
            if leg_search.is_visible():
                leg_search.fill("45-1")
                page.keyboard.press("Enter")
                time.sleep(1)
                tech_45 = page.locator("text=45-1").first
                if tech_45.is_visible():
                    tech_45.click()
                    time.sleep(1)
                    page_text = page.content()
                    assert "sụn chêm" in page_text.lower(), "Meniscus details missing"
                    assert "khoan đường hầm chày, đường hầm đùi" not in page_text, "Open meniscus repair has ACL error!"
                    # Close modal
                    close_modal_btn = page.locator("#modalCloseBtn, .modal-close").first
                    if close_modal_btn.is_visible():
                        close_modal_btn.click()
                        time.sleep(0.5)

            # Test 14: Hawkins Talar Neck (88-8)
            print("\n[TEST 14] Testing Hawkins Talar Neck Fracture ORIF (88-8)...")
            if leg_search.is_visible():
                leg_search.fill("88-8")
                page.keyboard.press("Enter")
                time.sleep(1)
                tech_88_8 = page.locator("text=88-8").first
                if tech_88_8.is_visible():
                    tech_88_8.click()
                    time.sleep(1)
                    page_text = page.content()
                    assert "Hawkins" in page_text, "Hawkins classification missing"
                    assert "Canale" in page_text, "Canale view missing"
                    assert "Home-Run từ xương chêm trong sang nền xương bàn 2" not in page_text, "Talus has Lisfranc error!"
                    # Close modal
                    close_modal_btn = page.locator("#modalCloseBtn, .modal-close").first
                    if close_modal_btn.is_visible():
                        close_modal_btn.click()
                        time.sleep(0.5)

            # Test 15A: Lisfranc ORIF (88-14)
            print("\n[TEST 15A] Testing Lisfranc Fracture-Dislocation ORIF (88-14)...")
            if leg_search.is_visible():
                leg_search.fill("88-14")
                page.keyboard.press("Enter")
                time.sleep(1)
                tech_88_14 = page.locator("text=88-14").first
                if tech_88_14.is_visible():
                    tech_88_14.click()
                    page.wait_for_selector("#techModal.active .clinical-card-wrapper", timeout=5000)
                    modal_text = page.locator("#techModal").inner_text()
                    print(f"DEBUG 15A modal_text head:\n{modal_text[:300]}")
                    assert "Lisfranc" in modal_text, "Lisfranc details missing in 88-14"
                    assert "Home-Run" in modal_text, "Home-run screw missing in 88-14"
                    assert "xương bàn 2" in modal_text.lower(), "2nd metatarsal keystone missing in 88-14"
                    close_modal_btn = page.locator("#modalCloseBtn, .modal-close").first
                    if close_modal_btn.is_visible():
                        close_modal_btn.click()
                        page.wait_for_selector("#techModal:not(.active)", timeout=5000)
                        time.sleep(0.5)

            # Test 15B: Syndesmosis Repair (89-1)
            print("\n[TEST 15B] Testing Distal Tibiofibular Syndesmosis Repair (89-1)...")
            if leg_search.is_visible():
                leg_search.fill("89-1")
                page.keyboard.press("Enter")
                time.sleep(1)
                tech_89_1 = page.locator("text=89-1").first
                if tech_89_1.is_visible():
                    tech_89_1.click()
                    page.wait_for_selector("#techModal.active .clinical-card-wrapper", timeout=5000)
                    modal_text = page.locator("#techModal").inner_text()
                    assert "Mộng Chày Mác" in modal_text or "chày mác" in modal_text.lower(), "Syndesmosis missing in 89-1"
                    assert "Lisfranc" not in modal_text, "89-1 erroneously contains Lisfranc cross-contamination!"
                    close_modal_btn = page.locator("#modalCloseBtn, .modal-close").first
                    if close_modal_btn.is_visible():
                        close_modal_btn.click()
                        page.wait_for_selector("#techModal:not(.active)", timeout=5000)
                        time.sleep(0.5)

            # Test 15C: Compartment Syndrome Fasciotomy (48-1) - Zero Tourniquet
            print("\n[TEST 15C] Testing Acute Compartment Syndrome Fasciotomy (48-1)...")
            if leg_search.is_visible():
                leg_search.fill("48-1")
                page.keyboard.press("Enter")
                time.sleep(1)
                tech_48_1 = page.locator("text=48-1").first
                if tech_48_1.is_visible():
                    tech_48_1.click()
                    page.wait_for_selector("#techModal.active .clinical-card-wrapper", timeout=5000)
                    modal_text = page.locator("#techModal").inner_text()
                    assert "chèn ép khoang" in modal_text.lower(), "Compartment syndrome missing in 48-1"
                    assert "không được đặt garo" in modal_text.lower() or "tuyệt đối không" in modal_text.lower() or "không đặt garo" in modal_text.lower(), "Tourniquet contraindication warning missing in 48-1!"
                    assert "garo đùi" not in modal_text.lower() or "chống chỉ định" in modal_text.lower() or "tuyệt đối không đặt garo" in modal_text.lower(), "48-1 erroneously contains tourniquet recommendation!"
                    close_modal_btn = page.locator("#modalCloseBtn, .modal-close").first
                    if close_modal_btn.is_visible():
                        close_modal_btn.click()
                        page.wait_for_selector("#techModal:not(.active)", timeout=5000)
                        time.sleep(0.5)

            # Test 15D: Upper Extremity Acromioplasty (46-1) - No Knee Contamination
            print("\n[TEST 15D] Testing Shoulder Acromioplasty (46-1)...")
            if leg_search.is_visible():
                leg_search.fill("46-1")
                page.keyboard.press("Enter")
                time.sleep(1)
                tech_46_1 = page.locator("text=46-1").first
                if tech_46_1.is_visible():
                    tech_46_1.click()
                    page.wait_for_selector("#techModal.active .clinical-card-wrapper", timeout=5000)
                    modal_text = page.locator("#techModal").inner_text()
                    assert "khớp vai" in modal_text.lower() or "mỏm cùng vai" in modal_text.lower() or "chóp xoay" in modal_text.lower(), "Shoulder details missing in 46-1"
                    assert "khớp gối" not in modal_text.lower(), "46-1 erroneously contains knee joint cross-contamination!"
                    assert "nẹp gối" not in modal_text.lower(), "46-1 erroneously contains knee brace cross-contamination!"
                    close_modal_btn = page.locator("#modalCloseBtn, .modal-close").first
                    if close_modal_btn.is_visible():
                        close_modal_btn.click()
                        page.wait_for_selector("#techModal:not(.active)", timeout=5000)
                        time.sleep(0.5)

            # Test 15E: Tarsal Tunnel Release (86-1) - No Osteotomy/Plating
            print("\n[TEST 15E] Testing Tarsal Tunnel Release (86-1)...")
            if leg_search.is_visible():
                leg_search.fill("86-1")
                page.keyboard.press("Enter")
                time.sleep(1)
                tech_86_1 = page.locator("text=86-1").first
                if tech_86_1.is_visible():
                    tech_86_1.click()
                    page.wait_for_selector("#techModal.active .clinical-card-wrapper", timeout=5000)
                    modal_text = page.locator("#techModal").inner_text()
                    assert "ống cổ chân" in modal_text.lower(), "Tarsal tunnel missing in 86-1"
                    assert "cắt xương sửa trục" not in modal_text.lower(), "86-1 erroneously contains osteotomy!"
                    assert "nẹp khóa" not in modal_text.lower(), "86-1 erroneously contains plate fixation!"
                    close_modal_btn = page.locator("#modalCloseBtn, .modal-close").first
                    if close_modal_btn.is_visible():
                        close_modal_btn.click()
                        page.wait_for_selector("#techModal:not(.active)", timeout=5000)
                        time.sleep(0.5)

            # Test 15F: Winograd Nail Procedure (87-4) - Digital Block & Phenol
            print("\n[TEST 15F] Testing Winograd Matrixectomy (87-4)...")
            if leg_search.is_visible():
                leg_search.fill("87-4")
                page.keyboard.press("Enter")
                time.sleep(1)
                tech_87_4 = page.locator("text=87-4").first
                if tech_87_4.is_visible():
                    tech_87_4.click()
                    page.wait_for_selector("#techModal.active .clinical-card-wrapper", timeout=5000)
                    modal_text = page.locator("#techModal").inner_text()
                    assert "mầm móng" in modal_text.lower() or "phiến móng" in modal_text.lower(), "Nail details missing in 87-4"
                    assert "cắt xương" not in modal_text.lower(), "87-4 erroneously contains osteotomy!"
                    assert "nẹp bột cẳng bàn chân" not in modal_text.lower(), "87-4 erroneously contains below-knee casting!"
                    close_modal_btn = page.locator("#modalCloseBtn, .modal-close").first
                    if close_modal_btn.is_visible():
                        close_modal_btn.click()
                        page.wait_for_selector("#techModal:not(.active)", timeout=5000)
                        time.sleep(0.5)

            # Test 16: Micro-JSON on-demand fetch latency benchmark (<50ms target)
            print("\n[TEST 16] Benchmarking micro-JSON fetch latency in mobile browser...")
            for tid in ["54-14", "6-2", "88-1", "9-1", "89-1"]:
                latency_ms = page.evaluate(f"""async () => {{
                    const t0 = performance.now();
                    const res = await fetch('data/techniques/{tid}.json');
                    const json = await res.json();
                    const t1 = performance.now();
                    return t1 - t0;
                }}""")
                print(f"  Micro-JSON {tid}.json fetch latency: {latency_ms:.2f} ms")
                assert latency_ms < 50.0, f"Micro-JSON {tid} fetch too slow: {latency_ms:.2f} ms >= 50ms"

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
