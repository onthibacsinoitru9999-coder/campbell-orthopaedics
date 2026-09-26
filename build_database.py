import fitz
import re
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

print("Loading document...")
doc = fitz.open('campbell_13th_ed.pdf')
total_pages = len(doc)

# Load outline tree and techniques_raw
with open('data/outline_tree.json', 'r', encoding='utf-8') as f:
    outline_tree = json.load(f)

# Anatomical categories mapping for the 89 chapters
ANATOMICAL_CATEGORIES = {
    "Approaches & General Principles": {
        "vi": "Tiếp cận ngoại khoa & Kỹ thuật đại cương",
        "icon": "📐",
        "chapters": [1, 2, 80]
    },
    "Hip & Pelvis": {
        "vi": "Khớp háng & Khung chậu",
        "icon": "🩻",
        "chapters": [3, 4, 5, 6, 30, 55, 56]
    },
    "Knee & Lower Leg": {
        "vi": "Khớp gối & Cẳng chân",
        "icon": "🦵",
        "chapters": [7, 8, 9, 45, 51, 54]
    },
    "Foot & Ankle": {
        "vi": "Bàn chân & Cổ chân",
        "icon": "🦶",
        "chapters": [10, 11, 15, 50, 81, 82, 83, 84, 85, 86, 87, 88, 89]
    },
    "Shoulder & Arm": {
        "vi": "Khớp vai & Cánh tay",
        "icon": "💪",
        "chapters": [12, 13, 46, 47, 52, 57]
    },
    "Elbow & Forearm": {
        "vi": "Khớp khuỷu & Cẳng tay",
        "icon": "🦾",
        "chapters": [12, 13, 46, 52, 57, 74]
    },
    "Hand & Wrist": {
        "vi": "Bàn tay & Cổ tay",
        "icon": "✋",
        "chapters": [19, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 75, 76, 77, 78, 79]
    },
    "Spine": {
        "vi": "Cột sống",
        "icon": "🦴",
        "chapters": [37, 38, 39, 40, 41, 42, 43, 44]
    },
    "Pediatric Orthopaedics": {
        "vi": "Chấn thương Chỉnh hình Nhi",
        "icon": "👶",
        "chapters": [29, 30, 31, 32, 33, 34, 35, 36, 43]
    },
    "Trauma & Fracture Reconstruction": {
        "vi": "Chấn thương, Gãy xương & Khớp giả",
        "icon": "🩹",
        "chapters": [48, 53, 54, 55, 56, 57, 58, 59, 60, 61]
    },
    "Peripheral Nerves & Microsurgery": {
        "vi": "Thần kinh ngoại biên & Vi phẫu",
        "icon": "⚡",
        "chapters": [62, 63, 68, 71]
    },
    "Amputations": {
        "vi": "Phẫu thuật Cắt cụt",
        "icon": "✂️",
        "chapters": [14, 15, 16, 17, 18, 19]
    },
    "Infections & Tumors": {
        "vi": "Nhiễm trùng & U xương phần mềm",
        "icon": "🔬",
        "chapters": [20, 21, 22, 23, 24, 25, 26, 27, 28]
    },
    "Arthroscopy & Sports": {
        "vi": "Nội soi khớp & Y học thể thao",
        "icon": "🏅",
        "chapters": [45, 46, 47, 49, 50, 51, 52, 89]
    }
}

# 1. Map each chapter to start page and title
chapter_map = {}
for node in outline_tree:
    title = node['title']
    m = re.match(r'^(\d+)\s+(.+)', title)
    if m:
        c_num = int(m.group(1))
        c_name = m.group(2)
        chapter_map[c_num] = {
            'chapter': c_num,
            'title': c_name,
            'full_title': title,
            'start_page': node.get('page'),
            'id': node['id']
        }

print(f"Total mapped chapters: {len(chapter_map)}")

# 2. Extract multi-line techniques properly from pages 4868 to end
print("Parsing techniques table accurately...")
full_tech_lines = []
for p in range(4868, total_pages):
    for line in doc[p].get_text().split("\n"):
        line = line.strip()
        if line:
            full_tech_lines.append(line)

