import fitz
import re
import json
import os
import sys
import random

sys.stdout.reconfigure(encoding='utf-8')

doc = fitz.open(r'd:\cambell\campbell_13th_ed.pdf')
total_pages = len(doc)

with open(r'd:\cambell\data\techniques_catalog.json', 'r', encoding='utf-8') as f:
    existing_techs = json.load(f)

with open(r'd:\cambell\data\chapters_catalog.json', 'r', encoding='utf-8') as f:
    existing_chapters = json.load(f)

with open(r'd:\cambell\data\outline_tree.json', 'r', encoding='utf-8') as f:
    outline_tree = json.load(f)

# -------------------------------------------------------------
# AUDIT 1: CONTINUITY & MISSING NUMBERS IN CHAPTERS
# -------------------------------------------------------------
print("="*60)
print("AUDIT 1: TECHNIQUES CONTINUITY PER CHAPTER")
print("="*60)

by_chap = {}
for t in existing_techs:
    c = t['chapter']
    num = int(t['tech_id'].split('-')[1])
    by_chap.setdefault(c, []).append((num, t))

chap_continuity = []
for c in range(1, 90):
    items = sorted(by_chap.get(c, []), key=lambda x: x[0])
    count = len(items)
    if count == 0:
        continue
    nums = [x[0] for x in items]
    min_num = min(nums)
    max_num = max(nums)
    expected_set = set(range(1, max_num + 1))
    actual_set = set(nums)
    missing = sorted(list(expected_set - actual_set))
    duplicates = [n for n in nums if nums.count(n) > 1]
    duplicates = sorted(list(set(duplicates)))
    
    chap_continuity.append({
        'chapter': c,
        'count': count,
        'min_num': min_num,
        'max_num': max_num,
        'is_continuous': (len(missing) == 0 and min_num == 1),
        'missing': missing,
        'duplicates': duplicates
    })

discontinuous_chapters = [ch for ch in chap_continuity if not ch['is_continuous']]
print(f"Total active chapters with techniques: {len(chap_continuity)}")
print(f"Chapters with continuous numbering (1..N): {len(chap_continuity) - len(discontinuous_chapters)}")
print(f"Chapters with discontinuous numbering: {len(discontinuous_chapters)}")
for d in discontinuous_chapters:
    print(f"  Chapter {d['chapter']}: min={d['min_num']}, max={d['max_num']}, count={d['count']}, missing={d['missing']}, duplicates={d['duplicates']}")

# -------------------------------------------------------------
# AUDIT 1B: BODY VS MASTER LIST (END OF BOOK)
# -------------------------------------------------------------
print("\n" + "="*60)
print("AUDIT 1B: BODY HEADING REGEX VS MASTER LIST")
print("="*60)

# True TECHNIQUE header in body text: usually "TECHNIQUE X-Y" as a header line
# Let's search specifically for headings
# Campbell headings typically appear as:
# "TECHNIQUE 1-1" or "TECHNIQUE 1-1\n..."
heading_regex = re.compile(r'^\s*TECHNIQUE\s+(\d+)-(\d+)', re.IGNORECASE | re.MULTILINE)
body_headings = {} # (chap, num) -> list of (page, matched_text)

for p in range(len(doc)):
    if p >= 4867: # End of book List of Techniques
        break
    text = doc[p].get_text()
    for m in heading_regex.finditer(text):
        c_num = int(m.group(1))
        t_num = int(m.group(2))
        t_id = f"{c_num}-{t_num}"
        # Grab the line
        start = m.start()
        end = text.find('\n', m.end())
        if end == -1: end = m.end() + 50
        line = text[start:end].strip()
        body_headings.setdefault(t_id, []).append((p + 1, line))

print(f"Total distinct TECHNIQUE headers found in body (p. 1-4867): {len(body_headings)}")

# Check 10-9 and 11-34
print("\nChecking 10-9 and 11-34 in body:")
for check_id in ['10-9', '11-34']:
    print(f"  {check_id}: in body_headings? {check_id in body_headings}")
    if check_id in body_headings:
        print(f"    Occurrences: {body_headings[check_id]}")
    # Let's inspect where 10-9 was referenced (page 563)
    p563 = doc[562].get_text()
    for line in p563.split('\n'):
        if '10-9' in line:
            print(f"    Page 563 line: {line.strip()}")
    # Let's inspect page 602 for 11-34
    p602 = doc[601].get_text()
    for line in p602.split('\n'):
        if '11-34' in line:
            print(f"    Page 602 line: {line.strip()}")

