import fitz
import re
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
doc = fitz.open('campbell_13th_ed.pdf')

with open('data/outline_tree.json', 'r', encoding='utf-8') as f:
    outline = json.load(f)

# Let's inspect Chapter 1 headings vs techniques
def find_node(nodes, prefix):
    for n in nodes:
        if n['title'].startswith(prefix):
            return n
    return None

ch1_node = find_node(outline, "1 ")
ch37_node = find_node(outline, "37 ")

def collect_all_headings(node, result=None):
    if result is None:
        result = []
    result.append((node['title'], node.get('page')))
    for c in node.get('children', []):
        collect_all_headings(c, result)
    return result

ch1_headings = collect_all_headings(ch1_node)
print(f"Total headings in Chapter 1 outline: {len(ch1_headings)}")

# Check how many have "TECHNIQUE" in title vs without
tech_in_heading = [h for h in ch1_headings if "TECHNIQUE" in h[0].upper()]
print(f"Headings in Chapter 1 outline with 'TECHNIQUE': {len(tech_in_heading)}")

# Let's check how many approaches exist in Chapter 1
approach_headings = [h for h in ch1_headings if "APPROACH" in h[0].upper()]
print(f"Headings in Chapter 1 outline with 'APPROACH': {len(approach_headings)}")

# Look at the list of techniques in Chapter 1: 120 techniques
# Are all 120 techniques in Chapter 1 mapped to headings?
# Let's check which approach headings in Chapter 1 do NOT have a corresponding TECHNIQUE 1-X
ch1_text = ""
for p in range(12, 146):
    ch1_text += doc[p].get_text() + "\n"

# Find all TECHNIQUE 1-X in Chapter 1 text
found_ch1_techs = sorted(list(set(int(m.group(1)) for m in re.finditer(r'TECHNIQUE\s+1-(\d+)', ch1_text))))
print(f"Unique TECHNIQUE 1-X found in Ch 1 text: {len(found_ch1_techs)} (min: {min(found_ch1_techs)}, max: {max(found_ch1_techs)})")

# Check if there are anatomical approaches described without TECHNIQUE number
# In Chapter 1, under SURGICAL APPROACHES:
# Notice sections: Toes, Calcaneus, Tarsus and ankle, Tibia, Fibula, Knee, Femur, Hip, Acetabulum and pelvis, Ilium, Symphysis pubis, Sacroiliac joint, Spine, Sternoclavicular joint, Acromioclavicular joint, Shoulder, Humerus, Elbow, Radius, Ulna, Wrist, Hand
# For example: "Spine" on page 107 of book (pdf page 107) -> In Chapter 1, is Spine just a cross-reference to Chapter 37?
p107_text = doc[106].get_text()
print("\n--- Content of 'Spine' section in Chapter 1 (page 107) ---")
for line in p107_text.split('\n'):
    if 'Spine' in line or 'surgical approaches to the spine' in line.lower():
        print("  ", line.strip())

# Check Chapter 37
ch37_headings = collect_all_headings(ch37_node)
print(f"\nTotal headings in Chapter 37 outline: {len(ch37_headings)}")
ch37_approach_headings = [h for h in ch37_headings if "APPROACH" in h[0].upper()]
print(f"Headings in Chapter 37 outline with 'APPROACH': {len(ch37_approach_headings)}")

ch37_text = ""
for p in range(1754, 1794):
    ch37_text += doc[p].get_text() + "\n"

found_ch37_techs = sorted(list(set(int(m.group(1)) for m in re.finditer(r'TECHNIQUE\s+37-(\d+)', ch37_text))))
print(f"Unique TECHNIQUE 37-X found in Ch 37 text: {len(found_ch37_techs)} (min: {min(found_ch37_techs)}, max: {max(found_ch37_techs)})")

# Check if any approach heading in Ch 37 is not numbered as a technique
# e.g., "Posterior Approach to the Sacrum AND Sacroiliac Joint" or "High Transthoracic Approach"
print("\nChecking all approach headings in Chapter 37 to see which have TECHNIQUE 37-X vs pure heading:")
for h_title, h_page in ch37_headings:
    if "APPROACH" in h_title.upper() or "SURGERY" in h_title.upper() or "MAXILLOTOMY" in h_title.upper():
        # check surrounding text on h_page
        text = doc[h_page - 1].get_text()
        m = re.search(r'TECHNIQUE\s+37-(\d+)', text)
        t_str = f"TECHNIQUE 37-{m.group(1)}" if m else "NO TECHNIQUE ON PAGE"
        print(f"  {h_title[:45]:45s} (p.{h_page:4d}) -> {t_str}")
