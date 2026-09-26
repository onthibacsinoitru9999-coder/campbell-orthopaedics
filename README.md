# 🦴 Campbell's Operative Orthopaedics (13th Edition) - Interactive Clinical Navigator & Guidemap
*Kinh thánh Chấn thương Chỉnh hình - Hệ thống Tra cứu Phẫu thuật & Phân loại Gãy xương Lâm sàng*

[![Tests](https://img.shields.io/badge/E2E%20Tests-85%2F85%20PASSED%20(100%25)-success)](file:///tests/run_e2e_tests.py)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-blue.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-Academic%20%2F%20Clinical-green.svg)](#)

---

## 📖 Giới thiệu
Ứng dụng tra cứu lâm sàng và giảng dạy phẫu thuật Chấn thương Chỉnh hình toàn diện, được số hóa và chuẩn hóa từ bộ giáo trình kinh điển **Campbell's Operative Orthopaedics (13th Edition, 4 Volumes, 4.887 trang, 89 chương)**.

Hệ thống kết hợp **Sơ đồ Khung xương Giải phẫu Tương tác (Interactive Skeleton Guidemap)**, **1.671 Kỹ thuật mổ chuẩn hóa**, **Hệ thống Bảng phân loại gãy kinh điển**, cùng **Trình xem trước Trang sách gốc Độ nét cao (High-DPI In-situ Viewer)** và **Gợi ý Tìm kiếm Siêu tốc (Live Autocomplete)**.

---

## 🌟 Tính năng Nổi bật

### 1. 🦴 Sơ đồ Khung xương Giải phẫu Guidemap (Interactive Human Skeleton)
- Tích hợp mô hình vector khung xương người SVG tương tác thời gian thực.
- Hiệu ứng phát sáng chuyên sâu khi rê chuột hoặc nhấp chọn các cấu trúc xương: **Mâm chày (Tibia)**, **Cổ xương đùi (Femur)**, **Khung chậu & Ổ cối (Pelvis)**, **Đầu trên xương cánh tay (Humerus)**, **Cột sống (Spine)**, **Xương quay / Xương trụ (Radius/Ulna)**, **Khối xương cổ chân (Tarsals)**, **Khối xương cổ tay (Carpals)**...
- Tự động hiển thị các **Bảng phân loại gãy xương tương ứng**:
  - *Schatzker* (Mâm chày - Tibial Plateau)
  - *Garden & Pauwels* (Cổ xương đùi - Femoral Neck)
  - *Neer* (Đầu trên xương cánh tay - Proximal Humerus)
  - *Denis & AO Spine* (Cột sống - Spine)
  - *Young-Burgess & Judet-Letournel* (Khung chậu & Ổ cối - Pelvis & Acetabulum)
  - *Danis-Weber & Lauge-Hansen* (Cổ chân - Ankle)
  - *Hawkins* (Xương sên - Talus)
  - *Frykman & Fernandez* (Đầu dưới xương quay - Distal Radius)
  - *Mason* (Chỏm quay - Radial Head)
  - *Gustilo-Anderson* (Gãy hở - Open Fractures)
- **Nút liên kết trực tiếp**: Nhấp vào từng thể phân loại (Type) để mở ngay kỹ thuật phẫu thuật chỉ định trong Campbell (ví dụ: *Schatzker II* -> *Technique 54-24*).

### 2. 🔍 Tìm kiếm Toàn diện & Gợi ý Thông minh (Live Autocomplete)
- Công cụ tìm kiếm song ngữ Anh - Việt, tự động chuẩn hóa dấu (diacritic folding, xử lý triệt để ký tự `đ`/`Đ`).
- Tìm kiếm tức thì theo tên danh nhân/eponyms kinh điển (*Broström, Bankart, Smith-Petersen, Latarjet, Chevron, Papineau, Ilizarov, Salter, Pemberton...*).
- **Hộp gợi ý tự động (Live Dropdown)**: Phân tách rõ ràng giữa thẻ **🦴 PHÂN LOẠI** (mở khung xương) và thẻ **🔪 KỸ THUẬT MỔ** (mở trang tài liệu).
- Hỗ trợ phím tắt điều hướng `↑`, `↓`, `Enter` và `Esc`.

### 3. 🖼️ Trình Xem Trang Sách Gốc Độ Phân Giải Cao (High-DPI In-situ Viewer)
- Render trang PDF gốc độ nét cao (150 - 200 DPI) trực tiếp trong cửa sổ Modal (<500ms khi đã lưu đệm cache).
- Đọc rõ ràng từng sơ đồ giải phẫu, hình vẽ đường mổ A-B-C, hướng đặt nẹp vít và dụng cụ phẫu thuật.
- **Thanh công cụ Viewer chuyên nghiệp**:
  - `◀ Trang trước` / `Trang sau ▶`
  - `🔍 Phóng to (+)` / `🔍 Thu nhỏ (-)` / `Kích thước gốc (100%)`
  - Mở ảnh gốc 200 DPI chất lượng cao.
- **Phím tắt phẫu thuật viên**:
  - Phím mũi tên `←` / `→`: Chuyển trang tài liệu kế tiếp / trước đó.
  - Phím `+` / `-`: Phóng to / thu nhỏ bản vẽ giải phẫu.
  - Phím `0`: Đưa tỷ lệ xem về chuẩn 100%.
  - Phím `Escape`: Đóng nhanh cửa sổ kỹ thuật.

### 4. 📚 Dữ liệu Đã Chuẩn hóa & Đối soát 100% Không Bỏ Sót
- **1.671 Kỹ thuật mổ** (Techniques 1-1 đến 89-14) xuyên suốt 80/80 chương có kỹ thuật, chuỗi số thứ tự liên tục 1..N (0 kỹ thuật bị nhảy số, 0 thiếu sót).
- **89 Chương sách** được phân loại khoa học vào 14 chuyên khoa sâu.
- **6.885 Đề mục outline** ánh xạ chuẩn xác số trang PDF và trang sách gốc.

---

## ⚡ Hướng dẫn Cài đặt & Khởi chạy

### 1. Yêu cầu Hệ thống
- Python 3.9+
- Bộ nhớ trống tối thiểu 2 GB

### 2. Cài đặt Thư viện Phụ thuộc
```bash
git clone <repository_url>
cd cambell
pip install -r requirements.txt
```

### 3. Tải File Sách Giáo trình PDF (437 MB)
*Do GitHub giới hạn kích thước file tải lên tối đa 100 MB, file PDF gốc không lưu trực tiếp trên Git repo.*

Chạy lệnh tự động sau để tải file PDF gốc trực tiếp từ Google Drive vào thư mục dự án:
```bash
python download.py
```
*(Nếu đã có sẵn file `campbell_13th_ed.pdf`, tập lệnh sẽ tự động nhận diện và bỏ qua bước tải).*

### 4. Khởi chạy Ứng dụng Web
- **Cách 1**: Nhấp đúp vào file [`run_web.bat`](run_web.bat)
- **Cách 2**: Chạy từ dòng lệnh:
  ```bash
  python -m uvicorn server:app --host 0.0.0.0 --port 8000
  ```

Truy cập hệ thống trên trình duyệt:
- **Giao diện Web Workstation**: [http://localhost:8000](http://localhost:8000)
- **Swagger API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🧪 Kiểm thử Tự động E2E (Master Test Suite)

Dự án được bảo chứng bởi bộ kiểm thử tự động 4 tầng (Tiers 1 - 4) với 85 ca kiểm thử bao quát toàn diện:
```bash
python tests/run_e2e_tests.py
```
Hoặc kiểm thử trực tiếp trên máy chủ đang chạy:
```bash
python tests/run_e2e_tests.py --live-url http://localhost:8000
```

**Kết quả kiểm định:**
```text
===========================================================================
           CAMPBELL 13TH ED - E2E TEST EXECUTION REPORT
===========================================================================
--- Tier 1: Feature Coverage (31 tests) [PASS] ---
--- Tier 2: Boundary & Corner Cases (25 tests) [PASS] ---
--- Tier 3: Cross-Feature Combinations (7 tests) [PASS] ---
--- Tier 4: Clinical Workload Scenarios (22 tests) [PASS] ---
===========================================================================
GRAND TOTAL: 85 tests run in 3.15s
PASSED: 85 | FAILED: 0 | SKIPPED: 0
SUCCESS RATE: 100.0%
===========================================================================
```

---

## 📁 Cấu trúc Mã nguồn Dự án

```
cambell/
├── .gitignore                      # Cấu hình loại trừ file PDF lớn & cache
├── requirements.txt                # Danh sách thư viện Python
├── download.py                     # Kịch bản tải PDF tự động từ Google Drive
├── server.py                       # FastAPI REST API Backend
├── run_web.bat                     # File kích hoạt 1-click cho Windows
├── README.md                       # Tài liệu hướng dẫn sử dụng
│
├── data/                           # Cơ sở dữ liệu JSON đã chuẩn hóa
│   ├── anatomical_categories.json  # 14 Nhóm chuyên khoa giải phẫu
│   ├── chapters_catalog.json       # Danh mục 89 chương sách
│   ├── fracture_classifications.json # 12+ Bảng phân loại gãy xương & liên kết kỹ thuật
│   ├── outline_tree.json           # Cây mục lục 6.885 đề mục phẫu thuật
│   └── techniques_catalog.json     # 1.671 Kỹ thuật mổ chuẩn Campbell
│
├── web/
│   └── static/
│       ├── human_skeleton.svg      # Sơ đồ khung xương tương tác Vector
│       ├── index.html              # Giao diện lâm sàng Workstation
│       ├── styles.css              # Giao diện responsive y khoa
│       └── app.js                  # Xử lý Guidemap, Autocomplete & High-DPI Modal
│
└── tests/                          # Bộ kiểm thử E2E 4 Tiers
    ├── e2e_client.py               # Test client ASGI / Live HTTP
    ├── run_e2e_tests.py            # Master Test Runner
    ├── test_e2e_guidemap.py        # Kiểm thử Khung xương SVG
    ├── test_e2e_search.py          # Kiểm thử Tìm kiếm & Lọc
    ├── test_e2e_viewer.py          # Kiểm thử High-DPI Page Viewer & Toolbar
    ├── test_e2e_classifications.py # Kiểm thử Phân loại gãy
    ├── test_e2e_audit.py           # Kiểm định đối soát 1.671 kỹ thuật
    └── test_e2e_clinical_scenarios.py # Kịch bản phẫu thuật lâm sàng thực tế
```

---

## 👨‍⚕️ Tác giả & Đóng góp
- **Chịu trách nhiệm nội dung**: Ôn Thi Bác Sĩ Nội Trú (`onthibacsinoitru9999@gmail.com`)
- **Mục tiêu**: Nền tảng tra cứu phục vụ lâm sàng, học tập, ôn luyện bác sĩ nội trú và phẫu thuật viên Chấn thương Chỉnh hình.
