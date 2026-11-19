# Retopo và topology chuẩn cho rig + animation (game 3D Unity, mobile / stylized)

Bản nghiên cứu 2026-11-18. Dành cho animator / rigger / artist. Số liệu có ghi nguồn; chỗ nào là kinh nghiệm chung mà nguồn không chốt thì ghi "ước lượng".

Liên quan trong repo: bước "Kiểm model" của skill `frolvy_rig` (`.claude/skills/frolvy_rig/SKILL.md` mục 1, `R.check_model`, `R.sections`) và luật skin theo vùng ở mục 4 cùng file. Tài liệu này là phần "model phải thế nào thì rig mới tốt", chạy trước các bước đó.

---

## 1. Nguyên tắc chung

1. **Toàn quad.** Quad cho loop sạch, smooth đều, skin mượt. Tam giác và n-gon (đa giác 5 cạnh trở lên) chỉ để ở chỗ phẳng, cứng, không gập. Game có triangulate lúc xuất, nhưng lúc làm vẫn giữ quad để edge loop còn đọc được.
2. **Edge loop vuông góc với hướng gập.** Khớp bản lề (khuỷu, gối) gập quanh một trục: loop phải bao quanh chi, vuông góc xương. Loop song song xương ở vùng gập thì mesh bị kéo giãn một phía, nén một phía, rồi gãy.
3. **Edge flow theo cơ.** Loop đi theo hướng cơ chính (vòng quanh mắt, quanh miệng, vai chảy xuống ngực và ra lưng). Cơ co thì da dồn về hướng đó, lưới theo cơ thì biến dạng tự nhiên.
4. **Mật độ theo mức biến dạng.** Dày ở khớp, mặt, bàn tay. Thưa ở thân phẳng, đùi, cẳng tay giữa. Cạnh có độ dài gần đều qua vùng gập (cạnh quá ngắn cạnh quá dài sẽ giãn nén không đều khi skin).
5. **Pole (đỉnh 3 hoặc 5 cạnh) đặt ở vùng phẳng, ít biến dạng.** Không để pole nằm trên đường nếp gập, trên đỉnh khuỷu / gối, hay giữa khớp. Dời pole ra xa trục gập.
6. **Loop liên tục.** Loop bị đứt (kết thúc giữa khớp) gây giãn / sập. Loop quanh khớp phải khép kín hoặc nối được sang vùng cạnh.
7. **Test sớm.** Xoay khuỷu / gối 90°, xoay cẳng tay, nhấc vai, nhìn có candy wrapper, nhăn hình sao, sập nếp không. Sửa topology sớm rẻ hơn sửa weight nhiều.

