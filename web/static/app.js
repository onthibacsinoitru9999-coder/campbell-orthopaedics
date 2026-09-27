// State
let currentTab = 'categories';
let categoriesData = [];
let chaptersData = [];
let currentPage = 1;
let currentCategory = '';
let currentChapter = '';
let currentAuthor = '';
let searchQuery = '';
let activeTechnique = null;
let currentBoneSelection = null;
let currentPortal = 'all';

const PORTAL_SPECS = {
  'spine-pelvis': {
    chapters: [37, 38, 39, 40, 41, 42, 43, 44, 55, 56],
    nameVi: 'Cột Sống & Vùng Chậu'
  },
  'general': {
    chapters: [1, 2, 20, 21, 22, 23, 24, 25, 26, 27, 28, 48, 80],
    nameVi: 'Đại Cương & Đường Mổ'
  },
  'upper': {
    chapters: [12, 13, 14, 46, 47, 52, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79],
    nameVi: 'Chi Trên & Khớp Vai'
  },
  'lower': {
    chapters: [3, 4, 5, 6, 7, 8, 9, 10, 11, 45, 50, 51, 54, 55, 56, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89],
    nameVi: 'Chi Dưới & Khung Chậu'
  }
};

// DOM Elements
const navTabs = document.querySelectorAll('.tab-btn');
const viewSections = document.querySelectorAll('.view-section');
const globalSearch = document.getElementById('globalSearch');
const searchBtn = document.getElementById('searchBtn');
const categoriesGrid = document.getElementById('categoriesGrid');
const techniquesGrid = document.getElementById('techniquesGrid');
const chaptersGrid = document.getElementById('chaptersGrid');
const outlineContainer = document.getElementById('outlineContainer');
const categoryFilter = document.getElementById('categoryFilter');
const chapterFilter = document.getElementById('chapterFilter');
const authorFilter = document.getElementById('authorFilter');
const techniqueSearch = document.getElementById('techniqueSearch');
const techniqueSuggestions = document.getElementById('techniqueSuggestions');
const techResultCount = document.getElementById('techResultCount');
const techPagination = document.getElementById('techPagination');

// Skeleton & Classification Elements
const btnModeSkeleton = document.getElementById('btnModeSkeleton');
const btnModeAllClassifications = document.getElementById('btnModeAllClassifications');
const btnModeGrid = document.getElementById('btnModeGrid');
const skeletonExplorerContainer = document.getElementById('skeletonExplorerContainer');
const allClassificationsDirectory = document.getElementById('allClassificationsDirectory');
const allClassificationsGrid = document.getElementById('allClassificationsGrid');
const classifSearchInput = document.getElementById('classifSearchInput');
const classifFilterPills = document.getElementById('classifFilterPills');
const quickBonesBar = document.getElementById('quickBonesBar');
const skeletonSvgBox = document.getElementById('skeletonSvgBox');
const skeletonTooltip = document.getElementById('skeletonTooltip');
const skeletonHoverTag = document.getElementById('skeletonHoverTag');
const selectedBoneName = document.getElementById('selectedBoneName');
const selectedBoneEn = document.getElementById('selectedBoneEn');
const statBoneChapters = document.getElementById('statBoneChapters');
const statBoneTechs = document.getElementById('statBoneTechs');
const statBoneApproaches = document.getElementById('statBoneApproaches');
const statBoneClassifications = document.getElementById('statBoneClassifications');
const skeletonSampleGrid = document.getElementById('skeletonSampleGrid');
const boneTechListTitle = document.getElementById('boneTechListTitle');
const boneTechSampleCount = document.getElementById('boneTechSampleCount');
const btnViewAllBoneTechs = document.getElementById('btnViewAllBoneTechs');
const tabBtnClassifications = document.getElementById('tabBtnClassifications');
const tabBtnTechs = document.getElementById('tabBtnTechs');
const skeletonClassificationsContainer = document.getElementById('skeletonClassificationsContainer');
const skeletonTechsContainer = document.getElementById('skeletonTechsContainer');

// Modal Elements
const techModal = document.getElementById('techModal');
const modalCloseBtn = document.getElementById('modalCloseBtn');
const modalTechId = document.getElementById('modalTechId');
const modalTechTitle = document.getElementById('modalTechTitle');
const modalTechMeta = document.getElementById('modalTechMeta');
const modalTechDetailHeader = document.getElementById('modalTechDetailHeader');
const modalLinkedClassifBox = document.getElementById('modalLinkedClassifBox');
const modalPageImage = document.getElementById('modalPageImage');
const modalExtractedText = document.getElementById('modalExtractedText');
const btnTextOpenDrive = document.getElementById('btnTextOpenDrive');
const btnTextSwitchScan = document.getElementById('btnTextSwitchScan');
const pagePreviewLabel = document.getElementById('pagePreviewLabel');
const pageIndicator = document.getElementById('pageIndicator');
const pageImgWrapper = document.getElementById('pageImgWrapper');
const downloadPageBtn = document.getElementById('downloadPageBtn');
const modalTabs = document.querySelectorAll('.modal-tab-btn');
const tabContentPagePreview = document.getElementById('tabContentPagePreview');
const tabContentExtractedText = document.getElementById('tabContentExtractedText');

// Modal Toolbar & Zoom Elements
const btnPrevPage = document.getElementById('btnPrevPage');
const btnNextPage = document.getElementById('btnNextPage');
const btnZoomIn = document.getElementById('btnZoomIn');
const btnZoomOut = document.getElementById('btnZoomOut');
const btnZoomReset = document.getElementById('btnZoomReset');
const zoomLevel = document.getElementById('zoomLevel');
const searchSuggestions = document.getElementById('searchSuggestions');

// Viewer & Search State
let currentModalPdfPage = 1;
let currentZoom = 1.0;
let panX = 0;
let panY = 0;
let isPanning = false;
let startPanX = 0;
let startPanY = 0;
let allClassesData = [];
let allTechniquesData = [];
let debounceTimer = null;
let activeSuggestionIndex = -1;
let isStaticMode = window.location.hostname.includes('github.io') || 
                   window.location.protocol === 'file:' || 
                   (window.location.port !== '8000' && window.location.port !== '');

// Universal Data Loader (Supports both FastAPI backend & GitHub Pages static mode)
async function loadStaticOrApi(apiUrl, staticPath) {
  if (isStaticMode) {
    try {
      const res = await fetch(staticPath);
      if (res.ok) return await res.json();
    } catch (e) {
      console.warn(`Static load failed for ${staticPath}`, e);
    }
  } else {
    try {
      const res = await fetch(apiUrl);
      if (res.ok) return await res.json();
    } catch (e) {
      isStaticMode = true;
    }
  }
  const res2 = await fetch(staticPath);
  return await res2.json();
}

async function getAllTechniques() {
  if (allTechniquesData.length > 0) return allTechniquesData;
  try {
    allTechniquesData = await loadStaticOrApi('/api/techniques?limit=2000', 'data/techniques_catalog.json');
  } catch (e) {
    console.error('Failed to load techniques catalog:', e);
  }
  return allTechniquesData || [];
}

