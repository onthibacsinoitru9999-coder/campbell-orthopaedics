"""Challenger 1 Adversarial Oracles for Milestone 1 (M1).

Oracles:
1. Check every technique in Ch 62, 63, 65, 68, 76 for any lingering inappropriate mechanical boilerplate:
   'đinh nội tủy', 'nẹp vít', 'khoan nẹp', 'cắt xương', 'bắt vít', 'osteotomy', 'intramedullary nail'.
2. Stress-check all 21 hand techniques:
   verify surgical_steps[0] describes incision/exposure and surgical_steps[-1] describes closure/dressing/splint.
3. Verify 1:1 synchronization between all 1,671 data/techniques/*.json and data/clinical_techniques.json (0 content mismatches).
4. Verify that Garden, Pauwels, and Judet-Letournel do NOT contain patellectomy or RIA.
"""

import json
import glob
import os
import re
import sys

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def run_oracle_1():
    print("=" * 60)
    print("ORACLE 1: Inappropriate Mechanical Boilerplate in Ch 62, 63, 65, 68, 76")
    print("=" * 60)
    
    boilerplate_terms = [
        'đinh nội tủy', 'nẹp vít', 'khoan nẹp', 'cắt xương', 'bắt vít',
        'osteotomy', 'intramedullary nail'
    ]
    
    target_chapters = [62, 63, 65, 68, 76]
    files = []
    for ch in target_chapters:
        pattern = f"data/techniques/{ch}-*.json"
        matched = glob.glob(pattern)
        files.extend(matched)
        print(f"Chapter {ch}: found {len(matched)} techniques")
        
    print(f"Total techniques across target chapters: {len(files)}")
    
    findings = []
    
    for fpath in files:
        with open(fpath, "r", encoding="utf-8") as f:
            tech = json.load(f)
            
        tech_id = tech.get("tech_id", os.path.basename(fpath))
        tech_name = tech.get("name", "")
        
        # Check all text fields
        full_text = json.dumps(tech, ensure_ascii=False).lower()
        
        matched_terms = []
        for term in boilerplate_terms:
            if term.lower() in full_text:
                matched_terms.append(term)
                
        if matched_terms:
            findings.append({
                "file": fpath,
                "tech_id": tech_id,
                "name": tech_name,
                "matched_terms": matched_terms,
                "tech": tech
            })
            
    print(f"\nOracle 1 Result: Found {len(findings)} techniques containing search terms.")
    for item in findings:
        print(f"  [-] {item['tech_id']} ({item['file']}): matched {item['matched_terms']}")
        # Print snippet of where it matched
        text = json.dumps(item['tech'], ensure_ascii=False)
        for term in item['matched_terms']:
            idx = text.lower().find(term.lower())
            if idx != -1:
                start = max(0, idx - 50)
                end = min(len(text), idx + len(term) + 50)
                print(f"      Context around '{term}': ...{text[start:end]}...")
                
    return findings

def run_oracle_2():
    print("\n" + "=" * 60)
    print("ORACLE 2: Stress-check all 21 Hand Techniques Sequence")
    print("=" * 60)
    
    target_21 = [
        "64-2", "65-9", "67-14", "67-29", "69-5", "69-21", "69-28", "69-49",
        "70-1", "70-2", "73-3", "76-5", "78-2", "78-5", "78-7", "79-9",
        "79-12", "79-27", "79-32", "79-41", "79-57"
    ]
    
    print(f"Checking {len(target_21)} specified hand techniques...")
    
    incision_keywords = [
        r'\brạch\b', r'\bbộc lộ\b', r'\bincision\b', r'\bexposure\b', r'\btiếp cận\b',
        r'\bapproach\b', r'\brạch da\b', r'\btư thế\b', r'\bpatient prep\b',
        r'\bpreparation\b', r'\bpositioning\b', r'\bbóc tách\b', r'\bphẫu tích\b',
        r'\bvô cảm\b', r'\banesthesia\b'
    ]
    closure_keywords = [
        r'\bđóng\b', r'\bkhâu\b', r'\bbó bột\b', r'\bnẹp\b', r'\bclosure\b',
        r'\bclose\b', r'\bdressing\b', r'\bsplint\b', r'\bbăng\b', r'\bbất động\b',
        r'\bdẫn lưu\b', r'\bvết mổ\b', r'\bgrafting\b', r'\bghép da\b'
    ]
    
    failures = []
    
    for tid in target_21:
        fpath = f"data/techniques/{tid}.json"
        if not os.path.exists(fpath):
            failures.append((tid, "FILE_NOT_FOUND", "", ""))
            continue
            
        with open(fpath, "r", encoding="utf-8") as f:
            tech = json.load(f)
            
        steps = tech.get("surgical_steps", [])
        if not steps:
            failures.append((tid, "NO_STEPS", "", ""))
            continue
            
        step_first = steps[0]
        step_last = steps[-1]
        
        first_title_desc = f"{step_first.get('title', '')} {step_first.get('detail', '')} {step_first.get('action', '')} {step_first.get('desc', '')}".lower()
        last_title_desc = f"{step_last.get('title', '')} {step_last.get('detail', '')} {step_last.get('action', '')} {step_last.get('desc', '')}".lower()
        
        first_ok = any(re.search(kw, first_title_desc) for kw in incision_keywords)
        last_ok = any(re.search(kw, last_title_desc) for kw in closure_keywords)

        
        # Check if first step is mistakenly closure (inverted order bug)
        first_title = step_first.get('title', '').lower()
        last_title = step_last.get('title', '').lower()
        first_is_closure = any(kw in first_title for kw in ['đóng vết mổ', 'bó bột', 'nẹp bột', 'closure', 'khâu da'])
        last_is_incision = any(kw in last_title for kw in ['đường rạch', 'rạch da &', 'skin incision', 'incision & exposure'])
        
        status = "PASS"
        issues = []
        if not first_ok or first_is_closure:
            status = "FAIL"
            issues.append(f"Step 0 not incision/exposure: '{step_first.get('title')}'")
        if not last_ok or last_is_incision:
            status = "FAIL"
            issues.append(f"Step -1 not closure/dressing/splint: '{step_last.get('title')}'")
            
        print(f"  [{status}] {tid}:")
        first_summary = step_first.get('detail') or step_first.get('action') or step_first.get('desc') or ''
        last_summary = step_last.get('detail') or step_last.get('action') or step_last.get('desc') or ''
        print(f"      Step 1: {step_first.get('title')} -> {str(first_summary)[:80]}...")
        print(f"      Step {len(steps)}: {step_last.get('title')} -> {str(last_summary)[:80]}...")
        if issues:
            print(f"      ISSUES: {issues}")
            failures.append((tid, issues, step_first, step_last))
            
    print(f"\nOracle 2 Result: {len(failures)} failures out of {len(target_21)} techniques.")
    return failures

