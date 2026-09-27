import os
import sys
import json
import re
try:
    import pymupdf as fitz
except ImportError:
    import fitz
import threading
import unicodedata
from typing import Optional, List, Dict, Any, Set
from fastapi import FastAPI, HTTPException, Query, Response
from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(
    title="Campbell's Operative Orthopaedics - Clinical Navigator",
    description="Tra cứu phẫu thuật Chấn thương Chỉnh hình theo Giải phẫu và Kỹ thuật mổ (Campbell 13th Ed)",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
CACHE_DIR = os.path.join(BASE_DIR, "cache", "pages")
os.makedirs(CACHE_DIR, exist_ok=True)

PDF_PATH = os.path.join(BASE_DIR, "campbell_13th_ed.pdf")

# Load precomputed datasets
with open(os.path.join(DATA_DIR, "techniques_catalog.json"), "r", encoding="utf-8") as f:
    TECHNIQUES = json.load(f)

with open(os.path.join(DATA_DIR, "chapters_catalog.json"), "r", encoding="utf-8") as f:
    CHAPTERS = json.load(f)

with open(os.path.join(DATA_DIR, "anatomical_categories.json"), "r", encoding="utf-8") as f:
    CATEGORIES_CONFIG = json.load(f)

with open(os.path.join(DATA_DIR, "outline_tree.json"), "r", encoding="utf-8") as f:
    OUTLINE_TREE = json.load(f)

CLASSIFICATIONS_FILE = os.path.join(DATA_DIR, "fracture_classifications.json")
CLASSIFICATIONS = []
if os.path.exists(CLASSIFICATIONS_FILE):
    with open(CLASSIFICATIONS_FILE, "r", encoding="utf-8") as f:
        CLASSIFICATIONS = json.load(f)

# Quick lookup dicts
TECH_DICT = {t["tech_id"]: t for t in TECHNIQUES}
CHAPTER_DICT = {c["chapter"]: c for c in CHAPTERS}

# Shared doc instance for rendering and text (protected by pdf_lock)
pdf_lock = threading.Lock()
pdf_doc = None

def get_pdf_doc():
    global pdf_doc
    if pdf_doc is None or pdf_doc.is_closed:
        with pdf_lock:
            if pdf_doc is None or pdf_doc.is_closed:
                pdf_doc = fitz.open(PDF_PATH)
    return pdf_doc


@app.get("/api/classifications")
def get_classifications(
    q: Optional[str] = Query(None, description="Search term in classification name or bone"),
    bone: Optional[str] = Query(None, description="Filter by bone name or SVG element ID"),
    category: Optional[str] = Query(None, description="Filter by anatomical category")
):
    filtered = CLASSIFICATIONS
    if category:
        filtered = [c for c in filtered if c.get("category") == category]
    if bone:
        bone_lower = bone.lower()
        filtered = [
            c for c in filtered
            if any(bone_lower == svg_id.lower() for svg_id in c.get("svg_ids", []))
            or bone_lower in c.get("bone", "").lower()
            or bone_lower in c.get("bone_vi", "").lower()
        ]
    if q:
        q_norm = normalize_text(q.strip())
        filtered = [
            c for c in filtered
            if q_norm in normalize_text(c["name"])
            or q_norm in normalize_text(c["en_name"])
            or q_norm in normalize_text(c["bone"])
            or q_norm in normalize_text(c["bone_vi"])
            or q_norm in normalize_text(c.get("description", ""))
        ]
    return filtered


@app.get("/api/stats")
def get_stats():
    return {
        "title": "Campbell's Operative Orthopaedics",
        "edition": "13th Edition (4-Volume Set)",
        "total_pages": len(get_pdf_doc()),
        "total_chapters": len(CHAPTERS),
        "total_techniques": len(TECHNIQUES),
        "total_categories": len(CATEGORIES_CONFIG)
    }


@app.get("/api/categories")
def get_categories():
    result = []
    for cat_id, cat_data in CATEGORIES_CONFIG.items():
        chaps = cat_data["chapters"]
        tech_count = sum(1 for t in TECHNIQUES if t["chapter"] in chaps)
        result.append({
            "id": cat_id,
            "vi": cat_data["vi"],
            "icon": cat_data["icon"],
            "chapters": chaps,
            "chapter_count": len(chaps),
            "technique_count": tech_count
        })
    return result


@app.get("/api/chapters")
def get_chapters(category: Optional[str] = None):
    if not category:
        return CHAPTERS
    if category in CATEGORIES_CONFIG:
        allowed = set(CATEGORIES_CONFIG[category]["chapters"])
        return [c for c in CHAPTERS if c["chapter"] in allowed]
    return CHAPTERS


@app.get("/api/authors")
def get_authors():
    authors = set()
    for t in TECHNIQUES:
        a = t.get("author")
        if a and a.strip():
            authors.add(a.strip())
    return sorted(list(authors))


def normalize_text(text: str) -> str:
    if not text:
        return ""
    # Handle Vietnamese 'đ'/'Đ' -> 'd'/'D'
    text = text.replace('đ', 'd').replace('Đ', 'D')
    # Strip accents / combining diacritics and convert to lower
    nfkd = unicodedata.normalize('NFKD', text)
    return ''.join(c for c in nfkd if not unicodedata.combining(c)).lower()

def canonical_text(text: str) -> str:
    norm = normalize_text(text)
    # Replace hyphens, underscores, slashes, and non-alphanumeric characters with spaces
    return re.sub(r'[\W_]+', ' ', norm).strip()

# Comprehensive Bilingual Vietnamese-English Orthopaedic Synonym Lexicon
ORTHOPAEDIC_LEXICON: Dict[str, List[str]] = {
    # Anatomical structures & Bones
    "mam chay": ["tibial plateau", "tibia plateau", "54-14", "54-15", "54-16"],
    "khop hang": ["hip", "hip joint", "femoroacetabular"],
    "co xuong dui": ["femoral neck", "neck of femur", "55-1", "55-4"],
    "dau tren xuong dui": ["proximal femur", "intertrochanteric", "subtrochanteric"],
    "dau duoi xuong dui": ["distal femur", "femoral condyle", "supracondylar femur"],
    "than xuong dui": ["femoral shaft", "shaft of femur"],
    "cot song": ["spine", "spinal", "vertebra", "vertebral"],
    "cot song co": ["cervical spine", "cervical"],
    "cot song nguc": ["thoracic spine", "thoracic"],
    "cot song that lung": ["lumbar spine", "lumbar", "lumbosacral"],
    "khop goi": ["knee", "knee joint", "patellofemoral", "tibiofemoral"],
    "co chan": ["ankle", "ankle joint", "tibiotalar", "talocrural", "bimalleolar", "trimalleolar"],
    "khop vai": ["shoulder", "shoulder joint", "glenohumeral"],
    "khop khuu": ["elbow", "elbow joint", "radiocapitellar"],
    "xuong canh tay": ["humerus", "humeral"],
    "dau tren xuong canh tay": ["proximal humerus", "humeral head"],
    "dau duoi xuong canh tay": ["distal humerus", "humeral condyle"],
    "than xuong canh tay": ["humeral shaft", "shaft of humerus"],
    "xuong quay": ["radius", "radial"],
    "dau duoi xuong quay": ["distal radius", "colles", "smith"],
    "chom xuong quay": ["radial head", "head of radius"],
    "xuong tru": ["ulna", "ulnar"],
    "mom khuu": ["olecranon"],
    "xuong banh che": ["patella", "patellar"],
    "o coi": ["acetabulum", "acetabular"],
    "khung chau": ["pelvis", "pelvic", "pelvic ring", "innominate"],
    "vong chau": ["pelvic ring", "pelvis"],
    "xuong chau": ["pelvis", "ilium", "ischium", "pubis"],
    "xuong dui": ["femur", "femoral"],
    "xuong chay": ["tibia", "tibial"],
    "xuong mac": ["fibula", "fibular"],
    "mat ca": ["malleolus", "malleolar", "bimalleolar", "trimalleolar"],
    "mat ca trong": ["medial malleolus"],
    "mat ca ngoai": ["lateral malleolus"],
    "xuong got": ["calcaneus", "calcaneal", "os calcis"],
    "xuong sen": ["talus", "talar"],
    "xuong thuyen": ["navicular", "scaphoid"],
    "ban chan": ["foot", "forefoot", "midfoot", "hindfoot"],
    "ngon chan": ["toe", "toes", "hallux", "phalanges", "lesser toe"],
    "ngon chan cai": ["hallux", "great toe"],
    "ban tay": ["hand", "metacarpal"],
    "ngon tay": ["finger", "digit", "phalangeal", "phalanges"],
    "ngon cai": ["thumb"],
    "co tay": ["wrist", "carpal", "carpus", "radiocarpal"],
    "khop cung chau": ["sacroiliac", "si joint"],
    "xuong cung": ["sacrum", "sacral"],

    # Soft tissues, Ligaments & Tendons
    "day chang": ["ligament", "ligamentous", "syndesmosis"],
    "day chang cheo truoc": ["anterior cruciate ligament", "acl"],
    "day chang cheo sau": ["posterior cruciate ligament", "pcl"],
    "day chang ben trong": ["medial collateral ligament", "mcl"],
    "day chang ben ngoai": ["lateral collateral ligament", "lcl"],
    "sun chem": ["meniscus", "meniscal"],
    "sun khop": ["cartilage", "chondral", "osteochondral"],
    "gan": ["tendon", "tendinous", "tenodesis"],
    "gan got": ["achilles", "achilles tendon", "tendo calcaneus"],
    "gan achilles": ["achilles", "achilles tendon"],
    "gan banh che": ["patellar tendon", "patellar ligament"],
    "chop xoay": ["rotator cuff", "supraspinatus", "subscapularis"],
    "gan co nhi dau": ["biceps", "biceps tendon", "biceps tenodesis"],
    "than kinh": ["nerve", "neural", "neurolysis"],
    "than kinh toa": ["sciatic nerve"],
    "than kinh quay": ["radial nerve"],
    "than kinh giua": ["median nerve"],
    "than kinh tru": ["ulnar nerve"],
    "than kinh mac": ["peroneal nerve", "fibular nerve"],

    # Procedures & Surgical Concepts
    "thay khop": ["arthroplasty", "replacement", "prosthesis"],
    "thay khop hang": ["hip arthroplasty", "total hip", "tha", "hemiarthroplasty"],
    "thay khop goi": ["knee arthroplasty", "total knee", "tka", "unicompartmental knee"],
    "thay khop vai": ["shoulder arthroplasty", "reverse shoulder", "hemiarthroplasty"],
    "thay khop khuu": ["elbow arthroplasty", "total elbow"],
    "thay khop co chan": ["ankle arthroplasty", "total ankle"],
    "duong mo": ["approach", "exposure", "incision", "anterolateral", "posterolateral", "ilioinguinal"],
    "tiep can": ["approach", "exposure", "access"],
    "phau truong": ["approach", "exposure"],
    "ket hop xuong": ["fixation", "osteosynthesis", "orif", "plate", "plating", "nailing"],
    "nan chinh": ["reduction", "closed reduction", "open reduction"],
    "nan": ["reduction"],
    "cat cut": ["amputation", "disarticulation", "stump"],
    "thao khop": ["disarticulation"],
    "cat xuong": ["osteotomy", "realignment"],
    "duc xuong": ["osteotomy"],
    "han khop": ["arthrodesis", "fusion", "joint fusion"],
    "dong cung khop": ["arthrodesis", "ankylosis"],
    "noi soi": ["arthroscopy", "arthroscopic", "endoscopic"],
    "ghep xuong": ["bone graft", "grafting", "autograft", "allograft"],
    "khau": ["repair", "suture", "tenorrhaphy"],
    "phuc hoi": ["repair", "reconstruction"],
    "sua chua": ["repair"],
    "tai tao": ["reconstruction", "plasty"],
    "tao hinh": ["reconstruction", "plasty", "arthroplasty"],
    "chuyen gan": ["tendon transfer", "transfer of tendon"],
    "keo dai chi": ["lengthening", "limb lengthening", "distraction"],
    "keo dai xuong": ["bone lengthening", "distraction osteogenesis"],
    "giai phong": ["release", "decompression", "capsulotomy", "tenotomy"],
    "cat bao khop": ["capsulotomy", "capsular release"],
    "cat gan": ["tenotomy"],
    "khung co dinh ngoai": ["external fixation", "external fixator", "ex-fix", "ilizarov", "circular frame"],
    "co dinh ngoai": ["external fixation", "external fixator", "ex-fix"],
    "dinh noi tuy": ["intramedullary nail", "intramedullary nailing", "im nail", "interlocking nail", "rod"],
    "nep vit": ["plate and screws", "plate fixation", "plating", "locking plate", "dcp"],
    "nep": ["plate", "plating"],
    "vit": ["screw", "screws", "cannulated screw"],
    "vit xop": ["cancellous screw", "cannulated screw"],
    "vit cuong song": ["pedicle screw", "pedicular screw"],
    "bat vit cuong": ["pedicle screw fixation"],
    "nao vet": ["curettage", "debridement"],
    "cat loc": ["debridement", "irrigation and debridement"],
    "giai ep": ["decompression", "decompressive"],

    # Pathologies & Clinical Entities
    "gay xuong": ["fracture", "fractures", "broken bone"],
    "trat khop": ["dislocation", "dislocations", "subluxation"],
    "ban trat": ["subluxation"],
    "chen ep khoang": ["compartment syndrome", "fasciotomy"],
    "u xuong": ["bone tumor", "tumor", "neoplasm", "osteosarcoma", "giant cell tumor", "cyst"],
    "khoi u": ["tumor", "mass", "neoplasm", "lesion"],
    "nhiem trung": ["infection", "osteomyelitis", "septic arthritis"],
    "viem xuong tuy": ["osteomyelitis", "bone infection"],
    "viem khop nhiem khuan": ["septic arthritis"],
    "thoat vi dia dem": ["herniated disc", "herniated nucleus pulposus", "discectomy", "disc herniation"],
    "veo cot song": ["scoliosis", "spinal deformity"],
    "gu cot song": ["kyphosis"],
    "truot dot song": ["spondylolisthesis", "spondylolysis"],
    "hep ong song": ["spinal stenosis", "stenosis", "laminectomy"],
    "khop gia": ["nonunion", "pseudoarthrosis"],
    "cham lien xuong": ["delayed union", "nonunion"],
    "can lech": ["malunion", "malunited fracture"],
    "lien lech": ["malunion"],
    "hoai tu vo mach": ["avascular necrosis", "osteonecrosis", "avn"],
    "hoai tu chom": ["avascular necrosis of femoral head", "osteonecrosis"],
    "thoai hoa khop": ["osteoarthritis", "degenerative joint disease", "arthrosis"],
    "viem khop dang thap": ["rheumatoid arthritis", "rheumatoid"],
    "ban chan bet": ["flatfoot", "pes planus"],
    "ban chan vom": ["cavus", "pes cavus"],
    "ngon chan khoam": ["claw toe", "clawing"],
    "ngon chan bua": ["hammer toe", "mallet toe"],
    "ngon chan cai veo ngoai": ["hallux valgus", "bunion", "bunionette"],
    "ban chan khoeo": ["clubfoot", "talipes equinovarus"],
    "mat vung": ["instability", "laxity", "subluxation"],
    "rach": ["tear", "rupture"],
    "dut": ["rupture", "tear", "transection"],
    "gay ho": ["open fracture", "compound fracture", "gustilo"],
    "mat doan xuong": ["bone defect", "bone loss", "segmental defect"],
    "hoi chung ong co tay": ["carpal tunnel syndrome", "carpal tunnel release"],

    # Classic Classifications & Eponyms
    "schatzker": ["schatzker", "tibial plateau", "54-14", "54-15", "54-16"],
    "garden": ["garden", "femoral neck", "55-1", "55-4"],
    "pauwels": ["pauwels", "femoral neck", "55-1", "58-20"],
    "neer": ["neer", "proximal humerus", "57-4", "57-5", "12-4"],
    "gustilo": ["gustilo", "open fracture", "53-1"],
    "young burgess": ["young-burgess", "pelvis", "pelvic ring", "56-4", "56-8"],
    "judet letournel": ["judet-letournel", "acetabulum", "56-1", "56-2"],
    "denis": ["denis", "spine", "thoracolumbar", "41-15", "41-16"],
    "danis weber": ["danis-weber", "ankle", "malleolus", "54-1", "54-2", "89-1"],
    "hawkins": ["hawkins", "talus", "talar neck", "88-8", "88-11"],
    "frykman": ["frykman", "distal radius", "57-13", "57-15"],
    "mason": ["mason", "radial head", "57-9", "57-10", "12-6"],
    "salter harris": ["salter-harris", "physeal fracture", "epiphyseal"],
    "brostrom": ["brostrom", "89-2", "89-6"],
    "bankart": ["bankart", "46-2", "52-2"],
    "latarjet": ["latarjet", "52-11"],
    "smith petersen": ["smith-petersen", "1-60", "1-62", "1-70", "3-2", "41-24"],
    "chevron": ["chevron", "austin", "83-2", "83-3"],
    "ilizarov": ["ilizarov", "external fixation", "distraction"],
    "papineau": ["papineau", "21-3"]
}

# Pre-computed search indexing for ultra-fast <50ms query processing
INDEXED_TECHNIQUES = []
for t in TECHNIQUES:
    tech_id_norm = normalize_text(t["tech_id"])
    tech_id_canon = canonical_text(t["tech_id"])
    name_norm = normalize_text(t["name"])
    name_canon = canonical_text(t["name"])
    author_norm = normalize_text(t.get("author", ""))
    author_canon = canonical_text(t.get("author", ""))
    chap_norm = normalize_text(t.get("chapter_title", ""))
    chap_canon = canonical_text(t.get("chapter_title", ""))

    cat_terms = []
    for c in t.get("categories", []):
        cat_terms.append(canonical_text(c.get("vi", "")))
        cat_terms.append(canonical_text(c.get("id", "")))
    cat_str = " ".join(cat_terms)

    full_text = f"{tech_id_canon} {name_canon} {author_canon} {chap_canon} {cat_str}"
    tokens = set(full_text.split())

    INDEXED_TECHNIQUES.append({
        "raw": t,
        "tech_id_norm": tech_id_norm,
        "tech_id_canon": tech_id_canon,
        "name_norm": name_norm,
        "name_canon": name_canon,
        "author_norm": author_norm,
        "author_canon": author_canon,
        "chap_norm": chap_norm,
        "chap_canon": chap_canon,
        "cat_str": cat_str,
        "tokens": tokens
    })

@app.get("/api/techniques")
def get_techniques(
    q: Optional[str] = Query(None, description="Search term in technique ID, name, or author"),
    category: Optional[str] = Query(None, description="Filter by anatomical category ID or name"),
    chapter: Optional[int] = Query(None, description="Filter by chapter number"),
    author: Optional[str] = Query(None, description="Filter by author name"),
    page: int = Query(1, ge=1),
    limit: int = Query(25, ge=1, le=200)
):
    # Base candidates
    candidates = INDEXED_TECHNIQUES

    # 1. Filter by category
    if category:
        cat_lower = category.strip().lower()
        allowed_chaps = None
        if category in CATEGORIES_CONFIG:
            allowed_chaps = set(CATEGORIES_CONFIG[category]["chapters"])
        else:
            for c_id, c_data in CATEGORIES_CONFIG.items():
                if cat_lower == c_id.lower() or cat_lower == c_data.get("vi", "").lower():
                    allowed_chaps = set(c_data["chapters"])
                    break
        if allowed_chaps is not None:
            candidates = [it for it in candidates if it["raw"]["chapter"] in allowed_chaps]
        else:
            candidates = [
                it for it in candidates
                if any(
                    cat_lower in c.get("id", "").lower() or cat_lower in c.get("vi", "").lower()
                    for c in it["raw"].get("categories", [])
                )
            ]

    # 2. Filter by chapter
    if chapter:
        candidates = [it for it in candidates if it["raw"]["chapter"] == chapter]

    # 3. Filter by author
    if author:
        author_canon = canonical_text(author)
        candidates = [
            it for it in candidates
            if author_canon in it["author_canon"] or normalize_text(author) in it["author_norm"]
        ]

    # 4. Search query
    if not q:
        filtered = [it["raw"] for it in candidates]
    else:
        q_raw = q.strip()
        q_norm = normalize_text(q_raw)
        q_canon = canonical_text(q_raw)
        q_tokens = set(q_canon.split())

        # Expand query using Bilingual Lexicon
        expanded_terms = []
        if q_canon in ORTHOPAEDIC_LEXICON:
            expanded_terms.extend(ORTHOPAEDIC_LEXICON[q_canon])
        else:
            for phrase, eng_list in ORTHOPAEDIC_LEXICON.items():
                if phrase in q_canon:
                    expanded_terms.extend(eng_list)

        expanded_canons = [canonical_text(et) for et in expanded_terms]

        scored = []
        for it in candidates:
            score = 0
            t = it["raw"]

            # Exact ID match
            if q_norm == it["tech_id_norm"] or q_canon == it["tech_id_canon"]:
                score += 2000
            elif it["tech_id_norm"].startswith(q_norm) or it["tech_id_canon"].startswith(q_canon):
                score += 1200
            elif q_norm in it["tech_id_norm"] or q_canon in it["tech_id_canon"]:
                score += 800

            # Exact phrase in Name or Author (with hyphen/space flexibility)
            if q_canon and q_canon in it["name_canon"]:
                score += 1000
            elif q_canon and q_canon in it["author_canon"]:
                score += 900
            elif q_norm and (q_norm in it["name_norm"] or q_norm in it["author_norm"]):
                score += 750

            # Substring in chapter title
            if q_canon and q_canon in it["chap_canon"]:
                score += 400

            # Query token overlap
            if q_tokens and q_tokens.issubset(it["tokens"]):
                score += 500
            elif q_tokens:
                overlap = len(q_tokens.intersection(it["tokens"]))
                if overlap > 0:
                    score += overlap * 60

            # Bilingual Lexicon matches
            for exp in expanded_canons:
                if exp in it["name_canon"]:
                    score += 600
                elif exp in it["chap_canon"]:
                    score += 350
                else:
                    exp_words = set(exp.split())
                    if exp_words and exp_words.issubset(it["tokens"]):
                        score += 450
                    elif exp_words:
                        ov = len(exp_words.intersection(it["tokens"]))
                        if ov > 0:
                            score += ov * 40

            if score > 0:
                scored.append((score, t))

        # Sort by relevance score descending, then chapter, then tech_id
        scored.sort(key=lambda x: (-x[0], x[1]["chapter"], x[1]["tech_id"]))
        filtered = [s[1] for s in scored]

    total = len(filtered)
    start = (page - 1) * limit
    end = start + limit
    items = filtered[start:end]

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit,
        "items": items
    }


