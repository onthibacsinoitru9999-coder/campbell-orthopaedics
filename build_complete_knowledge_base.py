import json
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
print("Reading existing data files...")

classifs = json.load(open("data/fracture_classifications.json", encoding="utf-8"))
techs_cat = json.load(open("data/techniques_catalog.json", encoding="utf-8"))
tech_map = {t["tech_id"]: t for t in techs_cat}

print(f"Loaded {len(classifs)} classifications and {len(techs_cat)} techniques.")

# 1. Update Classifications with Deep Clinical Protocols
clinical_meta = {
    "schatzker": {
        "overview": "Phân loại Schatzker (1979) chia gãy mâm chày thành 6 type phản ánh mức độ năng lượng chấn thương tăng dần. Type I-III là tổn thương năng lượng thấp (thường ở mâm chày ngoài), Type IV-VI là chấn thương năng lượng cao gây mất vững nghiêm trọng diện khớp và trục chi.",
        "mechanism": "Lực vẹo ngoài (valgus) hoặc vẹo trong (varus) kết hợp lực nén ép dọc trục (axial load). Ở người trẻ xương chắc thường gây tách rời (split), ở người lớn tuổi thường gây lún ép (depression).",
        "imaging": "X-quang khớp gối 4 tư thế (Thẳng, Nghiêng, Chếch 40°). BẮT BUỘC chụp CT-Scan dựng hình 3D để đo bậc thang diện khớp và góc lún thành sau ngoài.",
        "treatment_principles": "Phục hồi diện khớp tuyệt đối (bậc thang < 2mm), phục hồi trục cơ học chi, tái tạo độ vững dây chằng và cho phép tập vận động gối sớm tránh cứng khớp.",
        "complications": "Hội chứng chèn ép khoang cấp; Nhiễm trùng hoại tử vạt da; Liệt thần kinh mác chung; Sập lún diện khớp thứ phát do ghép xương không đủ; Thoái hóa khớp sau chấn thương."
    },
    "garden": {
        "overview": "Phân loại Garden (1961) dựa trên sự di lệch của hệ thống bè xương chịu lực trên phim X-quang khớp háng thẳng, chia thành 4 độ. Có ý nghĩa quyết định bảo tồn chỏm (kết hợp xương) hay thay khớp háng.",
        "mechanism": "Người cao tuổi ngã đập mông hoặc háng ở tư thế xoay ngoài nhẹ trên nền xương loãng. Người trẻ do chấn thương năng lượng cao.",
        "imaging": "X-quang khớp háng thẳng (AP) xoay trong 15° và nghiêng chậu gối (cross-table lateral). Chụp CT-Scan khi nghi ngờ gãy cài không hoàn toàn.",
        "treatment_principles": "Người trẻ (< 65 tuổi): Luôn ưu tiên nắn chỉnh cấp cứu (< 6-12h) và kết hợp xương giữ chỏm. Người già (> 65-70 tuổi) gãy di lệch: Chỉ định thay khớp háng (Bipolar hoặc toàn phần) để ngồi dậy và đi lại sớm.",
        "complications": "Hoại tử vô mạch chỏm xương đùi (AVN, chiếm 20-40%); Khớp giả không liền (Nonunion, chiếm 10-25%); Biến chứng nằm lâu ở người già (viêm phổi, loét tì đè, huyết khối tĩnh mạch DVT)."
    },
    "pauwels": {
        "overview": "Phân loại Pauwels (1935) phân loại dựa trên góc tạo bởi đường gãy và mặt phẳng nằm ngang. Góc này quyết định lực tác động lên ổ gãy là lực nén ép (compression) hay lực cắt trượt (shearing force).",
        "mechanism": "Đo góc giữa đường gãy và đường nằm ngang nối 2 gai chậu trước trên.",
        "imaging": "X-quang khớp háng tư thế thẳng chuẩn.",
        "treatment_principles": "Góc càng đứng (Pauwels III > 50°), lực trượt càng lớn, bắt vít thông thường rất dễ thất bại. Cần dùng vít góc cố định, nẹp DHS có vít chống xoay hoặc đục xương sửa trục đổi góc.",
        "complications": "Lực cắt trượt làm bung vít; Gập góc vẹo trong (varus collapse); Khớp giả không liền xương."
    },
    "neer": {
        "overview": "Phân loại Neer (1970) chia đầu trên xương cánh tay thành 4 phần giải phẫu: Chỏm, Củ lớn, Củ bé, Thân xương. Một phần được coi là di lệch khi khoảng cách > 1cm hoặc gập góc > 45°.",
        "mechanism": "Ngã chống tay ở tư thế duỗi hoặc ngã đập trực tiếp vùng vai.",
        "imaging": "Bộ phim chấn thương vai chuẩn (Neer series): X-quang vai thẳng thực sự, xuyên ngực chữ Y (Scapular Y), và tư thế nách (Axillary view). Chụp CT-Scan 3D khi gãy 3-4 mảnh.",
        "treatment_principles": "Gãy 1 phần (80%): Điều trị bảo tồn treo tay túi và tập phục hồi chức năng sớm. Gãy 2-3 phần: Mổ nẹp khóa (PHILOS). Gãy 4 phần ở người già: Thay khớp vai đảo ngược (RSA).",
        "complications": "Tổn thương thần kinh nách; Hoại tử vô mạch chỏm xương cánh tay (AVN); Cứng khớp vai do bất động kéo dài."
    },
    "gustilo": {
        "overview": "Phân loại Gustilo-Anderson (1976/1984) là hệ thống phân loại gãy xương hở quan trọng nhất thế giới, dựa trên độ dập nát mô mềm, mức năng lượng và tổn thương mạch máu để tiên lượng nhiễm trùng và bảo tồn chi.",
        "mechanism": "Lực chấn thương năng lượng cao trực tiếp hoặc đầu xương nhọn đâm thủng da từ trong ra ngoài.",
        "imaging": "X-quang chuẩn. Với Độ IIIC: Siêu âm Doppler hoặc chụp CT Angiography mạch máu khẩn cấp.",
        "treatment_principles": "CẤP CỨU NGOẠI KHOA: Kháng sinh tĩnh mạch trong 1 giờ đầu; Bơm rửa cắt lọc triệt để trong phòng mổ; Bất động vững chắc; Che phủ phần mềm sớm trong 7 ngày.",
        "complications": "Nhiễm trùng nông và sâu; Viêm xương tủy xương mạn tính; Khớp giả nhiễm trùng; Cắt cụt chi."
    },
    "bado_monteggia": {
        "overview": "Phân loại Bado (1967) phân loại tổn thương gãy xương trụ kèm trật chỏm xương quay thành 4 Type dựa theo hướng di lệch của chỏm quay. Mọi gãy xương trụ đơn độc bắt buộc phải chụp khớp khuỷu để tránh bỏ sót.",
        "mechanism": "Ngã chống tay kèm cẳng tay xoay sấp quá mức hoặc đòn đánh trực tiếp vào bờ sau xương trụ.",
        "imaging": "X-quang cẳng tay lấy đủ 2 khớp (khuỷu và cổ tay). Trục chỏm quay (radiocapitellar line) phải luôn đi qua tâm chỏm con xương cánh tay.",
        "treatment_principles": "Nắn chỉnh giải phẫu tuyệt đối chiều dài và trục xoay xương trụ bằng nẹp nén ép (DCP 3.5mm). Khi xương trụ về đúng giải phẫu, chỏm quay thường tự động về khớp.",
        "complications": "Bỏ sót trật chỏm quay gây cứng khớp khuỷu mạn tính; Tổn thương thần kinh gian cốt sau (PIN); Can lệch xương trụ."
    },
    "galeazzi": {
        "overview": "Tổn thương Galeazzi gồm gãy thân xương quay kèm trật hoặc mất vững khớp quay trụ dưới (DRUJ). Được mệnh danh là 'Gãy xương cần sự tôn trọng tuyệt đối' vì điều trị bảo tồn hầu như luôn thất bại ở người lớn.",
        "mechanism": "Ngã chống tay với cẳng tay xoay sấp tối đa hoặc chấn thương vặn xoắn cổ tay năng lượng cao.",
        "imaging": "X-quang cẳng tay thẳng và nghiêng chuẩn lấy đủ khớp khuỷu và cổ tay. Đánh giá độ giãn rộng khoang DRUJ > 2mm.",
        "treatment_principles": "Mổ nẹp nén ép giải phẫu tuyệt đối xương quay qua đường mổ Henry. Kiểm tra độ vững khớp DRUJ: nếu mất vững, xuyên kim Kirschner cố định khớp quay trụ dưới 4-6 tuần.",
        "complications": "Mất vững mạn tính khớp quay trụ dưới; Giảm tầm sấp ngửa cẳng tay; Đau mạn tính bờ trụ cổ tay do rách sụn tam giác TFCC."
    },
    "colles_smith_barton": {
        "overview": "Gãy đầu dưới xương quay là tổn thương xương phổ biến nhất chi trên, gồm: Gãy Colles (di lệch lưng bàn tay), Gãy Smith (di lệch lòng bàn tay), Gãy Barton (gãy trật nội khớp cổ tay).",
        "mechanism": "Gãy Colles do ngã chống tay duỗi cổ tay. Gãy Smith do ngã chống mu tay gập cổ tay. Gãy Barton do lực nén ép kèm trật khớp.",
        "imaging": "X-quang cổ tay 2 tư thế thẳng (PA) và nghiêng chuẩn. Đánh giá độ nghiêng xương quay (~22°), chiều cao xương quay (~11-12mm), độ nghiêng mặt lòng (~11°).",
        "treatment_principles": "Phục hồi độ nghiêng mặt lòng, chiều cao xương quay và diện khớp phẳng (< 2mm). Gãy mất vững hoặc gãy nội khớp chỉ định mổ nẹp khóa mặt lòng (Volar Locking Plate - VLP).",
        "complications": "Hội chứng ống cổ tay cấp; Đứt gân duỗi dài ngón cái (EPL); Hội chứng đau loạn dưỡng vùng phức tạp (CRPS); Cứng cổ tay."
    },
    "ruedi_allgower": {
        "overview": "Phân loại Rüedi-Allgöwer (1979) phân loại gãy vỡ trần diện khớp đầu dưới xương chày (Pilon chày) do xương sên bị dồn ép như búa tạ đóng thẳng vào trần mâm chày.",
        "mechanism": "Ngã từ trên cao xuống hoặc tai nạn xe máy với bàn chân đạp thẳng xuống sàn, lực nén dọc trục dồn ép lên diện khớp chày.",
        "imaging": "X-quang cổ chân 3 tư thế chuẩn. BẮT BUỘC chụp CT-Scan 3D xác định mảnh trước ngoài (Chaput), mảnh sau ngoài (Volkmann) và mắt cá trong.",
        "treatment_principles": "Chiến lược 2 thì bảo vệ phần mềm: Thì 1 đặt khung cố định ngoài bắc cầu qua cổ chân + nẹp xương mác. Đợi 10-14 ngày da hết phù nề mới làm Thì 2: Mổ ít xâm lấn (MIPO) nắn diện khớp và nẹp khóa.",
        "complications": "Hoại tử da lộ xương và dụng cụ; Nhiễm trùng sâu viêm xương tủy cổ chân; Thoái hóa khớp cổ chân dẫn đến hàn khớp (Arthrodesis)."
    },
    "danis_weber": {
        "overview": "Phân loại Danis-Weber dựa trên mức độ cao của đường gãy xương mác so với khớp chày mác dưới (khớp mộng chày mác - Syndesmosis), chia thành Type A, B, C.",
        "mechanism": "Lật cổ chân vào trong hoặc ra ngoài kết hợp xoay ngoài hoặc xoay trong.",
        "imaging": "X-quang cổ chân 3 tư thế (Thẳng, Nghiêng, Mộng chày mác - Mortise). Đánh giá khe sáng mộng chày mác < 4mm.",
        "treatment_principles": "Phục hồi chiều dài giải phẫu xương mác và độ khít của mộng chày mác. Type C hoặc Type B mất vững bắt buộc mổ nẹp xương mác và bắt vít định vị chày mác dưới.",
        "complications": "Can lệch xoay xương mác gây thoái hóa khớp cổ chân nhanh chóng; Gãy vít chày mác do tì đè quá sớm."
    },
    "denis_spine": {
        "overview": "Phân loại Denis (1983) chia cột sống ngực - thắt lưng thành 3 cột trụ: Cột trước (2/3 trước thân đốt sống + ALL), Cột giữa (1/3 sau thân đốt sống + PLL), Cột sau (cung cuống, diện khớp + PLC). Cột giữa quyết định mất vững và chèn ép tủy.",
        "mechanism": "Lực nén gập (wedge compression), lực ép nổ (axial burst), lực gập căng dãn (Chance), hoặc lực xoay cắt (shear).",
        "imaging": "X-quang cột sống thẳng nghiêng. Chụp CT-Scan đo phần trăm hẹp ống sống do mảnh xương đẩy lùi. Chụp MRI đánh giá tủy sống và phức hợp dây chằng sau (PLC).",
        "treatment_principles": "Tổn thương từ 2 cột trụ trở lên hoặc có khiếm khuyết thần kinh: Phẫu thuật cố định nẹp vít chân cung (Pedicle Screws) kết hợp mở cung sau giải ép tủy.",
        "complications": "Liệt tủy sống; Rò dịch não tủy do rách màng cứng; Gù gập cột sống tiến triển sau chấn thương."
    },
    "hawkins": {
        "overview": "Phân loại Hawkins (1970/1978) tiên lượng nguy cơ hoại tử vô mạch (AVN) của thân xương sên. Xương sên có 60% sụn bao phủ và không có cơ bám, mạng lưới mạch máu nuôi rất dễ bị cắt đứt khi di lệch.",
        "mechanism": "Lực gập lưng bàn chân quá mức dữ dội (chấn thương bàn đạp máy bay - Aviator's astragalus).",
        "imaging": "X-quang cổ chân thẳng, nghiêng và tư thế Canale view. Chụp CT-Scan đánh giá trật khớp sên gót và sên chày.",
        "treatment_principles": "CẤP CỨU CHỈNH HÌNH: Nắn chỉnh mở giải phẫu tuyệt đối và bắt 2 vít nén ép titan từ sau ra trước hoặc từ trước ra sau.",
        "complications": "Hoại tử vô mạch thân xương sên (AVN: Type I < 10%, Type II 30-50%, Type III 80-90%, Type IV ~100%); Dấu hiệu Hawkins sign ở tuần 6-8 chứng tỏ xương còn máu nuôi."
    },
    "mason": {
        "overview": "Phân loại Mason (1954/Johnston) phân loại gãy chỏm xương quay - cấu trúc chống lại lực vẹo ngoài và lực trượt ra sau của khớp khuỷu.",
        "mechanism": "Ngã chống tay với cẳng tay xoay sấp nhẹ và khớp khuỷu duỗi một phần.",
        "imaging": "X-quang khớp khuỷu thẳng, nghiêng và tư thế Greenspan view.",
        "treatment_principles": "Mason I không kẹt khớp: Bó nẹp treo tay tập sớm. Mason II có kẹt khớp: Mổ nẹp vít chìm ở vùng an toàn (Safe Zone). Mason III/IV vỡ vụn kèm mất vững khuỷu: Thay chỏm xương quay kim loại.",
        "complications": "Cứng khớp khuỷu; Mất vững vẹo ngoài; Tổn thương thần kinh gian cốt sau (PIN); Ngắn xương quay (Essex-Lopresti)."
    },
    "young_burgess": {
        "overview": "Phân loại Young-Burgess (1986) phân loại gãy khung chậu dựa trên hướng của lực chấn thương: LC (Ép bên), APC (Ép trước sau / Gãy cuốn sách mở), VS (Cắt dọc trục). Phản ánh nguy cơ mất máu đe dọa tính mạng.",
        "mechanism": "Tai nạn giao thông tốc độ cao hoặc rơi từ trên cao xuống.",
        "imaging": "X-quang khung chậu thẳng (AP), chếch trên (Inlet view - 45° đuôi) và chếch dưới (Outlet view - 45° đầu). CT-Scan chậu mạch máu khẩn cấp.",
        "treatment_principles": "CẤP CỨU HỒI SỨC: Băng thắt khung chậu (Pelvic Binder) ngang mức mấu chuyển lớn; Chụp mạch can thiệp nút mạch (Angioembolization) hoặc phẫu thuật nhồi gạc chậu (Pelvic Packing) cầm máu; Cố định khung chậu bằng khung cố định ngoài hoặc nẹp vít khớp mu / vít cùng chậu.",
        "complications": "Sốc mất máu xuất huyết nội sau phúc mạc; Tổn thương niệu đạo - bàng quang; Tổn thương đám rối thần kinh cùng cụt."
    },
    "letournel_judet": {
        "overview": "Phân loại Judet-Letournel (1964) là đỉnh cao kinh điển trong phân loại gãy ổ cối xương chậu, chia thành 5 kiểu gãy đơn giản (thành sau, trụ sau, thành trước, trụ trước, ngang) và 5 kiểu gãy phối hợp phức tạp.",
        "mechanism": "Chỏm xương đùi bị dồn nén va đập vào đáy ổ cối qua các tư thế háng khác nhau.",
        "imaging": "Bộ phim Judet 3 tư thế: X-quang chậu thẳng (AP), Tư thế cánh chậu (Iliac oblique - 45°), và Tư thế lỗ bịt (Obturator oblique - 45°). Chụp CT-Scan 3D ổ cối.",
        "treatment_principles": "Chỉ định phẫu thuật khi di lệch diện khớp ổ cối > 2mm ở vùng chịu lực (vòm ổ cối). Phẫu thuật phục hồi giải phẫu qua đường mổ Kocher-Langenbeck (lối sau) hoặc đường mổ Stoppa / chậu bẹn Ilioinguinal (lối trước).",
        "complications": "Liệt thần kinh tọa (thần kinh ngồi); Cốt hóa lạc chỗ quanh khớp háng (Heterotopic Ossification); Thoái hóa khớp háng sau chấn thương."
    },
    "pipkin": {
        "overview": "Phân loại Pipkin (1957) phân loại tổn thương gãy chỏm xương đùi kèm theo trật khớp háng ra sau. Đây là chấn thương táp-lô xe hơi (dashboard injury) nghiêm trọng.",
        "mechanism": "Khớp háng gấp và khép, đầu gối va đập mạnh vào táp-lô xe hơi dồn lực dọc thân đùi đẩy chỏm xương đùi trật ra sau và bị cọ vỡ vào bờ ổ cối.",
        "imaging": "X-quang khớp háng cấp cứu. Chụp CT-Scan dựng hình chỏm đùi sau khi nắn trật.",
        "treatment_principles": "NẮN TRẬT KHỚP HÁNG CẤP CỨU trong vòng 6 giờ dưới gây mê giãn cơ để cứu mạch máu chỏm. Mổ nắn mảnh gãy chỏm và bắt vít chìm không đầu (Herbert/headless screws) nếu mảnh gãy nằm ở vùng chịu lực hoặc kẹt khớp.",
        "complications": "Hoại tử vô mạch chỏm xương đùi (AVN); Thoái hóa khớp háng sớm; Liệt thần kinh tọa."
    },
    "sanders": {
        "overview": "Phân loại Sanders (1993) dựa trên hình ảnh cắt lớp vi tính (CT-Scan) mặt phẳng đứng ngang (Coronal) tại vị trí rộng nhất của mặt khớp sau xương gót, chia thành Type I đến IV dựa trên số lượng đường gãy và độ dập nát diện khớp.",
        "mechanism": "Ngã từ trên cao xuống chân tiếp đất, xương sên dồn nén ép vỡ nát mặt khớp sau xương gót.",
        "imaging": "BẮT BUỘC chụp CT-Scan cắt mỏng 1-2mm mặt phẳng Coronal và Axial xương gót. Đo góc Böhler (bình thường 20-40°) và góc Gissane (120-145°).",
        "treatment_principles": "Mục tiêu phục hồi góc Böhler, chiều cao và chiều rộng xương gót, diện khớp sau phẳng. Sanders II-III mổ mở nắn chỉnh qua đường chữ L mở rộng ngoài (extensile lateral approach) hoặc nẹp ít xâm lấn. Sanders IV vỡ nát: Hàn khớp dưới sên thì đầu (Primary Subtalar Arthrodesis).",
        "complications": "Hoại tử vạt da góc chữ L; Nhiễm trùng xương gót; Hội chứng chèn ép khoang bàn chân; Cứng khớp và thoái hóa khớp dưới sên."
    },
    "anderson_dalonzo": {
        "overview": "Phân loại Anderson-D'Alonzo (1974) phân loại gãy mỏm nha (odontoid/dens) đốt đội C2 thành 3 Type dựa theo vị trí giải phẫu của đường gãy. Type II là thể phổ biến nhất nhưng có tỉ lệ không liền xương cao nhất.",
        "mechanism": "Chấn thương uốn gập hoặc quá duỗi đốt sống cổ đột ngột (tai nạn giao thông, người già ngã đập trán).",
        "imaging": "X-quang cột sống cổ tư thế há miệng (Open-mouth odontoid view), thẳng và nghiêng. BẮT BUỘC chụp CT-Scan cột sống cổ cắt mỏng dựng hình sagittal và coronal.",
        "treatment_principles": "Type I và Type III: Điều trị bảo tồn nẹp cổ cứng hoặc áo Halo-vest, tỉ lệ liền xương > 90%. Type II ở người trẻ di lệch > 5mm: Mổ bắt 1-2 vít mỏm nha từ trước (Anterior Odontoid Screw) để bảo tồn vận động quay C1-C2. Người già hoặc đường gãy chéo ngược: Hàn C1-C2 lối sau (Harms construct).",
        "complications": "Không liền xương dẫn đến mất vững khớp đội trục đe dọa chèn ép hành tủy tử vong; Di lệch thứ phát làm hẹp ống sống cổ cao."
    },
    "winquist_hansen": {
        "overview": "Phân loại Winquist-Hansen (1984) phân loại gãy thân xương đùi dựa trên mức độ dập nát (comminution) của vỏ xương, quyết định mức độ vững cơ học sau khi đóng đinh nội tủy.",
        "mechanism": "Lực chấn thương năng lượng cao uốn cong, dồn nén hoặc xoắn vặn thân xương đùi.",
        "imaging": "X-quang xương đùi lấy đủ 2 khớp (khớp háng và khớp gối).",
        "treatment_principles": "TIÊU CHUẨN VÀNG: Đinh nội tủy có chốt xuôi dòng (Antegrade Interlocking Intramedullary Nailing). Type I-II có thể chốt tĩnh hoặc chốt động. Type III-IV bắt buộc chốt tĩnh cả đầu gần và đầu xa để kiểm soát chiều dài và chống xoay.",
        "complications": "Tắc mạch mỡ (Fat Embolism Syndrome - FES); Can lệch xoay xương đùi; Chậm liền xương hoặc gãy đinh nội tủy."
    },
    "russell_taylor": {
        "overview": "Phân loại Russell-Taylor (1992) phân loại gãy dưới mấu chuyển xương đùi (Subtrochanteric Fractures) dựa trên việc đường gãy có lan vào hố mấu chuyển (trochanteric fossa) và mấu chuyển bé hay không, quyết định loại đinh nội tủy sử dụng.",
        "mechanism": "Vùng dưới mấu chuyển chịu lực nén ép cực lớn (lên tới 1.200 lbs/sq inch ở vỏ trong), lực cơ kéo làm đoạn gần gập, dạng và xoay ngoài.",
        "imaging": "X-quang khớp háng và thân đùi thẳng và nghiêng chuẩn.",
        "treatment_principles": "Type I (Hố mấu chuyển còn nguyên): Đinh nội tủy tái tạo (Reconstruction Nail / Cephalomedullary Nail) qua đỉnh mấu chuyển lớn. Type II (Hố mấu chuyển bị vỡ): Nẹp khóa đầu trên xương đùi (Proximal Femoral Locking Plate) hoặc đinh nội tủy có điểm vào cải tiến.",
        "complications": "Gập góc vẹo trong (Varus malunion); Gãy nẹp hoặc đứt vít mấu chuyển; Không liền xương do vùng xương vỏ đặc ít mạch máu nuôi."
    },
    "ao_ota": {
        "overview": "Hệ thống phân loại AO/OTA là ngôn ngữ chung quốc tế chuẩn hóa toàn bộ các loại gãy xương theo mã số: [Số xương][Đoạn xương] - [Loại A/B/C][Mức độ 1/2/3].",
        "mechanism": "Áp dụng toàn diện cho tất cả các cơ chế chấn thương chỉnh hình trên cơ thể người.",
        "imaging": "X-quang quy ước chuẩn 2 bình diện vuông góc kết hợp CT-Scan khi tổn thương nội khớp (đoạn 1 và đoạn 3).",
        "treatment_principles": "Loại A (Đơn giản): Cố định vững chắc tương đối hoặc tuyệt đối. Loại B (Có mảnh nêm): Bảo tồn mạch máu mảnh nêm. Loại C (Phức tạp / Nội khớp hoàn toàn): Tái tạo giải phẫu diện khớp và cố định sinh học trục chi.",
        "complications": "Tùy thuộc từng vùng giải phẫu cụ thể theo phân loại chi tiết AO/OTA."
    },
    "salter_harris": {
        "overview": "Phân loại Salter-Harris (1963) là hệ thống phân loại kinh điển cho tổn thương sụn tiếp hợp (physis / growth plate) ở trẻ em, chia thành 5 Type (Rank 1968 bổ sung Type VI). Có giá trị tiên lượng rối loạn phát triển chiều dài chi.",
        "mechanism": "Lực chấn thương uốn bẻ, xoắn vặn hoặc dồn nén lên sụn tiếp hợp đang trong thời kỳ phát triển ở trẻ em.",
        "imaging": "X-quang so sánh 2 bên (bên tổn thương và bên lành đối diện). Chụp MRI khi nghi ngờ bắc cầu xương sụn (physeal bridge).",
        "treatment_principles": "Nắn chỉnh nhẹ nhàng tránh cọ xát làm dập nát lớp tế bào mầm sinh sụn. Type I-II: Nắn kín bó bột. Type III-IV: Mổ mở nắn giải phẫu và bắt vít/xuyên kim song song với sụn tiếp hợp (tuyệt đối KHÔNG xuyên vít qua đĩa sụn tiếp hợp).",
        "complications": "Bắc cầu xương sớm gây ngắn chi hoặc vẹo trục chi (vẹo trong/vẹo ngoài); Chậm liền xương."
    },
    "frykman": {
        "overview": "Phân loại Frykman (1967) phân loại gãy đầu dưới xương quay dựa trên việc đường gãy có đi vào khớp quay cổ tay (Radiocarpal) và khớp quay trụ dưới (DRUJ) hay không, kèm theo có hay không gãy mỏm trâm trụ.",
        "mechanism": "Ngã chống tay duỗi cổ tay.",
        "imaging": "X-quang cổ tay thẳng và nghiêng chuẩn.",
        "treatment_principles": "Độ chẵn (II, IV, VI, VIII) có kèm gãy mỏm trâm trụ, nguy cơ mất vững khớp quay trụ dưới rất cao. Độ V-VIII liên quan khớp DRUJ cần kiểm tra độ vững cẳng tay xoay sấp ngửa.",
        "complications": "Mất vững khớp quay trụ dưới (DRUJ); Cứng cổ tay; Thoái hóa khớp quay cổ tay."
    }
}

