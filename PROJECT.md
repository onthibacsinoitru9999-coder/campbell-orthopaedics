# Project: Kinh thánh Chấn thương Chỉnh hình (Campbell's Operative Orthopaedics 13th Ed)

## Architecture
Web-based clinical & surgical reference platform built on FastAPI (backend), PyMuPDF (PDF rendering engine), In-Memory Search Engine with Vietnamese unaccented normalization and orthopaedic synonym dictionary, Interactive SVG Human Skeleton Guidemap, and High-DPI Modal Viewer with Zoom/Pan and procedure text extraction.

### Core Components:
1. **Backend Server (`server.py`)**:
   - In-memory catalogs: 1,671 operative techniques, 89 chapters, 14 anatomical regions, 6,885 outline headings, clinical fracture classifications.
   - High-DPI page renderer: Thread-safe PyMuPDF rendering at 150-200 DPI with disk caching in `cache/pages/`.
   - Multi-dimensional search engine: Vietnamese accent-insensitive + English + eponym lookup + clinical synonym lexicon.
2. **Frontend Client (`web/static/`)**:
   - `index.html`: Responsive clinical workstation layout with Hero search, Interactive SVG guidemap, technique catalog with multi-facet filters, and High-DPI viewer modal.
   - `app.js`: Interactive bone click handlers, SVG glow effects, dynamic classification card rendering with per-type operative technique links, instant search autocomplete, zoom/pan viewer.
   - `style.css`: Medical workstation theme, SVG bone glowing animation, responsive grid.
   - `human_skeleton.svg`: Anatomical skeleton with interactive bone groups.
3. **Data Integrity & Classifications (`data/`)**:
   - `techniques_catalog.json`: 1,671 operative techniques with 100% verified printed and PDF page numbers.
   - `fracture_classifications.json`: Clinical fracture classifications with type descriptions, surgical indications, and verified technique links.
   - `outline_tree.json`: 6,885 outline headings mapped to exact PDF pages.
   - `anatomical_categories.json`: 14 anatomical regions with chapter groupings.

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| F1 | Interactive Skeleton SVG Guidemap | Interactive SVG with 61+ bones (including FemurRight fix), hover/selected glow effects, click events | M3 | R1, Survey |
| F2 | Clinical Fracture Classification System | 12+ classification systems with complete types, clinical descriptions, surgical principles, including AO/OTA | M2 | R1, Survey |
| F3 | Direct Per-Type Operative Technique Links | Direct link buttons on each classification type (e.g. Schatzker II -> Tech 54-24) opening the modal | M2, M3 | R1, Survey |
| F4 | 1,671 Operative Techniques Catalog | Complete verified catalog with 0 duplicates, 0 missing numbers across all 80 technique chapters | M1 | R2, R4, Survey |
| F5 | 100% Exact PDF Page Mapping | Correct 16 anomalous page assignments in catalog and systematic -1 page offset in outline headings | M1 | R2, R3, Survey |
| F6 | Multi-Dimensional Instant Search Engine | Instant sub-50ms search by technique ID, surgical title, authors, chapter, printed page, and PDF page | M1 | R2, Survey |
| F7 | Vietnamese Accent-Insensitive Normalization | Full diacritic folding including 'đ'/'Đ' -> 'd'/'D' and hyphen/space flexibility for eponyms | M1 | R2, Survey |
| F8 | Bilingual Orthopaedic Synonym Lexicon | Vietnamese clinical terminology search (e.g. "mâm chày", "khớp háng", "cột sống", "dây chằng") mapped to English techniques | M1 | R2, Survey |
| F9 | Multi-Facet Filtering UI | Filter by 14 Anatomical Regions, 89 Chapters, and Authors | M3 | R2, Survey |
| F10 | High-DPI In-situ Page Viewer | 150-200 DPI scan view inside modal without downloading 437MB PDF, thread-safe rendering | M4 | R3, Survey |
| F11 | Sub-500ms Cached Page Loading | Disk-cached PNG pages (<1ms cached load), pre-warming pipeline for technique pages | M1, M4 | R3, Survey |
| F12 | Viewer Interactive Controls (Zoom, Pan, Nav) | Zoom in/out, reset, click-and-drag pan, and Next/Prev page navigation for multi-page techniques | M4 | R3, Survey |
| F13 | Procedure Text Extraction | Full text extraction for technique steps, refined regex without truncation on complications | M4 | R3, Survey |
| F14 | 6-Part Volume Integrity Verification | Comprehensive audit report verifying 6 parts (Vol 1A, 1B-2A, 2B, 2C-3A, 3B, 4) and continuity | M1, M5 | R4, Survey |
| F15 | Comprehensive Opaque-Box E2E Test Suite | 4-tier requirement-driven test suite with automated verification runner | E2E Track | Acceptance Criteria |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| E2E | E2E Testing Track | Design & implement opaque-box test suite (Tiers 1-4) in parallel, publish TEST_READY.md | none | IN_PROGRESS |
| M1 | Data Pipeline & Search Core Integrity | Patch 16 anomalous PDF pages, fix outline tree shift, fix 'đ'/'Đ' & hyphen normalization, add Vietnamese orthopaedic synonym lexicon, thread-safe PDF render | none | IN_PROGRESS |
| M2 | Clinical Classifications & Medical Linking | Update classification schema with per-type buttons, fix all medical mis-linkages, add AO/OTA & clinical systems | M1 | PLANNED |
| M3 | Interactive SVG Guidemap & UI Polish | Group FemurRight in SVG, fix CSS glow styles, add Author filter, instant autocomplete, render per-type buttons | M2 | PLANNED |
| M4 | High-DPI Page Viewer Upgrade | Interactive Zoom/Pan, Next/Prev pagination, fix text extraction regex, pre-warm page cache | M1 | PLANNED |
| M5 | Final Milestone: 100% E2E Pass & Hardening | Phase 1: 100% E2E test pass (Tiers 1-4); Phase 2: Adversarial coverage hardening (Tier 5) | E2E, M3, M4 | PLANNED |

## Interface Contracts
### Data Formats & APIs:
- `GET /api/techniques?q={query}&category={cat}&chapter={chap}&author={author}`:
  Returns `[ { id, title, chapter_id, chapter_title, category, printed_page, pdf_page, author, approaches } ]`
- `GET /api/techniques/{tech_id}`:
  Returns single technique with full metadata and adjacent technique navigation
- `GET /api/classifications`:
  Returns `[ { id, name, bone, region, description, types: [ { type, description, principles, technique_id, technique_title } ], techniques: [...] } ]`
- `GET /api/page/{page_num}?dpi={dpi}`:
  Returns PNG image bytes with `Cache-Control: public, max-age=86400`
- `GET /api/technique-text/{tech_id}`:
  Returns `{ id, title, page, text, procedure_steps }`

## Code Layout
- `server.py`: FastAPI server, search indexing, rendering pipeline, API routes
- `build_classifications.py`: Generator script for clinical classifications
- `web/static/index.html`: Main SPA interface
- `web/static/app.js`: Client application logic
- `web/static/style.css`: Workstation design system & animations
- `web/static/human_skeleton.svg`: Interactive anatomical skeleton
- `data/techniques_catalog.json`: Master techniques catalog
- `data/fracture_classifications.json`: Master clinical classifications
- `data/outline_tree.json`: Master book outline
- `cache/pages/`: Rendered high-DPI page cache
- `tests/`: Automated test suite
