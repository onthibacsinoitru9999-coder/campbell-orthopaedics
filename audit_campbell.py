import fitz
import re
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

pdf_path = r'd:\cambell\campbell_13th_ed.pdf'
print(f"Opening PDF: {pdf_path}...")
doc = fitz.open(pdf_path)
total_pages = len(doc)
print(f"Total pages: {total_pages}")

# Load existing data
with open(r'd:\cambell\data\techniques_catalog.json', 'r', encoding='utf-8') as f:
    existing_techs = json.load(f)

with open(r'd:\cambell\data\chapters_catalog.json', 'r', encoding='utf-8') as f:
    existing_chapters = json.load(f)

with open(r'd:\cambell\data\outline_tree.json', 'r', encoding='utf-8') as f:
    outline_tree = json.load(f)

print(f"Existing catalog techniques count: {len(existing_techs)}")
print(f"Existing catalog chapters count: {len(existing_chapters)}")

# Audit 1: Check continuity in existing catalog techniques
existing_by_chapter = {}
for t in existing_techs:
    c = t['chapter']
    t_id = t['tech_id']
    num = int(t_id.split('-')[1])
    existing_by_chapter.setdefault(c, []).append((num, t_id, t['name'], t['pdf_page']))

continuity_issues = {}
for c in range(1, 90):
    techs = existing_by_chapter.get(c, [])
    nums = sorted([x[0] for x in techs])
    if not nums:
        continue
    expected = list(range(1, max(nums) + 1))
    missing = set(expected) - set(nums)
    if missing:
        continuity_issues[c] = {
            'max': max(nums),
            'count': len(nums),
            'missing': sorted(list(missing))
        }

print("\n--- CONTINUITY ISSUES IN EXISTING CATALOG ---")
for c, issue in continuity_issues.items():
    print(f"Chapter {c}: max={issue['max']}, count={issue['count']}, missing={issue['missing']}")

# Audit 1b: Scan entire PDF for all TECHNIQUE occurrences
print("\n--- SCANNING ENTIRE PDF BODY FOR TECHNIQUES ---")
body_tech_regex = re.compile(r'(?:TECHNIQUE|Technique)\s+(\d+)-(\d+)(?:\s+([^\n\r]+))?')
body_occurrences = {} # tech_id -> list of (page, line_text)

# Let's scan pages 1 to 4867 (body text before List of Techniques)
for p in range(len(doc)):
    text = doc[p].get_text()
    for m in body_tech_regex.finditer(text):
        t_id = f"{m.group(1)}-{m.group(2)}"
        title_snippet = m.group(3) if m.group(3) else ""
        body_occurrences.setdefault(t_id, []).append((p + 1, title_snippet.strip()))

print(f"Total unique technique IDs found in PDF via regex: {len(body_occurrences)}")

# Filter body occurrences before page 4868 (List of Techniques starts around 4868)
body_in_text = {k: v for k, v in body_occurrences.items() if any(p < 4868 for p, _ in v)}
print(f"Techniques appearing in main text (page < 4868): {len(body_in_text)}")

catalog_tech_ids = set(t['tech_id'] for t in existing_techs)
body_tech_ids = set(body_in_text.keys())

in_body_not_in_catalog = body_tech_ids - catalog_tech_ids
in_catalog_not_in_body = catalog_tech_ids - body_tech_ids

print(f"Techniques in body text but NOT in catalog (List of Techniques): {len(in_body_not_in_catalog)}")
if in_body_not_in_catalog:
    print(f"Examples: {sorted(list(in_body_not_in_catalog))[:20]}")

print(f"Techniques in catalog but NOT found in body text regex: {len(in_catalog_not_in_body)}")
if in_catalog_not_in_body:
    print(f"Examples: {sorted(list(in_catalog_not_in_body))[:20]}")

# Zero technique chapters
zero_chapters = []
for c_info in existing_chapters:
    c = c_info['chapter']
    if c_info['technique_count'] == 0:
        zero_chapters.append(c_info)

print(f"\nChapters with 0 techniques ({len(zero_chapters)}):")
for z in zero_chapters:
    print(f"Chapter {z['chapter']}: {z['title']} (start page {z['start_page']})")

# Save results for further analysis
results = {
    'continuity_issues': continuity_issues,
    'in_body_not_in_catalog': sorted(list(in_body_not_in_catalog)),
    'in_catalog_not_in_body': sorted(list(in_catalog_not_in_body)),
    'zero_chapters': zero_chapters
}

with open(r'd:\cambell\audit_part1.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