// Bone Anatomical Mappings for Skeleton Explorer
const BONE_MAPPINGS = {
  // Spine
  CervicalVertebrae: { nameVi: 'Cột sống cổ', nameEn: 'Cervical Vertebrae (C1-C7)', category: 'Spine', chapters: [37, 38, 43], approaches: 7 },
  l_Cervicle_Vertebrae: { nameVi: 'Cột sống cổ', nameEn: 'Cervical Vertebrae (C1-C7)', category: 'Spine', chapters: [37, 38, 43], approaches: 7 },
  ThoracicVertebrae: { nameVi: 'Cột sống ngực', nameEn: 'Thoracic Vertebrae (T1-T12)', category: 'Spine', chapters: [37, 39, 41, 42, 44], approaches: 8 },
  l_Thoracic_Vertebrae: { nameVi: 'Cột sống ngực', nameEn: 'Thoracic Vertebrae (T1-T12)', category: 'Spine', chapters: [37, 39, 41, 42, 44], approaches: 8 },
  LumbarVertebrae: { nameVi: 'Cột sống thắt lưng', nameEn: 'Lumbar Vertebrae (L1-L5)', category: 'Spine', chapters: [37, 39, 40, 41, 42, 44], approaches: 12 },
  l_Lumbar_Vertebrae: { nameVi: 'Cột sống thắt lưng', nameEn: 'Lumbar Vertebrae (L1-L5)', category: 'Spine', chapters: [37, 39, 40, 41, 42, 44], approaches: 12 },
  Sacrum: { nameVi: 'Xương cùng & Cột sống thắt lưng cùng', nameEn: 'Sacrum & Lumbosacral', category: 'Spine', chapters: [37, 40, 41], approaches: 5 },
  l_Sacrum: { nameVi: 'Xương cùng & Cột sống thắt lưng cùng', nameEn: 'Sacrum & Lumbosacral', category: 'Spine', chapters: [37, 40, 41], approaches: 5 },
  Coccyx: { nameVi: 'Xương cụt', nameEn: 'Coccyx', category: 'Spine', chapters: [37, 41], approaches: 2 },
  l_Coccyx: { nameVi: 'Xương cụt', nameEn: 'Coccyx', category: 'Spine', chapters: [37, 41], approaches: 2 },

  // Shoulder & Arm
  ClavicleLeft: { nameVi: 'Xương đòn', nameEn: 'Clavicle', category: 'Shoulder & Arm', chapters: [12, 46, 57], approaches: 6 },
  ClavicleRight: { nameVi: 'Xương đòn', nameEn: 'Clavicle', category: 'Shoulder & Arm', chapters: [12, 46, 57], approaches: 6 },
  l_Clavicle: { nameVi: 'Xương đòn', nameEn: 'Clavicle', category: 'Shoulder & Arm', chapters: [12, 46, 57], approaches: 6 },
  Scapula: { nameVi: 'Xương bả vai & Khớp vai', nameEn: 'Scapula & Glenohumeral Joint', category: 'Shoulder & Arm', chapters: [12, 13, 46, 47, 52], approaches: 18 },
  l_Scapula: { nameVi: 'Xương bả vai & Khớp vai', nameEn: 'Scapula & Glenohumeral Joint', category: 'Shoulder & Arm', chapters: [12, 13, 46, 47, 52], approaches: 18 },
  HumerusLeft: { nameVi: 'Xương cánh tay', nameEn: 'Humerus', category: 'Shoulder & Arm', chapters: [12, 46, 52, 57], approaches: 14 },
  HumerusRight: { nameVi: 'Xương cánh tay', nameEn: 'Humerus', category: 'Shoulder & Arm', chapters: [12, 46, 52, 57], approaches: 14 },
  l_Humerus: { nameVi: 'Xương cánh tay', nameEn: 'Humerus', category: 'Shoulder & Arm', chapters: [12, 46, 52, 57], approaches: 14 },

  // Elbow & Forearm
  RadiusLeft: { nameVi: 'Xương quay & Cẳng tay', nameEn: 'Radius & Forearm', category: 'Elbow & Forearm', chapters: [57, 74], approaches: 8 },
  RadiusRight: { nameVi: 'Xương quay & Cẳng tay', nameEn: 'Radius & Forearm', category: 'Elbow & Forearm', chapters: [57, 74], approaches: 8 },
  l_Radius: { nameVi: 'Xương quay & Cẳng tay', nameEn: 'Radius & Forearm', category: 'Elbow & Forearm', chapters: [57, 74], approaches: 8 },
  UlnaLeft: { nameVi: 'Xương trụ & Khớp khuỷu', nameEn: 'Ulna & Elbow Joint', category: 'Elbow & Forearm', chapters: [12, 13, 46, 52, 57, 74], approaches: 12 },
  UlnaRight: { nameVi: 'Xương trụ & Khớp khuỷu', nameEn: 'Ulna & Elbow Joint', category: 'Elbow & Forearm', chapters: [12, 13, 46, 52, 57, 74], approaches: 12 },
  l_Ulna: { nameVi: 'Xương trụ & Khớp khuỷu', nameEn: 'Ulna & Elbow Joint', category: 'Elbow & Forearm', chapters: [12, 13, 46, 52, 57, 74], approaches: 12 },

  // Hand & Wrist
  CarpalsLeft: { nameVi: 'Khối xương cổ tay', nameEn: 'Carpals (Scaphoid, Lunate, etc.)', category: 'Hand & Wrist', chapters: [67, 69, 73, 76], approaches: 10 },
  CarpalsRight: { nameVi: 'Khối xương cổ tay', nameEn: 'Carpals (Scaphoid, Lunate, etc.)', category: 'Hand & Wrist', chapters: [67, 69, 73, 76], approaches: 10 },
  l_Carpals: { nameVi: 'Khối xương cổ tay', nameEn: 'Carpals (Scaphoid, Lunate, etc.)', category: 'Hand & Wrist', chapters: [67, 69, 73, 76], approaches: 10 },
  MetacarpalsLeft: { nameVi: 'Xương đốt bàn tay', nameEn: 'Metacarpals', category: 'Hand & Wrist', chapters: [65, 66, 67, 71, 79], approaches: 15 },
  MetacarpalsRight: { nameVi: 'Xương đốt bàn tay', nameEn: 'Metacarpals', category: 'Hand & Wrist', chapters: [65, 66, 67, 71, 79], approaches: 15 },
  l_Metacarpals: { nameVi: 'Xương đốt bàn tay', nameEn: 'Metacarpals', category: 'Hand & Wrist', chapters: [65, 66, 67, 71, 79], approaches: 15 },
  PhalangesLeft: { nameVi: 'Xương đốt ngón tay', nameEn: 'Phalanges of Hand', category: 'Hand & Wrist', chapters: [19, 64, 65, 66, 67, 75, 79], approaches: 16 },
  PhalangesRight: { nameVi: 'Xương đốt ngón tay', nameEn: 'Phalanges of Hand', category: 'Hand & Wrist', chapters: [19, 64, 65, 66, 67, 75, 79], approaches: 16 },
  l_Phalanges: { nameVi: 'Xương đốt ngón tay', nameEn: 'Phalanges of Hand', category: 'Hand & Wrist', chapters: [19, 64, 65, 66, 67, 75, 79], approaches: 16 },

  // Pelvis & Hip
  PelvicGirdle: { nameVi: 'Khung chậu & Ổ cối', nameEn: 'Pelvic Girdle & Acetabulum', category: 'Hip & Pelvis', chapters: [3, 4, 5, 6, 30, 55, 56], approaches: 22 },
  l_Pelvic_Girdle: { nameVi: 'Khung chậu & Ổ cối', nameEn: 'Pelvic Girdle & Acetabulum', category: 'Hip & Pelvis', chapters: [3, 4, 5, 6, 30, 55, 56], approaches: 22 },
  FemurRight: { nameVi: 'Xương đùi & Khớp háng', nameEn: 'Femur & Hip Joint', category: 'Hip & Pelvis', chapters: [3, 4, 5, 6, 54, 55], approaches: 26 },
  FemurLeft: { nameVi: 'Xương đùi & Khớp háng', nameEn: 'Femur & Hip Joint', category: 'Hip & Pelvis', chapters: [3, 4, 5, 6, 54, 55], approaches: 26 },
  l_Femur: { nameVi: 'Xương đùi & Khớp háng', nameEn: 'Femur & Hip Joint', category: 'Hip & Pelvis', chapters: [3, 4, 5, 6, 54, 55], approaches: 26 },

  // Knee & Leg
  PatellaLeft: { nameVi: 'Xương bánh chè & Khớp gối', nameEn: 'Patella & Knee Extensor Mechanism', category: 'Knee & Lower Leg', chapters: [7, 8, 9, 45, 51, 54], approaches: 16 },
  PatellaRight: { nameVi: 'Xương bánh chè & Khớp gối', nameEn: 'Patella & Knee Extensor Mechanism', category: 'Knee & Lower Leg', chapters: [7, 8, 9, 45, 51, 54], approaches: 16 },
  l_Patella: { nameVi: 'Xương bánh chè & Khớp gối', nameEn: 'Patella & Knee Extensor Mechanism', category: 'Knee & Lower Leg', chapters: [7, 8, 9, 45, 51, 54], approaches: 16 },
  TibiaLeft: { nameVi: 'Xương chày (Mâm chày, Thân chày)', nameEn: 'Tibia (Plateau, Shaft)', category: 'Knee & Lower Leg', chapters: [7, 8, 9, 45, 51, 54], approaches: 18 },
  TibiaRight: { nameVi: 'Xương chày (Mâm chày, Thân chày)', nameEn: 'Tibia (Plateau, Shaft)', category: 'Knee & Lower Leg', chapters: [7, 8, 9, 45, 51, 54], approaches: 18 },
  l_Tibia: { nameVi: 'Xương chày (Mâm chày, Thân chày)', nameEn: 'Tibia (Plateau, Shaft)', category: 'Knee & Lower Leg', chapters: [7, 8, 9, 45, 51, 54], approaches: 18 },
  FibulaLeft: { nameVi: 'Xương mác & Chỏm mác', nameEn: 'Fibula & Fibular Head', category: 'Knee & Lower Leg', chapters: [1, 54, 89], approaches: 8 },
  FibulaRight: { nameVi: 'Xương mác & Chỏm mác', nameEn: 'Fibula & Fibular Head', category: 'Knee & Lower Leg', chapters: [1, 54, 89], approaches: 8 },
  l_Fibula: { nameVi: 'Xương mác & Chỏm mác', nameEn: 'Fibula & Fibular Head', category: 'Knee & Lower Leg', chapters: [1, 54, 89], approaches: 8 },

  // Foot & Ankle
  TarsalsLeft: { nameVi: 'Cổ chân & Khối xương cổ chân', nameEn: 'Tarsals (Talus, Calcaneus, Navicular)', category: 'Foot & Ankle', chapters: [10, 11, 50, 84, 88, 89], approaches: 24 },
  TarsalsRight: { nameVi: 'Cổ chân & Khối xương cổ chân', nameEn: 'Tarsals (Talus, Calcaneus, Navicular)', category: 'Foot & Ankle', chapters: [10, 11, 50, 84, 88, 89], approaches: 24 },
  l_Tarsals: { nameVi: 'Cổ chân & Khối xương cổ chân', nameEn: 'Tarsals (Talus, Calcaneus, Navicular)', category: 'Foot & Ankle', chapters: [10, 11, 50, 84, 88, 89], approaches: 24 },
  MetatarsalsLeft: { nameVi: 'Xương đốt bàn chân & Khớp Lisfranc', nameEn: 'Metatarsals & Midfoot', category: 'Foot & Ankle', chapters: [81, 82, 83, 84, 88], approaches: 14 },
  MetatarsalsRight: { nameVi: 'Xương đốt bàn chân & Khớp Lisfranc', nameEn: 'Metatarsals & Midfoot', category: 'Foot & Ankle', chapters: [81, 82, 83, 84, 88], approaches: 14 },
  l_Metatarsals: { nameVi: 'Xương đốt bàn chân & Khớp Lisfranc', nameEn: 'Metatarsals & Midfoot', category: 'Foot & Ankle', chapters: [81, 82, 83, 84, 88], approaches: 14 },
  PhalangesFootLeft: { nameVi: 'Xương đốt ngón chân (Ngón cái & các ngón nhỏ)', nameEn: 'Phalanges of Foot (Hallux & Lesser Toes)', category: 'Foot & Ankle', chapters: [15, 81, 83, 87, 88], approaches: 12 },
  PhalangesFootRight: { nameVi: 'Xương đốt ngón chân (Ngón cái & các ngón nhỏ)', nameEn: 'Phalanges of Foot (Hallux & Lesser Toes)', category: 'Foot & Ankle', chapters: [15, 81, 83, 87, 88], approaches: 12 },
  l_PhalangesFoot: { nameVi: 'Xương đốt ngón chân (Ngón cái & các ngón nhỏ)', nameEn: 'Phalanges of Foot (Hallux & Lesser Toes)', category: 'Foot & Ankle', chapters: [15, 81, 83, 87, 88], approaches: 12 },

  // Skull & Thorax
  Skull: { nameVi: 'Hộp sọ & Khối xương sọ mặt', nameEn: 'Skull & Craniofacial', category: 'Approaches & General Principles', chapters: [1, 37], approaches: 4 },
  Cranium: { nameVi: 'Vòm sọ & Khớp đội chẩm', nameEn: 'Cranium & Occipitocervical Junction', category: 'Spine', chapters: [37, 43], approaches: 3 },
  Mandible: { nameVi: 'Xương hàm dưới (Đường mổ xuyên miệng/cắt hàm)', nameEn: 'Mandible (Transmandibular/Transoral)', category: 'Spine', chapters: [37], approaches: 2 },
  Sternum: { nameVi: 'Xương ức (Đường mổ mở xương ức tiếp cận cột sống)', nameEn: 'Sternum (Transsternal Approach)', category: 'Spine', chapters: [37], approaches: 3 },
  Manubrium: { nameVi: 'Cán xương ức', nameEn: 'Manubrium', category: 'Spine', chapters: [37], approaches: 2 },
  l_Ribs: { nameVi: 'Khung xương sườn & Lồng ngực', nameEn: 'Ribs & Thoracic Cage', category: 'Spine', chapters: [37, 44], approaches: 5 }
};

document.addEventListener('DOMContentLoaded', async () => {
  setupEventListeners();

  // Detect sub-portal region
  const path = window.location.pathname.toLowerCase();
  let initialRegion = 'all';
  if (document.body.dataset.portal) {
    initialRegion = document.body.dataset.portal;
  } else if (path.includes('chi-duoi')) {
    initialRegion = 'lower';
  } else if (path.includes('chi-tren')) {
    initialRegion = 'upper';
  } else if (path.includes('cot-song')) {
    initialRegion = 'spine-pelvis';
  } else if (path.includes('dai-cuong')) {
    initialRegion = 'general';
  }

  if (initialRegion !== 'all') {
    currentPortal = initialRegion;
    currentClassifRegion = initialRegion;
    if (classifFilterPills) {
      const pills = classifFilterPills.querySelectorAll('.pill-btn');
      pills.forEach(p => {
        if (p.dataset.filter === initialRegion) {
          p.classList.add('active');
        } else {
          p.classList.remove('active');
        }
      });
    }
  }

  try {
    await loadAllClassificationsCache();
    renderAllClassificationsDirectory('', currentClassifRegion);
  } catch (e) {
    console.error('Failed to load classifications:', e);
  }

  // Pre-load supporting metadata in background without blocking initial render
  setTimeout(async () => {
    try { await loadCategories(); } catch (e) {}
    try { await loadAuthors(); } catch (e) {}
  }, 350);
});