@app.get("/api/techniques/{tech_id}")
def get_technique_detail(tech_id: str):
    if tech_id not in TECH_DICT:
        raise HTTPException(status_code=404, detail=f"Technique {tech_id} not found")
    
    tech = TECH_DICT[tech_id].copy()
    pdf_p = tech.get("pdf_page")

    # Extract text content from the PDF page (and next page if continuation)
    text_content = ""
    if pdf_p:
        doc = get_pdf_doc()
        if 1 <= pdf_p <= len(doc):
            with pdf_lock:
                combined_text = doc[pdf_p - 1].get_text()
                if pdf_p < len(doc):
                    combined_text += "\n--- Trang kế tiếp ---\n" + doc[pdf_p].get_text()

            # Search for technique section
            tech_match = re.search(
                rf"(TECHNIQUE\s+{re.escape(tech_id)}[\s\S]*?)(?=(?:TECHNIQUE\s+\d+-\d+|POSTOPERATIVE\s+CARE|COMPLICATIONS|\Z))",
                combined_text,
                re.IGNORECASE
            )
            if tech_match and len(tech_match.group(1).strip()) > 30:
                text_content = tech_match.group(1).strip()
            else:
                text_content = combined_text[:4000].strip()

    tech["extracted_text"] = text_content
    return tech


