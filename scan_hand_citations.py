import pymupdf
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

hand_chapters = [19] + list(range(64, 80))

with open('data/techniques_catalog.json', 'r', encoding='utf-8') as f:
    catalog = json.load(f)

hand_techs = [t for t in catalog if t.get('chapter') in hand_chapters]
print(f"Total Hand & Wrist techniques in catalog: {len(hand_techs)}")

doc = pymupdf.open('campbell_13th_ed.pdf')

results = []

for item in hand_techs:
    tid = item.get('tech_id')
    ch = item.get('chapter')
    pdf_p = item.get('pdf_page', 0)
    name = item.get('name_en')
    
    # Read text around pdf_p (e.g. pdf_p - 1 to pdf_p + 3)
    p_start = max(0, pdf_p - 1)
    p_end = min(len(doc), pdf_p + 4)
    
    combined_text = ""
    for p in range(p_start, p_end):
        combined_text += f"\n--- Page {p} ---\n" + doc[p].get_text()
    
    # Find TECHNIQUE tid
    pattern = rf"TECHNIQUE\s+{re.escape(tid)}\b"
    m = re.search(pattern, combined_text, re.IGNORECASE)
    
    cited_figs = []
    if m:
        # Look ahead 1500 chars from the technique start
        snippet = combined_text[m.start():m.start() + 2500]
        # find (Figs. X-Y to X-Z) or (Fig. X-Y) or see Figs. X-Y
        found = re.findall(r"(?:(?:see\s+)?Figs?\.?|Figures?)\s*(\d+[-–]\d+(?:\s*(?:to|and|,)\s*\d+[-–]?\d*)*)", snippet, re.IGNORECASE)
        for fmatch in found:
            # extract individual figure numbers
            nums = re.findall(r"\b(\d+[-–]\d+)\b", fmatch)
            cited_figs.extend(nums)
    
    # Also search for 'SEE TECHNIQUE tid' anywhere in the chapter pages
    # or just nearby
    see_tech_pattern = rf"SEE\s+TECHNIQUE\s+{re.escape(tid)}\b"
    see_matches = re.finditer(see_tech_pattern, combined_text, re.IGNORECASE)
    for sm in see_matches:
        # look backwards 500 chars for FIGURE X-Y
        before_snippet = combined_text[max(0, sm.start() - 600):sm.start()]
        fnums = re.findall(r"FIGURE\s+(\d+[-–]\d+)", before_snippet, re.IGNORECASE)
        if fnums:
            cited_figs.extend(fnums)

    cited_figs = list(dict.fromkeys(cited_figs)) # unique preserving order
    results.append({
        'tech_id': tid,
        'chapter': ch,
        'pdf_page': pdf_p,
        'name': name,
        'cited_figs': cited_figs
    })

print(f"Techniques scanned: {len(results)}")
with_cited = [r for r in results if r['cited_figs']]
print(f"Techniques with explicit figure citations: {len(with_cited)} / {len(results)} ({len(with_cited)/len(results)*100:.1f}%)")

for r in results[:20]:
    print(f"Tech {r['tech_id']} (Ch {r['chapter']}): cited {r['cited_figs']}")