// Setup Events
function setupEventListeners() {
  // Navigation Tabs
  navTabs.forEach(btn => {
    btn.addEventListener('click', () => {
      const tab = btn.dataset.tab;
      switchTab(tab);
    });
  });

  // All Classifications Directory Search Input
  let classifDebounce = null;
  if (classifSearchInput) {
    classifSearchInput.addEventListener('input', () => {
      clearTimeout(classifDebounce);
      classifDebounce = setTimeout(() => {
        renderAllClassificationsDirectory(classifSearchInput.value, currentClassifRegion);
      }, 120);
    });
  }

  // All Classifications Directory Region Filter Pills
  if (classifFilterPills) {
    const pills = classifFilterPills.querySelectorAll('.pill-btn');
    pills.forEach(p => {
      p.addEventListener('click', () => {
        pills.forEach(b => b.classList.remove('active'));
        p.classList.add('active');
        currentClassifRegion = p.dataset.filter || 'all';
        renderAllClassificationsDirectory(classifSearchInput ? classifSearchInput.value : '', currentClassifRegion);
      });
    });
  }

  // Quick Search Chips in Hero
  const quickChips = document.querySelectorAll('.search-quick-chip');
  quickChips.forEach(chip => {
    chip.addEventListener('click', () => {
      const q = chip.dataset.q;
      if (globalSearch) globalSearch.value = q;
      performSearch(q);
    });
  });

  // Global Search
  searchBtn.addEventListener('click', () => performSearch());
  globalSearch.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') performSearch();
  });

  // Autocomplete Suggestions on Input for Global Search
  globalSearch.addEventListener('input', () => {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(handleSearchAutocomplete, 180);
  });

  globalSearch.addEventListener('keydown', (e) => {
    if (!searchSuggestions || searchSuggestions.style.display === 'none') return;
    const items = searchSuggestions.querySelectorAll('.suggestion-item');
    if (items.length === 0) return;

    if (e.key === 'ArrowDown') {
      e.preventDefault();
      activeSuggestionIndex = (activeSuggestionIndex + 1) % items.length;
      updateActiveSuggestion(items);
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      activeSuggestionIndex = (activeSuggestionIndex - 1 + items.length) % items.length;
      updateActiveSuggestion(items);
    } else if (e.key === 'Enter') {
      if (activeSuggestionIndex >= 0 && activeSuggestionIndex < items.length) {
        e.preventDefault();
        items[activeSuggestionIndex].click();
      }
    } else if (e.key === 'Escape') {
      closeSuggestions();
    }
  });

  // Click outside to close search suggestions
  document.addEventListener('click', (e) => {
    if (!e.target.closest('.search-bar-wrap')) {
      closeSuggestions();
    }
    if (techniqueSearch && techniqueSuggestions && !e.target.closest('#techniqueSearch') && !e.target.closest('#techniqueSuggestions')) {
      closeTechniqueSuggestions();
    }
  });

  // Filters
  categoryFilter.addEventListener('change', (e) => {
    currentCategory = e.target.value;
    currentPage = 1;
    loadTechniques();
  });

  chapterFilter.addEventListener('change', (e) => {
    currentChapter = e.target.value;
    currentPage = 1;
    loadTechniques();
  });

  if (authorFilter) {
    authorFilter.addEventListener('change', (e) => {
      currentAuthor = e.target.value;
      currentPage = 1;
      loadTechniques();
    });
  }

  // Technique Catalog Live Search & Autocomplete
  if (techniqueSearch) {
    techniqueSearch.addEventListener('input', () => {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(handleTechniqueSearchAutocomplete, 180);
    });

    techniqueSearch.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') {
        closeTechniqueSuggestions();
        const val = techniqueSearch.value.trim();
        performSearch(val);
      }
    });
  }

  // Modal Close
  modalCloseBtn.addEventListener('click', () => {
    techModal.classList.remove('active');
  });

  techModal.addEventListener('click', (e) => {
    if (e.target === techModal) {
      techModal.classList.remove('active');
    }
  });

  // Modal Tabs
  modalTabs.forEach(btn => {
    btn.addEventListener('click', () => {
      modalTabs.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const tab = btn.dataset.modaltab;
      if (tab === 'pagePreview') {
        tabContentPagePreview.style.display = 'flex';
        tabContentExtractedText.style.display = 'none';
      } else {
        tabContentPagePreview.style.display = 'none';
        tabContentExtractedText.style.display = 'block';
      }
    });
  });

  // Global Keyboard Shortcuts
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      if (techModal && techModal.classList.contains('active')) {
        techModal.classList.remove('active');
      }
      closeImageLightbox();
    }
  });

  // Skeleton Panel Subtabs (if present)
  if (tabBtnClassifications) {
    tabBtnClassifications.addEventListener('click', () => {
      tabBtnClassifications.classList.add('active');
      if (tabBtnTechs) tabBtnTechs.classList.remove('active');
      if (skeletonClassificationsContainer) skeletonClassificationsContainer.style.display = 'block';
      if (skeletonTechsContainer) skeletonTechsContainer.style.display = 'none';
    });
  }

  if (tabBtnTechs) {
    tabBtnTechs.addEventListener('click', () => {
      tabBtnTechs.classList.add('active');
      if (tabBtnClassifications) tabBtnClassifications.classList.remove('active');
      if (skeletonClassificationsContainer) skeletonClassificationsContainer.style.display = 'none';
      if (skeletonTechsContainer) skeletonTechsContainer.style.display = 'block';
    });
  }

  // Skeleton View All Button (if present)
  if (btnViewAllBoneTechs) {
    btnViewAllBoneTechs.addEventListener('click', () => {
      if (currentBoneSelection && currentBoneSelection.category) {
        categoryFilter.value = currentBoneSelection.category;
        currentCategory = currentBoneSelection.category;
        currentPage = 1;
        switchTab('techniques');
        loadTechniques();
      }
    });
  }
}

let techniquesLoaded = false;
let chaptersLoaded = false;

function switchTab(tabName) {
  currentTab = tabName;
  navTabs.forEach(btn => {
    btn.classList.toggle('active', btn.dataset.tab === tabName);
  });
  viewSections.forEach(section => {
    section.classList.toggle('active', section.id === `view-${tabName}`);
  });

  if (tabName === 'techniques') {
    if (!techniquesLoaded) {
      techniquesLoaded = true;
      loadTechniques();
    }
  } else if (tabName === 'chapters') {
    if (!chaptersLoaded || (chaptersGrid && chaptersGrid.children.length === 0)) {
      chaptersLoaded = true;
      loadChapters();
    }
  } else if (tabName === 'outline') {
    if (outlineContainer && outlineContainer.children.length === 0) {
      loadOutline();
    }
  }
}

async function performSearch(customQuery) {
  closeSuggestions();
  closeTechniqueSuggestions();
  const rawQ = (typeof customQuery === 'string' ? customQuery : (globalSearch ? globalSearch.value : '')).trim();
  if (!rawQ) {
    searchQuery = '';
    currentPage = 1;
    techniquesLoaded = true;
    switchTab('techniques');
    loadTechniques();
    return;
  }

  const normQuery = normalizeStr(rawQ);

  // Check if query matches a fracture classification (e.g. Schatzker, Garden, Gustilo, Denis, AO/OTA...)
  const matchedClass = allClassesData.find(c => {
    const idNorm = normalizeStr(c.id);
    const nameNorm = normalizeStr(c.name);
    const enNameNorm = normalizeStr(c.en_name);
    return idNorm === normQuery ||
           nameNorm.includes(normQuery) ||
           enNameNorm.includes(normQuery) ||
           (normQuery.length >= 3 && (idNorm.includes(normQuery) || normQuery.includes(idNorm)));
  });

  if (matchedClass) {
    scrollToClassification(matchedClass.id);
    return;
  }

  // Otherwise, standard techniques search
  searchQuery = rawQ;
  currentPage = 1;
  techniquesLoaded = true;
  switchTab('techniques');
  loadTechniques();
}

function scrollToClassification(classifId) {
  switchTab('categories');
  const matchedClass = allClassesData.find(c => c.id === classifId);
  const searchTerm = matchedClass ? matchedClass.name : '';
  if (classifSearchInput) classifSearchInput.value = searchTerm;
  renderAllClassificationsDirectory(searchTerm, 'all');
  setTimeout(() => {
    const card = document.getElementById(`all-classif-${classifId}`);
    if (card) {
      card.scrollIntoView({ behavior: 'smooth', block: 'center' });
      card.style.transition = 'all 0.3s ease';
      card.style.borderColor = '#0284c7';
      card.style.boxShadow = '0 0 0 3px rgba(2, 132, 199, 0.4)';
      setTimeout(() => {
        card.style.borderColor = '';
        card.style.boxShadow = '';
      }, 3500);
    }
  }, 120);
}

// ----------------- SKELETON EXPLORER -----------------
async function initSkeletonExplorer() {
  try {
    let svgText = '';
    const svgPaths = ['web/static/human_skeleton.svg', '/static/human_skeleton.svg', 'human_skeleton.svg'];
    for (const p of svgPaths) {
      try {
        const res = await fetch(p);
        if (res.ok) {
          svgText = await res.text();
          if (svgText && svgText.includes('<svg')) break;
        }
      } catch (e) {}
    }
    if (!svgText) throw new Error('Không thể tải file human_skeleton.svg');
    skeletonSvgBox.innerHTML = svgText;

    const svg = skeletonSvgBox.querySelector('svg');
    if (!svg) return;

    // Attach interactivity to known bone groups
    Object.keys(BONE_MAPPINGS).forEach(id => {
      const el = svg.getElementById(id);
      if (el) {
        el.classList.add('bone-interactive');
        el.style.cursor = 'pointer';

        el.addEventListener('mouseenter', (e) => {
          const info = BONE_MAPPINGS[id];
          skeletonHoverTag.textContent = `${info.nameVi} (${info.nameEn})`;
          showTooltip(e, `${info.nameVi} • ${info.category}`);
          el.classList.add('hovered');
        });

        el.addEventListener('mousemove', (e) => {
          moveTooltip(e);
        });

        el.addEventListener('mouseleave', () => {
          hideTooltip();
          el.classList.remove('hovered');
          if (!currentBoneSelection) {
            skeletonHoverTag.textContent = 'Toàn thân';
          } else {
            skeletonHoverTag.textContent = `${currentBoneSelection.nameVi}`;
          }
        });

        el.addEventListener('click', () => {
          selectBone(id, BONE_MAPPINGS[id]);
        });
      }
    });

    // Select Knee by default as a great initial showcase
    selectBone('PatellaLeft', BONE_MAPPINGS['PatellaLeft']);

  } catch (err) {
    console.error('Failed to init skeleton SVG:', err);
    skeletonSvgBox.innerHTML = '<div style="color: red; padding: 2rem;">Lỗi tải sơ đồ khung xương.</div>';
  }
}

function showTooltip(e, text) {
  skeletonTooltip.textContent = text;
  skeletonTooltip.style.display = 'block';
  moveTooltip(e);
}

function moveTooltip(e) {
  const rect = skeletonExplorerContainer.getBoundingClientRect();
  const x = e.clientX - rect.left;
  const y = e.clientY - rect.top;
  skeletonTooltip.style.left = `${x}px`;
  skeletonTooltip.style.top = `${y}px`;
}

function hideTooltip() {
  skeletonTooltip.style.display = 'none';
}

async function selectBone(id, boneInfo) {
  currentBoneSelection = boneInfo;

  // Highlight active SVG element
  const svg = skeletonSvgBox.querySelector('svg');
  if (svg) {
    svg.querySelectorAll('.bone-interactive.selected').forEach(el => el.classList.remove('selected'));
    const target = svg.getElementById(id);
    if (target) target.classList.add('selected');
  }

  // Update UI Card
  selectedBoneName.innerHTML = `🦴 ${boneInfo.nameVi}`;
  selectedBoneEn.textContent = `${boneInfo.nameEn} • Chuyên khoa: ${boneInfo.category}`;
  statBoneChapters.textContent = boneInfo.chapters ? boneInfo.chapters.length : 'N/A';
  statBoneApproaches.textContent = boneInfo.approaches || '10+';
  skeletonHoverTag.textContent = `${boneInfo.nameVi}`;

  // Load Classifications first (Guidemap feature)
  await loadBoneClassifications(id, boneInfo);

  // Load Sample Techniques
  boneTechListTitle.textContent = `Các kỹ thuật mổ tiêu biểu cho ${boneInfo.nameVi}`;
  skeletonSampleGrid.innerHTML = '<div style="padding: 1rem; color: var(--text-muted);">Đang tải kỹ thuật...</div>';

  try {
    let data = null;
    if (!isStaticMode) {
      try {
        const params = new URLSearchParams({
          category: boneInfo.category,
          limit: 6
        });
        const res = await fetch(`/api/techniques?${params.toString()}`);
        if (res.ok) data = await res.json();
      } catch (e) {
        isStaticMode = true;
      }
    }

    if (!data) {
      const all = await getAllTechniques();
      const filtered = all.filter(t => (t.categories && t.categories.includes(boneInfo.category)) || t.category === boneInfo.category);
      data = {
        total: filtered.length,
        items: filtered.slice(0, 6)
      };
    }

    statBoneTechs.textContent = data.total;
    boneTechSampleCount.textContent = `Hiển thị ${Math.min(6, data.items.length)} / ${data.total} kỹ thuật`;

    skeletonSampleGrid.innerHTML = '';
    data.items.forEach(tech => {
      const card = document.createElement('div');
      card.className = 'tech-card';
      card.innerHTML = `
        <div>
          <div class="tech-header">
            <span class="tech-code">TECHNIQUE ${tech.tech_id}</span>
            <span class="badge" style="font-size: 0.75rem;">Chương ${tech.chapter}</span>
          </div>
          <h4 class="tech-name" style="font-size: 0.95rem;">${tech.name}</h4>
          ${tech.author ? `<div class="tech-author" style="font-size: 0.8rem;">👨‍⚕️ ${tech.author}</div>` : ''}
          <div class="tech-chapter" style="font-size: 0.75rem;">📖 Ch.${tech.chapter}: ${tech.chapter_title}</div>
        </div>
        <div class="tech-footer">
          <span style="font-size: 0.75rem; color: var(--primary); font-weight: 600;">Campbell 13th Ed</span>
          <button class="view-btn" style="font-size: 0.75rem; padding: 0.25rem 0.6rem;">Xem chi tiết &rarr;</button>
        </div>
      `;
      card.addEventListener('click', () => openTechniqueModal(tech.tech_id));
      skeletonSampleGrid.appendChild(card);
    });
  } catch (err) {
    console.error('Failed to load bone sample techniques:', err);
    skeletonSampleGrid.innerHTML = '<div style="color: red; padding: 1rem;">Lỗi tải kỹ thuật mẫu.</div>';
  }
}

