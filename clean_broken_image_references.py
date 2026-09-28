import os
import json
import glob
import sys

sys.stdout.reconfigure(encoding='utf-8')

print("Auditing and cleaning non-existent image paths across all techniques...")

tech_files = glob.glob('data/techniques/*.json')
cleaned_count = 0
total_removed_refs = 0
total_valid_images = 0

for tf in tech_files:
    with open(tf, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    modified = False
    
    # Check image_url
    iurl = data.get('image_url')
    if iurl:
        if not os.path.exists(iurl):
            data['image_url'] = ""
            modified = True
            total_removed_refs += 1
        else:
            total_valid_images += 1
            
    # Check images list
    valid_images = []
    for img in data.get('images', []):
        u = img.get('url')
        if u and os.path.exists(u):
            valid_images.append(img)
            total_valid_images += 1
        else:
            total_removed_refs += 1
            modified = True
            
    if len(valid_images) != len(data.get('images', [])):
        data['images'] = valid_images
        modified = True
        
    if modified:
        cleaned_count += 1
        with open(tf, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Total technique JSONs checked: {len(tech_files)}")
print(f"Technique JSONs cleaned: {cleaned_count}")
print(f"Broken image references purged: {total_removed_refs}")
print(f"Total valid image references retained: {total_valid_images}")

# Also sync data/clinical_techniques.json
if os.path.exists('data/clinical_techniques.json'):
    with open('data/clinical_techniques.json', 'r', encoding='utf-8') as f:
        clin = json.load(f)
        
    clin_modified = 0
    for tid, cdata in clin.items():
        if isinstance(cdata, dict):
            iurl = cdata.get('image_url')
            if iurl and not os.path.exists(iurl):
                cdata['image_url'] = ""
                clin_modified += 1
            v_imgs = [img for img in cdata.get('images', []) if img.get('url') and os.path.exists(img['url'])]
            if len(v_imgs) != len(cdata.get('images', [])):
                cdata['images'] = v_imgs
                clin_modified += 1
                
    if clin_modified:
        with open('data/clinical_techniques.json', 'w', encoding='utf-8') as f:
            json.dump(clin, f, ensure_ascii=False, indent=2)
        print(f"Synchronized data/clinical_techniques.json (modified {clin_modified} entries)")
