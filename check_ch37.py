import fitz
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
doc = fitz.open('campbell_13th_ed.pdf')

for p in range(1760, 1765):
    text = doc[p].get_text()
    print(f"=== PAGE {p+1} ===")
    for line in text.split('\n'):
        if any(w in line.upper() for w in ['TECHNIQUE', 'APPROACH', 'TRANSORAL', 'RETROPHARYNGEAL']):
            print("  ", line.strip())
