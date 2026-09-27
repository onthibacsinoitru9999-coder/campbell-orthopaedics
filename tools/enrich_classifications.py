import json
import os

CLASSIFICATIONS_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "fracture_classifications.json")

with open(CLASSIFICATIONS_PATH, "r", encoding="utf-8") as f:
    classes = json.load(f)

existing_ids = {c["id"] for c in classes}

new_classes = [
    {
        "id": "bado_monteggia",
        "name": "Phân loại Bado (Gãy trật Monteggia)",
        "en_name": "Bado Classification of Monteggia Fracture-Dislocations",
        "bone": "Ulna & Radius",
        "bone_vi": "Xương trụ & Khớp quay trụ trên",
        "svg_ids": ["UlnaLeft", "UlnaRight", "l_Ulna", "RadiusLeft", "RadiusRight", "l_Radius"],
        "category": "Elbow & Forearm",
        "chapter": 57,
        "chapter_title": "Fractures of Shoulder, Arm, and Forearm",
        "pdf_page": 3280,
        "book_page": "2960",
        "description": "Phân loại Bado chia tổn thương gãy xương trụ kèm trật chỏm xương quay thành 4 Type dựa theo hướng di lệch của chỏm xương quay.",
        "types": [
            {
                "type": "Type I",
                "code": "Type I",
                "name": "Trật chỏm quay ra TRƯỚC (Anterior dislocation)",
                "description": "Gãy thân xương trụ gập góc mở ra sau kèm trật chỏm xương quay ra trước. Thể phổ biến nhất ở cả người lớn và trẻ em (chiếm 70%).",
                "principles": "Nắn chỉnh giải phẫu tuyệt đối chiều dài và trục xoay xương trụ bằng nẹp nén ép vững chắc (DCP 3.5mm). Khi xương trụ về đúng giải phẫu, chỏm quay thường tự động về khớp.",
                "technique_id": "57-10",
                "technique_title": "Open Reduction and Internal Fixation of Forearm Fractures",
                "button_label": "Xem Kỹ thuật 57-10 (ORIF Thân xương cẳng tay)"
            },
            {
                "type": "Type II",
                "code": "Type II",
                "name": "Trật chỏm quay ra SAU (Posterior dislocation)",
                "description": "Gãy thân hoặc hành xương trụ gập góc mở ra trước kèm trật chỏm xương quay ra sau hoặc sau ngoài (thường gặp ở người lớn tuổi kèm tổn thương dây chằng bên).",
                "principles": "Mổ mở kết hợp xương nẹp nén ép vững chắc xương trụ. Nếu chỏm quay vẫn bán trật hoặc kẹt dây chằng vòng, phải mở kiểm tra khớp và tái tạo dây chằng vòng.",
                "technique_id": "57-10",
                "technique_title": "Open Reduction and Internal Fixation of Forearm Fractures",
                "button_label": "Xem Kỹ thuật 57-10 (Kết hợp nẹp nén ép xương trụ)"
            },
            {
                "type": "Type III",
                "code": "Type III",
                "name": "Trật chỏm quay sang BÊN / NGOÀI (Lateral dislocation)",
                "description": "Gãy hành xương trụ đoạn gần kèm trật chỏm xương quay sang bên ngoài. Thường gặp ở trẻ em sau lực vẹo trong tác động lên cẳng tay duỗi.",
                "principles": "Ở trẻ em ưu tiên nắn kín và bó bột cẳng bàn tay gập khuỷu. Ở người lớn mổ nẹp nén ép giải phẫu xương trụ.",
                "technique_id": "57-10",
                "technique_title": "Open Reduction of Monteggia Lesion",
                "button_label": "Xem Kỹ thuật 57-10 (Nắn chỉnh mở Monteggia)"
            },
            {
                "type": "Type IV",
                "code": "Type IV",
                "name": "Gãy CẢ HAI xương cẳng tay kèm trật chỏm quay ra trước",
                "description": "Gãy cả thân xương quay và xương trụ cùng mức kèm trật chỏm quay ra trước. Chấn thương năng lượng cao phức tạp.",
                "principles": "Mổ mở kết hợp xương vững chắc giải phẫu cả 2 xương bằng 2 nẹp nén ép riêng biệt qua 2 đường mổ độc lập (Henry trước ngoài và đường sau trong).",
                "technique_id": "57-10",
                "technique_title": "ORIF Both Bone Forearm Fractures",
                "button_label": "Xem Kỹ thuật 57-10 (ORIF Cả hai xương cẳng tay)"
            }
        ],
        "techniques": ["57-10", "57-1", "57-2"]
    },
    {
        "id": "galeazzi",
        "name": "Tổn thương Galeazzi (Gãy trật Galeazzi)",
        "en_name": "Galeazzi Fracture-Dislocations",
        "bone": "Radius & DRUJ",
        "bone_vi": "Xương quay & Khớp quay trụ dưới (DRUJ)",
        "svg_ids": ["RadiusLeft", "RadiusRight", "l_Radius", "CarpalsLeft", "CarpalsRight", "l_Carpals"],
        "category": "Elbow & Forearm",
        "chapter": 57,
        "chapter_title": "Fractures of Shoulder, Arm, and Forearm",
        "pdf_page": 3290,
        "book_page": "2970",
        "description": "Gãy thân xương quay đoạn 1/3 giữa hoặc 1/3 dưới kèm trật hoặc mất vững khớp quay trụ dưới (Distal Radioulnar Joint - DRUJ). Được mệnh danh là 'Gãy xương cần sự tôn trọng tuyệt đối'.",
        "types": [
            {
                "type": "Di lệch < 7.5cm từ khớp",
                "code": "Classic Galeazzi",
                "name": "Gãy xương quay cách diện khớp cổ tay < 7.5 cm",
                "description": "Nguy cơ tổn thương sụn tam giác (TFCC) và trật khớp quay trụ dưới cực cao (trên 90%).",
                "principles": "Bắt buộc mổ mở nắn chỉnh giải phẫu tuyệt đối chiều dài xương quay bằng nẹp LCDCP 3.5mm mặt trước (đường mổ Henry). Kiểm tra độ vững DRUJ: nếu mất vững, xuyên kim Kirschner cố định khớp quay trụ dưới hoặc khâu sụn TFCC.",
                "technique_id": "57-10",
                "technique_title": "Open Reduction and Fixation of Galeazzi Fractures",
                "button_label": "Xem Kỹ thuật 57-10 (ORIF Galeazzi qua đường Henry)"
            },
            {
                "type": "Di lệch > 7.5cm từ khớp",
                "code": "Proximal Galeazzi",
                "name": "Gãy xương quay cách diện khớp cổ tay > 7.5 cm",
                "description": "Tổn thương màng gian cốt ít lan rộng hơn, khớp DRUJ có thể tự vững sau khi nắn chỉnh xương quay chuẩn giải phẫu.",
                "principles": "Kết hợp xương nẹp nén ép vững chắc xương quay và kiểm tra độ trôi mỏm trâm trụ sau mổ dưới màn tăng sáng C-arm.",
                "technique_id": "57-10",
                "technique_title": "Fixation of Radius with Plate",
                "button_label": "Xem Kỹ thuật 57-10 (Kết hợp nẹp nén ép xương quay)"
            }
        ],
        "techniques": ["57-10", "57-3", "73-1"]
    },
    {
        "id": "winquist_hansen",
        "name": "Phân loại Winquist-Hansen (Gãy thân xương đùi)",
        "en_name": "Winquist-Hansen Femoral Shaft Fracture Classification",
        "bone": "Femur",
        "bone_vi": "Thân xương đùi",
        "svg_ids": ["FemurRight", "FemurLeft", "l_Femur"],
        "category": "Hip & Pelvis",
        "chapter": 54,
        "chapter_title": "Fractures of the Lower Extremity",
        "pdf_page": 3010,
        "book_page": "2700",
        "description": "Phân loại mức độ vỡ vụn vỏ xương thân xương đùi để quyết định chỉ định đóng đinh nội tủy có chốt tĩnh hay động (static vs dynamic reamed intramedullary nailing).",
        "types": [
            {
                "type": "Type 0",
                "code": "Type 0",
                "name": "Đường gãy đơn giản, không có mảnh rời",
                "description": "Gãy ngang hoặc gãy chéo ngắn đơn thuần, không có mảnh vỡ rời, tiếp xúc diện gãy 100%.",
                "principles": "Đóng đinh nội tủy có chốt xoay. Có thể chốt động (dynamic) hoặc chốt tĩnh cho phép tỳ đè chịu lực sớm.",
                "technique_id": "54-1",
                "technique_title": "Antegrade Intramedullary Nailing of the Femur",
                "button_label": "Xem Kỹ thuật 54-1 (Đóng đinh nội tủy xuôi dòng)"
            },
            {
                "type": "Type I",
                "code": "Type I",
                "name": "Mảnh vỡ nhỏ < 25% chu vi thân xương",
                "description": "Có mảnh vỡ bướm nhỏ không đáng kể, hai đầu xương chính tiếp xúc diện gãy > 75% chu vi.",
                "principles": "Đóng đinh nội tủy xuôi dòng có doa tủy, chốt tĩnh 2 đầu để kiểm soát xoay và chiều dài.",
                "technique_id": "54-1",
                "technique_title": "Reamed Intramedullary Nailing of Femur",
                "button_label": "Xem Kỹ thuật 54-1 (Đinh nội tủy có doa tủy)"
            },
            {
                "type": "Type II",
                "code": "Type II",
                "name": "Mảnh vỡ bướm chiếm 25% - 50% chu vi thân xương",
                "description": "Mảnh vỡ rời hình cánh bướm lớn hơn nhưng hai đầu đoạn gãy chính vẫn còn tiếp xúc diện gãy tối thiểu 50%.",
                "principles": "Bắt buộc đóng đinh nội tủy chốt tĩnh (static interlocking nailing) ở cả đầu gần và đầu xa để chống co ngắn và chống xoay.",
                "technique_id": "54-1",
                "technique_title": "Static Interlocking Nailing",
                "button_label": "Xem Kỹ thuật 54-1 (Đinh nội tủy chốt tĩnh 2 đầu)"
            },
            {
                "type": "Type III",
                "code": "Type III",
                "name": "Mảnh vỡ lớn > 50% chu vi thân xương",
                "description": "Mảnh gãy rời vỡ nát trên 50% chu vi, tiếp xúc trực tiếp giữa hai đoạn gãy chính bị mất hoàn toàn.",
                "principles": "Bắt buộc chốt tĩnh hai đầu với đinh nội tủy đường kính lớn. Tránh tỳ đè chịu tải toàn phần sớm cho đến khi có can xương bắc cầu.",
                "technique_id": "54-1",
                "technique_title": "Interlocking Nailing for Comminuted Fractures",
                "button_label": "Xem Kỹ thuật 54-1 (Đinh nội tủy cho gãy nát)"
            },
            {
                "type": "Type IV",
                "code": "Type IV",
                "name": "Gãy nát phân đoạn hoàn toàn (Segmental Comminution)",
                "description": "Thân xương đùi bị vỡ vụn nát toàn bộ chiều dài một đoạn xương, mất hoàn toàn tiếp xúc vỏ xương hai đầu gãy.",
                "principles": "Đóng đinh nội tủy có chốt tĩnh khóa đa hướng trên bàn kéo chỉnh hình. Giữ nguyên khối cơ màng xương bao bọc mảnh vỡ (sinh học), không mở ổ gãy bóc tách.",
                "technique_id": "54-1",
                "technique_title": "Bridge Nailing for Severe Segmental Comminution",
                "button_label": "Xem Kỹ thuật 54-1 (Đinh nội tủy bắc cầu sinh học)"
            }
        ],
        "techniques": ["54-1", "54-2", "54-3"]
    },
    {
        "id": "ruedi_allgower",
        "name": "Phân loại Rüedi-Allgöwer (Gãy Pilon chày)",
        "en_name": "Rüedi-Allgöwer Classification of Tibial Pilon Fractures",
        "bone": "Tibia (Distal/Pilon)",
        "bone_vi": "Đầu dưới xương chày (Trần chày/Pilon)",
        "svg_ids": ["TibiaLeft", "TibiaRight", "l_Tibia", "TarsalsLeft", "TarsalsRight", "l_Tarsals"],
        "category": "Foot & Ankle",
        "chapter": 54,
        "chapter_title": "Fractures of the Lower Extremity",
        "pdf_page": 3105,
        "book_page": "2795",
        "description": "Phân loại tổn thương gãy trần khớp chày sên (Pilon fracture) do lực dồn ép dọc trục năng lượng cao, chia làm 3 type dựa trên mức độ lún và di lệch diện khớp.",
        "types": [
            {
                "type": "Type I",
                "code": "Type I",
                "name": "Gãy trần khớp chày không di lệch diện khớp",
                "description": "Đường gãy thấu khớp nhưng mặt khớp trần chày không bị di lệch bậc thang hay phân ly mảnh gãy.",
                "principles": "Kết hợp xương nẹp nén ép bảo tồn diện khớp, hoặc nẹp nâng đỡ đặt dưới da ít xâm lấn (MIPO).",
                "technique_id": "54-20",
                "technique_title": "Minimally Invasive Plating of Pilon Fractures",
                "button_label": "Xem Kỹ thuật 54-20 (MIPO Nẹp Pilon chày)"
            },
            {
                "type": "Type II",
                "code": "Type II",
                "name": "Gãy trần khớp có di lệch nhưng không vỡ vụn nát",
                "description": "Diện khớp bị di lệch bậc thang rõ rệt nhưng các mảnh sụn khớp còn lớn, chưa bị lún nát trung tâm.",
                "principles": "Nắn chỉnh mở diện khớp giải phẫu tuyệt đối, cố định vững chắc bằng vít xốp hoặc nẹp nâng đỡ trước trong/trước ngoài.",
                "technique_id": "54-20",
                "technique_title": "Open Reduction and Internal Fixation of Pilon Fractures",
                "button_label": "Xem Kỹ thuật 54-20 (Mổ mở nắn chỉnh diện khớp Pilon)"
            },
            {
                "type": "Type III",
                "code": "Type III",
                "name": "Gãy lún vỡ vụn nát diện khớp nghiêm trọng",
                "description": "Mặt khớp trần chày bị lún sâu vào hành chày và vỡ nát thành nhiều mảnh nhỏ. Chấn thương năng lượng cực cao, phù nề bọng nước phần mềm nặng nề.",
                "principles": "Chiến lược 2 thì bắc cầu (Span-scan-plan): Thì 1 đặt khung cố định ngoài qua cổ chân và nẹp xương mác phục hồi chiều dài; Thì 2 kết hợp xương diện khớp và nẹp nâng đỡ khi phần mềm nhăn da.",
                "technique_id": "54-21",
                "technique_title": "Two-Stage Treatment and External Fixation of Pilon",
                "button_label": "Xem Kỹ thuật 54-21 (Điều trị 2 thì & Cố định ngoài Pilon)"
            }
        ],
        "techniques": ["54-20", "54-21", "54-22"]
    },
    {
        "id": "colles_smith_barton",
        "name": "Phân loại Gãy đầu dưới xương quay (Colles, Smith, Barton)",
        "en_name": "Classic Eponymous Distal Radius Fractures (Colles, Smith, Barton)",
        "bone": "Radius (Distal)",
        "bone_vi": "Đầu dưới xương quay & Cổ tay",
        "svg_ids": ["RadiusLeft", "RadiusRight", "l_Radius", "CarpalsLeft", "CarpalsRight", "l_Carpals"],
        "category": "Hand & Wrist",
        "chapter": 73,
        "chapter_title": "Fractures, Dislocations, and Ligamentous Injuries of the Wrist",
        "pdf_page": 3820,
        "book_page": "3500",
        "description": "Các dạng gãy kinh điển vùng đầu dưới xương quay được phân loại theo hướng di lệch của đầu gãy xa và tính chất phạm khớp.",
        "types": [
            {
                "type": "Colles Fracture",
                "code": "Gãy Colles",
                "name": "Gãy ngoài khớp gập góc ra SAU / LƯNG (Dorsal tilt - Dinner fork)",
                "description": "Gãy ngoài khớp cách diện khớp cổ tay 2-3 cm, đầu gãy xa di lệch ra sau, lên trên và nghiêng ngoài, tạo hình ảnh biến dạng thìa ăn cơm (dinner-fork deformity).",
                "principles": "Nắn kín bó bột cẳng bàn tay gập nhẹ cổ tay và nghiêng trụ. Nếu mất vững (lún vỏ xương lưng, tuổi trẻ, di lệch thứ phát), chỉ định mổ nẹp khóa lòng bàn tay (volar locking plate).",
                "technique_id": "73-1",
                "technique_title": "Volar Plating of Distal Radius Fractures",
                "button_label": "Xem Kỹ thuật 73-1 (Nẹp khóa lòng bàn tay Volar Plate)"
            },
            {
                "type": "Smith Fracture",
                "code": "Gãy Smith",
                "name": "Gãy gập góc ra TRƯỚC / GAN TAY (Volar tilt - Garden spade)",
                "description": "Thường gọi là gãy Colles ngược. Đầu gãy xa di lệch ra phía trước gan tay, tạo biến dạng hình lưỡi xẻng (garden-spade deformity). Thường rất mất vững.",
                "principles": "Hầu như luôn có chỉ định mổ mở nắn chỉnh và cố định bằng nẹp nâng đỡ hoặc nẹp khóa mặt lòng bàn tay (volar buttress plate).",
                "technique_id": "73-1",
                "technique_title": "Open Reduction and Internal Fixation of Smith Fracture",
                "button_label": "Xem Kỹ thuật 73-1 (Kết hợp xương nẹp mặt lòng gãy Smith)"
            },
            {
                "type": "Barton Fracture",
                "code": "Gãy Barton",
                "name": "Gãy trật bờ khớp đầu dưới xương quay (Intraarticular Fracture-Subluxation)",
                "description": "Gãy phạm khớp chéo vát qua bờ lưng hoặc bờ gan tay kèm trật khối xương cổ tay theo mảnh gãy. Thể bờ gan tay (Volar Barton) thường gặp và nguy hiểm hơn.",
                "principles": "Bắt buộc mổ nẹp nâng đỡ (buttress plate) để chống trượt khối cổ tay và nắn phẳng diện khớp tuyệt đối.",
                "technique_id": "73-1",
                "technique_title": "Fixation of Barton Fracture-Subluxation",
                "button_label": "Xem Kỹ thuật 73-1 (Nẹp nâng đỡ Barton gãy trật cổ tay)"
            }
        ],
        "techniques": ["73-1", "73-2", "73-3"]
    },
    {
        "id": "russell_taylor",
        "name": "Phân loại Russell-Taylor (Gãy dưới mấu chuyển xương đùi)",
        "en_name": "Russell-Taylor Subtrochanteric Femoral Fracture Classification",
        "bone": "Femur (Subtrochanteric)",
        "bone_vi": "Dưới mấu chuyển xương đùi",
        "svg_ids": ["FemurRight", "FemurLeft", "l_Femur"],
        "category": "Hip & Pelvis",
        "chapter": 55,
        "chapter_title": "Fractures and Dislocations of the Hip",
        "pdf_page": 3160,
        "book_page": "2840",
        "description": "Phân loại gãy vùng dưới mấu chuyển xương đùi dựa trên sự lan rộng của đường gãy vào hố mấu chuyển (piriformis fossa) và mấu động nhỏ để lựa chọn loại đinh nội tủy hoặc nẹp góc.",
        "types": [
            {
                "type": "Type IA",
                "code": "Type IA",
                "name": "Không lan vào hố mấu chuyển & mấu động nhỏ còn nguyên",
                "description": "Đường gãy hoàn toàn dưới mấu động nhỏ, hố mấu chuyển và mấu chuyển lớn nguyên vẹn.",
                "principles": "Chỉ định vàng là đóng đinh nội tủy có chốt tiêu chuẩn (standard interlocking nail). Phục hồi giải phẫu nhanh chóng.",
                "technique_id": "55-6",
                "technique_title": "Intramedullary Fixation of Subtrochanteric Fractures",
                "button_label": "Xem Kỹ thuật 55-6 (Đóng đinh nội tủy dưới mấu chuyển)"
            },
            {
                "type": "Type IB",
                "code": "Type IB",
                "name": "Không lan vào hố mấu chuyển nhưng mấu động nhỏ bị gãy",
                "description": "Mấu động nhỏ bị tổn thương (mất vững vách trong calcar) nhưng hố mấu chuyển vẫn còn nguyên vẹn.",
                "principles": "Đóng đinh nội tủy chốt đầu gần kiểu Gamma/Cephalomedullary nail hoặc nẹp góc nén ép 95 độ.",
                "technique_id": "55-7",
                "technique_title": "Cephalomedullary Nailing for Subtrochanteric Fractures",
                "button_label": "Xem Kỹ thuật 55-7 (Đinh nội tủy Cephalomedullary)"
            },
            {
                "type": "Type IIA",
                "code": "Type IIA",
                "name": "Đường gãy lan vào hố mấu chuyển nhưng mấu động nhỏ còn nguyên",
                "description": "Hố mấu chuyển bị đường gãy phá hủy, không thể sử dụng điểm vào đinh nội tủy tiêu chuẩn.",
                "principles": "Sử dụng đinh chốt qua đỉnh mấu chuyển lớn (trochanteric entry nail) hoặc nẹp góc nén ép 95 độ (condylar blade plate / DCS).",
                "technique_id": "55-8",
                "technique_title": "95-Degree Condylar Blade Plate Fixation",
                "button_label": "Xem Kỹ thuật 55-8 (Nẹp góc 95 độ bản lề)"
            },
            {
                "type": "Type IIB",
                "code": "Type IIB",
                "name": "Đường gãy lan vào CẢ hố mấu chuyển và mấu động nhỏ",
                "description": "Tổn thương cực kỳ mất vững ở cả điểm vào hố mấu chuyển và thành xương trong calcar.",
                "principles": "Kết hợp xương bằng nẹp khóa đầu trên xương đùi (proximal femoral locking plate) hoặc đinh nội tủy trochanteric tái tạo kèm buộc chỉ thép nâng đỡ.",
                "technique_id": "55-8",
                "technique_title": "Proximal Femoral Locked Plating",
                "button_label": "Xem Kỹ thuật 55-8 (Nẹp khóa đầu trên xương đùi)"
            }
        ],
        "techniques": ["55-6", "55-7", "55-8"]
    }
]

added = 0
for nc in new_classes:
    if nc["id"] not in existing_ids:
        classes.append(nc)
        existing_ids.add(nc["id"])
        added += 1

with open(CLASSIFICATIONS_PATH, "w", encoding="utf-8") as f:
    json.dump(classes, f, ensure_ascii=False, indent=2)

print(f"Added {added} new classifications. Total now: {len(classes)}")
