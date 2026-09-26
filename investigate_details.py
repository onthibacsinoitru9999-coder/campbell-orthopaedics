import fitz
import re
import json
import random

doc = fitz.open(r'd:\cambell\campbell_13th_ed.pdf')

# 1. Investigate 10-9, 11-34, 52-14, 79-47
print("=== INVESTIGATING 10-9, 11-34, 52-14, 79-47 ===")

# Search 10-9 in body and in end pages (4868-4887)
for t_id in ['10-9', '11-34', '52-14', '79-47']:
    print(f"\n--- Checking {t_id} ---")
    body_matches = []
    end_matches = []
    for p in range(len(doc)):
        text = doc[p].get_text()
        if re.search(rf'TECHNIQUE\s+{t_id}\b', text, re.IGNORECASE) or re.search(rf'\b{t_id}\b', text):
            # check if it looks like the technique heading or mention
            for line in text.split('\n'):
                if t_id in line:
                    if p < 4868:
                        body_matches.append((p + 1, line.strip()))
                    else:
                        end_matches.append((p + 1, line.strip()))
    print(f"Body matches for {t_id}: {body_matches[:5]}")
    print(f"End list matches for {t_id}: {end_matches[:5]}")

# 2. Check Surgical Approaches in Chapter 1 and Chapter 37
print("\n=== SURGICAL APPROACHES IN CHAPTER 1 & 37 ===")
# Chapter 1 starts around page 13, Chapter 2 starts at page 147
# Let's see how Chapter 1 outlines approaches
ch1_techs = []
for p in range(12, 147):
    text = doc[p].get_text()
    for m in re.finditer(r'(?:TECHNIQUE\s+)?(1-\d+)\s+([^\n\r]+)', text):
        ch1_techs.append((p + 1, m.group(0).strip()))

print(f"Total technique occurrences in Chapter 1: {len(ch1_techs)}")
print(f"Sample Ch 1 techniques: {ch1_techs[:5]}")
print(f"Last Ch 1 techniques: {ch1_techs[-5:]}")

# Check Chapter 37 (Spine approaches)
# Let's find Chapter 37 pages
with open(r'd:\cambell\data\chapters_catalog.json', 'r', encoding='utf-8') as f:
    chapters = json.load(f)

ch37 = next(c for c in chapters if c['chapter'] == 37)
ch38 = next(c for c in chapters if c['chapter'] == 38)
print(f"Chapter 37: {ch37['title']}, start {ch37['start_page']}, end before {ch38['start_page']}")
ch37_techs = []
for p in range(ch37['start_page'] - 1, ch38['start_page'] - 1):
    text = doc[p].get_text()
    for m in re.finditer(r'(?:TECHNIQUE\s+)?(37-\d+)\s+([^\n\r]+)', text):
        ch37_techs.append((p + 1, m.group(0).strip()))
print(f"Techniques in Ch 37: {ch37_techs}")

# Let's check non-technique headings in Chapter 37
# Look at outline tree for chapter 37
with open(r'd:\cambell\data\outline_tree.json', 'r', encoding='utf-8') as f:
    outline = json.load(f)

def find_chapter_node(nodes, ch_num):
    for node in nodes:
        if node['title'].startswith(f"{ch_num} "):
            return node
    return None

ch37_node = find_chapter_node(outline, 37)
if ch37_node:
    print(f"Ch 37 outline children count: {len(ch37_node.get('children', []))}")
    for child in ch37_node.get('children', [])[:10]:
        print(f"  - {child['title']} (page {child['page']})")

# 3. Check Video Contents in front matter
print("\n=== VIDEO CONTENTS AUDIT ===")
video_pages = []
for p in range(0, 50):
    text = doc[p].get_text()
    if "video" in text.lower() and ("contents" in text.lower() or "video 1" in text.lower() or "video " in text.lower()):
        video_pages.append(p + 1)

