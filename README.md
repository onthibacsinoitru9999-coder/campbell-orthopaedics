# 🦴 Campbell's Operative Orthopaedics (13th Edition) - Interactive Clinical Navigator & Guidemap
*Kinh thánh Chấn thương Chỉnh hình - Hệ thống Tra cứu Phẫu thuật & Phân loại Gãy xương Lâm sàng*

[![Tests](https://img.shields.io/badge/Playwright%20Mobile-17%2F17%20PASSED%20(100%25)-success)](file:///tests/test_playwright_mobile.py)
[![Hosting](https://img.shields.io/badge/Hosting-GitHub%20Pages%20(Pure%20Static)-blue.svg)](https://onthibacsinoitru9999-coder.github.io/campbell-orthopaedics/)
[![License](https://img.shields.io/badge/License-Academic%20%2F%20Clinical-green.svg)](#)

---

## 📖 Giới thiệu
Ứng dụng tra cứu lâm sàng và giảng dạy phẫu thuật Chấn thương Chỉnh hình toàn diện, được số hóa và chuẩn hóa từ bộ giáo trình kinh điển **Campbell's Operative Orthopaedics (13th Edition, 4 Volumes, 4.887 trang, 89 chương)**.

Hệ thống được xây dựng theo kiến trúc **100% Serverless Static Web**, chạy trực tiếp và lưu trữ toàn diện trên Git / GitHub Pages, không cần cài đặt hay duy trì máy chủ backend local.

Hệ thống kết hợp **Sơ đồ Khung xương Giải phẫu Tương tác (Interactive Skeleton Guidemap)**, **1.671 Kỹ thuật mổ chuẩn hóa**, **Hệ thống Thẻ gợi mở Bảng phân loại gãy tinh gọn**, cùng **Hộp thoại Phẫu thuật 5 Tab Chuyên sâu** và **Gợi ý Tìm kiếm Siêu tốc (Live Autocomplete)**.

---

## 🌐 Truy cập Trực tuyến trên Git (GitHub Pages)

Hệ thống được phân bổ thành 6 chuyên đề độc lập với thanh điều hướng đa tầng:

- 🏛️ **Cổng tổng hợp toàn diện**: [campbell-orthopaedics](https://onthibacsinoitru9999-coder.github.io/campbell-orthopaedics/)
- 🖐️ **Chuyên đề Chi Trên & Bàn Tay**: [chi-tren.html](https://onthibacsinoitru9999-coder.github.io/campbell-orthopaedics/chi-tren.html)
- 🦵 **Chuyên đề Chi Dưới & Bàn Chân**: [chi-duoi.html](https://onthibacsinoitru9999-coder.github.io/campbell-orthopaedics/chi-duoi.html)
- 🦴 **Chuyên đề Cột Sống & Vùng Chậu**: [cot-song.html](https://onthibacsinoitru9999-coder.github.io/campbell-orthopaedics/cot-song.html)
- 👶 **Chuyên đề Chấn Thương Chỉnh Hình Nhi**: [nhi-khoa.html](https://onthibacsinoitru9999-coder.github.io/campbell-orthopaedics/nhi-khoa.html)
- 📖 **Chuyên đề Đại Cương & Đường Mổ**: [dai-cuong.html](https://onthibacsinoitru9999-coder.github.io/campbell-orthopaedics/dai-cuong.html)

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

### 2. 🗂️ Thẻ Gợi Mở Tra Cứu Tinh Gọn (Compact Teaser Cards)
- Thẻ phân loại gãy xương trên trang đầu hiển thị ở định dạng **gợi mở tinh gọn** (~140px), giúp tra cứu nhanh trên thiết bị di động mà không phải cuộn trang dài.
- Tích hợp thumbnail thu nhỏ (72×72px) kèm nút phóng to tức thì qua Lightbox.
- Nút `📖 Mở xem nhanh ▾`: Mở rộng toàn bộ ảnh lớn, 4 ô lâm sàng (*Cơ chế, CĐHA, Nguyên tắc xử trí, Biến chứng*) và tất cả các phân nhóm chi tiết ngay tại chỗ.
- Nút `📋 Phác đồ & Quy trình mổ ➔`: Mở hộp thoại trạm phẫu thuật lâm sàng 5 tab.

### 3. 🔪 Trạm Phẫu Thuật Lâm Sàng 5 Tab (5-Tab Surgical Workstation)
- **Tab 1: 🔪 Quy trình mổ**: Phân đoạn 5 pha phẫu thuật chuẩn, động tác then chốt và các mốc giải phẫu.
- **Tab 2: 🖼️ Hình ảnh & Sơ đồ**: Thư viện ảnh giải phẫu, sơ đồ đường mổ, X-quang/CT độ nét cao WebP kèm kính lúp Lightbox.
- **Tab 3: ⚠️ Cảnh báo & Mẹo mổ**: Danger Zones (vùng thần kinh mạch máu nguy hiểm), Pearls & Pitfalls, và Chống chỉ định tuyệt đối.
- **Tab 4: 📋 Chỉ định & Chuẩn bị**: Bảng phân loại gãy xương liên kết, tư thế người bệnh, chuẩn bị bàn mổ và dụng cụ.
- **Tab 5: 🩺 Hậu phẫu & Trích dẫn**: Phác đồ phục hồi chức năng sau mổ và trích xuất nguyên văn Campbell 13th Ed.

### 4. 🔍 Tìm kiếm Toàn diện & Gợi ý Thông minh (Live Autocomplete)
- Tìm kiếm tức thì theo tên danh nhân/eponyms kinh điển (*Broström, Bankart, Smith-Petersen, Latarjet, Chevron, Papineau, Ilizarov, Salter, Pemberton...*).
- Bộ lọc theo 14 Chuyên khoa, 89 Chương sách và danh mục Phẫu thuật viên tác giả.

---

## ⚡ Xem Trực Tiếp & Kiểm Thử Ngoại Tuyến

Do ứng dụng được thiết kế dạng **100% Static Serverless**, bạn có thể:
1. **Xem trực tiếp trên GitHub Pages**: [campbell-orthopaedics](https://onthibacsinoitru9999-coder.github.io/campbell-orthopaedics/)
2. **Hoặc xem trực tiếp trên máy không cần cài đặt backend**:
   Chỉ cần mở file `index.html` hoặc chạy máy chủ tĩnh tiêu chuẩn của Python:
   ```bash
   python -m http.server 8000
   ```
   Sau đó mở [http://localhost:8000](http://localhost:8000).

3. **Chạy bộ kiểm thử tự động trên mobile (Playwright)**:
   ```bash
   python tests/test_playwright_mobile.py
   ```

---

## 📁 Cấu trúc Mã nguồn Dự án

```
cambell/
├── index.html                      # Cổng thông tin lâm sàng tổng hợp (Hub)
├── chi-tren.html                   # Chuyên đề Chi Trên & Bàn Tay (24 chương)
├── chi-duoi.html                   # Chuyên đề Chi Dưới & Bàn Chân (25 chương)
├── cot-song.html                   # Chuyên đề Cột Sống & Vùng Chậu (8 chương)
├── nhi-khoa.html                   # Chuyên đề Chấn Thương Chỉnh Hình Nhi (9 chương)
├── dai-cuong.html                  # Chuyên đề Đại Cương & Đường Mổ (14 chương)
├── README.md                       # Tài liệu hướng dẫn hệ thống
│
├── web/
│   └── static/
│       ├── app.js                  # Frontend Controller thuần tĩnh (Pure Static)
│       ├── styles.css              # Giao diện responsive di động & 5-tab workstation
│       ├── authors.json            # Danh bạ 120+ phẫu thuật viên tác giả kinh điển
│       └── human_skeleton.svg      # Mô hình giải phẫu vector tương tác
│
├── data/                           # Cơ sở dữ liệu JSON tĩnh đã chuẩn hóa
│   ├── anatomical_categories.json  # 14 Nhóm chuyên khoa giải phẫu
│   ├── chapters_catalog.json       # Danh mục 89 chương sách
│   ├── fracture_classifications.json # 35+ Bảng phân loại gãy xương & liên kết kỹ thuật
│   ├── outline_tree.json           # Cây mục lục 6.885 đề mục phẫu thuật
│   ├── techniques_catalog.json     # Danh mục 1.671 kỹ thuật mổ
│   └── techniques/                 # 1.671 Micro-JSON chi tiết từng kỹ thuật mổ
│       ├── 1-1.json
│       ├── 54-14.json
│       └── ...
│
└── tests/
    └── test_playwright_mobile.py   # Bộ kiểm thử 17 kịch bản di động (Mobile viewport)
```

---

## 👨‍⚕️ Tác giả & Đóng góp
- **Chịu trách nhiệm nội dung**: Ôn Thi Bác Sĩ Nội Trú (`onthibacsinoitru9999@gmail.com`)
- **Mục tiêu**: Nền tảng tra cứu phục vụ lâm sàng, học tập, ôn luyện bác sĩ nội trú và phẫu thuật viên Chấn thương Chỉnh hình.
