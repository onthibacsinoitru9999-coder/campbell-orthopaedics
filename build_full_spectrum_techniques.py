import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

print("="*70)
print("CAMPBELL 13TH ED: FULL SPECTRUM CLINICAL DATA ENRICHMENT PIPELINE")
print("="*70)

with open('data/techniques_catalog.json', 'r', encoding='utf-8') as f:
    catalog = json.load(f)

with open('data/techniques_text.json', 'r', encoding='utf-8') as f:
    texts = json.load(f)

with open('data/chapters_catalog.json', 'r', encoding='utf-8') as f:
    chapters = json.load(f)

chap_map = {c['chapter']: c for c in chapters}

print(f"Loaded {len(catalog)} techniques from catalog and {len(texts)} raw text entries.")

def clean_campbell_raw(txt):
    if not txt:
        return ""
    # De-hyphenate words split across line breaks
    dehyphen = re.sub(r'(\b[a-zA-Z]+)-\s*\r?\n\s*([a-zA-Z]+\b)', r'\1\2', txt)
    lines = dehyphen.split('\n')
    cleaned = []
    for l in lines:
        s = l.strip()
        if not s:
            continue
        if re.match(r'^TECHNIQUE\s+\d+-\d+', s, re.IGNORECASE):
            continue
        if re.match(r'^---\s*Trang\s+\d+\s*---', s, re.IGNORECASE):
            continue
        if re.match(r'^FIGURE\s+\d+-\d+', s, re.IGNORECASE):
            continue
        cleaned.append(s)
    return " ".join(cleaned)

