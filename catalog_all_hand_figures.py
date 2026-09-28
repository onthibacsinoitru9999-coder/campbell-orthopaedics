import pymupdf
import json
import re
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

doc = pymupdf.open('campbell_13th_ed.pdf')

hand_chapters = [19] + list(range(64, 80))

print("Scanning all PDF pages for Hand & Wrist figure definitions...")

# First find page ranges of these chapters
# From techniques_catalog.json
with open('data/techniques_catalog.json', 'r', encoding='utf-8') as f:
    catalog = json.load(f)

chapter_pages = {}
for item in catalog:
    ch = item.get('chapter')
    if ch in hand_chapters:
        p = item.get('pdf_page', 0)
        if ch not in chapter_pages:
            chapter_pages[ch] = {'min': p, 'max': p}
        else:
            chapter_pages[ch]['min'] = min(chapter_pages[ch]['min'], p)
            chapter_pages[ch]['max'] = max(chapter_pages[ch]['max'], p)

# Expand ranges a bit
for ch, r in chapter_pages.items():
    r['min'] = max(0, r['min'] - 10)
    r['max'] = min(len(doc) - 1, r['max'] + 20)
    print(f"Chapter {ch}: pages {r['min']} to {r['max']}")

# Map figure_id -> list of occurrences with page, bbox, caption
figures_db = {}

for ch, r in chapter_pages.items():
    ch_fig_pattern = rf"\bFIGURE\s+({ch}-\d+)\b"
    for p in range(r['min'], r['max'] + 1):
        page = doc[p]
        text = page.get_text()
        matches = list(re.finditer(ch_fig_pattern, text))
        for m in matches:
            fig_id = m.group(1)
            # caption snippet
            start = m.start()
            caption_snippet = text[start:start + 400].replace('\n', ' ').strip()
            
            # search for rect on page
            rects = page.search_for(f"FIGURE {fig_id}")
            if not rects:
                rects = page.search_for(f"FIG. {fig_id}")
            
            if fig_id not in figures_db:
                figures_db[fig_id] = []
            figures_db[fig_id].append({
                'fig_id': fig_id,
                'chapter': ch,
                'pdf_page': p,
                'caption': caption_snippet,
                'caption_rect': [rects[0].x0, rects[0].y0, rects[0].x1, rects[0].y1] if rects else None
            })

print(f"\nTotal distinct Hand & Wrist figures indexed in PDF: {len(figures_db)}")
with open('data/hand_figures_index.json', 'w', encoding='utf-8') as f:
    json.dump(figures_db, f, ensure_ascii=False, indent=2)

print("Saved to data/hand_figures_index.json")