# Check 52-14 and 79-47 in body_headings
print("\nChecking 52-14 and 79-47:")
print(f"  52-14 in body_headings? {52-14 in body_headings}")
print(f"  79-47 in body_headings? {'79-47' in body_headings}")
if '52-14' in body_headings:
    print(f"    52-14: {body_headings['52-14']}")
if '79-47' in body_headings:
    print(f"    79-47: {body_headings['79-47']}")

# Compare catalog vs body_headings
catalog_ids = set(t['tech_id'] for t in existing_techs)
body_ids = set(body_headings.keys())

only_in_catalog = catalog_ids - body_ids
only_in_body = body_ids - catalog_ids

print(f"\nTechniques in Catalog (End List) but no direct 'TECHNIQUE X-Y' heading in body: {len(only_in_catalog)}")
if only_in_catalog:
    print(f"  IDs: {sorted(list(only_in_catalog))[:20]}")

print(f"Techniques with 'TECHNIQUE X-Y' heading in body but NOT in Catalog: {len(only_in_body)}")
if only_in_body:
    print(f"  IDs: {sorted(list(only_in_body))}")

# -------------------------------------------------------------
# AUDIT 1C: ZERO TECHNIQUE CHAPTERS
# -------------------------------------------------------------
print("\n" + "="*60)
print("AUDIT 1C: ZERO TECHNIQUE CHAPTERS")
print("="*60)
zero_chaps = [c for c in existing_chapters if c['technique_count'] == 0]
for z in zero_chaps:
    print(f"Chapter {z['chapter']}: {z['title']}")
    # let's print page range and topic reason
    start_p = z['start_page']
    # find next chapter start page
    next_ch = next((c for c in existing_chapters if c['chapter'] == z['chapter'] + 1), None)
    end_p = next_ch['start_page'] if next_ch else "End"
    print(f"   Pages: {start_p} -> {end_p}")

# -------------------------------------------------------------
# AUDIT 2: SURGICAL APPROACHES (CHAPTER 1 & CHAPTER 37)
# -------------------------------------------------------------
print("\n" + "="*60)
print("AUDIT 2: SURGICAL APPROACHES AUDIT")
print("="*60)

# Chapter 1: How many techniques are in Chapter 1?
ch1_techs_catalog = [t for t in existing_techs if t['chapter'] == 1]
print(f"Chapter 1 Techniques in catalog: {len(ch1_techs_catalog)} (from 1-1 to 1-{len(ch1_techs_catalog)})")
print(f"First 3: {[t['name'] for t in ch1_techs_catalog[:3]]}")
print(f"Last 3: {[t['name'] for t in ch1_techs_catalog[-3:]]}")

# Chapter 37: Spinal Anatomy and Surgical Approaches
ch37_techs_catalog = [t for t in existing_techs if t['chapter'] == 37]
print(f"\nChapter 37 Techniques in catalog: {len(ch37_techs_catalog)}")
for t in ch37_techs_catalog:
    print(f"  - {t['tech_id']}: {t['name']} (PDF page {t['pdf_page']})")

# Let's inspect Chapter 37 outline structure to see what approaches are listed
def get_node(nodes, ch_num):
    for n in nodes:
        if n['title'].startswith(f"{ch_num} "):
            return n
    return None

ch37_outline = get_node(outline_tree, 37)
if ch37_outline:
    print("\nChapter 37 Outline Headings (Approaches):")
    for child in ch37_outline.get('children', []):
        print(f"  * {child['title']} (page {child['page']})")
        for sub in child.get('children', [])[:5]:
            print(f"      - {sub['title']} (page {sub['page']})")