@app.get("/api/technique-text/{tech_id}")
def get_technique_text(tech_id: str):
    detail = get_technique_detail(tech_id)
    return {
        "id": detail.get("tech_id"),
        "title": detail.get("name"),
        "page": detail.get("pdf_page"),
        "text": detail.get("extracted_text", ""),
        "procedure_steps": []
    }


@app.get("/api/outline")
def get_outline():
    return OUTLINE_TREE


_IMAGE_CACHE: Dict[str, bytes] = {}
_IMAGE_CACHE_LOCK = threading.Lock()
MAX_IMAGE_CACHE_ENTRIES = 256

def render_page_to_cache(page_num: int, dpi: int = 150) -> str:
    """Thread-safe rendering of a single PDF page to disk cache."""
    doc = get_pdf_doc()
    if page_num < 1 or page_num > len(doc):
        raise HTTPException(status_code=404, detail="Page number out of bounds")

    cache_file = os.path.join(CACHE_DIR, f"page_{page_num}_dpi{dpi}.png")
    if os.path.exists(cache_file):
        return cache_file

    with pdf_lock:
        if not os.path.exists(cache_file):
            page = doc[page_num - 1]
            pix = page.get_pixmap(dpi=dpi)
            temp_cache = f"{cache_file}_{os.getpid()}_{threading.get_ident()}.tmp.png"
            pix.save(temp_cache)
            os.replace(temp_cache, cache_file)

    return cache_file


