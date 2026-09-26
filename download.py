import os
import sys
import re
import urllib.parse
import requests

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TARGET_PDF = os.path.join(BASE_DIR, 'campbell_13th_ed.pdf')

if os.path.exists(TARGET_PDF) and os.path.getsize(TARGET_PDF) > 400 * 1024 * 1024:
    size_mb = os.path.getsize(TARGET_PDF) / (1024 * 1024)
    print(f"[*] File sách đã tồn tại sẵn: {TARGET_PDF} ({size_mb:.2f} MB). Không cần tải lại!")
    sys.exit(0)

file_id = '1O1yB4AHK5heNfXyokgoCF9a8rJmWh-hy'
url = f'https://drive.usercontent.google.com/download?id={file_id}&export=download&confirm=t'

print(f"[*] Bắt đầu tải giáo trình Campbell's Operative Orthopaedics (13th Ed)...")
print(f"[*] Link Google Drive: https://drive.google.com/file/d/{file_id}/view")

session = requests.Session()
response = session.get(url, stream=True)

if response.status_code != 200:
    print(f"[!] Lỗi kết nối Google Drive (Mã HTTP: {response.status_code})")
    sys.exit(1)

CHUNK_SIZE = 64 * 1024
total = 0
with open(TARGET_PDF, 'wb') as f:
    for chunk in response.iter_content(CHUNK_SIZE):
        if chunk:
            f.write(chunk)
            total += len(chunk)
            if total % (20 * 1024 * 1024) < CHUNK_SIZE:
                print(f"    -> Đã tải {total / (1024 * 1024):.1f} MB...", flush=True)

print(f"[✓] Tải thành công! Đã lưu tại: {TARGET_PDF} ({total / (1024 * 1024):.2f} MB)")