// Load and Render Bone Classifications
async function loadBoneClassifications(id, boneInfo) {
  try {
    skeletonClassificationsContainer.innerHTML = '<div style="padding: 1rem; color: var(--text-muted);">Đang tải bảng phân loại gãy xương...</div>';
    
    let data = null;
    if (!isStaticMode) {
      try {
        let res = await fetch(`/api/classifications?bone=${id}`);
        if (res.ok) data = await res.json();

        // If no direct bone match, try by category
        if (data && data.length === 0 && boneInfo.category) {
          const resCat = await fetch(`/api/classifications?category=${encodeURIComponent(boneInfo.category)}`);
          if (resCat.ok) data = await resCat.json();
        }
      } catch (e) {
        isStaticMode = true;
      }
    }

    if (!data) {
      if (allClassesData.length === 0) {
        allClassesData = await loadStaticOrApi('/api/classifications', 'data/fracture_classifications.json');
      }
      data = allClassesData.filter(c => c.bone === id || c.bone_id === id || (c.bones && c.bones.includes(id)));
      if (data.length === 0 && boneInfo.category) {
        data = allClassesData.filter(c => c.category === boneInfo.category);
      }
    }

    statBoneClassifications.textContent = data.length;

    if (data.length === 0) {
      skeletonClassificationsContainer.innerHTML = `
        <div style="background: #f8fafc; border: 1px dashed var(--border); border-radius: 12px; padding: 1.5rem; text-align: center; color: var(--text-muted);">
          <p style="font-weight: 600; font-size: 1rem;">Chưa có bảng phân loại gãy chuyên biệt cho vị trí ${boneInfo.nameVi}</p>
          <p style="font-size: 0.85rem; margin-top: 0.5rem;">Hãy chuyển sang tab "🔪 Kỹ thuật mổ tiêu biểu" để xem các phẫu thuật liên quan đến vùng giải phẫu này.</p>
        </div>
      `;
      return;
    }

    skeletonClassificationsContainer.innerHTML = '';

    data.forEach(item => {
      const card = document.createElement('div');
      card.className = 'classification-card';
      card.id = `classification-${item.id}`;

      // Types list HTML
      const typesHtml = (item.types || []).map(t => {
        const typeCode = t.code || t.type || '';
        const typeName = t.name || '';
        const typeDesc = t.desc || t.description || '';
        const typeMgmt = t.management || t.principles || '';
        const techId = t.technique_id || '';
        const btnLabel = t.button_label || (techId ? `Xem Kỹ thuật ${techId} (${t.technique_title || ''})` : '');

        return `
          <div class="type-item">
            <div class="type-item-header">
              <span class="type-code">📌 ${typeCode}</span>
              ${typeName ? `<strong style="color: var(--dark); font-size: 0.9rem;">${typeName}</strong>` : ''}
            </div>
            ${typeDesc ? `<div class="type-desc" style="line-height: 1.4; color: #334155;">${typeDesc}</div>` : ''}
            ${typeMgmt ? `<div class="type-management" style="margin-top: 0.35rem;">⚡ Chỉ định & Xử trí: ${typeMgmt}</div>` : ''}
            ${techId ? `
              <div class="type-action-row" style="margin-top: 0.5rem;">
                <button class="type-tech-btn" onclick="openTechniqueModal('${techId}')" title="Mở trang phẫu thuật High-DPI trong Campbell">
                  🔪 ${btnLabel} &rarr;
                </button>
              </div>
            ` : ''}
          </div>
        `;
      }).join('');

      // Techniques pills HTML
      const techsHtml = (item.techniques || []).map(t_id => `
        <button class="tech-tag-btn" onclick="openTechniqueModal('${t_id}')">🔪 Kỹ thuật ${t_id}</button>
      `).join('');

      card.innerHTML = `
        <div class="classification-header">
          <div class="classification-title">
            <h4>${item.name}</h4>
            <span>${item.en_name} • Vị trí: ${item.bone_vi}</span>
          </div>
          <button class="view-btn classif-protocol-btn" onclick="openClassificationProtocol('${item.id}')">
            📋 Phác đồ & Quy trình &rarr;
          </button>
        </div>
        ${item.image_url ? `
          <div class="classif-image-wrap">
            <img src="${item.image_url}" alt="${escapeHtml(item.name)}" class="classif-main-img" loading="lazy" data-img-url="${item.image_url}" data-caption="${escapeHtml(item.name + ' - Sơ đồ giải phẫu & hướng phẫu thuật Campbell')}" onclick="openImageLightbox(this.dataset.imgUrl || this.src, this.dataset.caption)">
            <div class="image-caption">🔍 Sơ đồ phân loại chuẩn Campbell • Nhấn để phóng to</div>
          </div>
        ` : ''}
        <p class="classification-desc">${item.description}</p>
        <div class="classification-types">
          ${typesHtml}
        </div>
        ${techsHtml ? `
          <div class="classification-techniques">
            <span>KỸ THUẬT MỔ CHỈ ĐỊNH (CAMPBELL):</span>
            ${techsHtml}
          </div>
        ` : ''}
      `;

      skeletonClassificationsContainer.appendChild(card);
    });

  } catch (err) {
    console.error('Failed to load bone classifications:', err);
    skeletonClassificationsContainer.innerHTML = '<div style="color: red; padding: 1rem;">Lỗi tải phân loại gãy xương.</div>';
  }
}

// ----------------- STANDARD LOADERS -----------------

// Load Categories
async function loadCategories() {
  try {
    categoriesData = await loadStaticOrApi('/api/categories', 'data/anatomical_categories.json');

    // Convert object map to array if in static mode
    if (categoriesData && !Array.isArray(categoriesData) && typeof categoriesData === 'object') {
      categoriesData = Object.entries(categoriesData).map(([id, cat]) => ({
        id: id,
        vi: cat.vi || id,
        icon: cat.icon || '🦴',
        chapters: cat.chapters || [],
        chapter_count: (cat.chapters || []).length,
        technique_count: 0
      }));
    }

    if (!Array.isArray(categoriesData)) categoriesData = [];

    // Populate category dropdown
    if (categoryFilter) {
      const portalChaps = (currentPortal && currentPortal !== 'all' && PORTAL_SPECS[currentPortal]) ? new Set(PORTAL_SPECS[currentPortal].chapters) : null;
      categoryFilter.innerHTML = '<option value="">Tất cả vùng giải phẫu</option>';
      categoriesData.forEach(cat => {
        if (portalChaps && !(cat.chapters || []).some(c => portalChaps.has(c))) return;
        const opt = document.createElement('option');
        opt.value = cat.id;
        opt.textContent = `${cat.icon} ${cat.vi}` + (cat.technique_count ? ` (${cat.technique_count} kỹ thuật)` : '');
        categoryFilter.appendChild(opt);
      });
    }

    // Render Categories Grid if element exists
    if (categoriesGrid) {
      categoriesGrid.innerHTML = '';
      categoriesData.forEach(cat => {
        const card = document.createElement('div');
        card.className = 'category-card';
        card.innerHTML = `
          <div>
            <div class="cat-top">
              <div class="cat-icon">${cat.icon}</div>
              <div class="cat-title">
                <h3>${cat.vi}</h3>
                <span>${cat.id}</span>
              </div>
            </div>
            <p style="font-size: 0.85rem; color: var(--text-muted); margin-top: 0.5rem;">
              Bao gồm các chương: ${(cat.chapters || []).map(c => `Ch.${c}`).join(', ')}
            </p>
          </div>
          <div class="cat-meta">
            <span class="badge badge-chapter">📚 ${cat.chapter_count} Chương</span>
            ${cat.technique_count ? `<span class="badge">🔪 ${cat.technique_count} Kỹ thuật mổ</span>` : ''}
          </div>
        `;
        card.addEventListener('click', () => {
          if (categoryFilter) categoryFilter.value = cat.id;
          currentCategory = cat.id;
          currentPage = 1;
          switchTab('techniques');
          loadTechniques();
        });
        categoriesGrid.appendChild(card);
      });
    }
  } catch (err) {
    console.error('Failed to load categories:', err);
  }
}

// Load Chapters
async function loadChapters() {
  try {
    chaptersData = await loadStaticOrApi('/api/chapters', 'data/chapters_catalog.json');

    const portalChaps = (currentPortal && currentPortal !== 'all' && PORTAL_SPECS[currentPortal]) ? PORTAL_SPECS[currentPortal].chapters : null;
    chapterFilter.innerHTML = portalChaps ? `<option value="">Tất cả chương chuyên khoa (${portalChaps.length} chương)</option>` : '<option value="">Tất cả chương sách (1-89)</option>';
    chaptersGrid.innerHTML = '';

    chaptersData.forEach(chap => {
      if (portalChaps && !portalChaps.includes(chap.chapter)) return;
      const opt = document.createElement('option');
      opt.value = chap.chapter;
      opt.textContent = `Chương ${chap.chapter}: ${chap.title} (${chap.technique_count} KT)`;
      chapterFilter.appendChild(opt);

      const card = document.createElement('div');
      card.className = 'tech-card';
      card.innerHTML = `
        <div>
          <div class="tech-header">
            <span class="tech-code">CHƯƠNG ${chap.chapter}</span>
            <span class="badge" style="font-size: 0.75rem;">${chap.technique_count} Kỹ thuật</span>
          </div>
          <h3 class="tech-name">${chap.title}</h3>
          <div style="display: flex; gap: 0.35rem; flex-wrap: wrap; margin-bottom: 0.75rem;">
            ${(chap.categories || []).map(c => `<span class="badge badge-chapter">${c.icon} ${c.vi}</span>`).join('')}
          </div>
        </div>
        <div class="tech-footer">
          <span>🔪 <strong>${chap.technique_count}</strong> kỹ thuật mổ</span>
          <button class="view-btn">Xem kỹ thuật &rarr;</button>
        </div>
      `;
      card.addEventListener('click', () => {
        chapterFilter.value = chap.chapter;
        currentChapter = chap.chapter;
        currentPage = 1;
        switchTab('techniques');
        loadTechniques();
      });
      chaptersGrid.appendChild(card);
    });
  } catch (err) {
    console.error('Failed to load chapters:', err);
  }
}

// Load Authors for Filter Dropdown
async function loadAuthors() {
  if (!authorFilter) return;
  try {
    const authors = await loadStaticOrApi('/api/authors', 'web/static/authors.json');
    authorFilter.innerHTML = '<option value="">Tất cả tác giả phẫu thuật</option>';
    if (Array.isArray(authors)) {
      authors.forEach(auth => {
        const opt = document.createElement('option');
        opt.value = auth;
        opt.textContent = `👨‍⚕️ ${auth}`;
        authorFilter.appendChild(opt);
      });
    }
  } catch (err) {
    console.error('Failed to load authors:', err);
  }
}