# -------------------------------------------------------------
# AUDIT 3: CLASSIFICATIONS & CLINICAL SYSTEMS
# -------------------------------------------------------------
print("\n" + "="*60)
print("AUDIT 3: CLASSIFICATIONS & CLINICAL SYSTEMS AUDIT")
print("="*60)
key_classifications = {
    "Gustilo-Anderson": r"Gustilo(?:-Anderson)?\s+(?:classification|type|grade)",
    "AO/OTA Classification": r"AO(?:/OTA)?\s+classification",
    "Neer Classification": r"Neer\s+(?:classification|four-part|three-part|two-part)",
    "Schatzker Classification": r"Schatzker\s+(?:classification|type)",
    "Garden Classification": r"Garden\s+(?:classification|stage|type)",
    "Denis Classification (Spine)": r"Denis\s+(?:three-column|classification)",
    "Paprosky Classification (Acetabular/Femoral)": r"Paprosky\s+(?:classification|type)",
    "Vancouver Classification (Periprosthetic)": r"Vancouver\s+classification",
    "Tile Classification (Pelvis)": r"Tile\s+classification",
    "Young-Burgess (Pelvis)": r"Young(?:-|\s+and\s+)Burgess",
    "Salter-Harris (Physeal)": r"Salter-Harris\s+(?:classification|type)",
    "Pauwels Classification (Femoral neck)": r"Pauwels\s+(?:classification|angle|type)",
    "Pipkin Classification (Femoral head)": r"Pipkin\s+(?:classification|type)",
    "Rockwood Classification (AC joint)": r"Rockwood\s+(?:classification|type)",
    "Hawkins Classification (Talus)": r"Hawkins\s+(?:classification|type|group)",
    "Frykman / Fernandez (Distal radius)": r"(?:Frykman|Fernandez)\s+classification",
    "Letournel & Judet (Acetabulum)": r"(?:Letournel|Judet)\s+classification",
    "Anderson & D'Alonzo (Dens/Odontoid)": r"Anderson\s+(?:and|&)\s+D'?Alonzo",
    "Meyers-McKeever (Tibial spine)": r"Meyers(?:-|\s+and\s+)McKeever",
    "Tscherne Classification (Soft tissue)": r"Tscherne\s+classification"
}

classif_results = {}
for name, pattern in key_classifications.items():
    regex = re.compile(pattern, re.IGNORECASE)
    matches = []
    for p in range(len(doc)):
        text = doc[p].get_text()
        m = regex.search(text)
        if m:
            matches.append(p + 1)
    classif_results[name] = {
        'total_pages_matched': len(matches),
        'sample_pages': matches[:5]
    }
    print(f"{name}: found on {len(matches)} pages. Samples: {matches[:5]}")

# -------------------------------------------------------------
# AUDIT 4: VIDEO CONTENTS AUDIT
# -------------------------------------------------------------
print("\n" + "="*60)
print("AUDIT 4: VIDEO CONTENTS AUDIT")
print("="*60)

# Check front matter pages 1 to 30 for Video list
video_entries = []
video_regex = re.compile(r'Video\s+(\d+)[-–:]\s*([^\n\r]+)', re.IGNORECASE)
for p in range(0, 30):
    text = doc[p].get_text()
    if "Video Contents" in text or "List of Videos" in text or "VIDEO CONTENTS" in text or "Videos" in text:
        print(f"Found Video section on page {p + 1}")
        for line in text.split('\n'):
            line = line.strip()
            if re.match(r'^Video\s+\d+', line, re.IGNORECASE) or re.match(r'^\d+\s+Video', line, re.IGNORECASE):
                video_entries.append((p + 1, line))

print(f"Total video lines extracted in front matter: {len(video_entries)}")
for v in video_entries[:15]:
    print(f"  p.{v[0]}: {v[1]}")

# Also scan entire front matter p. 1-25 for full text of video contents
for p in range(0, 25):
    t = doc[p].get_text()
    if "VIDEO CONTENTS" in t.upper():
        print(f"\n--- Complete Text of Video Contents on page {p+1} ---")
        print(t[:2000])

# -------------------------------------------------------------
# AUDIT 5: PAGE ACCURACY AUDIT (SAMPLE 40)
# -------------------------------------------------------------
print("\n" + "="*60)
print("AUDIT 5: PAGE ACCURACY AUDIT (40 TECHNIQUES ACROSS 4 VOLUMES)")
print("="*60)