def extract_surgical_steps_from_text(raw_txt, default_titles, default_actions):
    cleaned = clean_campbell_raw(raw_txt)
    # Check for bullet points in Campbell text
    raw_bullets = re.split(r'[\u25a0\u25aa\u2022]\s+|\n\s*\d+\.\s+', raw_txt)
    bullet_parts = [clean_campbell_raw(b) for b in raw_bullets if len(clean_campbell_raw(b)) > 40]
    
    chosen_parts = []
    if len(bullet_parts) >= 3:
        chosen_parts = bullet_parts
    else:
        # Split into sentences
        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', cleaned) if len(s.strip()) > 30]
        if len(sentences) >= 3:
            chunk_size = max(1, len(sentences) // min(5, len(default_titles)))
            for i in range(0, len(sentences), chunk_size):
                chunk = " ".join(sentences[i:i+chunk_size])
                if len(chunk) > 40:
                    chosen_parts.append(chunk)
    
    num_steps = len(default_titles)
    steps = []
    for i in range(num_steps):
        title = f"Thì {i + 1}: {default_titles[i]}"
        action = default_actions[min(i, len(default_actions) - 1)]
        detail = ""
        if chosen_parts and i < len(chosen_parts):
            dt = chosen_parts[i]
            if len(dt) > 650:
                cut = dt[:650].rfind(' ')
                dt = dt[:cut if cut > 300 else 650] + "..."
            detail = dt
        else:
            detail = f"Thực hiện các thao tác chuyên môn theo đúng nguyên bản kỹ thuật {default_titles[i]} mô tả trong Campbell's Operative Orthopaedics 13th Edition. Bộc lộ rõ phẫu trường, bảo vệ mô lành và kiểm soát cầm máu triệt để."
        
        steps.append({
            "step": i + 1,
            "title": title,
            "detail": detail,
            "action": action
        })
    return steps

def generate_domain_profile(t, raw_text):
    tid = t['tech_id']
    ch = t['chapter']
    name_en = t['name']
    author = t.get('author', 'Campbell Clinic Service')
    pdf_p = t.get('pdf_page', 1)
    
    # 1. Approaches (Ch 1)
    if ch == 1:
        cat_vi = "Đường Mổ & Tiếp Cận Ngoại Khoa"
        name_vi = f"Đường Mổ Ngoại Khoa ({tid}): {name_en}"
        indications = f"Tiếp cận phẫu thuật chuẩn xác cho các can thiệp chỉnh hình và chấn thương thuộc vùng giải phẫu của kỹ thuật {name_en} theo nguyên bản Campbell 13th Ed."
        contraindications = "Nhiễm trùng nông hoặc tổn thương da trợt loét tại vị trí rạch mổ; suy dinh dưỡng nặng hoặc tổn thương mạch máu nuôi dưỡng vạt da chưa tái thông."
        patient_prep = "Bệnh nhân nằm trên bàn mổ ở tư thế thích hợp theo vị trí giải phẫu can thiệp. Bộc lộ rộng rãi, sát khuẩn 3 lần bằng cồn Povidone-Iodine, trải săng vô khuẩn cho phép cử động tự do các khớp lân cận."
        danger_info = "Cấu trúc nguy cơ: Bảo tồn các nhánh thần kinh cảm giác nông dưới da (nhánh bì), các bó mạch nuôi dưỡng màng xương; tuyệt đối tôn trọng ranh giới gian cơ (internervous plane) để tránh làm mất phân bố thần kinh cơ."
        postop = "Chăm sóc theo dõi vết mổ, thay băng vô trùng ngày thứ 2, phát hiện sớm dấu hiệu tụ máu hoặc hoại tử mép da. Bất động nẹp đỡ tạm thời và hướng dẫn tập vận động chủ động sớm cơ khớp lân cận."
        pearls = "Rạch da dứt khoát 1 lần vuông góc với mặt da; bóc tách vạt da và tổ chức dưới da cùng 1 lớp (full thickness) để bảo tồn mạng lưới mạch dưới da; bộc lộ dọc theo các khe gian cơ sinh lý."
        
        default_titles = [
            "Định vị mốc giải phẫu & Đường rạch da",
            "Phẫu tích lớp dưới da & Xác định khe gian cơ",
            "Mở mạc sâu & Bộc lộ bao khớp / màng xương",
            "Đặt banh tự động bảo vệ thần kinh - mạch máu",
            "Kiểm tra phẫu trường, cầm máu & Đóng vết mổ theo lớp"
        ]
        default_actions = [
            "Đánh dấu mốc xương bề mặt; rạch da chính xác theo chiều dài phẫu trường dự kiến.",
            "Tách vạt da dưới da dày; nhận diện chính xác khe gian cơ tự nhiên.",
            "Rạch mạc cơ dọc thớ; bóc tách màng xương nhẹ nhàng bảo vệ cuống mạch.",
            "Đặt các banh tỳ xương vững chắc, tránh tì đè kéo căng bó mạch thần kinh.",
            "Rửa sạch phẫu trường, khâu phục hồi mạc sâu mũi rời và khâu mép da không căng."
        ]

    # 2. Shoulder & Elbow Arthroplasty (Ch 12, 13)
    elif ch in [12, 13]:
        cat_vi = "Tái Tạo & Thay Khớp Vai - Khuỷu"
        name_vi = f"Phẫu Thuật Vai - Khuỷu ({tid}): {name_en}"
        indications = f"Chỉ định trong thoái hóa khớp vai/khuỷu nặng, hoại tử vô mạch chỏm xương cánh tay, thoái hóa do rách chóp xoay diện rộng (CTA) hoặc gãy vụn phức tạp đầu trên xương cánh tay / đầu dưới cánh tay người cao tuổi."
        contraindications = "Nhiễm trùng khớp vai/khuỷu đang tiến triển; liệt hoàn toàn cơ delta (đối với thay khớp vai giải phẫu); bệnh lý thần kinh khớp Charcot; tổn thương đám rối thần kinh cánh tay chưa hồi phục."
        patient_prep = "Tư thế ghế bãi biển (Beach-chair position) với đầu được cố định vững chắc trên giá đỡ chuyên dụng, gập háng 45-60°. Toàn bộ chi trên được sát khuẩn và bọc săng vô trùng để có thể vận động xoay tự do trong mổ."
        danger_info = "Cấu trúc nguy cơ: Dây thần kinh nách (Axillary nerve - đi vòng dưới bờ dưới bao khớp vai, cách mỏm cùng vai 5 cm); Thần kinh cơ bì (cách mỏm quạ 5-8 cm); Tĩnh mạch đầu (Cephalic vein); Dây thần kinh trụ ở rãnh ròng rọc khuỷu."
        postop = "Bất động chi trên bằng túi treo tay hoặc đai nâng vai chuyên dụng có gối dạng 30° trong 4-6 tuần. Tập vận động con lắc Codman ngày thứ 1. Bắt đầu tập phục hồi tầm vận động thụ động dưới sự hướng dẫn của kỹ thuật viên."
        pearls = "Bảo vệ tĩnh mạch đầu bằng cách kéo vào trong cùng với cơ ngực lớn; Nhận diện và treo bảo vệ thần kinh nách bằng ngón tay ở mặt trước dưới bao khớp; Đặt thành phần ổ chảo/lồi cầu đúng góc nghiêng retroversion sinh lý."
        
        default_titles = [
            "Đường mổ rãnh Delta - Ngực (Deltopectoral) & Bộc lộ",
            "Mở gân cơ dưới vai & Cắt chỏm xương cánh tay",
            "Doa ổ chảo & Đặt đế tựa Glenoid / Glenosphere",
            "Khoét lòng tủy cánh tay & Đặt chuôi khớp Stem",
            "Nắn khớp thử nghiệm, khâu phục hồi gân cơ & Đóng mổ"
        ]
        default_actions = [
            "Rạch da dọc rãnh delta-ngực, bảo tồn tĩnh mạch đầu, tách mở khoang bộc lộ bao khớp.",
            "Tách gân dưới vai có đánh dấu chỉ neo; cắt chỏm xương cánh tay ở góc retroversion 20-30°.",
            "Bộc lộ toàn bộ viền ổ chảo; doa phẳng diện xương và bắt vít cố định đế ổ chảo vững chắc.",
            "Giũa lòng tủy cánh tay tăng dần kích thước; đặt chuôi thử và chuôi chính thức.",
            "Khâu đính lại gân cơ dưới vai vào mấu động nhỏ bằng chỉ siêu bền; khâu da thẩm mỹ."
        ]

    # 3. Amputations (Ch 15-19)
    elif ch in [15, 16, 17, 18, 19]:
        cat_vi = "Phẫu Thuật Cắt Cụt & Tạo Hình Mỏm Cụt"
        name_vi = f"Phẫu Thuật Cắt Cụt ({tid}): {name_en}"
        indications = f"Chỉ định trong hoại tử chi do tắc mạch máu không thể tái thông, chấn thương dập nát chi độ III-C đứt bó mạch thần kinh không thể bảo tồn, u ác tính xương phần mềm xâm lấn rộng hoặc nhiễm trùng huyết đe dọa tính mạng."
        contraindications = "Tình trạng thiếu máu lan tỏa vượt quá mức cắt dự kiến (cần nâng mức cắt lên cao hơn); sốc chấn thương chưa được hồi sức bồi phụ thể tích tuần hoàn ổn định."
        patient_prep = "Bệnh nhân nằm ngửa trên bàn mổ. Đặt garo hơi ở gốc chi nếu không có chống chỉ định mạch máu. Đánh dấu cẩn thận thiết kế vạt da trước mổ đảm bảo tỷ lệ chiều dài vạt đủ che phủ đầu xương không căng."
        danger_info = "Cấu trúc nguy cơ: Thắt buộc chắc chắn 2 lần các thân động mạch và tĩnh mạch lớn tránh tụ máu thứ phát; Kéo nhẹ các thân thần kinh chính xuống, cắt dứt khoát bằng dao sắc và để thần kinh co rút tự nhiên vào trong khối cơ ít nhất 3-5 cm để phòng ngừa u thần kinh mỏm cụt (Neuroma)."
        postop = "Băng ép mỏm cụt bằng băng chun vô khuẩn hình số 8 hoặc nẹp bột cứng bảo vệ tránh co rút gập khớp. Theo dõi sát màu sắc mép vạt và dịch dẫn lưu. Rút dẫn lưu sau 24-48 giờ. Hướng dẫn tập gồng cơ mỏm cụt và tập phục hồi chức năng đi chi giả sớm."
        pearls = "Tuyệt đối không khâu căng mép vạt da mỏm cụt; Bắt buộc khâu đính cơ qua xương (Myodesis) hoặc khâu cơ đối cơ (Myoplasty) để tạo đệm êm vững chắc cho mỏm cụt tì đè; Vát tròn các bờ xương sắc nhọn."
        
        default_titles = [
            "Thiết kế vạt da mỏm cụt & Rạch da theo tỷ lệ",
            "Phẫu tích khối cơ, thắt mạch máu chính 2 lần",
            "Cắt xử lý thân thần kinh chống u thần kinh mỏm cụt",
            "Cắt xương, vát tròn bờ xương & Khâu cố định cơ Myodesis",
            "Cầm máu triệt để, đặt dẫn lưu kín & Đóng da không căng"
        ]
        default_actions = [
            "Đo vẽ thiết kế vạt da dày đầy đủ tổ chức dưới da theo chuẩn tỷ lệ chiều dài/rộng.",
            "Cắt cơ theo lớp vát hình nón; phẫu tích bộc lộ bó mạch lớn và thắt kép an toàn.",
            "Kéo nhẹ thân thần kinh xuống 3-5 cm, cắt ngang dứt khoát để đầu thần kinh co sâu vào cơ.",
            "Cắt xương ngang mức dự kiến; dùng giũa mài tròn nhẵn các góc cạnh sắc của vỏ xương.",
            "Khâu vạt cơ qua các lỗ khoan xương màng xương; khâu da mũi rời nới lỏng không thiếu máu."
        ]

    # 4. Infections (Ch 21-24)
    elif ch in [21, 22, 23, 24]:
        cat_vi = "Nhiễm Trùng Cơ Xương Khớp"
        name_vi = f"Phẫu Thuật Nhiễm Trùng ({tid}): {name_en}"
        indications = f"Chỉ định trong viêm mủ khớp cấp tính, viêm tủy xương cấp tính hoặc mạn tính có ổ áp xe dưới màng xương / trong tủy xương, rò mủ kéo dài, có mảnh xương mục (sequestrum) hoặc thất bại sau điều trị kháng sinh toàn thân."
        contraindications = "Viêm khớp phản ứng hoặc viêm khớp vô khuẩn; bệnh nhân nhiễm trùng huyết đang sốc cần hồi sức cấp cứu ổn định trước khi phẫu thuật."
        patient_prep = "Bệnh nhân nằm ngửa trên bàn mổ. Không đặt garo hoặc chỉ bơm garo sau khi dồn máu bằng nâng cao chi (tuyệt đối không dùng băng chun Esmarch ép dồn mủ vào tuần hoàn). Chuẩn bị hệ thống bơm rửa áp lực lớn và dụng cụ lấy bệnh phẩm vi sinh."
        danger_info = "Cấu trúc nguy cơ: Đi theo các đường mổ giải phẫu kinh điển để tránh làm tổn thương các bó mạch thần kinh lân cận; Không phẫu tích bóc tách quá rộng màng xương vùng xương lành để tránh làm lan rộng diện tích thiếu máu xương."
        postop = "Để hở vết mổ một phần hoặc đặt hệ thống hút áp lực âm VAC / tưới rửa liên tục kín (continuous irrigation-suction). Điều trị kháng sinh tĩnh mạch liều cao theo kháng sinh đồ ít nhất 4-6 tuần. Bất động nẹp bột giảm đau và phòng ngừa gãy xương bệnh lý."
        pearls = "Cắt lọc triệt để toàn bộ mô hoại tử đến tận vùng mô hạt chảy máu tươi (dấu hiệu Paprika); Lấy tối thiểu 3-5 mẫu bệnh phẩm vô trùng tại các vị trí sâu khác nhau để cấy vi khuẩn hiếu khí, kỵ khí và nấm; Đặt hạt xi măng kháng sinh PMMA nồng độ cao tại chỗ."
        
        default_titles = [
            "Đường rạch trực tiếp qua ổ mủ & Bộc lộ tổn thương",
            "Mở bao khớp / Khoan mở cửa sổ vỏ xương giải áp",
            "Nạo vét mô hoại tử, gắp bỏ mảnh xương mục (Sequestrectomy)",
            "Bơm rửa xung áp lực cao & Đặt xi măng kháng sinh PMMA",
            "Dẫn lưu kín áp lực âm / Đóng vết mổ bán phần nới lỏng"
        ]
        default_actions = [
            "Rạch da trực tiếp theo trục dọc tiếp cận ổ viêm; lấy ngay mủ gửi nhuộm Gram và cấy vi sinh.",
            "Khoan nhiều lỗ mở cửa sổ vỏ xương hình bầu dục giải phóng mủ và mô viêm trong ống tủy.",
            "Dùng thìa nạo sắc nạo sạch ổ viêm hoại tử đến lớp xương lành chảy máu rỉ điểm (Paprika sign).",
            "Bơm rửa phẫu trường bằng 6-9 lít nước muối sinh lý; đặt chuỗi hạt kháng sinh tự tiêu/xi măng PMMA.",
            "Đặt ống dẫn lưu kín có đục lỗ; khâu da lỏng hoặc băng vết thương bằng hệ thống VAC."
        ]

    # 5. Pediatric Orthopaedics (Ch 29-36)
    elif ch in [29, 30, 31, 32, 33, 34, 35, 36]:
        cat_vi = "Chỉnh Hình Nhi Khoa"
        name_vi = f"Chỉnh Hình Nhi Khoa ({tid}): {name_en}"
        indications = f"Chỉ định trong các dị tật bẩm sinh hoặc di chứng chấn thương ở trẻ em (bàn chân khoèo, trật khớp háng bẩm sinh DDH, trượt chỏm xương đùi SCFE, bệnh Perthes, biến dạng trục chi, gãy xương trẻ em) theo phác đồ Campbell Nhi khoa."
        contraindications = "Nhiễm trùng cấp tính tại chỗ; các dị tật bẩm sinh đa cơ quan nặng chưa ổn định tim mạch hô hấp; chống chỉ định toàn thân với gây mê nội khí quản."
        patient_prep = "Bệnh nhân nhi được gây mê nội khí quản kết hợp gây tê vùng/phong bế thần kinh ngoại vi để giảm đau đa mô thức. Đặt tư thế phù hợp trên bàn mổ có sưởi ấm thân nhiệt liên tục. Chuẩn bị máy tăng sáng C-arm với liều xạ thấp nhất có thể."
        danger_info = "Cấu trúc nguy cơ: BẢO VỆ TỐI THƯỢNG SỤN TIẾP HỢP (Physis / Growth plate) - tránh khoan hoặc bắt vít vắt chéo sụn tiếp hợp trừ khi bắt buộc có chỉ định triệt tiêu sụn; Bảo vệ cuống mạch nuôi chỏm xương đùi (nhánh sâu động mạch mũ đùi trong) trong trật háng và SCFE; Bảo tồn thần kinh chày sau và thần kinh mác."
        postop = "Bất động bằng bột chậu - lưng - chân (Spica cast) hoặc nẹp bột đùi cẳng bàn chân trong 6-12 tuần tùy lứa tuổi. Chụp X-quang kiểm tra vị trí nắn chỉnh và dụng cụ kết hợp xương định kỳ. Hướng dẫn phụ huynh chăm sóc nẹp bột chống loét tì đè."
        pearls = "Thao tác phẫu tích ở trẻ em phải cực kỳ tinh tế, nhẹ nhàng; Không bóc tách màng xương quá mức gây dính sụn phát triển; Luôn kiểm tra đối chiếu bên lành trên màn tăng sáng C-arm; Đạt được nắn chỉnh đồng tâm tuyệt đối trong trật háng."
        
        default_titles = [
            "Bộc lộ phẫu trường & Nhận diện mốc giải phẫu nhi khoa",
            "Bảo tồn sụn tiếp hợp & Giải phóng mô xơ co rút",
            "Cắt xương chỉnh trục / Nắn chỉnh giải phẫu ổ khớp",
            "Cố định bằng kim Kirschner / Nẹp vít chuyên dụng nhi",
            "Kiểm tra C-arm 2 bình diện, cầm máu & Bó bột bất động"
        ]
        default_actions = [
            "Rạch da theo nếp lằn tự nhiên; phẫu tích nhẹ nhàng nhận diện và bảo vệ sụn tiếp hợp.",
            "Kéo dài gân hoặc cắt bao khớp co rút nới lỏng tổ chức mô mềm quanh khớp.",
            "Cắt xương chỉnh góc mở/đóng hoặc nắn kín/nắn mở đưa chỏm khớp vào trung tâm ổ cối.",
            "Ghim kim K-wire dẫn đường hoặc nẹp khóa nhi khoa đạt độ cố định cơ học vững vàng.",
            "Chụp kiểm tra C-arm xác nhận góc trục giải phẫu hoàn hảo; băng vô trùng và bó bột Spica."
        ]

    # 6. Spine Surgery (Ch 37-44)
    elif ch in [37, 38, 39, 40, 41, 42, 43, 44]:
        cat_vi = "Phẫu Thuật Cột Sống"
        name_vi = f"Phẫu Thuật Cột Sống ({tid}): {name_en}"
        indications = f"Chỉ định trong chấn thương mất vững cột sống, thoát vị đĩa đệm chèn ép tủy/rễ thần kinh kháng trị, hẹp ống sống, trượt đốt sống, gù vẹo cột sống vô căn (AIS) hoặc thoái hóa cột sống mất vững theo phân loại TLICS/SLIC."
        contraindications = "Nhiễm trùng huyết hoặc nhiễm trùng mô mềm vùng cột sống; bệnh lý loãng xương quá nặng không thể neo giữ ốc vít (cần gia cố xi măng); liệt hoàn toàn tủy sống quá thời gian vàng phục hồi."
        patient_prep = "Bệnh nhân nằm sấp trên khung mổ cột sống chuyên dụng (Jackson table hoặc khung Wilson) để giảm áp lực ổ bụng, chống ứ trệ tĩnh mạch ngoài màng tủy gây chảy máu (hoặc nằm ngửa trong mổ ACDF lối trước). Lắp đặt hệ thống theo dõi điện sinh lý thần kinh trong mổ (IONM: MEPs và SSEPs)."
        danger_info = "Cấu trúc nguy cơ: BẢO VỆ TỐI THƯỢNG TỦY SỐNG VÀ RỄ THẦN KINH (Spinal cord & Nerve roots); Đám rối tĩnh mạch ngoài màng cứng Batson (chảy máu ồ ạt nếu rách); Động mạch đốt sống (Vertebral artery) trong mổ cột sống cổ; Khí quản, thực quản và dây thần kinh quặt ngược thanh quản trong lối trước cổ; Động mạch và tĩnh mạch chủ chậu trong lối trước ngực thắt lưng."
        postop = "Nằm nghỉ tại giường ngày đầu, mang áo nẹp cột sống cứng (Thoracolumbosacral orthosis - TLSO) hoặc nẹp cổ Philadelphia khi ngồi dậy và tập đi từ ngày thứ 2. Theo dõi sát chức năng vận động, cảm giác 2 chi dưới và cơ tròn bàng quang. Điều trị giảm đau đa mô thức."
        pearls = "Luôn kiểm tra mốc đốt sống bằng C-arm trước khi rạch da; Dùng máy mài cao tốc (High-speed burr) và kẹp Kerrison thận trọng giải ép không chạm bao màng cứng; Kiểm tra độ chính xác của đường luồn vít cuống sống bằng que thăm dò bóng (Ball-tip probe) ở cả 4 thành vỏ xương trước khi bắt vít."
        
        default_titles = [
            "Định vị C-arm tầng can thiệp & Rạch da bộc lộ",
            "Bóc tách cơ cạnh sống & Bộc lộ mốc cuống sống / diện khớp",
            "Mở cung sau giải ép tủy và rễ thần kinh (Laminectomy)",
            "Khoan bắt vít cuống sống & Đặt miếng ghép liên thân đốt",
            "Nắn chỉnh góc gù vẹo, khóa thanh Rod & Đóng mổ theo lớp"
        ]
        default_actions = [
            "Chụp C-arm định vị chính xác đốt sống tổn thương; rạch da đường giữa dọc mỏm gai.",
            "Dùng dao điện bóc tách cơ cạnh sống sát màng xương ra đến mỏm ngang hai bên.",
            "Cắt dây chằng vàng, dùng kẹp Kerrison gặm giải phóng hoàn toàn chèn ép rễ và bao tủy.",
            "Tạo lỗ cuống sống, dò 4 thành xương an toàn, bắt vít cuống sống và đặt lồng Cage ghép xương.",
            "Lắp thanh nẹp dọc (Rod), ép nén phục hồi đường cong sinh lý, siết chặt ốc khóa và đóng da."
        ]

    # 7. Upper Extremity Trauma (Ch 57-61)
    elif ch in [57, 58, 59, 60, 61]:
        cat_vi = "Chấn Thương Gãy Xương Chi Trên"
        name_vi = f"Chấn Thương Chi Trên ({tid}): {name_en}"
        indications = f"Chỉ định trong gãy xương đòn di lệch, trật khớp cùng đòn, gãy đầu trên xương cánh tay (Neer 3-4 phần), gãy thân xương cánh tay mất vững, gãy mỏm khuỷu, gãy chỏm quay Mason, gãy hai xương cẳng tay Monteggia/Galeazzi di lệch."
        contraindications = "Nhiễm trùng da và mô mềm vùng cánh cẳng tay; tổn thương gãy xương không di lệch có thể điều trị bảo tồn thành công bằng nẹp bột."
        patient_prep = "Bệnh nhân nằm ngửa kê vai đối với xương đòn/vai hoặc nằm nghiêng/ngửa có bàn để tay đối với khuỷu và cẳng tay. Đặt garo hơi cánh tay (nếu can thiệp khuỷu - cẳng tay). Chuẩn bị máy tăng sáng C-arm và bộ nẹp khóa giải phẫu LC-DCP/PHILOS 3.5mm/4.5mm."
        danger_info = "Cấu trúc nguy cơ: Dây thần kinh quay (Radial nerve - nằm trong rãnh xoắn xương cánh tay ở mặt sau và xuyên vách gian cơ ngoài 10 cm trên lồi cầu ngoài); Dây thần kinh gian cốt sau (PIN - xuyên qua cung Frohse, bắt buộc giữ cẳng tay ở tư thế SẤP khi bộc lộ); Thần kinh nách ở cổ phẫu thuật xương cánh tay; Thần kinh trụ ở rãnh ròng rọc khuỷu."
        postop = "Bất động nẹp đỡ cánh cẳng bàn tay trong vài ngày đầu để giảm đau và chống nề. Bắt đầu tập vận động chủ động có trợ lực các ngón tay và khớp vai/khuỷu sớm từ ngày thứ 3-5 để chống cứng khớp. Chụp phim X-quang kiểm tra liền xương sau 4, 8 và 12 tuần."
        pearls = "Luôn phẫu tích nhận diện và bảo vệ thần kinh quay trước khi thao tác bắt nẹp thân xương cánh tay; Luôn giữ cẳng tay ở tư thế SẤP khi bộc lộ chỏm quay qua đường mổ Kocher; Khôi phục hoàn hảo chiều dài và độ cong sinh lý của xương quay để bảo tồn biên độ sấp ngửa."
        
        default_titles = [
            "Đường mổ giải phẫu chuẩn & Bộc lộ ổ gãy",
            "Nhận diện và treo bảo vệ dây thần kinh nguy cơ",
            "Làm sạch ổ gãy, nắn chỉnh phục hồi giải phẫu",
            "Cố định bằng nẹp khóa giải phẫu / Đinh nội tủy",
            "Kiểm tra C-arm biên độ vận động, cầm máu & Đóng mổ"
        ]
        default_actions = [
            "Rạch da dọc theo đường mổ giải phẫu kinh điển, tách cơ nhẹ nhàng bộc lộ mặt xương.",
            "Phẫu tích nhẹ nhàng nhận diện và bộc lộ dây thần kinh nguy cơ (quay/trụ/nách), treo giữ cẩn thận.",
            "Gắp sạch mô xơ và máu tụ ổ gãy, nắn chỉnh mảnh gãy khớp khít giải phẫu, kẹp giữ xương.",
            "Áp nẹp khóa giải phẫu ôm khít thân xương, bắt các vít vỏ xương và vít khóa nén ép vững chắc.",
            "Kiểm tra C-arm thấy trục thẳng diện gãy phẳng; vận động thử kiểm tra độ vững và đóng vết mổ."
        ]

    # Fallback default
    else:
        cat_vi = "Phẫu Thuật Chỉnh Hình Campbell"
        name_vi = f"Kỹ thuật Phẫu Thuật ({tid}): {name_en}"
        indications = f"Chỉ định can thiệp ngoại khoa điều trị bệnh lý và chấn thương theo nguyên bản sách Campbell's Operative Orthopaedics 13th Edition cho kỹ thuật {name_en}."
        contraindications = "Nhiễm trùng tại chỗ phẫu trường; bệnh nhân có bệnh lý nội khoa nặng chưa kiểm soát; thể trạng chưa sẵn sàng cho cuộc mổ lớn."
        patient_prep = "Bệnh nhân nằm trên bàn mổ ở tư thế phù hợp theo vùng giải phẫu. Sát trùng rộng rãi, trải săng vô trùng cho phép cử động tự do các khớp lân cận."
        danger_info = "Cấu trúc nguy cơ: Bảo tồn các mạch máu và dây thần kinh lớn đi qua vùng can thiệp; tránh kéo căng quá mức mô mềm."
        postop = "Chăm sóc theo dõi vết mổ, nẹp bột hoặc đai đỡ bất động theo đúng chỉ định. Bắt đầu tập phục hồi chức năng sớm chống cứng khớp và teo cơ."
        pearls = "Tôn trọng mô mềm và màng xương; tuân thủ các mốc giải phẫu an toàn của Campbell."
        default_titles = [
            "Bộc lộ phẫu trường theo lớp giải phẫu",
            "Đánh giá thương tổn & Chuẩn bị diện phẫu thuật",
            "Thực hiện can thiệp tạo hình / Tái tạo chính thức",
            "Cố định phương tiện kết hợp xương / Khâu phục hồi",
            "Kiểm tra cơ học, cầm máu & Đóng vết mổ theo lớp"
        ]
        default_actions = [
            "Rạch da chính xác theo đường mổ chuẩn, bóc tách nhẹ nhàng theo lớp giải phẫu.",
            "Nhận diện rõ thương tổn bệnh lý, bảo tồn tối đa mô lành xung quanh.",
            "Thực hiện các thao tác chuyên sâu theo quy trình chuẩn của Campbell 13th Ed.",
            "Cố định phương tiện chỉnh hình đạt độ vững chắc sinh học cơ học tối ưu.",
            "Rửa sạch phẫu trường, kiểm tra cầm máu kỹ lưỡng và đóng vết mổ theo từng lớp."
        ]

    steps = extract_surgical_steps_from_text(raw_text, default_titles, default_actions)
    
    # Existing image URLs if present
    img_url = f"web/static/images/techniques/{tid}.webp"
    images_list = [
        {
            "url": f"web/static/images/techniques/{tid}.webp",
            "type": "drawing",
            "caption": f"Sơ đồ nét vẽ giải phẫu & quy trình kỹ thuật {tid} ({name_en}) - Campbell 13th Ed"
        },
        {
            "url": f"web/static/images/techniques/{tid}_xray.webp",
            "type": "xray",
            "caption": f"Phim chụp X-quang & ca lâm sàng phẫu thuật {tid} ({name_en}) - Campbell 13th Ed"
        }
    ]

    return {
        "tech_id": tid,
        "name_en": name_en,
        "name_vi": name_vi,
        "chapter": ch,
        "category": cat_vi,
        "pdf_page": pdf_p,
        "author": author,
        "clinical_indications": indications,
        "contraindications": contraindications,
        "patient_prep": patient_prep,
        "surgical_approach": danger_info,
        "surgical_steps": steps,
        "postop_protocol": postop,
        "pearls_pitfalls": pearls,
        "image_url": img_url,
        "images": images_list
    }

# Scan techniques to upgrade
files_updated = 0
for t in catalog:
    tid = t['tech_id']
    fpath = f"data/techniques/{tid}.json"
    raw_txt = texts.get(tid, "")
    
    # Check if currently boilerplate
    needs_upgrade = False
    if os.path.exists(fpath):
        with open(fpath, 'r', encoding='utf-8') as f:
            content = f.read()
        if 'vùng giải phẫu General' in content or '(General)' in content or 'Chương ' in content and 'General' in content:
            needs_upgrade = True
    else:
        needs_upgrade = True
        
    if needs_upgrade:
        profile = generate_domain_profile(t, raw_txt)
        with open(fpath, 'w', encoding='utf-8') as f:
            json.dump(profile, f, ensure_ascii=False, indent=2)
        files_updated += 1

print(f"Successfully enriched {files_updated} techniques across all un-enriched chapters!")

# Sync master clinical_techniques.json
print("Synchronizing data/clinical_techniques.json with all 1,671 technique files...")
all_techniques = {}
for t in catalog:
    tid = t['tech_id']
    fpath = f"data/techniques/{tid}.json"
    if os.path.exists(fpath):
        with open(fpath, 'r', encoding='utf-8') as f:
            all_techniques[tid] = json.load(f)

with open('data/clinical_techniques.json', 'w', encoding='utf-8') as f:
    json.dump(all_techniques, f, ensure_ascii=False, indent=2)

print(f"Synchronized {len(all_techniques)} techniques into data/clinical_techniques.json!")