Nguồn: [NovEdge – Anatomy-driven retopology](https://novedge.com/blogs/design-news/zbrush-tip-anatomy-driven-retopology-for-predictable-deformation), [BlenderCG – model hỏng trước khi thêm bone](http://blender-cg.net/character-modeling-decisions-that-break-rigging/), [Tripo3D – chuẩn bị mesh cho deformation](https://www.tripo3d.ai/blog/explore/smart-mesh-character-mesh-deformation-readiness), [Wikipedia – Edge loop](https://en.wikipedia.org/wiki/Edge_loop), [Wikipedia – Retopology](https://en.wikipedia.org/wiki/Retopology).

---

## 2. Theo từng vùng

Quy ước: "loop" = edge loop vòng quanh chi / thân. Số loop là cho bản **realistic / mid-poly**; cột "Low-poly mobile" là mức tối thiểu chịu được (ước lượng, xem mục 4 và 8).

| Vùng | Loop khuyến nghị | Low-poly mobile (tối thiểu) | Hướng loop / vị trí so với joint | Tránh |
|---|---|---|---|---|
| **Vai** | 3–4 loop đồng tâm quanh khớp, thêm 1 loop dọc ranh trước/sau cơ delta; pose cực đoan 5–6 | 2 loop đồng tâm + 1 loop nách | Loop quanh khớp vai như hình cầu; flow đi xuống ngực và vòng ra lưng (xương đòn, delta, nách, ngực, bả vai) | Pole ngay trên joint vai; tam giác ở nách |
| **Khuỷu** | 3 loop (2–3 là mức sàn) trong vùng nếp gập mặt trong | 2 loop, 1 loop đúng joint + 1 mỗi bên | Loop vuông góc xương, 1 loop **ngay tại joint** (hoặc đối xứng hai bên joint), cạnh dài đều; pole dời khỏi nếp | Tam giác / n-gon; loop chạy dọc cánh tay |
| **Đầu gối** | 3 loop, thêm ở mặt sau gối (gập nhiều nhất) | 2 loop (1 loop ngay gối) | Như khuỷu. Xương bánh chè nằm mặt trước, mặt sau cần cạnh dày hơn | Quá ít loop ở mặt sau, gối bị vuông / nhọn |
| **Hông** | 3–4 loop đồng tâm quanh khớp (cầu), flow từ mông qua bẹn lên bụng dưới | 2 loop + 1 loop háng | Ball joint xoay nhiều hướng: loop kiểu vòng cung, tách sạch hai đùi ở háng | Háng dính hai chân; pole ngay joint hông |
| **Cổ** | 2–3 loop quanh cổ, nối liền loop vai / xương đòn / chẩm | 2 loop | Loop tròn quanh cổ, ranh giới cằm–cổ có loop riêng (cúi đầu thì cằm không dính ngực) | Cổ chỉ 1 loop; cằm liền cổ không có khe |
| **Cổ tay** | 2–3 loop quanh cổ tay + 1 loop ổn định phía trên và dưới | 2 loop | Loop tròn vuông góc xương; thêm loop dọc cẳng tay để chịu xoắn (candy wrapper, mục 6) | Cổ tay 1 loop; dải weight 50/50 rơi vào một hàng đỉnh |
| **Ngón tay** | 2–3 loop quanh mỗi khớp chính (đốt gốc, đốt giữa), ít loop ở thân đốt | 1–2 loop quanh khớp ngón, hoặc ngón liền khối kiểu mitten nếu không anim ngón | Loop khớp ngón nằm ngay joint; kết thúc loop sạch ở lòng bàn tay (chỗ hay xẹp) | Loop kết thúc bừa ở lòng bàn tay; ngón dính nhau |
| **Bàn chân** | 2 loop quanh cổ chân, 1–2 loop ở gốc ngón (khớp bóng) để mũi chân gập | 1–2 loop quanh cổ chân + 1 loop khớp bóng | Loop cổ chân vuông xương; loop khớp ngón (ball) vuông trục gập của mũi chân | Đế giày không có loop ở chỗ gập; mũi giày cứng không cho gập |
| **Mặt: miệng** | Loop tròn đồng tâm quanh miệng (môi), 2–3 vòng ra ngoài | 1–2 vòng quanh miệng | Theo cơ vòng miệng, nối ra nếp mũi–má (nasolabial) | Cạnh cắt ngang đường môi, khóe miệng bị rách khi mở |
| **Mặt: mắt** | Loop tròn đồng tâm quanh mắt (mi trên / dưới), 2–3 vòng | 1–2 vòng | Theo cơ vòng mắt; mi nháy thì trượt trên cầu mắt, nên loop mi phải khép kín | Không có loop quanh mắt: mi trượt chứ không khép |
| **Mặt: mày / trán** | Loop ngang trán, vài loop vòng cung trên mắt, nối với loop mắt | 1 loop mày | Ngang theo cơ trán; vòng cung theo xương mày | Loop dọc chạy xuyên mày làm mày không nhăn |
| **Thân / bụng** | Thưa. 2–3 loop quanh eo cho spine; loop ngực để ngực nở | 2 loop quanh eo / bụng | Loop ngang vuông xương sống; eo cần loop vì thân gập / xoắn | Mật độ đều khắp thân bỏ phí; eo chỉ 1 loop |

**Vị trí loop so với joint.** Ba kiểu thường dùng:
- **Loop ngay tại joint** (joint đi xuyên qua loop): quen thuộc ở khuỷu / gối, giữ đúng điểm gập.
- **Hai loop đối xứng hai bên joint:** mềm hơn, đỡ nhọn đỉnh khuỷu.
- Joint của rig phải nằm **ở trung tâm mặt cắt** của chi, đúng tâm nếp gập, không lệch ra ngoài mesh. Frolvy: dùng `R.sections` để lấy tâm mặt cắt, rồi đặt joint (skill `frolvy_rig` mục 2).
- Sai số vài mm không sao, nhưng joint lệch nhiều khiến phần weight 50/50 rơi vào hàng đỉnh sai, mesh gập méo.

**Số loop tối thiểu quanh khớp.** Hầu hết nguồn: 2–3 loop cho khuỷu / gối (3 nếu muốn tròn trịa), 3–4 cho vai / hông. Bản low-poly chấp nhận 2 nếu nhân vật stylized và camera xa, nhưng bù bằng weight tay cẩn thận và (nếu cần) joint phụ.

Nguồn: [CGTyphoon – Elbow topology](https://cgtyphoon.com/topology/elbow-topology-explained-for-character-modeling/), [NovEdge](https://novedge.com/blogs/design-news/zbrush-tip-anatomy-driven-retopology-for-predictable-deformation), [Tripo3D – mesh optimization for rigging](https://www.tripo3d.ai/blog/explore/smart-mesh-mesh-optimization-for-animation-rigging), [Tripo3D – hand topology](https://www.tripo3d.ai/blog/explore/smart-mesh-topology-for-hands-fingers-low-poly), [Reallusion – Face Topology Guide](https://wiki.reallusion.com/Content_Dev:CC_Face_Topology_Guide), [VSquad – Face topology](https://vsquad.art/blog/modeling-guide-to-achieving-good-face-topology), [M3DS Academy – facial rigging basics](https://www.m3dsacademy.com/blog/facial-rigging-basics-every-character-artist-should-know).

---

## 3. Pose tạo mesh

- **T-pose** (tay dang ngang): cũ nhất, auto-rig (Mixamo, một số tool retarget) thường đòi. Dễ đặt joint đối xứng. Nhược điểm: vai bị kéo xa trạng thái nghỉ, hay méo nách khi hạ tay.
- **A-pose** (tay hạ khoảng 30–45°): gần dáng thật, vai ít phải xoay hơn khi anim, ít méo vai. Hơi khó đặt trục tay hơn. Với game thường dùng A-pose hoặc T-pose tuỳ chuẩn của dự án.
- Chọn **một** pose cho cả dự án, ghi vào brief. Mesh, joint, bind pose phải cùng pose. Giữ bản copy pose trung tính để reset.
- **Khớp hơi gập sẵn:** khuỷu và gối gập nhẹ (vài độ đến ~15° là đủ, ước lượng) giúp rigger / IK biết chiều gập, và nếp gấp tạo sẵn không bị phẳng. Chi duỗi thẳng tuyệt đối dễ khiến IK gập ngược. Có người sculpt khuỷu 45°, gối 45° rồi chạy skin ở dáng giữa các tư thế cực trị, nhưng đó là lựa chọn riêng, không phải chuẩn.
- **Ngón tay:** xoè nhẹ, có khe giữa các ngón (đủ để quét mặt cắt lấy tâm từng ngón, như bước "ngón tay" của skill frolvy_rig), bàn tay ở dáng mở / trung tính, ngón hơi cong tự nhiên. Ngón dính sát nhau thì skin hai ngón nhập một. Ngón không bao giờ thẳng trục tuyệt đối nên joint ngón thường phải xoay tay cho đúng.
- **Đối xứng:** mesh đối xứng qua mặt phẳng giữa. Rig dựng một bên rồi mirror, mesh lệch thì mirror weight lệch theo (skill frolvy_rig kiểm: Y lên, mặt nhìn +Z, phải là −X).

Nguồn: [Polycount – T-pose advantages](https://polycount.com/discussion/87255/different-t-pose-advantages), [Tumblr askagamedev – A-pose vs T-pose](https://www.tumblr.com/askagamedev/694298319820849152/are-there-any-differences-between-an-a-pose-and-a), [GarageFarm – T-pose](https://garagefarm.net/blog/t-pose-significance-use-and-modeling-insights), [Nhance – T vs A pose](https://nhance-school.com/tools/glossary/t-pose-vs-a-pose), [OurCodeWorld – rigging readiness](https://ourcodeworld.com/articles/read/4299/ai-character-rigging-readiness-t-pose-edge-flow-auto-rig-motion-test-and-fbx-export).

---

## 4. Polycount game và LOD (Unity, mobile / stylized)

**Con số (các nguồn lệch nhau nhiều, dùng làm khoảng tham khảo):**

| Loại | Khoảng tri (triangle) | Ghi chú |
|---|---|---|
| Nhân vật stylized mobile "nhẹ" | 1.500–5.000 | lowpoly3d, Neural4D |
| Hero casual stylized mobile | 3.000–15.000 | Sunstrike, nhiều nguồn khác |
| NPC / quái | ~2.000–8.000 | |
| Hero mobile cao cấp | 15.000–40.000 | Tripo3D, Game-Ace |
| Tay (cả hai bàn) trong game stylized mobile cụ thể | tối đa 250 tri | brief Polycount |
| Unity manual cũ (5.6) cho mobile | 300–1.500 mỗi mesh | **đã cũ**, máy hiện nay chịu nhiều hơn |

**Giới hạn skin của Unity (nguồn chính hãng):**
- Mỗi đỉnh có thể bị 1–32 xương tác động khi import. Cap lúc chạy chỉnh ở `Project Settings > Quality > Skin Weights` (Auto, 1, 2, 4 Bones) hoặc `SkinnedMeshRenderer.quality`. Hơn 4 xương mỗi đỉnh giảm hiệu năng. Mobile thường đặt 2–4 xương.
- Manual cũ khuyên: dưới ~30 xương cho mobile, một Skinned Mesh Renderer cho mỗi nhân vật, 2–3 material.
- Nghĩa với artist: weight cần gọn, tối đa 4 xương mỗi đỉnh, đừng rải weight lung tung (cũng khớp với skill frolvy_rig skin bằng joint DEF).

**Cân bằng poly và chất lượng skin:**
- Cắt poly ở thân phẳng, đùi, cẳng, phần camera ít thấy. **Không cắt** loop khớp, mặt, bàn tay mà không thử deform.
- Kiểm silhouette đen phẳng từ góc camera game. Mất ngón / vai thì trả poly lại chỗ đó.
- Chi ít loop thì (a) weight tay kỹ hơn, (b) thêm joint phụ (twist, helper), (c) cho mesh hơi mập ở khớp để nếp gập đỡ lộ.
- Mobile stylized, camera xa: 2 loop quanh khớp thường đủ, miễn là loop ngay joint và không có tam giác ở nếp gập.

**LOD:**
- LOD0 giữ nguyên topology khớp. LOD1, LOD2 giảm poly bằng cách **bỏ loop ở vùng thân phẳng trước**, giữ loop khớp tới LOD cuối. Số xương và hierarchy **giống nhau** giữa các LOD để dùng chung animation (hoặc chỉ cắt joint phụ ở LOD thấp).
- Unity 6 có Mesh LOD trên Skinned Mesh Renderer (LOD Override, LOD Selection Bias). Với mobile stylized nhân vật ít, thường chỉ cần LOD0 + 1 bản thấp, hoặc không LOD nếu camera cố định (ước lượng).

Nguồn: [Unity – Modeling characters for optimal performance (5.6)](https://docs.unity3d.com/560/Documentation/Manual/ModelingOptimizedCharacters.html), [Unity – Skinned Mesh Renderer (6000.3)](https://docs.unity3d.com/6000.3/Documentation/Manual/class-SkinnedMeshRenderer.html), [Unity – QualitySettings.skinWeights](https://docs.unity3d.com/ScriptReference/QualitySettings-skinWeights.html), [Polycount – low-poly char & rigger (250 tri hands)](https://polycount.com/discussion/238743/paid-low-poly-character-artist-rigger-modular-customization-assets-1-700-2-000-tris), [Sunstrike – how game characters are made](https://sunstrikestudios.com/en/blog/how-game-characters-are-made/), [Neural4D – polygon count](https://blog.neural4d.com/user-guide/polygon-count-for-3d-game-assets-printing-and-webar/), [Tripo3D – poly count for game assets](https://www.tripo3d.ai/blog/poly-count-for-game-assets-how-to-prepare-ai-3d-models).

---

## 5. Quần áo, tóc, phụ kiện, váy / khăn / đuôi; chibi và thú

**Quần áo.**
- Mesh tách riêng lớp áo (đè lên thân) hay liền với thân đều được. Tách thì áo phải **bao ngoài thân đủ xa** để không xuyên khi gập, và nên skin theo cùng bộ joint DEF của thân. Liền thì tiết kiệm draw call, nhưng sửa thay đồ khó.
- Mobile: thường gộp thành **một** Skinned Mesh Renderer (manual Unity khuyên một mesh mỗi nhân vật) và ít material.
- Đường may, viền áo, đai, nếp: để loop khớp với loop thân ở khuỷu / vai / eo, để weight chuyển mượt cùng nhau. Áo rộng ở nách cần thêm loop để không kéo thân theo.
- Giáp / đồ cứng (giáp vai, huy hiệu, túi): thường **không biến dạng**, gán cứng 100% vào một joint (skill frolvy_rig dùng "shell cứng" cho các shell này). Đừng skin đồ cứng như đồ mềm.

**Tóc.**
- Tóc ngắn / stylized khối: một khối skin vào Head, thêm vài joint chuỗi nếu cần đung đưa.
- Tóc dài / mái / đuôi ngựa: chuỗi 2–5 joint phụ theo hướng tóc rủ, skin các lọn vào chuỗi đó. Hair card (tấm phẳng có texture) thì skin vào cùng chuỗi. Nguồn kết quả không nói riêng về hair card trong Unity, đây là hiểu biết chung (ước lượng).

**Váy, khăn, áo choàng, đuôi.**
- Bên game thường dùng **chuỗi joint phụ** (3–6 joint dọc hướng chảy của vải) skin mesh vào các joint đó. Rẻ hơn Cloth của Unity, chạy ổn mobile. Có thể thêm dynamic-bone / spring bone để nó đung đưa lúc chạy.
- Váy ngắn / vạt áo: một vòng chuỗi quanh hông (mỗi chuỗi 2–3 joint) là đủ. Chú ý váy nằm sát hai đùi: weight dễ bị đùi kéo, cần tách vùng váy khỏi đùi (xem mục 6).
- Áo choàng dài, khăn rộng: có thể dùng Cloth của Unity (một nguồn nói chỉ áo choàng mới đáng dùng Cloth), nhưng Cloth cần SkinnedMeshRenderer, chạy nặng, va chạm kém với đầu gối. Trên mobile ưu tiên chuỗi joint.
- Topology: loop **ngang** theo hướng gập của vải, các cột (dọc) song song chuỗi joint. Mỗi hàng loop ứng với một joint trong chuỗi.
- Đuôi thú: chuỗi joint dài, loop vòng ngang quanh đuôi cách đều, mỗi joint gần một loop. Đuôi nhọn giữ loop ở khoảng cách đều, đừng dồn.
- Trong repo: skill `frolvy_auto_rig` có bước "thêm chuỗi joint cho váy / vạt áo / khăn / áo choàng".

**Chibi (đầu to).**
- Cho phép **ít loop hơn** ở khớp: nguồn nói khuỷu chibi 3–4 loop so với 7–8 của realistic. Loop vẫn phải bao kín khớp.
- Đặt joint ở vị trí khớp **thực của model**, không theo tỉ lệ người thường. Auto-rig nhầm tỉ lệ chibi: kiểm cổ, vai sau khi auto-rig.
- Cổ ngắn / không cổ: vẫn cần 1–2 loop quanh chỗ nối đầu–thân để đầu to nghiêng được mà không kéo thân. Đầu to nặng nên nghiêng đầu dễ lộ lỗi.
- Tay chân ngắn mũm: loop ít nhưng cạnh đều, mesh hơi phồng ở khớp giúp nếp gập không lộ. Test chạy / nhảy sớm vì vai và hông lộ lỗi nhanh nhất.
- Mặt chibi (mắt to, miệng nhỏ): vẫn cần loop tròn quanh mắt và miệng cho blendshape.

**Thú (quadruped).**
- Loop quanh vai (xương vai trượt trên lồng ngực khi chạy), hông, gối / khuỷu sau, và mặt. Chú ý chuyển tiếp **đùi–xương chậu** và **vai–cổ**, nơi hay giãn và mất thể tích.
- Chân thú có thêm một khớp ngược (cổ chân sau cao, "gót" trông như gối ngược): cần loop đúng chỗ khớp **thực**, không theo hình người.
- Khi sculpt thú: xoay tay chân ra ngoài như đang bay giúp kéo guide retopo dễ và đặt loop quanh vai / hông hợp lý.
- Thú stylized: đầu và tai có thể là joint riêng (tai, râu, mũi), tương tự chuỗi phụ của tóc.

Nguồn: [Unity Discussions – Cloth vs blendshape vs bones on mobile](https://discussions.unity.com/t/unitys-cloth-physics-vs-blend-shapes-vs-animated-bones-for-characters-clothing-on-mobile-device/900238), [Bitsoul – cloth sim for game characters](https://bitsoulhosting.com/marketplace/blog/cloth-simulation-game-characters-blender-unity-unreal-godot), [Polycount – rig cloth/hair in games](https://polycount.com/discussion/88047/how-to-rig-and-animate-cloth-hair-in-games), [Medium – Unity & Maya cloth workflows](https://medium.com/another-angle/unity-and-maya-character-cloth-workflows-e480e1f7afd), [Stellar Game Assets – secondary animation](https://www.stellargameassets.com/post/secondary-animation-in-unity), [Tripo3D – chibi 3D model](https://www.tripo3d.ai/blog/explore/3d-chibi-model), [Threedium – chibi](https://threedium.io/create/3d-models/character/anime/chibi), [Salivity – quadruped pipeline](https://salivity.github.io/game-development/article/quadruped-character-creation-and-rigging-pipeline), [N. Anozie – cartoony quadruped topology](http://nathananozie.blogspot.com/2014/11/tip-quadruped-cartoony-topology-in.html).

---

## 6. Lỗi topology gây skin xấu và cách sửa

| Lỗi | Dấu hiệu | Nguyên nhân | Cách sửa |
|---|---|---|---|
| **Candy wrapper** (cẳng tay / cổ tay xoắn như kẹo) | Cẳng tay thắt lại thành nút khi xoay bàn tay | Skin tuyến tính (LBS): đỉnh weight nửa cẳng tay nửa bàn tay lấy trung bình hai phép xoay, sập vào trục | Thêm **twist / roll joint** (gợi ý nguồn: 1 cho cánh tay trên, 2–3 cho cẳng tay, 1 cho bắp chân); dàn weight trên nhiều loop để không có đỉnh nào ở đúng 50/50; thêm loop dọc cẳng tay; hoặc corrective blendshape. Dual quaternion giảm nhưng Unity không dùng sẵn, đừng dựa vào nó |
| **Mất thể tích (volume loss)** | Khuỷu, vai, gối xẹp khi gập | Quá ít loop; loop không bao khớp; weight chuyển quá gắt | Thêm loop quanh khớp (tối thiểu 2–3); mesh hơi phồng sẵn ở mặt trong nếp; helper joint xoay 50% (kiểu HelperJoints); corrective blendshape ở vai / cổ tay |
| **Pinch / hình sao** | Nhiều cạnh dồn vào một đỉnh khi gập | Pole 5+ cạnh đúng ở khớp | Dời pole ra xa nếp, đổi flow cho cạnh đều |
| **Giãn / sập** | Mặt kéo dài hoặc lõm | Loop đứt, lệch trục quay | Làm loop liên tục, vuông xương |
| **Mesh chéo / lồng nhau** | Áo xuyên da, váy xuyên đùi, giáp cắt vào thân | Hai lớp quá sát hoặc weight hai lớp không khớp | Tách xa lớp hơn ở khớp; weight lớp ngoài chép từ thân rồi chỉnh; váy tách vùng weight khỏi đùi; khoét thân phần bị che để khỏi xuyên (ước lượng, cách làm quen thuộc ở game) |
| **Đỉnh trùng, mặt đảo normal, vertex lạc** | Đốm đen, nứt khi anim | Dọn mesh dở dang | Merge by distance, flip normal, xóa đỉnh mồ côi |
| **Háng / nách dính** | Chân này kéo chân kia, tay kéo thân | Không đủ khe giữa hai phần | Tách 2 chi rõ ràng trong model, thêm loop háng / nách; skill frolvy_rig có luật "nách" và "không ăn bên kia" |
| **Weight bleed** (váy, áo choàng bị thân kéo) | Vải méo khi chân bước | Hai phần sát nhau nên auto-weight lẫn | Skin theo vùng chứ không auto; skill frolvy_rig `R.skin_pass` có luật cứng |

Nguồn: [Game-Ace – game character skinning](https://game-ace.com/blog/game-character-skinning/), [Polycount – low poly joints deform](https://polycount.com/discussion/84889/low-poly-joints-how-can-i-stop-the-deform), [Jessy Leite – fix candy wrap](https://jessyleite.dev/posts/blender-candy-wrap-twist-deformation/), [Arise – HelperJoints](https://ariserigging.com/docs/attachments/helperjoints/), [Autodesk forum – hand candy wrapper](https://forums.autodesk.com/t5/motionbuilder-forum/hand-twisted-like-candy-wrapper-even-with-twist-joints-in-hik/td-p/13681908), [Cinevva – weight painting problems](https://app.cinevva.com/guides/blender-weight-painting-problems).

---

## 7. Checklist trước khi rig

Đối chiếu với bước 1 "Kiểm model" của skill `frolvy_rig` (cao, đơn vị mét, Y lên, mặt nhìn +Z, phải là −X, đối xứng, từng mảnh rời và joint nó gắn vào, tay nào cầm đạo cụ, các mốc xương). Các mục dưới thêm phần topology.

**Chung (từ skill frolvy_rig)**
- [ ] Đơn vị mét, Y lên, mặt +Z, phải −X, cao đúng ý
- [ ] Mesh đối xứng (nếu rig mirror)
- [ ] Liệt kê từng mảnh rời, mỗi mảnh gắn vào joint nào; đạo cụ cầm tay đã rõ tay nào
- [ ] Đã quét mặt cắt để lấy tâm chân, thân, tay, ngón (`R.sections`)

**Pose và sạch mesh**
- [ ] Pose A hoặc T thống nhất cả dự án, mesh đã ở pose đó
- [ ] Khuỷu, gối gập nhẹ để rig biết chiều gập
- [ ] Ngón xoè, có khe giữa ngón (nếu anim ngón)
- [ ] Không đỉnh trùng, không mặt lật, không đỉnh mồ côi, không edge không-manifold
- [ ] Transform đã freeze (scale 1, xoay 0), pivot ở gốc hợp lý
- [ ] Không lỗ hở, mesh rời nằm đúng chỗ

**Topology theo vùng**
- [ ] Quad ở mọi vùng gập; tam giác / n-gon chỉ ở chỗ phẳng
- [ ] Vai ≥ 2–3 loop đồng tâm; khuỷu, gối ≥ 2 loop (3 nếu mid-poly) vuông xương
- [ ] Hông 2–3 loop quanh khớp; háng tách rõ hai chân
- [ ] Cổ ≥ 2 loop; cằm có khe với cổ
- [ ] Cổ tay có loop, có loop dọc cẳng tay chịu xoắn
- [ ] Khớp ngón có loop (nếu anim ngón); cổ chân và khớp bóng bàn chân có loop
- [ ] Mặt: loop tròn quanh mắt, miệng (nếu có blendshape / mặt)
- [ ] Không pole trên nếp gập hay trên joint

**Quần áo, phụ kiện**
- [ ] Lớp áo không xuyên thân ở pose nghỉ
- [ ] Váy / khăn / đuôi có loop ngang theo chuỗi joint dự kiến
- [ ] Đồ cứng (giáp, vũ khí) là mảnh riêng để gán cứng
- [ ] Tóc / phụ kiện lắc đã quyết dùng chuỗi joint phụ hay cứng

**Hiệu năng (Unity)**
- [ ] Poly trong ngân sách của dự án (mục 4)
- [ ] 1 Skinned Mesh Renderer / nhân vật nếu được; 2–3 material
- [ ] Số xương mục tiêu (mobile ~ dưới 30–60 tuỳ dự án, ước lượng); weight tối đa 4 xương mỗi đỉnh
- [ ] LOD: cùng hierarchy xương giữa các LOD

**Test sau khi skin thô (smoke test)**
- [ ] Xoay khuỷu / gối 90°, vai giơ cao, hạ tay, cổ cúi và xoay, cẳng tay xoắn 90°
- [ ] Nhìn candy wrapper, sập thể tích, xuyên lớp; nếu có `R.pose_stretch` thì đo cạnh giãn
- [ ] Idle, walk, jump thử sớm trước khi anim thật

---

## 8. Chưa chắc / thiếu nguồn

- **Số loop cho bản low-poly mobile** (cột "Low-poly mobile" ở mục 2) là ước lượng tổng hợp. Chỉ có nguồn nói rõ cho chibi (khuỷu 3–4 loop) và bản mid-poly (2–3). Chưa có nguồn chuẩn ngành cho từng khớp ở 1.500–5.000 tri.
- **Polycount**: các nguồn lệch nhau lớn (300 tri đến 40.000 tri). Số của Unity (300–1.500 mỗi mesh, dưới 30 xương) là manual 5.6, đã cũ. Cần chốt ngân sách theo máy mục tiêu và dự án cụ thể.
- **Khuỷu / gối hơi gập sẵn bao nhiêu độ**: nguồn chỉ nói "hơi gập"; con số vài độ đến 15° là ước lượng, các số 45° là ý riêng một vài artist.
- **Hair card, váy dùng chuỗi joint hay Cloth, số joint mỗi chuỗi**: nguồn là diễn đàn / blog, không phải tài liệu hãng. Con số 3–6 joint là kinh nghiệm chung.
- **Thú**: chỉ có vài nguồn nhỏ (blog, một bài salivity), chưa có tài liệu chuẩn cho chân sau thú (khớp ngược).
- **Cách sửa mesh chéo / lồng nhau**: tổng hợp từ kinh nghiệm chung, các nguồn tìm được ít nói trực tiếp.
- Nhiều nguồn tìm được là blog / SEO (Tripo3D, Meshy, v.v.), không phải tài liệu hãng. Đáng tin hơn: Unity docs, Reallusion wiki, Polycount, bài của rigger / artist. Nên đối chiếu thêm với ghi chú của rigger nội bộ trước khi biến thành luật cứng.
- Chưa chạy thử trên model thật của dự án (Frolvy / Studio). Nên thử checklist trên 1–2 nhân vật đã rig (ví dụ Hero RPG2, Bastion) để chỉnh số cho đúng với phong cách của team.
- `MAP.md` chưa có dòng cho file này (theo yêu cầu không sửa file khác); nếu giữ, nên thêm một dòng vào bảng docs.
