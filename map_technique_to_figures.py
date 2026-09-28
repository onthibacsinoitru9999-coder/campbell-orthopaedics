import pymupdf
import json
import re
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('data/hand_figures_index.json', 'r', encoding='utf-8') as f:
    figures_db = json.load(f)

with open('data/techniques_catalog.json', 'r', encoding='utf-8') as f:
    catalog = json.load(f)

hand_chapters = [19] + list(range(64, 80))
hand_techs = [t for t in catalog if t.get('chapter') in hand_chapters]

doc = pymupdf.open('campbell_13th_ed.pdf')

mapping = {}
unmapped = []

for item in hand_techs:
    tid = item.get('tech_id')
    ch = item.get('chapter')
    pdf_p = item.get('pdf_page', 0)
    name = item.get('name_en') or ''
    name_vi = item.get('name_vi') or ''
    
    # 1. Search for explicit figure mentions in the technique text in PDF
    p_start = max(0, pdf_p - 1)
    p_end = min(len(doc), pdf_p + 5)
    
    combined_text = ""
    for p in range(p_start, p_end):
        combined_text += f"\n--- Page {p} ---\n" + doc[p].get_text()
        
    pattern = rf"TECHNIQUE\s+{re.escape(tid)}\b"
    m = re.search(pattern, combined_text, re.IGNORECASE)
    
    candidate_figs = []
    
    # Priority A: Check if any figure in figures_db explicitly says 'SEE TECHNIQUE {tid}'
    for fid, occurrences in figures_db.items():
        if fid.startswith(f"{ch}-"):
            for occ in occurrences:
                if re.search(rf"\bSEE\s+TECHNIQUE\s+{re.escape(tid)}\b", occ['caption'], re.IGNORECASE):
                    candidate_figs.append((fid, 'see_technique_caption', occ))
    
    # Priority B: Check citations right under the technique header
    if m:
        tech_snippet = combined_text[m.start():m.start() + 2500]
        # Look for (Figs. XX-YY) or see Figs. XX-YY
        cit_matches = re.findall(r"(?:(?:see\s+)?Figs?\.?|Figures?)\s*(\d+[-–]\d+(?:\s*(?:to|and|,)\s*\d+[-–]?\d*)*)", tech_snippet[:1200], re.IGNORECASE)
        for cmatch in cit_matches:
            nums = re.findall(r"\b(\d+[-–]\d+)\b", cmatch)
            for num in nums:
                num = num.replace('–', '-')
                if num in figures_db:
                    candidate_figs.append((num, 'explicit_text_citation', figures_db[num][0]))
                    
        # Also check within full technique text (up to next TECHNIQUE)
        next_tech = re.search(r"TECHNIQUE\s+\d+[-–]\d+", tech_snippet[100:])
        end_idx = 100 + next_tech.start() if next_tech else len(tech_snippet)
        inner_snippet = tech_snippet[:end_idx]
        inner_matches = re.findall(r"(?:Figs?\.?|Figures?)\s*(\d+[-–]\d+)", inner_snippet, re.IGNORECASE)
        for num in inner_matches:
            num = num.replace('–', '-')
            if num in figures_db:
                candidate_figs.append((num, 'inner_text_citation', figures_db[num][0]))

    # Priority C: Keyword matching between technique name and figures in the same chapter
    if not candidate_figs:
        words = [w.lower() for w in re.findall(r"\b[a-zA-Z]{4,}\b", name)]
        stopwords = {'technique', 'closed', 'open', 'reduction', 'fixation', 'repair', 'transfer', 'reconstruction'}
        keywords = [w for w in words if w not in stopwords]
        if keywords:
            for fid, occurrences in figures_db.items():
                if fid.startswith(f"{ch}-"):
                    for occ in occurrences:
                        cap_lower = occ['caption'].lower()
                        match_count = sum(1 for kw in keywords if kw in cap_lower)
                        if match_count >= 1:
                            candidate_figs.append((fid, f'keyword_match_{match_count}', occ))

    # Priority D: Figure located within 1 page of technique start
    if not candidate_figs:
        for fid, occurrences in figures_db.items():
            if fid.startswith(f"{ch}-"):
                for occ in occurrences:
                    if abs(occ['pdf_page'] - pdf_p) <= 1:
                        candidate_figs.append((fid, 'proximity', occ))

    # Deduplicate candidate_figs
    unique_candidates = []
    seen = set()
    for fid, reason, occ in candidate_figs:
        if fid not in seen:
            seen.add(fid)
            unique_candidates.append({
                'figure_id': fid,
                'reason': reason,
                'pdf_page': occ['pdf_page'],
                'caption': occ['caption'],
                'caption_rect': occ.get('caption_rect')
            })

    if unique_candidates:
        mapping[tid] = {
            'tech_id': tid,
            'chapter': ch,
            'name': name,
            'figures': unique_candidates
        }
    else:
        unmapped.append(tid)

print(f"\nTotal Hand & Wrist techniques: {len(hand_techs)}")
print(f"Mapped to authentic figures: {len(mapping)} ({len(mapping)/len(hand_techs)*100:.1f}%)")
print(f"Unmapped: {len(unmapped)}")

with open('data/hand_techniques_figure_mapping.json', 'w', encoding='utf-8') as f:
    json.dump(mapping, f, ensure_ascii=False, indent=2)

print("\nSample Mapped Techniques:")
for tid in ['19-1', '19-15', '66-1', '67-1', '67-2', '67-3', '67-4', '67-5']:
    if tid in mapping:
        figs = [f['figure_id'] + f" ({f['reason']})" for f in mapping[tid]['figures']]
        print(f"Tech {tid}: {figs}")
