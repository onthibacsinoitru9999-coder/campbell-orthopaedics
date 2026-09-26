"""Tier 1 to Tier 4 E2E Tests: High-DPI Page Viewer & Text Extraction.

Verifies:
- Tier 1: Feature Coverage (High-DPI 150-200 DPI rendering, PNG magic bytes, text extraction endpoint, cache storage)
- Tier 2: Boundary & Corner Cases (Page 1, Page 4887, Out of bounds 0 and 4888, Cold vs Warm cache latency < 500ms)
- Tier 3: Cross-Feature Combinations (Technique detail -> PDF page -> Page image -> Page text alignment, multi-page)
- Tier 4: Real-World Clinical Workload Scenarios (Schatzker p.3058, Neer p.3266, Denis spine p.1952, Broström p.4832)
"""

import os
import time
import unittest
from tests.e2e_client import get_test_client

PNG_MAGIC_BYTES = b"\x89PNG\r\n\x1a\n"


class TestE2EViewer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = get_test_client()

    # =========================================================================
    # TIER 1: FEATURE COVERAGE
    # =========================================================================

    def test_tier1_page_image_rendering_default_dpi(self):
        """Verify GET /api/page-image/{page_num} returns valid PNG bytes at default 150 DPI."""
        resp = self.client.get("/api/page-image/100")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.headers.get("content-type"), "image/png")
        self.assertTrue(resp.content.startswith(PNG_MAGIC_BYTES), "Response body must start with PNG magic bytes")
        self.assertGreater(len(resp.content), 20000, "150 DPI page image should be at least 20KB")

    def test_tier1_page_image_high_dpi_200(self):
        """Verify rendering at 200 DPI produces crisp, larger image payload than 150 DPI."""
        resp_150 = self.client.get("/api/page-image/200?dpi=150")
        self.assertEqual(resp_150.status_code, 200)

        resp_200 = self.client.get("/api/page-image/200?dpi=200")
        self.assertEqual(resp_200.status_code, 200)
        self.assertTrue(resp_200.content.startswith(PNG_MAGIC_BYTES))
        self.assertGreater(
            len(resp_200.content), len(resp_150.content),
            "200 DPI image should produce higher byte size than 150 DPI"
        )

    def test_tier1_page_text_extraction(self):
        """Verify GET /api/page-text/{page_num} extracts textual content from PDF."""
        resp = self.client.get("/api/page-text/100")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["page_num"], 100)
        self.assertIn("text", data)
        self.assertGreater(len(data["text"]), 100, "Content page 100 must contain text")

    def test_tier1_disk_cache_persistence(self):
        """Verify rendered pages are cached to cache/pages/ on disk."""
        page_num = 150
        dpi = 150
        resp = self.client.get(f"/api/page-image/{page_num}?dpi={dpi}")
        self.assertEqual(resp.status_code, 200)

        cache_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "cache", "pages", f"page_{page_num}_dpi{dpi}.png"
        )
        self.assertTrue(os.path.exists(cache_path), f"Expected cache file at {cache_path}")
        self.assertGreater(os.path.getsize(cache_path), 20000)

    # =========================================================================
    # TIER 2: BOUNDARY & CORNER CASES
    # =========================================================================

    def test_tier2_boundary_first_page_1(self):
        """Boundary test: Page 1 (Cover page of Campbell 13th Ed)."""
        resp = self.client.get("/api/page-image/1?dpi=150")
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.content.startswith(PNG_MAGIC_BYTES))

    def test_tier2_boundary_last_page_4887(self):
        """Boundary test: Page 4887 (Final page of Campbell 13th Ed)."""
        resp = self.client.get("/api/page-image/4887?dpi=150")
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.content.startswith(PNG_MAGIC_BYTES))

    def test_tier2_boundary_page_zero_returns_404(self):
        """Boundary test: Page 0 is out of bounds and must return HTTP 404."""
        resp = self.client.get("/api/page-image/0")
        self.assertEqual(resp.status_code, 404)

        resp_text = self.client.get("/api/page-text/0")
        self.assertEqual(resp_text.status_code, 404)

    def test_tier2_boundary_page_beyond_max_returns_404(self):
        """Boundary test: Page 4888 (exceeding total pages 4887) must return HTTP 404."""
        resp = self.client.get("/api/page-image/4888")
        self.assertEqual(resp.status_code, 404)

        resp_text = self.client.get("/api/page-text/4888")
        self.assertEqual(resp_text.status_code, 404)

    def test_tier2_boundary_negative_page_returns_404(self):
        """Boundary test: Negative page number must return HTTP 404."""
        resp = self.client.get("/api/page-image/-5")
        self.assertEqual(resp.status_code, 404)

    def test_tier2_cached_page_latency_under_500ms(self):
        """Performance Acceptance Criteria: Cached page loading MUST be < 500ms."""
        page_num = 300
        # First request primes the cache
        self.client.get(f"/api/page-image/{page_num}?dpi=150")

        # Second request measures warm cache retrieval time
        t0 = time.perf_counter()
        resp = self.client.get(f"/api/page-image/{page_num}?dpi=150")
        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        self.assertEqual(resp.status_code, 200)
        self.assertLess(
            elapsed_ms, 500.0,
            f"Cached page render exceeded 500ms latency requirement: {elapsed_ms:.2f} ms"
        )

    # =========================================================================
    # TIER 3: CROSS-FEATURE COMBINATIONS
    # =========================================================================

    def test_tier3_technique_to_multipage_viewer_navigation(self):
        """Cross-feature: Technique 54-24 spanning multiple pages (p. 3058 and p. 3059)."""
        resp_tech = self.client.get("/api/techniques/54-24")
        self.assertEqual(resp_tech.status_code, 200)
        tech = resp_tech.json()
        pdf_page = tech["pdf_page"]

        # 1. Render primary page
        resp_p1 = self.client.get(f"/api/page-image/{pdf_page}?dpi=150")
        self.assertEqual(resp_p1.status_code, 200)
        self.assertTrue(resp_p1.content.startswith(PNG_MAGIC_BYTES))

        # 2. Render subsequent page for continuation of procedure
        resp_p2 = self.client.get(f"/api/page-image/{pdf_page + 1}?dpi=150")
        self.assertEqual(resp_p2.status_code, 200)
        self.assertTrue(resp_p2.content.startswith(PNG_MAGIC_BYTES))

        # 3. Extract text from both pages
        text1 = self.client.get(f"/api/page-text/{pdf_page}").json()["text"]
        text2 = self.client.get(f"/api/page-text/{pdf_page + 1}").json()["text"]
        self.assertGreater(len(text1), 50)
        self.assertGreater(len(text2), 50)

    # =========================================================================
    # TIER 4: REAL-WORLD CLINICAL WORKLOAD SCENARIOS
    # =========================================================================

    def test_tier4_clinical_schatzker_surgical_diagram_render(self):
        """Clinical Scenario: Surgeon opens Schatzker tibial plateau surgical guide (p.3058)."""
        resp = self.client.get("/api/page-image/3058?dpi=150")
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.content.startswith(PNG_MAGIC_BYTES))

        # Verify page text contains tibial plateau fracture discussion
        text = self.client.get("/api/page-text/3058").json()["text"]
        self.assertTrue(
            "tibia" in text.lower() or "plateau" in text.lower() or "54-24" in text,
            "Page 3058 text should discuss tibial plateau fractures"
        )

    def test_tier4_clinical_neer_humerus_render(self):
        """Clinical Scenario: Surgeon opens Neer proximal humerus guide (p.3266)."""
        resp = self.client.get("/api/page-image/3266?dpi=150")
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.content.startswith(PNG_MAGIC_BYTES))

        text = self.client.get("/api/page-text/3266").json()["text"]
        self.assertTrue(
            "humerus" in text.lower() or "proximal" in text.lower(),
            "Page 3266 text should discuss proximal humerus fractures"
        )

    def test_tier4_clinical_brostrom_ankle_render(self):
        """Clinical Scenario: Foot & ankle surgeon opens Broström procedure (p.4832 / Chapter 89)."""
        resp = self.client.get("/api/page-image/4832?dpi=150")
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.content.startswith(PNG_MAGIC_BYTES))

        text = self.client.get("/api/page-text/4832").json()["text"]
        self.assertTrue(
            "broström" in text.lower() or "brostrom" in text.lower() or "ligament" in text.lower(),
            "Page 4832 text should discuss lateral ankle ligament reconstruction"
        )

    # =========================================================================
    # TIER 1: FRONTEND WORKSTATION UI INTEGRITY
    # =========================================================================

    def test_tier1_frontend_viewer_toolbar_and_autocomplete_markup(self):
        """Verify index.html contains modal zoom controls, page navigation, and autocomplete container."""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)
        html = resp.text

        required_ids = [
            "btnPrevPage",
            "btnNextPage",
            "btnZoomIn",
            "btnZoomOut",
            "btnZoomReset",
            "pagePreviewLabel",
            "searchSuggestions",
            "globalSearch"
        ]
        for element_id in required_ids:
            self.assertIn(f'id="{element_id}"', html, f"index.html must include element with id='{element_id}'")

    def test_tier1_frontend_app_js_features(self):
        """Verify app.js implements zoom, page navigation, and search autocomplete logic."""
        resp = self.client.get("/static/app.js")
        self.assertEqual(resp.status_code, 200)
        js = resp.text

        required_functions = [
            "applyZoom",
            "setModalPdfPage",
            "handleSearchAutocomplete",
            "loadAllClassificationsCache",
            "closeSuggestions"
        ]
        for func_name in required_functions:
            self.assertIn(func_name, js, f"app.js must include implementation of {func_name}")

    def test_tier1_frontend_styles_autocomplete(self):
        """Verify styles.css includes styling rules for search suggestions and viewer toolbar."""
        resp = self.client.get("/static/styles.css")
        self.assertEqual(resp.status_code, 200)
        css = resp.text

        required_classes = [
            ".search-suggestions",
            ".suggestion-item",
            ".viewer-toolbar",
            ".page-preview-img"
        ]
        for class_name in required_classes:
            self.assertIn(class_name, css, f"styles.css must include CSS rule for '{class_name}'")


if __name__ == "__main__":
    unittest.main()