// Load Techniques with filters
async function loadTechniques() {
  try {
    techResultCount.textContent = 'Đang tìm kiếm...';
    techniquesGrid.innerHTML = '<div style="padding: 2rem; color: var(--text-muted); grid-column: 1/-1;">Đang tải danh sách kỹ thuật...</div>';

    let data = null;
    const params = new URLSearchParams({
      page: currentPage,
      limit: 24
    });
    if (searchQuery) params.append('q', searchQuery);
    if (currentCategory) params.append('category', currentCategory);
    if (currentChapter) params.append('chapter', currentChapter);
    if (currentAuthor) params.append('author', currentAuthor);
    if (currentPortal && currentPortal !== 'all') params.append('portal', currentPortal);

    if (!isStaticMode) {
      try {
        const res = await fetch(`/api/techniques?${params.toString()}`);
        if (res.ok) data = await res.json();
      } catch (e) {
        isStaticMode = true;
      }
    }

    if (!data) {
      const all = await getAllTechniques();
      let filtered = all;
      if (currentPortal && currentPortal !== 'all' && PORTAL_SPECS[currentPortal]) {
        const portalChaps = PORTAL_SPECS[currentPortal].chapters;
        filtered = filtered.filter(t => portalChaps.includes(t.chapter));
      }
      if (currentCategory) {
        filtered = filtered.filter(t => (t.categories && t.categories.includes(currentCategory)) || t.category === currentCategory);
      }
      if (currentChapter) {
        filtered = filtered.filter(t => String(t.chapter) === String(currentChapter));
      }
      if (currentAuthor) {
        filtered = filtered.filter(t => t.author && t.author.toLowerCase().includes(currentAuthor.toLowerCase()));
      }
      if (searchQuery) {
        const normQ = normalizeStr(searchQuery);
        filtered = filtered.filter(t => {
          return (
            t.tech_id.toLowerCase().includes(normQ) ||
            normalizeStr(t.name).includes(normQ) ||
            (t.author && normalizeStr(t.author).includes(normQ)) ||
            (t.chapter_title && normalizeStr(t.chapter_title).includes(normQ))
          );
        });
      }
      const limit = 24;
      const total = filtered.length;
      const pages = Math.ceil(total / limit) || 1;
      const page = Math.min(Math.max(currentPage, 1), pages);
      const start = (page - 1) * limit;
      const items = filtered.slice(start, start + limit);
      data = { total, page, pages, items };
    }

    techResultCount.textContent = `Tìm thấy ${data.total} kỹ thuật mổ (Trang ${data.page}/${data.pages || 1})`;
    techniquesGrid.innerHTML = '';

    if (data.items.length === 0) {
      techniquesGrid.innerHTML = `
        <div style="padding: 3rem; text-align: center; color: var(--text-muted); grid-column: 1/-1;">
          <p style="font-size: 1.2rem;">Không tìm thấy kỹ thuật phù hợp với từ khóa "${searchQuery}"</p>
          <p style="margin-top: 0.5rem;">Hãy thử xóa bớt bộ lọc hoặc gõ tên tác giả, tên phẫu thuật khác.</p>
        </div>
      `;
      techPagination.innerHTML = '';
      return;
    }

    data.items.forEach(tech => {
      const card = document.createElement('div');
      card.className = 'tech-card';
      card.innerHTML = `
        <div>
          <div class="tech-header">
            <span class="tech-code">TECHNIQUE ${tech.tech_id}</span>
            <span class="badge" style="font-size: 0.75rem;">Chương ${tech.chapter}</span>
          </div>
          <h3 class="tech-name">${tech.name}</h3>
          ${tech.author ? `<div class="tech-author">👨‍⚕️ Tác giả / Tên định danh: ${tech.author}</div>` : ''}
          <div class="tech-chapter">📖 Chương ${tech.chapter}: ${tech.chapter_title}</div>
        </div>
        <div class="tech-footer">
          <span style="font-size: 0.85rem; color: var(--primary); font-weight: 600;">Campbell 13th Ed</span>
          <button class="view-btn">Xem chi tiết quy trình &rarr;</button>
        </div>
      `;
      card.addEventListener('click', () => openTechniqueModal(tech.tech_id));
      techniquesGrid.appendChild(card);
    });

    renderPagination(data.page, data.pages);
  } catch (err) {
    console.error('Failed to load techniques:', err);
    techResultCount.textContent = 'Lỗi tải dữ liệu';
  }
}

// Render Pagination
function renderPagination(current, total) {
  techPagination.innerHTML = '';
  if (total <= 1) return;

  const prevBtn = document.createElement('button');
  prevBtn.className = 'page-btn';
  prevBtn.textContent = '« Trang trước';
  prevBtn.disabled = current === 1;
  prevBtn.addEventListener('click', () => {
    currentPage = current - 1;
    loadTechniques();
    window.scrollTo({ top: 300, behavior: 'smooth' });
  });
  techPagination.appendChild(prevBtn);

  let startP = Math.max(1, current - 2);
  let endP = Math.min(total, current + 2);

  for (let p = startP; p <= endP; p++) {
    const pBtn = document.createElement('button');
    pBtn.className = `page-btn ${p === current ? 'active' : ''}`;
    pBtn.textContent = p;
    pBtn.addEventListener('click', () => {
      currentPage = p;
      loadTechniques();
      window.scrollTo({ top: 300, behavior: 'smooth' });
    });
    techPagination.appendChild(pBtn);
  }

  const nextBtn = document.createElement('button');
  nextBtn.className = 'page-btn';
  nextBtn.textContent = 'Trang sau »';
  nextBtn.disabled = current === total;
  nextBtn.addEventListener('click', () => {
    currentPage = current + 1;
    loadTechniques();
    window.scrollTo({ top: 300, behavior: 'smooth' });
  });
  techPagination.appendChild(nextBtn);
}

// Quick Bones Bar Initialization
function initQuickBonesBar() {
  const chips = document.querySelectorAll('.bone-chip-btn');
  chips.forEach(btn => {
    btn.addEventListener('click', () => {
      chips.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const boneKey = btn.dataset.bone;
      if (boneKey === 'gustilo') {
        if (btnModeAllClassifications) btnModeAllClassifications.click();
        if (classifSearchInput) {
          classifSearchInput.value = 'Gustilo';
          renderAllClassificationsDirectory('Gustilo', 'all');
        }
      } else if (BONE_MAPPINGS[boneKey]) {
        if (btnModeSkeleton && !btnModeSkeleton.classList.contains('active')) {
          btnModeSkeleton.click();
        }
        selectBone(boneKey, BONE_MAPPINGS[boneKey]);
        if (tabBtnClassifications) tabBtnClassifications.click();
        
        setTimeout(() => {
          if (skeletonClassificationsContainer) {
            skeletonClassificationsContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
          }
        }, 150);
      }
    });
  });
}

// All Classifications Directory Renderer
let currentClassifRegion = 'all';
let currentClassifSearch = '';

function renderAllClassificationsDirectory(filterText, regionFilter) {
  if (!allClassificationsGrid) return;

  if (typeof filterText === 'string') currentClassifSearch = filterText.trim().toLowerCase();
  if (typeof regionFilter === 'string') currentClassifRegion = regionFilter;

  if (allClassesData.length === 0) {
    allClassificationsGrid.innerHTML = '<div style="padding: 2rem; color: var(--text-muted); text-align: center;">Đang nạp 23+ bảng phân loại gãy xương...</div>';
    return;
  }

  let filtered = allClassesData;

  // Region filter
  if (currentClassifRegion === 'lower') {
    filtered = filtered.filter(c => c.category === 'Knee & Lower Leg' || c.category === 'Hip & Pelvis' || c.category === 'Foot & Ankle');
  } else if (currentClassifRegion === 'upper') {
    filtered = filtered.filter(c => c.category === 'Shoulder & Arm' || c.category === 'Elbow & Forearm' || c.category === 'Hand & Wrist');
  } else if (currentClassifRegion === 'spine-pelvis') {
    filtered = filtered.filter(c => c.category === 'Spine' || (c.bone_vi && (c.bone_vi.includes('chậu') || c.bone_vi.includes('cối') || c.bone_vi.includes('sống'))));
  } else if (currentClassifRegion === 'general') {
    filtered = filtered.filter(c => c.category === 'Approaches & General Principles' || c.id === 'gustilo' || c.id === 'salter_harris' || c.id === 'ao_ota');
  }

  // Text search filter
  if (currentClassifSearch) {
    const qNorm = normalizeStr(currentClassifSearch);
    filtered = filtered.filter(c => {
      return (
        normalizeStr(c.name).includes(qNorm) ||
        normalizeStr(c.en_name).includes(qNorm) ||
        normalizeStr(c.bone_vi).includes(qNorm) ||
        normalizeStr(c.category).includes(qNorm) ||
        (c.types && c.types.some(t => normalizeStr(t.name).includes(qNorm) || normalizeStr(t.code).includes(qNorm) || normalizeStr(t.description).includes(qNorm)))
      );
    });
  }

  if (filtered.length === 0) {
    allClassificationsGrid.innerHTML = `
      <div style="background: #fff; padding: 2.5rem; text-align: center; border-radius: 12px; border: 1px dashed var(--border); color: var(--text-muted);">
        <p style="font-size: 1.1rem; font-weight: 600;">Không tìm thấy bảng phân loại gãy phù hợp với "${escapeHtml(currentClassifSearch)}"</p>
        <p style="margin-top: 0.5rem; font-size: 0.9rem;">Hãy thử gõ tên tác giả (Schatzker, Neer, Garden, Denis, Gustilo, Bado...) hoặc vị trí xương (mâm chày, cổ xương đùi, cổ chân...).</p>
      </div>
    `;
    return;
  }

  allClassificationsGrid.innerHTML = '';

  filtered.forEach(item => {
    const card = document.createElement('div');
    card.className = 'classification-card';
    card.id = `all-classif-${item.id}`;

    const typesHtml = (item.types || []).map(t => {
      const typeCode = t.code || t.type || '';
      const typeName = t.name || '';
      const typeDesc = t.desc || t.description || '';
      const typeMgmt = t.management || t.principles || '';
      const techId = t.technique_id || '';
      const btnLabel = t.button_label || (techId ? `Xem Kỹ thuật ${techId} (${t.technique_title || ''})` : '');

      return `
        <div class="type-item">
          <div class="type-item-header">
            <span class="type-code">📌 ${escapeHtml(typeCode)}</span>
            ${typeName ? `<strong style="color: var(--dark); font-size: 0.925rem;">${escapeHtml(typeName)}</strong>` : ''}
          </div>
          ${typeDesc ? `<div class="type-desc" style="line-height: 1.45; color: #334155;">${escapeHtml(typeDesc)}</div>` : ''}
          ${typeMgmt ? `<div class="type-management" style="margin-top: 0.4rem; color: #0369a1; font-weight: 500;">⚡ <strong>Chỉ định & Xử trí:</strong> ${escapeHtml(typeMgmt)}</div>` : ''}
          ${techId ? `
            <div class="type-action-row" style="margin-top: 0.5rem;">
              <button class="type-tech-btn" onclick="openTechniqueModal('${techId}')" title="Mở toàn văn quy trình phẫu thuật">
                🔪 ${escapeHtml(btnLabel)} &rarr;
              </button>
            </div>
          ` : ''}
        </div>
      `;
    }).join('');

    const techsHtml = (item.techniques || []).map(t_id => `
      <button class="tech-tag-btn" onclick="openTechniqueModal('${t_id}')">🔪 Kỹ thuật ${t_id}</button>
    `).join('');

    card.innerHTML = `
      <div class="classification-header">
        <div class="classification-title">
          <h3 style="font-size: 1.25rem; font-weight: 800; color: #0f172a;">${escapeHtml(item.name)}</h3>
          <span style="font-size: 0.85rem; color: #0284c7; font-weight: 600;">${escapeHtml(item.en_name)} • Vị trí: ${escapeHtml(item.bone_vi)} • Chuyên khoa: ${escapeHtml(item.category)}</span>
        </div>
        <button class="view-btn classif-protocol-btn" onclick="openClassificationProtocol('${item.id}')">
          📋 Phác đồ & Quy trình mổ &rarr;
        </button>
      </div>

      ${item.image_url ? `
        <div class="classif-image-wrap">
          <img src="${item.image_url}" alt="${escapeHtml(item.name)}" class="classif-main-img" loading="lazy" data-img-url="${item.image_url}" data-caption="${escapeHtml(item.name + ' - Sơ đồ phân loại & hướng phẫu thuật Campbell')}" onclick="openImageLightbox(this.dataset.imgUrl || this.src, this.dataset.caption)">
          <div class="image-caption">🔍 Sơ đồ phân loại & hướng điều trị chuẩn Campbell • Nhấn để phóng to</div>
        </div>
      ` : ''}

      <p class="classification-desc" style="font-size: 0.925rem; line-height: 1.5; color: #475569; margin: 0.75rem 0 0.85rem;">
        ${escapeHtml(item.overview || item.description)}
      </p>

      <div class="classif-clinical-grid">
        ${item.mechanism ? `
          <div class="classif-clinical-box mechanism-box">
            <div class="classif-box-title">💥 Cơ chế chấn thương</div>
            <div class="classif-box-content">${escapeHtml(item.mechanism)}</div>
          </div>
        ` : ''}
        ${item.imaging ? `
          <div class="classif-clinical-box imaging-box">
            <div class="classif-box-title">📷 Đánh giá X-quang & CT</div>
            <div class="classif-box-content">${escapeHtml(item.imaging)}</div>
          </div>
        ` : ''}
        ${item.treatment_principles ? `
          <div class="classif-clinical-box treatment-box">
            <div class="classif-box-title">🎯 Nguyên tắc xử trí</div>
            <div class="classif-box-content">${escapeHtml(item.treatment_principles)}</div>
          </div>
        ` : ''}
        ${item.complications ? `
          <div class="classif-clinical-box complications-box">
            <div class="classif-box-title">⚠️ Biến chứng cần lưu ý</div>
            <div class="classif-box-content">${escapeHtml(item.complications)}</div>
          </div>
        ` : ''}
      </div>

      <div class="classification-types">
        ${typesHtml}
      </div>
      ${techsHtml ? `
        <div class="classification-techniques" style="margin-top: 1rem; padding-top: 0.75rem; border-top: 1px dashed var(--border);">
          <span style="font-size: 0.8rem; font-weight: 800; color: #64748b; display: block; margin-bottom: 0.5rem;">CÁC KỸ THUẬT MỔ CHỈ ĐỊNH (CAMPBELL 13TH ED):</span>
          <div style="display: flex; gap: 0.5rem; flex-wrap: wrap;">${techsHtml}</div>
        </div>
      ` : ''}
    `;

    allClassificationsGrid.appendChild(card);
  });
}