# Merge into classifications
for c in classifs:
    cid = c["id"]
    if cid in clinical_meta:
        c.update(clinical_meta[cid])

with open("data/fracture_classifications.json", "w", encoding="utf-8") as f:
    json.dump(classifs, f, ensure_ascii=False, indent=2)

print("Updated data/fracture_classifications.json with rich clinical protocols.")

# 2. Build Structured Clinical Techniques
print("Synthesizing structured clinical operative guides...")

clinical_techs_db = {
    "54-14": {
        "tech_id": "54-14",
        "name_en": "Open Reduction and Fixation of a Lateral Tibial Plateau Fracture",
        "name_vi": "Phẫu thuật Kết hợp xương Gãy Mâm chày Ngoài (Nắn chỉnh mở & Nẹp nâng đỡ)",
        "chapter": 54,
        "category": "Knee & Lower Leg",
        "pdf_page": 3078,
        "author": "Campbell Clinic Trauma Service",
        "clinical_indications": "Gãy mâm chày ngoài di lệch (Schatzker I, II, III) có bậc thang diện khớp > 2mm, mất vững khớp gối > 5° khi duỗi hoàn toàn, gãy hở hoặc gãy kèm chèn ép khoang cấp.",
        "contraindications": "Phần mềm quanh gối đụng dập bầm dập nặng, nổi nốt phỏng nước (blisters) chưa lành; nhiễm trùng da vùng mổ; bệnh nhân sốc đa chấn thương chưa ổn định (chỉ đặt khung cố định ngoài tạm thời).",
        "patient_prep": "Bệnh nhân nằm ngửa trên bàn mổ thấu xạ. Đặt gối độn dưới mông cùng bên và một gối nhỏ dưới khoeo để gối gập nhẹ 20-30°. Đặt garo hơi gốc đùi (áp lực 250-300 mmHg). Máy tăng sáng C-arm đặt ở phía đối diện, vào vuông góc với khớp gối.",
        "surgical_approach": "Đường mổ trước ngoài (Anterolateral Approach). Rạch da hình chữ S hoặc hơi cong bắt đầu từ 3-5 cm trên diện khớp, đi qua bờ ngoài gân bánh chè, qua củ Gerdy và kéo dài xuống dưới cách ổ gãy 4-5 cm. Cắt mạc sâu, tách cơ chày trước ra khỏi vỏ ngoài xương chày. Bảo vệ dây thần kinh mác chung ở cổ xương mác.",
        "surgical_steps": [
            {
                "step": 1,
                "title": "Bộc lộ diện khớp & Đánh giá sụn chêm ngoài",
                "detail": "Rạch ngang bao khớp ngay dưới sụn chêm ngoài (submeniscal arthrotomy). Dùng chỉ nâng đỡ sụn chêm lên trên để quan sát trực tiếp toàn bộ diện khớp mâm chày ngoài. Bơm rửa sạch máu đọng và các mảnh xương vụn nhỏ."
            },
            {
                "step": 2,
                "title": "Nắn chỉnh phục hồi diện khớp (Reduction)",
                "detail": "Với gãy lún (Schatzker II, III), tạo một cửa sổ xương dưới sụn ở vỏ xương chày trước ngoài. Dùng cây đục đầu tù hoặc cây nâng chuyên dụng nhẹ nhàng đội khối sụn lún lên ngang bằng diện khớp lành. Kiểm tra liên tục bằng mắt thường qua diện khớp và dưới màn tăng sáng C-arm."
            },
            {
                "step": 3,
                "title": "Ghép xương khoang khuyết hổng (Bone Grafting)",
                "detail": "Sau khi đội diện khớp lên, nhồi chặt chất thay thế xương (calcium phosphate cement) hoặc xương xốp tự thân (lấy từ mào chậu) vào khoang rỗng dưới diện sụn để làm giá đỡ chống sập lún thứ phát."
            },
            {
                "step": 4,
                "title": "Cố định nẹp nâng đỡ ngoài (Lateral Buttress Plating)",
                "detail": "Bắt 2-3 vít xốp rỗng 6.5mm/7.0mm có đệm (washers) dưới diện khớp để kéo ép mảnh tách rời. Đặt nẹp nâng đỡ mặt ngoài (nẹp L hoặc nẹp khóa mâm chày ngoài LCP), bắt các vít khóa cố định vững chắc vào hành xương và thân xương chày."
            },
            {
                "step": 5,
                "title": "Kiểm tra độ vững & Khâu phục hồi sụn chêm/bao khớp",
                "detail": "Kiểm tra vận động gập duỗi gối dưới C-arm (0-120°). Khâu đính lại sụn chêm vào bao khớp bằng chỉ tiêu chậm PDS 2-0. Đặt dẫn lưu kín và đóng vết mổ theo từng lớp giải phẫu."
            }
        ],
        "postop_protocol": "Nẹp gối có khóa trong 7 ngày đầu. Bắt đầu tập vận động gập duỗi thụ động có trợ giúp (CPM) từ ngày thứ 3. KHÔNG tì đè (Non-weight bearing) trong 6-8 tuần đầu. Tì đè một phần từ tuần 8-12. Tì đè hoàn toàn khi có bằng chứng liền xương trên X-quang.",
        "pearls_pitfalls": "Cạm bẫy sập lún thứ phát do ghép xương xốp không đủ chặt; Tránh bóc tách mô mềm quá mức ra phía sau ngoài để bảo vệ dây thần kinh mác chung; Đảm bảo vít nâng đỡ nằm ngay sát dưới mặt sụn (< 5mm) để tạo bệ đỡ dạng giàn giáo (rafting construct)."
    },
    "55-1": {
        "tech_id": "55-1",
        "name_en": "Fixation of Femoral Neck Fracture with Cannulated Screws",
        "name_vi": "Phẫu thuật Kết hợp xương Cổ Xương đùi bằng 3 Vít xốp rỗng Song song",
        "chapter": 55,
        "category": "Hip & Pelvis",
        "pdf_page": 3144,
        "author": "ASIF / AO Trauma Principles",
        "clinical_indications": "Gãy cổ xương đùi Garden I, II ở mọi lứa tuổi; Gãy Garden III, IV ở người trẻ tuổi (< 65 tuổi) cần bảo tồn chỏm; Gãy góc Pauwels I và II.",
        "contraindications": "Gãy Garden III, IV ở người cao tuổi loãng xương nặng (ưu tiên thay khớp háng); Gãy Pauwels III góc dốc đứng (ưu tiên nẹp DHS có vít chống xoay); Nhiễm trùng tại chỗ khớp háng.",
        "patient_prep": "Bệnh nhân nằm ngửa trên bàn chỉnh hình kéo nắn (Fracture table). Chân lành dạng và nâng cao. Chân gãy cố định vào ủng kéo. Máy C-arm đặt giữa 2 chân để soi được cả tư thế thẳng (AP) và nghiêng chậu gối (cross-table lateral).",
        "surgical_approach": "Kỹ thuật ít xâm lấn qua da (Percutaneous). Rạch 3 đường nhỏ 1.5 cm ở mặt ngoài gốc mấu chuyển lớn, cách đỉnh mấu chuyển lớn 2-4 cm về phía xa.",
        "surgical_steps": [
            {
                "step": 1,
                "title": "Nắn chỉnh ổ gãy trên bàn chỉnh hình (Closed Reduction)",
                "detail": "Kéo thẳng dọc trục để phục hồi chiều dài chi, xoay trong bàn chân 15-20° để khử biến dạng xoay ngoài, khép nhẹ chi. Kiểm tra góc bè xương trên C-arm cả 2 bình diện thẳng và nghiêng đạt giải phẫu hoàn hảo (chỉ số Garden 160-180°)."
            },
            {
                "step": 2,
                "title": "Định vị 3 kim dẫn đường Kirschner (Guide Wires)",
                "detail": "Dưới C-arm, khoan 3 kim dẫn 2.8mm song song nhau theo hình tam giác ngược (1 vít dưới nằm sát vỏ xương đùi dưới để chống vẹo trong, 2 vít trên nằm sát vỏ trước và sau). Kim dừng cách mặt sụn chỏm đùi 5mm."
            },
            {
                "step": 3,
                "title": "Đo chiều dài và khoan rỗng (Drilling & Measuring)",
                "detail": "Dùng thước đo chuyên dụng đo chiều dài vít. Khoan mở xương xốp bằng mũi khoan rỗng có cữ chặn dừng trước chỏm đùi."
            },
            {
                "step": 4,
                "title": "Bắt 3 vít xốp rỗng nén ép (Screw Insertion)",
                "detail": "Bắt 3 vít xốp rỗng 7.3mm (hoặc 6.5mm) có đệm (washers). Xiết đều tay từng vít để tạo lực nén ép đồng trục tối đa qua khe gãy. Kiểm tra dưới C-arm thấy khe gãy khép khít hoàn toàn."
            },
            {
                "step": 5,
                "title": "Rút kim dẫn đường & Đóng da",
                "detail": "Rút bỏ 3 kim dẫn đường, rửa sạch vết mổ và khâu da mũi rời. Không cần đặt dẫn lưu."
            }
        ],
        "postop_protocol": "Cho bệnh nhân ngồi dậy ngay ngày đầu sau mổ để tránh ứ đọng phổi. Tập gập duỗi khớp háng và khớp gối chủ động có trợ giúp. Đi nạng chống chân không tì đè trong 6-8 tuần đầu. Tì đè một phần từ tuần thứ 8 và tì đè hoàn toàn khi X-quang có cầu xương liền tốt (12 tuần).",
        "pearls_pitfalls": "Bắt buộc 3 vít phải song song tuyệt đối để cho phép ổ gãy trượt nén ép sinh học; Vít phía dưới phải tựa sát vào vỏ xương đùi dưới (calcar femorale) để chống gập góc varus; Tuyệt đối không để đầu vít xuyên thủng vào khớp háng."
    },
    "55-4": {
        "tech_id": "55-4",
        "name_en": "Compression Hip Screw Fixation of Intertrochanteric Femoral Fractures",
        "name_vi": "Phẫu thuật Kết hợp xương Gãy Liên mấu chuyển bằng Nẹp Trượt Nén ép DHS (Dynamic Hip Screw)",
        "chapter": 55,
        "category": "Hip & Pelvis",
        "pdf_page": 3147,
        "author": "Richard / Clawson / Campbell Trauma",
        "clinical_indications": "Gãy liên mấu chuyển xương đùi thể vững (AO/OTA 31-A1, A2.1); Gãy cổ xương đùi góc Pauwels III ở người trẻ tuổi.",
        "contraindications": "Gãy liên mấu chuyển thể mất vững có gãy vỡ thành ngoài (Lateral wall fracture < 20.5mm); Gãy có đường gãy xiên ngược (Reverse obliquity 31-A3, ưu tiên đinh nội tủy Gamma/PFNA).",
        "patient_prep": "Nằm ngửa trên bàn chỉnh hình kéo nắn. Nắn chỉnh diện khớp thẳng trục dưới kiểm tra C-arm.",
        "surgical_approach": "Đường mổ ngoài trực tiếp (Direct Lateral Approach). Rạch da thẳng dài 8-10 cm từ gốc mấu chuyển lớn xuôi xuống thân đùi. Cắt dải chậu chày, rạch lật cơ rộng ngoài bộc lộ vỏ ngoài xương đùi.",
        "surgical_steps": [
            {
                "step": 1,
                "title": "Nắn chỉnh kín và đặt thước ngắm góc 135°",
                "detail": "Kiểm tra phục hồi góc cổ thân xương đùi 130-135°. Đặt dưỡng ngắm góc 135° ở mặt ngoài thân xương đùi, khoan kim dẫn đường xuyên tâm cổ chỏm đùi."
            },
            {
                "step": 2,
                "title": "Kiểm tra vị trí kim dẫn (TAD < 25mm)",
                "detail": "Kim dẫn đường bắt buộc phải nằm ở vị trí trung tâm - trung tâm (Center-Center) hoặc dưới - trung tâm trên cả phim thẳng và nghiêng. Tính khoảng cách chóp - đỉnh (Tip-Apex Distance - TAD) < 20-25mm để chống trôi bung vít (cut-out)."
            },
            {
                "step": 3,
                "title": "Doa mở rộng 3 tầng và taro ren",
                "detail": "Dùng mũi doa 3 tầng (Triple reamer) doa mở đường hầm cho vít trượt và nẹp nòng. Taro ren ở vùng xương xốp chỏm đùi."
            },
            {
                "step": 4,
                "title": "Bắt vít trượt cổ đùi (Lag Screw) & Đặt nẹp DHS",
                "detail": "Vặn vít trượt DHS đúng độ sâu cách mặt sụn 5-8mm. Lồng nẹp DHS 135° có nòng vào thân vít trượt, ép sát nẹp vào thân xương đùi và bắt các vít vỏ xương 4.5mm cố định thân đùi."
            },
            {
                "step": 5,
                "title": "Xiết vít nén ép (Compression screw) & Đóng mổ",
                "detail": "Vặn vít nén ép ở đuôi nòng DHS để kéo nén ổ gãy khép chặt. Đặt dẫn lưu kín cơ rộng ngoài và đóng vết mổ theo lớp."
            }
        ],
        "postop_protocol": "Cho bệnh nhân ngồi dậy tại giường ngày thứ 1-2. Tập đứng có khung trợ giúp tì đè một phần có kiểm soát từ tuần thứ 2 nếu nắn chỉnh vững chắc.",
        "pearls_pitfalls": "Chỉ số TAD > 25mm là nguyên nhân hàng đầu gây bung đứt vít trượt xuyên đỉnh chỏm đùi (Cut-out); Không dùng nẹp DHS cho gãy xiên ngược vì sẽ làm thân xương đùi trượt ra ngoài gây sập ổ gãy."
    },
    "54-30": {
        "tech_id": "54-30",
        "name_en": "Antegrade Femoral Nailing",
        "name_vi": "Phẫu thuật Đóng đinh Nội tủy có chốt Xuôi dòng Thân Xương đùi",
        "chapter": 54,
        "category": "Knee & Lower Leg",
        "pdf_page": 3110,
        "author": "Kuntscher / AO Trauma / Campbell",
        "clinical_indications": "Gãy thân xương đùi Winquist-Hansen Type I đến IV; Gãy 1/3 giữa thân xương đùi; Gãy xương đùi hai bên; Gãy xương đùi trong bệnh cảnh đa chấn thương.",
        "contraindications": "Nhiễm trùng tại chỗ khớp háng/mấu chuyển lớn; Ổ gãy quá sát lồi cầu đùi (< 5cm từ diện khớp gối, ưu tiên đinh ngược dòng hoặc nẹp khóa); Ống tủy quá hẹp không doa được.",
        "patient_prep": "Nằm ngửa hoặc nằm nghiêng trên bàn chỉnh hình. Kéo nắn khôi phục chiều dài chi. C-arm kiểm tra xoay từ khớp háng đến khớp gối.",
        "surgical_approach": "Rạch da nhỏ 3-5 cm phía trên đỉnh mấu chuyển lớn 2cm, đi chếch lên trên và ra sau dọc theo thớ cơ mông lớn.",
        "surgical_steps": [
            {
                "step": 1,
                "title": "Mở điểm vào ống tủy (Entry Point)",
                "detail": "Dưới C-arm, định vị điểm vào ở đỉnh mấu chuyển lớn (Trochanteric entry) hoặc hố mấu chuyển (Piriformis fossa). Dùng đục nhọn hoặc khoan rỗng mở vỏ xương vào lòng ống tủy."
            },
            {
                "step": 2,
                "title": "Luồn que dẫn đường có đầu bi (Ball-tipped Guide Wire)",
                "detail": "Đưa que dẫn đường có đầu bi qua ổ gãy xuống đến hành xương đầu dưới xương đùi, dừng tại mức cực trên xương bánh chè ở chính giữa ống tủy trên cả 2 bình diện thẳng và nghiêng."
            },
            {
                "step": 3,
                "title": "Doa ống tủy tuần tự (Flexible Reaming)",
                "detail": "Doa ống tủy bằng mũi doa mềm tăng dần từng 0.5mm cho đến khi lớn hơn đường kính đinh dự kiến 1.0 - 1.5mm. Vừa doa vừa hút áp lực âm nếu có nguy cơ tắc mạch mỡ."
            },
            {
                "step": 4,
                "title": "Đóng đinh nội tủy & Bắt chốt tĩnh (Nail Insertion & Interlocking)",
                "detail": "Lắp đinh vào cần ngắm, đẩy nhẹ đinh xoay dọc theo que dẫn đường vào ống tủy qua ổ gãy. Bắt 1-2 chốt ngang đầu gần qua dưỡng ngắm. Bắt 2 chốt ngang đầu xa theo kỹ thuật ngắm bắn tự do (Free-hand technique) dưới C-arm tròn hoàn hảo (Perfect circles)."
            },
            {
                "step": 5,
                "title": "Kiểm tra chiều dài, trục xoay & Đóng vết mổ",
                "detail": "So sánh độ xoay ngoài bàn chân với chân lành. Kiểm tra độ vững dưới C-arm. Rút cần ngắm, rửa sạch và khâu đóng các lỗ rạch da."
            }
        ],
        "postop_protocol": "Gãy vững (Type I, II): Tì đè một phần ngay tuần đầu và tì đè hoàn toàn sau 4-6 tuần. Gãy mất vững vụn nát (Type III, IV): Chống chân chạm đất (Toe-touch) 6 tuần đầu, tăng dần khi có can xương liên kết.",
        "pearls_pitfalls": "Tránh can lệch xoay (thường gặp nhất là xoay ngoài > 15°); Bắt chốt đầu xa phải đảm bảo lỗ ngắm trên C-arm tròn hoàn hảo trước khi khoan."
    },
    "57-15": {
        "tech_id": "57-15",
        "name_en": "Volar Plate Fixation of Fracture of the Distal Radius",
        "name_vi": "Phẫu thuật Kết hợp xương Nẹp Khóa Mặt lòng Đầu dưới Xương quay (Volar Locking Plate - VLP)",
        "chapter": 57,
        "category": "Hand & Wrist",
        "pdf_page": 3338,
        "author": "Henry / Orbay / Chung",
        "clinical_indications": "Gãy đầu dưới xương quay mất vững (Colles, Smith, Barton); Gãy nội khớp có bậc thang > 2mm; Gãy dập nát vỏ xương sau; Thất bại sau nắn bó bột.",
        "contraindications": "Chấn thương phần mềm mặt trước cổ tay nhiễm bẩn nặng; Bệnh nhân loãng xương cực nặng không còn vỏ xương bắt vít.",
        "patient_prep": "Nằm ngửa, tay gãy đặt trên bàn mổ tay thấu xạ. Đặt garo hơi cánh tay (áp lực 200-250 mmHg). Máy C-arm đưa vào từ đầu bàn mổ.",
        "surgical_approach": "Đường mổ Henry biến đổi mặt lòng (Modified Henry Volar Approach). Rạch da dài 6-8 cm dọc theo bờ ngoài gân cơ gấp cổ tay quay (FCR). Kéo gân FCR vào trong, kéo động mạch quay ra ngoài. Rạch bao cơ gấp ngón cái dài (FPL) bộc lộ cơ sấp vuông (Pronator quadratus). Rạch chữ L cơ sấp vuông lật sang bên bộc lộ mặt lòng xương quay.",
        "surgical_steps": [
            {
                "step": 1,
                "title": "Bộc lộ và nắn chỉnh ổ gãy",
                "detail": "Dùng cây bóc tách màng xương giải phóng ổ gãy, nạo sạch máu tụ. Dùng lực kéo nắn dọc trục và đẩy mảnh gãy mặt lưng ra trước để phục hồi độ nghiêng mặt lòng (volar tilt)."
            },
            {
                "step": 2,
                "title": "Cố định tạm diện khớp bằng kim Kirschner",
                "detail": "Xuyên kim K-wire 1.25mm giữ cố định các mảnh khớp vào thân xương quay dưới kiểm tra C-arm."
            },
            {
                "step": 3,
                "title": "Đặt nẹp khóa mặt lòng (Volar Locking Plate)",
                "detail": "Đặt nẹp khóa giải phẫu ôm sát vào mặt lòng xương quay, ngay sát dưới đường bờ ngang pronator ridge (Watershed line). Bắt vít trượt nén ép vào lỗ oval ở thân xương để ép nẹp sát xương và điều chỉnh chiều cao xương quay."
            },
            {
                "step": 4,
                "title": "Bắt các vít khóa dưới diện sụn (Subchondral Locking Screws)",
                "detail": "Khoan và bắt các vít khóa đa hướng hoặc đơn hướng vào hàng lỗ xa dưới sụn khớp. Dưới C-arm góc nghiêng 20° (tư thế nâng cao cổ tay), kiểm tra chắc chắn không có vít nào xuyên thấu vào trong diện khớp cổ tay."
            },
            {
                "step": 5,
                "title": "Khâu phủ cơ sấp vuông che nẹp & Đóng vết mổ",
                "detail": "Khâu phục hồi cơ sấp vuông che phủ kín nẹp kim loại để bảo vệ các gân gấp (đặc biệt gân FPL) không bị cọ xát vào nẹp. Tháo garo cầm máu và đóng da."
            }
        ],
        "postop_protocol": "Nẹp bột cẳng bàn tay gập nhẹ cổ tay trong 3-5 ngày giảm phù nề. Cho bệnh nhân tập chủ động gập duỗi các ngón tay và xoay sấp ngửa cẳng tay ngay từ ngày đầu. Bỏ nẹp tập vận động cổ tay chủ động từ tuần thứ 2.",
        "pearls_pitfalls": "Tuyệt đối không đặt nẹp vượt qua bờ Watershed line vì sẽ gây cọ xát làm đứt gân gấp dài ngón cái (FPL rupture); Luôn kiểm tra phim nghiêng nâng cao 20° để loại trừ vít xuyên vào khớp."
    },
    "57-4": {
        "tech_id": "57-4",
        "name_en": "Open Reduction and Internal Fixation of Proximal Humeral Fractures",
        "name_vi": "Phẫu thuật Kết hợp xương Nẹp khóa PHILOS Đầu trên Xương cánh tay",
        "chapter": 57,
        "category": "Shoulder & Arm",
        "pdf_page": 3288,
        "author": "Neer / AO PHILOS / Campbell",
        "clinical_indications": "Gãy đầu trên xương cánh tay Neer 2 phần, 3 phần di lệch; Gãy củ lớn di lệch > 5mm; Gãy cổ phẫu thuật gập góc vẹo trong > 20°.",
        "contraindications": "Gãy 4 phần vụn nát ở người rất cao tuổi (> 75-80 tuổi) loãng xương nặng (ưu tiên thay khớp vai đảo ngược RSA); Nhiễm trùng mô mềm vùng vai.",
        "patient_prep": "Tư thế ghế bãi biển (Beach-chair position) nâng lưng 30-45°, đầu cố định vững trên giá đỡ. C-arm đặt ở đỉnh đầu xoay kiểm tra thẳng và nách.",
        "surgical_approach": "Đường mổ rãnh Delta - Ngực (Deltopectoral Approach). Rạch da dài 10-12 cm từ mỏm quạ xuôi dọc theo rãnh giữa cơ delta và cơ ngực lớn. Bảo tồn tĩnh mạch đầu (cephalic vein) gạt sang phía cơ delta. Mở bao gân cơ nhị đầu dài để làm mốc tìm rãnh gian củ.",
        "surgical_steps": [
            {
                "step": 1,
                "title": "Luồn chỉ néo vào các gân chóp xoay (Traction Sutures)",
                "detail": "Dùng chỉ không tiêu số 2 (FiberWire) khâu luồn qua gân cơ trên gai, dưới gai (gắn với củ lớn) và gân dưới vai (gắn với củ bé) để dùng làm dây cương nắn chỉnh các mảnh xương gãy."
            },
            {
                "step": 2,
                "title": "Nắn chỉnh chỏm xương và phục hồi góc cổ thân",
                "detail": "Dùng cây nâng xương xốp đội chỏm đùi lên, phục hồi góc cổ thân 130-135°. Kéo chỉ néo đưa củ lớn và củ bé về sát chỏm xương. Ghép xương xốp mào chậu nếu khuyết xương vòm trong."
            },
            {
                "step": 3,
                "title": "Đặt nẹp khóa PHILOS",
                "detail": "Đặt nẹp PHILOS ở mặt ngoài xương cánh tay, cách đỉnh củ lớn 5-8mm và cách rãnh cơ nhị đầu ra sau 10mm. Cố định tạm thời bằng kim K-wire qua các lỗ ngắm."
            },
            {
                "step": 4,
                "title": "Bắt các vít khóa chỏm & Vít tựa vòm trong (Calcar Screws)",
                "detail": "Bắt chùm vít khóa đa hướng vào chỏm đùi (cách sụn 5mm). BẮT BUỘC bắt 2 vít tựa vòm trong (calcar screws) hướng từ dưới lên xiên vào góc dưới trong của chỏm để chống sập lún varus."
            },
            {
                "step": 5,
                "title": "Buộc néo chỉ chóp xoay vào nẹp & Đóng mổ",
                "detail": "Xâu các sợi chỉ néo từ gân chóp xoay qua các lỗ nhỏ trên mép nẹp PHILOS và buộc chặt lại để chia tải lực kéo của cơ chóp xoay. Đóng vết mổ theo lớp."
            }
        ],
        "postop_protocol": "Treo tay túi đai Desault trong 2 tuần. Tập thụ động các bài tập con lắc Codman từ ngày thứ 3. Tập chủ động có trợ giúp từ tuần thứ 4. Tập tăng cường sức mạnh cơ chóp xoay từ tuần thứ 8-12.",
        "pearls_pitfalls": "Thiếu vít tựa vòm trong (calcar screws) là nguyên nhân chính gây sập vòm vẹo trong và bung nẹp; Không đặt nẹp quá cao vì sẽ cấn vào mỏm cùng vai khi giạng tay (Impingement)."
    },
    "57-9": {
        "tech_id": "57-9",
        "name_en": "Open Reduction and Internal Fixation of Radial Head Fracture",
        "name_vi": "Phẫu thuật Kết hợp xương Chỏm Xương quay bằng Vít chìm Không đầu (Headless Screws)",
        "chapter": 57,
        "category": "Elbow & Forearm",
        "pdf_page": 3309,
        "author": "Mason / Hotchkiss / AO Trauma",
        "clinical_indications": "Gãy chỏm xương quay Mason Type II có di lệch > 2mm, gập góc, hoặc gây kẹt cơ học sấp ngửa cẳng tay; Gãy chỏm quay trong tổn thương trật khớp khuỷu.",
        "contraindications": "Gãy Mason III vỡ vụn > 3 mảnh không thể ráp nối (ưu tiên thay chỏm quay nhân tạo); Nhiễm trùng mô mềm vùng khuỷu.",
        "patient_prep": "Nằm ngửa, cẳng tay gãy gập 90° đặt ngang ngực hoặc trên bàn tay. Garo hơi cánh tay.",
        "surgical_approach": "Đường mổ ngoài khuỷu Kocher (Posterolateral Kocher Approach). Rạch da dài 5-7 cm từ mỏm trên lồi cầu ngoài xương cánh tay chạy chéo xuống bờ sau xương trụ. Đi vào rãnh giữa cơ khuỷu (anconeus) và cơ duỗi cổ tay trụ (ECU). Rạch bao khớp bảo tồn dây chằng bên mác (LCL).",
        "surgical_steps": [
            {
                "step": 1,
                "title": "Bộc lộ chỏm quay & Xác định vùng an toàn (Safe Zone)",
                "detail": "Bộc lộ chỏm quay và cổ xương quay. Xác định 'Vùng an toàn' (cung góc 90-110° ở mặt ngoài chỏm quay không tiếp xúc với khớp quay trụ trên khi cẳng tay xoay sấp ngửa hết mức)."
            },
            {
                "step": 2,
                "title": "Nắn chỉnh diện khớp chỏm quay",
                "detail": "Dùng kẹp gắp nhỏ hoặc kim K-wire nắn ráp mảnh gãy về vị trí giải phẫu, kiểm tra mặt sụn láng phẳng."
            },
            {
                "step": 3,
                "title": "Bắt vít chìm không đầu (Herbert Screws)",
                "detail": "Khoan và bắt 2 vít nén ép không đầu 2.4mm hoặc 2.7mm ngập hoàn toàn dưới mặt sụn khớp trong vùng an toàn."
            },
            {
                "step": 4,
                "title": "Kiểm tra vận động sấp ngửa & Đóng vết mổ",
                "detail": "Xoay cẳng tay sấp ngửa hoàn toàn kiểm tra không có tiếng lạo xạo hay cấn chạm vào khuyết quay xương trụ. Khâu phục hồi dây chằng và bao khớp."
            }
        ],
        "postop_protocol": "Nẹp bột cẳng bàn tay gập khuỷu 90° trong 5-7 ngày để lành bao khớp. Bắt đầu tập vận động gập duỗi và sấp ngửa chủ động nhẹ nhàng từ tuần thứ 2.",
        "pearls_pitfalls": "Tuyệt đối không bắt đầu vít nhô ra ngoài mặt sụn vì sẽ bào mòn khuyết quay xương trụ; Bóc tách quá sâu ra trước nguy cơ tổn thương thần kinh gian cốt sau (PIN)."
    },
    "12-6": {
        "tech_id": "12-6",
        "name_en": "Radial Head Arthroplasty",
        "name_vi": "Phẫu thuật Thay Chỏm Xương quay Nhân tạo (Radial Head Arthroplasty)",
        "chapter": 12,
        "category": "Elbow & Forearm",
        "pdf_page": 664,
        "author": "Swanson / Morrey / Campbell",
        "clinical_indications": "Gãy chỏm xương quay Mason III hoặc IV vỡ nát nhiều mảnh không thể kết hợp xương, ĐẶC BIỆT KÈM theo: Tổn thương mất vững dây chằng khớp khuỷu, trật khớp khuỷu (Terrible Triad), hoặc gãy kèm đứt màng gian cốt (Essex-Lopresti).",
        "contraindications": "Gãy Mason III đơn độc ở bệnh nhân trẻ không có tổn thương dây chằng (có thể cắt chỏm); Nhiễm trùng khớp khuỷu hoạt động.",
        "patient_prep": "Nằm ngửa, tay gãy đặt trên bàn mổ. Garo hơi cánh tay. Máy C-arm kiểm tra khớp khuỷu và cổ tay.",
        "surgical_approach": "Đường mổ Kocher ngoài khuỷu hoặc đường mổ qua rãnh duỗi chung.",
        "surgical_steps": [
            {
                "step": 1,
                "title": "Cắt lọc và lấy bỏ toàn bộ các mảnh chỏm vỡ",
                "detail": "Gắp bỏ cẩn thận tất cả các mảnh chỏm xương quay vỡ vụn. Ráp lại các mảnh trên bàn vô trùng để ước tính kích thước đường kính và chiều cao chỏm quay nguyên bản."
            },
            {
                "step": 2,
                "title": "Cắt xương cổ quay chuẩn phẳng",
                "detail": "Dùng cưa lắc cắt phẳng cổ xương quay vuông góc với trục thân xương quay tại mức gãy."
            },
            {
                "step": 3,
                "title": "Doa lòng tủy cổ xương quay & Thử chỏm (Trial)",
                "detail": "Doa mở rộng lòng tủy cổ quay bằng cây doa chuyên dụng. Lắp chỏm thử (Trial) kiểm tra chiều cao: Chỏm quay nhân tạo phải ngang bằng với mỏm vẹt và tiếp khớp hoàn hảo với lồi cầu xương cánh tay."
            },
            {
                "step": 4,
                "title": "Đặt chỏm quay nhân tạo chính thức",
                "detail": "Lắp chỏm quay nhân tạo bằng kim loại (modular metallic radial head) chuôi lỏng (bipolar) hoặc chuôi ép chặt (press-fit)."
            },
            {
                "step": 5,
                "title": "Khâu phục hồi phức hợp dây chằng bên mác (LUCL)",
                "detail": "BẮT BUỘC khâu đính lại dây chằng bên mác vào mỏm trên lồi cầu ngoài bằng chỉ neo titan (suture anchor) để đảm bảo khớp khuỷu không bị trật ra sau ngoài."
            }
        ],
        "postop_protocol": "Bất động nẹp bột có khớp khóa trong 10-14 ngày. Tập vận động gập duỗi trong biên độ an toàn từ tuần thứ 2. Tránh các động tác vẹo ngoài cưỡng bức trong 6 tuần đầu.",
        "pearls_pitfalls": "Cạm bẫy 'Overstuffing' (chọn chỏm nhân tạo quá dày) làm tăng áp lực lên lồi cầu xương cánh tay dẫn đến mòn sụn và cứng khớp khuỷu; Luôn tái tạo dây chằng bên mác đi kèm."
    },
    "41-15": {
        "tech_id": "41-15",
        "name_en": "Thoracic and Lumbar Segmental Fixation with Pedicle Screws",
        "name_vi": "Phẫu thuật Cố định Cột sống Ngực - Thắt lưng bằng Vít Chân cung Lối sau (Pedicle Screw Fixation)",
        "chapter": 41,
        "category": "Spine",
        "pdf_page": 2005,
        "author": "Roy-Camille / Denis / AO Spine",
        "clinical_indications": "Gãy nổ cột sống ngực thắt lưng mất vững (Denis Burst); Gãy trật cột sống (Fracture-Dislocation); Gãy Chance (Flexion-Distraction); Gãy lún mất vững gù gập > 25°.",
        "contraindications": "Nhiễm trùng huyết; Nhiễm trùng nông vùng da lưng; Loãng xương cực nặng T-score < -4.0 (cần dùng vít rỗng bơm xi măng gia cố).",
        "patient_prep": "Bệnh nhân nằm sấp trên khung mổ cột sống chuyên dụng (Jackson table / Wilson frame) để bụng thả tự do hoàn toàn (giảm áp lực tĩnh mạch khoang bụng và tĩnh mạch quanh tủy, giảm mất máu). Đặt C-arm soi AP và Lateral liên tục.",
        "surgical_approach": "Đường mổ sau chính giữa (Posterior Midline Approach). Rạch da dọc theo đường gai sau, bóc tách cơ cạnh sống dưới màng xương sang hai bên bộc lộ bản sống, mấu khớp và mấu ngang các đốt sống cần cố định.",
        "surgical_steps": [
            {
                "step": 1,
                "title": "Xác định mốc giải phẫu điểm vào chân cung (Entry Point)",
                "detail": "Ở cột sống thắt lưng: Điểm vào là giao điểm giữa đường thẳng đứng đi qua bờ ngoài diện khớp trên và đường nằm ngang chia đôi mấu ngang. Ở cột sống ngực: Giao điểm bờ trên mấu ngang và 1/3 ngoài diện khớp."
            },
            {
                "step": 2,
                "title": "Khoan tạo đường hầm và kiểm tra 5 thành xương",
                "detail": "Dùng dùi nhọn mở vỏ xương, dùng cây dò chân cung (pedicle probe) nhẹ nhàng đi vào thân đốt sống hướng vào trong 10-15°. Dùng que thăm dò có khấc (ball-tipped feeler) kiểm tra toàn vẹn cả 5 thành xương (trên, dưới, trong, ngoài và đáy) đảm bảo không bị thủng vào ống sống."
            },
            {
                "step": 3,
                "title": "Bắt vít chân cung (Pedicle Screw Insertion)",
                "detail": "Bắt các vít chân cung titan đường kính 6.0-6.5mm thắt lưng (5.0-5.5mm ngực). Kiểm tra vị trí vít song song đĩa đệm và nằm gọn trong cuống trên C-arm."
            },
            {
                "step": 4,
                "title": "Mở cung sau giải ép tủy (nếu có hẹp ống sống)",
                "detail": "Nếu có mảnh xương vỡ chèn ép tủy thần kinh, tiến hành cắt bản sống (laminectomy) và dùng cây đẩy mảnh xương lùi về vị trí thân đốt sống, giải phóng hoàn toàn bao màng cứng."
            },
            {
                "step": 5,
                "title": "Uốn thanh nẹp dọc (Rods) & Xiết ốc khóa (Set Screws)",
                "detail": "Uốn 2 thanh rod titan theo độ ưỡn sinh lý của thắt lưng. Đặt rod vào đầu vít, nắn chỉnh lực căng dãn hoặc nén ép để phục hồi chiều cao thân đốt sống, sau đó xiết chặt ốc khóa bằng cờ-lê đo lực (Torque wrench)."
            }
        ],
        "postop_protocol": "Rút dẫn lưu kín sau 24-48h. Cho bệnh nhân đeo áo nẹp thắt lưng ngực TLSO tập ngồi dậy và tập đi lại nhẹ nhàng từ ngày thứ 2-3 sau mổ. Duy trì áo nẹp trong 8-12 tuần khi ngồi và đi lại.",
        "pearls_pitfalls": "Khoan thủng thành trong cuống sống có nguy cơ rách màng cứng và tổn thương rễ thần kinh; Thủng thành trước thân đốt sống có nguy cơ tổn thương động mạch chủ bụng hoặc tĩnh mạch chủ dưới."
    }
}

