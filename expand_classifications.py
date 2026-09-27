import json

with open('data/fracture_classifications.json', 'r', encoding='utf-8') as f:
    fc = json.load(f)

# Keep the original 23 classifications exactly intact
original_23_ids = [
    'schatzker', 'garden', 'pauwels', 'neer', 'gustilo', 'young_burgess',
    'letournel_judet', 'denis_spine', 'danis_weber', 'hawkins', 'frykman',
    'mason', 'ao_ota', 'salter_harris', 'pipkin', 'sanders', 'anderson_dalonzo',
    'bado_monteggia', 'galeazzi', 'winquist_hansen', 'ruedi_allgower',
    'colles_smith_barton', 'russell_taylor'
]

cleaned_fc = [c for c in fc if c['id'] in original_23_ids]

new_classifications = [
    {
        "id": "tile_pelvis",
        "name": "Phân loại Gãy Khung Chậu Marvin Tile (AO/OTA 61)",
        "en_name": "Tile Classification of Pelvic Ring Fractures (AO/OTA 61)",
        "bone": "Pelvis",
        "bone_vi": "Khung chậu",
        "svg_ids": ["PelvisLeft", "PelvisRight", "Sacrum", "l_Pelvis", "r_Pelvis"],
        "category": "Hip & Pelvis",
        "chapter": 56,
        "pdf_page": 2862,
        "description": "Phân loại chuẩn hóa gãy vòng chậu dựa trên độ vững của phức hợp dây chằng chậu cùng: Tile A vững, Tile B mất vững xoay, Tile C mất vững hoàn toàn cả xoay và dọc.",
        "types": [
            {
                "type": "Tile A",
                "code": "Tile A",
                "name": "Gãy vững cung sau (Stable)",
                "desc": "Cung sau nguyên vẹn, gãy ngoài vòng chậu hoặc không di lệch (gãy giật gai chậu, gãy cánh chậu đơn độc, gãy ngành mu một bên).",
                "description": "Cung sau nguyên vẹn, gãy ngoài vòng chậu hoặc không di lệch (gãy giật gai chậu, gãy cánh chậu đơn độc, gãy ngành mu một bên).",
                "principles": "Điều trị bảo tồn, giảm đau, cho phép tì đè sớm có trợ đỡ.",
                "management": "Điều trị bảo tồn, giảm đau, cho phép tì đè sớm có trợ đỡ.",
                "technique_id": "56-1",
                "button_label": "Xem Kỹ thuật 56-1 (Tiếp cận Khung chậu Stoppa)"
            },
            {
                "type": "Tile B",
                "code": "Tile B",
                "name": "Mất vững xoay, còn vững dọc (Partially Stable / Rotationally Unstable)",
                "desc": "Tổn thương một phần cung sau (giãn khớp chậu cùng trước, rách dây chằng cùng gai/cùng ụ ngồi). Gồm B1 (cuốn sách mở - Open book), B2 (ép bên - Lateral compression), B3 (tổn thương xoay hai bên).",
                "description": "Tổn thương một phần cung sau (giãn khớp chậu cùng trước, rách dây chằng cùng gai/cùng ụ ngồi). Gồm B1 (cuốn sách mở - Open book), B2 (ép bên - Lateral compression), B3 (tổn thương xoay hai bên).",
                "principles": "Đóng khung cố định ngoài hoặc nẹp vít kết hợp xương khớp mu lối trước (Stoppa / Pfannenstiel).",
                "management": "Đóng khung cố định ngoài hoặc nẹp vít kết hợp xương khớp mu lối trước (Stoppa / Pfannenstiel).",
                "technique_id": "56-8",
                "button_label": "Xem Kỹ thuật 56-8 (ORIF Khớp mu lối trước)"
            },
            {
                "type": "Tile C",
                "code": "Tile C",
                "name": "Mất vững hoàn toàn cả xoay và dọc (Unstable)",
                "desc": "Đứt rách hoàn toàn cung sau (khớp chậu cùng hoặc gãy cánh chậu/xương cùng qua lỗ thần kinh). Di lệch dọc lên trên do lực xé dọc (Vertical shear).",
                "description": "Đứt rách hoàn toàn cung sau (khớp chậu cùng hoặc gãy cánh chậu/xương cùng qua lỗ thần kinh). Di lệch dọc lên trên do lực xé dọc (Vertical shear).",
                "principles": "Cấp cứu hồi sức cầm máu (khung kẹp chậu C-clamp, nhét gạc chậu hông), sau đó mổ kết hợp xương vững chắc cả cung trước và cung sau (vít chậu cùng SI screw, nẹp mặt sau).",
                "management": "Cấp cứu hồi sức cầm máu (khung kẹp chậu C-clamp, nhét gạc chậu hông), sau đó mổ kết hợp xương vững chắc cả cung trước và cung sau (vít chậu cùng SI screw, nẹp mặt sau).",
                "technique_id": "56-10",
                "button_label": "Xem Kỹ thuật 56-10 (Bắt vít chậu cùng SI screw)"
            }
        ],
        "techniques": ["56-1", "56-2", "56-8", "56-10"]
    },
    {
        "id": "lauge_hansen",
        "name": "Phân loại Lauge-Hansen",
        "en_name": "Lauge-Hansen Ankle Fracture Classification",
        "bone": "Ankle (Fibula & Tibia)",
        "bone_vi": "Cổ chân & Mắt cá",
        "svg_ids": ["FibulaLeft", "FibulaRight", "l_Fibula", "r_Fibula"],
        "category": "Foot & Ankle",
        "chapter": 54,
        "pdf_page": 3088,
        "description": "Hệ thống phân loại kinh điển của Campbell dựa trên 2 yếu tố: Tư thế bàn chân lúc chấn thương (Supination/Pronation) và Hướng của lực xoay (External Rotation / Abduction / Adduction).",
        "types": [
            {
                "type": "SER",
                "code": "SER",
                "name": "Supination - External Rotation (Bàn chân ngửa - xoay ngoài)",
                "desc": "Chiếm 60-70% gãy cổ chân. Độ 1: Đứt AiTFL; Độ 2: Gãy chéo xoắn xương mác ngang mộng chày mác; Độ 3: Gãy mắt cá sau Volkmann; Độ 4: Đứt dây chằng delta hoặc gãy mắt cá trong.",
                "description": "Chiếm 60-70% gãy cổ chân. Độ 1: Đứt AiTFL; Độ 2: Gãy chéo xoắn xương mác ngang mộng chày mác; Độ 3: Gãy mắt cá sau Volkmann; Độ 4: Đứt dây chằng delta hoặc gãy mắt cá trong.",
                "principles": "SER 1-2 vững có thể bó bột; SER 3-4 mất vững mộng chày mác bắt buộc mổ mở nẹp vít mắt cá ngoài và bắt vít mắt cá trong/sau.",
                "management": "SER 1-2 vững có thể bó bột; SER 3-4 mất vững mộng chày mác bắt buộc mổ mở nẹp vít mắt cá ngoài và bắt vít mắt cá trong/sau.",
                "technique_id": "54-1",
                "button_label": "Xem Kỹ thuật 54-1 (ORIF Mắt cá ngoài)"
            },
            {
                "type": "PER",
                "code": "PER",
                "name": "Pronation - External Rotation (Bàn chân sấp - xoay ngoài)",
                "desc": "Bàn chân sấp - xoay ngoài. Độ 1: Gãy mắt cá trong; Độ 2: Rách toàn bộ AiTFL và màng gian cốt; Độ 3: Gãy chéo cao xương mác (Maisonneuve / Weber C); Độ 4: Đứt PiTFL / gãy Volkmann.",
                "description": "Bàn chân sấp - xoay ngoài. Độ 1: Gãy mắt cá trong; Độ 2: Rách toàn bộ AiTFL và màng gian cốt; Độ 3: Gãy chéo cao xương mác (Maisonneuve / Weber C); Độ 4: Đứt PiTFL / gãy Volkmann.",
                "principles": "Bắt buộc mổ nẹp vít xương mác và BẮT VÍT HOẶC DÂY TIE-IN CỐ ĐỊNH DÂY CHẰNG CHÀY MÁC DƯỚI (Syndesmotic fixation).",
                "management": "Bắt buộc mổ nẹp vít xương mác và BẮT VÍT HOẶC DÂY TIE-IN CỐ ĐỊNH DÂY CHẰNG CHÀY MÁC DƯỚI (Syndesmotic fixation).",
                "technique_id": "89-1",
                "button_label": "Xem Kỹ thuật 89-1 (Phục hồi Dây chằng Chày mác dưới)"
            }
        ],
        "techniques": ["54-1", "54-2", "89-1"]
    },
    {
        "id": "kellgren_lawrence",
        "name": "Phân loại Thoái hóa Khớp Gối Kellgren-Lawrence (K-L)",
        "en_name": "Kellgren-Lawrence Knee Osteoarthritis Grading System",
        "bone": "Knee Joint",
        "bone_vi": "Khớp gối",
        "svg_ids": ["FemurLeft", "FemurRight", "TibiaLeft", "TibiaRight", "l_Femur", "r_Femur"],
        "category": "Knee & Lower Leg",
        "chapter": 7,
        "pdf_page": 435,
        "description": "Phân loại chuẩn quốc tế trên X-quang đứng chịu lực để quyết định chỉ định bảo tồn, cắt xương chỉnh trục (HTO) hay thay khớp (UKA/TKA).",
        "types": [
            {
                "type": "Độ 2-3",
                "code": "Độ 2-3",
                "name": "Thoái hóa mức độ nhẹ đến vừa (Chồi xương, hẹp khe khớp 1 ngăn)",
                "desc": "Chồi xương rõ ở rìa khớp, khe khớp hẹp khu trú một ngăn trong hoặc ngăn ngoài, trục gối vẹo nhẹ.",
                "description": "Chồi xương rõ ở rìa khớp, khe khớp hẹp khu trú một ngăn trong hoặc ngăn ngoài, trục gối vẹo nhẹ.",
                "principles": "Bệnh nhân trẻ tuổi (<60 tuổi): Cắt xương chày chỉnh trục HTO (TomoFix) hoặc thay khớp gối đơn ngăn UKA.",
                "management": "Bệnh nhân trẻ tuổi (<60 tuổi): Cắt xương chày chỉnh trục HTO (TomoFix) hoặc thay khớp gối đơn ngăn UKA.",
                "technique_id": "9-1",
                "button_label": "Xem Kỹ thuật 9-1 (Cắt xương chỉnh trục HTO)"
            },
            {
                "type": "Độ 4",
                "code": "Độ 4",
                "name": "Thoái hóa khớp gối nặng tiến triển giai đoạn cuối (Severe OA)",
                "desc": "Mất hoàn toàn khe khớp (tiếp xúc xương tựa xương), đặc xương dưới sụn lan tỏa, biến dạng bề mặt lồi cầu và mâm chày nặng.",
                "description": "Mất hoàn toàn khe khớp (tiếp xúc xương tựa xương), đặc xương dưới sụn lan tỏa, biến dạng bề mặt lồi cầu và mâm chày nặng.",
                "principles": "Chỉ định vàng: Phẫu thuật Thay khớp gối toàn phần (Total Knee Arthroplasty - TKA).",
                "management": "Chỉ định vàng: Phẫu thuật Thay khớp gối toàn phần (Total Knee Arthroplasty - TKA).",
                "technique_id": "7-1",
                "button_label": "Xem Kỹ thuật 7-1 (Thay khớp gối toàn phần TKA)"
            }
        ],
        "techniques": ["7-1", "7-2", "9-1"]
    },
    {
        "id": "allman_neer_clavicle",
        "name": "Phân loại Gãy Xương Đòn Allman & Neer",
        "en_name": "Allman-Neer Clavicle Fracture Classification",
        "bone": "Clavicle",
        "bone_vi": "Xương đòn",
        "svg_ids": ["ClavicleLeft", "ClavicleRight", "l_Clavicle", "r_Clavicle"],
        "category": "Shoulder & Elbow",
        "chapter": 57,
        "pdf_page": 2930,
        "description": "Phân loại gãy xương đòn theo vị trí giải phẫu và độ mất vững của phức hợp dây chằng quạ đòn.",
        "types": [
            {
                "type": "Group I",
                "code": "Group I",
                "name": "Gãy 1/3 giữa thân xương đòn (Midshaft)",
                "desc": "Chiếm 80% gãy xương đòn. Mảnh trung tâm bị cơ ức đòn chũm kéo lên, mảnh ngoại vi bị trọng lượng chi kéo xuống.",
                "description": "Chiếm 80% gãy xương đòn. Mảnh trung tâm bị cơ ức đòn chũm kéo lên, mảnh ngoại vi bị trọng lượng chi kéo xuống.",
                "principles": "Di lệch ngắn >2cm, gãy vụn hoặc đe dọa da: Mổ nẹp vít nén ép 3.5mm mặt trên.",
                "management": "Di lệch ngắn >2cm, gãy vụn hoặc đe dọa da: Mổ nẹp vít nén ép 3.5mm mặt trên.",
                "technique_id": "57-1",
                "button_label": "Xem Kỹ thuật 57-1 (ORIF Thân xương đòn)"
            },
            {
                "type": "Group II",
                "code": "Group II",
                "name": "Gãy 1/3 ngoài xương đòn (Distal Clavicle - Neer II)",
                "desc": "Đứt hoặc rách phức hợp dây chằng quạ đòn (mất vững cao, tỷ lệ khớp giả >30%).",
                "description": "Đứt hoặc rách phức hợp dây chằng quạ đòn (mất vững cao, tỷ lệ khớp giả >30%).",
                "principles": "Chỉ định mổ mở nẹp móc (Hook plate) hoặc nẹp khóa đầu ngoài kèm neo chỉ tái tạo quạ đòn.",
                "management": "Chỉ định mổ mở nẹp móc (Hook plate) hoặc nẹp khóa đầu ngoài kèm neo chỉ tái tạo quạ đòn.",
                "technique_id": "57-2",
                "button_label": "Xem Kỹ thuật 57-2 (ORIF Đầu ngoài xương đòn)"
            }
        ],
        "techniques": ["57-1", "57-2"]
    },
    {
        "id": "mayo_olecranon",
        "name": "Phân loại Gãy Mỏm Khuỷu Mayo",
        "en_name": "Mayo Olecranon Fracture Classification",
        "bone": "Ulna (Olecranon)",
        "bone_vi": "Mỏm khuỷu xương trụ",
        "svg_ids": ["UlnaLeft", "UlnaRight", "l_Ulna", "r_Ulna"],
        "category": "Shoulder & Elbow",
        "chapter": 57,
        "pdf_page": 2965,
        "description": "Phân loại gãy mỏm khuỷu dựa trên 3 tiêu chí: Độ di lệch, Độ gãy vụn và Độ mất vững của khớp khuỷu.",
        "types": [
            {
                "type": "Type IIA",
                "code": "Type IIA",
                "name": "Di lệch, gãy đơn giản, khớp khuỷu vững",
                "desc": "Mất cơ chế duỗi chủ động nhưng khớp cánh tay trụ vẫn thẳng trục vững vàng.",
                "description": "Mất cơ chế duỗi chủ động nhưng khớp cánh tay trụ vẫn thẳng trục vững vàng.",
                "principles": "Phẫu thuật buộc néo ép chỉ thép qua 2 kim Kirschner (Tension Band Wiring - TBW).",
                "management": "Phẫu thuật buộc néo ép chỉ thép qua 2 kim Kirschner (Tension Band Wiring - TBW).",
                "technique_id": "57-8",
                "button_label": "Xem Kỹ thuật 57-8 (TBW Mỏm khuỷu)"
            },
            {
                "type": "Type IIB / III",
                "code": "Type IIB / III",
                "name": "Gãy nhiều mảnh vụn hoặc kèm trật khớp khuỷu",
                "desc": "Gãy vụn nát mỏm khuỷu phạm diện khớp hoặc kèm mất vững khớp cánh tay trụ.",
                "description": "Gãy vụn nát mỏm khuỷu phạm diện khớp hoặc kèm mất vững khớp cánh tay trụ.",
                "principles": "Mổ mở nắn chỉnh giải phẫu và cố định vững chắc bằng nẹp khóa giải phẫu mỏm khuỷu.",
                "management": "Mổ mở nắn chỉnh giải phẫu và cố định vững chắc bằng nẹp khóa giải phẫu mỏm khuỷu.",
                "technique_id": "57-11",
                "button_label": "Xem Kỹ thuật 57-11 (Nẹp khóa mỏm khuỷu)"
            }
        ],
        "techniques": ["57-8", "57-11"]
    },
    {
        "id": "tlics_spine",
        "name": "Thang điểm Chấn thương Cột sống Ngực Thắt lưng TLICS",
        "en_name": "Thoracolumbar Injury Classification and Severity Score (TLICS)",
        "bone": "Thoracolumbar Spine",
        "bone_vi": "Cột sống ngực - thắt lưng",
        "svg_ids": ["SpineThoracic", "SpineLumbar", "l_Spine", "r_Spine"],
        "category": "Spine",
        "chapter": 38,
        "pdf_page": 1815,
        "description": "Hệ thống tính điểm toàn diện để ra quyết định phẫu thuật gãy cột sống dựa trên hình thái gãy, thần kinh và tính toàn vẹn của dây chằng sau (PLC).",
        "types": [
            {
                "type": "TLICS <= 3",
                "code": "TLICS <= 3",
                "name": "Tổng điểm TLICS <= 3 (Điều trị bảo tồn)",
                "desc": "Gãy lún đơn thuần, thần kinh nguyên vẹn và phức hợp dây chằng sau nguyên vẹn.",
                "description": "Gãy lún đơn thuần, thần kinh nguyên vẹn và phức hợp dây chằng sau nguyên vẹn.",
                "principles": "Điều trị nội khoa, bất động bằng áo nẹp cứng ngực thắt lưng (TLSO) trong 8-12 tuần.",
                "management": "Điều trị nội khoa, bất động bằng áo nẹp cứng ngực thắt lưng (TLSO) trong 8-12 tuần.",
                "technique_id": "38-1",
                "button_label": "Xem Kỹ thuật 38-1 (Đánh giá Cột sống)"
            },
            {
                "type": "TLICS >= 5",
                "code": "TLICS >= 5",
                "name": "Tổng điểm TLICS >= 5 (Chỉ định Phẫu thuật Bắt buộc)",
                "desc": "Gãy mất vững do cơ chế xé rách/cắt xoay, có tổn thương rách phức hợp dây chằng sau hoặc có tổn thương thần kinh tiến triển.",
                "description": "Gãy mất vững do cơ chế xé rách/cắt xoay, có tổn thương rách phức hợp dây chằng sau hoặc có tổn thương thần kinh tiến triển.",
                "principles": "Phẫu thuật cấp cứu giải ép tủy và nắn chỉnh bắt vít cuống sống nẹp cột sống hàn xương lối sau.",
                "management": "Phẫu thuật cấp cứu giải ép tủy và nắn chỉnh bắt vít cuống sống nẹp cột sống hàn xương lối sau.",
                "technique_id": "41-15",
                "button_label": "Xem Kỹ thuật 41-15 (Bắt vít cuống sống nẹp cột sống)"
            }
        ],
        "techniques": ["38-1", "41-15"]
    },
    {
        "id": "gartland_supracondylar",
        "name": "Phân loại Gãy Trên Lồi Cầu Xương Cánh Tay Trẻ Em Gartland",
        "en_name": "Gartland Pediatric Supracondylar Humerus Fracture Classification",
        "bone": "Humerus (Distal)",
        "bone_vi": "Đầu dưới xương cánh tay",
        "svg_ids": ["HumerusLeft", "HumerusRight", "l_Humerus", "r_Humerus"],
        "category": "Shoulder & Elbow",
        "chapter": 36,
        "pdf_page": 1720,
        "description": "Phân loại cấp cứu chấn thương nhi khoa phổ biến nhất theo độ di lệch của mảnh gãy đầu dưới xương cánh tay.",
        "types": [
            {
                "type": "Type I",
                "code": "Type I",
                "name": "Gãy không di lệch (Non-displaced)",
                "desc": "Đường gãy không di lệch, đường trước xương cánh tay vẫn đi qua 1/3 giữa chỏm con.",
                "description": "Đường gãy không di lệch, đường trước xương cánh tay vẫn đi qua 1/3 giữa chỏm con.",
                "principles": "Bó bột cánh cẳng bàn tay gập khuỷu 90° cẳng tay trung tính trong 3-4 tuần.",
                "management": "Bó bột cánh cẳng bàn tay gập khuỷu 90° cẳng tay trung tính trong 3-4 tuần.",
                "technique_id": "36-1",
                "button_label": "Xem Kỹ thuật 36-1 (Bất động gãy trên lồi cầu)"
            },
            {
                "type": "Type II & III",
                "code": "Type II & III",
                "name": "Gãy gập góc di lệch hoàn toàn (Displaced)",
                "desc": "Mảnh gãy di lệch ra sau hoặc xoay, có nguy cơ chèn ép thần kinh quay, thần kinh giữa và động mạch cánh tay.",
                "description": "Mảnh gãy di lệch ra sau hoặc xoay, có nguy cơ chèn ép thần kinh quay, thần kinh giữa và động mạch cánh tay.",
                "principles": "Nắn kín cấp cứu dưới màn tăng sáng C-arm và ghim 2-3 kim Kirschner qua da (CRPP).",
                "management": "Nắn kín cấp cứu dưới màn tăng sáng C-arm và ghim 2-3 kim Kirschner qua da (CRPP).",
                "technique_id": "36-2",
                "button_label": "Xem Kỹ thuật 36-2 (Nắn kín ghim kim CRPP)"
            }
        ],
        "techniques": ["36-1", "36-2"]
    },
    {
        "id": "lichtman_kienbock",
        "name": "Phân loại Hoại tử Vô mạch Xương Nguyệt Lichtman (Kienböck)",
        "en_name": "Lichtman Classification of Kienböck Disease",
        "bone": "Lunate Carpal Bone",
        "bone_vi": "Xương nguyệt",
        "svg_ids": ["CarpalsLeft", "CarpalsRight", "l_Carpals", "r_Carpals"],
        "category": "Hand & Wrist",
        "chapter": 69,
        "pdf_page": 3520,
        "description": "Phân loại 4 giai đoạn tiến triển của bệnh lý hoại tử vô mạch xương nguyệt dựa trên X-quang và MRI để định hướng phẫu thuật bảo tồn hay hàn khớp.",
        "types": [
            {
                "type": "Stage II-IIIA",
                "code": "Stage II-IIIA",
                "name": "Xơ hóa hoặc xẹp lún chưa mất vững cổ tay",
                "desc": "Xương nguyệt tăng đậm độ hoặc xẹp lún nhưng xương thuyền chưa xoay gập (chưa có biến dạng DISI).",
                "description": "Xương nguyệt tăng đậm độ hoặc xẹp lún nhưng xương thuyền chưa xoay gập (chưa có biến dạng DISI).",
                "principles": "Phẫu thuật Cắt ngắn xương quay (Radial shortening osteotomy) nếu phương sai xương trụ âm tính.",
                "management": "Phẫu thuật Cắt ngắn xương quay (Radial shortening osteotomy) nếu phương sai xương trụ âm tính.",
                "technique_id": "69-21",
                "button_label": "Xem Kỹ thuật 69-21 (Cắt ngắn xương quay)"
            },
            {
                "type": "Stage IIIB-IV",
                "code": "Stage IIIB-IV",
                "name": "Xẹp lún mất vững cổ tay hoặc thoái hóa toàn bộ (SLAC)",
                "desc": "Xương nguyệt tiêu hủy kèm thoái hóa diện khớp quay - cổ tay và khớp gian cổ tay.",
                "description": "Xương nguyệt tiêu hủy kèm thoái hóa diện khớp quay - cổ tay và khớp gian cổ tay.",
                "principles": "Cắt bỏ hàng xương cổ tay thứ nhất (PRC) hoặc Hàn cứng khớp cổ tay 4 góc.",
                "management": "Cắt bỏ hàng xương cổ tay thứ nhất (PRC) hoặc Hàn cứng khớp cổ tay 4 góc.",
                "technique_id": "69-28",
                "button_label": "Xem Kỹ thuật 69-28 (Hàn khớp cổ tay)"
            }
        ],
        "techniques": ["69-21", "69-28"]
    },
    {
        "id": "herbert_scaphoid",
        "name": "Phân loại Gãy Xương Thuyền Herbert & Fisher",
        "en_name": "Herbert and Fisher Scaphoid Fracture Classification",
        "bone": "Scaphoid",
        "bone_vi": "Xương thuyền",
        "svg_ids": ["CarpalsLeft", "CarpalsRight", "l_Carpals", "r_Carpals"],
        "category": "Hand & Wrist",
        "chapter": 67,
        "pdf_page": 3410,
        "description": "Phân loại định hướng phẫu thuật bắt vít nén ép không mũ (Herbert screw) dựa trên tính ổn định sinh học cơ học của ổ gãy xương thuyền.",
        "types": [
            {
                "type": "Type A",
                "code": "Type A",
                "name": "Gãy vững cấp tính (Stable Acute Fractures)",
                "desc": "Gãy củ xương thuyền hoặc nứt rạn không hoàn toàn qua eo xương thuyền.",
                "description": "Gãy củ xương thuyền hoặc nứt rạn không hoàn toàn qua eo xương thuyền.",
                "principles": "Bó bột ôm ngón cái (Thumb spica) 6-8 tuần hoặc bắt vít nén ép qua da để vận động sớm.",
                "management": "Bó bột ôm ngón cái (Thumb spica) 6-8 tuần hoặc bắt vít nén ép qua da để vận động sớm.",
                "technique_id": "67-14",
                "button_label": "Xem Kỹ thuật 67-14 (Cố định xương thuyền)"
            },
            {
                "type": "Type B & D",
                "code": "Type B & D",
                "name": "Gãy không vững cấp tính hoặc khớp giả (Unstable / Nonunion)",
                "desc": "Gãy ngang hoàn toàn qua eo, gãy cực gần hoặc khớp giả sập gập hình lưng lạc đà.",
                "description": "Gãy ngang hoàn toàn qua eo, gãy cực gần hoặc khớp giả sập gập hình lưng lạc đà.",
                "principles": "Mổ nắn chỉnh mở hoặc kín bắt vít nén ép Herbert kết hợp ghép xương xốp mào chậu tự thân.",
                "management": "Mổ nắn chỉnh mở hoặc kín bắt vít nén ép Herbert kết hợp ghép xương xốp mào chậu tự thân.",
                "technique_id": "69-5",
                "button_label": "Xem Kỹ thuật 69-5 (Ghép xương & Bắt vít Herbert)"
            }
        ],
        "techniques": ["67-14", "69-5"]
    },
    {
        "id": "cierny_mader",
        "name": "Phân loại Viêm Tủy Xương Cierny-Mader",
        "en_name": "Cierny-Mader Staging System for Osteomyelitis",
        "bone": "Long Bones",
        "bone_vi": "Xương dài & Toàn thân",
        "svg_ids": ["TibiaLeft", "TibiaRight", "FemurLeft", "FemurRight", "l_Tibia", "r_Tibia"],
        "category": "General Principles",
        "chapter": 21,
        "pdf_page": 890,
        "description": "Hệ thống phân giai đoạn viêm xương tủy xương mạn tính chuẩn quốc tế kết hợp tổn thương giải phẫu xương và tình trạng miễn dịch ký chủ.",
        "types": [
            {
                "type": "Stage 1-2",
                "code": "Stage 1-2",
                "name": "Viêm trong tủy hoặc viêm bề mặt xương",
                "desc": "Ổ nhiễm trùng khu trú bên trong ống tủy hoặc trên bề mặt ngoài của vỏ xương.",
                "description": "Ổ nhiễm trùng khu trú bên trong ống tủy hoặc trên bề mặt ngoài của vỏ xương.",
                "principles": "Khoan nạo lòng tủy hoặc bạt vỏ xương hoại tử kết hợp chuyển vạt che phủ giàu mạch máu.",
                "management": "Khoan nạo lòng tủy hoặc bạt vỏ xương hoại tử kết hợp chuyển vạt che phủ giàu mạch máu.",
                "technique_id": "21-1",
                "button_label": "Xem Kỹ thuật 21-1 (Nạo viêm tủy xương)"
            },
            {
                "type": "Stage 3-4",
                "code": "Stage 3-4",
                "name": "Viêm khu trú hoặc viêm lan tỏa mất vững xương",
                "desc": "Ổ viêm ăn thủng vỏ xương hoặc mục nát toàn bộ chu vi thân xương làm mất tính vững cơ học.",
                "description": "Ổ viêm ăn thủng vỏ xương hoặc mục nát toàn bộ chu vi thân xương làm mất tính vững cơ học.",
                "principles": "Cắt bỏ toàn bộ đoạn xương chết hoại tử, đặt chuỗi hạt xi măng kháng sinh PMMA và ghép xương tái tạo thì hai.",
                "management": "Cắt bỏ toàn bộ đoạn xương chết hoại tử, đặt chuỗi hạt xi măng kháng sinh PMMA và ghép xương tái tạo thì hai.",
                "technique_id": "21-4",
                "button_label": "Xem Kỹ thuật 21-4 (Chuỗi hạt kháng sinh PMMA)"
            }
        ],
        "techniques": ["21-1", "21-4"]
    },
    {
        "id": "tubiana_dupuytren",
        "name": "Phân loại Co Rút Cân Gan Tay Dupuytren Tubiana",
        "en_name": "Tubiana Classification of Dupuytren Disease",
        "bone": "Hand (Fascia)",
        "bone_vi": "Cân gan bàn tay & Ngón tay",
        "svg_ids": ["PhalangesLeft", "PhalangesRight", "l_Phalanges", "r_Phalanges"],
        "category": "Hand & Wrist",
        "chapter": 72,
        "pdf_page": 3615,
        "description": "Đánh giá mức độ co rút gập các ngón tay trong bệnh lý Dupuytren dựa trên tổng góc co rút của 3 khớp (MCP, PIP, DIP).",
        "types": [
            {
                "type": "Giai đoạn I-II",
                "code": "Giai đoạn I-II",
                "name": "Co rút nhẹ đến vừa (Tổng góc co rút 0° đến 90°)",
                "desc": "Dải xơ co rút khớp bàn ngón (MCP) hoặc khớp liên đốt gần (PIP) từ 0 đến 90 độ.",
                "description": "Dải xơ co rút khớp bàn ngón (MCP) hoặc khớp liên đốt gần (PIP) từ 0 đến 90 độ.",
                "principles": "Phẫu thuật Cắt bỏ cân gan tay chọn lọc (Limited Fasciectomy) qua đường rạch ziczac Bruner.",
                "management": "Phẫu thuật Cắt bỏ cân gan tay chọn lọc (Limited Fasciectomy) qua đường rạch ziczac Bruner.",
                "technique_id": "76-1",
                "button_label": "Xem Kỹ thuật 76-1 (Mổ cân bàn tay)"
            },
            {
                "type": "Giai đoạn III-IV",
                "code": "Giai đoạn III-IV",
                "name": "Co rút nặng tiến triển (Tổng góc co rút > 90°)",
                "desc": "Biến dạng gập dính ngón nặng, co rút cả bao khớp trước PIP, ảnh hưởng nghiêm trọng chức năng cầm nắm.",
                "description": "Biến dạng gập dính ngón nặng, co rút cả bao khớp trước PIP, ảnh hưởng nghiêm trọng chức năng cầm nắm.",
                "principles": "Phẫu thuật cắt cân mở rộng kết hợp mở giải phóng bao khớp bên (Capsulotomy) hoặc hàn cứng khớp PIP.",
                "management": "Phẫu thuật cắt cân mở rộng kết hợp mở giải phóng bao khớp bên (Capsulotomy) hoặc hàn cứng khớp PIP.",
                "technique_id": "76-2",
                "button_label": "Xem Kỹ thuật 76-2 (Giải phóng bao khớp)"
            }
        ],
        "techniques": ["76-1", "76-2"]
    },
    {
        "id": "tscherne_soft_tissue",
        "name": "Phân loại Tổn thương Phần mềm Kín Tscherne",
        "en_name": "Tscherne Classification of Closed Fractures",
        "bone": "Soft Tissue & Bones",
        "bone_vi": "Phần mềm & Xương chi",
        "svg_ids": ["TibiaLeft", "TibiaRight", "FemurLeft", "FemurRight", "l_Tibia", "r_Tibia"],
        "category": "General Principles",
        "chapter": 48,
        "pdf_page": 2680,
        "description": "Phân loại mức độ dập nát phần mềm bên dưới da nguyên vẹn trong gãy xương kín để dự báo nguy cơ chèn ép khoang.",
        "types": [
            {
                "type": "Độ 0-1",
                "code": "Độ 0-1",
                "name": "Tổn thương phần mềm kín mức độ nhẹ hoặc trung bình",
                "desc": "Gãy xương năng lượng thấp, trầy xước nông hoặc đụng dập cơ nhẹ, không đe dọa chèn ép khoang.",
                "description": "Gãy xương năng lượng thấp, trầy xước nông hoặc đụng dập cơ nhẹ, không đe dọa chèn ép khoang.",
                "principles": "Có thể phẫu thuật kết hợp xương sớm thì đầu trong 24 giờ đầu an toàn.",
                "management": "Có thể phẫu thuật kết hợp xương sớm thì đầu trong 24 giờ đầu an toàn.",
                "technique_id": "54-11",
                "button_label": "Xem Kỹ thuật 54-11 (Kết hợp xương đinh chày)"
            },
            {
                "type": "Độ 2-3",
                "code": "Độ 2-3",
                "name": "Đụng dập cơ sâu diện rộng, phỏng nước, hội chứng khoang",
                "desc": "Chấn thương năng lượng cao, phỏng nước căng, bóc tách ngầm dưới da nghiêm trọng hoặc đe dọa chèn ép khoang.",
                "description": "Chấn thương năng lượng cao, phỏng nước căng, bóc tách ngầm dưới da nghiêm trọng hoặc đe dọa chèn ép khoang.",
                "principles": "Bắt buộc rạch mở cân giải áp khoang (Fasciotomy) cấp cứu và đặt khung cố định ngoài tạm thời.",
                "management": "Bắt buộc rạch mở cân giải áp khoang (Fasciotomy) cấp cứu và đặt khung cố định ngoài tạm thời.",
                "technique_id": "48-1",
                "button_label": "Xem Kỹ thuật 48-1 (Mở cân giải áp Fasciotomy)"
            }
        ],
        "techniques": ["48-1", "54-11"]
    }
]

for nc in new_classifications:
    cleaned_fc.append(nc)

with open('data/fracture_classifications.json', 'w', encoding='utf-8') as f:
    json.dump(cleaned_fc, f, ensure_ascii=False, indent=2)

print(f"Standardized fracture_classifications.json with {len(cleaned_fc)} fully compliant classifications!")