print(f"Potential video list pages in front matter: {video_pages}")
for p in video_pages:
    print(f"\n--- Page {p} snippet ---")
    lines = [l.strip() for l in doc[p - 1].get_text().split('\n') if l.strip()]
    for l in lines[:25]:
        print(f"  {l}")

# 4. Check Classic Classifications
print("\n=== CLASSIFICATIONS AUDIT ===")
classifications = [
    "Gustilo", "Schatzker", "Garden", "Neer", "AO/OTA", "Denis",
    "Paprosky", "Vancouver", "Tscherne", "Pauwels", "Pipkin",
    "Salter-Harris", "Tile", "Young-Burgess", "Rockwood", "Meyers-McKeever",
    "Hawkins", "Frykman", "Fernandez", "Letournel", "Judet", "Anderson-D'Alonzo"
]

classification_findings = {}
for c_name in classifications:
    count = 0
    sample_pages = []
    for p in range(len(doc)):
        text = doc[p].get_text()
        if re.search(rf'\b{c_name}\b', text, re.IGNORECASE):
            count += 1
            if len(sample_pages) < 3:
                sample_pages.append(p + 1)
    classification_findings[c_name] = {'count': count, 'sample_pages': sample_pages}
    print(f"Classification '{c_name}': mentioned on {count} pages, samples: {sample_pages}")

# 5. Page Accuracy Audit (Random 40 techniques across 4 volumes)
print("\n=== PAGE ACCURACY AUDIT (SAMPLE 40) ===")
with open(r'd:\cambell\data\techniques_catalog.json', 'r', encoding='utf-8') as f:
    tech_catalog = json.load(f)

# Group by volume based on pages:
# Vol 1: ~1-1200, Vol 2: ~1201-2400, Vol 3: ~2401-3600, Vol 4: ~3601-4867
vols = {1: [], 2: [], 3: [], 4: []}
for t in tech_catalog:
    p = t.get('pdf_page')
    if not p:
        continue
    if p < 1300:
        vols[1].append(t)
    elif p < 2500:
        vols[2].append(t)
    elif p < 3700:
        vols[3].append(t)
    else:
        vols[4].append(t)

random.seed(42)
sampled_techs = []
for v in [1, 2, 3, 4]:
    sampled_techs.extend(random.sample(vols[v], 10))

print(f"Sampled {len(sampled_techs)} techniques.")
verified_count = 0
results_sample = []

for t in sampled_techs:
    t_id = t['tech_id']
    pdf_p = t['pdf_page'] # 1-based
    # check page pdf_p, pdf_p - 1, pdf_p + 1
    found_on = None
    for check_p in [pdf_p, pdf_p + 1, pdf_p - 1]:
        if 1 <= check_p <= total_pages:
            text = doc[check_p - 1].get_text()
            if re.search(rf'TECHNIQUE\s+{t_id}\b', text, re.IGNORECASE):
                found_on = check_p
                break
    
    exact_match = (found_on == pdf_p)
    near_match = (found_on is not None)
    if near_match:
        verified_count += 1
    results_sample.append({
        'tech_id': t_id,
        'name': t['name'],
        'catalog_pdf_page': pdf_p,
        'found_on': found_on,
        'exact': exact_match,
        'near': near_match
    })

print(f"Verified {verified_count}/{len(sampled_techs)} ({verified_count/len(sampled_techs)*100:.1f}%) within +/- 1 page.")
exact_count = sum(1 for r in results_sample if r['exact'])
print(f"Exact page match: {exact_count}/{len(sampled_techs)} ({exact_count/len(sampled_techs)*100:.1f}%)")

# Save all details to json
with open(r'd:\cambell\audit_part2.json', 'w', encoding='utf-8') as f:
    json.dump({
        'classification_findings': classification_findings,
        'sample_verification': results_sample,
        'exact_rate': exact_count / len(sampled_techs),
        'near_rate': verified_count / len(sampled_techs)
    }, f, ensure_ascii=False, indent=2)
