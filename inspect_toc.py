import fitz  # PyMuPDF
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Find the pdf file in d:\cambell
pdf_files = [f for f in os.listdir('.') if f.endswith('.pdf')]
if not pdf_files:
    print("No PDF found")
    sys.exit(1)

pdf_path = pdf_files[0]
print(f"Reading: {pdf_path}")

doc = fitz.open(pdf_path)
page_count = len(doc)
print(f"Total pages: {page_count}")

toc = doc.get_toc()  # [[lvl, title, page, ...], ...]
print(f"Total TOC items: {len(toc)}")

# Save TOC sample and structure
with open("toc_raw.json", "w", encoding="utf-8") as f:
    json.dump(toc, f, ensure_ascii=False, indent=2)

print("\nFirst 40 TOC entries:")
for item in toc[:40]:
    lvl, title, page = item[0], item[1], item[2]
    indent = "  " * (lvl - 1)
    print(f"{indent}[L{lvl}] {title} (p. {page})")

print("\n--- Summary of top levels (Level 1 and 2) ---")
for item in toc:
    lvl, title, page = item[0], item[1], item[2]
    if lvl <= 2:
        indent = "  " * (lvl - 1)
        print(f"{indent}[L{lvl}] {title} (p. {page})")

doc.close()