def get_page_image_bytes(page_num: int, dpi: int = 150) -> bytes:
    """Thread-safe retrieval of rendered page bytes with memory and disk caching."""
    cache_key = f"{page_num}_{dpi}"
    with _IMAGE_CACHE_LOCK:
        if cache_key in _IMAGE_CACHE:
            return _IMAGE_CACHE[cache_key]

    cache_file = render_page_to_cache(page_num, dpi=dpi)
    with open(cache_file, "rb") as f:
        img_bytes = f.read()

    with _IMAGE_CACHE_LOCK:
        if len(_IMAGE_CACHE) >= MAX_IMAGE_CACHE_ENTRIES:
            oldest_key = next(iter(_IMAGE_CACHE))
            _IMAGE_CACHE.pop(oldest_key, None)
        _IMAGE_CACHE[cache_key] = img_bytes

    return img_bytes


@app.get("/api/page-image/{page_num}")
@app.get("/api/page/{page_num}")
def get_page_image(page_num: int, dpi: int = 150):
    img_bytes = get_page_image_bytes(page_num, dpi=dpi)
    return Response(
        content=img_bytes,
        media_type="image/png",
        headers={"Cache-Control": "public, max-age=86400"}
    )


@app.get("/api/page-text/{page_num}")
def get_page_text(page_num: int):
    doc = get_pdf_doc()
    if page_num < 1 or page_num > len(doc):
        raise HTTPException(status_code=404, detail="Page number out of bounds")

    with pdf_lock:
        page = doc[page_num - 1]
        text = page.get_text()

    return {
        "page_num": page_num,
        "text": text
    }