// Open Dedicated Classification Clinical Protocol Modal
async function openClassificationProtocol(classifId) {
  if (allClassesData.length === 0) {
    allClassesData = await loadStaticOrApi('/api/classifications', 'data/fracture_classifications.json');
  }
  const item = allClassesData.find(c => c.id === classifId);
  if (!item) return;

  techModal.classList.add('active');
  modalTechId.textContent = `PHÁC ĐỒ ĐIỀU TRỊ • ${item.name.toUpperCase()}`;
  modalTechTitle.textContent = item.name + ' (' + item.en_name + ')';
  modalTechMeta.textContent = `Chuyên khoa: ${item.category} • Vị trí: ${item.bone_vi} • Chương ${item.chapter}: ${item.chapter_title}`;

  if (tabContentExtractedText) tabContentExtractedText.style.display = 'block';

  if (modalTechDetailHeader) {
    modalTechDetailHeader.innerHTML = `
      <div class="tech-detail-top-row">
        <span class="tech-code" style="font-size: 0.85rem; font-weight: 800;">PHÁC ĐỒ ĐIỀU TRỊ CHUẨN CAMPBELL</span>
        <span class="badge" style="font-size: 0.8rem; background: #0284c7; color: #fff;">Chương ${item.chapter}</span>
      </div>
      <h3 class="tech-detail-title">${escapeHtml(item.name)} (${escapeHtml(item.en_name)})</h3>
      <div class="tech-detail-meta-pills">
        <span>Vị trí: <strong>${escapeHtml(item.bone_vi)}</strong></span>
        <span>•</span>
        <span>Chuyên khoa: <strong>${escapeHtml(item.category)}</strong></span>
      </div>
    `;
  }

  if (modalLinkedClassifBox) {
    modalLinkedClassifBox.style.display = 'none';
  }

  let protocolHtml = `
    <div class="clinical-card-wrapper">
      ${item.image_url ? `
        <div class="classif-image-wrap">
          <img src="${item.image_url}" alt="${escapeHtml(item.name)}" class="classif-main-img" data-img-url="${item.image_url}" data-caption="${escapeHtml(item.name + ' - Sơ đồ phân loại & hướng phẫu thuật Campbell')}" onclick="openImageLightbox(this.dataset.imgUrl || this.src, this.dataset.caption)">
          <div class="image-caption">🔍 Sơ đồ phân loại & hướng điều trị chuẩn Campbell • Nhấn để phóng to</div>
        </div>
      ` : ''}

      <div class="clinical-section-card">
        <div class="clinical-section-title">📌 Tổng quan & Định nghĩa phân loại</div>
        <div class="clinical-section-body">${escapeHtml(item.overview || item.description)}</div>
      </div>

      <div class="classif-clinical-grid">
        ${item.mechanism ? `
          <div class="classif-clinical-box mechanism-box">
            <div class="classif-box-title">💥 Cơ chế chấn thương</div>
            <div class="classif-box-content">${escapeHtml(item.mechanism)}</div>
          </div>
        ` : ''}
        ${item.imaging ? `
          <div class="classif-clinical-box imaging-box">
            <div class="classif-box-title">📷 Đánh giá X-quang & CT</div>
            <div class="classif-box-content">${escapeHtml(item.imaging)}</div>
          </div>
        ` : ''}
        ${item.treatment_principles ? `
          <div class="classif-clinical-box treatment-box">
            <div class="classif-box-title">🎯 Nguyên tắc xử trí & Chỉ định</div>
            <div class="classif-box-content">${escapeHtml(item.treatment_principles)}</div>
          </div>
        ` : ''}
        ${item.complications ? `
          <div class="classif-clinical-box complications-box">
            <div class="classif-box-title">⚠️ Biến chứng cần cảnh giác</div>
            <div class="classif-box-content">${escapeHtml(item.complications)}</div>
          </div>
        ` : ''}
      </div>

      <div class="clinical-section-card">
        <div class="clinical-section-title">⚡ Chiến lược điều trị chi tiết theo từng phân độ</div>
        <div class="clinical-steps-list">
          ${(item.types || []).map(t => `
            <div class="clinical-step-item">
              <div class="clinical-step-header">
                <span class="clinical-step-pill">${escapeHtml(t.code || t.type)}</span>
                <span class="clinical-step-title">${escapeHtml(t.name || '')}</span>
              </div>
              <div class="clinical-step-desc">${escapeHtml(t.desc || t.description || '')}</div>
              ${t.management || t.principles ? `
                <div class="clinical-step-action">
                  <strong>Xử trí khuyến cáo:</strong> ${escapeHtml(t.management || t.principles)}
                </div>
              ` : ''}
              ${t.technique_id ? `
                <div style="margin-top: 0.6rem;">
                  <button class="type-tech-btn" onclick="openTechniqueModal('${t.technique_id}')">
                    🔪 Xem Kỹ thuật mổ ${t.technique_id} (${escapeHtml(t.technique_title || '')}) &rarr;
                  </button>
                </div>
              ` : ''}
            </div>
          `).join('')}
        </div>
      </div>

      ${item.techniques && item.techniques.length > 0 ? `
        <div class="clinical-section-card">
          <div class="clinical-section-title">🔪 Các quy trình kỹ thuật mổ chỉ định liên quan</div>
          <div style="display: flex; gap: 0.5rem; flex-wrap: wrap; margin-top: 0.5rem;">
            ${item.techniques.map(t_id => `
              <button class="tech-tag-btn" onclick="openTechniqueModal('${t_id}')" style="padding: 0.4rem 0.8rem; font-size: 0.85rem;">
                🔪 Kỹ thuật ${t_id} &rarr;
              </button>
            `).join('')}
          </div>
        </div>
      ` : ''}
    </div>
  `;

  modalExtractedText.innerHTML = protocolHtml;
}

// Full-text loading & formatting helpers
let allTechniqueTextsCache = null;
let allPagesTextCache = null;

async function getAllTechniqueTexts() {
  if (allTechniqueTextsCache) return allTechniqueTextsCache;
  try {
    const res = await fetch('data/techniques_text.json');
    if (res.ok) {
      allTechniqueTextsCache = await res.json();
      return allTechniqueTextsCache;
    }
  } catch (e) {
    console.warn('Failed to load techniques_text.json:', e);
  }
  return {};
}

async function getAllPagesText() {
  if (allPagesTextCache) return allPagesTextCache;
  try {
    const res = await fetch('data/pages_text.json');
    if (res.ok) {
      allPagesTextCache = await res.json();
      return allPagesTextCache;
    }
  } catch (e) {
    console.warn('Failed to load pages_text.json:', e);
  }
  return {};
}

function formatTechniqueText(rawText) {
  if (!rawText) {
    return '<p style="color: var(--text-muted); font-style: italic;">Không có nội dung văn bản trích xuất trực tiếp cho kỹ thuật này.</p>';
  }

  // Join hyphenated line breaks
  let text = rawText.replace(/(\w+)-\s*\n\s*(\w+)/g, '$1$2');
  const lines = text.split('\n').map(l => l.trim()).filter(l => l.length > 0);

  let html = '<div class="formatted-tech-body">';

  lines.forEach(line => {
    if (/^(TECHNIQUE\s+\d+-\d+|SURGICAL\s+APPROACH|INDICATIONS|OPERATIVE\s+TECHNIQUE|POSTOPERATIVE\s+CARE|AFTERTREATMENT|COMPLICATIONS|SURGICAL\s+ANATOMY|EQUIPMENT|PITFALLS)/i.test(line)) {
      html += `<div class="tech-heading">📌 ${escapeHtml(line)}</div>`;
    } else if (/^(STEP\s+\d+|Thì\s+\d+|Bước\s+\d+|\d+\.\s+)/i.test(line)) {
      html += `<div class="tech-step"><strong>${escapeHtml(line)}</strong></div>`;
    } else {
      html += `<p style="margin-bottom: 0.75rem; line-height: 1.75;">${escapeHtml(line)}</p>`;
    }
  });

  html += '</div>';
  return html;
}

// Structured Clinical Knowledge Base helpers
let clinicalTechniquesCache = null;

async function getClinicalTechnique(techId) {
  const safeId = String(techId).replace('/', '_');
  try {
    const res = await fetch(`data/techniques/${safeId}.json`);
    if (res.ok) {
      return await res.json();
    }
  } catch (e) {}

  if (clinicalTechniquesCache && (clinicalTechniquesCache[techId] || clinicalTechniquesCache[safeId])) {
    return clinicalTechniquesCache[techId] || clinicalTechniquesCache[safeId];
  }

  if (!isStaticMode) {
    try {
      const res = await fetch(`/api/techniques/${techId}`);
      if (res.ok) return await res.json();
    } catch (e) {}
  }
  return null;
}

async function getClinicalTechniques() {
  if (clinicalTechniquesCache) return clinicalTechniquesCache;
  try {
    const res = await fetch('data/clinical_techniques.json');
    if (res.ok) {
      clinicalTechniquesCache = await res.json();
      return clinicalTechniquesCache;
    }
  } catch (e) {
    console.warn('Failed to load clinical_techniques.json:', e);
  }
  return {};
}

function toggleRawBookText(btn) {
  const body = btn.nextElementSibling;
  if (!body) return;
  const isHidden = body.style.display === 'none' || !body.style.display;
  body.style.display = isHidden ? 'block' : 'none';
  btn.textContent = isHidden 
    ? '📖 Ẩn trích dẫn nguyên bản tiếng Anh ▴' 
    : '📖 Xem trích dẫn nguyên bản văn bản sách tiếng Anh (Campbell 13th Ed) ▾';
}

