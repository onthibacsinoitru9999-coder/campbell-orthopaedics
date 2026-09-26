"""Tier 4 E2E Tests: Real-World Clinical Workload Scenarios.

Verifies end-to-end clinician reference workflows from presentation to surgical plan:
1. Scenario 1: Tibial plateau fracture Schatzker II -> Tech 54-24 -> High-DPI page render
2. Scenario 2: Femoral neck fracture Garden III/IV / Pauwels III -> Tech 55-1 / 3-1
3. Scenario 3: Proximal humerus Neer 3-part / 4-part -> Tech 57-1 / 57-4
4. Scenario 4: Acetabular fracture Judet-Letournel posterior wall / both-column -> Tech 56-5, Approach 1-57
5. Scenario 5: Unstable thoracolumbar spine Denis burst fracture -> Tech 41-1..41-3
6. Scenario 6: Pronation-external rotation ankle Danis-Weber C -> Tech 88-1 / 89-1
7. Scenario 7: Gustilo-Anderson IIIB open tibia fracture -> Tech 53-1 / 54-1 / 63-1
"""

import unittest
from tests.e2e_client import get_test_client

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


class TestE2EClinicalScenarios(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = get_test_client()

    def test_clinical_scenario_1_schatzker_tibial_plateau(self):
        """Clinical Scenario 1: Lateral tibial plateau split-depression (Schatzker II)."""
        # Step 1: Clinician queries Guidemap for Tibia
        resp = self.client.get("/api/classifications", params={"bone": "TibiaLeft"})
        self.assertEqual(resp.status_code, 200)
        schatzker = next(c for c in resp.json() if c["id"] == "schatzker")

        # Step 2: Clinician evaluates Type II criteria
        type_ii = next(t for t in schatzker["types"] if "Type II" in (t.get("code") or t.get("type", "")))
        self.assertIn("lún", type_ii["desc"].lower())
        self.assertIn("nẹp", type_ii["management"].lower())

        # Step 3: Clinician retrieves linked operative technique 54-24
        self.assertIn("54-24", schatzker["techniques"])
        tech_resp = self.client.get("/api/techniques/54-24")
        self.assertEqual(tech_resp.status_code, 200)
        tech = tech_resp.json()
        self.assertEqual(tech["chapter"], 54)
        pdf_page = tech["pdf_page"]

        # Step 4: Clinician views High-DPI page render of surgical steps
        img_resp = self.client.get(f"/api/page-image/{pdf_page}?dpi=150")
        self.assertEqual(img_resp.status_code, 200)
        self.assertTrue(img_resp.content.startswith(PNG_MAGIC))

        # Step 5: Extract procedure text
        text_resp = self.client.get(f"/api/page-text/{pdf_page}")
        self.assertEqual(text_resp.status_code, 200)
        page_text = text_resp.json()["text"].lower()
        self.assertTrue("54-24" in page_text or "technique" in page_text or "condyle" in page_text or "fracture" in page_text)

    def test_clinical_scenario_2_garden_pauwels_femoral_neck(self):
        """Clinical Scenario 2: Displaced femoral neck fracture in elderly (Garden IV / Pauwels III)."""
        resp = self.client.get("/api/classifications", params={"bone": "FemurLeft"})
        self.assertEqual(resp.status_code, 200)
        classifs = {c["id"]: c for c in resp.json()}

        # Verify Garden & Pauwels both guide hip management
        self.assertIn("garden", classifs)
        self.assertIn("pauwels", classifs)

        garden = classifs["garden"]
        pauwels = classifs["pauwels"]

        # Garden IV: complete displacement, AVN risk -> Arthroplasty in elderly
        g4 = next(t for t in garden["types"] if "IV" in (t.get("code") or t.get("type", "")))
        self.assertTrue("thay khớp" in g4["management"].lower() or "bipolar" in g4["management"].lower())

        # Pauwels III: vertical shear angle > 50 degrees
        p3 = next(t for t in pauwels["types"] if "III" in (t.get("code") or t.get("type", "")))
        self.assertTrue("50" in p3["desc"])

        # Retrieve hip technique 55-1 and render page
        tech_resp = self.client.get("/api/techniques/55-1")
        self.assertEqual(tech_resp.status_code, 200)
        pdf_page = tech_resp.json()["pdf_page"]
        img_resp = self.client.get(f"/api/page-image/{pdf_page}?dpi=150")
        self.assertEqual(img_resp.status_code, 200)
        self.assertTrue(img_resp.content.startswith(PNG_MAGIC))

    def test_clinical_scenario_3_neer_proximal_humerus(self):
        """Clinical Scenario 3: Complex 3-part proximal humerus fracture (Neer classification)."""
        resp = self.client.get("/api/classifications", params={"bone": "HumerusLeft"})
        self.assertEqual(resp.status_code, 200)
        neer = next(c for c in resp.json() if c["id"] == "neer")

        # Verify 4 parts: One-part, Two-part, Three-part, Four-part
        types = neer["types"]
        self.assertGreaterEqual(len(types), 4)

        # Three-part management includes locking plate
        three_part = next(t for t in types if "Three-Part" in (t.get("code") or t.get("type", "")))
        self.assertTrue("nẹp" in three_part["management"].lower())

        # Four-part management includes shoulder arthroplasty
        four_part = next(t for t in types if "Four-Part" in (t.get("code") or t.get("type", "")))
        self.assertTrue("thay khớp" in four_part["management"].lower() or "hemiarthroplasty" in four_part["management"].lower())

        # Check linked techniques include chapter 57 and chapter 12
        self.assertTrue(any(t.startswith("57-") for t in neer["techniques"]))
        self.assertTrue(any(t.startswith("12-") for t in neer["techniques"]))

    def test_clinical_scenario_4_judet_letournel_acetabulum(self):
        """Clinical Scenario 4: Posterior wall and column acetabular fracture (Judet-Letournel)."""
        resp = self.client.get("/api/classifications", params={"bone": "PelvicGirdle"})
        self.assertEqual(resp.status_code, 200)
        letournel = next(c for c in resp.json() if c["id"] == "letournel_judet")

        # Verify Kocher-Langenbeck surgical approach is recommended for posterior wall/column
        post_wall = next(t for t in letournel["types"] if "thành sau" in (t.get("code", "") + t.get("desc", "")).lower())
        self.assertIn("kocher-langenbeck", post_wall["management"].lower())

        # Verify Ilioinguinal approach is recommended for anterior column
        ant_col = next(t for t in letournel["types"] if "cột trước" in (t.get("code", "") + t.get("desc", "")).lower())
        self.assertIn("ilioinguinal", ant_col["management"].lower())

        # Verify Technique 56-5 (acetabular reconstruction) detail retrieval
        t56_resp = self.client.get("/api/techniques/56-5")
        self.assertEqual(t56_resp.status_code, 200)
        self.assertEqual(t56_resp.json()["chapter"], 56)

    def test_clinical_scenario_5_denis_three_column_spine_burst(self):
        """Clinical Scenario 5: Unstable thoracolumbar burst fracture with retropulsion (Denis)."""
        resp = self.client.get("/api/classifications", params={"bone": "ThoracicVertebrae"})
        self.assertEqual(resp.status_code, 200)
        denis = next(c for c in resp.json() if c["id"] == "denis_spine")

        # Burst fracture involves both anterior and middle columns
        burst = next(
            t for t in denis["types"]
            if any(k in (t.get("code", "") + t.get("desc", "")).lower() for k in ["burst", "nổ", "gãy nổ"])
        )
        self.assertTrue("cột giữa" in burst["desc"].lower() or "middle" in burst["desc"].lower())
        self.assertTrue("vít" in burst["management"].lower() or "pedicle" in burst["management"].lower())

        # Retrieve spine technique 41-1 and verify high-DPI render
        tech_resp = self.client.get("/api/techniques/41-1")
        self.assertEqual(tech_resp.status_code, 200)
        pdf_page = tech_resp.json()["pdf_page"]
        img_resp = self.client.get(f"/api/page-image/{pdf_page}?dpi=150")
        self.assertEqual(img_resp.status_code, 200)
        self.assertTrue(img_resp.content.startswith(PNG_MAGIC))

    def test_clinical_scenario_6_danis_weber_c_ankle_syndesmosis(self):
        """Clinical Scenario 6: High fibular fracture with syndesmotic diastasis (Danis-Weber C)."""
        resp = self.client.get("/api/classifications", params={"bone": "FibulaLeft"})
        self.assertEqual(resp.status_code, 200)
        weber = next(c for c in resp.json() if c["id"] == "danis_weber")

        # Weber C: suprasyndesmotic fracture requiring syndesmotic fixation
        weber_c = next(t for t in weber["types"] if "weber c" in t.get("code", "").lower())
        self.assertTrue("trên" in weber_c["desc"].lower() or "suprasyndesmotic" in weber_c["desc"].lower())
        self.assertTrue("chày mác dưới" in weber_c["management"].lower() or "syndesmotic" in weber_c["management"].lower())

        # Retrieve linked ankle technique 88-1
        tech_resp = self.client.get("/api/techniques/88-1")
        self.assertEqual(tech_resp.status_code, 200)
        self.assertEqual(tech_resp.json()["chapter"], 88)

    def test_clinical_scenario_7_gustilo_open_fracture_protocol(self):
        """Clinical Scenario 7: Severe open tibia fracture (Gustilo-Anderson IIIB)."""
        resp = self.client.get("/api/classifications", params={"q": "Gustilo"})
        self.assertEqual(resp.status_code, 200)
        gustilo = resp.json()[0]

        # Type IIIB: extensive soft tissue injury, periosteal stripping, requiring flap
        type_3b = next(t for t in gustilo["types"] if "IIIB" in (t.get("code") or t.get("type", "")))
        self.assertTrue("màng xương" in type_3b["desc"].lower() or "periosteal" in type_3b["desc"].lower())
        self.assertTrue("vạt" in type_3b["management"].lower() or "flap" in type_3b["management"].lower())

        # Verify linked multidisciplinary techniques (Ch 53 general principles, Ch 54 fracture, Ch 63 microsurgery/flaps)
        techs = gustilo["techniques"]
        self.assertTrue(any(t.startswith("53-") for t in techs))
        self.assertTrue(any(t.startswith("54-") for t in techs))
        self.assertTrue(any(t.startswith("63-") for t in techs))


if __name__ == "__main__":
    unittest.main()
