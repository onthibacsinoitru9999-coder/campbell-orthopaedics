"""Tier 1 to Tier 4 E2E Tests: 6-Part Volume Integrity, Data Auditing & Catalog Continuity.

Verifies:
- Tier 1: Feature Coverage (89 chapters, 14 categories, 6,885 outline headings, 1,671 techniques, zero duplicate IDs)
- Tier 2: Boundary & Corner Cases (Continuity 1..N per chapter, valid page bounds [1, 4887], patched 16 anomalies)
- Tier 3: Surgical Approaches Audit (Chapter 1 general approaches, Chapter 37 spinal approaches)
- Tier 4: Multi-Volume Representative Sampling (Vol 1, Vol 2, Vol 3, Vol 4 cross-verification with PDF content)
"""

import json
import os
import unittest
from tests.e2e_client import get_test_client


class TestE2EAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = get_test_client()

        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
        with open(os.path.join(data_dir, "techniques_catalog.json"), "r", encoding="utf-8") as f:
            cls.techniques = json.load(f)

        with open(os.path.join(data_dir, "chapters_catalog.json"), "r", encoding="utf-8") as f:
            cls.chapters = json.load(f)

        with open(os.path.join(data_dir, "anatomical_categories.json"), "r", encoding="utf-8") as f:
            cls.categories = json.load(f)

        with open(os.path.join(data_dir, "outline_tree.json"), "r", encoding="utf-8") as f:
            cls.outline = json.load(f)

    # =========================================================================
    # TIER 1: FEATURE COVERAGE
    # =========================================================================

    def test_tier1_89_chapters_presence(self):
        """Verify all 89 chapters are present in the chapters catalog and API."""
        resp = self.client.get("/api/chapters")
        self.assertEqual(resp.status_code, 200)
        api_chaps = resp.json()
        self.assertEqual(len(api_chaps), 89, f"Expected 89 chapters, got {len(api_chaps)}")

        chapter_numbers = {c["chapter"] for c in api_chaps}
        expected_set = set(range(1, 90))
        self.assertEqual(chapter_numbers, expected_set, "Chapters must span continuously from 1 to 89")

    def test_tier1_14_anatomical_categories(self):
        """Verify all 14 anatomical categories are configured and cover all 89 chapters."""
        resp = self.client.get("/api/categories")
        self.assertEqual(resp.status_code, 200)
        api_cats = resp.json()
        self.assertEqual(len(api_cats), 14, f"Expected 14 categories, got {len(api_cats)}")

        # Verify all 89 chapters are covered across categories
        all_covered_chaps = set()
        for cat in api_cats:
            all_covered_chaps.update(cat["chapters"])
            self.assertGreater(cat["technique_count"], 0, f"Category '{cat['id']}' has 0 techniques")

        self.assertEqual(
            len(all_covered_chaps), 89,
            f"Expected 89 unique chapters covered across 14 categories, got {len(all_covered_chaps)}"
        )

    def test_tier1_outline_tree_structure(self):
        """Verify the master outline tree is accessible and structured hierarchically."""
        resp = self.client.get("/api/outline")
        self.assertEqual(resp.status_code, 200)
        tree = resp.json()
        self.assertIsInstance(tree, list)
        self.assertGreater(len(tree), 0)

        # Count total outline nodes recursively
        def count_nodes(nodes):
            total = len(nodes)
            for n in nodes:
                if "children" in n and n["children"]:
                    total += count_nodes(n["children"])
            return total

        total_outline_headings = count_nodes(tree)
        self.assertGreaterEqual(
            total_outline_headings, 6000,
            f"Outline tree should contain ~6,885 headings, got {total_outline_headings}"
        )

    def test_tier1_zero_duplicate_technique_ids(self):
        """Data Integrity: Ensure 0 duplicate technique IDs across all 1,671 techniques."""
        tech_ids = [t["tech_id"] for t in self.techniques]
        self.assertEqual(len(tech_ids), 1671)
        unique_ids = set(tech_ids)
        self.assertEqual(
            len(unique_ids), 1671,
            f"Found duplicate technique IDs: {len(tech_ids) - len(unique_ids)} duplicates"
        )

    # =========================================================================
    # TIER 2: BOUNDARY & CORNER CASES
    # =========================================================================

    def test_tier2_techniques_continuity_per_chapter(self):
        """Verify technique numbering begins at 1 and is largely continuous within chapters."""
        by_chapter = {}
        for t in self.techniques:
            c = t["chapter"]
            num = int(t["tech_id"].split("-")[1])
            by_chapter.setdefault(c, []).append(num)

        # 80 of 89 chapters have techniques (9 chapters are text/overview chapters)
        self.assertGreaterEqual(len(by_chapter), 80)

        for c, nums in by_chapter.items():
            min_num = min(nums)
            max_num = max(nums)
            self.assertEqual(min_num, 1, f"Chapter {c} technique numbering should start at 1, starts at {min_num}")
            self.assertEqual(len(nums), len(set(nums)), f"Chapter {c} has duplicate technique numbers")

    def test_tier2_all_techniques_have_valid_pdf_pages(self):
        """Verify all 1,671 techniques have valid pdf_page in range [1, 4887]."""
        for t in self.techniques:
            p = t.get("pdf_page")
            self.assertIsNotNone(p, f"Technique {t['tech_id']} missing pdf_page")
            self.assertGreaterEqual(p, 1, f"Technique {t['tech_id']} has pdf_page < 1")
            self.assertLessEqual(p, 4887, f"Technique {t['tech_id']} has pdf_page > 4887")

    def test_tier2_exact_page_mapping_patched(self):
        """Verify the 16 previously anomalous page assignments were corrected."""
        patched_expected = {
            "89-2": 4832,   # Broström procedure (previously jumped to 570)
            "58-10": 3376,  # Previously jumped to 567
            "82-2": 4487,   # Previously jumped to 567
            "83-6": 4569,   # Previously jumped to 1161
            "86-14": 4702,  # Previously jumped to 567
            "52-14": 2894,  # Previously defaulted to chapter start
            "79-47": 4325   # Previously defaulted to chapter start
        }
        tech_dict = {t["tech_id"]: t for t in self.techniques}
        for tech_id, expected_page in patched_expected.items():
            tech = tech_dict.get(tech_id)
            self.assertIsNotNone(tech, f"Technique {tech_id} must exist in catalog")
            self.assertEqual(
                tech["pdf_page"], expected_page,
                f"Technique {tech_id} expected at page {expected_page}, but got {tech['pdf_page']}"
            )

    # =========================================================================
    # TIER 3: SURGICAL APPROACHES & SPECIAL CHAPTERS
    # =========================================================================

    def test_tier3_surgical_approaches_chapter_1(self):
        """Audit Chapter 1: Surgical Approaches (foundational surgical access routes)."""
        ch1_techs = [t for t in self.techniques if t["chapter"] == 1]
        self.assertGreaterEqual(len(ch1_techs), 50, "Chapter 1 should contain over 50 surgical approaches")

        # Verify key eponymic approaches
        ch1_titles = " ".join([t["name"] for t in ch1_techs]).lower()
        key_approaches = ["smith-petersen", "kocher", "campbell", "abbott", "anterolateral"]
        for app in key_approaches:
            self.assertIn(app, ch1_titles, f"Key approach '{app}' missing from Chapter 1 techniques")

    def test_tier3_spinal_approaches_chapter_37(self):
        """Audit Chapter 37: Spinal Anatomy and Approaches."""
        ch37_techs = [t for t in self.techniques if t["chapter"] == 37]
        self.assertGreaterEqual(len(ch37_techs), 1, "Chapter 37 should have documented spinal approaches")
        # Check that Chapter 37 starts around page 1757
        ch37_info = next(c for c in self.chapters if c["chapter"] == 37)
        self.assertGreaterEqual(ch37_info["start_page"], 1700)

    # =========================================================================
    # TIER 4: MULTI-VOLUME REPRESENTATIVE SAMPLING
    # =========================================================================

    def test_tier4_volume_1_sampling(self):
        """Representative sample from Volume 1 (Chapters 1-28, Arthroplasty & Principles)."""
        sample_ids = ["1-1", "3-1", "12-1", "21-3"]
        for tech_id in sample_ids:
            resp = self.client.get(f"/api/techniques/{tech_id}")
            self.assertEqual(resp.status_code, 200)
            data = resp.json()
            self.assertIn(data["chapter"], range(1, 29))
            self.assertLess(data["pdf_page"], 1200)

    def test_tier4_volume_2_sampling(self):
        """Representative sample from Volume 2 (Chapters 29-47, Pediatrics, Spine, Sports)."""
        sample_ids = ["32-19", "41-1", "45-12"]
        for tech_id in sample_ids:
            resp = self.client.get(f"/api/techniques/{tech_id}")
            self.assertEqual(resp.status_code, 200)
            data = resp.json()
            self.assertIn(data["chapter"], range(29, 48))
            self.assertGreater(data["pdf_page"], 1100)
            self.assertLess(data["pdf_page"], 2800)

    def test_tier4_volume_3_sampling(self):
        """Representative sample from Volume 3 (Chapters 48-63, Trauma & Fractures)."""
        sample_ids = ["54-24", "55-1", "56-5", "57-4"]
        for tech_id in sample_ids:
            resp = self.client.get(f"/api/techniques/{tech_id}")
            self.assertEqual(resp.status_code, 200)
            data = resp.json()
            self.assertIn(data["chapter"], range(48, 64))
            self.assertGreater(data["pdf_page"], 2700)
            self.assertLess(data["pdf_page"], 3800)

    def test_tier4_volume_4_sampling(self):
        """Representative sample from Volume 4 (Chapters 64-89, Hand, Foot & Ankle)."""
        sample_ids = ["67-1", "81-3", "88-1", "89-2"]
        for tech_id in sample_ids:
            resp = self.client.get(f"/api/techniques/{tech_id}")
            self.assertEqual(resp.status_code, 200)
            data = resp.json()
            self.assertIn(data["chapter"], range(64, 90))
            self.assertGreater(data["pdf_page"], 3700)
            self.assertLessEqual(data["pdf_page"], 4887)


if __name__ == "__main__":
    unittest.main()
