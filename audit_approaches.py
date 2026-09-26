import fitz
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('data/techniques_catalog.json', 'r', encoding='utf-8') as f:
    techs = json.load(f)

with open('data/outline_tree.json', 'r', encoding='utf-8') as f:
    outline = json.load(f)

doc = fitz.open('campbell_13th_ed.pdf')

# Check Chapter 1 techniques
ch1_techs = [t for t in techs if t['chapter'] == 1]
print(f"Chapter 1 has {len(ch1_techs)} techniques.")
print("First 10 of Ch 1:")
for t in ch1_techs[:10]:
    print(f"  {t['tech_id']}: {t['name']} (p. {t['pdf_page']})")

print("\nTechniques 11 to 20:")
for t in ch1_techs[10:20]:
    print(f"  {t['tech_id']}: {t['name']} (p. {t['pdf_page']})")

# In Chapter 1, notice:
# 1-1 to 1-10: what are they?
# Let's inspect where Surgical Approaches begins in Chapter 1:
# On page 13, TOC says "SURGICAL APPROACHES 23" (book page 23, pdf page around 34)

# Check Chapter 37 (Spinal Anatomy and Surgical Approaches)
ch37_techs = [t for t in techs if t['chapter'] == 37]
print(f"\nChapter 37 has {len(ch37_techs)} techniques.")
for t in ch37_techs:
    print(f"  {t['tech_id']}: {t['name']} (p. {t['pdf_page']})")

# Now check outline tree for Chapter 1 and Chapter 37
def find_node(nodes, prefix):
    for n in nodes:
        if n['title'].startswith(prefix):
            return n
    return None

ch1_node = find_node(outline, "1 ")
ch37_node = find_node(outline, "37 ")

print("\n--- Outline analysis for Chapter 1 ---")
# Count children and subchildren
def dump_tree_summary(node, depth=0):
    indent = "  " * depth
    title = node['title']
    has_tech = "TECHNIQUE" in title.upper()
    print(f"{indent}- [{ 'TECH' if has_tech else 'HEAD' }] {title} (p. {node.get('page')})")
    for child in node.get('children', [])[:15]:
        dump_tree_summary(child, depth + 1)
    if len(node.get('children', [])) > 15:
        print(f"{indent}  ... ({len(node.get('children', [])) - 15} more children)")

if ch1_node:
    print("Chapter 1 root node summary:")
    dump_tree_summary(ch1_node, 0)

if ch37_node:
    print("\nChapter 37 root node summary:")
    dump_tree_summary(ch37_node, 0)