# Let's stitch split lines where a technique name wrapped onto 2 or 3 lines
cleaned_entries = []
i = 0
while i < len(full_tech_lines):
    line = full_tech_lines[i]
    if line.startswith("VOLUME ") or any(line.startswith(x) for x in ["Campbell", "List of Techniques"]):
        i += 1
        continue
    
    # Check if starts with \d+-\d+
    m = re.match(r'^(\d+-\d+)\s+(.*)', line)
    if m:
        tech_id = m.group(1)
        rest = m.group(2)
        # Check if next lines are continuation (do not start with \d+-\d+ and not section title)
        j = i + 1
        while j < len(full_tech_lines):
            next_l = full_tech_lines[j]
            if re.match(r'^\d+-\d+', next_l) or next_l.startswith("VOLUME ") or any(next_l.startswith(x) for x in ["Campbell", "List of Techniques"]):
                break
            # If line ends with page number or starts with continuation
            # A section heading typically doesn't contain commas or parenthesis or ends with a page number
            if any(c in next_l for c in [',', '(', ')', 'et al', 'and']) or re.search(r'\d+$', next_l):
                rest += " " + next_l
                j += 1
            else:
                # Could be a section header
                break
        
        # Parse rest into name and page
        page_match = re.search(r',\s*(\d+[a-z\d\.\-]*)$', rest)
        book_page = None
        if page_match:
            book_page = page_match.group(1)
            name = rest[:page_match.start()].strip()
        else:
            name = rest.strip()
            
        cleaned_entries.append({
            'tech_id': tech_id,
            'chapter': int(tech_id.split('-')[0]),
            'name': name,
            'book_page': book_page
        })
        i = j
    else:
        i += 1

print(f"Cleaned techniques count from master list: {len(cleaned_entries)}")

# 3. Scan the entire PDF for exact occurrence of each TECHNIQUE to get accurate PDF page
print("Scanning PDF for exact TECHNIQUE headings across all 4887 pages...")
tech_regex = re.compile(r'TECHNIQUE\s+(\d+-\d+)\s*(.*?)(?:\n|$)', re.IGNORECASE)
found_pages = {}
for p in range(12, 4868):
    text = doc[p].get_text()
    for m in tech_regex.finditer(text):
        t_id = m.group(1)
        if t_id not in found_pages:
            found_pages[t_id] = p + 1

print(f"Found {len(found_pages)} techniques located directly in book text.")

# Merge and enrich techniques
final_techniques = []
for entry in cleaned_entries:
    t_id = entry['tech_id']
    c_num = entry['chapter']
    chap_info = chapter_map.get(c_num, {})
    
    pdf_p = found_pages.get(t_id)
    if not pdf_p and chap_info.get('start_page'):
        # Fallback to chapter start page
        pdf_p = chap_info.get('start_page')
        
    # Determine categories
    categories = []
    for cat_name, cat_data in ANATOMICAL_CATEGORIES.items():
        if c_num in cat_data['chapters']:
            categories.append({
                'id': cat_name,
                'vi': cat_data['vi'],
                'icon': cat_data['icon']
            })
            
    # Extract eponym/author from technique name if in parentheses
    author_match = re.search(r'\(([^)]+)\)', entry['name'])
    author = author_match.group(1) if author_match else ""
    
    final_techniques.append({
        'tech_id': t_id,
        'chapter': c_num,
        'chapter_title': chap_info.get('title', f'Chapter {c_num}'),
        'name': entry['name'],
        'author': author,
        'book_page': entry['book_page'],
        'pdf_page': pdf_p,
        'categories': categories
    })

# Save enriched techniques catalog
with open('data/techniques_catalog.json', 'w', encoding='utf-8') as f:
    json.dump(final_techniques, f, ensure_ascii=False, indent=2)

# Save chapters catalog
chapters_list = []
for c_num, c_info in sorted(chapter_map.items()):
    cats = []
    for cat_name, cat_data in ANATOMICAL_CATEGORIES.items():
        if c_num in cat_data['chapters']:
            cats.append({
                'id': cat_name,
                'vi': cat_data['vi'],
                'icon': cat_data['icon']
            })
    # count techniques in chapter
    t_count = sum(1 for t in final_techniques if t['chapter'] == c_num)
    chapters_list.append({
        'chapter': c_num,
        'title': c_info['title'],
        'start_page': c_info.get('start_page'),
        'technique_count': t_count,
        'categories': cats
    })

with open('data/chapters_catalog.json', 'w', encoding='utf-8') as f:
    json.dump(chapters_list, f, ensure_ascii=False, indent=2)

with open('data/anatomical_categories.json', 'w', encoding='utf-8') as f:
    json.dump(ANATOMICAL_CATEGORIES, f, ensure_ascii=False, indent=2)

print("Saved data/techniques_catalog.json, data/chapters_catalog.json, data/anatomical_categories.json!")
print(f"Sample technique: {final_techniques[0]}")