def run_oracle_3():
    print("\n" + "=" * 60)
    print("ORACLE 3: 1:1 Synchronization between data/techniques/*.json and clinical_techniques.json")
    print("=" * 60)
    
    with open("data/clinical_techniques.json", "r", encoding="utf-8") as f:
        master = json.load(f)
        
    master_map = master if isinstance(master, dict) else {t["tech_id"]: t for t in master}
    
    file_paths = glob.glob("data/techniques/*.json")
    print(f"Total individual technique files: {len(file_paths)}")
    print(f"Total techniques in master file: {len(master_map)}")
    
    mismatches = []
    missing_in_master = []
    missing_in_files = []
    
    file_map = {}
    for fpath in file_paths:
        tid = os.path.splitext(os.path.basename(fpath))[0]
        with open(fpath, "r", encoding="utf-8") as f:
            t = json.load(f)
            file_map[tid] = t
            
    for tid in file_map:
        if tid not in master_map:
            missing_in_master.append(tid)
            
    for tid in master_map:
        if tid not in file_map:
            missing_in_files.append(tid)
            
    for tid, file_tech in file_map.items():
        if tid in master_map:
            master_tech = master_map[tid]
            str_file = json.dumps(file_tech, sort_keys=True, ensure_ascii=False)
            str_master = json.dumps(master_tech, sort_keys=True, ensure_ascii=False)
            if str_file != str_master:
                mismatches.append(tid)
                
    print(f"Missing in master: {len(missing_in_master)}")
    print(f"Missing in files: {len(missing_in_files)}")
    print(f"Content mismatches: {len(mismatches)}")
    if mismatches:
        for tid in mismatches[:10]:
            print(f"  [-] Mismatch in {tid}")
    else:
        print("  [+] PASS: 100% exact 1:1 synchronization (0 mismatches)")
            
    return {
        "total_files": len(file_paths),
        "total_master": len(master_map),
        "missing_in_master": missing_in_master,
        "missing_in_files": missing_in_files,
        "mismatches": mismatches
    }

def run_oracle_4():
    print("\n" + "=" * 60)
    print("ORACLE 4: Garden, Pauwels, Judet-Letournel do NOT contain patellectomy or RIA")
    print("=" * 60)
    
    with open("data/fracture_classifications.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        
    classifs_list = data if isinstance(data, list) else data.get("classifications", [])
    
    patellectomy_techniques = ["54-20", "54-21", "54-22"]
    ria_techniques = ["53-1", "53-2", "53-3"]
    checked_systems = ["garden", "pauwels", "letournel_judet", "judet_letournel"]
    
    violations = []
    
    for c in classifs_list:
        sys_id = c.get("id")
        if sys_id not in checked_systems:
            continue
        sys_techs = c.get("techniques", [])
        print(f"Classification '{sys_id}': linked techniques = {sys_techs}")
        
        # Check top-level techniques
        for t in sys_techs:
            if t in patellectomy_techniques:
                violations.append((sys_id, "TOP_LEVEL", t, "PATELLECTOMY"))
            if t in ria_techniques:
                violations.append((sys_id, "TOP_LEVEL", t, "RIA"))
                
        # Check per-type techniques
        for idx, tp in enumerate(c.get("types", [])):
            type_techs = list(tp.get("techniques", []))
            if "technique_id" in tp and tp["technique_id"]:
                type_techs.append(tp["technique_id"])
            for t in type_techs:
                if t in patellectomy_techniques:
                    violations.append((sys_id, f"TYPE_{idx}", t, "PATELLECTOMY"))
                if t in ria_techniques:
                    violations.append((sys_id, f"TYPE_{idx}", t, "RIA"))
                    
    print(f"\nOracle 4 Result: {len(violations)} violations found.")
    if not violations:
        print("  [+] PASS: Garden, Pauwels, Judet-Letournel contain 0 patellectomy or RIA links.")
    for v in violations:
        print(f"  [-] VIOLATION: {v}")
        
    return violations

if __name__ == "__main__":
    o1 = run_oracle_1()
    o2 = run_oracle_2()
    o3 = run_oracle_3()
    o4 = run_oracle_4()