function renderClinicalTechniqueCard(guide, rawFallback) {
  const stepsHtml = (guide.surgical_steps || []).map(s => `
    <div class="clinical-step-item">
      <div class="clinical-step-header">
        <span class="clinical-step-pill">Thì ${s.step || 1}</span>
        <span class="clinical-step-title">${escapeHtml(s.title || '')}</span>
      </div>
      <div class="clinical-step-desc">${escapeHtml(s.detail || s.description || '')}</div>
      ${s.action || s.key_action ? `
        <div class="clinical-step-action">
          ⚡ <strong>Thao tác then chốt:</strong> ${escapeHtml(s.action || s.key_action)}
        </div>
      ` : ''}
    </div>
  `).join('');

  return `
    <div class="clinical-card-wrapper">
      <!-- Badges -->
      <div class="clinical-badges-row">
        <span class="clinical-badge-tag primary">Chuyên khoa: ${escapeHtml(guide.category || 'General')}</span>
        <span class="clinical-badge-tag">Chương ${guide.chapter || ''}</span>
        ${guide.author ? `<span class="clinical-badge-tag highlight">👨‍⚕️ ${escapeHtml(guide.author)}</span>` : ''}
      </div>

      <!-- Indications & Objectives -->
      ${guide.clinical_indications ? `
        <div class="clinical-section-card">
          <div class="clinical-section-title">📌 Chỉ định lâm sàng & Mục tiêu phẫu thuật</div>
          <div class="clinical-section-body">${escapeHtml(guide.clinical_indications)}</div>
        </div>
      ` : ''}

      <!-- Contraindications -->
      ${guide.contraindications ? `
        <div class="clinical-box-contra">
          <div class="clinical-box-contra-title">🚫 Chống chỉ định can thiệp</div>
          <div class="clinical-section-body">${escapeHtml(guide.contraindications)}</div>
        </div>
      ` : ''}

      <!-- Patient Prep & Positioning -->
      ${guide.patient_prep ? `
        <div class="clinical-section-card">
          <div class="clinical-section-title">📐 Tư thế bệnh nhân & Chuẩn bị (Setup)</div>
          <div class="clinical-section-body">${escapeHtml(guide.patient_prep)}</div>
        </div>
      ` : ''}

      <!-- Surgical Approach & Danger Zones -->
      ${guide.surgical_approach ? `
        <div class="clinical-box-danger">
          <div class="clinical-box-danger-title">🔪 Đường mổ & Cấu trúc giải phẫu nguy cơ</div>
          <div class="clinical-section-body">${escapeHtml(guide.surgical_approach)}</div>
        </div>
      ` : ''}

      <!-- Operative Diagram / X-ray Figure / Gallery -->
      ${(guide.images && guide.images.length > 0) ? `
        <div class="tech-images-gallery">
          ${guide.images.map(img => `
            <div class="tech-image-card">
              <img src="${img.url}" alt="${escapeHtml(img.caption || guide.name_vi)}" class="tech-main-img" loading="lazy" data-img-url="${img.url}" data-caption="${escapeHtml(img.caption || guide.name_vi)}" onclick="openImageLightbox(this.dataset.imgUrl || this.src, this.dataset.caption)">
              <div class="image-caption">${img.type === 'xray' ? '🩻 Phim X-quang / Ca lâm sàng' : '🔍 Sơ đồ phẫu thuật Campbell'} • ${escapeHtml(img.caption || '')}</div>
            </div>
          `).join('')}
        </div>
      ` : (guide.image_url ? `
        <div class="tech-image-wrap">
          <img src="${guide.image_url}" alt="${escapeHtml(guide.name_vi)}" class="tech-main-img" loading="lazy" data-img-url="${guide.image_url}" data-caption="${escapeHtml(guide.name_vi + ' - Sơ đồ kỹ thuật mổ chuẩn Campbell')}" onclick="openImageLightbox(this.dataset.imgUrl || this.src, this.dataset.caption)">
          <div class="image-caption">🔍 Sơ đồ giải phẫu & kỹ thuật phẫu thuật thực hành chuẩn Campbell • Nhấn để phóng to</div>
        </div>
      ` : '')}

      <!-- Step-by-Step Operative Technique -->
      <div class="clinical-section-card">
        <div class="clinical-section-title">⚡ Các thì phẫu thuật từng bước (Operative Steps)</div>
        <div class="clinical-steps-list">
          ${stepsHtml}
        </div>
      </div>

      <!-- Postoperative Care & Rehab -->
      ${guide.postop_protocol ? `
        <div class="clinical-box-rehab">
          <div class="clinical-box-rehab-title">🩺 Chăm sóc sau mổ & Phục hồi chức năng (Rehabilitation)</div>
          <div class="clinical-section-body">${escapeHtml(guide.postop_protocol)}</div>
        </div>
      ` : ''}

      <!-- Campbell's Pearls & Traps -->
      ${guide.pearls_pitfalls ? `
        <div class="clinical-box-pearls">
          <div class="clinical-box-pearls-title">⚠️ Lưu ý chuyên môn & Cạm bẫy của Campbell (Pearls & Pitfalls)</div>
          <div class="clinical-section-body">${escapeHtml(guide.pearls_pitfalls)}</div>
        </div>
      ` : ''}

      <!-- Optional In-Depth Text Accordion -->
      ${rawFallback ? `
        <div style="margin-top: 0.5rem;">
          <button class="clinical-raw-toggle-btn" onclick="toggleRawBookText(this)">
            📖 Xem trích dẫn chi tiết từ Campbell's Operative Orthopaedics ▾
          </button>
          <div class="clinical-raw-body">
            ${formatTechniqueText(rawFallback)}
          </div>
        </div>
      ` : ''}
    </div>
  `;
}

// Lightbox modal helpers
function openImageLightbox(imgUrl, caption) {
  const lightbox = document.getElementById('imageLightbox');
  const img = document.getElementById('lightboxImg');
  const cap = document.getElementById('lightboxCaption');
  if (lightbox && img) {
    img.src = imgUrl;
    if (cap) cap.textContent = caption || '';
    lightbox.classList.remove('zoomed');
    lightbox.classList.add('active');
  }
}

function toggleLightboxZoom(e) {
  if (e) e.stopPropagation();
  const lightbox = document.getElementById('imageLightbox');
  if (lightbox) {
    lightbox.classList.toggle('zoomed');
  }
}

function closeImageLightbox() {
  const lightbox = document.getElementById('imageLightbox');
  if (lightbox) {
    lightbox.classList.remove('active');
    lightbox.classList.remove('zoomed');
  }
}

// Open Technique Modal
async function openTechniqueModal(techId) {
  try {
    techModal.classList.add('active');
    modalTechId.textContent = `TECHNIQUE ${techId}`;
    modalTechTitle.textContent = 'Đang tải thông tin...';
    modalTechMeta.textContent = '';
    
    if (tabContentExtractedText) tabContentExtractedText.style.display = 'block';
    if (modalLinkedClassifBox) {
      modalLinkedClassifBox.style.display = 'none';
      modalLinkedClassifBox.innerHTML = '';
    }

    modalExtractedText.innerHTML = '<div style="padding: 1.5rem; color: var(--text-muted);">Đang nạp toàn văn quy trình phẫu thuật từ Campbell 13th Ed...</div>';

    let tech = null;
    if (!isStaticMode) {
      try {
        const res = await fetch(`/api/techniques/${techId}`);
        if (res.ok) {
          tech = await res.json();
        } else {
          isStaticMode = true;
        }
      } catch (e) {
        isStaticMode = true;
      }
    }

    if (!tech) {
      const all = await getAllTechniques();
      tech = all.find(t => String(t.tech_id) === String(techId));
    }

    if (!tech) throw new Error('Không tìm thấy kỹ thuật ' + techId);
    activeTechnique = tech;

    modalTechTitle.textContent = tech.name;
    modalTechMeta.textContent = `Chương ${tech.chapter}: ${tech.chapter_title} • Phẫu thuật Chỉnh hình Campbell`;

    // Render structured header card
    if (modalTechDetailHeader) {
      modalTechDetailHeader.innerHTML = `
        <div class="tech-detail-top-row">
          <span class="tech-code" style="font-size: 0.85rem; font-weight: 800;">CAMPBELL TECHNIQUE ${tech.tech_id}</span>
          <span class="badge" style="font-size: 0.8rem; background: #0284c7; color: #fff;">Chương ${tech.chapter}</span>
        </div>
        <h3 class="tech-detail-title">${escapeHtml(tech.name)}</h3>
        ${tech.author ? `<div class="tech-detail-author">👨‍⚕️ Tác giả / Tên định danh phẫu thuật: <strong>${escapeHtml(tech.author)}</strong></div>` : ''}
        <div class="tech-detail-meta-pills">
          <span>📖 Chương ${tech.chapter}: ${escapeHtml(tech.chapter_title)}</span>
          ${tech.categories && tech.categories.length > 0 ? `<span>•</span><span>Giải phẫu: <strong>${tech.categories.map(c => c.vi || c.id).join(', ')}</strong></span>` : ''}
        </div>
      `;
    }

    // Check if this technique is linked to a fracture classification!
    if (allClassesData.length === 0) {
      allClassesData = await loadStaticOrApi('/api/classifications', 'data/fracture_classifications.json');
    }
    const linkedClass = allClassesData.find(c => {
      if (c.techniques && c.techniques.includes(techId)) return true;
      if (c.types && c.types.some(t => t.technique_id === techId)) return true;
      return false;
    });

    if (modalLinkedClassifBox) {
      if (linkedClass) {
        const matchingType = linkedClass.types ? linkedClass.types.find(t => t.technique_id === techId) : null;
        modalLinkedClassifBox.style.display = 'flex';
        modalLinkedClassifBox.innerHTML = `
          <div class="linked-classif-info">
            <h4>🦴 BẢNG PHÂN LOẠI GÃY LIÊN QUAN: ${escapeHtml(linkedClass.name)} (${escapeHtml(linkedClass.bone_vi)})</h4>
            <p>${matchingType ? `⚡ <strong>Chỉ định (${escapeHtml(matchingType.code)} - ${escapeHtml(matchingType.name)}):</strong> ${escapeHtml(matchingType.principles || matchingType.description)}` : escapeHtml(linkedClass.description)}</p>
          </div>
          <button class="linked-classif-btn" id="btnGoToLinkedClassif">
            Xem Bảng phân loại &rarr;
          </button>
        `;
        const btnGo = modalLinkedClassifBox.querySelector('#btnGoToLinkedClassif');
        if (btnGo) {
          btnGo.onclick = () => {
            techModal.classList.remove('active');
            scrollToClassification(linkedClass.id);
          };
        }
      } else {
        modalLinkedClassifBox.style.display = 'none';
      }
    }

    // Fast path: load lightweight 3-4KB micro-technique directly
    const guide = await getClinicalTechnique(techId);

    if (guide && (guide.surgical_steps || guide.indications || guide.description_vi)) {
      modalExtractedText.innerHTML = renderClinicalTechniqueCard(guide, tech.extracted_text || '');
    } else {
      let fullText = tech.extracted_text || '';
      if (!fullText) {
        const allTexts = await getAllTechniqueTexts();
        fullText = allTexts[techId] || '';
      }
      if (!fullText || fullText.length < 80) {
        if (tech.pdf_page) {
          const allPages = await getAllPagesText();
          fullText = allPages[String(tech.pdf_page)] || '';
        }
      }
      modalExtractedText.innerHTML = formatTechniqueText(fullText);
    }

  } catch (err) {
    console.error('Failed to load technique detail:', err);
    modalTechTitle.textContent = 'Lỗi tải kỹ thuật';
    modalExtractedText.innerHTML = '<div style="color: red; padding: 1.5rem;">Không thể nạp nội dung kỹ thuật mổ.</div>';
  }
}

// Load Outline Tree
async function loadOutline() {
  try {
    outlineContainer.innerHTML = '<p style="color: var(--text-muted);">Đang dựng cây đề mục phẫu thuật...</p>';
    const outline = await loadStaticOrApi('/api/outline', 'data/outline_tree.json');

    outlineContainer.innerHTML = '';
    outline.forEach(node => {
      outlineContainer.appendChild(renderTreeNode(node));
    });
  } catch (err) {
    console.error('Failed to load outline:', err);
    outlineContainer.innerHTML = '<p style="color: red;">Lỗi tải mục lục.</p>';
  }
}

function renderTreeNode(node) {
  const div = document.createElement('div');
  div.className = 'tree-item';
  const hasKids = node.children && node.children.length > 0;

  div.innerHTML = `
    <span style="color: ${hasKids ? 'var(--primary)' : 'var(--text-muted)'}; font-size: 0.8rem;">
      ${hasKids ? '📁' : '📄'}
    </span>
    <span style="font-weight: ${node.level === 1 ? '700' : 'normal'}; font-size: ${node.level === 1 ? '1rem' : '0.9rem'};">
      ${node.title}
    </span>
    ${node.page ? `<span class="badge" style="font-size: 0.7rem; margin-left: auto;">Campbell</span>` : ''}
  `;

  if (node.page) {
    div.addEventListener('click', (e) => {
      e.stopPropagation();
      openPageImageDirect(node.page, node.title);
    });
  }

  if (hasKids) {
    const container = document.createElement('div');
    const childWrapper = document.createElement('div');
    childWrapper.className = 'tree-node';
    childWrapper.style.display = node.level > 1 ? 'none' : 'block';

    div.addEventListener('click', () => {
      childWrapper.style.display = childWrapper.style.display === 'none' ? 'block' : 'none';
    });

    node.children.forEach(c => {
      childWrapper.appendChild(renderTreeNode(c));
    });

    container.appendChild(div);
    container.appendChild(childWrapper);
    return container;
  }

  return div;
}

