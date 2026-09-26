import fitz
import re
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

pdf_path = 'campbell_13th_ed.pdf'
print(f"Opening {pdf_path}...")
doc = fitz.open(pdf_path)
total_pages = len(doc)
print(f"Total pages: {total_pages}")

# 1. Build original page mapping
def get_page_order(root_xref):
    pages = []
    def traverse(xref):
        txt = doc.xref_object(xref)
        if '/Kids' not in txt:
            pages.append(xref)
            return
        kids_match = re.search(r'/Kids\s*\[(.*?)\]', txt, re.DOTALL)
        if kids_match:
            kids_str = kids_match.group(1)
            kid_xrefs = [int(x) for x in re.findall(r'(\d+)\s+0\s+R', kids_str)]
            for k in kid_xrefs:
                traverse(k)
        else:
            pages.append(xref)
    traverse(root_xref)
    return pages

print("Building page mapping...")
old_pages = get_page_order(11393)
old_page_to_pdf_page = {xref: idx + 1 for idx, xref in enumerate(old_pages)}
print(f"Mapped {len(old_page_to_pdf_page)} pages.")

# 2. Extract full outline hierarchy
print("Extracting full outline hierarchy...")
outlines = []

def traverse_outline(item_xref, parent_id=None, level=1):
    curr = item_xref
    while curr:
        title = doc.xref_get_key(curr, 'Title')[1]
        dest = doc.xref_get_key(curr, 'Dest')
        pdf_page = None
        if dest[0] != 'null':
            m = re.search(r'\[(\d+)\s+0\s+R', dest[1])
            if m:
                target_xref = int(m.group(1))
                pdf_page = old_page_to_pdf_page.get(target_xref, None)
        
        node = {
            'xref': curr,
            'title': title,
            'level': level,
            'page': pdf_page,
            'children': []
        }
        
        # Check first child
        first_child = doc.xref_get_key(curr, 'First')
        if first_child[0] == 'xref':
            child_xref = int(first_child[1].split()[0])
            node['children'] = traverse_outline(child_xref, curr, level + 1)
            
        outlines.append(node)
        
        nxt = doc.xref_get_key(curr, 'Next')
        if nxt[0] != 'xref':
            break
        curr = int(nxt[1].split()[0])
    return outlines

# Root outline xref is 85998
root_first = int(doc.xref_get_key(85997, 'First')[1].split()[0])

all_outline_nodes = []
def build_tree(curr, level=1):
    items = []
    while curr:
        title = doc.xref_get_key(curr, 'Title')[1]
        dest = doc.xref_get_key(curr, 'Dest')
        pdf_page = None
        if dest[0] != 'null':
            m = re.search(r'\[(\d+)\s+0\s+R', dest[1])
            if m:
                target_xref = int(m.group(1))
                pdf_page = old_page_to_pdf_page.get(target_xref, None)
                
        node = {
            'id': curr,
            'title': title,
            'level': level,
            'page': pdf_page,
            'children': []
        }
        
        first_child = doc.xref_get_key(curr, 'First')
        if first_child[0] == 'xref':
            child_xref = int(first_child[1].split()[0])
            node['children'] = build_tree(child_xref, level + 1)
            
        items.append(node)
        nxt = doc.xref_get_key(curr, 'Next')
        if nxt[0] != 'xref':
            break
        curr = int(nxt[1].split()[0])
    return items

full_tree = build_tree(root_first, level=1)
print(f"Top-level outline items: {len(full_tree)}")

# 3. Extract the comprehensive List of Techniques from pages 4868 to end
print("Extracting List of Techniques from back of book...")
tech_text = ""
for p in range(4868, total_pages):
    tech_text += doc[p].get_text() + "\n"

# Process techniques
raw_lines = [l.strip() for l in tech_text.split("\n") if l.strip()]
techniques = []
curr_vol = ""
curr_chap_name = ""

pattern = re.compile(r'^(\d+-\d+)\s+(.+?)(?:,\s*(\d+[a-z\d\.]*))?$')

for i, line in enumerate(raw_lines):
    if line.startswith("VOLUME "):
        curr_vol = line
        continue
    if any(line.startswith(x) for x in ["Campbell’s", "Campbell's", "List of Techniques"]):
        continue
        
    m = pattern.match(line)
    if m:
        num = m.group(1)
        name = m.group(2).strip()
        book_page = m.group(3)
        chap_num = int(num.split('-')[0])
        techniques.append({
            'tech_id': num,
            'chapter_num': chap_num,
            'name': name,
            'book_page': book_page,
            'volume': curr_vol,
            'section': curr_chap_name
        })
    elif len(line) < 70 and not line.endswith(','):
        curr_chap_name = line

print(f"Extracted {len(techniques)} techniques.")

os.makedirs('data', exist_ok=True)
with open('data/outline_tree.json', 'w', encoding='utf-8') as f:
    json.dump(full_tree, f, ensure_ascii=False, indent=2)

with open('data/techniques_raw.json', 'w', encoding='utf-8') as f:
    json.dump(techniques, f, ensure_ascii=False, indent=2)

print("Saved outline_tree.json and techniques_raw.json successfully!")