def prewarm_technique_pages(dpi: int = 150, max_pages: Optional[int] = None) -> dict:
    """Pre-cache all technique main pages at 150 DPI into cache/pages/."""
    os.makedirs(CACHE_DIR, exist_ok=True)
    doc = get_pdf_doc()
    pages_to_cache = sorted(set(
        t["pdf_page"] for t in TECHNIQUES
        if t.get("pdf_page") and 1 <= t["pdf_page"] <= len(doc)
    ))
    if max_pages is not None:
        pages_to_cache = pages_to_cache[:max_pages]

    cached_count = 0
    skipped_count = 0

    for page_num in pages_to_cache:
        cache_file = os.path.join(CACHE_DIR, f"page_{page_num}_dpi{dpi}.png")
        if os.path.exists(cache_file):
            skipped_count += 1
            continue

        with pdf_lock:
            if not os.path.exists(cache_file):
                page = doc[page_num - 1]
                pix = page.get_pixmap(dpi=dpi)
                temp_cache = f"{cache_file}_{os.getpid()}_{threading.get_ident()}.tmp.png"
                pix.save(temp_cache)
                os.replace(temp_cache, cache_file)
                cached_count += 1

    return {
        "total_technique_pages": len(pages_to_cache),
        "rendered": cached_count,
        "already_cached": skipped_count,
        "dpi": dpi
    }


