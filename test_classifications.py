"""
Comprehensive Verification Test Suite for Clinical Classifications & Medical Linking
Grounded in Campbell's Operative Orthopaedics (13th Edition).
Verifies:
- All 17 classifications (12 upgraded + 5 newly added).
- Complete schema adherence for every type (type, name, description, principles, technique_id, technique_title, button_label).
- 100% valid technique_id references against data/techniques_catalog.json.
- Accurate Campbell 13th Ed clinical linkages for all required classification systems.
- Bone filtering and query endpoints in server.py.
"""

import sys
import json
import unittest
from fastapi.testclient import TestClient

sys.stdout.reconfigure(encoding='utf-8')
import server

class TestClassifications(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(server.app)
        with open('data/techniques_catalog.json', encoding='utf-8') as f:
            cls.catalog_techniques = json.load(f)
        cls.tech_by_id = {t['tech_id']: t for t in cls.catalog_techniques}

    def test_total_classifications_count(self):
        """Verify that exactly 17 classifications exist (12 classic + 5 newly added)."""
        res = self.client.get('/api/classifications')
        self.assertEqual(res.status_code, 200)
        items = res.json()
        self.assertEqual(len(items), 17, f"Expected 17 classifications, got {len(items)}")

    def test_all_17_classification_ids_present(self):
        """Verify presence of all 17 expected classification IDs."""
        expected_ids = {
            "schatzker", "garden", "pauwels", "neer", "gustilo",
            "young_burgess", "letournel_judet", "denis_spine", "danis_weber",
            "hawkins", "frykman", "mason",
            "ao_ota", "salter_harris", "pipkin", "sanders", "anderson_dalonzo"
        }
        res = self.client.get('/api/classifications')
        actual_ids = {c["id"] for c in res.json()}
        missing = expected_ids - actual_ids
        self.assertEqual(len(missing), 0, f"Missing classification IDs: {missing}")

    def test_top_level_schema(self):
        """Verify each classification has all required top-level metadata."""
        res = self.client.get('/api/classifications')
        required_keys = [
            "id", "name", "en_name", "bone", "bone_vi", "svg_ids",
            "category", "chapter", "chapter_title", "pdf_page", "book_page",
            "description", "types", "techniques"
        ]
        for c in res.json():
            for key in required_keys:
                self.assertIn(key, c, f"Classification '{c.get('id')}' missing key '{key}'")
            self.assertIsInstance(c["types"], list)
            self.assertGreater(len(c["types"]), 0, f"Classification '{c['id']}' has empty types")
            self.assertIsInstance(c["techniques"], list)
            self.assertGreater(len(c["techniques"]), 0, f"Classification '{c['id']}' has empty techniques")

    def test_per_type_mandatory_schema(self):
        """Verify each item in types[] contains all required schema fields."""
        res = self.client.get('/api/classifications')
        mandatory_fields = [
            "type", "name", "description", "principles",
            "technique_id", "technique_title", "button_label",
            "code", "desc", "management"  # Backward compatibility
        ]
        for c in res.json():
            for t in c["types"]:
                for field in mandatory_fields:
                    self.assertIn(field, t, f"Type in '{c['id']}' missing mandatory field '{field}': {t}")
                    self.assertTrue(str(t[field]).strip(), f"Field '{field}' in '{c['id']}' must not be empty")

    def test_all_technique_ids_exist_in_catalog(self):
        """Verify that EVERY technique_id across all types exists in data/techniques_catalog.json."""
        res = self.client.get('/api/classifications')
        checked_type_links = 0
        for c in res.json():
            for t in c["types"]:
                tid = t["technique_id"]
                self.assertIn(
                    tid, self.tech_by_id,
                    f"Technique ID '{tid}' in classification '{c['id']}', type '{t['type']}' NOT FOUND in techniques_catalog.json!"
                )
                checked_type_links += 1

        print(f"Verified {checked_type_links} per-type technique_id links against catalog: 100% VALID")

    def test_all_top_level_techniques_exist_in_catalog(self):
        """Verify that EVERY technique in top-level techniques[] exists in data/techniques_catalog.json."""
        res = self.client.get('/api/classifications')
        checked_top_links = 0
        for c in res.json():
            for tid in c["techniques"]:
                self.assertIn(
                    tid, self.tech_by_id,
                    f"Top-level technique '{tid}' in '{c['id']}' NOT FOUND in techniques_catalog.json!"
                )
                checked_top_links += 1

        print(f"Verified {checked_top_links} top-level classification technique links against catalog: 100% VALID")

    def test_schatzker_clinical_linkages(self):
        """Verify Schatzker tibial plateau types and techniques."""
        res = self.client.get('/api/classifications')
        schatzker = next(c for c in res.json() if c["id"] == "schatzker")
        self.assertEqual(len(schatzker["types"]), 6)
        self.assertIn("54-14", schatzker["techniques"])
        self.assertIn("54-24", schatzker["techniques"])
        self.assertIn("54-15", schatzker["techniques"])
        self.assertIn("54-16", schatzker["techniques"])
        self.assertIn("54-17", schatzker["techniques"])

        t_map = {t["type"]: t["technique_id"] for t in schatzker["types"]}
        self.assertEqual(t_map["Type I"], "54-14")
        self.assertEqual(t_map["Type II"], "54-14")
        self.assertEqual(t_map["Type III"], "54-14")
        self.assertEqual(t_map["Type IV"], "54-15")
        self.assertEqual(t_map["Type V"], "54-16")
        self.assertEqual(t_map["Type VI"], "54-17")

    def test_garden_and_pauwels_clinical_linkages(self):
        """Verify Garden & Pauwels femoral neck types and techniques."""
        res = self.client.get('/api/classifications')
        garden = next(c for c in res.json() if c["id"] == "garden")
        pauwels = next(c for c in res.json() if c["id"] == "pauwels")

        self.assertEqual(len(garden["types"]), 4)
        self.assertTrue(any(t in garden["techniques"] for t in ["55-1", "55-2", "3-1"]))
        g_map = {t["type"]: t["technique_id"] for t in garden["types"]}
        self.assertEqual(g_map["Garden I"], "54-20")
        self.assertEqual(g_map["Garden II"], "54-20")
        self.assertEqual(g_map["Garden III"], "54-21")
        self.assertEqual(g_map["Garden IV"], "54-22")

        self.assertEqual(len(pauwels["types"]), 3)
        p_map = {t["type"]: t["technique_id"] for t in pauwels["types"]}
        self.assertEqual(p_map["Pauwels Type I"], "54-20")
        self.assertEqual(p_map["Pauwels Type II"], "54-21")
        self.assertEqual(p_map["Pauwels Type III"], "54-22")

    def test_neer_clinical_linkages(self):
        """Verify Neer proximal humerus types and techniques."""
        res = self.client.get('/api/classifications')
        neer = next(c for c in res.json() if c["id"] == "neer")
        self.assertIn("57-4", neer["techniques"])
        self.assertIn("57-5", neer["techniques"])
        self.assertIn("57-3", neer["techniques"])

        t_map = {t["type"]: t["technique_id"] for t in neer["types"]}
        self.assertEqual(t_map["Two-Part"], "57-4")
        self.assertEqual(t_map["Three-Part"], "57-4")
        self.assertEqual(t_map["Four-Part"], "57-5")
        self.assertEqual(t_map["Tuberosity Part"], "57-3")

    def test_judet_letournel_clinical_linkages(self):
        """Verify Judet-Letournel acetabulum types and techniques."""
        res = self.client.get('/api/classifications')
        letournel = next(c for c in res.json() if c["id"] == "letournel_judet")
        self.assertIn("53-1", letournel["techniques"])
        self.assertIn("53-2", letournel["techniques"])
        self.assertIn("53-3", letournel["techniques"])

        t_map = {t["type"]: t["technique_id"] for t in letournel["types"]}
        self.assertEqual(t_map["Thành trước / Cột trước"], "53-1")
        self.assertEqual(t_map["Thành sau / Cột sau"], "53-2")
        self.assertEqual(t_map["Hai cột / Chữ T"], "53-3")

    def test_denis_spine_clinical_linkages(self):
        """Verify Denis thoracolumbar spine types and techniques."""
        res = self.client.get('/api/classifications')
        denis = next(c for c in res.json() if c["id"] == "denis_spine")
        self.assertIn("38-1", denis["techniques"])
        self.assertIn("38-2", denis["techniques"])
        self.assertIn("38-3", denis["techniques"])
        self.assertIn("38-5", denis["techniques"])

        t_map = {t["type"]: t["technique_id"] for t in denis["types"]}
        self.assertEqual(t_map["Gãy nén (Compression)"], "38-1")
        self.assertEqual(t_map["Gãy nổ (Burst Fracture)"], "38-2")
        self.assertEqual(t_map["Gãy uốn căng (Seat-belt / Chance)"], "38-3")
        self.assertEqual(t_map["Gãy trật (Fracture-Dislocation)"], "38-5")

    def test_young_burgess_clinical_linkages(self):
        """Verify Young-Burgess pelvic ring types and techniques."""
        res = self.client.get('/api/classifications')
        yb = next(c for c in res.json() if c["id"] == "young_burgess")
        self.assertIn("53-5", yb["techniques"])
        self.assertIn("53-6", yb["techniques"])

        t_map = {t["type"]: t["technique_id"] for t in yb["types"]}
        self.assertEqual(t_map["LC (Lateral Compression)"], "53-5")
        self.assertEqual(t_map["APC (Anterior-Posterior Compression)"], "53-6")
        self.assertEqual(t_map["VS (Vertical Shear)"], "56-10")

    def test_danis_weber_clinical_linkages(self):
        """Verify Danis-Weber ankle types and techniques in Chapter 54."""
        res = self.client.get('/api/classifications')
        weber = next(c for c in res.json() if c["id"] == "danis_weber")
        self.assertEqual(weber["chapter"], 54)
        self.assertIn("54-1", weber["techniques"])
        self.assertIn("54-2", weber["techniques"])
        self.assertIn("54-3", weber["techniques"])

        t_map = {t["type"]: t["technique_id"] for t in weber["types"]}
        self.assertEqual(t_map["Weber A"], "54-1")
        self.assertEqual(t_map["Weber B"], "54-2")
        self.assertEqual(t_map["Weber C"], "54-3")

    def test_hawkins_clinical_linkages(self):
        """Verify Hawkins talus types and techniques in Chapter 88."""
        res = self.client.get('/api/classifications')
        hawkins = next(c for c in res.json() if c["id"] == "hawkins")
        self.assertEqual(hawkins["chapter"], 88)
        self.assertIn("88-8", hawkins["techniques"])
        self.assertIn("88-9", hawkins["techniques"])

        t_map = {t["type"]: t["technique_id"] for t in hawkins["types"]}
        self.assertEqual(t_map["Type I"], "88-8")
        self.assertEqual(t_map["Type II"], "88-8")
        self.assertEqual(t_map["Type III"], "88-8")
        self.assertEqual(t_map["Type IV"], "88-9")

    def test_frykman_clinical_linkages(self):
        """Verify Frykman distal radius types and techniques in Chapter 57."""
        res = self.client.get('/api/classifications')
        frykman = next(c for c in res.json() if c["id"] == "frykman")
        self.assertEqual(frykman["chapter"], 57)
        self.assertIn("57-13", frykman["techniques"])
        self.assertIn("57-14", frykman["techniques"])
        self.assertIn("57-15", frykman["techniques"])

        t_map = {t["type"]: t["technique_id"] for t in frykman["types"]}
        self.assertEqual(t_map["Type I & II"], "57-13")
        self.assertEqual(t_map["Type III & IV"], "57-15")
        self.assertEqual(t_map["Type V & VI"], "57-14")
        self.assertEqual(t_map["Type VII & VIII"], "57-15")

    def test_mason_clinical_linkages(self):
        """Verify Mason radial head types and techniques."""
        res = self.client.get('/api/classifications')
        mason = next(c for c in res.json() if c["id"] == "mason")
        self.assertIn("57-9", mason["techniques"])
        self.assertIn("12-6", mason["techniques"])

        t_map = {t["type"]: t["technique_id"] for t in mason["types"]}
        self.assertEqual(t_map["Type I"], "57-9")
        self.assertEqual(t_map["Type II"], "57-9")
        self.assertEqual(t_map["Type III"], "12-6")
        self.assertEqual(t_map["Type IV"], "12-6")

    def test_ao_ota_coverage(self):
        """Verify AO/OTA Comprehensive Classification covers 11 through 44 (13 segments)."""
        res = self.client.get('/api/classifications')
        ao = next(c for c in res.json() if c["id"] == "ao_ota")
        expected_segments = ["11", "12", "13", "21", "22", "23", "31", "32", "33", "41", "42", "43", "44"]
        actual_types = [t["type"] for t in ao["types"]]
        for seg in expected_segments:
            self.assertTrue(any(seg in t for t in actual_types), f"AO/OTA missing segment {seg}")

    def test_salter_harris_coverage(self):
        """Verify Salter-Harris pediatric physeal classification has Types I to V."""
        res = self.client.get('/api/classifications')
        sh = next(c for c in res.json() if c["id"] == "salter_harris")
        self.assertEqual(sh["category"], "Pediatrics")
        self.assertEqual(sh["chapter"], 36)
        self.assertEqual(len(sh["types"]), 5)
        for expected in ["Type I", "Type II", "Type III", "Type IV", "Type V"]:
            self.assertTrue(any(expected in t["type"] for t in sh["types"]), f"Salter-Harris missing {expected}")

    def test_pipkin_coverage(self):
        """Verify Pipkin femoral head classification has Types I to IV."""
        res = self.client.get('/api/classifications')
        pipkin = next(c for c in res.json() if c["id"] == "pipkin")
        self.assertEqual(len(pipkin["types"]), 4)
        for expected in ["Pipkin I", "Pipkin II", "Pipkin III", "Pipkin IV"]:
            self.assertTrue(any(expected in t["type"] for t in pipkin["types"]), f"Pipkin missing {expected}")

    def test_sanders_coverage(self):
        """Verify Sanders calcaneal fracture classification has Types I to IV."""
        res = self.client.get('/api/classifications')
        sanders = next(c for c in res.json() if c["id"] == "sanders")
        self.assertEqual(len(sanders["types"]), 4)
        for expected in ["Sanders Type I", "Sanders Type II", "Sanders Type III", "Sanders Type IV"]:
            self.assertTrue(any(expected in t["type"] for t in sanders["types"]), f"Sanders missing {expected}")

    def test_anderson_dalonzo_coverage(self):
        """Verify Anderson-D'Alonzo odontoid process classification has Types I to III."""
        res = self.client.get('/api/classifications')
        ad = next(c for c in res.json() if c["id"] == "anderson_dalonzo")
        self.assertEqual(len(ad["types"]), 3)
        for expected in ["Type I", "Type II", "Type III"]:
            self.assertTrue(any(expected in t["type"] for t in ad["types"]), f"Anderson-D'Alonzo missing {expected}")

    def test_bone_filtering_endpoints(self):
        """Verify /api/classifications?bone={bone_id} works for all major bones."""
        test_bones = [
            ("TibiaLeft", ["schatzker", "gustilo", "ao_ota"]),
            ("FemurLeft", ["garden", "pauwels", "pipkin", "ao_ota"]),
            ("FemurRight", ["garden", "pauwels", "pipkin", "ao_ota"]),
            ("HumerusLeft", ["neer", "ao_ota"]),
            ("PelvicGirdle", ["young_burgess", "letournel_judet"]),
            ("ThoracicVertebrae", ["denis_spine", "anderson_dalonzo"]),
            ("FibulaLeft", ["danis_weber", "gustilo", "ao_ota"]),
            ("RadiusLeft", ["frykman", "mason", "ao_ota"]),
            ("TarsalsLeft", ["hawkins", "sanders", "danis_weber"])
        ]
        for bone, expected_ids in test_bones:
            res = self.client.get(f'/api/classifications?bone={bone}')
            self.assertEqual(res.status_code, 200)
            returned_ids = {c["id"] for c in res.json()}
            for exp_id in expected_ids:
                self.assertIn(exp_id, returned_ids, f"Bone '{bone}' expected to contain '{exp_id}'")

    def test_search_classifications_query(self):
        """Verify /api/classifications?q={query} searches name, en_name, bone, and description."""
        queries = [
            ("Schatzker", "schatzker"),
            ("mâm chày", "schatzker"),
            ("Garden", "garden"),
            ("cổ xương đùi", "garden"),
            ("Pauwels", "pauwels"),
            ("Neer", "neer"),
            ("AO/OTA", "ao_ota"),
            ("Salter", "salter_harris"),
            ("Pipkin", "pipkin"),
            ("Sanders", "sanders"),
            ("Anderson", "anderson_dalonzo")
        ]
        for q, expected_id in queries:
            res = self.client.get(f'/api/classifications?q={q}')
            self.assertEqual(res.status_code, 200)
            returned_ids = {c["id"] for c in res.json()}
            self.assertIn(expected_id, returned_ids, f"Query '{q}' did not return expected '{expected_id}'")


if __name__ == '__main__':
    unittest.main()