async function openPageImageDirect(pageNum, title) {
  techModal.classList.add('active');
  modalTechId.textContent = `CAMPBELL 13TH ED • ĐỀ MỤC LÂM SÀNG`;
  modalTechTitle.textContent = title || `Chuyên đề Phẫu thuật`;
  modalTechMeta.textContent = `Phẫu thuật Chỉnh hình Campbell 13th Edition`;

  if (tabContentExtractedText) tabContentExtractedText.style.display = 'block';
  modalExtractedText.innerHTML = '<div style="padding: 2rem; color: var(--text-muted); text-align: center;">Đang nạp phác đồ chuyên môn...</div>';

  // Check if this page matches any known technique
  const allGuides = await getClinicalTechniques();
  const matchedTechId = Object.keys(allGuides).find(id => Number(allGuides[id].pdf_page) === Number(pageNum));
  if (matchedTechId) {
    const all = await getAllTechniques();
    const tech = all.find(t => String(t.tech_id) === String(matchedTechId));
    if (tech) {
      openTechniqueModal(matchedTechId);
      return;
    }
  }

  // Check if this page matches any classification
  if (allClassesData.length === 0) {
    allClassesData = await loadStaticOrApi('/api/classifications', 'data/fracture_classifications.json');
  }
  const matchedClassif = allClassesData.find(c => Number(c.pdf_page) === Number(pageNum));
  if (matchedClassif) {
    openClassificationProtocol(matchedClassif.id);
    return;
  }

  const allPages = await getAllPagesText();
  const pageText = allPages[String(pageNum)] || allPages[pageNum] || '';

  if (pageText) {
    modalExtractedText.innerHTML = `
      <div class="clinical-card-wrapper">
        <div class="clinical-section-card" style="border-left: 4px solid #0284c7;">
          <div class="clinical-section-title">📖 Đề mục: ${escapeHtml(title || 'Chuyên đề lâm sàng')}</div>
          <div class="clinical-section-body">
            <p style="color: #64748b; font-size: 0.85rem;">Trích yếu chuyên môn & Hướng dẫn phẫu thuật thực hành</p>
          </div>
        </div>
        <div class="clinical-section-card">
          <div class="clinical-section-title">📄 Nội dung trích xuất & Hướng dẫn chi tiết</div>
          <div class="clinical-section-body">
            ${formatTechniqueText(pageText)}
          </div>
        </div>
      </div>
    `;
  } else {
    modalExtractedText.innerHTML = `
      <div style="padding: 2rem; background: #fff; border-radius: 8px; border: 1px solid var(--border); text-align: center;">
        <h4 style="color: #0f172a; margin-bottom: 0.5rem;">📖 Đề mục: ${escapeHtml(title || '')}</h4>
        <p style="color: #475569; line-height: 1.6; margin-bottom: 1.25rem;">
          Đề mục chuyên môn trong hệ thống Campbell's Operative Orthopaedics.
        </p>
      </div>
    `;
  }
}

// PDF Viewer no-op helpers
function setModalPdfPage(pageNum) {}
function updateViewerTransform() {}
function applyZoom(scale) {}

function updateViewerTransform() {
  if (modalPageImage) {
    modalPageImage.style.transform = `translate(${panX}px, ${panY}px) scale(${currentZoom})`;
  }
  const pct = `${Math.round(currentZoom * 100)}%`;
  if (btnZoomReset) btnZoomReset.textContent = `↺ ${pct}`;
  const zoomLevelEl = document.getElementById('zoomLevel');
  if (zoomLevelEl) zoomLevelEl.textContent = pct;
}

function applyZoom(scale) {
  currentZoom = Math.min(Math.max(scale, 0.5), 3.0);
  updateViewerTransform();
}

// ----------------- SEARCH AUTOCOMPLETE & SUGGESTIONS -----------------
function normalizeStr(str) {
  if (!str) return '';
  return str.toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[đĐ]/g, 'd')
    .trim();
}

function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

async function loadAllClassificationsCache() {
  try {
    allClassesData = await loadStaticOrApi('/api/classifications', 'data/fracture_classifications.json');
  } catch (err) {
    console.error('Failed to pre-cache classifications:', err);
  }
}

function closeSuggestions() {
  if (searchSuggestions) {
    searchSuggestions.style.display = 'none';
    searchSuggestions.innerHTML = '';
  }
  activeSuggestionIndex = -1;
}

function updateActiveSuggestion(items) {
  items.forEach((item, idx) => {
    item.classList.toggle('active', idx === activeSuggestionIndex);
    if (idx === activeSuggestionIndex) {
      item.scrollIntoView({ block: 'nearest' });
    }
  });
}

async function handleSearchAutocomplete() {
  const query = globalSearch.value.trim();
  if (query.length < 2) {
    closeSuggestions();
    return;
  }

  const normQuery = normalizeStr(query);

  // Match in classifications
  const matchedClass = allClassesData.filter(c => {
    const matchName = normalizeStr(c.name).includes(normQuery);
    const matchEn = normalizeStr(c.en_name).includes(normQuery);
    const matchBone = normalizeStr(c.bone_vi).includes(normQuery);
    const matchCat = normalizeStr(c.category).includes(normQuery);
    return matchName || matchEn || matchBone || matchCat;
  }).slice(0, 3);

  // Match in techniques via API or static fallback
  let matchedTechs = [];
  if (!isStaticMode) {
    try {
      const res = await fetch(`/api/techniques?q=${encodeURIComponent(query)}&limit=5`);
      if (res.ok) {
        const data = await res.json();
        matchedTechs = data.items || [];
      } else {
        isStaticMode = true;
      }
    } catch (e) {
      isStaticMode = true;
    }
  }

  if (isStaticMode) {
    const all = await getAllTechniques();
    matchedTechs = all.filter(t => {
      return (
        t.tech_id.toLowerCase().includes(normQuery) ||
        normalizeStr(t.name).includes(normQuery) ||
        (t.author && normalizeStr(t.author).includes(normQuery))
      );
    }).slice(0, 5);
  }

  if (matchedClass.length === 0 && matchedTechs.length === 0) {
    searchSuggestions.innerHTML = `
      <div style="padding: 0.75rem 1.25rem; color: #64748b; font-size: 0.85rem;">
        Không có gợi ý nhanh cho "<strong>${escapeHtml(query)}</strong>". Nhấn Enter để tìm kiếm toàn văn.
      </div>
    `;
    searchSuggestions.style.display = 'block';
    return;
  }

  searchSuggestions.innerHTML = '';
  activeSuggestionIndex = -1;

  // Render classifications
  matchedClass.forEach(item => {
    const div = document.createElement('div');
    div.className = 'suggestion-item';
    div.innerHTML = `
      <div class="suggestion-left">
        <span class="suggestion-badge classif">🦴 PHÂN LOẠI</span>
        <span class="suggestion-title">${item.name} (${item.bone_vi})</span>
      </div>
      <span class="suggestion-meta">${item.category}</span>
    `;
    div.addEventListener('click', () => {
      closeSuggestions();
      globalSearch.value = item.name;
      scrollToClassification(item.id);
    });
    searchSuggestions.appendChild(div);
  });

  // Render techniques
  matchedTechs.forEach(tech => {
    const div = document.createElement('div');
    div.className = 'suggestion-item';
    div.innerHTML = `
      <div class="suggestion-left">
        <span class="suggestion-badge tech">🔪 KT ${tech.tech_id}</span>
        <span class="suggestion-title">${tech.name}</span>
      </div>
      <span class="suggestion-meta">Chương ${tech.chapter}</span>
    `;
    div.addEventListener('click', () => {
      closeSuggestions();
      openTechniqueModal(tech.tech_id);
    });
    searchSuggestions.appendChild(div);
  });

  // Footer "Xem tất cả"
  const footerDiv = document.createElement('div');
  footerDiv.className = 'suggestion-item';
  footerDiv.style.background = '#f8fafc';
  footerDiv.style.borderTop = '1px solid #e2e8f0';
  footerDiv.innerHTML = `
    <div class="suggestion-left">
      <span style="font-size: 0.9rem;">🔍</span>
      <span class="suggestion-title" style="color: var(--primary);">Xem tất cả kết quả tìm kiếm cho "${escapeHtml(query)}"</span>
    </div>
    <span class="suggestion-meta" style="font-weight: 600; color: var(--primary);">Nhấn Enter ↵</span>
  `;
  footerDiv.addEventListener('click', () => {
    closeSuggestions();
    performSearch();
  });
  searchSuggestions.appendChild(footerDiv);

  searchSuggestions.style.display = 'block';
}

function closeTechniqueSuggestions() {
  if (techniqueSuggestions) {
    techniqueSuggestions.style.display = 'none';
    techniqueSuggestions.innerHTML = '';
  }
}

async function handleTechniqueSearchAutocomplete() {
  if (!techniqueSearch || !techniqueSuggestions) return;
  const query = techniqueSearch.value.trim();
  if (query.length < 2) {
    closeTechniqueSuggestions();
    return;
  }

  const normQuery = normalizeStr(query);

  // Match in classifications
  const matchedClass = allClassesData.filter(c => {
    const matchName = normalizeStr(c.name).includes(normQuery);
    const matchEn = normalizeStr(c.en_name).includes(normQuery);
    const matchBone = normalizeStr(c.bone_vi).includes(normQuery);
    return matchName || matchEn || matchBone;
  }).slice(0, 2);

  // Match in techniques via API or static fallback
  let matchedTechs = [];
  if (!isStaticMode) {
    try {
      const params = new URLSearchParams({ q: query, limit: 6 });
      if (currentCategory) params.append('category', currentCategory);
      if (currentChapter) params.append('chapter', currentChapter);
      if (currentAuthor) params.append('author', currentAuthor);
      const res = await fetch(`/api/techniques?${params.toString()}`);
      if (res.ok) {
        const data = await res.json();
        matchedTechs = data.items || [];
      } else {
        isStaticMode = true;
      }
    } catch (e) {
      isStaticMode = true;
    }
  }

  if (isStaticMode) {
    const all = await getAllTechniques();
    let filtered = all;
    if (currentCategory) {
      filtered = filtered.filter(t => (t.categories && t.categories.includes(currentCategory)) || t.category === currentCategory);
    }
    if (currentChapter) {
      filtered = filtered.filter(t => String(t.chapter) === String(currentChapter));
    }
    if (currentAuthor) {
      filtered = filtered.filter(t => t.author && t.author.toLowerCase().includes(currentAuthor.toLowerCase()));
    }
    matchedTechs = filtered.filter(t => {
      return (
        t.tech_id.toLowerCase().includes(normQuery) ||
        normalizeStr(t.name).includes(normQuery) ||
        (t.author && normalizeStr(t.author).includes(normQuery))
      );
    }).slice(0, 6);
  }

  if (matchedClass.length === 0 && matchedTechs.length === 0) {
    techniqueSuggestions.innerHTML = `
      <div style="padding: 0.75rem 1rem; color: #64748b; font-size: 0.85rem;">
        Không tìm thấy kỹ thuật cho "<strong>${escapeHtml(query)}</strong>"
      </div>
    `;
    techniqueSuggestions.style.display = 'block';
    return;
  }

  techniqueSuggestions.innerHTML = '';

  // Render classifications
  matchedClass.forEach(item => {
    const div = document.createElement('div');
    div.className = 'suggestion-item';
    div.innerHTML = `
      <div class="suggestion-left">
        <span class="suggestion-badge classif">🦴 PHÂN LOẠI</span>
        <span class="suggestion-title">${item.name} (${item.bone_vi})</span>
      </div>
      <span class="suggestion-meta">${item.category}</span>
    `;
    div.addEventListener('click', () => {
      closeTechniqueSuggestions();
      scrollToClassification(item.id);
    });
    techniqueSuggestions.appendChild(div);
  });

  // Render techniques
  matchedTechs.forEach(tech => {
    const div = document.createElement('div');
    div.className = 'suggestion-item';
    div.innerHTML = `
      <div class="suggestion-left">
        <span class="suggestion-badge tech">🔪 KT ${tech.tech_id}</span>
        <span class="suggestion-title">${tech.name}</span>
      </div>
      <span class="suggestion-meta">${tech.author ? tech.author + ' • ' : ''}Chương ${tech.chapter}</span>
    `;
    div.addEventListener('click', () => {
      closeTechniqueSuggestions();
      openTechniqueModal(tech.tech_id);
    });
    techniqueSuggestions.appendChild(div);
  });

  techniqueSuggestions.style.display = 'block';
}