@app.get("/api/admin/prewarm")
@app.post("/api/admin/prewarm")
@app.get("/api/prewarm")
def admin_prewarm(dpi: int = 150, max_pages: Optional[int] = None):
    return prewarm_technique_pages(dpi=dpi, max_pages=max_pages)


# Static web directory
STATIC_DIR = os.path.join(BASE_DIR, "web", "static")
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
    app.mount("/web/static", StaticFiles(directory=STATIC_DIR), name="web_static")

DATA_DIR = os.path.join(BASE_DIR, "data")
if os.path.exists(DATA_DIR):
    app.mount("/data", StaticFiles(directory=DATA_DIR), name="data")

@app.get("/")
def serve_index():
    root_index = os.path.join(BASE_DIR, "index.html")
    if os.path.exists(root_index):
        return FileResponse(root_index)
    index_file = os.path.join(BASE_DIR, "web", "static", "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return HTMLResponse("<h1>Campbell Web Navigator</h1><p>Static files loading...</p>")

@app.get("/{page_name}.html")
def serve_html_page(page_name: str):
    target = os.path.join(BASE_DIR, f"{page_name}.html")
    if os.path.exists(target):
        return FileResponse(target)
    target_static = os.path.join(BASE_DIR, "web", "static", f"{page_name}.html")
    if os.path.exists(target_static):
        return FileResponse(target_static)
    raise HTTPException(status_code=404, detail="Page not found")

if __name__ == "__main__":
    if "--prewarm" in sys.argv:
        print("Pre-warming technique pages...")
        res = prewarm_technique_pages()
        print(f"Pre-warm complete: {res}")
    else:
        uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