# Select 10 techniques per volume evenly
# Vol 1: Ch 1-28 (~p 1-1120)
# Vol 2: Ch 29-47 (~p 1121-2740)
# Vol 3: Ch 48-63 (~p 2741-3750)
# Vol 4: Ch 64-89 (~p 3751-4867)
vol_ranges = [
    (1, 1, 28, "Volume 1: General Principles, Arthroplasty, Infections, Tumors"),
    (2, 29, 47, "Volume 2: Pediatrics, Spine, Sports Medicine"),
    (3, 48, 63, "Volume 3: Trauma, Amputations, Nerve/Plexus"),
    (4, 64, 89, "Volume 4: Hand, Wrist, Foot & Ankle")
]

random.seed(12345) # fixed reproducible seed
audit_samples = []

for vol_num, ch_start, ch_end, vol_desc in vol_ranges:
    vol_techs = [t for t in existing_techs if ch_start <= t['chapter'] <= ch_end and t.get('pdf_page')]
    sampled = random.sample(vol_techs, 10)
    for t in sampled:
        t_id = t['tech_id']
        claimed_page = t['pdf_page']
        
        # Check claimed page, +1, -1, +2
        found_at = None
        exact = False
        
        # Check text in claimed_page
        text_exact = doc[claimed_page - 1].get_text() if 1 <= claimed_page <= total_pages else ""
        if re.search(rf'TECHNIQUE\s+{t_id}\b', text_exact, re.IGNORECASE):
            found_at = claimed_page
            exact = True
        else:
            for offset in [1, -1, 2, -2]:
                check_p = claimed_page + offset
                if 1 <= check_p <= total_pages:
                    text_off = doc[check_p - 1].get_text()
                    if re.search(rf'TECHNIQUE\s+{t_id}\b', text_off, re.IGNORECASE):
                        found_at = check_p
                        break
        
        audit_samples.append({
            'volume': vol_num,
            'chapter': t['chapter'],
            'tech_id': t_id,
            'name': t['name'],
            'claimed_page': claimed_page,
            'found_page': found_at,
            'exact_match': exact,
            'near_match': (found_at is not None),
            'offset': (found_at - claimed_page) if found_at else None
        })

exact_count = sum(1 for s in audit_samples if s['exact_match'])
near_count = sum(1 for s in audit_samples if s['near_match'])
total_sampled = len(audit_samples)

print(f"Sample size: {total_sampled}")
print(f"Exact page match: {exact_count}/{total_sampled} ({exact_count/total_sampled*100:.1f}%)")
print(f"Within +/- 2 pages: {near_count}/{total_sampled} ({near_count/total_sampled*100:.1f}%)")

print("\nSample Details Table:")
for s in audit_samples:
    status = "EXACT" if s['exact_match'] else (f"OFFSET {s['offset']:+d}" if s['near_match'] else "NOT FOUND")
    print(f"Vol {s['volume']} | Ch {s['chapter']:02d} | Tech {s['tech_id']:7s} | Claimed: {s['claimed_page']:4d} | Found: {str(s['found_page']):4s} | [{status}] | {s['name'][:40]}")

# Save full audit payload to json
full_audit_payload = {
    'summary': {
        'total_techniques_catalog': len(existing_techs),
        'total_chapters': len(existing_chapters),
        'discontinuous_chapters_count': len(discontinuous_chapters),
        'zero_technique_chapters_count': len(zero_chaps),
        'sample_page_accuracy_exact': exact_count / total_sampled,
        'sample_page_accuracy_near': near_count / total_sampled
    },
    'discontinuous_chapters': discontinuous_chapters,
    'zero_technique_chapters': zero_chaps,
    'only_in_catalog': sorted(list(only_in_catalog)),
    'only_in_body': sorted(list(only_in_body)),
    'classifications': classif_results,
    'video_entries': video_entries,
    'audit_samples': audit_samples
}

with open(r'd:\cambell\full_audit_report.json', 'w', encoding='utf-8') as f:
    json.dump(full_audit_payload, f, ensure_ascii=False, indent=2)

print("\nFull audit report saved to d:\\cambell\\full_audit_report.json")