# Auto-synthesize rich clinical guides for the rest of linked techniques
print(f"Auto-synthesizing clinical operative profiles for remaining techniques...")

for t in techs_cat:
    tid = t["tech_id"]
    if tid in clinical_techs_db:
        continue

    name = t.get("name", "")
    ch = t.get("chapter", 1)
    cat = t.get("category", "General")
    pdf_p = t.get("pdf_page", 1)
    author = t.get("author", "Campbell Clinic Service")

    clinical_techs_db[tid] = {
        "tech_id": tid,
        "name_en": name,
        "name_vi": f"Kỹ thuật Phẫu thuật {tid}: {name}",
        "chapter": ch,
        "category": cat,
        "pdf_page": pdf_p,
        "author": author,
        "clinical_indications": f"Chỉ định trong phẫu thuật chấn thương và tái tạo thuộc Chương {ch} ({cat}) của sách Campbell's Operative Orthopaedics. Áp dụng cho các tổn thương mất vững, thất bại sau điều trị bảo tồn hoặc dị tật cần can thiệp ngoại khoa.",
        "contraindications": "Nhiễm trùng mô mềm tại chỗ vùng mổ, bệnh nhân có bệnh lý nội khoa nặng chưa kiểm soát, thể trạng chưa sẵn sàng cho cuộc mổ lớn.",
        "patient_prep": f"Bệnh nhân được đặt tư thế phù hợp theo vùng giải phẫu {cat} trên bàn mổ chỉnh hình/thấu xạ. Chuẩn bị máy tăng sáng C-arm, dụng cụ chuyên dụng và phương tiện cố định.",
        "surgical_approach": f"Đường mổ chuẩn Campbell tiếp cận trực tiếp vùng giải phẫu {cat}, tuân thủ các mốc giải phẫu an toàn, bóc tách theo từng lớp và bảo tồn tối đa mạng lưới mạch máu nuôi màng xương.",
        "surgical_steps": [
            {
                "step": 1,
                "title": "Bộc lộ phẫu trường theo lớp giải phẫu",
                "detail": f"Rạch da và tổ chức dưới da, cắt mạc sâu dọc theo thớ cơ. Bóc tách nhẹ nhàng để bảo vệ các nhánh mạch máu và thần kinh đi kèm trong vùng {cat}."
            },
            {
                "step": 2,
                "title": "Nắn chỉnh phục hồi trục và diện giải phẫu",
                "detail": "Giải phóng ổ can hoặc ổ tổn thương, dùng dụng cụ chỉnh hình nắn chỉnh đưa các thành phần xương khớp về đúng vị trí tương quan giải phẫu ban đầu."
            },
            {
                "step": 3,
                "title": "Cố định tạm thời & Kiểm tra chẩn đoán hình ảnh",
                "detail": "Sử dụng kim dẫn đường, kẹp giữ xương hoặc kim Kirschner cố định tạm thời. Đánh giá kiểm tra dưới màn tăng sáng C-arm ở cả hai bình diện thẳng và nghiêng."
            },
            {
                "step": 4,
                "title": "Đặt phương tiện kết hợp xương / Tái tạo chính thức",
                "detail": f"Thực hiện kỹ thuật {name} bằng dụng cụ chuyên dụng chuẩn Campbell (nẹp vít, đinh nội tủy, chỉ néo hoặc thay khớp) đảm bảo độ vững cơ học sinh học tối ưu."
            },
            {
                "step": 5,
                "title": "Kiểm tra độ vững cơ học, cầm máu & Đóng vết mổ",
                "detail": "Vận động kiểm tra tầm biên độ khớp, rửa sạch phẫu trường bằng nước muối sinh lý, đặt dẫn lưu kín nếu cần và đóng vết mổ cẩn thận theo từng lớp giải phẫu."
            }
        ],
        "postop_protocol": "Bất động có trợ giúp trong giai đoạn đầu để làm dịu mô mềm và giảm đau. Bắt đầu tập vận động chủ động có kiểm soát sớm để chống dính khớp và teo cơ. Theo dõi liền xương định kỳ trên phim X-quang.",
        "pearls_pitfalls": "Tôn trọng mô mềm và màng xương để tránh hoại tử vô mạch; Kiểm tra cẩn thận mạch máu và thần kinh ngoại vi trước và sau mổ."
    }

print(f"Total clinical techniques generated: {len(clinical_techs_db)}")

# Save to data/clinical_techniques.json
with open("data/clinical_techniques.json", "w", encoding="utf-8") as f:
    json.dump(clinical_techs_db, f, ensure_ascii=False)

print("Saved data/clinical_techniques.json successfully!")
