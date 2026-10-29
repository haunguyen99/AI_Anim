// SINH TỰ ĐỘNG bởi tools/studio/port_pose.py từ work/pose_lab/index.html — đừng sửa tay, sửa port_pose.py rồi chạy lại.
ST.POSE_HTML = "<div class=\"app\">\n  <header class=\"top\">\n    <div class=\"crumb\"><small id=\"projName\">Shoot Die Repeat</small><b id=\"poseName\">Pose</b></div>\n    <div class=\"tools\" role=\"toolbar\" aria-label=\"Công cụ pose\">\n      <button class=\"ibtn tool\" id=\"mSel\" title=\"Chỉ chọn khớp, không gizmo (Q)\">Chọn <kbd>Q</kbd></button>\n      <button class=\"ibtn tool\" id=\"mMove\" title=\"Dời hông, bàn chân hoặc bàn tay (IK) (W)\">Dời <kbd>W</kbd></button>\n      <button class=\"ibtn tool on\" id=\"mRot\" title=\"Xoay khớp (E)\">Xoay <kbd>E</kbd></button>\n      <button class=\"ibtn tool\" id=\"mScale\" title=\"Scale (R): rig không cho scale khớp\">Scale <kbd>R</kbd></button>\n      <button class=\"ibtn tool\" id=\"mSpace\" title=\"Trục local / world (X)\">Trục: local <kbd>X</kbd></button>\n      <span class=\"vsep\"></span>\n      <button class=\"ibtn tool on\" id=\"tLock\" title=\"Khi dời/xoay hông, hai bàn chân giữ nguyên trên sàn (IK)\">Khóa chân</button>\n      <button class=\"ibtn tool on\" id=\"tGunR\" title=\"Khi dời/xoay súng, tay phải giữ nguyên chỗ cầm (IK tay)\">Tay phải bám súng</button>\n      <button class=\"ibtn tool\" id=\"tGhost\" title=\"Bóng mờ của pose gốc để so sánh\">Bóng pose gốc</button>\n      <button class=\"ibtn tool on\" id=\"tJoints\" title=\"Hiện các điểm khớp (J)\">Điểm khớp <kbd>J</kbd></button>\n      <button class=\"ibtn tool\" id=\"tTrail\" title=\"Quỹ đạo của khớp đang chọn qua cả clip (T). Đường xanh lơ = kết quả đang thấy (có vật lý / AutoPhysics), đường xám nét đứt = pose key gốc. Mỗi chấm là một frame: chấm thưa = nhanh, dày = chậm; chấm to = frame đang xem\">Quỹ đạo <kbd>T</kbd></button>\n      <button class=\"ibtn tool on\" id=\"tRef\" hidden title=\"Ảnh ref của frame đang xem, cạnh model (G)\">Ref <kbd>G</kbd></button>\n      <span class=\"vsep\"></span>\n      <button class=\"ibtn tool\" id=\"bPB\" title=\"Quay playblast (nhiều camera) và tải .webm\">Quay playblast</button>\n      <button class=\"ibtn tool\" id=\"undo\" title=\"Hoàn tác (Ctrl+Z)\">Hoàn tác</button>\n      <button class=\"ibtn tool\" id=\"resetAll\" title=\"Trả cả pose về bản gốc\">Về pose gốc</button>\n      <span class=\"vsep\"></span>\n      <button class=\"ibtn tool on\" id=\"tList\" title=\"Ẩn / hiện bảng Phiên bản bên trái ( [ )\">Phiên bản <kbd>[</kbd></button>\n      <label class=\"tmchk\" id=\"tmLbl\" title=\"Chế độ cảm ứng (iPad / điện thoại)\"><input type=\"checkbox\" id=\"tmChk\" aria-label=\"Chế độ cảm ứng\"><svg viewBox=\"0 0 24 24\"><path d=\"M9 11V5a1.6 1.6 0 013.2 0v5l3.3.7a2 2 0 011.5 2.3L16.4 19a2 2 0 01-2 1.6H11a2 2 0 01-1.6-.8L6 14.6a1.5 1.5 0 012.2-1.9z\"/></svg></label>\n      <button class=\"ibtn tool on\" id=\"tSide\" title=\"Ẩn / hiện bảng Khớp đang chọn + Điều chỉnh bên phải ( ] )\">Bảng chỉnh <kbd>]</kbd></button>\n    </div>\n  </header>\n\n  <div class=\"main\">\n    <nav class=\"pane list\" aria-label=\"Danh sách pose\">\n      <h2>Phiên bản <span id=\"poseCount\"></span></h2>\n      <div id=\"poses\"></div>\n      <details class=\"help\"><summary title=\"Phím tắt và cách điều khiển\" aria-label=\"Phím tắt\"><svg viewBox=\"0 0 24 24\"><circle cx=\"12\" cy=\"12\" r=\"9\"/><path d=\"M9.5 9.5a2.5 2.5 0 114 2c-1 .7-1.5 1.2-1.5 2.5M12 17h.01\"/></svg></summary><p>Điều khiển như Maya: <b>Alt + chuột trái</b> xoay camera, <b>Alt + chuột giữa</b> dời, <b>Alt + chuột phải</b> hoặc cuộn để zoom. <b>F</b> zoom vào khớp đang chọn, <b>A</b> xem cả người.<br><br>\nBấm điểm khớp để chọn (các điểm khác tạm ẩn), bấm ra chỗ trống hoặc Esc để bỏ chọn. <b>Q</b> chọn · <b>W</b> dời · <b>E</b> xoay · <b>↑ ↓</b> sang khớp cha / con · <b>+ −</b> cỡ gizmo.<br><br>\nChannel Box: kéo ngang tên kênh để chỉnh (Shift chậm, Ctrl nhanh) hoặc gõ số rồi Enter. <b>, .</b> key trước / sau, <b>← →</b> frame.</p></details>\n    </nav>\n\n    <section class=\"viewer\" id=\"viewer\" aria-label=\"Viewport 3D\"><div id=\"p_tmBar\" role=\"toolbar\" aria-label=\"Thao tác cảm ứng\"><button data-m=\"orbit\" class=\"on\" title=\"Xoay / kéo / zoom camera (1 ngón xoay, 2 ngón zoom + kéo)\" aria-label=\"Xoay camera\"><svg viewBox=\"0 0 24 24\"><path d=\"M12 3a9 9 0 109 9\"/><path d=\"M12 3l3 3M12 3L9 6\"/><circle cx=\"12\" cy=\"12\" r=\"2.4\"/></svg></button><button data-m=\"sel\" title=\"Chạm để chọn, kéo gizmo để chỉnh\" aria-label=\"Chọn\"><svg viewBox=\"0 0 24 24\"><path d=\"M6 4l11 6-5 1.5L10 17z\"/></svg></button><button data-m=\"box\" title=\"Kéo khung để chọn nhiều điểm\" aria-label=\"Chọn khung\"><svg viewBox=\"0 0 24 24\"><path d=\"M5 8V5h3M16 5h3v3M19 16v3h-3M8 19H5v-3\" /><path d=\"M10 12h4\"/></svg></button><button data-add=\"1\" title=\"Thêm vào vùng chọn (như giữ Shift)\" aria-label=\"Thêm vào chọn\"><svg viewBox=\"0 0 24 24\"><path d=\"M12 5v14M5 12h14\"/></svg></button></div>\n      \n      <canvas id=\"drawCv\"></canvas>\n      <div class=\"drawbar\" role=\"toolbar\" aria-label=\"Vẽ ghi chú\"><button id=\"dvOn\" title=\"Vẽ lên khung 3D; khi lưu ghi chú ảnh khung này (kèm nét vẽ) được lưu cùng\">✎ Vẽ</button><span id=\"dvTools\" hidden style=\"display:flex;gap:4px;align-items:center\"><button class=\"sw on\" data-c=\"#ff4d4d\" style=\"background:#ff4d4d\" aria-label=\"Đỏ\"></button><button class=\"sw\" data-c=\"#ffd23f\" style=\"background:#ffd23f\" aria-label=\"Vàng\"></button><button class=\"sw\" data-c=\"#3ddc97\" style=\"background:#3ddc97\" aria-label=\"Xanh lá\"></button><button id=\"dvUndo\">Hoàn tác nét</button><button id=\"dvClear\">Xóa nét</button></span></div>\n      <div class=\"hud\">\n        <div class=\"tag\" id=\"camTag\">Camera: <b>Right (ingame)</b></div>\n        <div class=\"tag\" id=\"selTag\" hidden></div>\n        <div class=\"tag\" id=\"trailTag\" hidden></div>\n      </div>\n      <div class=\"cams\" role=\"group\" aria-label=\"Camera\">\n        <button data-cam=\"right\" class=\"on\" title=\"Camera ingame (1)\">Right</button>\n        <button data-cam=\"left\" title=\"5\">Left</button>\n        <button data-cam=\"front\" title=\"2\">Front</button>\n        <button data-cam=\"back\" title=\"6\">Back</button>\n        <button data-cam=\"top\" title=\"3\">Top</button>\n        <button data-cam=\"bottom\" title=\"7\">Bottom</button>\n        <button data-cam=\"persp\" title=\"4\">3/4</button>\n      </div>\n      <div class=\"refbox\" id=\"refbox\" hidden><div class=\"rbar\" id=\"rbar\" role=\"group\" aria-label=\"Góc ref\"></div><div class=\"rpair\"><div class=\"rimg\" id=\"rimg\" title=\"Bấm để đổi cỡ ảnh\"></div><canvas class=\"ranim\" id=\"ranim\" hidden title=\"Model qua đúng camera ref\"></canvas></div><div class=\"rcap\" id=\"rcap\"></div></div>\n      <div class=\"loading\" id=\"loading\">Đang tải model…</div>\n    </section>\n\n    <aside class=\"side\">\n      <div>\n        <h2>Khớp đang chọn</h2>\n        <div class=\"sel\">\n          <div class=\"name\" id=\"selName\">Chưa chọn khớp</div>\n          <div class=\"hint\" id=\"selHint\">Bấm một khớp để chỉnh.</div>\n          <div class=\"cb\" id=\"cb\" hidden></div>\n          <div class=\"row\">\n            <button class=\"ibtn btn\" id=\"resetJoint\" disabled>Trả khớp này về gốc</button>\n          </div>\n          <div class=\"changes\" id=\"changes\"></div>\n        </div>\n        <details class=\"phys\" id=\"physBox\" hidden open>\n          <summary>Vật lý <span id=\"physSum\"></span></summary>\n          <div class=\"pbody\">\n            <div class=\"row\">\n              <button class=\"ibtn btn\" id=\"physOn\" title=\"Bật / tắt lớp vật lý (so trước và sau). Bóng pose gốc luôn là pose của key, không vật lý\">Vật lý: tắt</button>\n              <button class=\"ibtn btn\" id=\"physChar\" title=\"Dùng bộ lò xo đã duyệt cho nhân vật này (Gaygor: tay phải, chùy, khuỷu trái; vai trái là vùng chắn)\">Mức của nhân vật</button>\n              <button class=\"ibtn btn\" id=\"physBake\" title=\"Ghi mọi frame (có vật lý) thành key rồi tắt vật lý, để sửa tay tiếp. Ctrl+Z để lấy lại key cũ\">Bake thành key</button>\n            </div>\n            <h3 title=\"Giống AutoPhysics của Cascadeur: mỗi mục bật / tắt và mức 0-100, chồng lên key (không sửa key)\">AutoPhysics</h3>\n            <div id=\"apRows\"></div>\n            <div class=\"pinfo\" id=\"apInfo\"></div>\n            <h3>Lò xo từng phần</h3>\n            <div class=\"pparts\" id=\"physParts\"></div>\n            <div class=\"row\">\n              <button class=\"ibtn btn\" id=\"physAdd\" title=\"Thêm khớp đang chọn: khuỷu/gối = bản lề, vũ khí = vật cầm tay, còn lại = khớp mềm\">+ Thêm khớp đang chọn</button>\n              <button class=\"ibtn btn\" id=\"physColAdd\" title=\"Khớp đang chọn thành vùng chắn: vật cầm tay không lại gần khớp này hơn lúc nghỉ (đệm mềm 2,5 cm)\">+ Vùng chắn</button>\n            </div>\n            <div class=\"pcols\" id=\"physCols\"></div>\n            <label class=\"pinfo\">Trả về đúng pose key ở <input type=\"number\" id=\"physEnd\" min=\"0\" max=\"30\" step=\"1\"> frame cuối (clip lặp: tự nối vòng)</label>\n            <canvas id=\"physGraph\" width=\"580\" height=\"192\" aria-label=\"Tốc độ xoay theo frame của phần đang chọn\"></canvas>\n            <div class=\"pinfo\" id=\"physInfo\"></div>\n            <h3>Tác động</h3>\n            <div class=\"row\">\n              <button class=\"ibtn btn\" id=\"impAdd\" title=\"Bấm rồi bấm lên người: đặt một cú tác động (trúng đòn, trúng đạn, bị tông) ở frame đang xem\">+ Tác động</button>\n              <button class=\"ibtn btn\" id=\"impAim\" title=\"Bấm hoặc kéo trên màn hình ở chỗ lực đến: mũi tên chỉ vào điểm trúng\">Kéo hướng lực</button>\n              <button class=\"ibtn btn\" id=\"impStep\" title=\"Khi bị đẩy ra ngoài chân quá 5 cm: tự bước (tối đa 3 bước). Tắt: chỉ báo cần bước và vẽ vòng đỏ ở chỗ đặt chân\">Tự bước: bật</button>\n            </div>\n            <div class=\"pparts\" id=\"impList\"></div>\n            <div class=\"pinfo\" id=\"impInfo\"></div>\n            <h3>Ragdoll</h3>\n            <div id=\"ragBox\">\n              <div class=\"row\">\n                <button class=\"ibtn btn\" id=\"ragOn\" title=\"Từ frame chọn, cơ thể thành các khối nối khớp (giới hạn khớp của nhân vật), mất sức theo đường Sức rồi đổ, đập sàn và lắng. Lực ở frame đó trở đi đẩy ragdoll\">Ragdoll: tắt</button>\n                <label class=\"pinfo\">từ F <input type=\"number\" id=\"ragFrom\" min=\"2\" step=\"1\" style=\"width:58px\"></label>\n                <button class=\"ibtn btn\" id=\"ragRelease\" title=\"Chùy rời tay từ frame đang xem: rơi, nảy, nằm riêng\">Buông chùy ở F đang xem</button>\n              </div>\n              <div class=\"row\">\n                <button class=\"ibtn btn\" id=\"ragGoal\" title=\"Về đích: sau khi chạm sàn, cơ kéo tay chân về pose key cuối; frame cuối trùng đúng key cuối (phần lệch còn lại trộn dần trong ~10 frame cuối)\">Về đích: tắt</button>\n                <label class=\"psl\" id=\"ragMatchBox\" style=\"flex:1 1 100%\" title=\"Frame cuối giống key cuối bao nhiêu: 0 % = để nguyên vật lý, 100 % = đúng key cuối\"><span>Khớp pose cuối</span><input type=\"range\" id=\"ragMatch\" min=\"0\" max=\"1\" step=\"0.05\"><output id=\"ragMatchOut\"></output></label>\n                <button class=\"ibtn btn\" id=\"ragGoalRoot\" title=\"Chỉ dáng: người nằm ở đâu là do vật lý (và tác động), chỉ dáng tay chân / thân / đầu về theo key cuối. Dáng + vị trí: cả hông cũng kéo về đúng chỗ của key cuối\">Đích: chỉ dáng</button>\n                <button class=\"ibtn btn\" id=\"ragGoalFind\" title=\"Chạy ragdoll nhiều lần với cú đẩy ban đầu khác nhau (hướng, độ mạnh, xoay) để người nằm đúng chỗ và đúng hướng của key cuối (khoảng 1-2 phút)\">Tìm cú đổ</button>\n              </div>\n              <canvas id=\"ragGraph\" width=\"580\" height=\"150\" aria-label=\"Đường Sức của ragdoll theo frame: kéo điểm, bấm chỗ trống để thêm, bấm đúp để xoá\"></canvas>\n              <div id=\"ragGroups\" title=\"Sức riêng từng phần (nhân với đường Sức). Sức chân giữ thăng bằng: còn sức và chân chạm đất thì hông được kéo về pose key\"></div>\n              <div class=\"row\"><button class=\"ibtn btn\" id=\"ragLim\" title=\"Vẽ vùng cho phép của khớp đang chọn (gập x dang) trên model\">Hiện giới hạn khớp</button></div>\n              <div class=\"pinfo\" id=\"ragLimTxt\"></div>\n              <div class=\"pinfo\" id=\"ragInfo\"></div>\n            </div>\n            <h3>Va chạm thân</h3>\n            <div class=\"row\">\n              <button class=\"ibtn btn\" id=\"bodyViz\" title=\"Hiện hình va chạm trên model: lõi con nhộng (xanh), khúc đang xuyên (đỏ), điểm bề mặt của khúc xuyên\">Hiện vùng va chạm</button>\n              <button class=\"ibtn btn\" id=\"bodyRebuild\" title=\"Dựng lại hình va chạm từ lưới (sau khi đổi bán kính)\">Dựng lại</button>\n            </div>\n            <label class=\"psl\" id=\"bodyRBox\" hidden><span id=\"bodyRName\">Bán kính</span><input type=\"range\" id=\"bodyR\" min=\"2\" max=\"40\" step=\"1\"><output id=\"bodyROut\"></output></label>\n            <div class=\"pissues\" id=\"bodyIssues\"></div>\n            <div class=\"pinfo\" id=\"bodyInfo\"></div>\n            <h3>Cân bằng</h3>\n            <div class=\"row\">\n              <button class=\"ibtn btn\" id=\"balViz\" title=\"Trên sàn: vùng đỡ (chân + vũ khí chạm đất), chấm trọng tâm, mũi tên tới điểm cần đặt chân để không ngã. Xanh = vững, vàng = đang bước kịp, đỏ = lỗi\">Hiện cân bằng</button>\n              <button class=\"ibtn btn\" id=\"balFix\" title=\"Frame đang xem: dời hông ngang (hai bàn chân khóa trên sàn, vũ khí theo người) tới khi trọng tâm vào vùng đỡ, rồi đặt key\">Đưa trọng tâm vào chân</button>\n            </div>\n            <label class=\"psl\"><span>Vũ khí nặng</span><input type=\"range\" id=\"balProp\" min=\"0\" max=\"60\" step=\"1\"><output id=\"balPropOut\"></output></label>\n            <div class=\"pissues\" id=\"balIssues\"></div>\n            <div class=\"pinfo\" id=\"balInfo\"></div>\n            <div class=\"row\"><button class=\"ibtn btn\" id=\"fallGhost\" title=\"Trong một cú ngã: bóng mờ là cả người ở frame bắt đầu đổ, đổ cứng theo vật lý (cùng góc và đà ban đầu) để so với anim\">Bóng đổ theo vật lý</button></div>\n            <canvas id=\"fallGraph\" width=\"580\" height=\"160\" aria-label=\"Chiều cao trọng tâm trong cú ngã: anim và vật lý\" hidden></canvas>\n          </div>\n        </details>\n      </div>\n      <div class=\"pane\" id=\"adjList\" aria-live=\"polite\">\n        <h2>Điều chỉnh đã gửi <span id=\"adjCount\"></span></h2>\n        <p class=\"empty\" id=\"adjEmpty\">Chưa có điều chỉnh.</p>\n        <div id=\"adjs\"></div>\n      </div>\n      <div class=\"compose\">\n        \n        <textarea id=\"text\" aria-label=\"Ghi chú cho AI\" placeholder=\"Ghi chú cho AI: vì sao chỉnh, chỗ nào\"></textarea>\n        <div class=\"row\">\n          <button class=\"ibtn btn primary\" id=\"save\" disabled>Lưu điều chỉnh</button>\n          <button class=\"ibtn btn\" id=\"aiSend\" disabled>Gửi cho AI</button>\n        </div>\n        <div class=\"round\" id=\"round\" data-s=\"none\"><span id=\"roundTxt\">Vòng review đang mở.</span><small id=\"roundSub\"></small></div>\n        <div class=\"aiself\" id=\"aiself\">\n          <label title=\"Sau mỗi lần Gửi cho AI: khi AI ra version mới, trang tự chụp anim ở 3 góc và nhờ AI đánh giá, rồi gửi kết quả cho AI sửa tiếp, đủ số vòng thì dừng chờ bạn duyệt\"><input type=\"checkbox\" id=\"asOn\"> AI tự xem lại</label>\n          <label>Số vòng <select id=\"asRounds\"><option>1</option><option selected>2</option><option>3</option><option>4</option><option>5</option></select></label>\n          <button class=\"tmgB\" id=\"asRun\" title=\"Nhờ AI xem và đánh giá version đang mở ngay bây giờ (kết quả thành một ghi chú)\">Xem ngay</button>\n        </div>\n        <div class=\"asStatus\" id=\"asStatus\" role=\"status\"></div>\n        <div class=\"status\" id=\"p_status\" role=\"status\"></div>\n      </div>\n    </aside>\n  </div>\n</div>\n\n<footer class=\"timeline\" aria-label=\"Timeline\">\n  <div class=\"tmg\" id=\"tmgPanel\" hidden>\n    <div class=\"tmgh\">\n      <b>⏱ Timing</b>\n      <span class=\"tmgInfo\" id=\"tmgInfo\"></span>\n      <label class=\"tmgOpt\" title=\"Bật: kéo một key chính thì mọi key chính phía sau dịch theo, độ dài các pha sau giữ nguyên (pha cuối bị nén vì key cuối cố định). Tắt: chỉ dời key chính đó, hai pha kề nó co giãn.\"><input type=\"checkbox\" id=\"tmgRipple\"> Dịch cả các pha sau</label>\n      <span class=\"tmgHelp\" title=\"Kéo kim cương lớn (key chính của từng giai đoạn). Các chấm nhỏ là key chuyển tiếp, tự co giãn theo tỉ lệ, pose giữ nguyên. Key đầu và cuối cố định nên clip vẫn dài như cũ. Ctrl+Z hoàn tác.\">ⓘ</span>\n      <button class=\"tmgB\" id=\"tmgSplit\" disabled title=\"Biến key chuyển tiếp ở frame đang đứng thành key chính: tách pha đang chứa nó làm hai (cũng có thể nhấp đúp vào chấm nhỏ)\">+ Tách pha</button>\n      <button class=\"tmgB\" id=\"tmgMerge\" disabled title=\"Key chính ở frame đang đứng trở lại thành key chuyển tiếp: pha bắt đầu từ nó gộp vào pha trước\">− Gộp pha</button>\n      <span class=\"tmgSp\"></span>\n      <span class=\"tmgDirty\" id=\"tmgDirty\" hidden>● chưa gửi</span>\n      <button class=\"tmgB\" id=\"tmgReset\" disabled title=\"Đưa timing về như lần gửi trước (hoặc như lúc AI dựng version này)\">↺ Về lần gửi trước</button>\n      <button class=\"tmgB primary\" id=\"tmgSend\" disabled title=\"Lưu timing vừa kéo thành một góp ý (chữ trong khung ghi chú được kèm vào), rồi bấm Gửi cho AI như các góp ý khác\">Gửi timing như góp ý</button>\n    </div>\n    <div class=\"tmgt\" id=\"tmgTrack\"></div>\n  </div>\n  <div class=\"lanes\" aria-label=\"Chân chạm đất\">\n    <div class=\"lane\" data-s=\"L\" id=\"laneL\" title=\"Chân trái chạm đất: kéo trên dải xanh để tô / xoá frame. Trên các frame này bàn chân bám sàn (IK)\"></div>\n    <div class=\"lane\" data-s=\"R\" id=\"laneR\" title=\"Chân phải chạm đất: kéo trên dải tím để tô / xoá frame\"></div>\n    <div class=\"lane\" data-s=\"Bl\" id=\"laneBl\" title=\"Cân bằng: cam đậm = lỗi (nghiêng quá, đà quá mạnh, bước hụt, lơ lửng), cam nhạt = trọng tâm ra ngoài chân nhưng bước kịp (bấm để tới frame đó)\"></div>\n    <div class=\"lane\" data-s=\"X\" id=\"laneX\" title=\"Xuyên thân: frame tô đỏ có khúc lẹm vào nhau sâu hơn lúc nghỉ quá 2 cm (bấm để tới frame đó)\"></div>\n    <div class=\"lane\" data-s=\"S\" id=\"laneS\" title=\"Sức của ragdoll: cam càng đậm càng nhiều sức (bấm để tới frame đó)\"></div>\n    <div class=\"lane\" data-s=\"I\" id=\"laneI\" title=\"Tác động: cam đậm = frame có lực, cam nhạt = đang tự bước (bấm để tới frame đó)\"></div>\n    <div class=\"lane\" data-s=\"P\" id=\"laneP\" title=\"Ghim pose key: trên các frame tô vàng, vật lý tắt (giữ đúng pose key, vd frame trúng đòn), chuyển êm trong 3 frame\"></div>\n  </div>\n  <div class=\"strip\" id=\"strip\" role=\"slider\" tabindex=\"0\" aria-label=\"Frame\" aria-valuemin=\"1\"></div>\n  <div class=\"transport\">\n    <button class=\"ibtn btn\" id=\"prevKey\" title=\"Key trước (Shift+←)\">◀◆</button>\n    <button class=\"ibtn btn\" id=\"prevF\" title=\"Frame trước (←)\">◀</button>\n    <button class=\"ibtn btn primary\" id=\"play\" title=\"Phát / dừng (Space)\">Phát</button>\n    <button class=\"ibtn btn\" id=\"nextF\" title=\"Frame sau (→)\">▶</button>\n    <button class=\"ibtn btn\" id=\"nextKey\" title=\"Key sau (Shift+→)\">◆▶</button>\n    <span class=\"fcount\" id=\"fcount\">F<b>1</b> / 1</span>\n    <span class=\"vsep\"></span>\n    <button class=\"ibtn btn\" id=\"copyKey\" title=\"Copy pose của frame này: các khớp đang chọn (chọn nhiều bằng Shift hoặc quét), hoặc cả người khi chưa chọn (Ctrl+C). Shift = kèm các khớp con\">Copy key</button>\n    <button class=\"ibtn btn\" id=\"pasteKey\" disabled title=\"Paste vào frame này (Ctrl+V). Shift = paste từ frame này đến trước key kế tiếp\">Paste</button>\n    <button class=\"ibtn btn\" id=\"pasteHold\" disabled title=\"Paste từ frame này đến trước key kế tiếp (Ctrl+Shift+V)\">Paste đến key kế</button>\n    <span class=\"kgrp\" id=\"kTools\" hidden>\n      <span class=\"vsep\"></span>\n      <button class=\"ibtn btn primary\" id=\"kSet\" title=\"Đặt key ở frame này bằng pose đang thấy (S)\">◆ Key <kbd>S</kbd></button>\n      <button class=\"ibtn btn\" id=\"lanesBtn\" title=\"Hiện / ẩn các dải phân tích: chân trái và phải chạm đất, cân bằng, xuyên thân, ragdoll, tác động, ghim pose\">Dải phân tích</button>\n      <button class=\"ibtn btn\" id=\"tmgBtn\" title=\"Mở bảng Timing: kéo key để đổi nhịp các pha\">⏱ Timing</button>\n      <button class=\"ibtn btn\" id=\"kDel\" title=\"Xoá key ở frame này (Delete). Dời key: Shift + kéo key trên timeline (hoặc kéo bằng chuột giữa)\">Xoá key</button>\n      <button class=\"ibtn btn\" id=\"kAuto\" title=\"Bật: mỗi lần chỉnh xong một khớp là tự đặt key ở frame đó\">Auto key: bật</button>\n      <button class=\"ibtn btn\" id=\"kInterp\" title=\"Đổi giữa spline (mượt) và bậc thang (blocking: giữ pose tới key kế)\">Spline</button>\n      <button class=\"ibtn btn\" id=\"kLock\" title=\"Trên các frame chạm đất (dải xanh / tím), bàn chân đi thẳng giữa các vị trí ở key, không trượt, không lún\">Bám sàn: bật</button>\n      <button class=\"ibtn btn\" id=\"kFit\" title=\"Tự xoay hông, chân, thân, chùy và tay cho bóng nhân vật trùng bóng ref ở frame này (5 góc), rồi đặt key. Bấm lần nữa để dừng\">Khớp ref</button>\n      <button class=\"ibtn btn\" id=\"kFloor\" title=\"Mọi key: chân đang chống (dải chạm đất) đặt đúng lên sàn theo điểm thấp nhất của lưới bàn chân; chân đang nhấc không được xuyên sàn\">Chân lên sàn</button>\n      <button class=\"ibtn btn\" id=\"kAutoCt\" title=\"Tô dải chạm đất từ các key: bàn chân thấp (sát sàn) ở hai key liền nhau thì chạm đất suốt đoạn giữa\">Dò chạm đất</button>\n      <span class=\"vsep\"></span>\n    </span>\n    <button class=\"ibtn btn\" id=\"expFbx\" title=\"Xuất cả clip thành FBX (chỉ xương + animation, 30 fps) cho Unity. File tải về là .zip chứa .fbx\">Xuất FBX</button>\n    <span class=\"clipinfo\" id=\"clipInfo\"></span>\n    <span class=\"legend\"><span><i style=\"background:var(--joint)\"></i>key / đã lưu điều chỉnh</span><span><i style=\"background:#4db3ff\"></i>key mới của version này</span><span><i style=\"background:var(--edit)\"></i>đang chỉnh, chưa lưu</span><span class=\"kgrp\" id=\"kLegend\" hidden><span><i style=\"background:var(--laneL)\"></i>trái chạm đất</span><span><i style=\"background:var(--laneR)\"></i>phải chạm đất</span><span><i style=\"background:var(--joint)\"></i>ghim pose (vật lý tắt)</span><span><i style=\"background:var(--edit)\"></i>xuyên thân</span><span><i style=\"background:#ff9f43\"></i>cân bằng</span></span></span>\n  </div>\n</footer>";
ST.POSE_RENAME = {"tmBar": "p_tmBar", "status": "p_status"};

// Kho dữ liệu trên máy cho các Lab khi không có db của claude.ai: nói chuyện với Home server (tools/home/store.py), ghi file thật vào work/store/<ns>/.
// Cùng giao diện với db của artifact (doc/collection, get/set/update/delete/add/onSnapshot) nên mã Lab không phải đổi.
// Kèm nút "Lưu trữ" (xuất / mở file .json). Nguồn: tools/home/localdb.js, nhúng bằng work/patch_localdb.py.
ST.poseDB = function (NS) {
  const API = location.origin + "/api/store";
  const slug = s => String(s || "page").toLowerCase().replace(/[^a-z0-9]+/g, "_").replace(/^_|_$/g, "").slice(0, 80) || "page";

  const enc = encodeURIComponent;
  async function call(method, path, body) {
    const r = await fetch(API + "/" + path, { method, headers: body !== undefined ? { "Content-Type": "application/json" } : {}, body: body !== undefined ? JSON.stringify(body) : undefined });
    if (!r.ok) throw new Error("store " + r.status);
    return r.json();
  }
  const snapOf = (id, data) => ({ id, exists: data !== null && data !== undefined, data: () => data });
  const watchers = {};   // col → { subs:Set, last:string, timer }
  async function fetchCol(col) { const r = await call("GET", enc(NS) + "/" + enc(col)); return r.docs; }
  const colSnap = docs => { const d = docs.map(x => snapOf(x.id, x.data)); return { docs: d, size: d.length, empty: !d.length, forEach: f => d.forEach(f) }; };
  async function tick(col) {
    const w = watchers[col]; if (!w || !w.subs.size) return;
    try {
      const docs = await fetchCol(col), sig = JSON.stringify(docs);
      if (sig !== w.last) { w.last = sig; const sn = colSnap(docs); w.subs.forEach(f => { try { f(sn); } catch (e) { console.error(e); } }); }
    } catch (e) {}
  }
  const poke = col => { if (watchers[col]) tick(col); };
  function docRef(col, id) {
    const base = () => enc(NS) + "/" + enc(col) + "/" + id.split("/").map(enc).join("/");
    return {
      id, path: col + "/" + id,
      get: async () => { const r = await call("GET", base()); return snapOf(id, r.exists ? r.data : null); },
      set: async d => { await call("PUT", base(), d); poke(col); },
      update: async d => { await call("PATCH", base(), d); poke(col); },
      delete: async () => { await call("DELETE", base()); poke(col); },
    };
  }
  function colRef(col) {
    return {
      id: col, doc: id => docRef(col, id),
      get: async () => colSnap(await fetchCol(col)),
      add: async d => { const r = await call("POST", enc(NS) + "/" + enc(col), d); poke(col); return docRef(col, r.id); },
      onSnapshot: cb => {
        const w = watchers[col] || (watchers[col] = { subs: new Set(), last: null, timer: 0 });
        w.subs.add(cb); w.last = null; tick(col);
        if (!w.timer) w.timer = setInterval(() => tick(col), 2000);
        return () => { w.subs.delete(cb); if (!w.subs.size) { clearInterval(w.timer); w.timer = 0; } };
      },
    };
  }
  const db = { isLocal: true, ns: NS, doc: path => { const [c, ...r] = path.split("/"); return docRef(c, r.join("/")); }, collection: colRef };
  db.ping = async function () {
    try {
      const ctl = new AbortController(), t = setTimeout(() => ctl.abort(), 1200);
      const r = await fetch(API + "/_ping", { signal: ctl.signal }); clearTimeout(t);
      if (!r.ok) return null; await r.json(); return db;
    } catch (e) { return null; }
  };

  return db;
};

ST.poseEngine = function (POSES_IN, host) {
const CAM = host.cam;
// camera Orthographic ở các góc thẳng (user 2026-10-29): cỡ 1 pixel màn hình (m) tại điểm cách camera d, đổi tỉ lệ khung, kéo xa / lại gần
const pxAt = d => { const c = CAM(), h = Math.max(1, canvas.clientHeight); return c.isOrthographicCamera ? (c.top - c.bottom) / c.zoom / h : 2 * Math.tan(THREE.MathUtils.degToRad(c.fov) / 2) * d / h; };
const camAspect = a => { const c = CAM(); if (c.isOrthographicCamera) { c.left = -a; c.right = a; c.top = 1; c.bottom = -1; } else c.aspect = a; c.updateProjectionMatrix(); };
const camDolly = k => { const c = CAM(), t = orbit.target; if (c.isOrthographicCamera) { c.zoom /= k; c.updateProjectionMatrix(); } else { c.position.sub(t).multiplyScalar(k).add(t); c.lookAt(t); } };
// ---------------------------------------------------------------- data
// One entry per VERSION, newest first, like CLIPS on the playblast review page. This master keeps every clip;
// work/pose_lab/split_pages.py writes one page per animation (own artifact + own db), so map2 and map06 never mix.
// glb = the animation of that version (work/blender/export_pose_glb.py, first key = F1; old models are kept so every
// version stays viewable); frames = clip length, keys = key-pose frames shown on the timeline; note = what changed.
// mode "keys" = the animation is made ON the page: keys live in db "keys" (seeded from `keys` sampled out of the glb,
// or copied from version `seedFrom`), in-betweens are splined here, FBX is exported from that. loop = last frame == F1.
// contacts = default planted frames per foot ("15-45", cycle frames); ref = sprite sheets of the reference video
// (work/pose_lab/make_ref_sprites.py), offset = ref frame - anim frame.
const POSES = POSES_IN;
const NAMES = {
  Root_M: "Hông (Root)", Spine1_M: "Lưng dưới", Chest_M: "Ngực", Neck_M: "Cổ", Head_M: "Đầu",
  Scapula_L: "Bả vai trái", Shoulder_L: "Vai trái", Elbow_L: "Khuỷu trái", Wrist_L: "Cổ tay trái",
  Scapula_R: "Bả vai phải", Shoulder_R: "Vai phải", Elbow_R: "Khuỷu phải", Wrist_R: "Cổ tay phải",
  Hip_L: "Đùi trái", Knee_L: "Gối trái", Ankle_L: "Cổ chân trái", Hip_R: "Đùi phải", Knee_R: "Gối phải", Ankle_R: "Cổ chân phải",
  slingshot_0: "Dao",
};
const NAMES0 = { ...NAMES };
let JOINTS = Object.keys(NAMES);
const FINGER_VI = { Thumb: "ngón cái", Index: "ngón trỏ", Middle: "ngón giữa", Ring: "ngón áp út", Pinky: "ngón út" };
function jointLabel(n) {    // nhãn tiếng Việt cho khớp thêm từ rig: "Ngón trỏ 2 phải", "Mũi chân trái", "joint1 phải"
  const side = n.endsWith("_R") ? " phải" : n.endsWith("_L") ? " trái" : "", m = n.match(/^(\w+?)Finger(\d)_/);
  if (m) return FINGER_VI[m[1]][0].toUpperCase() + FINGER_VI[m[1]].slice(1) + " " + m[2] + side;
  if (/^Toes_/.test(n)) return "Mũi chân" + side;
  if (/^Scarf\d/.test(n)) return "Khăn " + n.match(/^Scarf(\d+)/)[1] + side;
  if (n === "Weapon") return "Vũ khí";
  return n.replace(/_[LR]$/, "") + side;
}
function useNames(p) {      // per-clip labels / extra joints (SDR06: gun, drum, fingers)
  for (const k of Object.keys(NAMES)) delete NAMES[k];
  Object.assign(NAMES, NAMES0, p.names || {}); JOINTS = Object.keys(NAMES);
}
const LEGS = { L: ["Hip_L", "Knee_L", "Ankle_L"], R: ["Hip_R", "Knee_R", "Ankle_R"] };
// Arm IK (user 2026-10-22 "Sao tôi trong dời dk mà chỉ xoay"): W on a wrist drags the hand, shoulder + elbow bend
// like an IK handle, the hand keeps its world orientation. Saved as rotations, so Blender applies it unchanged.
const ARMS = { L: ["Shoulder_L", "Elbow_L", "Wrist_L"], R: ["Shoulder_R", "Elbow_R", "Wrist_R"] };
const MOVABLE = new Set(["Root_M", "Ankle_L", "Ankle_R", "Wrist_L", "Wrist_R", "slingshot_0"]);   // khớp có cách dời riêng (hông, IK chân / tay, súng)
const RIGSET = () => window.__rigSetup || null;   // cài đặt bước 6 Vật lý của Rig (Studio), không có thì như cũ
const canMove = n => !!B[n] && !(RIGSET() && RIGSET().joints && RIGSET().joints[n] && RIGSET().joints[n].move === false);   // mọi khớp dời được (W), user 2026-10-27 "các khớp không được di dời"; khớp khác dời thẳng theo cha
const isWrist = n => !!n && n.startsWith("Wrist_");
// Gun (user 2026-10-22 "Tôi muốn chỉnh vị trí của súng"): slingshot_0 moves (W) and turns (E) in world space; with
// "Tay phải bám súng" on, the right hand keeps its grip (arm IK). Blender: pose_lab_apply.py turns it into CTRL_knife keys.
const GUN = "slingshot_0";
let gunFollow = true, gunRel = null;
const wmat4 = o => new THREE.Matrix4().compose(wp(o), wq(o), new V3(1, 1, 1));
function gunGrab() {        // right wrist in gun space, taken before a gun change
  gunRel = gunFollow && B[GUN] && B.Wrist_R ? wmat4(B[GUN]).invert().multiply(wmat4(B.Wrist_R)) : null;
}
function gunFollowHand() {
  if (!gunRel) return;
  const m = wmat4(B[GUN]).multiply(gunRel), p = new V3(), q = new Q(); m.decompose(p, q, new V3());
  handQ.R = q; solveArm("R", p);
}

const $ = id => document.getElementById(id);
const V3 = THREE.Vector3, Q = THREE.Quaternion;
const css = n => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
const TM = { on: false, mode: "orbit", add: false };   // touch mode state (wired at the end of the script)

// ---------------------------------------------------------------- three.js scene
const canvas = host.canvas, viewer = host.viewer, renderer = host.renderer, orbit = host.orbit, gizmo = host.gizmo;
const scene = new THREE.Scene(), overlay = new THREE.Scene(); host.scenes(scene, overlay);
scene.add(new THREE.HemisphereLight(0xffffff, 0x404650, 1.0));
const sun = new THREE.DirectionalLight(0xffffff, 0.9); sun.position.set(-3, 5, 4); scene.add(sun);
const grid = new THREE.GridHelper(4, 16, 0x4a515c, 0x30353d); scene.add(grid);
gizmo.setSize(0.85); gizmo.setSpace("local");
const footHandle = { L: new THREE.Object3D(), R: new THREE.Object3D() };
const handHandle = { L: new THREE.Object3D(), R: new THREE.Object3D() };
scene.add(footHandle.L, footHandle.R, handHandle.L, handHandle.R);
let handQ = {};

let model = null, ghost = null, B = {}, base = {}, edited = new Set(), sel = null, mode = "rotate";
let footT = {}, footQ = {}, lockFeet = true, markers = {}, undoStack = [];
let frame = 1, drafts = {}, mixers = [], playing = false, playT0 = 0, playF0 = 1, cache = {}, gB = {};
// Joints as a stick figure (user 2026-10-22 "điểm khớp chồng lên nhau rối mắt, đổi thành dạng que"): a small dot per
// joint + a thin stick to its parent joint. Opacity 20 % by default (JOINT_BASE), fading with CAM() distance (near = clearest),
// 100 % when the mouse comes close or the joint is selected. Several joints can be selected (Shift, marquee drag).
// sizes in screen pixels (user 2026-10-22 "Kích thước khớp to quá"): dot radius DOT_PX, stick radius STICK_PX
const DOT_PX = 3.5, STICK_PX = 0.8, JOINT_BASE = 0.2;   // độ đậm khớp khi chuột chưa lại gần (trước 0.5); rê tới / chọn = 100 %
const markerGeo = new THREE.SphereGeometry(1, 12, 8);
const stickGeo = new THREE.CylinderGeometry(1, 1, 1, 6, 1); stickGeo.translate(0, 0.5, 0);
const COL = { joint: new THREE.Color(css("--joint")), edit: new THREE.Color(css("--edit")), sel: new THREE.Color(css("--accent")), hot: new THREE.Color(0xffffff) };
const jointMat = () => new THREE.MeshBasicMaterial({ color: COL.joint.clone(), depthTest: false, transparent: true, opacity: .5 });
let sticks = {}, selSet = new Set(), hoverXY = null, multiQ0 = null, hotEl = null, hotN = null;

const CAMS = {   // glTF world: Y up, character faces +Z, its right side is -X
  right: { pos: [-6.5, 1.0, 0], tgt: [0, 0.9, 0], label: "Right (ingame)" },
  front: { pos: [0, 1.0, 6.5], tgt: [0, 0.9, 0], label: "Front" },
  top: { pos: [0, 7.5, 0.001], tgt: [0, 0.5, 0], label: "Top" },
  left: { pos: [6.5, 1.0, 0], tgt: [0, 0.9, 0], label: "Left" },
  back: { pos: [0, 1.0, -6.5], tgt: [0, 0.9, 0], label: "Back" },
  bottom: { pos: [0, -7.5, 0.001], tgt: [0, 0.5, 0], label: "Bottom" },
  persp: { pos: [-4.2, 2.2, 4.2], tgt: [0, 0.9, 0], label: "3/4" },
};
// camFit scales the CAM() presets to the character (CAMS were set for a ~1.75 m soldier; Gaygor is bigger), from the
// highest joint at load
let curCam = "right", camFit = 1;
function setCam(k) {
  const c = CAMS[k]; curCam = k; if (host.camName) host.camName(k); if (typeof renderRef === "function") renderRef();
  const t = new V3(...c.tgt).multiplyScalar(camFit);
  if (host.setOrtho) host.setOrtho(k !== "persp");   // Studio: góc thẳng = camera Orthographic, 3/4 = phối cảnh
  const cam = CAM(), off = new V3(...c.pos).sub(new V3(...c.tgt)).multiplyScalar(camFit);
  if (cam.isOrthographicCamera) { cam.zoom = 1 / (off.length() * Math.tan(THREE.MathUtils.degToRad(30) / 2)); cam.position.copy(t).addScaledVector(off.normalize(), Math.max(20, 8 * camFit)); cam.up.set(0, 1, 0); cam.lookAt(t); cam.updateProjectionMatrix(); }
  else cam.position.copy(off.add(t));
  orbit.target.copy(t); orbit.update();
  document.querySelectorAll(".cams button").forEach(b => b.classList.toggle("on", b.dataset.cam === k));
  $("camTag").innerHTML = "Camera: <b></b>"; $("camTag").querySelector("b").textContent = c.label;
}
document.querySelectorAll(".cams button").forEach(b => b.onclick = () => setCam(b.dataset.cam));
orbit.addEventListener("start", () => { document.querySelectorAll(".cams button").forEach(b => b.classList.remove("on")); if (curCam !== "persp" && CAM().isPerspectiveCamera) { curCam = "persp"; $("camTag").innerHTML = "Camera: <b>persp (tự do)</b>"; } if (host.camName) host.camName("free"); });

function resize() { host.resize(); }

// ---------------------------------------------------------------- pose helpers
const wq = o => o.getWorldQuaternion(new Q());
const wp = o => o.getWorldPosition(new V3());
function setWorldQuat(o, q) {
  const pq = wq(o.parent); o.quaternion.copy(pq.invert().multiply(q)); o.updateMatrixWorld(true);
}
function rotateWorld(o, q) { setWorldQuat(o, q.clone().multiply(wq(o))); }
function swing(o, from, to) {   // rotate bone o (about its head) so that world direction `from` becomes `to`
  const q = new Q().setFromUnitVectors(from.clone().normalize(), to.clone().normalize()); rotateWorld(o, q);
}
function solveLeg(s) { solve2(LEGS[s], footT[s], footQ[s]); }
function solveArm(s, tgt) { solve2(ARMS[s], tgt, handQ[s]); }
function solve2(chain, target, endQ) {   // two-bone IK, bend plane kept from the current middle joint
  const [h, k, a] = chain.map(n => B[n]);
  const hip = wp(h), knee = wp(k), ank = wp(a), tgt = target.clone();
  const la = knee.distanceTo(hip), lb = ank.distanceTo(knee);
  let d = tgt.clone().sub(hip); const dist = Math.min(Math.max(d.length(), 1e-4), la + lb - 1e-4); d.normalize();
  let pole = knee.clone().sub(hip); pole.sub(d.clone().multiplyScalar(pole.dot(d)));
  if (pole.lengthSq() < 1e-8) pole.set(0, 0, 1); pole.normalize();
  const cosA = Math.min(1, Math.max(-1, (la * la + dist * dist - lb * lb) / (2 * la * dist)));
  const kneeT = hip.clone().add(d.clone().multiplyScalar(la * cosA)).add(pole.multiplyScalar(la * Math.sqrt(1 - cosA * cosA)));
  swing(h, knee.clone().sub(hip), kneeT.clone().sub(hip));
  const knee2 = wp(k), ank2 = wp(a);
  swing(k, ank2.clone().sub(knee2), hip.clone().add(d.multiplyScalar(dist)).sub(knee2));
  setWorldQuat(a, endQ);
  chain.forEach(n => edited.add(n));
}
function captureFeet() { for (const s of ["L", "R"]) { footT[s] = wp(B[LEGS[s][2]]); footQ[s] = wq(B[LEGS[s][2]]); } }
function snapshot() {
  const o = {}; for (const n of Object.keys(B)) o[n] = [B[n].position.clone(), B[n].quaternion.clone()];
  return { bones: o, edited: new Set(edited), footT: { L: footT.L.clone(), R: footT.R.clone() }, footQ: { L: footQ.L.clone(), R: footQ.R.clone() },
           base, keys: keysMode() ? new Map(KEYS) : null };
}
function restore(sn) {
  for (const n of Object.keys(sn.bones)) { B[n].position.copy(sn.bones[n][0]); B[n].quaternion.copy(sn.bones[n][1]); }
  model.updateMatrixWorld(true); edited = new Set(sn.edited); footT = sn.footT; footQ = sn.footQ;
  if (sn.base) base = sn.base;
  if (sn.keys && keysMode()) {     // key changes are undone too (and written back to the db)
    for (const f of new Set([...KEYS.keys(), ...sn.keys.keys()])) if (KEYS.get(f) !== sn.keys.get(f)) dirtyKeys.add(f);
    KEYS = new Map(sn.keys); keysChanged();
  }
  attachGizmo(); refresh();
}
const pushUndo = () => { undoStack.push(snapshot()); if (undoStack.length > 60) undoStack.shift(); };

// ---------------------------------------------------------------- load
const loader = new THREE.GLTFLoader();
// keys added by this version = in P.keys but not in the previous version of the same clip (blue diamond on the timeline)
let NEWK = new Set();
function calcNewKeys() { const i = POSES.indexOf(P), prev = POSES.slice(i + 1).find(q => q.clip === P.clip && q.keys);
  NEWK = prev && (P.keys || []).length < (P.frames || 1) ? new Set((P.keys || []).filter(f => !prev.keys.includes(f))) : new Set(); }   // a bake keys every frame: nothing to mark
let P = POSES[0]; calcNewKeys();
function loadGlb(url) { return new Promise((res, rej) => loader.load(url, res, undefined, rej)); }
let openTok = 0;
async function openPose(p) {
  if (keysMode() && (dirtyKeys.size || animDirty)) { clearTimeout(flushT); await flush(); }   // keys of the old version first
  P = p; calcNewKeys(); useNames(p);
  document.body.classList.toggle("km", keysMode()); $("kTools").hidden = $("kLegend").hidden = !keysMode(); if (!keysMode() && typeof TMG !== "undefined" && TMG.on) $("tmgBtn").click();
  ready = false; BN = []; TR = null; $("loading").hidden = false; $("loading").textContent = "Đang tải model…";
  $("poseName").textContent = p.label + " · " + p.version; $("projName").textContent = p.project;
  if (model) { scene.remove(model); scene.remove(ghost); }
  gizmo.detach(); sel = null; selSet = new Set(); edited.clear(); undoStack = []; drafts = {}; mixers = []; frame = 1; stopPlay();
  const tok = ++openTok;
  try {
    const live = host.liveModel ? await host.liveModel(p) : null, src = live || p.glb;   // Studio W3a: model dựng từ mesh + rig + skin hiện tại
    const [g1, g2, g0] = await Promise.all([loadGlb(src), loadGlb(src), live ? loadGlb(p.glb).catch(() => null) : null]);
    if (tok !== openTok) return;          // a newer version was opened while this one loaded: its model must not stay in the scene (two maces, 2026-10-27)
    if (model) { scene.remove(model); scene.remove(ghost); }
    model = posed(g1); ghost = posed(g2);
    ghost.traverse(o => { if (o.isMesh) { o.material = new THREE.MeshBasicMaterial({ color: 0x8fd3ff, transparent: true, opacity: .18, depthWrite: false, skinning: !!o.isSkinnedMesh }); o.renderOrder = 2; } });
    ghost.visible = $("tGhost").classList.contains("on") && ONION.mode === "orig";
    scene.add(model, ghost); onionReset(src);
    B = {}; model.traverse(o => { if (o.isBone) B[o.name] = o; });
    LIVE = null;
    if (live) {   // vị trí nghỉ của rig hiện tại và của model chụp (nếu còn file) để đổi vị trí key qua lại
      const rest = {}; for (const n in B) rest[n] = B[n].position.clone();
      let snap = null; if (g0) { snap = {}; g0.scene.traverse(o => { if (o.isBone) snap[o.name] = o.position.clone(); }); }
      LIVE = { rest, snap };
    }
    // rig dựng ở Studio (Rig): đốt ngón, mũi chân, joint phụ (giáp vai, túi…) cũng là điểm khớp chọn / xoay / key được (user 2026-10-27)
    for (const n of Object.keys(B)) if (!NAMES[n] && (/^((Index|Middle|Ring|Pinky|Thumb)Finger\d|Toes|joint\d+|Scarf\d+)_[LR]$/.test(n) || n === "Weapon")) { NAMES[n] = jointLabel(n); JOINTS.push(n); }
    if (RIGSET() && RIGSET().joints) JOINTS = JOINTS.filter(n => { const j = RIGSET().joints[n]; return !j || j.ctl !== false; });   // Rig: khớp không điều khiển thì không có điểm
    gB = {}; ghost.traverse(o => { if (o.isBone) gB[o.name] = o; });
    buildCache(g1.animations[0]);
    if (keysMode()) initKeys();
    setupRef();
    buildMarkers(); $("loading").hidden = true; buildStrip(); goto(1, true); renderAdjs(); renderRound();
    const top = Math.max(...Object.values(B).map(b => wp(b).y));
    camFit = P.camFit || Math.max(0.6, Math.min(4, top / 1.75)); if (!camInit) { camInit = true; setCam(curCam); }   // chỉ lần đầu: đổi phiên bản giữ nguyên camera (user 2026-10-29)   // POSES camFit when a prop sticks out above the joints
    ready = true; if (keysMode()) applyRemote(); renderPhys(); if (keysMode()) bodyChanged(true);
    setTimeout(() => maybeAutoReview(), 1500);
  } catch (e) {
    $("loading").textContent = "Không tải được model (" + (e && e.message ? e.message : "lỗi mạng") + "). Tải lại trang để thử lại.";
  }
}
function posed(g) {
  const root = g.scene;
  if (g.animations.length) { const mx = new THREE.AnimationMixer(root); mx.clipAction(g.animations[0]).play(); mx.setTime(0); mixers.push(mx); }
  root.traverse(o => { if (o.isMesh) { o.frustumCulled = false; } });
  return root;
}
// ---------------------------------------------------------------- frames
// The original pose of every frame is sampled once at load; frame changes restore from this cache
// (a mixer does not re-apply a zero-length clip, which made edits leak into the base pose).
function buildCache(clip) {
  cache = {};
  const n = P.frames || 1, fps = P.fps || 30, dur = clip ? clip.duration : 0;
  const mx = mixers[0];
  // Blender's exporter starts the clip at frame/fps (F1 = 1/30 s), not 0: offset from the first key (was 1 frame late)
  const t0 = clip && clip.tracks.length ? clip.tracks[0].times[0] : 0;
  for (let f = 1; f <= n; f++) {
    if (mx) mx.setTime(Math.min(t0 + (f - 1) / fps, Math.max(0, dur - 1e-6)));
    cache[f] = Object.fromEntries(Object.keys(B).map(k => [k, [B[k].position.clone(), B[k].quaternion.clone()]]));
  }
  mixers.forEach(m => m.stopAllAction());
}
function sampleAt(f) {
  if (keysMode() && evalPose(f)) {        // page keys: spline + foot lock; the ghost shows the key pose (no physics)
    for (const k of Object.keys(gB)) if (B[k]) { gB[k].position.copy(B[k].position); gB[k].quaternion.copy(B[k].quaternion); }
    if (typeof applyFallGhost === "function") applyFallGhost(f);
    applyPhys(f);
    return;
  }
  const c = cache[f] || cache[1]; if (!c) return;
  for (const [k, [p, q]] of Object.entries(c)) {
    if (B[k]) { B[k].position.copy(p); B[k].quaternion.copy(q); }
    if (gB[k]) { gB[k].position.copy(p); gB[k].quaternion.copy(q); }
  }
  // saved, not yet applied adjustments of this frame show on the model (the ghost keeps the original): a new edit is
  // then a delta on top of them, which is how Blender applies them (pose_lab_apply.py: frame, then createdAt order)
  for (const [k, v] of Object.entries(savedOverlay(f))) if (B[k]) { B[k].quaternion.fromArray(v.q); B[k].position.fromArray(v.p); }
}
function savedOverlay(f) {
  const o = {};
  for (const a of mine().filter(a => a.status !== "done" && (a.frame || 1) === f).sort((a, b) => (a.createdAt || "").localeCompare(b.createdAt || "")))
    Object.assign(o, a.local || {});
  return o;
}
function stashDraft() {   // keep this frame's unsaved edits (local transforms of the edited bones)
  if (!model) return;
  const list = editedList();
  if (list.length) drafts[frame] = Object.fromEntries(list.map(n => [n, { q: B[n].quaternion.clone(), p: B[n].position.clone() }]));
  else delete drafts[frame];
}
// ---------------------------------------------------------------- onion skin kiểu Maya Ghost (user 2026-10-28)
// Bóng mờ = pose ở các key (hoặc frame) TRƯỚC (cam) và SAU (xanh) frame đang xem, càng xa càng mờ. Chế độ "Pose gốc" = bóng cũ
// (pose key chưa cộng điều chỉnh / vật lý). Mỗi bóng là một bản model nạp thêm (không mixer), nạp lười khi cần.
const ONION = { mode: "k1", frames: "", src: null, list: [], loading: null, off: 0 };
try { ONION.frames = localStorage.getItem("pl:onionF") || ""; } catch (e) {}
const onionOn = () => $("tGhost") && $("tGhost").classList.contains("on");
function onionReset(src) { ONION.list.forEach(o => scene.remove(o.root)); ONION.list = []; ONION.src = src; ONION.loading = null; }
function onionFrames(f) {
  const n = NFR(), want = [...new Set(String(ONION.frames || "").split(/[^0-9]+/).filter(Boolean).map(Number).filter(x => x >= 1 && x <= n))].slice(0, 6);
  if (want.length) return want.map(x => ({ f: x, side: x < f ? -1 : x > f ? 1 : 0, i: 0 }));   // frame người dùng nhập
  const m = ONION.mode;
  if (m === "orig") return [];
  if (m[0] === "k") {
    const c = +m.slice(1), ks = keyList();
    return ks.filter(k => k < f).slice(-c).reverse().map((k, i) => ({ f: k, side: -1, i })).concat(ks.filter(k => k > f).slice(0, c).map((k, i) => ({ f: k, side: 1, i })));
  }
  const step = +m.slice(1), out = [];
  for (let i = 1; i <= 3; i++) { if (f - i * step >= 1) out.push({ f: f - i * step, side: -1, i: i - 1 }); if (f + i * step <= n) out.push({ f: f + i * step, side: 1, i: i - 1 }); }
  return out;
}
function onionEnsure(n) {
  if (ONION.list.length >= n || !ONION.src) return Promise.resolve();
  if (ONION.loading) return ONION.loading;
  const src = ONION.src;
  return (ONION.loading = (async () => {
    while (ONION.list.length < n) {
      const g = await loadGlb(src); if (src !== ONION.src) return;
      const root = g.scene, bones = {};
      root.traverse(o => { if (o.isBone) bones[o.name] = o; if (o.isMesh) { o.frustumCulled = false; o.material = new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: .2, depthWrite: false, skinning: !!o.isSkinnedMesh }); o.renderOrder = 2; } });
      root.visible = false; scene.add(root); ONION.list.push({ root, bones });
    }
    ONION.loading = null;
  })());
}
function onionUpdate(f) {          // gọi trong goto TRƯỚC khi dựng frame f (sampleAt ghi vào B; frame f dựng lại ngay sau)
  const show = onionOn() && !playing && !ONION.off, list = show ? onionFrames(f) : [];
  if (list.length > ONION.list.length) onionEnsure(list.length).then(() => { if (model) goto(frame); });
  ONION.list.forEach((o, k) => {
    const it = list[k]; if (!it) { o.root.visible = false; return; }
    sampleAt(it.f);
    for (const n in o.bones) if (B[n]) { o.bones[n].position.copy(B[n].position); o.bones[n].quaternion.copy(B[n].quaternion); }
    const col = it.side < 0 ? 0xff8a3d : it.side > 0 ? 0x3da5ff : 0xc3c9d4, op = [0.3, 0.17, 0.09][it.i] || 0.07;
    o.root.traverse(m => { if (m.isMesh) { m.material.color.setHex(col); m.material.opacity = op; } });
    o.root.visible = true; o.root.updateMatrixWorld(true);
  });
}
function goto(f, first) {
  if (!model) return;
  f = Math.max(1, Math.min(P.frames || 1, Math.round(f)));
  if (!first) stashDraft();
  onionUpdate(f);
  frame = f; sampleAt(f); model.updateMatrixWorld(true); if (ghost) ghost.updateMatrixWorld(true);
  rebase();
  edited = new Set();
  if (drafts[f]) { for (const [n, v] of Object.entries(drafts[f])) { B[n].quaternion.copy(v.q); B[n].position.copy(v.p); edited.add(n); } model.updateMatrixWorld(true); }
  undoStack = []; captureFeet(); attachGizmo(); refresh(); if (bodyVizOn) drawBodyViz(); if (balVizOn) drawBalViz(); if (BAL && BAL.falls && BAL.falls.length) drawFallGraph();
  if (typeof drawImpacts === "function") { drawImpacts(); drawRagGraph(); if (ragLimOn) drawRagLimits(); }
}
function rebase() {   // the pose on screen becomes the reference of the Channel Box / "changed" checks
  base = {}; for (const n of Object.keys(B)) base[n] = { q: wq(B[n]), p: wp(B[n]), lq: B[n].quaternion.clone(), lp: B[n].position.clone() };
  followGrab();
}
function buildStrip() {
  const st = $("strip"); st.innerHTML = ""; st.setAttribute("aria-valuemax", P.frames || 1);
  for (let f = 1; f <= (P.frames || 1); f++) {
    const c = document.createElement("div"); c.className = "cell" + (!keysMode() && (P.keys || []).includes(f) ? " key" : "");
    c.dataset.f = f; c.textContent = (P.frames || 1) <= 40 || f % 5 === 0 || f === 1 ? f : ""; st.append(c);
  }
  for (const s of ["L", "R", "P", "X", "Bl", "I", "S"]) {
    const ln = $("lane" + s); ln.innerHTML = "";
    for (let f = 1; f <= (P.frames || 1); f++) { const i = document.createElement("i"); i.dataset.f = f; ln.append(i); }
  }
}
function renderLanes() {
  if (!keysMode()) return;
  for (const s of ["L", "R", "P"]) for (const i of $("lane" + s).children) {
    const f = +i.dataset.f; i.classList.toggle("on", laneSet(s).has(cyc(f))); i.classList.toggle("mirror", cyc(f) !== f);
  }
  for (const i of $("laneX").children) { const f = +i.dataset.f; i.classList.toggle("on", !!(BODYSCAN && BODYSCAN.issues[f] && BODYSCAN.issues[f].length)); }
  for (const i of $("laneBl").children) { const r = balRow(+i.dataset.f); i.classList.toggle("on", !!r && r.state === "bad"); i.classList.toggle("step", !!r && r.state === "step"); }
  const st = PHYS && PHYS.imp ? PHYS.imp.steps : [];
  { const R = ANIM.phys && ANIM.phys.rag, on = R && R.on && !P.loop;
    for (const i of $("laneS").children) { const f = +i.dataset.f; i.style.background = on && f >= R.from ? "rgba(255,159,67," + (0.12 + 0.88 * Math.min(1, ragStrength(f))).toFixed(2) + ")" : ""; } }
  for (const i of $("laneI").children) { const f = +i.dataset.f; i.classList.toggle("on", impAt(f) >= 0); i.classList.toggle("step", st.some(s => f >= s.f0 && f <= s.f1)); }
}
// timeline theo đối tượng đang chọn (user 2026-10-29 "key trên timeline đang hiển thị chung cho tất cả đối tượng"):
// chọn vật thể phụ = key riêng của nó; chọn khớp = key cả người nhưng key mà khớp đó giữ nguyên (so key trước) vẽ rỗng; không chọn = như cũ
const boneDiff = (a, b) => { if (!a || !b) return !!(a || b); const d = Math.abs(a[0] * b[0] + a[1] * b[1] + a[2] * b[2] + a[3] * b[3]); return d < 0.99999 || Math.hypot(a[4] - b[4], a[5] - b[5], a[6] - b[6]) > 1e-4; };
function keyFilter() {
  const pk = host.propKeys ? host.propKeys() : null;
  if (pk) return { kind: "prop", name: pk.name, keys: new Set(pk.keys) };
  const js = [...selSet].filter(n => B[n]); if (!js.length || !keysMode()) return null;
  const ks = [...KEYS.keys()].sort((a, b) => a - b), moved = new Set();
  ks.forEach((f, i) => { const a = i ? (KEYS.get(ks[i - 1]).pose || {}) : null, b = KEYS.get(f).pose || {}; if (!a || js.some(n => boneDiff(a[n], b[n]))) moved.add(f); });
  return { kind: "joint", name: js.map(n => NAMES[n] || n).join(", "), keys: moved };
}
let stripSig = "";
const stripSigNow = () => { const pk = host.propKeys ? host.propKeys() : null; return (pk ? pk.name + ":" + pk.keys.join(",") : "") + "|" + [...selSet].join(","); };
function renderStrip() {
  if (!model) return;
  const KF = keyFilter(); stripSig = stripSigNow();
  { let tag = $("kfTag"); if (!tag) { tag = document.createElement("span"); tag.id = "kfTag"; tag.className = "kftag"; $("fcount").after(tag); }
    tag.hidden = !KF; tag.textContent = KF ? (KF.kind === "prop" ? "Key: " + KF.name : "Key: " + KF.name + " (rỗng = khớp giữ nguyên)") : "";
    tag.title = KF ? (KF.kind === "prop" ? "Timeline đang hiện key của vật thể " + KF.name + ". Bỏ chọn để thấy key cả người." : "Key đặc = khớp đang chọn đổi so với key trước, rỗng = giữ nguyên. Bỏ chọn để thấy mọi key.") : ""; }
  const saved = new Set(mine().filter(a => a.status !== "done").map(a => a.frame || 1));
  const live = new Set(Object.keys(drafts).map(Number)); if (editedList().length) live.add(frame); else live.delete(frame);
  const km = keysMode();
  for (const c of $("strip").children) {
    const f = +c.dataset.f; c.classList.toggle("cur", f === frame);
    if (KF && KF.kind === "prop") { c.classList.toggle("key", KF.keys.has(f)); c.classList.add("kprop"); c.classList.remove("knew", "loopend", "khold", "kdrop"); }
    else if (km) { c.classList.remove("kprop"); c.classList.toggle("key", f === cyc(f) && KEYS.has(f)); c.classList.toggle("knew", f === cyc(f) && KEYS.has(f) && NEWK.has(f) && !KF); c.classList.toggle("loopend", f !== cyc(f) && KEYS.has(cyc(f)));
              c.classList.toggle("khold", !!KF && f === cyc(f) && KEYS.has(f) && !KF.keys.has(f));
              c.classList.toggle("kdrop", !!keyDrag && keyDrag.to === f); }
    else c.classList.remove("kprop", "khold");
    c.querySelectorAll(".dot").forEach(d => d.remove());
    if (live.has(f)) { const d = document.createElement("i"); d.className = "dot draft"; c.append(d); }
    if (saved.has(f)) { const d = document.createElement("i"); d.className = "dot saved"; c.append(d); }
  }
  $("fcount").innerHTML = "F<b></b> / " + (P.frames || 1); $("fcount").querySelector("b").textContent = frame;
  $("strip").setAttribute("aria-valuenow", frame);
  renderLanes(); renderRef(); drawPhysGraph(); renderTiming();
}
function frameAtX(x) {
  const r = $("strip").getBoundingClientRect(); return 1 + Math.floor(Math.max(0, Math.min(0.9999, (x - r.left) / r.width)) * (P.frames || 1));
}
let scrubbing = false, keyDrag = null;
$("strip").addEventListener("pointerdown", e => {
  stopPlay(); try { $("strip").setPointerCapture(e.pointerId); } catch {}
  const f = frameAtX(e.clientX);
  if (keysMode() && !(host.propKeys && host.propKeys()) && (e.button === 1 || e.shiftKey || TM.add) && KEYS.has(cyc(f))) {     // Shift / middle drag = move the key (không khi timeline đang hiện key vật thể)
    e.preventDefault(); keyDrag = { from: cyc(f), to: f }; renderStrip(); return;
  }
  scrubbing = true; goto(f);
});
$("strip").addEventListener("pointermove", e => {
  const f = frameAtX(e.clientX);
  if (keyDrag) { if (f !== keyDrag.to) { keyDrag.to = f; renderStrip(); } return; }
  if (scrubbing && f !== frame) goto(f);
});
$("strip").addEventListener("pointerup", () => {
  scrubbing = false;
  if (!keyDrag) return;
  const { from } = keyDrag, to = cyc(keyDrag.to); keyDrag = null;
  if (to !== from) {
    if (KEYS.has(to)) $("p_status").textContent = "F" + to + " đã có key: xoá key đó trước rồi dời.";
    else { const k = KEYS.get(from); KEYS.delete(from); KEYS.set(to, { ...k, at: new Date().toISOString() }); dirtyKeys.add(from); dirtyKeys.add(to);
           keysChanged(); goto(to, true); $("p_status").textContent = "Đã dời key F" + from + " → F" + to + "."; }
  }
  renderStrip();
});
// ---------------------------------------------------------------- Timing panel: drag the MAIN keys (the phases); the breakdowns between them follow
// Main keys = the keys of the oldest version of this clip (the team's blocking), found again by their rank among the keys so they
// stay main after being moved. Dragging a main key re-spaces the keys between its neighbours in proportion (breakdown poses unchanged).
const PHASE_NAMES = { "Gaygor_Attack 10 Blocking": ["Quật ra sau", "Nén", "Giơ chùy", "Đập", "Gồng, nhấc chùy", "Đặt về vai", "Lắng"] };
const TMG = { on: false, ripple: false, drag: null };
const tmgKeys = () => [...KEYS.keys()].sort((a, b) => a - b);
function tmgRanks() {     // ranks (among all keys) of the main keys, null when this version has no usable list
  const ks = tmgKeys(), old = POSES.filter(q => q.clip === P.clip && q.keys && q.keys.length).pop(), seed = [...(P.keys || [])].sort((a, b) => a - b);
  if (old && ks.length === seed.length) { const r = seed.map((k, i) => old.keys.includes(k) ? i : -1).filter(i => i >= 0); if (r.length >= 3) return r; }
  return null;
}
function tmgMain() {      // main keys carry a stored flag (survives moves and reloads); first time: derive them and save the flag
  const ks = tmgKeys(), flagged = ks.filter(k => KEYS.get(k).main);
  if (flagged.length >= 2) { seedPhaseNames(flagged); return flagged; }
  const r = tmgRanks(), old = POSES.filter(q => q.clip === P.clip && q.keys && q.keys.length).pop(), given = (P.main || []).filter(k => KEYS.has(k));
  let m = given.length >= 2 ? given : r ? r.map(i => ks[i]) : old ? ks.filter(k => old.keys.includes(k)) : [];
  if (m.length < 3) return ks;
  for (const k of m) { KEYS.set(k, { ...KEYS.get(k), main: true }); dirtyKeys.add(k); }
  seedPhaseNames(m); scheduleFlush(); return m;
}
function seedPhaseNames(main) {   // first time only: the default names of this clip go onto the keys that start each phase
  const def = P.phases || PHASE_NAMES[P.clip];
  if (!def || def.length !== main.length - 1 || main.some(k => KEYS.get(k).phase)) return;
  main.slice(0, -1).forEach((k, i) => { KEYS.set(k, { ...KEYS.get(k), phase: def[i] }); dirtyKeys.add(k); }); scheduleFlush();
}
const phaseNames = main => main.slice(0, -1).map((k, i) => (KEYS.get(k) && KEYS.get(k).phase) || "Pha " + (i + 1));
function setMain(f, on) {         // split a phase at key f (on) or merge the phase starting at f into the one before (off)
  const k = KEYS.get(f); if (!k) return;
  pushUndo(); const n = { ...k };
  if (on) { n.main = true; n.phase = "Pha mới"; } else { delete n.main; delete n.phase; }
  KEYS.set(f, n); dirtyKeys.add(f); keysChanged(); renderTiming();
  $("p_status").textContent = on ? "Đã tách pha ở F" + f + ". Nhấp đúp vào thanh pha để đặt tên." : "Đã gộp pha ở F" + f + " vào pha trước.";
}
function setPhaseName(f, name) {
  const k = KEYS.get(f); name = (name || "").trim(); if (!k || !k.main || name === (k.phase || "")) return;
  pushUndo(); KEYS.set(f, { ...k, phase: name.slice(0, 40) }); dirtyKeys.add(f); keysChanged(); renderTiming();
}
function tmgMap(mainNew) {      // old frame -> new frame for every key: piecewise-linear between the main keys, then strictly between the neighbouring main keys
  const ks = tmgKeys(), mains = [...mainNew.keys()].sort((a, b) => a - b), out = new Map(mainNew);
  for (let i = 0; i + 1 < mains.length; i++) {
    const a = mains[i], b = mains[i + 1], subs = ks.filter(k => k > a && k < b), v = subs.map(k => Math.round(mainNew.get(a) + (k - a) * (mainNew.get(b) - mainNew.get(a)) / (b - a)));
    for (let j = 0; j < v.length; j++) v[j] = Math.max(v[j], (j ? v[j - 1] : mainNew.get(a)) + 1);               // forward: strictly after the previous key
    for (let j = v.length - 1; j >= 0; j--) v[j] = Math.min(v[j], (j < v.length - 1 ? v[j + 1] : mainNew.get(b)) - 1);   // backward: strictly before the next (a rounded key used to land on a main key and overwrite it)
    subs.forEach((k, j) => out.set(k, v[j]));
  }
  for (const k of ks) if (!out.has(k)) out.set(k, k);
  return out;
}
function renderTiming() {
  if (!TMG.on || !keysMode() || $("tmgTrack").querySelector(".tbin")) return;   // keep a phase name being typed
  const box = $("tmgTrack"), N = P.frames || 1, ks = tmgKeys(), main = tmgMain(), pos = TMG.drag ? TMG.drag.pos : new Map(ks.map(k => [k, k]));
  const xp = f => ((f - 0.5) / N * 100) + "%", el = (cls, st, txt) => { const d = document.createElement("div"); d.className = cls; Object.assign(d.style, st); if (txt != null) d.textContent = txt; box.append(d); return d; };
  const names = phaseNames(main);
  box.innerHTML = "";
  for (let f = 5; f <= N; f += (N > 80 ? 10 : 5)) { el("tk", { left: xp(f) }); el("tkl", { left: xp(f) }, f); }
  for (let i = 0; i + 1 < main.length; i++) {
    const a = pos.get(main[i]), b = pos.get(main[i + 1]), nm = names[i] + " ";
    const d = el("tb" + (i % 2 ? " odd" : ""), { left: xp(a), width: ((b - a) / N * 100) + "%" }, nm + (b - a) + "F");
    d.title = nm + (b - a) + " frame = " + ((b - a) / (P.fps || 30)).toFixed(2) + " s. Nhấp đúp để đổi tên."; d.dataset.k = main[i];
  }
  for (const k of ks) if (!main.includes(k)) { const d = el("tsub", { left: xp(pos.get(k)) }); d.dataset.k = k; d.title = "F" + k + ": nhấp đúp để tách pha ở đây"; }
  for (const o of main) {
    const n = pos.get(o), fixed = o === main[0] || o === main[main.length - 1], moved = o !== n;
    const h = el("tk2" + (fixed ? " fixed" : "") + (moved ? " moved" : ""), { left: xp(n) }); h.dataset.o = o; h.title = "F" + o + (moved ? " → F" + n : "") + (fixed ? " (cố định)" : "");
    el("tkn" + (moved ? " moved" : ""), { left: xp(n) }, moved ? o + "→" + n : n);
  }
  el("tcur", { left: xp(frame) });
  const isMain = main.includes(frame), canSplit = KEYS.has(frame) && !isMain && frame > main[0] && frame < main[main.length - 1];
  $("tmgSplit").disabled = !canSplit; $("tmgSplit").textContent = "+ Tách pha" + (canSplit ? " ở F" + frame : "");
  $("tmgMerge").disabled = !(isMain && frame !== main[0] && frame !== main[main.length - 1]); $("tmgMerge").textContent = "− Gộp pha" + (!$("tmgMerge").disabled ? " ở F" + frame : "");
  const chg = tmgChanged(), same = tmgBase().length === ks.length;
  $("tmgSend").disabled = !db || !canWrite || !chg; $("tmgReset").disabled = !chg || !same; $("tmgDirty").hidden = !chg;
  $("tmgInfo").textContent = N + " F · " + (N / (P.fps || 30)).toFixed(2) + " s · " + main.length + " key chính · " + (ks.length - main.length) + " chuyển tiếp";
}
function tmgTarget(clientX) {
  const r = $("tmgTrack").getBoundingClientRect(), N = P.frames || 1, ks = tmgKeys(), main = tmgMain(), o = TMG.drag.o;
  let delta = Math.round((clientX - TMG.drag.x0) / r.width * N);
  const cnt = (a, b) => ks.filter(k => k > a && k < b).length, i = main.indexOf(o), prev = main[i - 1], last = main[main.length - 1], nxt = main[i + 1];
  const mainNew = new Map(main.map(k => [k, k]));
  if (!TMG.ripple) { delta = Math.max(prev + cnt(prev, o) + 1 - o, Math.min(nxt - cnt(o, nxt) - 1 - o, delta)); mainNew.set(o, o + delta); }
  else {
    const mv = main.filter(k => k >= o && k !== last), lm = mv[mv.length - 1];
    delta = Math.max(prev + cnt(prev, o) + 1 - o, Math.min(last - cnt(lm, last) - 1 - lm, delta)); for (const k of mv) mainNew.set(k, k + delta);
  }
  return { pos: tmgMap(mainNew), delta };
}
function tmgCommit(pos) {
  const moves = [...pos].filter(([o, n]) => o !== n); if (!moves.length) return;
  pushUndo();
  const saved = new Map(moves.map(([o]) => [o, KEYS.get(o)])), at = new Date().toISOString();
  for (const [o] of moves) KEYS.delete(o);
  for (const [o, n] of moves) { KEYS.set(n, { ...saved.get(o), at }); dirtyKeys.add(o); dirtyKeys.add(n); }
  keysChanged(); reEval();
  $("p_status").textContent = "Timing: " + moves.length + " key dời (" + moves.slice(0, 6).map(([o, n]) => "F" + o + "→F" + n).join(", ") + (moves.length > 6 ? "…" : "") + "). Ctrl+Z để hoàn tác.";
}
function tmgBase() {      // frames the AI last built / was last told: the latest timing note of this version, else the version's own key list
  const t = mine().filter(a => a.kind === "timing" && a.timing && a.timing.after).sort((x, y) => (x.createdAt || "").localeCompare(y.createdAt || "")).pop();
  return t ? t.timing.after : [...(P.keys || [])].sort((a, b) => a - b);
}
const tmgChanged = () => { const b = tmgBase(), c = tmgKeys(); return b.length !== c.length || b.some((k, i) => k !== c[i]); };
$("tmgSend").onclick = async () => {
  const before = tmgBase(), after = tmgKeys(), main = tmgMain(), names = phaseNames(main), r = after.map((k, i) => main.includes(k) ? i : -1).filter(i => i >= 0);
  if (!db || !canWrite) { $("p_status").textContent = "Chưa lưu được góp ý (cần đăng nhập và có quyền ghi)."; return; }
  const bm = r && before.length === after.length ? r.map(i => before[i]) : before, am = r && before.length === after.length ? r.map(i => after[i]) : after;
  const lines = [];
  for (let i = 0; i + 1 < bm.length; i++) { const d0 = bm[i + 1] - bm[i], d1 = am[i + 1] - am[i]; if (d0 !== d1) lines.push((names[i] || "F" + bm[i] + "→F" + bm[i + 1]) + " " + d0 + "F → " + d1 + "F"); }
  const note = $("text").value.trim();
  const text = "Timing mới (key chính F" + am.join(", F") + "; trước đó F" + bm.join(", F") + ")" + (lines.length ? ". Đổi: " + lines.join("; ") : "") +
    ". Key chuyển tiếp co giãn theo tỉ lệ, pose giữ nguyên." + (note ? " " + note : "");
  const body = { clip: P.clip, version: P.version, frame: frame, kind: "timing", bones: {}, local: {}, text, timing: { before, after, main: { before: bm, after: am }, phases: names }, status: "open", createdAt: new Date().toISOString() };
  if (myId) body.author = myId;
  $("tmgSend").disabled = true;
  try { await db.collection("adjusts").add(body); adjs.push({ ...body }); if (note) $("text").value = ""; renderAdjs(); renderTiming();
        $("p_status").textContent = "Đã lưu góp ý timing. Bấm Gửi cho AI để gửi cùng các góp ý khác."; }
  catch (e) { fail(e); renderTiming(); }
};
function applyLanes(on) { document.body.classList.toggle("lanesOn", on); $("lanesBtn").classList.toggle("primary", on); try { localStorage.setItem("poselab:lanes", on ? "1" : "0"); } catch {} window.dispatchEvent(new Event("resize")); }
$("lanesBtn").onclick = () => applyLanes(!document.body.classList.contains("lanesOn"));
{ let on = false; try { on = localStorage.getItem("poselab:lanes") === "1"; } catch {} applyLanes(on); }
$("tmgSplit").onclick = () => setMain(frame, true);
$("tmgMerge").onclick = () => setMain(frame, false);
$("tmgTrack").addEventListener("dblclick", e => {
  const sub = e.target.closest(".tsub"); if (sub) { setMain(+sub.dataset.k, true); return; }
  const bar = e.target.closest(".tb"); if (!bar) return;
  const k = +bar.dataset.k, inp = document.createElement("input"); inp.className = "tbin"; inp.value = (KEYS.get(k) && KEYS.get(k).phase) || "";
  inp.style.left = bar.style.left; inp.style.width = "max(120px, " + bar.style.width + ")"; inp.placeholder = "Tên pha";
  $("tmgTrack").append(inp); inp.focus(); inp.select();
  let done = false; const fin = ok => { if (done) return; done = true; if (ok) setPhaseName(k, inp.value); inp.remove(); renderTiming(); };
  inp.onkeydown = ev => { ev.stopPropagation(); if (ev.key === "Enter") fin(true); if (ev.key === "Escape") fin(false); };
  inp.onblur = () => fin(true);
});
$("tmgReset").onclick = () => { const b = tmgBase(), c = tmgKeys(); if (b.length === c.length) { tmgCommit(new Map(c.map((k, i) => [k, b[i]]))); renderTiming(); } };
$("tmgBtn").onclick = () => { TMG.on = !TMG.on; $("tmgPanel").hidden = !TMG.on; document.body.classList.toggle("tmgOn", TMG.on); $("tmgBtn").classList.toggle("primary", TMG.on); window.dispatchEvent(new Event("resize")); renderTiming(); };
$("tmgRipple").onchange = e => { TMG.ripple = e.target.checked; };
$("tmgTrack").addEventListener("pointerdown", e => {
  if (e.target.closest(".tbin")) return;
  const h = e.target.closest(".tk2"); if (!h) { const r = $("tmgTrack").getBoundingClientRect(); goto(Math.max(1, Math.min(P.frames || 1, 1 + Math.floor((e.clientX - r.left) / r.width * (P.frames || 1))))); return; }
  const o = +h.dataset.o; goto(o); if (h.classList.contains("fixed")) return;
  try { $("tmgTrack").setPointerCapture(e.pointerId); } catch {}
  TMG.drag = { o, x0: e.clientX, pos: new Map(tmgKeys().map(k => [k, k])) }; e.preventDefault();
});
$("tmgTrack").addEventListener("pointermove", e => { if (!TMG.drag) return; TMG.drag.pos = tmgTarget(e.clientX).pos; renderTiming(); });
$("tmgTrack").addEventListener("pointerup", e => { if (!TMG.drag) return; const { pos } = tmgTarget(e.clientX); TMG.drag = null; tmgCommit(pos); renderTiming(); });
$("tmgTrack").addEventListener("pointercancel", () => { TMG.drag = null; renderTiming(); });
$("strip").addEventListener("auxclick", e => e.preventDefault());
const keyList = () => keysMode() ? [...new Set([...KEYS.keys(), ...(P.loop ? [P.frames] : [])])].sort((a, b) => a - b)
  : [...new Set([1, ...(P.keys || []), P.frames || 1])].sort((a, b) => a - b);
$("prevF").onclick = () => { stopPlay(); goto(frame - 1); };
$("nextF").onclick = () => { stopPlay(); goto(frame + 1); };
$("prevKey").onclick = () => { stopPlay(); const k = keyList().filter(f => f < frame).pop(); if (k) goto(k); };
$("nextKey").onclick = () => { stopPlay(); const k = keyList().find(f => f > frame); if (k) goto(k); };
function stopPlay() { playing = false; $("play").textContent = "Phát"; }
$("play").onclick = () => {
  if (playing) { stopPlay(); return; }
  if ((P.frames || 1) < 2) { $("p_status").textContent = "Clip này chỉ có 1 pose nên không có gì để phát."; return; }
  playing = true; $("play").textContent = "Dừng"; playT0 = performance.now(); playF0 = frame >= (P.frames || 1) ? 1 : frame;
  gizmo.detach();
};
function tickPlay(now) {
  if (!playing) return;
  const f = 1 + ((playF0 - 1 + Math.floor((now - playT0) / 1000 * (P.fps || 30))) % (P.frames || 1));
  if (f !== frame) goto(f);
}

function buildMarkers() {
  for (const m of Object.values(markers)) overlay.remove(m);
  for (const t of Object.values(sticks)) overlay.remove(t);
  markers = {}; sticks = {};
  for (const n of JOINTS) if (B[n]) {
    const m = new THREE.Mesh(markerGeo, jointMat()); m.renderOrder = 11; m.userData.bone = n; overlay.add(m); markers[n] = m;
  }
  for (const n of Object.keys(markers)) {          // stick to the nearest ancestor that has a joint dot
    let pa = null;
    for (let o = B[n].parent; o; o = o.parent) if (markers[o.name]) { pa = o.name; break; }
    if (!pa) continue;
    const t = new THREE.Mesh(stickGeo, jointMat()); t.renderOrder = 10; t.userData = { from: pa, to: n }; overlay.add(t); sticks[n] = t;
  }
}
const jointPos = n => n === "slingshot_0" ? B[n].localToWorld(new V3(0, 0, 0)) : wp(B[n]);
function toScreen(p) {
  const r = canvas.getBoundingClientRect(), v = p.clone().project(CAM());
  return { x: (v.x + 1) / 2 * r.width, y: (1 - v.y) / 2 * r.height, front: v.z < 1 };
}
const UP = new V3(0, 1, 0);
function placeMarkers() {
  placePoles();
  const show = $("tJoints").classList.contains("on");
  const P3 = {}, D = {};
  let dmin = Infinity, dmax = 0;
  for (const n of Object.keys(markers)) {
    P3[n] = jointPos(n); D[n] = CAM().position.distanceTo(P3[n]);
    dmin = Math.min(dmin, D[n]); dmax = Math.max(dmax, D[n]);
  }
  const op = {}, SZ = {};
  // khớp sẽ được chọn nếu bấm ngay (user 2026-10-29: rê chuột thì nhiều khớp cùng sáng, không biết bấm trúng khớp nào):
  // đúng luật của pickAt, tô trắng + to hơn + tên cạnh chuột
  let hot = null; try { hot = show && hoverXY && !gizmo.dragging && !(marq && marq.on) ? pickAt(hoverXY[0], hoverXY[1]) : null; } catch (e) {}
  hotTag(hot);
  for (const [n, m] of Object.entries(markers)) {
    const far = dmax > dmin ? (D[n] - dmin) / (dmax - dmin) : 0;          // 0 = nearest joint, 1 = farthest
    let o = JOINT_BASE * (1 - 0.55 * far);                                 // mặc định mờ (user 2026-10-29 "độ mờ của khớp ban đầu mờ hơn nữa"), nhạt dần theo khoảng cách
    if (hoverXY) {
      const sp = toScreen(P3[n]), px = Math.hypot(sp.x - hoverXY[0], sp.y - hoverXY[1]);
      o += (1 - o) * Math.max(0, Math.min(1, 1 - (px - 12) / 60));         // mouse close -> 100 %
    }
    const on = selSet.has(n);
    if (on || n === hot) o = 1;
    op[n] = o;
    m.position.copy(P3[n]); m.visible = show;
    m.material.color.copy(n === hot && !on ? COL.hot : on ? COL.sel : edited.has(n) ? COL.edit : COL.joint);
    m.material.opacity = o;
    SZ[n] = pxAt(D[n]);                                                    // world size of 1 screen pixel there
    m.scale.setScalar(SZ[n] * DOT_PX * (n === sel ? 1.5 : n === hot ? 1.7 : on ? 1.25 : 1));
  }
  for (const [n, t] of Object.entries(sticks)) {
    const a = P3[t.userData.from], b = P3[n], d = b.clone().sub(a), len = d.length();
    t.visible = show && len > 1e-4;
    if (!t.visible) continue;
    const on = selSet.has(n);
    t.position.copy(a); t.quaternion.setFromUnitVectors(UP, d.divideScalar(len)); const w = (SZ[n] + SZ[t.userData.from]) / 2 * STICK_PX * (on ? 1.6 : 1); t.scale.set(w, len, w);
    t.material.color.copy(on ? COL.sel : edited.has(n) ? COL.edit : COL.joint);
    t.material.opacity = Math.min(op[n], op[t.userData.from]) * 0.85;
  }
}

// ---------------------------------------------------------------- selection + gizmo
// Click = pick the joint dot nearest the cursor on screen (within 14 px); Shift+click adds / removes it. Drag on empty
// space (not on the gizmo, no Alt) = marquee: joints inside the box are selected (Shift adds them). The gizmo works
// on the last picked joint; in rotate mode the other selected joints turn by the same world rotation.
let downAt = null, marq = null, marqDiv = null;
const visJoints = () => $("tJoints").classList.contains("on") ? Object.keys(markers) : [];
function hotTag(n) {   // tên khớp sắp chọn, cạnh con trỏ
  if (!hotEl) { hotEl = document.createElement("div"); hotEl.className = "jhot"; hotEl.style.cssText = "position:absolute;pointer-events:none;z-index:7;padding:1px 6px;border-radius:4px;background:#000c;color:#fff;font:11px/1.5 system-ui,sans-serif;white-space:nowrap;display:none"; viewer.appendChild(hotEl); }
  if (n !== hotN) { hotN = n; hotEl.textContent = n ? (NAMES[n] || n) : ""; }
  canvas.style.cursor = n ? "pointer" : "";
  if (!n || !hoverXY) { hotEl.style.display = "none"; return; }
  const r = canvas.getBoundingClientRect(), vr = viewer.getBoundingClientRect();
  hotEl.style.display = "block"; hotEl.style.left = (r.left - vr.left + hoverXY[0] + 14) + "px"; hotEl.style.top = (r.top - vr.top + hoverXY[1] + 10) + "px";
}
function pickAt(x, y) {
  const R = TM.on ? 30 : 14; let best = null, bd = R, bz = Infinity;
  for (const n of visJoints()) {
    const p = jointPos(n), sp = toScreen(p); if (!sp.front) continue;
    const d = Math.hypot(sp.x - x, sp.y - y), z = CAM().position.distanceTo(p);
    if (d > R) continue;
    if (d < bd - 3 || (Math.abs(d - bd) <= 3 && z < bz)) { best = n; bd = d; bz = z; }   // overlapping: nearer the CAM() wins
  }
  return best;
}
const localXY = e => { const r = canvas.getBoundingClientRect(); return [e.clientX - r.left, e.clientY - r.top]; };
canvas.addEventListener("pointerdown", e => {
  downAt = localXY(e);
  marq = e.button === 0 && !e.altKey && !gizmo.axis && (!TM.on || TM.mode === "box") ? { x0: downAt[0], y0: downAt[1], shift: e.shiftKey || TM.add, on: false } : null;
});
canvas.addEventListener("pointermove", e => {
  hoverXY = localXY(e);
  if (impAim && (e.buttons & 1) && !e.altKey) { impAimAt(hoverXY[0], hoverXY[1], false); return; }
  if (!marq || gizmo.dragging || !(e.buttons & 1)) return;
  const [x, y] = hoverXY;
  if (!marq.on && Math.hypot(x - marq.x0, y - marq.y0) < 5) return;
  marq.on = true; marq.x1 = x; marq.y1 = y;
  if (!marqDiv) { marqDiv = document.createElement("div"); marqDiv.className = "marquee"; viewer.append(marqDiv); }
  const r = canvas.getBoundingClientRect(), vr = viewer.getBoundingClientRect();
  Object.assign(marqDiv.style, { left: (r.left - vr.left + Math.min(x, marq.x0)) + "px", top: (r.top - vr.top + Math.min(y, marq.y0)) + "px",
    width: Math.abs(x - marq.x0) + "px", height: Math.abs(y - marq.y0) + "px", display: "block" });
});
canvas.addEventListener("pointerleave", () => { hoverXY = null; hotTag(null); });
canvas.addEventListener("pointerup", e => {
  const m = marq; marq = null;
  if (marqDiv) marqDiv.style.display = "none";
  if (impAim && !e.altKey && !gizmo.dragging) { const [x, y] = localXY(e); impAimAt(x, y, true); return; }
  if (impPick && !e.altKey && !gizmo.dragging) { const [x, y] = localXY(e); impPick = false;
    try { if (!impPickAt(x, y)) { $("p_status").textContent = "Không trúng điểm nào trên người: bấm sát bề mặt hơn."; renderImpacts(); } }
    catch (err) { console.error(err); renderImpacts(); $("p_status").textContent = "Lỗi khi đặt tác động: " + (err && err.message || err) + " @ " + String(err && err.stack || "").split("\n").slice(1, 3).join(" | ").replace(/https?:[^ )]*\//g, ""); }
    return; }
  if (m && m.on) {                                  // marquee select
    const xa = Math.min(m.x0, m.x1), xb = Math.max(m.x0, m.x1), ya = Math.min(m.y0, m.y1), yb = Math.max(m.y0, m.y1);
    const inside = visJoints().filter(n => { const sp = toScreen(jointPos(n)); return sp.front && sp.x >= xa && sp.x <= xb && sp.y >= ya && sp.y <= yb; });
    const names = m.shift ? [...selSet, ...inside.filter(n => !selSet.has(n))] : inside;
    setSelection(names, inside.length ? inside[inside.length - 1] : sel);
    return;
  }
  if (!downAt || e.altKey || gizmo.dragging) return;
  const [x, y] = localXY(e);
  if (Math.hypot(x - downAt[0], y - downAt[1]) > 4) return;
  const pk = pickPole(x, y); if (pk) { selectPole(pk); return; }
  const n = pickAt(x, y);
  const addSel = e.shiftKey || TM.add;
  if (n && addSel) {                            // Shift+click: add / remove
    if (selSet.has(n)) { const rest = [...selSet].filter(k => k !== n); setSelection(rest, n === sel ? rest[rest.length - 1] : sel); }
    else setSelection([...selSet, n], n);
  } else if (n) setSelection([n], n);
  else if (!gizmo.axis && !addSel) select(null);
});
function setSelection(names, primary) {
  if (playing) stopPlay(); setTimeout(() => { if (typeof renderBody === "function") renderBody(); if (typeof drawRagLimits === "function" && ragLimOn) drawRagLimits(); });
  poleSel = null;
  selSet = new Set(names.filter(n => markers[n]));
  sel = primary && selSet.has(primary) ? primary : [...selSet].pop() || null;
  if (!sel) { gizmo.detach(); refresh(); return; }
  attachGizmo(); refresh();
}
function select(n) { setSelection(n ? [n] : [], n); }
function attachGizmo() {
  if (!sel) return;
  const isAnkle = sel.startsWith("Ankle_");
  if (mode === "select") { gizmo.detach(); return; }
  if (mode === "translate" && !canMove(sel)) { setMode("rotate"); return; }
  gizmo.setMode(mode);
  if (mode === "translate" && isAnkle) {
    const s = sel.slice(-1); footHandle[s].position.copy(footT[s]); footHandle[s].quaternion.set(0, 0, 0, 1); footHandle[s].updateMatrixWorld(true);
    gizmo.attach(footHandle[s]);
  } else if (mode === "translate" && isWrist(sel)) {
    const s = sel.slice(-1); handQ[s] = wq(B[sel]);
    handHandle[s].position.copy(wp(B[sel])); handHandle[s].quaternion.set(0, 0, 0, 1); handHandle[s].updateMatrixWorld(true);
    gizmo.attach(handHandle[s]);
  } else gizmo.attach(B[sel]);
}
function setMode(m) {
  mode = m; $("mRot").classList.toggle("on", m === "rotate"); $("mMove").classList.toggle("on", m === "translate");
  $("mSel").classList.toggle("on", m === "select");
  attachGizmo(); refresh();
}
$("mRot").onclick = () => setMode("rotate");
$("mSel").onclick = () => setMode("select");
$("mScale").onclick = () => { $("p_status").textContent = "Rig không cho scale khớp: dùng W (dời) hoặc E (xoay)."; };
$("mMove").onclick = () => setMode("translate");
$("mSpace").onclick = () => { const s = gizmo.space === "local" ? "world" : "local"; gizmo.setSpace(s); $("mSpace").firstChild.textContent = "Trục: " + s + " "; };
gizmo.addEventListener("dragging-changed", e => {
  orbit.enabled = !e.value;
  if (e.value) {
    stopPlay(); pushUndo(); if (sel === GUN) gunGrab();
    multiQ0 = mode === "rotate" && selSet.size > 1 ? { p: wq(B[sel]), o: Object.fromEntries([...selSet].filter(n => n !== sel).map(n => [n, wq(B[n])])) } : null;
  } else { multiQ0 = null; commitEdit(); }
});
const depth = n => { let d = 0; for (let o = B[n]; o; o = o.parent) d++; return d; };
function rotateOthers() {        // same world rotation as the gizmo joint, applied parent -> child
  if (!multiQ0) return;
  const dq = wq(B[sel]).multiply(multiQ0.p.clone().invert());
  for (const n of Object.keys(multiQ0.o).sort((a, b) => depth(a) - depth(b))) {
    setWorldQuat(B[n], dq.clone().multiply(multiQ0.o[n])); edited.add(n);
  }
  model.updateMatrixWorld(true);
}
gizmo.addEventListener("objectChange", () => {
  if (poleSel && model) { poleDrag(poleSel); return; }
  if (!sel || !model) return;
  model.updateMatrixWorld(true);
  const isAnkle = sel.startsWith("Ankle_"), s = sel.slice(-1);
  if (isAnkle && mode === "translate") { footT[s] = footHandle[s].position.clone(); solveLeg(s); refresh(); }
  else if (isWrist(sel) && mode === "translate") { solveArm(s, handHandle[s].position); followEdit(); refresh(); }
  else { rotateOthers(); afterEdit(); }
});
// ---------------------------------------------------------------- pole vectors (knee / elbow)
// An orange diamond beside each knee and elbow (user 2026-10-23 "không có ctl pole vector"): drag it and the middle joint
// swings round the root->end line (hip->ankle, shoulder->wrist) while the foot / hand stay where they are. The IK keeps the
// bend plane the pole gives it, so the pole also stays put when the foot or hand is moved.
const POLE_NAMES = { Knee_L: "Pole gối trái", Knee_R: "Pole gối phải", Elbow_L: "Pole khuỷu trái", Elbow_R: "Pole khuỷu phải" };
const POLES = {};
let poleSel = null;
const poleChain = k => k.startsWith("Knee") ? LEGS[k.slice(-1)] : ARMS[k.slice(-1)];
function polePoint(k) {      // the pole now: from the middle joint, away from the root->end line, 80 % of the upper bone
  const [h, m, e] = poleChain(k).map(n => B[n]); if (!h || !m || !e) return null;
  const a = wp(h), mid = wp(m), ax = wp(e).sub(a); if (ax.lengthSq() < 1e-10) return null; ax.normalize();
  const v = mid.clone().sub(a); v.sub(ax.clone().multiplyScalar(v.dot(ax)));
  if (v.lengthSq() < 1e-8) { v.set(0, 0, k.startsWith("Knee") ? 1 : -1); v.sub(ax.clone().multiplyScalar(v.dot(ax))); }
  return mid.clone().add(v.normalize().multiplyScalar(0.8 * mid.distanceTo(a)));
}
function placePoles() {
  if (!model || !B.Root_M) return;
  const show = $("tJoints").classList.contains("on"), pxW = 2 * Math.tan(THREE.MathUtils.degToRad(CAM().fov) / 2) / Math.max(1, canvas.clientHeight);
  for (const k of Object.keys(POLE_NAMES)) {
    let o = POLES[k];
    if (!o) {
      const mesh = new THREE.Mesh(new THREE.OctahedronGeometry(1), new THREE.MeshBasicMaterial({ color: 0xffa63d, depthTest: false, transparent: true, opacity: .9 }));
      mesh.renderOrder = 12;
      const line = new THREE.Line(new THREE.BufferGeometry().setFromPoints([new V3(), new V3()]), new THREE.LineBasicMaterial({ color: 0xffa63d, depthTest: false, transparent: true, opacity: .55 }));
      line.renderOrder = 9; overlay.add(mesh, line);
      const handle = new THREE.Object3D(); scene.add(handle);
      o = POLES[k] = { mesh, line, handle };
    }
    const pt = polePoint(k), vis = show && !!pt;
    o.mesh.visible = o.line.visible = vis; if (!vis) continue;
    if (!gizmo.dragging || poleSel !== k) o.handle.position.copy(pt);
    const pos = o.handle.position, mid = wp(B[poleChain(k)[1]]);
    o.mesh.position.copy(pos); o.mesh.scale.setScalar(pxAt(CAM().position.distanceTo(pos)) * 6 * (poleSel === k ? 1.5 : 1));
    o.mesh.material.color.set(poleSel === k ? 0xffe0a0 : 0xffa63d);
    o.line.geometry.setFromPoints([mid, pos]);
  }
}
function pickPole(x, y) {
  let best = null, bd = 14;
  for (const [k, o] of Object.entries(POLES)) {
    if (!o.mesh.visible) continue;
    const sp = toScreen(o.mesh.position); if (!sp.front) continue;
    const d = Math.hypot(sp.x - x, sp.y - y); if (d < bd) { best = k; bd = d; }
  }
  return best;
}
function selectPole(k) {
  setSelection([], null); poleSel = k;
  gizmo.setMode("translate"); gizmo.attach(POLES[k].handle);
  $("p_status").textContent = POLE_NAMES[k] + ": kéo để xoay " + (k.startsWith("Knee") ? "gối quanh trục hông → cổ chân" : "khuỷu quanh trục vai → cổ tay") + ", bàn " + (k.startsWith("Knee") ? "chân" : "tay") + " giữ nguyên chỗ.";
  refresh();
}
function poleDrag(k) {
  const ch = poleChain(k), [h, m, e] = ch.map(n => B[n]); model.updateMatrixWorld(true);
  const a = wp(h), ax = wp(e).sub(a); if (ax.lengthSq() < 1e-10) return; ax.normalize();
  const perp = p => { const v = p.clone().sub(a); return v.sub(ax.clone().multiplyScalar(v.dot(ax))); };
  const cur = perp(wp(m)), tgt = perp(POLES[k].handle.position);
  if (cur.lengthSq() < 1e-8 || tgt.lengthSq() < 1e-8) return;
  cur.normalize(); tgt.normalize();
  let ang = Math.acos(Math.min(1, Math.max(-1, cur.dot(tgt)))); if (new V3().crossVectors(cur, tgt).dot(ax) < 0) ang = -ang;
  const endQ = wq(e);
  rotateWorld(h, new Q().setFromAxisAngle(ax, ang)); setWorldQuat(e, endQ); model.updateMatrixWorld(true);
  ch.forEach(n => edited.add(n));
  if (k.startsWith("Knee")) captureFeet(); else { const sv = sel; sel = ch[1]; followEdit(); sel = sv; }
  refresh();
}
let FREL = null;            // prop / grip relation taken at rebase (each frame change, each key)
function followGrab() {
  if (!hasFollow()) { FREL = null; return; }
  model.updateMatrixWorld(true);
  const c = P.follow, Wp = B[c.prop].matrixWorld;
  FREL = { w: B[c.to].matrixWorld.clone().invert().multiply(Wp), h: Wp.clone().invert().multiply(B[ARMS[c.hand][2]].matrixWorld) };
}
function followEdit() {     // after an edit: the prop rides its bone; editing the prop moves the hand; editing the arm moves the grip
  if (!FREL || !hasFollow()) return;
  const c = P.follow, arm = ARMS[c.hand];
  if (sel === c.prop) { FREL.w = B[c.to].matrixWorld.clone().invert().multiply(B[c.prop].matrixWorld); propHandTo(B[c.prop].matrixWorld.clone(), FREL.h); }
  else if (arm.includes(sel)) FREL.h = B[c.prop].matrixWorld.clone().invert().multiply(B[arm[2]].matrixWorld);
  else propHandTo(B[c.to].matrixWorld.clone().multiply(FREL.w), FREL.h);
  edited.add(c.prop); arm.forEach(n => edited.add(n));
}
function afterEdit() {      // a joint was rotated / the hip moved (gizmo or Channel Box)
  {
    edited.add(sel);
    if (sel === GUN) gunFollowHand();
    if (sel === "Root_M" && lockFeet) { solveLeg("L"); solveLeg("R"); }
    else if (LEGS.L.includes(sel) || LEGS.R.includes(sel)) captureFeet();   // FK edit on a leg moves its foot target
    else if (lockFeet && sel === "Spine1_M") {}                              // upper body: feet untouched
    followEdit();
  }
  refresh();
}
$("tLock").onclick = () => { lockFeet = !lockFeet; $("tLock").classList.toggle("on", lockFeet); };
$("tGunR").onclick = () => { gunFollow = !gunFollow; $("tGunR").classList.toggle("on", gunFollow); };
$("tGhost").onclick = () => { const on = !$("tGhost").classList.contains("on"); $("tGhost").classList.toggle("on", on); if (ghost) ghost.visible = on && ONION.mode === "orig"; goto(frame); };
(function () {   // ô nhập frame cho bóng mờ cạnh nút (như Ghost Options → custom frames của Maya)
  const b = $("tGhost"); if (!b || $("tGhostF")) return;
  const s = document.createElement("input"); s.id = "tGhostF"; s.type = "text"; s.inputMode = "numeric"; s.className = "ghostf";
  s.style.cssText = "height:28px;width:72px;margin:0 4px 0 2px;font-size:12px;padding:0 6px";
  s.placeholder = "F: 1, 7"; s.value = ONION.frames;
  s.title = "Bóng mờ (như Ghost của Maya): gõ frame cần hiện pose, vd 1 hoặc 1, 7 rồi Enter. Trước frame đang xem = cam, sau = xanh. Để trống = key ngay trước + ngay sau";
  const apply = () => { ONION.frames = s.value.trim(); try { localStorage.setItem("pl:onionF", ONION.frames); } catch (e) {} if (!b.classList.contains("on")) b.click(); else goto(frame); };
  s.addEventListener("change", apply);
  s.addEventListener("keydown", e => { e.stopPropagation(); if (e.key === "Enter") { apply(); s.blur(); } });   // phím gõ không chạy phím tắt của Pose
  b.after(s);
})();
$("tJoints").onclick = () => $("tJoints").classList.toggle("on");
$("tTrail").onclick = () => { trailOn = !trailOn; $("tTrail").classList.toggle("on", trailOn); trailSig = ""; if (!trailOn) trailClear(); };
$("undo").onclick = () => { const sn = undoStack.pop(); if (sn) restore(sn); };
$("resetAll").onclick = () => { if (!model) return; pushUndo(); for (const n of Object.keys(B)) { B[n].quaternion.copy(base[n].lq); B[n].position.copy(base[n].lp); } model.updateMatrixWorld(true); edited.clear(); delete drafts[frame]; captureFeet(); attachGizmo(); refresh(); };
$("resetJoint").onclick = () => {
  if (!sel) return; pushUndo();
  for (const n of selSet) { B[n].quaternion.copy(base[n].lq); B[n].position.copy(base[n].lp); edited.delete(n); }
  model.updateMatrixWorld(true);
  if (selSet.has("Root_M") && lockFeet) { solveLeg("L"); solveLeg("R"); }
  attachGizmo(); refresh(); commitEdit();
};
document.addEventListener("keydown", e => {
  if (!host.alive()) return;
  if (e.target.matches && e.target.matches("textarea, input")) return;
  const k = e.key.toLowerCase();
  if (e.key === "Alt") { e.preventDefault(); return; }        // keep the browser menu bar from taking the focus
  if (e.ctrlKey || e.metaKey) {
    if (k === "z") { e.preventDefault(); $("undo").click(); }
    else if (k === "c") { e.preventDefault(); copyKey(e.shiftKey); }
    else if (k === "v") { e.preventDefault(); e.shiftKey ? pasteHold() : pasteKey(); }
    return;
  }
  if (k === "s" && keysMode()) { $("kSet").click(); return; }
  if (e.key === "Delete" && keysMode()) { $("kDel").click(); return; }
  if (k === "g" && P && P.ref) { $("tRef").click(); return; }
  if (k === "[") { $("tList").click(); return; }
  if (k === "]") { $("tSide").click(); return; }
  if (k === "q") setMode("select"); else if (k === "w") setMode("translate"); else if (k === "e") setMode("rotate");
  else if (k === "r") $("mScale").click();
  else if (k === "f") frameSel(); else if (k === "a") frameAll();
  else if (k === "+" || k === "=") gizmo.setSize(Math.min(3, gizmo.size * 1.2));
  else if (k === "-" || k === "_") gizmo.setSize(Math.max(0.3, gizmo.size / 1.2));
  else if (e.key === "ArrowUp" && sel) { e.preventDefault(); pickwalk(-1); }
  else if (e.key === "ArrowDown" && sel) { e.preventDefault(); pickwalk(1); }
  else if (k === "," || k === ".") { stopPlay(); (e.altKey ? (k === "," ? $("prevF") : $("nextF")) : (k === "," ? $("prevKey") : $("nextKey"))).click(); }
  else if (k === "x") $("mSpace").click(); else if (k === "j") $("tJoints").click(); else if (k === "t") $("tTrail").click();
  else if (k === "escape") select(null);
  else if ((e.ctrlKey || e.metaKey) && k === "z") { e.preventDefault(); $("undo").click(); }
  else if ("1234567".includes(k)) setCam(["right", "front", "top", "persp", "left", "back", "bottom"][+k - 1]);
  else if (e.key === "ArrowLeft") { e.preventDefault(); (e.shiftKey ? $("prevKey") : $("prevF")).click(); }
  else if (e.key === "ArrowRight") { e.preventDefault(); (e.shiftKey ? $("nextKey") : $("nextF")).click(); }
  else if (e.key === " ") { e.preventDefault(); $("play").click(); }
});

// ---------------------------------------------------------------- Maya: framing, pickwalk
function frameAt(t, dist) {
  const dir = CAM().position.clone().sub(orbit.target).normalize();
  orbit.target.copy(t); CAM().position.copy(t.clone().add(dir.multiplyScalar(dist))); orbit.update();
}
function frameSel() { if (model && sel) frameAt(wp(B[sel]), 1.6); }
function frameAll() { if (model) frameAt(new V3(0, 0.9 * camFit, 0), 6.5 * camFit); }
function pickwalk(dir) {     // up = parent joint, down = first child joint (joints with a marker only)
  let n = null;
  if (dir < 0) { for (let o = B[sel].parent; o; o = o.parent) if (markers[o.name]) { n = o.name; break; } }
  else { const q = [...B[sel].children]; while (q.length && !n) { const o = q.shift(); if (markers[o.name]) n = o.name; else q.push(...o.children); } }
  if (n) select(n);
}

// ---------------------------------------------------------------- copy / paste key
// Copy = the local pose (as now on screen, edits included) of the selected joint (Shift: + its child joints), or of
// every joint when nothing is selected. Paste = onto the current frame as an edit (red dot), saved like any edit.
// Only the joints with a handle are copied: those are the ones the Blender side applies.
let keyClip = null;
function copyKey(withChildren) {
  if (!model) return;
  const picked = [...selSet];
  let names = picked.length ? [...picked] : JOINTS.filter(n => B[n]);
  if (picked.length && withChildren) for (const n0 of picked) B[n0].traverse(o => { if (o !== B[n0] && markers[o.name] && !names.includes(o.name)) names.push(o.name); });
  keyClip = { from: frame, sel, withChildren: !!(picked.length && withChildren),
              bones: Object.fromEntries(names.map(n => [n, [B[n].position.clone(), B[n].quaternion.clone()]])) };
  const what = !picked.length ? "cả người" : (picked.length > 1 ? picked.length + " khớp" : (NAMES[sel] || sel)) + (withChildren ? " + khớp con" : "");
  $("clipInfo").textContent = "Đã copy F" + frame + ": " + what;
  $("p_status").textContent = "Đã copy pose " + what + " ở F" + frame + ". Sang frame khác rồi bấm Paste (Ctrl+V).";
  refresh();
}
function pasteHere() {
  const names = Object.keys(keyClip.bones);
  for (const n of names) { B[n].position.copy(keyClip.bones[n][0]); B[n].quaternion.copy(keyClip.bones[n][1]); edited.add(n); }
  model.updateMatrixWorld(true);
  const legs = names.some(n => LEGS.L.includes(n) || LEGS.R.includes(n));
  if (legs) captureFeet();
  else if (names.includes("Root_M") && lockFeet) { solveLeg("L"); solveLeg("R"); }   // hip pasted, feet stay planted
  return names.length;
}
function pasteKey() {
  if (!model || !keyClip) return;
  stopPlay(); pushUndo(); const n = pasteHere(); attachGizmo(); refresh();
  $("p_status").textContent = "Đã paste " + n + " khớp từ F" + keyClip.from + " vào F" + frame + ". " +
    (keysMode() ? (autoKey ? "Đã đặt key." : "Bấm ◆ Key (S) để giữ.") : "Bấm \"Lưu điều chỉnh\" để giữ.");
  commitEdit();
}
function pasteHold() {    // hold the copied pose from here up to the frame before the next key (stepped blocking)
  if (!model || !keyClip) return;
  if (keysMode()) { pasteKey(); return; }     // page keys: a key holds by itself in stepped mode
  stopPlay();
  const f0 = frame, nk = (P.keys || []).find(f => f > f0) || (P.frames || 1) + 1, last = Math.max(f0, nk - 1);
  for (let f = f0; f <= last; f++) { if (f !== frame) goto(f); pasteHere(); }
  goto(f0); attachGizmo(); refresh();
  $("p_status").textContent = "Đã paste pose F" + keyClip.from + " vào F" + f0 + (last > f0 ? "–F" + last : "") + ". Bấm \"Lưu điều chỉnh\" để lưu cả các frame này.";
}
$("copyKey").onclick = e => copyKey(e.shiftKey);
$("pasteKey").onclick = e => (e.shiftKey ? pasteHold() : pasteKey());
$("pasteHold").onclick = () => pasteHold();

// ---------------------------------------------------------------- Channel Box
// Rotate X/Y/Z = degrees about the joint's own local axes, relative to the original pose of this frame (0 = untouched).
// Translate X/Y/Z (hip, feet) = cm in Blender world axes (X, Y, Z up) from the original position.
const CH_R = ["Rotate X", "Rotate Y", "Rotate Z"], CH_T = ["Translate X", "Translate Y", "Translate Z"];
let cbFor = null, cbDrag = null;
function chanRot(n) {
  const e = new THREE.Euler().setFromQuaternion(base[n].lq.clone().invert().multiply(B[n].quaternion), "XYZ");
  return [e.x, e.y, e.z].map(THREE.MathUtils.radToDeg);
}
function setRot(n, v) {
  const d = new Q().setFromEuler(new THREE.Euler(...v.map(THREE.MathUtils.degToRad), "XYZ"));
  B[n].quaternion.copy(base[n].lq.clone().multiply(d)); model.updateMatrixWorld(true);
}
const posNow = n => n.startsWith("Ankle_") ? footT[n.slice(-1)].clone() : wp(B[n]);
function chanPos(n) { const d = posNow(n).sub(base[n].p); return [d.x * 100, -d.z * 100, d.y * 100]; }
function setPos(n, v) {
  const t = base[n].p.clone().add(new V3(v[0], v[2], -v[1]).multiplyScalar(0.01));
  if (n.startsWith("Ankle_")) { footT[n.slice(-1)] = t; solveLeg(n.slice(-1)); return; }
  if (isWrist(n)) { const s = n.slice(-1); handQ[s] = wq(B[n]); solveArm(s, t); return; }
  if (n === GUN) gunGrab();
  B[n].parent.updateMatrixWorld(true); B[n].position.copy(B[n].parent.worldToLocal(t)); model.updateMatrixWorld(true);
}
function cbSet(kind, i, val) {
  if (!sel || !Number.isFinite(val)) return;
  if (kind === "r") { const v = chanRot(sel); v[i] = val; if (sel === GUN) gunGrab(); setRot(sel, v); afterEdit(); }
  else { const v = chanPos(sel); v[i] = val; setPos(sel, v); if (sel.startsWith("Ankle_") || isWrist(sel)) refresh(); else afterEdit(); }
  attachGizmo();
}
function buildCB() {
  const cb = $("cb"); cb.innerHTML = ""; cbFor = sel; cb.hidden = !sel || !model;
  if (cb.hidden) return;
  const rows = [["r", CH_R, "Xoay (độ, trục local của khớp, so với pose gốc)"]];
  if (canMove(sel)) rows.push(["t", CH_T, "Dời (cm, trục Blender, so với pose gốc)"]);
  for (const [kind, names, hd] of rows) {
    const h = document.createElement("div"); h.className = "hd"; h.textContent = hd; cb.append(h);
    names.forEach((nm, i) => {
      const l = document.createElement("div"); l.className = "lbl"; l.textContent = nm; l.title = "Kéo ngang để chỉnh (Shift chậm, Ctrl nhanh)";
      const inp = document.createElement("input"); inp.type = "text"; inp.inputMode = "decimal"; inp.dataset.k = kind; inp.dataset.i = i;
      inp.setAttribute("aria-label", nm);
      inp.addEventListener("keydown", e => {
        if (e.key === "Enter") { pushUndo(); cbSet(kind, i, parseFloat(inp.value.replace(",", "."))); commitEdit(); inp.select(); }
        else if (e.key === "Escape") { inp.blur(); }
        else if (e.key === "ArrowUp" || e.key === "ArrowDown") {
          e.preventDefault(); pushUndo();
          const nv = (parseFloat(inp.value.replace(",", ".")) || 0) + (e.key === "ArrowUp" ? 1 : -1) * (e.shiftKey ? 0.1 : e.ctrlKey ? 10 : 1);
          cbSet(kind, i, nv); commitEdit(); inp.value = nv.toFixed(2);
        }
      });
      inp.addEventListener("blur", () => refresh());
      l.addEventListener("pointerdown", e => {
        if (!sel) return; e.preventDefault(); l.setPointerCapture(e.pointerId); l.classList.add("drag"); stopPlay(); pushUndo();
        cbDrag = { kind, i, x0: e.clientX, v0: (kind === "r" ? chanRot(sel) : chanPos(sel))[i] };
      });
      l.addEventListener("pointermove", e => {
        if (!cbDrag || cbDrag.kind !== kind || cbDrag.i !== i) return;
        const step = (kind === "r" ? 0.5 : 0.1) * (e.shiftKey ? 0.2 : e.ctrlKey ? 5 : 1);
        cbSet(kind, i, cbDrag.v0 + (e.clientX - cbDrag.x0) * step);
      });
      const end = () => { if (cbDrag) commitEdit(); cbDrag = null; l.classList.remove("drag"); };
      l.addEventListener("pointerup", end); l.addEventListener("pointercancel", end);
      cb.append(l, inp);
    });
  }
}
function renderCB() {
  if (cbFor !== sel || $("cb").hidden !== !(sel && model)) buildCB();
  if (!sel || !model) return;
  const vals = { r: chanRot(sel), t: canMove(sel) ? chanPos(sel) : null };
  for (const inp of $("cb").querySelectorAll("input")) {
    if (inp === document.activeElement) continue;
    const v = vals[inp.dataset.k][+inp.dataset.i];
    inp.value = (Math.abs(v) < 0.005 ? 0 : v).toFixed(2);
    inp.classList.toggle("chg", Math.abs(v) >= 0.005);
  }
}

// ---------------------------------------------------------------- what changed
function deltaDeg(n) { return THREE.MathUtils.radToDeg(2 * Math.acos(Math.min(1, Math.abs(wq(B[n]).multiply(base[n].q.clone().invert()).w)))); }
function localDeg(n) { return THREE.MathUtils.radToDeg(B[n].quaternion.angleTo(base[n].lq)); }
function changed(n) { return localDeg(n) > 0.2 || B[n].position.distanceTo(base[n].lp) > 1e-4; }
function editedList() { return [...edited].filter(n => B[n] && changed(n)); }
function refresh() {
  placeMarkers();
  const list = editedList();
  $("changes").innerHTML = "";
  for (const n of list) {
    const d = document.createElement("div"), a = document.createElement("span"), b = document.createElement("span");
    a.textContent = NAMES[n] || n;
    b.textContent = n === "Root_M" && B[n].position.distanceTo(base[n].lp) > 1e-4
      ? localDeg(n).toFixed(1) + "° · " + (wp(B[n]).distanceTo(base[n].p) * 100).toFixed(1) + " cm" : localDeg(n).toFixed(1) + "°";
    d.append(a, b); $("changes").append(d);
  }
  $("selName").textContent = !sel ? (poleSel ? POLE_NAMES[poleSel] : "Chưa chọn khớp") : selSet.size > 1 ? selSet.size + " khớp · gizmo: " + (NAMES[sel] || sel) : (NAMES[sel] || sel);
  renderCB();
  $("selHint").textContent = !sel ? "Bấm vào một khớp, hoặc kéo quét một vùng để chọn nhiều. Giữ Shift để chọn thêm." :
    selSet.size > 1 ? "Đang chọn " + [...selSet].map(n => NAMES[n] || n).join(", ") + ". Xoay (E): các khớp cùng xoay theo gizmo. Ctrl+C copy tất cả." :
    MOVABLE.has(sel) ? (sel === "Root_M" ? "Xoay (E) hoặc dời hông (W). Khóa chân giữ hai bàn chân trên sàn."
      : sel === GUN ? "Dời (W) / xoay (E) súng. Bật \"Tay phải bám súng\" để tay phải giữ chỗ cầm."
      : isWrist(sel) ? "Dời (W) để kéo bàn tay, vai và khuỷu tự gập theo IK, hướng bàn tay giữ nguyên. Xoay (E) để xoay cổ tay."
      : "Dời (W) để kéo bàn chân, gối tự gập theo IK. Xoay (E) để đổi hướng bàn chân.")
    : "Xoay (E) hoặc dời (W) khớp, hoặc chỉnh trong Channel Box. X đổi trục local/world, ↑ ↓ sang khớp cha / con.";
  $("resetJoint").disabled = !sel || ![...selSet].some(changed);
  $("resetJoint").textContent = selSet.size > 1 ? "Trả " + selSet.size + " khớp về gốc" : "Trả khớp này về gốc";
  const tag = $("selTag"); tag.hidden = !sel;
  if (sel) tag.textContent = (NAMES[sel] || sel) + (changed(sel) ? " · " + localDeg(sel).toFixed(1) + "°" : "");
  renderStrip();
  const nf = draftFrames().length;
  // outside claude.ai (local preview) there is no db: the button downloads the adjustments as a .json file instead
  // (user 2026-10-22 "Sao ko lưu được pose đã chỉnh": edited on localhost, the button stayed disabled)
  if (keysMode()) {          // page keys: the button keys every edited frame and keeps the note for the AI
    const txt = $("text").value.trim();
    $("save").textContent = nf ? "Đặt key " + nf + " frame" + (txt ? " + lưu ghi chú" : "") : "Lưu ghi chú";
    $("save").disabled = (db && !canWrite) || (!nf && !((txt || DV.strokes.length) && db));
    $("save").title = "Key lưu thẳng trên trang. Ghi chú gửi kèm cho AI ở frame đang xem.";
  } else {
  $("save").textContent = (db ? "Lưu điều chỉnh" : "Tải file điều chỉnh") + (nf > 1 ? " (" + nf + " frame)" : "");
  $("save").disabled = (db && !canWrite) || !nf;
  $("save").title = !nf ? "Chưa chỉnh khớp nào" : !db ? "Trang đang mở ngoài claude.ai: tải file .json rồi gửi cho AI" : "";
  }
  if (keysMode()) {
    $("kDel").disabled = !KEYS.has(cyc(frame)) || KEYS.size <= 1;
    $("kAuto").textContent = "Auto key: " + (autoKey ? "bật" : "tắt"); $("kAuto").classList.toggle("on", autoKey);
    $("kInterp").textContent = ANIM.interp === "step" ? "Bậc thang" : "Spline";
    $("kLock").textContent = "Bám sàn: " + (ANIM.lock ? "bật" : "tắt");
  }
  $("pasteKey").disabled = $("pasteHold").disabled = !keyClip || !model;
}

// ---------------------------------------------------------------- export for Blender
// glTF world (Y up) -> Blender world (Z up): (x, y, z) -> (x, -z, y); quaternions keep w, axis maps the same way.
const toBl = v => [+v.x.toFixed(5), +(-v.z).toFixed(5), +v.y.toFixed(5)];
const qToBl = q => [+q.w.toFixed(6), +q.x.toFixed(6), +(-q.z).toFixed(6), +q.y.toFixed(6)];
function buildAdjust() {
  const bones = {}, local = {};
  const list = editedList();
  if (B[GUN] && !list.includes(GUN) && list.length && (deltaDeg(GUN) > 0.2 || wp(B[GUN]).distanceTo(base[GUN].p) > 1e-4)) list.push(GUN);
  for (const n of list) {
    const dq = wq(B[n]).multiply(base[n].q.clone().invert());
    bones[n] = { dq: qToBl(dq), deg: +deltaDeg(n).toFixed(2) };
    local[n] = { q: B[n].quaternion.toArray().map(x => +x.toFixed(6)), p: B[n].position.toArray().map(x => +x.toFixed(4)) };
  }
  const root = { dp: toBl(wp(B.Root_M).sub(base.Root_M.p)) };
  if (bones[GUN]) bones[GUN].dp = toBl(wp(B[GUN]).sub(base[GUN].p));     // gun head moved (world, Blender axes)
  const legs = {};
  for (const s of ["L", "R"]) legs[s] = { ankle: toBl(wp(B[LEGS[s][2]])), knee: toBl(wp(B[LEGS[s][1]])),
    ankleDq: qToBl(wq(B[LEGS[s][2]]).multiply(base[LEGS[s][2]].q.clone().invert())) };
  return { bones, local, root, legs };
}

// ---------------------------------------------------------------- db: adjusts + rounds
let db = null, user = null, comments = null, myId = null, canWrite = true, adjs = [], rounds = {}, armed = false;
const mine = () => adjs.filter(a => a.clip === P.clip && a.version === P.version);
function fmtTime(s) { try { return new Date(s).toLocaleString("vi-VN", { hour: "2-digit", minute: "2-digit", day: "2-digit", month: "2-digit" }); } catch { return s; } }
function fail(e) {
  const c = e && e.code;
  if (c === "invalid_argument" || c === "permission_denied") { canWrite = false; $("p_status").textContent = "Bạn đang ở quyền chỉ xem nên không lưu được. Nhờ chủ trang cấp quyền Contributor."; }
  else if (c === "quota_exceeded") $("p_status").textContent = "Kho điều chỉnh đã đầy. Xoá bớt điều chỉnh đã sửa.";
  else $("p_status").textContent = "Chưa lưu được, thử lại sau ít giây.";
  refresh();
}
function draftFrames() {    // frames with unsaved edits: the stashed ones + this frame
  const fs = new Set(Object.keys(drafts).map(Number));
  if (model && editedList().length) fs.add(frame); else fs.delete(frame);
  return [...fs].sort((a, b) => a - b);
}
$("text").addEventListener("input", () => { if (keysMode()) refresh(); });
$("save").onclick = async () => {
  if (!model) return;
  if (keysMode()) { saveKeysMode(); return; }
  const fs = draftFrames(); if (!fs.length) return;
  $("save").disabled = true; $("p_status").textContent = "Đang lưu…";
  stashDraft();
  const cur = frame, text = $("text").value.trim(), saved = [], offline = [];
  for (const f of fs) {          // one adjust doc per frame, each against that frame's original pose
    goto(f, true);
    const body = { clip: P.clip, version: P.version, frame: f, ...buildAdjust(), text, status: "open", createdAt: new Date().toISOString() };
    if (myId) body.author = myId;
    if (!db) { offline.push(body); saved.push(f); continue; }
    try { await db.collection("adjusts").add(body); delete drafts[f]; saved.push(f); adjs.push({ ...body }); }   // shown at once, the snapshot replaces it
    catch (e) { fail(e); break; }
  }
  goto(cur, true);                 // the saved edits now show as this frame's pose (savedOverlay)
  if (!db) {                       // keep the edits on screen (drafts stay) and hand the file over
    const a = document.createElement("a");
    a.href = URL.createObjectURL(new Blob([JSON.stringify(offline, null, 1)], { type: "application/json" }));
    a.download = P.clip + "_" + P.version + "_adjusts_" + saved.map(f => "F" + f).join("-") + ".json"; a.click();
    $("p_status").textContent = "Đã tải file điều chỉnh " + saved.map(f => "F" + f).join(", ") + ". Gửi file cho AI, hoặc mở trang trên claude.ai để lưu thẳng.";
    refresh(); return;
  }
  if (saved.length) { $("text").value = "";
    $("p_status").textContent = "Đã lưu điều chỉnh ở " + saved.map(f => "F" + f).join(", ") + ". Bấm \"Gửi cho AI\" khi review xong."; }
  refresh();
};
async function renderAdjs() {
  renderStrip();
  const list = mine().sort((a, b) => ((a.frame || 1) - (b.frame || 1)) || (a.createdAt || "").localeCompare(b.createdAt || ""));
  $("adjCount").textContent = list.length ? list.length + "" : "";
  $("adjEmpty").hidden = list.length > 0;
  const ids = [...new Set(list.map(a => a.author).filter(Boolean))];
  const ps = user && ids.length ? await user.profiles(ids).catch(() => ({})) : {};
  const box = $("adjs"); box.innerHTML = "";
  for (const a of list) {
    const el = document.createElement("div"); el.className = "adj" + (a.status === "done" ? " done" : "");
    const meta = document.createElement("div"); meta.className = "meta";
    const who = document.createElement("span"); who.textContent = "F" + (a.frame || 1) + " · " + ((a.author && ps[a.author] && ps[a.author].name) || "Ai đó") + " · " + fmtTime(a.createdAt);
    const pill = document.createElement("span"); pill.className = "pill" + (a.status === "done" ? " done" : ""); pill.textContent = a.status === "done" ? "AI đã áp" : "chờ AI";
    meta.append(who, pill);
    const bones = document.createElement("div"); bones.className = "bones";
    bones.textContent = Object.entries(a.bones || {}).map(([n, v]) => (NAMES[n] || n) + " " + (v.deg ?? 0).toFixed(1) + "°").join(" · ");
    el.append(meta, bones);
    if (a.text) { const p = document.createElement("p"); p.textContent = a.text; el.append(p); }
    for (const g of (a.imgs && a.imgs.length ? a.imgs : a.img ? [a.img] : [])) if (g && g.url) { const im = document.createElement("img"); im.className = "adjimg"; im.loading = "lazy"; im.src = g.url; im.alt = "Ảnh ghi chú F" + (a.frame || 1); im.onclick = () => window.open(g.url, "_blank"); el.append(im); }
    const row = document.createElement("div"); row.className = "row";
    // bấm vào mục (không phải nút / ô sửa / ảnh) = nhảy tới frame, áp điều chỉnh, về góc CAM() lúc ghi (thay nút "Xem trên model")
    el.style.cursor = "pointer"; el.title = "Bấm để tới F" + (a.frame || 1) + " và xem điều chỉnh trên model";
    el.onclick = e => { if (e.target.closest("button,textarea,img,a")) return;
      applyLocal(a); if (a.cam && a.cam.pos) { CAM().position.fromArray(a.cam.pos); orbit.target.fromArray(a.cam.target); orbit.update(); } };
    if (a.id && db && canWrite && (!a.author || a.author === myId || (user && user.canEdit && user.canEdit()))) {
      // Sửa lời ghi chú tại chỗ (user 2026-10-29 "các fb cần có tính năng xóa, sửa"); mục không ghi người tạo (Studio trên máy) cũng sửa / xoá được
      const ed = document.createElement("button"); ed.className = "btn"; ed.textContent = "Sửa";
      ed.onclick = () => {
        const ta = document.createElement("textarea"); ta.value = a.text || ""; ta.rows = 3; ta.style.cssText = "width:100%;margin:4px 0";
        const ok = document.createElement("button"); ok.className = "btn primary"; ok.textContent = "Lưu";
        const no = document.createElement("button"); no.className = "btn"; no.textContent = "Huỷ";
        const r2 = document.createElement("div"); r2.className = "row"; r2.append(ok, no);
        ta.addEventListener("keydown", e => e.stopPropagation());   // gõ chữ không chạy phím tắt Pose
        no.onclick = () => renderAdjs();
        ok.onclick = async () => { const { id, ...rest } = a; rest.text = ta.value.trim(); rest.editedAt = new Date().toISOString();
          try { await db.doc("adjusts/" + a.id).set(rest); a.text = rest.text; } catch (e) { fail(e); } renderAdjs(); };
        el.querySelector("p") ? el.querySelector("p").replaceWith(ta) : el.insertBefore(ta, row); row.replaceWith(r2); ta.focus();
      };
      row.append(ed);
      const del = document.createElement("button"); del.className = "btn"; del.textContent = "Xoá";
      del.onclick = () => { if (del.dataset.arm) db.doc("adjusts/" + a.id).delete().catch(fail); else { del.dataset.arm = 1; del.textContent = "Bấm lần nữa để xoá"; } };
      row.append(del);
    }
    if (row.children.length) {   // menu ⋯ ở góc dòng đầu thay hàng nút (user 2026-10-29)
      el.style.position = "relative";
      const kb = document.createElement("button"); kb.className = "btn akebab"; kb.textContent = "⋯"; kb.title = "Sửa / Xoá"; kb.setAttribute("aria-label", "Sửa hoặc xoá");
      kb.style.cssText = "padding:0 8px;min-height:0;height:22px;line-height:20px;font-size:16px;margin-left:6px;background:transparent;border:0;cursor:pointer;color:inherit";
      row.hidden = true; row.style.cssText = "position:fixed;z-index:50;min-width:90px;flex-direction:column;align-items:stretch;gap:4px;padding:6px;background:var(--panel,#1f2430);border:1px solid var(--line,#333);border-radius:8px;box-shadow:0 6px 18px rgba(0,0,0,.4)";
      // menu nổi (fixed) theo vị trí nút ⋯: khung cuộn của panel không cắt mất; bấm ra ngoài / cuộn thì đóng
      const close = () => { row.hidden = true; row.style.display = "none"; document.removeEventListener("pointerdown", outside, true); };
      const outside = e => { if (!row.contains(e.target) && e.target !== kb) close(); };
      kb.onclick = e => { e.stopPropagation(); if (!row.hidden) return close();
        const r = kb.getBoundingClientRect(); row.hidden = false; row.style.display = "flex";
        row.style.top = Math.min(r.bottom + 4, innerHeight - row.offsetHeight - 8) + "px"; row.style.left = Math.max(8, r.right - row.offsetWidth) + "px";
        document.addEventListener("pointerdown", outside, true); };
      row.style.display = "none";
      row.addEventListener("click", e => e.stopPropagation());
      for (const b of row.querySelectorAll("button")) { const f = b.onclick; if (b.textContent === "Sửa") b.onclick = ev => { row.style.cssText = ""; row.hidden = false; kb.remove(); f(ev); }; }
      const grp = document.createElement("span"); grp.style.cssText = "display:inline-flex;align-items:center;gap:2px"; pill.replaceWith(grp); grp.append(kb, pill);   // ⋯ ngay trước nhãn trạng thái
    }
    el.append(row); box.append(el);
  }
}
function applyLocal(a) {
  if (!model) return; stopPlay(); goto(a.frame || 1); pushUndo();
  for (const n of Object.keys(B)) { B[n].quaternion.copy(base[n].lq); B[n].position.copy(base[n].lp); }
  edited.clear();
  for (const [n, v] of Object.entries(a.local || {})) if (B[n]) { B[n].quaternion.fromArray(v.q); B[n].position.fromArray(v.p); edited.add(n); }
  model.updateMatrixWorld(true); captureFeet(); attachGizmo(); refresh();
  $("p_status").textContent = "Đang xem điều chỉnh này ở F" + (a.frame || 1) + ". Bấm \"Về pose gốc\" để bỏ.";
}

const roundId = () => (P.clip + "-" + P.version).replace(/[^A-Za-z0-9_\-.]/g, "_");
async function renderRound() {
  const r = rounds[roundId()], open = mine().filter(a => a.status !== "done"), btn = $("aiSend");
  $("round").dataset.s = r ? r.status : "none";
  let who = "";
  if (r && r.sentBy && user) { const ps = await user.profiles([r.sentBy]).catch(() => ({})); who = (ps[r.sentBy] && ps[r.sentBy].name) || ""; }
  if (!r) { $("roundTxt").textContent = "Vòng review đang mở: lưu điều chỉnh xong thì gửi cho AI."; $("roundSub").textContent = open.length + " điều chỉnh chờ AI"; }
  else if (r.status === "sent") { $("roundTxt").textContent = "Đã gửi cho AI, đang chờ nhận việc"; $("roundSub").textContent = (who ? who + " · " : "") + fmtTime(r.sentAt) + " · " + (r.adjustCount || 0) + " điều chỉnh"; }
  else if (r.status === "working") { $("roundTxt").textContent = "AI đang áp điều chỉnh vào Blender"; $("roundSub").textContent = r.aiNote || ""; }
  else { $("roundTxt").textContent = "AI đã áp xong vòng này"; $("roundSub").textContent = r.aiNote || ""; }
  btn.textContent = armed ? "Xác nhận gửi " + open.length + " điều chỉnh" : (r && r.status !== "fixed" ? "Gửi lại cho AI" : "Gửi cho AI");
  btn.classList.toggle("arm", armed);
  btn.disabled = !db || !canWrite || !open.length;
}
$("aiSend").onclick = async () => {
  const open = mine().filter(a => a.status !== "done");
  if (!armed) { armed = true; renderRound(); setTimeout(() => { armed = false; renderRound(); }, 6000); return; }
  armed = false; $("aiSend").disabled = true; $("p_status").textContent = "Đang gửi cho AI…";
  let toClaude = false;
  try {
    if (comments && (await comments.canSendToClaude().catch(() => "off")) === "available") {
      const anchor = await comments.anchorFor($("aiSend"));
      const fr = [...new Set(open.map(a => a.frame || 1))].sort((a, b) => a - b).join(", ");
      await comments.sendToClaude({ anchor, text: `Pose Lab: ${open.length} điều chỉnh pose cho ${P.clip} ${P.version} (frame ${fr}). ` +
        `Đọc collection "adjusts" (clip ${P.clip}, version ${P.version}) rồi áp vào pose (ảnh ghi chú ở trường img.url, CAM() ở cam).` +
        (AIS.on ? ` Bật AI tự xem lại ${AIS.rounds} vòng: ra version mới thì trang tự xem lại và gửi kết quả, sửa đủ ${AIS.rounds} vòng rồi chờ duyệt.` : "") });
      toClaude = true;
    }
  } catch (e) {}
  const body = { clip: P.clip, version: P.version, kind: "pose", status: "sent", sentAt: new Date().toISOString(), adjustCount: open.length, toClaude };
  if (myId) body.sentBy = myId;
  if (AIS.on) { body.selfRounds = AIS.rounds; db.doc("selfplan/" + planId()).set({ clip: P.clip, from: P.version, left: AIS.rounds, of: AIS.rounds, done: [], at: new Date().toISOString() }).catch(fail); }
  try { await db.doc("rounds/" + roundId()).set(body);
        $("p_status").textContent = toClaude ? "Đã gửi cho AI. Trạng thái sẽ cập nhật ở đây." : "Đã đánh dấu gửi. AI sẽ nhận ở lần kiểm tra trang kế tiếp."; }
  catch (e) { fail(e); }
  renderRound();
};

// ---------------------------------------------------------------- AI tự xem lại (user 2026-10-27): the page shoots the anim in 3 views and asks
// Claude (sample capability) for a review; the result is an adjust note kind "ai". With "AI tự xem lại" on, every Gửi cho AI opens a plan
// of N rounds (db selfplan): each new version the AI publishes is reviewed once when the page opens it, the result is sent to the AI,
// until N rounds are done. Settings live in db settings/aiself.
const AIS = { on: false, rounds: 2, plan: null, busy: false };
const planId = () => idOf(P.clip, "selfplan");
function aisFrames() {
  const N = P.frames || 1;
  let m = (P.main && P.main.length ? P.main : keysMode() ? tmgMain() : (P.keys || [1])).filter(f => f >= 1 && f <= N);
  m = [...new Set([1, ...m, N])].sort((a, b) => a - b);
  const out = new Set(m);          // a frame every ~4 F inside each phase (one midpoint made F33-43 look static to the reviewer)
  for (let i = 0; i + 1 < m.length; i++) { const g = m[i + 1] - m[i], n = Math.max(g >= 3 ? 1 : 0, Math.round(g / 4) - 1); for (let j = 1; j <= n; j++) out.add(Math.round(m[i] + g * j / (n + 1))); }
  return [...out].sort((a, b) => a - b).slice(0, 24);
}
async function aisSheets(frames) {
  const cams = ["right", "front", "top"], cols = 6, cw = 220, ch = 220, rows = Math.ceil(frames.length / cols), sheets = [];
  const wasFrame = frame, wasCam = curCam, wasGhost = ghost && ghost.visible, wasSize = renderer.getSize(new THREE.Vector2()), bg = new THREE.Color(0x15181f);
  stopPlay(); if (ghost) ghost.visible = false; ONION.off++; goto(frame); gizmo.detach();
  try {
    for (const k of cams) {
      const out = document.createElement("canvas"); out.width = cw * cols; out.height = ch * rows + 26; const c = out.getContext("2d");
      c.fillStyle = "#15181f"; c.fillRect(0, 0, out.width, out.height);
      c.fillStyle = "#fff"; c.font = "bold 15px sans-serif"; c.fillText(P.clip.replace(/_/g, " ") + " · " + P.version + " · góc " + CAMS[k].label, 8, 18);
      renderer.setSize(cw, ch, false); camAspect(cw / ch);
      frames.forEach((f, i) => {
        goto(f); model.updateMatrixWorld(true); setCam(k);
        camDolly(1.5);   // square cell: pull back so the 2.5 m mace stays in frame (polish_v2 review cropped it at F33)
        renderer.setClearColor(bg, 1); renderer.clear(); renderer.render(scene, CAM());
        const x = (i % cols) * cw, y = 26 + Math.floor(i / cols) * ch; c.drawImage(renderer.domElement, x, y, cw, ch);
        c.strokeStyle = "#333"; c.lineWidth = 1; c.strokeRect(x + .5, y + .5, cw - 1, ch - 1);
        c.font = "bold 16px sans-serif"; c.lineWidth = 3; c.strokeStyle = "#000"; c.strokeText("F" + f, x + 6, y + 20); c.fillStyle = "#ffd23f"; c.fillText("F" + f, x + 6, y + 20);
      });
      sheets.push(await new Promise(r => out.toBlob(r, "image/jpeg", 0.85)));
    }
  } finally {
    if (ghost) ghost.visible = wasGhost; ONION.off = Math.max(0, ONION.off - 1); renderer.setSize(wasSize.x, wasSize.y, false); resize(); setCam(wasCam); goto(wasFrame); renderer.setClearColor(0x000000, 0);
  }
  return { sheets, cams };
}
// per-part measurements for the reviewer (user 2026-10-27: "chưa tự check hết từng bộ phận"): every frame, every part
const AIS_PARTS = { "Hông": ["Root_M"], "Thân, ngực": ["Spine1_M", "Chest_M"], "Đầu, cổ": ["Neck_M", "Head_M"],
  "Tay trái": ["Shoulder_L", "Elbow_L", "Wrist_L"], "Tay phải": ["Shoulder_R", "Elbow_R", "Wrist_R"],
  "Chân trái": ["Hip_L", "Knee_L", "Ankle_L"], "Chân phải": ["Hip_R", "Knee_R", "Ankle_R"], "Vũ khí": ["Weapon"], "Vạt áo, phụ kiện": ["DressFront_M", "DressBack_M", "Prop_M"] };
function aisMetrics() {
  const N = P.frames || 1, wasFrame = frame, Q = new THREE.Quaternion(), V = new THREE.Vector3(), rows = [];
  const parts = Object.fromEntries(Object.entries(AIS_PARTS).map(([k, bs]) => [k, bs.filter(b => B[b])]).filter(([, bs]) => bs.length));
  const used = [...new Set(Object.values(parts).flat())];
  try {
    for (let f = 1; f <= N; f++) {
      goto(f); model.updateMatrixWorld(true); const r = {};
      for (const b of used) { r[b] = { q: B[b].getWorldQuaternion(Q.clone()), p: B[b].getWorldPosition(V.clone()).multiplyScalar(100) }; }
      rows.push(r);
    }
  } finally { goto(wasFrame); }
  const deg = (a, b) => THREE.MathUtils.radToDeg(a.angleTo(b));
  const hinge = (r, a, b, c) => { const u = r[a].p.clone().sub(r[b].p), v = r[c].p.clone().sub(r[b].p); return THREE.MathUtils.radToDeg(u.angleTo(v)); };
  const out = {};
  for (const [part, bs] of Object.entries(parts)) {
    const sp = rows.map((r, i) => i ? Math.max(...bs.map(b => deg(rows[i - 1][b].q, r[b].q))) : 0);
    const spikes = []; for (let i = 2; i < N - 1; i++) if (sp[i] > 6 && sp[i] > 2.5 * Math.max(sp[i - 1], .5) && sp[i] > 2.5 * Math.max(sp[i + 1], .5)) spikes.push("F" + (i + 1));
    const stops = []; for (let i = 2; i < N - 1; i++) if (sp[i - 1] > 4 && sp[i] < 0.25 * sp[i - 1] && sp[i + 1] > 4) stops.push("F" + (i + 1));
    const o = { speed: sp.map(x => Math.round(x)), spikes, stops };
    const side = part === "Tay trái" ? "L" : part === "Tay phải" ? "R" : part === "Chân trái" ? "L" : part === "Chân phải" ? "R" : null;
    if (side && part.startsWith("Tay") && bs.length === 3) o.elbow = rows.map(r => Math.round(hinge(r, "Shoulder_" + side, "Elbow_" + side, "Wrist_" + side)));
    if (side && part.startsWith("Chân") && bs.length === 3) {
      o.knee = rows.map(r => Math.round(hinge(r, "Hip_" + side, "Knee_" + side, "Ankle_" + side)));
      const a = "Ankle_" + side, low = Math.min(...rows.map(r => r[a].p.y));
      o.ankleHeight = rows.map(r => Math.round(r[a].p.y - low));
      const slide = []; for (let i = 1; i < N; i++) { const p0 = rows[i - 1][a].p, p1 = rows[i][a].p; if (p0.y - low < 2 && p1.y - low < 2) { const d = Math.hypot(p1.x - p0.x, p1.z - p0.z); if (d > 1.5) slide.push("F" + (i + 1) + " " + d.toFixed(1) + "cm"); } }
      o.slideOnFloor = slide;
    }
    if (part === "Vũ khí") o.height = rows.map(r => Math.round(r.Weapon.p.y));
    out[part] = o;
  }
  return out;
}
function aisMetricsText(m) {
  return Object.entries(m).map(([part, o]) => "- " + part + ": tốc độ xoay °/frame F1→: " + o.speed.join(" ") +
    (o.spikes.length ? " | giật (vọt hơn 2,5 lần hai frame bên): " + o.spikes.join(", ") : "") + (o.stops.length ? " | khựng (đang đi thì gần dừng 1 frame): " + o.stops.join(", ") : "") +
    (o.elbow ? " | góc khuỷu: " + o.elbow.join(" ") : "") + (o.knee ? " | góc gối: " + o.knee.join(" ") : "") +
    (o.ankleHeight ? " | cổ chân cao hơn điểm thấp nhất (cm): " + o.ankleHeight.join(" ") : "") + (o.slideOnFloor && o.slideOnFloor.length ? " | trượt khi đang chạm sàn: " + o.slideOnFloor.join(", ") : "") +
    (o.height ? " | độ cao gốc vũ khí (cm): " + o.height.join(" ") : "")).join("\n");
}
function aisPrompt(frames, metrics) {
  const main = P.main && P.main.length ? P.main : keysMode() ? tmgMain() : (P.keys || []);
  const names = P.phases || (keysMode() ? phaseNames(main) : []);
  const ph = main.slice(0, -1).map((f, i) => (names[i] || "Pha " + (i + 1)) + " F" + f + "–F" + main[i + 1]).join("; ");
  return `Bạn là animator game senior, review một anim 3D cho game. Nhân vật ${P.project || ""}: boss to vạm vỡ, chân ngắn tay dài, cầm chùy rất nặng dài khoảng 2,5 m.
Clip "${P.clip}", version ${P.version} (${P.label}), ${P.frames} frame, 30 fps. Các pha: ${ph || "không có"}.
Ghi chú của version: ${P.note || "(không)"}.
Ảnh gửi kèm: 3 tấm, mỗi tấm một góc nhìn (phải = góc game, trước, trên); mỗi ô là một frame, số frame ghi ở góc ô: ${frames.map(f => "F" + f).join(", ")}.
Số đo của trang cho TỪNG bộ phận ở MỌI frame (đo thật từ anim, tin số này hơn mắt khi nói về giật, khựng, trượt, góc khớp):
${aisMetricsText(metrics)}
Kiểm LẦN LƯỢT TỪNG bộ phận trong danh sách trên, không bỏ bộ phận nào: với mỗi bộ phận xét cả chuỗi frame - chuyển động có liền mạch không (dùng tốc độ: chỗ giật, khựng, trôi), có độ trễ / overlap hợp lý so với hông và thân không, khớp có gập sai chiều hay duỗi khóa không (góc khuỷu, góc gối), chân có trượt hoặc xuyên sàn khi đang chịu lực không, tay có rời cán không, vũ khí có thể hiện độ nặng không. Sau đó xét toàn thân: pha nào đọc không rõ, dáng (silhouette) ở góc game.
Không ước lượng góc khớp từ ảnh; dùng số đo. Lỗi phải chỉ rõ frame.
Trả lời CHỈ bằng JSON, tiếng Việt:
{"summary": "1-2 câu", "score": 1-10,
 "parts": [{"part": "đúng tên bộ phận như danh sách", "ok": true/false, "frames": "các frame có vấn đề hoặc rỗng", "comment": "nhận xét ngắn, kể cả khi ổn"}],
 "issues": [{"frame": số, "part": "bộ phận", "problem": "lỗi", "fix": "cách sửa"}]}
"parts" phải có đủ mọi bộ phận trong danh sách. "issues" tối đa 8, nặng nhất trước.`;
}
const AIS_ERR = { not_granted: "Bạn chưa cho phép trang gọi AI.", images_unavailable: "Trang chưa được phép gửi ảnh cho AI.", rate_limited: "AI đang bận, thử lại sau ít phút.", cancelled: "Đã dừng." };
async function aisRun(round, of) {          // one review of the open version -> adjust note kind "ai"; returns the note or null
  if (AIS.busy || !model) return null;
  const st = $("asStatus"), sample = window.claude && claude.use ? await claude.use("sample").catch(() => null) : null;
  if (!sample) { st.textContent = "Không gọi được AI từ trang này (cần mở trên claude.ai)."; return null; }
  AIS.busy = true; $("asRun").disabled = true;
  try {
    const frames = aisFrames(); st.textContent = "AI tự xem lại: đang chụp " + frames.length + " frame × 3 góc…";
    const { sheets } = await aisSheets(frames);
    st.textContent = "AI đang xem và đánh giá (thường 30–90 giây)…";
    st.textContent = "AI tự xem lại: đang đo từng bộ phận ở mọi frame…"; const metrics = aisMetrics();
    st.textContent = "AI đang xem và đánh giá từng bộ phận (thường 30–90 giây)…";
    const r = (await sample.json(aisPrompt(frames, metrics), { images: sheets, cache: false })) || {};
    const issues = Array.isArray(r.issues) ? r.issues.slice(0, 8) : [], parts = Array.isArray(r.parts) ? r.parts : [];
    const imgs = [], as = await getAssets();
    if (as) for (const b of sheets) { try { const up = await as.upload(b); imgs.push({ id: up.id, url: up.url }); } catch (e) {} }
    const text = "AI tự kiểm" + (round ? " vòng " + round + "/" + of : "") + " (điểm " + (r.score ?? "?") + "/10): " + (r.summary || "") +
      (parts.length ? " Từng bộ phận: " + parts.map(x => (x.ok ? "✓ " : "✗ ") + x.part + (x.frames ? " (" + x.frames + ")" : "") + ": " + (x.comment || "")).join("; ") + "." : "") +
      (issues.length ? " Lỗi: " + issues.map(i => "F" + i.frame + " " + (i.part || "") + ": " + (i.problem || "") + " → " + (i.fix || "")).join("; ") : " Không thấy lỗi rõ.");
    const body = { clip: P.clip, version: P.version, frame: (issues[0] && +issues[0].frame) || 1, kind: "ai", bones: {}, local: {}, text,
      ai: { score: r.score ?? null, summary: r.summary || "", parts, issues, frames, metrics, round: round || null, of: of || null }, status: "open", createdAt: new Date().toISOString() };
    if (imgs.length) { body.img = imgs[0]; body.imgs = imgs; }
    if (myId) body.author = myId;
    if (db && canWrite) { await db.collection("adjusts").add(body); adjs.push({ ...body }); renderAdjs(); renderRound(); }
    st.textContent = "AI tự kiểm xong: " + parts.filter(x => !x.ok).length + "/" + parts.length + " bộ phận có vấn đề, " + issues.length + " lỗi, điểm " + (r.score ?? "?") + "/10 (ghi chú ở danh sách điều chỉnh).";
    return body;
  } catch (e) { st.textContent = "AI tự xem lại chưa chạy được: " + (AIS_ERR[e && e.code] || (e && e.message) || e); return null; }
  finally { AIS.busy = false; $("asRun").disabled = false; }
}
async function maybeAutoReview() {           // the round of the plan for this version, once, when the page opens the newest version
  const pl = AIS.plan;
  if (!AIS.on || !pl || AIS.busy || !ready || !model || !db || !canWrite) return;
  if (POSES.find(q => q.clip === P.clip) !== P || P.version === pl.from || (pl.done || []).includes(P.version) || !(pl.left > 0)) return;
  const k = pl.of - pl.left + 1, left = pl.left - 1;
  AIS.plan = { ...pl, left, done: [...(pl.done || []), P.version], at: new Date().toISOString() };
  await db.doc("selfplan/" + planId()).set(AIS.plan);          // mark first: one run per version
  const note = await aisRun(k, pl.of); if (!note) return;
  try {
    if (comments && (await comments.canSendToClaude().catch(() => "off")) === "available") {
      const anchor = await comments.anchorFor($("aiSend"));
      await comments.sendToClaude({ anchor, text: `Pose Lab: AI tự kiểm vòng ${k}/${pl.of} cho ${P.clip} ${P.version}: ${note.ai.issues.length} lỗi, điểm ${note.ai.score ?? "?"}/10. ` +
        `Đọc collection "adjusts" (clip ${P.clip}, version ${P.version}, kind "ai"; ảnh 3 góc ở imgs), sửa rồi ra version mới. ` + (left > 0 ? `Còn ${left} vòng tự kiểm.` : `Đây là vòng cuối: sửa xong thì dừng, chờ người dùng duyệt.`) });
      $("asStatus").textContent += " Đã gửi kết quả cho AI.";
    } else $("asStatus").textContent += " Bấm Gửi cho AI để AI sửa theo kết quả này.";
  } catch (e) { $("asStatus").textContent += " Bấm Gửi cho AI để AI sửa theo kết quả này."; }
}
function aisSave() { AIS.on = $("asOn").checked; AIS.rounds = +$("asRounds").value; if (db && canWrite) db.doc("settings/aiself").set({ on: AIS.on, rounds: AIS.rounds, at: new Date().toISOString() }).catch(fail); }
$("asOn").onchange = aisSave; $("asRounds").onchange = aisSave;
$("asRun").onclick = () => aisRun(null, null);

function renderPoses() {     // version list (newest first): status of its review round + its adjustments
  const box = $("poses"); box.innerHTML = ""; $("poseCount").textContent = POSES.length;
  const ST = { sent: "đã gửi AI", working: "AI đang sửa", fixed: "AI đã sửa" };
  POSES.forEach((p, i) => {
    const b = document.createElement("button"); b.className = "item" + (p === P ? " on" : "");
    const head = document.createElement("div"); head.className = "vhead";
    const v = document.createElement("span"); v.className = "vname"; v.textContent = p.version + (i === 0 ? " · mới nhất" : "");
    head.append(v);
    const r = rounds[(p.clip + "-" + p.version).replace(/[^A-Za-z0-9_\-.]/g, "_")];
    if (r) { const pl = document.createElement("span"); pl.className = "pill " + (r.status === "fixed" ? "done" : r.status); pl.textContent = ST[r.status] || r.status; head.append(pl); }
    const t = document.createElement("b"); t.textContent = p.label;
    b.append(head, t); b.title = p.note || "";
    if (p.note) { const n = document.createElement("span"); n.className = "vnote"; n.textContent = p.note; b.append(n); }
    const na = adjs.filter(a => a.clip === p.clip && a.version === p.version), open = na.filter(a => a.status !== "done").length;
    const s = document.createElement("small");
    s.textContent = [p.date, (p.frames || 1) + " frame", na.length ? na.length + " điều chỉnh" + (open ? " (" + open + " chờ AI)" : "") : ""].filter(Boolean).join(" · ");
    b.append(s); b.onclick = () => { if (p !== P) { openPose(p); renderPoses(); } }; box.append(b);
  });
}

// ---------------------------------------------------------------- keys on the page (POSES mode "keys")
// The page is the animation: a key = the local pose of every bone at one frame (db "keys", one doc per key, id
// "<clip>-<version>-F<f>"). In-betweens: per channel (quaternion xyzw aligned to one hemisphere, position xyz) cubic
// Hermite, tangents like Blender's auto-clamped handles (flat on a peak, Fritsch-Carlson limited so nothing overshoots)
// or stepped for blocking. Loop clips: the last frame == F1 and the curves wrap. "Bám sàn": on the frames painted in
// the contact lanes the ankle moves on straight lines through its positions at the span ends and at the keys inside the
// span (two-bone IK on the spline pose), so a planted foot neither floats, sinks nor wobbles between keys.
let KEYS = new Map(), TR = null, ANK = {}, BN = [], REST = {}, CT = { L: new Set(), R: new Set() }, ready = false;
let ANIM = { interp: "spline", lock: true }, animAt = "", autoKey = true, keysInDb = false, dirtyKeys = new Set(), animDirty = false, flushT = 0, flushing = false, quietUntil = 0;
let remoteKeys = {}, remoteAnims = {}, keySig = "";
function keysMode() { return !!P && P.mode === "keys"; }
const NFR = () => P.frames || 1;
const PER = () => P.loop ? Math.max(1, NFR() - 1) : NFR();
function cyc(f) { if (!P.loop) return Math.max(1, Math.min(NFR(), f)); const N = PER(); return ((f - 1) % N + N) % N + 1; }
const idOf = (clip, ver) => (clip + "-" + ver).replace(/[^A-Za-z0-9_\-.]/g, "_");
function parseSet(s) {
  const o = new Set();
  for (const part of String(s || "").split(",")) {
    const m = part.trim().match(/^(\d+)(?:-(\d+))?$/); if (!m) continue;
    const a = +m[1], b = +(m[2] || m[1]); for (let f = Math.min(a, b); f <= Math.max(a, b); f++) o.add(f);
  }
  return o;
}
function fmtSet(set) {
  const fs = [...set].sort((a, b) => a - b), out = [];
  for (let i = 0; i < fs.length; i++) { let j = i; while (j + 1 < fs.length && fs[j + 1] === fs[j] + 1) j++; out.push(i === j ? "" + fs[i] : fs[i] + "-" + fs[j]); i = j; }
  return out.join(",");
}
let LIVE = null;   // Studio W3a: {rest, snap} khi đang hiện bằng nhân vật hiện tại
const LIVE_ROOTS = new Set(["root", "Root_M"]);
function liveIn(n, k) {    // key (theo model chụp) -> rig hiện tại: giữ góc xoay, độ dài xương theo rig mới, phần dời thêm giữ nguyên
  k = k.slice(); const r = LIVE && LIVE.rest[n]; if (!r) return k;
  const s = LIVE.snap && LIVE.snap[n];
  if (s) { k[4] = r.x + k[4] - s.x; k[5] = r.y + k[5] - s.y; k[6] = r.z + k[6] - s.z; }
  else if (!LIVE_ROOTS.has(n)) { k[4] = r.x; k[5] = r.y; k[6] = r.z; }
  return k;
}
function liveOut(pose) {   // ngược lại khi lưu key: key luôn theo model chụp, Pose Lab cũ vẫn đọc đúng
  if (!LIVE || !LIVE.snap) return pose; const o = {};
  for (const n in pose) { const k = pose[n].slice(), r = LIVE.rest[n], s = LIVE.snap[n]; if (r && s) { k[4] += s.x - r.x; k[5] += s.y - r.y; k[6] += s.z - r.z; } o[n] = k; }
  return o;
}
const packBone = (q, p) => [...q.toArray().map(x => +x.toFixed(6)), ...p.toArray().map(x => +x.toFixed(5))];
function poseNow() { const o = {}; for (const n of BN) o[n] = packBone(B[n].quaternion, B[n].position); return o; }
function poseFromCache(f) { const c = cache[f] || cache[1], o = {}; for (const n of BN) if (c && c[n]) o[n] = packBone(c[n][1], c[n][0]); return o; }
const sigOf = m => [...m.entries()].sort((a, b) => a[0] - b[0]).map(([f, k]) => f + "@" + k.at + (k.main ? "*" : "") + (k.phase || "")).join("|");

function initKeys() {
  BN = Object.keys(B); REST = poseFromCache(1); if (P.frames0 != null) P.frames = P.frames0;
  KEYS = new Map(); keysInDb = false; dirtyKeys = new Set(); animDirty = false; animAt = "";
  ANIM = { interp: P.interp || "spline", lock: true, phys: P.phys ? JSON.parse(JSON.stringify(P.phys)) : physDefault() };
  CT = { L: parseSet((P.contacts || {}).L), R: parseSet((P.contacts || {}).R) };
  const local = !window.claude ? loadLocal() : null;            // local preview: keys kept in this browser
  if (local) {
    KEYS = new Map(Object.entries(local.keys || {}).map(([f, k]) => [+f, k]));
    if (local.anim) { ANIM.interp = local.anim.interp || ANIM.interp; ANIM.lock = local.anim.lock !== false; CT = { L: parseSet(local.anim.contacts.L), R: parseSet(local.anim.contacts.R) };
                      if (local.anim.phys) ANIM.phys = local.anim.phys; }
  }
  PINS = parseSet(ANIM.phys.pin); propPts = {}; PHYS = null; physDirty = true; BODY = null; BODYSCAN = null; bodyDirty = true; if (typeof bakeUndo !== "undefined") bakeUndo = null;
  if (!KEYS.size) for (const f of P.keys || [1]) if (f <= PER() || !P.loop) KEYS.set(cyc(f), { pose: liveOut(poseFromCache(f)), at: "seed" });
  keySig = sigOf(KEYS); buildTracks();
}
function loadLocal() { try { return JSON.parse(localStorage.getItem("poselab:" + idOf(P.clip, P.version)) || "null"); } catch { return null; } }
function saveLocal() {
  try { localStorage.setItem("poselab:" + idOf(P.clip, P.version), JSON.stringify({ keys: Object.fromEntries(KEYS),
    anim: { interp: ANIM.interp, lock: ANIM.lock, contacts: { L: fmtSet(CT.L), R: fmtSet(CT.R) }, phys: ANIM.phys } })); } catch {}
}

function buildTracks() {
  ANK = {}; RELK = {}; physDirty = true; bodyDirty = true;
  const ks = [...KEYS.keys()].sort((a, b) => a - b), m = ks.length;
  TR = { ks, t: [], idx: [], bones: {} };
  if (!m) return;
  const idx = [];
  if (P.loop) { const N = PER(); for (let j = -2; j < m + 2; j++) { const i = ((j % m) + m) % m; idx.push(i); TR.t.push(ks[i] + Math.floor(j / m) * N); } }
  else ks.forEach((k, i) => { idx.push(i); TR.t.push(k); });
  const t = TR.t; TR.idx = idx;
  for (const n of BN) {
    const V = idx.map(i => { const k = (KEYS.get(ks[i]).pose || {})[n]; return k ? liveIn(n, k) : REST[n].slice(); });
    for (let j = 1; j < V.length; j++) {          // shortest way round between neighbouring keys
      const a = V[j - 1], b = V[j];
      if (a[0] * b[0] + a[1] * b[1] + a[2] * b[2] + a[3] * b[3] < 0) for (let c = 0; c < 4; c++) b[c] = -b[c];
    }
    const M = V.map((v, j) => v.map((x, c) => {
      if (j === 0 || j === V.length - 1) return 0;
      const h0 = t[j] - t[j - 1], h1 = t[j + 1] - t[j], d0 = (x - V[j - 1][c]) / h0, d1 = (V[j + 1][c] - x) / h1;
      if (d0 * d1 <= 0) return 0;                                   // peak / flat: flat tangent (auto-clamped)
      const s = (V[j + 1][c] - V[j - 1][c]) / (t[j + 1] - t[j - 1]);
      return Math.sign(s) * Math.min(Math.abs(s), 3 * Math.abs(d0), 3 * Math.abs(d1));   // no overshoot
    }));
    TR.bones[n] = { V, M };
  }
}
function evalFK(f) {      // spline / stepped pose of the keys at frame f -> bone locals
  if (!TR || !TR.ks.length) return false;
  const x = cyc(f), t = TR.t, L = t.length;
  let j = 0; while (j < L - 1 && t[j + 1] <= x) j++;
  const hold = ANIM.interp === "step" || x <= t[0] || j >= L - 1, h = hold ? 1 : t[j + 1] - t[j], s = hold ? 0 : (x - t[j]) / h;
  const s2 = s * s, s3 = s2 * s, h00 = 2 * s3 - 3 * s2 + 1, h10 = s3 - 2 * s2 + s, h01 = -2 * s3 + 3 * s2, h11 = s3 - s2;
  for (const n of BN) {
    const tr = TR.bones[n]; if (!tr) continue;
    const a = tr.V[j];
    let v = a;
    if (!hold) { const b = tr.V[j + 1], ma = tr.M[j], mb = tr.M[j + 1]; v = a.map((y, c) => h00 * y + h10 * h * ma[c] + h01 * b[c] + h11 * h * mb[c]); }
    B[n].quaternion.set(v[0], v[1], v[2], v[3]).normalize(); B[n].position.set(v[4], v[5], v[6]);
  }
  return true;
}
function ankW(f) {        // ankle world transforms of the pure spline pose (cached until keys / contacts change)
  f = cyc(f); if (ANK[f]) return ANK[f];
  evalFK(f); model.updateMatrixWorld(true);
  const o = {}; for (const s of ["L", "R"]) { const a = B[LEGS[s][2]]; o[s] = { p: wp(a), q: wq(a) }; }
  return (ANK[f] = o);
}
function contactRun(s, c) {    // planted span around cycle frame c as unwrapped [a, b], or null
  const S = CT[s]; if (!S.has(c)) return null;
  const N = PER(), has = u => S.has(cyc(u));
  let a = c, b = c, g = 0;
  if (!P.loop) { while (a > 1 && has(a - 1)) a--; while (b < N && has(b + 1)) b++; return [a, b]; }
  while (has(a - 1) && g++ < N) a--; g = 0; while (has(b + 1) && g++ < N) b++;
  return b - a + 1 >= N ? null : [a, b];
}
function lockTarget(s, f) {
  const c = cyc(f), r = contactRun(s, c); if (!r || !B[LEGS[s][2]]) return null;
  const [a, b] = r, N = PER(), pts = new Set([a, b]);
  for (const k of TR.ks) for (const u of P.loop ? [k - N, k, k + N] : [k]) if (u > a && u < b) pts.add(u);
  const us = [...pts].sort((x, y) => x - y);
  let i = 0; while (i < us.length - 1 && us[i + 1] <= c) i++;
  const A = ankW(us[i])[s];
  if (i >= us.length - 1 || us[i] === c) return { p: A.p.clone(), q: A.q.clone() };
  const Bn = ankW(us[i + 1])[s], w = (c - us[i]) / (us[i + 1] - us[i]);
  return { p: A.p.clone().lerp(Bn.p, w), q: A.q.clone().slerp(Bn.q, w) };
}
// Prop lock (POSES follow {prop, to, hand}): the prop's transform relative to its bone and the hand's grip on the prop
// are read at every key and blended between keys, then applied after the spline: the mace stays on the shoulder and
// the hand on the mace on every in-between (the prop bone itself is a child of the root in this rig).
let RELK = {};
function relAtKey(k) {
  if (RELK[k]) return RELK[k];
  evalFK(k); model.updateMatrixWorld(true);
  const c = P.follow, Wp = B[c.prop].matrixWorld, d = (M) => { const p = new V3(), q = new Q(), s = new V3(); M.decompose(p, q, s); return { p, q }; };
  return (RELK[k] = { w: d(B[c.to].matrixWorld.clone().invert().multiply(Wp)), h: d(Wp.clone().invert().multiply(B[ARMS[c.hand][2]].matrixWorld)) });
}
function relAt(f) {
  const x = cyc(f), t = TR.t, L = t.length; let j = 0; while (j < L - 1 && t[j + 1] <= x) j++;
  const A = relAtKey(TR.ks[TR.idx[j]]);
  if (ANIM.interp === "step" || x <= t[0] || j >= L - 1 || t[j] === x) return A;
  const Bk = relAtKey(TR.ks[TR.idx[j + 1]]), w = (x - t[j]) / (t[j + 1] - t[j]);
  const mix = (a, b) => ({ p: a.p.clone().lerp(b.p, w), q: a.q.clone().slerp(b.q, w) });
  return { w: mix(A.w, Bk.w), h: mix(A.h, Bk.h) };
}
const relM = r => new THREE.Matrix4().compose(r.p, r.q, new V3(1, 1, 1));
function setWorldMat(o, M) {
  o.parent.updateMatrixWorld(true);
  new THREE.Matrix4().copy(o.parent.matrixWorld).invert().multiply(M).decompose(o.position, o.quaternion, new V3());
  o.updateMatrixWorld(true);
}
function propHandTo(Mprop, relH) {   // prop world matrix, then the hand IK onto its grip
  const c = P.follow; setWorldMat(B[c.prop], Mprop); model.updateMatrixWorld(true);
  const p = new V3(), q = new Q(); B[c.prop].matrixWorld.clone().multiply(relH).decompose(p, q, new V3());
  handQ[c.hand] = q; solveArm(c.hand, p); model.updateMatrixWorld(true);
}
const hasFollow = () => !!(P && P.follow && B[P.follow.prop] && B[P.follow.to]);
function evalPose(f) {
  if (!TR || !TR.ks.length || !BN.length) return false;
  const tg = {};
  // stepped blocking holds the WHOLE key pose, feet included (user 2026-10-23 "Phần chân đang chưa để Step by Step":
  // the foot lock kept sliding the planted feet between keys); the lock works on spline only
  if (ANIM.lock && ANIM.interp !== "step") for (const s of ["L", "R"]) tg[s] = lockTarget(s, f);
  const rel = hasFollow() ? relAt(f) : null;
  evalFK(f); model.updateMatrixWorld(true);
  const ed = edited;
  for (const s of ["L", "R"]) if (tg[s]) { edited = new Set(); solve2(LEGS[s], tg[s].p, tg[s].q); }
  // floor: no foot mesh below the floor on any frame (spline arcs of hip/knee rotations dipped the swinging right
  // foot 14 cm under the floor at F33); the foot is lifted straight up by leg IK
  if (ANIM.interp !== "step" && !fitRun) for (const s of ["L", "R"]) {
    const lo = footLowY(s);
    if (lo < -0.002) { model.updateMatrixWorld(true); const a = B[LEGS[s][2]]; edited = new Set(); solve2(LEGS[s], wp(a).add(new V3(0, -lo, 0)), wq(a)); model.updateMatrixWorld(true); }
  }
  if (rel) { edited = new Set(); propHandTo(B[P.follow.to].matrixWorld.clone().multiply(relM(rel.w)), relM(rel.h)); }
  edited = ed; model.updateMatrixWorld(true);
  return true;
}

// ---------------------------------------------------------------- physics layer (docs/poselab_physics_p1.md)
// After evalPose (spline -> foot lock -> floor -> prop follow), parts get damped springs in WORLD space toward the key
// pose, frame by frame from F1 (a spring needs the frames before): they drag, overshoot and settle. Lessons from Gaygor
// Hit polish_v3..v7: follow the key motion (never a pre-smoothed path), contacts inside the simulation as a soft pad (a
// post push popped 20-25 deg), always from the key pose (no springs on springs), ease back onto the key pose at the end.
// Types: joint (world rotation), hinge (only the bend about the bone's local Z), prop (turns about the gripping hand,
// the arm IK'd back onto the grip, kept off colliders), swing (elbow about the shoulder->wrist axis, hand kept).
// The result is cached per frame (PHYS) and applied in sampleAt: view, play, playblast and FBX export all include it.
const PHYS_PRESETS = {
  light: { label: "Nhẹ", period: 8, bounce: 0.62, limit: 12 }, medium: { label: "Vừa", period: 12, bounce: 0.68, limit: 15 },
  heavy: { label: "Nặng", period: 15, bounce: 0.72, limit: 24 }, vheavy: { label: "Rất nặng", period: 20, bounce: 0.75, limit: 30 },
};
const PHYS_LABEL = { Weapon: "Vũ khí (chùy)", DressFront_M: "Vạt khố trước", DressBack_M: "Vạt khố sau", slingshot_0: "Vũ khí" };
const physName = n => NAMES[n] || PHYS_LABEL[n] || n;
const PHYS_TYPES = { joint: "Khớp mềm", hinge: "Bản lề", prop: "Vật cầm tay", swing: "Đung đưa khuỷu" };
// per character (by clip name prefix): the springs approved on Gaygor Hit (polish_v5 arms, polish_v7 mace)
const CHAR_PHYS = {
  Gaygor: { parts: [
    { bone: "Scapula_R", type: "joint", preset: "medium", limit: 5 }, { bone: "Shoulder_R", type: "joint", preset: "medium" },
    { bone: "Elbow_R", type: "hinge", preset: "medium" }, { bone: "Wrist_R", type: "joint", preset: "light" },
    { bone: "Weapon", type: "prop", hand: "L", preset: "heavy" }, { bone: "Elbow_L", type: "swing", preset: "medium" } ],
    colliders: [{ bone: "Shoulder_L" }], end: 8, propMass: 15,
    // ragdoll joint limits (deg, around the rest pose): bend about the bone's Z, spread, twist. Measured on Hit (polish_v7,
    // b75_v2, k10_v1) + Walk anim_v1, widened 20 %, joined with anatomy; elbows / knees from straight to 145 / 150 deg
    // (2026-10-25). Attack's team blocking was left out: its left upper arm turns 180 deg with the elbow bent the other way.
    limits: {"Spine1_M":[-35,35,-25,25,-33,30],"Chest_M":[-35,35,-25,25,-30,30],"Neck_M":[-40,40,-30,30,-40,40],"Head_M":[-40,40,-30,30,-50,50],"Shoulder_L":[-90,90,-90,90,-80,80],"Shoulder_R":[-90,90,-90,90,-80,86],"Elbow_L":[-39,106,-10,10,-15,15],"Elbow_R":[-34,111,-10,10,-15,15],"Wrist_L":[-70,70,-40,42,-60,60],"Wrist_R":[-70,70,-40,40,-60,60],"Hip_L":[-90,90,-50,58,-40,77],"Hip_R":[-90,90,-50,50,-111,40],"Knee_L":[-88,62,-8,8,-15,15],"Knee_R":[-93,57,-8,8,-15,15],"Ankle_L":[-45,45,-62,25,-20,45],"Ankle_R":[-45,76,-42,68,-30,39]},
    // rest pose for the body collision (Idle F1 = Gaygor Hit F1, page locals)
    rest: {"root":[-0.707107,0,0,0.707107,0,0,0],"Root_M":[0.597661,0.521738,0.458601,0.400344,0,69.12482,-9.46238],"Spine1_M":[-0.001001,-9.3e-05,0.031293,0.99951,18.42679,0,0],"Chest_M":[0.001335,0.009876,0.214884,0.976589,19.4202,0,0],"Neck_M":[-0.002814,-0.003161,0.057943,0.998311,35.01968,0,0],"Head_M":[0.011859,0.013613,0.118472,0.992793,21.5911,0,0],"HeadEnd_M":[0,0,0,1,26.33226,-0.00081,0.00011],"Scapula_R":[0.02202,0.634419,-0.106137,0.765351,23.11413,-5.13918,-10.86021],"Shoulder_R":[-0.063718,0.50518,0.284828,0.812161,38.02157,-4e-05,5e-05],"Elbow_R":[-0.002122,0.022609,0.293444,0.955706,47.7726,-1e-05,2e-05],"Wrist_R":[0.139965,-0.15793,0.043233,0.976524,43.28481,0,4e-05],"MiddleFinger1_R":[0.038409,0.794951,-0.028303,0.604794,25.7486,-1e-05,-3e-05],"MiddleFinger2_R":[0.00016,0.878742,0.00027,0.477296,12.17631,-1e-05,1e-05],"MiddleFinger3_R":[0,0.573576,0,0.819152,15.71442,-2e-05,-1e-05],"ThumbFinger1_R":[-0.546921,0.412128,0.316043,0.656615,7.96313,14.52626,-6.60183],"ThumbFinger2_R":[0,0.602463,0,0.798147,10.98152,-2e-05,0],"ThumbFinger3_R":[0,0.300706,0,0.953717,8.42847,4e-05,-1e-05],"IndexFinger1_R":[-0.074121,0.790266,-0.022296,0.607856,25.25854,9.91485,-0.94242],"IndexFinger2_R":[-0.000264,0.898875,0.00044,0.438205,12.86582,0,0],"IndexFinger3_R":[0,0.573577,0,0.819152,13.36576,0,0],"RingFinger1_R":[0.126955,0.747966,-0.053034,0.64932,23.91846,-8.30188,-1.84497],"RingFinger2_R":[-0.000965,0.902391,-0.002424,0.43091,11.89394,1e-05,1e-05],"RingFinger3_R":[0,0.573577,0,0.819152,13.41643,0,0],"PinkyFinger1_R":[0.203291,0.746569,-0.057624,0.630863,20.8562,-17.26331,-4.6987],"PinkyFinger2_R":[0.001949,0.912385,0.000425,0.409329,9.58454,1e-05,1e-05],"PinkyFinger3_R":[0,0.573577,0,0.819152,10.80161,-2e-05,1e-05],"Prop_M":[0.540352,0.456092,0.540352,-0.456092,24.13095,29.69802,4e-05],"Scapula_L":[-0.631111,0.021007,0.767681,0.109195,23.11414,-5.13919,10.86022],"Shoulder_L":[-0.62152,0.405048,0.100986,0.662911,-38.02146,3e-05,0.00013],"Elbow_L":[-1.1e-05,4e-06,-0.798087,0.602542,-47.77282,0.00022,0.00027],"Wrist_L":[-0.592528,0.080678,-0.26625,0.755985,-43.28429,0.00065,0.1422],"MiddleFinger1_L":[0.027847,0.529014,-0.041078,0.847161,-25.74857,1e-05,6e-05],"MiddleFinger2_L":[0.003075,0.622383,-8.9e-05,0.782707,-12.17626,0,7e-05],"MiddleFinger3_L":[0.002034,0.3007,0.000302,0.953717,-15.7144,0,1e-05],"ThumbFinger1_L":[-0.445352,0.369214,0.288653,0.762904,-7.96316,-14.52624,6.60182],"ThumbFinger2_L":[0.00383,0.348775,0.180979,0.919559,-10.98151,-1e-05,0],"ThumbFinger3_L":[-0.056942,0.021017,0.171831,0.983255,-8.42846,3e-05,-3e-05],"IndexFinger1_L":[-0.024683,0.521079,0.05838,0.851152,-25.25853,-9.91488,0.94245],"IndexFinger2_L":[0.026065,0.645981,0.09012,0.757567,-12.86583,-2e-05,4e-05],"IndexFinger3_L":[-0.0003,0.292989,0.067687,0.953717,-13.36577,1e-05,0],"RingFinger1_L":[0.052061,0.471757,-0.131875,0.870255,-23.91843,8.30186,1.84502],"RingFinger2_L":[-0.035868,0.655637,-0.068296,0.751125,-11.89392,3e-05,6e-05],"RingFinger3_L":[-0.00953,0.295793,-0.053295,0.953717,-13.41646,0,4e-05],"PinkyFinger1_L":[0.086746,0.478704,-0.199363,0.850631,-20.85616,17.26331,4.69871],"PinkyFinger2_L":[-0.046153,0.65736,-0.130881,0.740687,-9.58448,-3e-05,4e-05],"PinkyFinger3_L":[-0.003333,0.283299,-0.100774,0.953717,-10.80161,1e-05,1e-05],"DressFront_M":[-0.495801,-0.504164,-0.495801,0.504164,-17.71235,25.08229,0.00022],"DressBack_M":[-0.495801,-0.504164,-0.495801,0.504164,-9.02297,-26.64032,-0.00035],"Hip_R":[0.457229,0.843632,-0.082739,0.269038,-3.16371,-0.49132,-19.30545],"Knee_R":[0.024752,0.054113,-0.478246,0.876208,32.8415,3e-05,2e-05],"Ankle_R":[0.080604,0.101276,0.034328,0.990993,34.4131,7e-05,1e-05],"Toes_R":[-0.018929,-0.012841,0.582915,0.812211,9.162,16.42479,-0.00022],"ToesEnd_R":[0,0,0,1,22.25883,-0.0002,0.0005],"Hip_L":[0.888454,-0.266711,-0.330287,-0.174429,-3.16371,-0.49132,19.30546],"Knee_L":[0.024158,0.058212,-0.514474,0.855187,-32.84157,4e-05,0],"Ankle_L":[-0.025179,0.212172,0.211262,0.953791,-34.4132,2e-05,0],"Toes_L":[-0.018929,-0.012841,0.582915,0.812211,-9.16199,-16.42505,-0.00026],"ToesEnd_L":[0,1e-06,0,1,-22.2586,0.00022,0.00072],"Weapon":[-0.310153,0.103795,0.271785,0.905077,62.48257,159.28162,-13.60932]} },
};
const CM_W = 0.01;                 // 1 cm in world units (glTF world in metres)
// props: 64 sub-steps (small contact corrections); contact = inelastic constraint (see computePhysCore)
const PHYS_SUB = 8, PHYS_SUBP = 64, PIN_RAMP = 3, PHYS_BODY_EVERY = 4, FLOOR_BOUNCE = 0.15;
let PHYS = null, physDirty = true, physSel = 0, PINS = new Set(), propPts = {};
const physDefault = () => ({ on: false, parts: [], colliders: [], pin: "", end: 8, impacts: [], autoStep: true });
const physOn = () => !!(keysMode() && model && ANIM.phys && ANIM.phys.on && (ANIM.phys.parts.some(p => B[p.bone]) || (!P.loop && (ANIM.phys.impacts || []).some(i => B[i.seg])) || ragOn() || apAny()));
// ---- AutoPhysics (user 2026-10-26: a Cascadeur-like AutoPhysics panel; phase 1 = smooth trajectory / rotation, separation,
// secondary, penetration). Layers on top of the keys (+ springs / impacts), keys untouched. docs/poselab_autophysics.md
const AP_ROWS = [["phys", "Hiệu chỉnh vật lý", "Trọng tâm bay đúng parabol khi trên không, không tự xoay, trọng tâm trong chân khi đứng (đợt 2)", true],
  ["traj", "Làm mượt quỹ đạo", "Làm mượt đường đi của hông: bỏ giật, rung nhỏ giữa các key. Chân đang chống giữ nguyên chỗ"],
  ["rot", "Làm mượt xoay", "Làm mượt góc xoay của các khớp: bỏ xoay đột ngột, lắc qua lại"],
  ["comp", "Chuyển động bù trừ", "Thân và tay tự đưa ngược lại để giữ thăng bằng (đợt 2)", true],
  ["sep", "Tách nhịp chuyển động", "Lệch nhịp theo chuỗi hông → lưng → ngực → cổ → đầu và vai → khuỷu → cổ tay, để các phần không cùng bắt đầu, cùng dừng"],
  ["sec", "Chuyển động phụ", "Quán tính, trễ rồi lắng (lò xo) cho tay, chùy, vạt khố. Chưa có lò xo thì dùng bộ của nhân vật. Thanh trượt = độ lớn"],
  ["pen", "Xử lý xuyên", "Nâng người khỏi sàn, đẩy tay / chân ra khỏi thân khi lẹm vào nhau sâu hơn lúc nghỉ"]];
const apOn = k => !!(ANIM.phys && ANIM.phys.ap && ANIM.phys.ap[k] && ANIM.phys.ap[k].on && !(AP_ROWS.find(r => r[0] === k) || [])[3]);
const apV = k => Math.max(0, Math.min(1, ((ANIM.phys.ap[k] || {}).v ?? 50) / 100));
const apAny = () => AP_ROWS.some(r => apOn(r[0]));
function physPart(p) {             // preset -> numbers (explicit numbers win)
  const pr = PHYS_PRESETS[p.preset] || PHYS_PRESETS.medium;
  return { ...p, period: p.period ?? pr.period, bounce: p.bounce ?? pr.bounce, limit: p.limit ?? pr.limit };
}
function rvec(qa, qb) {            // rotation taking qa to qb as a world rotation vector (rad)
  const d = qb.clone().multiply(qa.clone().invert()); if (d.w < 0) { d.x = -d.x; d.y = -d.y; d.z = -d.z; d.w = -d.w; }
  const s = Math.sqrt(d.x * d.x + d.y * d.y + d.z * d.z); if (s < 1e-9) return new V3();
  return new V3(d.x, d.y, d.z).multiplyScalar(2 * Math.atan2(s, d.w) / s);
}
const qrv = v => { const a = v.length(); return a < 1e-12 ? new Q() : new Q().setFromAxisAngle(v.clone().divideScalar(a), a); };
function softLimit(a, L) {         // continuous, slope 1 below 60 % of the limit, never above it
  const k = 0.6 * L; return a <= k ? a : k + (L - k) * Math.tanh((a - k) / (L - k));
}
const smooth01 = u => { u = Math.max(0, Math.min(1, u)); return u * u * (3 - 2 * u); };
function boneDepth(n) { let d = 0, o = B[n]; while (o && o.parent && o.parent.isBone) { d++; o = o.parent; } return d; }
const comp = (a, i, c) => c === 0 ? a.getX(i) : c === 1 ? a.getY(i) : c === 2 ? a.getZ(i) : a.getW(i);
function propPoints(name) {        // prop mesh points in the prop's unit-scale frame (vertices mostly skinned to it)
  if (propPts[name]) return propPts[name];
  const bone = B[name], inv = wmat4(bone).invert(), pts = [];
  model.updateMatrixWorld(true);
  model.traverse(o => {
    if (!o.isSkinnedMesh) return;
    const bi = o.skeleton.bones.indexOf(bone); if (bi < 0) return;
    const pos = o.geometry.attributes.position, si = o.geometry.attributes.skinIndex, sw = o.geometry.attributes.skinWeight;
    const idx = []; for (let i = 0; i < pos.count; i++) for (let c = 0; c < 4; c++) if (comp(si, i, c) === bi && comp(sw, i, c) >= 0.5) { idx.push(i); break; }
    const step = Math.max(1, Math.floor(idx.length / 160));
    for (let j = 0; j < idx.length; j += step) {
      const v = new V3().fromBufferAttribute(pos, idx[j]); o.boneTransform(idx[j], v); o.localToWorld(v); pts.push(v.applyMatrix4(inv));
    }
  });
  return (propPts[name] = pts);
}
function propGap(pts, q, pos, c) {  // closest prop point to c with the prop at (q, pos); returns [dist, point]
  let best = 1e9, bp = null;
  for (const p of pts) { const w = p.clone().applyQuaternion(q).add(pos), d = w.distanceTo(c); if (d < best) { best = d; bp = w; } }
  return [best, bp];
}
// ---------------------------------------------------------------- body collision for the springs (phase 2)
// A spring part may not push its segments (its bone and everything below it: shoulder -> forearm -> hand + shield)
// deeper into another body segment than the key pose itself does. Moving geometry = surface points (radius 0) + core
// axis samples (radius = core r) of the moved segments, in the part bone's frame; obstacles = the cores of the segments
// they are paired with (BODY.pairs). Inside the sub-steps the same inelastic contact as the props (turn out about the
// pivot by the depth, kill the speed into it); a bisection toward the key pose is the safety net.
function bodyMovers(bone) {            // body segments that turn with `bone`
  const out = [];
  for (const k of Object.keys(BODY.caps)) { for (let o = B[k]; o; o = o.parent) if (o === B[bone]) { out.push(k); break; } }
  return out;
}
function bodyLink(bone, extraExcl) {   // -> {mov, obs, valid}: what moves, what it may hit (cores), which pairs count
  const mov = bodyMovers(bone), ms = new Set(mov), pairOK = new Set(), obs = new Set();
  for (const [a, b] of BODY.pairs) {
    if (BODY.props.includes(a) || BODY.props.includes(b)) continue;
    if (ms.has(a) && !ms.has(b)) { obs.add(b); pairOK.add(a + "~" + b); }
    else if (ms.has(b) && !ms.has(a)) { obs.add(a); pairOK.add(b + "~" + a); }
  }
  for (const e of extraExcl || []) obs.delete(e);
  const O = [...obs].filter(o => BODY.caps[o]); O.push("__floor");          // fall pack: the floor for every moved segment
  return { mov, obs: O, valid: O.map(o => mov.map(k => o === "__floor" || pairOK.has(k + "~" + o))) };
}
function bodyMovPts(bone, link) {      // points in the bone's unit frame at the current (key) pose
  const inv = wmat4(B[bone]).invert(), X = [], R = [], K = [], ax = [];
  link.mov.forEach((k, ki) => {
    const M = inv.clone().multiply(wmat4(B[k])), c = BODY.caps[k];
    (BODY.shells[k] || []).forEach((p, i) => { if (i % 2) return; const q = p.clone().applyMatrix4(M); X.push(q.x, q.y, q.z); R.push(0); K.push(ki); });   // half the surface (cost)
    for (let i = 0; i <= 4; i++) { const q = c.a.clone().lerp(c.b, i / 4).applyMatrix4(M); X.push(q.x, q.y, q.z); R.push(c.r); K.push(ki); }
    ax.push({ a: c.a.clone().applyMatrix4(M), b: c.b.clone().applyMatrix4(M), reach: BODY.reach[k] });   // for pruning
  });
  return { X: Float64Array.from(X), R: Float64Array.from(R), K: Int32Array.from(K), ax };
}
function bodyObsWorld(link) {          // obstacle cores in world space now (+ the floor plane)
  return link.obs.map(o => { if (o === "__floor") return { plane: true, y: 0 };
    const c = BODY.caps[o], M = wmat4(B[o]), a = c.a.clone().applyMatrix4(M), b = c.b.clone().applyMatrix4(M); return { a, b, r: c.r }; });
}
// visit every (point, obstacle) overlap with the bone turned to q about pivot: fn(pen, wx, wy, wz, cx, cy, cz)
function bodyOverlaps(q, pivot, mp, ob, link, allow, fn) {
  const e = new THREE.Matrix4().makeRotationFromQuaternion(q).elements, n = mp.R.length;
  const wa = mp.ax.map(s => ({ a: s.a.clone().applyQuaternion(q).add(pivot), b: s.b.clone().applyQuaternion(q).add(pivot), reach: s.reach }));
  for (let oi = 0; oi < ob.length; oi++) {
    const o = ob[oi];
    if (o.plane) {                      // the floor: a point (radius R) may not go below y (minus what the key pose allows)
      const ok = link.valid[oi].map((v, ki) => v && Math.min(wa[ki].a.y, wa[ki].b.y) - wa[ki].reach < o.y + 0.05), al = allow ? allow[oi] : null;
      if (!ok.some(Boolean)) continue;
      for (let i = 0; i < n; i++) {
        const ki = mp.K[i]; if (!ok[ki]) continue;
        const x = mp.X[3 * i], y = mp.X[3 * i + 1], z = mp.X[3 * i + 2];
        const wx = e[0] * x + e[4] * y + e[8] * z + pivot.x, wy = e[1] * x + e[5] * y + e[9] * z + pivot.y, wz = e[2] * x + e[6] * y + e[10] * z + pivot.z;
        const pen = o.y + mp.R[i] - wy - (al ? al[ki] : 0);
        if (pen > 0) fn(pen, wx, wy, wz, wx, wy - 1, wz, oi, ki);
      }
      continue;
    }
    const ax = o.a.x, ay = o.a.y, az = o.a.z, dx = o.b.x - ax, dy = o.b.y - ay, dz = o.b.z - az, L2 = Math.max(dx * dx + dy * dy + dz * dz, 1e-12);
    const ok = link.valid[oi].map((v, ki) => v && segSegDist(wa[ki].a, wa[ki].b, o.a, o.b) <= wa[ki].reach + o.r), al = allow ? allow[oi] : null;
    if (!ok.some(Boolean)) continue;
    for (let i = 0; i < n; i++) {
      const ki = mp.K[i]; if (!ok[ki]) continue;
      const x = mp.X[3 * i], y = mp.X[3 * i + 1], z = mp.X[3 * i + 2];
      const wx = e[0] * x + e[4] * y + e[8] * z + pivot.x, wy = e[1] * x + e[5] * y + e[9] * z + pivot.y, wz = e[2] * x + e[6] * y + e[10] * z + pivot.z;
      let t = ((wx - ax) * dx + (wy - ay) * dy + (wz - az) * dz) / L2; t = t < 0 ? 0 : t > 1 ? 1 : t;
      const cx = ax + dx * t, cy = ay + dy * t, cz = az + dz * t, d = Math.sqrt((cx - wx) ** 2 + (cy - wy) ** 2 + (cz - wz) ** 2);
      const pen = o.r + mp.R[i] - d - (al ? al[ki] : 0);
      if (pen > 0) fn(pen, wx, wy, wz, cx, cy, cz, oi, ki);
    }
  }
}
function bodyAllow(q, pivot, mp, ob, link) {   // how deep the key pose itself goes, per obstacle x moving segment
  const al = ob.map(() => new Float64Array(link.mov.length));
  bodyOverlaps(q, pivot, mp, ob, link, null, (pen, wx, wy, wz, cx, cy, cz, oi, ki) => { if (pen > al[oi][ki]) al[oi][ki] = pen; });
  return al;
}
function bodyExcess(q, pivot, mp, ob, link, allow) { let m = 0; bodyOverlaps(q, pivot, mp, ob, link, allow, pen => { if (pen > m) m = pen; }); return m; }
function bodyPush(st, pivot, mp, ob, link, allow) {   // inelastic contact on a quaternion state {S, vel}
  let tx = 0, ty = 0, tz = 0, mx = 0, my = 0, mz = 0, sw = 0, floorHit = false;
  bodyOverlaps(st.S, pivot, mp, ob, link, allow, (pen, wx, wy, wz, cx, cy, cz, oi) => {
    if (ob[oi].plane) floorHit = true;
    const rx = wx - pivot.x, ry = wy - pivot.y, rz = wz - pivot.z, ux = cx - wx, uy = cy - wy, uz = cz - wz;
    const axx = ry * uz - rz * uy, axy = rz * ux - rx * uz, axz = rx * uy - ry * ux, l = Math.sqrt(axx * axx + axy * axy + axz * axz);
    if (l < 1e-12) return; const k = pen * pen / l; tx += axx * k; ty += axy * k; tz += axz * k; mx += wx * pen; my += wy * pen; mz += wz * pen; sw += pen;
  });
  if (!sw) return false;
  const ax = new V3(tx / sw, ty / sw, tz / sw), pen = ax.length(); if (pen < 1e-12) return false; ax.divideScalar(pen);
  const lever = Math.max(new V3(mx / sw, my / sw, mz / sw).distanceTo(pivot), CM_W);
  st.S.premultiply(new Q().setFromAxisAngle(ax, -pen / lever));
  const vin = st.vel.dot(ax); if (vin > 0) st.vel.sub(ax.multiplyScalar(vin * (1 + (floorHit ? FLOOR_BOUNCE : 0))));   // a small bounce off the floor
  return true;
}
function bodySafe(T, o, pivot, mp, ob, link, allow) {  // safety net: the largest share of the turn that adds no depth
  if (!ob.length || bodyExcess(o, pivot, mp, ob, link, allow) <= 0.05 * CM_W) return [o, false, 1];
  let lo = 0, hi = 1;
  for (let k = 0; k < 18; k++) { const m = (lo + hi) / 2; if (bodyExcess(T.clone().slerp(o, m), pivot, mp, ob, link, allow) <= 0.05 * CM_W) lo = m; else hi = m; }
  return [T.clone().slerp(o, lo), true, lo];
}
// ---------------------------------------------------------------- impacts (step 1 of docs/poselab_physics_p5_impact.md)
// A hit = an impulse at a point of the body. The body is a tree of rigid core capsules (phase 2 shapes, mass = volume x
// 1000 kg/m3, the held prop a point mass on its hand) with a free root: solving M qd = J^T j gives the root's velocity and
// every joint's relative turn speed right after the hit (a light far segment - head, hand - turns fast, the heavy pelvis
// moves slowly). The level is the visible result: the push speed of the whole body's CoM (|j| = dv x total mass).
// Then each turn is an under-damped spring offset on top of the key pose (trunk heavy, head medium, free arms light; the
// arm springs of phase 1 get the turn speed injected instead), the hips translate on a spring with the feet locked (leg
// IK), and when the capture point leaves the feet by more than 5 cm a step is taken (auto step) or reported.
const IMP_LEVEL = { light: { label: "Nhẹ", dv: 0.3, dur: 1 }, medium: { label: "Vừa", dv: 1, dur: 2 }, strong: { label: "Mạnh", dv: 2.5, dur: 3 }, launch: { label: "Hất văng", dv: 5, dur: 5 } };
const IMP_DIRS = { normal: "Vuông góc bề mặt", front: "Từ phía trước", back: "Từ phía sau", left: "Từ bên trái", right: "Từ bên phải", top: "Từ trên xuống", drag: "Kéo trên màn hình" };
const IMP_RHO = 1000, IMP_SPR = { trunk: { period: 15, bounce: 0.55, limit: 20 }, head: { period: 12, bounce: 0.62, limit: 30 }, arm: { period: 8, bounce: 0.62, limit: 35 },
  rootRot: { period: 18, bounce: 0.4, limit: 18 }, root: { K: (2 * Math.PI / 12) ** 2, C: 2 * 0.6 * 2 * Math.PI / 12 } };   // root: vertical only
const IMP_STEP = { outCm: 5, maxLen: 0.8, minWidth: 0.2, lift: 0.06, max: 3 }, IMP_TONE = 0.6;
const IMP_HIP = 0.08;                      // hip strategy: bending / arm swing moves the pressure point 8 cm past the feet
const impSpring = n => /^(Root_M|Spine1_M|Chest_M)$/.test(n) ? IMP_SPR.trunk : /^(Neck_M|Head_M)$/.test(n) ? IMP_SPR.head : IMP_SPR.arm;
const impSprK = s => { const w = 2 * Math.PI / s.period, z = 1 - s.bounce; return { w, z, wd: w * Math.sqrt(Math.max(1e-6, 1 - z * z)), K: w * w, C: 2 * z * w }; };
const impG = (s, t) => t <= 0 ? 0 : Math.exp(-s.z * s.w * t) * Math.sin(s.wd * t) / s.wd;   // unit start speed -> offset (frames)
const impList = () => ((ANIM.phys && ANIM.phys.impacts) || []).filter(i => i && (BODY ? BODY.caps[i.seg] || BODY.props.includes(i.seg) : true) && B[i.seg]);
const impDV = i => ((IMP_LEVEL[i.level] || {}).dv ?? i.dv ?? 1) * (i.mul ?? 1);
const impDur = i => Math.max(1, Math.round(i.dur ?? (IMP_LEVEL[i.level] || IMP_LEVEL.medium).dur));
const impHand = () => (P.follow && P.follow.hand) || ((ANIM.phys.parts || []).find(p => p.type === "prop") || {}).hand || "L";
function impSegs() {                       // body segments root-first: {k, par, m, ...}
  const ks = Object.keys(BODY.caps).filter(k => B[k]), segPar = k => { let o = B[k].parent; while (o && o.isBone) { if (BODY.caps[o.name]) return o.name; o = o.parent; } return null; };
  const out = ks.map(k => ({ k, par: segPar(k) }));
  const depth = s => { let d = 0, x = s.par; while (x) { d++; x = out.find(o => o.k === x).par; } return d; };
  out.forEach(s => s.d = depth(s)); out.sort((a, b) => a.d - b.d);
  return out;
}
function polyClamp(poly, q, out) {        // q if inside the convex polygon (grown by `out`), else the nearest such point
  if (polyMargin(poly, q) >= -(out || 0)) return q; let best = null, bd = 1e9;
  for (let i = 0; i < poly.length; i++) { const a = poly[i], b = poly[(i + 1) % poly.length], ex = b[0] - a[0], ey = b[1] - a[1], L2 = ex * ex + ey * ey;
    const t = L2 > 1e-12 ? Math.max(0, Math.min(1, ((q[0] - a[0]) * ex + (q[1] - a[1]) * ey) / L2)) : 0, p2 = [a[0] + ex * t, a[1] + ey * t], d = Math.hypot(p2[0] - q[0], p2[1] - q[1]);
    if (d < bd) { bd = d; best = p2; } }
  if (best && out) { const dx = q[0] - best[0], dz = q[1] - best[1], l = Math.hypot(dx, dz); if (l > 1e-9) best = [best[0] + dx / l * out, best[1] + dz / l * out]; }
  return best || q;
}
function impCom() {                       // CoM of the pose on screen (core capsules + held prop), world
  const { m, pm } = impMass(), c = new V3(); let M = 0;
  for (const [k, cp] of Object.entries(BODY.caps)) { if (!B[k]) continue; const W = wmat4(B[k]); c.addScaledVector(cp.a.clone().applyMatrix4(W).add(cp.b.clone().applyMatrix4(W)), 0.5 * m[k]); M += m[k]; }
  const prop = BODY.props[0]; if (prop && pm > 0 && BODY.shells[prop]) { const W = wmat4(B[prop]), sh = BODY.shells[prop]; c.addScaledVector(sh.reduce((s2, q) => s2.add(q.clone().applyMatrix4(W)), new V3()).divideScalar(sh.length), pm); M += pm; }
  return c.divideScalar(M);
}
function impMass() {                       // kg per segment (+ prop) and the total
  const m = {}; let M = 0;
  const rm = (RIGSET() && RIGSET().mass) || {};
  for (const [k, c] of Object.entries(BODY.caps)) { const L = c.a.distanceTo(c.b), r = c.r; m[k] = rm[k] != null ? rm[k] : IMP_RHO * (Math.PI * r * r * L + 4 / 3 * Math.PI * r ** 3); M += m[k]; }
  const pm = M * balPropPct() / 100; return { m, pm, M: M + pm };
}
// generalized velocity of the body after impulse j (world N s, at world point x on segment seg) for the pose on screen.
// dofs: root v (0-2), root w (3-5), then 3 per non-root segment (turn relative to its parent segment, world axes).
function impSolve(seg, x, j) {
  const segs = impSegs(), root = segs[0].k, idx = {}; let n = 6; for (const s of segs) if (s.par) { idx[s.k] = n; n += 3; }
  const { m, pm } = impMass(), pr = wp(B[root]), chain = k => { const c = []; let s = segs.find(o => o.k === k); while (s && s.par) { c.push(s.k); s = segs.find(o => o.k === s.par); } return c; };
  const piv = {}; for (const s of segs) piv[s.k] = wp(B[s.k]);
  const Mx = new Float64Array(n * n);
  const addPoint = (k, x0, mass, I) => {   // J^T [m 0; 0 I] J for a body on segment k with centre x0
    const ch = chain(k), cols = [[0, null], [3, pr]].concat(ch.map(c => [idx[c], piv[c]]));
    const Jv = new Float64Array(3 * n), Jw = new Float64Array(3 * n);
    for (const [c0, p] of cols) {
      if (c0 === 0) { for (let a = 0; a < 3; a++) Jv[a * n + a] = 1; continue; }
      const r = x0.clone().sub(p);                   // w x r = -[r]x w
      const R = [[0, r.z, -r.y], [-r.z, 0, r.x], [r.y, -r.x, 0]];
      for (let a = 0; a < 3; a++) for (let b = 0; b < 3; b++) { Jv[a * n + c0 + b] = R[a][b]; }
      for (let a = 0; a < 3; a++) Jw[a * n + c0 + a] = 1;
    }
    for (let p = 0; p < n; p++) for (let q = 0; q < n; q++) {
      let s = 0; for (let a = 0; a < 3; a++) s += mass * Jv[a * n + p] * Jv[a * n + q];
      if (I) for (let a = 0; a < 3; a++) for (let b = 0; b < 3; b++) s += Jw[a * n + p] * I[a][b] * Jw[b * n + q];
      Mx[p * n + q] += s;
    }
    return Jv;
  };
  for (const s of segs) {
    const c = BODY.caps[s.k], W = wmat4(B[s.k]), a = c.a.clone().applyMatrix4(W), b = c.b.clone().applyMatrix4(W), L = a.distanceTo(b), mm = m[s.k];
    const u = b.clone().sub(a).normalize(), ip = mm * (3 * c.r * c.r + L * L) / 12, ia = 0.5 * mm * c.r * c.r, uu = [u.x, u.y, u.z];
    const I = [0, 1, 2].map(r => [0, 1, 2].map(q => ip * ((r === q ? 1 : 0) - uu[r] * uu[q]) + ia * uu[r] * uu[q]));
    addPoint(s.k, a.clone().add(b).multiplyScalar(0.5), mm, I);
  }
  const prop = BODY.props[0], hk = "Wrist_" + impHand();
  if (prop && pm > 0 && BODY.caps[hk] && BODY.shells[prop]) { const W = wmat4(B[prop]), sh = BODY.shells[prop]; const c = sh.reduce((s, q) => s.add(q.clone().applyMatrix4(W)), new V3()).divideScalar(sh.length); addPoint(hk, c, pm, null); }
  const onSeg = BODY.caps[seg] ? seg : hk;            // a hit on the prop goes to the hand holding it
  const Jx = addPoint(onSeg, x, 0, null);            // mass 0: only the point's Jacobian
  const Qv = new Float64Array(n); for (let p = 0; p < n; p++) Qv[p] = Jx[p] * j.x + Jx[n + p] * j.y + Jx[2 * n + p] * j.z;
  let tr = 0; for (let p = 0; p < n; p++) tr = Math.max(tr, Mx[p * n + p]); for (let p = 0; p < n; p++) Mx[p * n + p] += 1e-9 * tr;
  const L = new Float64Array(n * n);                  // Cholesky
  for (let i = 0; i < n; i++) for (let k = 0; k <= i; k++) {
    let s = Mx[i * n + k]; for (let t = 0; t < k; t++) s -= L[i * n + t] * L[k * n + t];
    L[i * n + k] = i === k ? Math.sqrt(Math.max(s, 1e-12)) : s / L[k * n + k];
  }
  const y = new Float64Array(n); for (let i = 0; i < n; i++) { let s = Qv[i]; for (let t = 0; t < i; t++) s -= L[i * n + t] * y[t]; y[i] = s / L[i * n + i]; }
  const qd = new Float64Array(n); for (let i = n - 1; i >= 0; i--) { let s = y[i]; for (let t = i + 1; t < n; t++) s -= L[t * n + i] * qd[t]; qd[i] = s / L[i * n + i]; }
  // muscle tone: blend with the joints-locked answer (the same mass model, root dofs only = one rigid body). Both carry the
  // full momentum j, so any blend does too. Fully limp (tone 0) flung the chest at ~10 m/s while the hips barely moved.
  const qr = (() => { const A = [...Array(6)].map((_, r) => [...Array(6)].map((_, c) => Mx[r * n + c]).concat(Qv[r]));
    for (let c = 0; c < 6; c++) { let pv = c; for (let r = c + 1; r < 6; r++) if (Math.abs(A[r][c]) > Math.abs(A[pv][c])) pv = r; [A[c], A[pv]] = [A[pv], A[c]];
      for (let r = 0; r < 6; r++) if (r !== c) { const k = A[r][c] / A[c][c]; for (let q = c; q < 7; q++) A[r][q] -= k * A[c][q]; } }
    return A.map((r, i) => r[6] / r[i]); })();
  const tone = Math.max(0, Math.min(1, ANIM.phys.tone ?? IMP_TONE));
  for (let p = 0; p < n; p++) qd[p] = (1 - tone) * qd[p] + tone * (p < 6 ? qr[p] : 0);
  const v3 = o => new V3(qd[o], qd[o + 1], qd[o + 2]), rel = {}; for (const s of segs) if (s.par) rel[s.k] = v3(idx[s.k]);
  const abs = {}; for (const s of segs) abs[s.k] = (s.par ? abs[s.par].clone() : v3(3)).add(s.par ? rel[s.k] : new V3());
  let ke = 0; for (let p = 0; p < n; p++) { let s = 0; for (let q = 0; q < n; q++) s += (Mx[p * n + q]) * qd[q]; ke += 0.5 * qd[p] * s; }
  return { root, v: v3(0), w: v3(3), rel, abs, ke, qd: [...qd] };
}
function impPointW(i) {                    // impact point + push direction in world space for the pose on screen
  const W = wmat4(B[i.seg]), x = new V3(...i.p).applyMatrix4(W);
  let d;
  if (i.dirMode === "normal" || !i.dir) {
    const c = BODY.caps[i.seg]; if (c) { const a = c.a.clone().applyMatrix4(W), b = c.b.clone().applyMatrix4(W); d = closestOnSeg(x, a, b).sub(x); }
    else { const sh = BODY.shells[i.seg]; d = sh.reduce((s, q) => s.add(q.clone().applyMatrix4(W)), new V3()).divideScalar(sh.length).sub(x); }
    if (d.lengthSq() < 1e-10) d = new V3(0, 0, -1);
  } else d = new V3(...i.dir);
  return { x, d: d.normalize() };
}
function impDirPreset(mode) {              // force coming FROM that side -> push direction (glTF: character faces +Z, right = -X)
  return { front: CF.clone().negate(), back: CF.clone(), left: CR.clone(), right: CR.clone().negate(), top: CU.clone().negate() }[mode] || null;
}
// prepares the impact stage for computePhysCore: per impact its solve at its frame (key pose) and the springs
function impPrepare() {
  const L = impList().filter(i => !ragOn() || i.f < ANIM.phys.rag.from); if (!L.length || P.loop) return null;   // hits from the ragdoll's start go to the ragdoll
  const fps = P.fps || 30, { M } = impMass(), hits = [];
  for (const i of L) {
    evalPose(i.f); model.updateMatrixWorld(true);
    const { x, d } = impPointW(i), dur = impDur(i), j = d.clone().multiplyScalar(impDV(i) * M);
    const r = impSolve(i.seg, x, j); hits.push({ i, f: i.f, dur, x, d, j, r, parQ: {} });
    const h = hits[hits.length - 1], segs0 = impSegs(); for (const k of Object.keys(r.rel)) h.parQ[k] = wq(B[segs0.find(s => s.k === k).par]);
  }
  hits.sort((a, b) => a.f - b.f);
  const f0 = hits[0].f; evalPose(Math.max(1, f0 - 1)); model.updateMatrixWorld(true); const comPrev = impCom();
  const segs = impSegs(), root = segs[0].k, sp = {}; for (const s of segs) if (s.par) sp[s.k] = impSprK(impSpring(s.k));
  return { hits, segs, root, sp, spRot: impSprK(IMP_SPR.rootRot), fps, M,
    x: new V3(), v: new V3(), foot: { L: new V3(), R: new V3() }, stepping: null, steps: [], need: [], fell: null, nSteps: 0, comPrev, rec: {} };
}
// parts (phase 1 springs) that the hit turns directly: world turn speed (rad / frame) per bone at frame f
function impInject(S, f, bone) {
  if (!S) return null; let w = null;
  const g = bodyGroup(bone), seg = BODY.caps[g] ? g : BODY.props.includes(bone) ? "Wrist_" + impHand() : null; if (!seg) return null;
  for (const h of S.hits) if (f >= h.f && f < h.f + h.dur && h.r.abs[seg]) { (w ||= new V3()).addScaledVector(h.r.abs[seg], 1 / S.fps / h.dur); }
  return w;
}
const impPartBones = () => new Set((ANIM.phys.parts || []).filter(p => B[p.bone]).map(p => p.bone));
function impContact(s, f) {                // key pose: is foot s planted at f (painted lanes win, else the sole near the floor)
  if (CT.L.size + CT.R.size) return CT[s].has(cyc(f));
  const sh = BODY.shells["Ankle_" + s]; if (!sh) return false; const W = wmat4(B["Ankle_" + s]);
  let lo = 1e9; for (const q of sh) lo = Math.min(lo, q.clone().applyMatrix4(W).y); return lo < BAL_GROUND_CM * CM_W;
}
// the impact stage of frame f: called with the key pose of f on screen (after evalPose), leaves the moved pose on screen
function impApply(S, f, first) {
  if (!S || !S.hits.length || f < S.hits[0].f) return;
  const fps = S.fps, root = B[S.root], keyAnk = {}, keyCon = {};
  for (const s of ["L", "R"]) { const a = B[LEGS[s][2]]; if (a) keyAnk[s] = { p: wp(a), q: wq(a) }; keyCon[s] = impContact(s, f); }
  const rel = hasFollow() ? relAt(f) : null, partB = impPartBones(), followArm = hasFollow() ? P.follow.hand : null;
  const comKey = impCom(), vKey = comKey.clone().sub(S.comPrev).multiplyScalar(fps); S.comPrev = comKey.clone();
  // steps: the moving foot follows its arc; afterwards the offset stays until the key itself lifts that foot
  if (S.stepping) {
    const st = S.stepping, u = Math.min(1, (f - st.f0) / (st.f1 - st.f0));
    S.foot[st.s] = st.from.clone().lerp(st.to, smooth01(u)).setY(Math.sin(Math.PI * u) * IMP_STEP.lift);
    if (u >= 1) { S.foot[st.s].setY(0); S.stepping = null; }
  }
  for (const s of ["L", "R"]) if (!keyCon[s] && !(S.stepping && S.stepping.s === s)) S.foot[s].multiplyScalar(0.75);
  // support now: the planted feet moved by their step offsets (the stepping foot is in the air)
  const feet = {}, pts = [];
  for (const s of ["L", "R"]) {
    const sh = BODY.shells["Ankle_" + s]; if (!sh) continue; const W = wmat4(B["Ankle_" + s]), o = S.foot[s];
    feet[s] = sh.map(q => q.clone().applyMatrix4(W).add(o)); feet[s].c = feet[s].reduce((a2, q) => a2.add(q), new V3()).divideScalar(feet[s].length);
    if (keyCon[s] && !(S.stepping && S.stepping.s === s)) for (const q of feet[s]) if (q.y < BAL_GROUND_CM * CM_W + o.y) pts.push([q.x, q.z]);
  }
  const hull = hull2(pts);
  // CoM offset on the floor = linear inverted pendulum (x'' = w0^2 (x - u)): the legs can only push the centre of pressure
  // u around INSIDE the feet; u aims to bring the capture point back (u = rest + 2 (xi - rest)). A push whose capture point
  // leaves the feet cannot be held: that is when a step is needed. (A plain spring on the hips swallowed a 5 m/s push.)
  for (const h of S.hits) if (f >= h.f && f < h.f + h.dur) S.v.addScaledVector(h.j, 1 / S.M / fps / h.dur);   // the CoM's own speed: j / M
  const w0 = Math.sqrt(BAL_G / Math.max(0.3, comKey.y)) / fps, rest = S.foot.L.clone().add(S.foot.R).multiplyScalar(0.5).setY(0), NS = 8;
  const copK = (() => { const ptsK0 = []; for (const s of ["L", "R"]) if (feet[s] && keyCon[s]) for (const q of feet[s]) { const k = q.clone().sub(S.foot[s]); if (k.y < BAL_GROUND_CM * CM_W) ptsK0.push([k.x, k.z]); }
    const hk = hull2(ptsK0); return hk.length ? polyClamp(hk, [comKey.x, comKey.z]) : [comKey.x, comKey.z]; })();
  if (!first) for (let k = 0; k < NS; k++) {
    const xi = [S.x.x + S.v.x / w0, S.x.z + S.v.z / w0];
    let u = [rest.x + 2 * (xi[0] - rest.x), rest.z + 2 * (xi[1] - rest.z)];
    if (hull.length) { const c = polyClamp(hull, [copK[0] + u[0], copK[1] + u[1]], IMP_HIP); u = [c[0] - copK[0], c[1] - copK[1]]; } else u = [S.x.x, S.x.z];
    const ax = w0 * w0 * (S.x.x - u[0]), az = w0 * w0 * (S.x.z - u[1]), ay = IMP_SPR.root.K * (0 - S.x.y) - IMP_SPR.root.C * S.v.y;
    S.v.x += ax / NS; S.v.z += az / NS; S.v.y += ay / NS; S.x.addScaledVector(S.v, 1 / NS);
  }
  S.x.y = Math.max(-0.15, Math.min(0.05, S.x.y));
  // capture point vs the planted feet
  const com = comKey.clone().add(S.x), v = vKey.clone().add(S.v.clone().multiplyScalar(fps)), wS = w0 * fps;
  const cp = [com.x + v.x / wS, com.z + v.z / wS], mg = hull.length ? polyMargin(hull, cp) : -1;
  // the key pose's own balance at f (its own steps are acting, not the hit's): only what the hit ADDS triggers a step
  const ptsK = []; for (const s of ["L", "R"]) if (feet[s] && keyCon[s]) for (const q of feet[s]) { const k = q.clone().sub(S.foot[s]); if (k.y < BAL_GROUND_CM * CM_W) ptsK.push([k.x, k.z]); }
  const wK = Math.sqrt(BAL_G / Math.max(0.3, comKey.y)), hullK = hull2(ptsK), mgK = hullK.length ? polyMargin(hullK, [comKey.x + vKey.x / wK, comKey.z + vKey.z / wK]) : 0;
  const worse = Math.min(0, mgK) - mg;                // how much further out than the key itself
  const sp = Math.hypot(S.v.x, S.v.z) * fps, Ts = Math.max(8, Math.min(10, Math.round(10 - 3 * (sp - 0.5))));   // the hit's own speed (m/s)
  const planted = s => !(CT.L.size + CT.R.size) || [...Array(Ts + 1)].every((_, t) => CT[s].has(cyc(f + t)));
  S.rec[f] = { x: S.x.toArray(), foot: { L: S.foot.L.toArray(), R: S.foot.R.toArray() }, cp, mg, mgK, com: com.toArray() };
  if (!S.stepping && hull.length && worse > IMP_STEP.outCm * CM_W && f >= S.hits[0].f) {
    const d = new V3(cp[0] - com.x, 0, cp[1] - com.z); if (d.lengthSq() < 1e-8) d.set(0, 0, -1); d.normalize();
    // per foot: lifting it leaves only the other foot to push on, and the capture point runs away from that foot
    // (xi(t) = u + (xi - u) e^(w0 t)); the foot lands where xi will be then. The shorter feasible step wins (lifting the
    // loaded foot - the one the body leans over - makes the other far away and the step huge).
    const gr = Math.exp(w0 * Ts);
    let best = null;
    for (const s of ["L", "R"]) {
      if (!feet[s] || !keyCon[s] || !planted(s)) continue; const o = s === "L" ? "R" : "L"; if (!feet[o]) continue;
      const po = []; for (const q of feet[o]) if (q.y < BAL_GROUND_CM * CM_W + S.foot[o].y) po.push([q.x, q.z]);
      const ho = hull2(po), uo = ho.length ? polyClamp(ho, cp, IMP_HIP) : [feet[o].c.x, feet[o].c.z];
      const T = new V3(uo[0] + (cp[0] - uo[0]) * gr, 0, uo[1] + (cp[1] - uo[1]) * gr).addScaledVector(d, 0.05);
      const side = feet[s].c.clone().sub(feet[o].c).setY(0); const sd = side.length() > 1e-4 ? side.normalize() : (s === "L" ? CR.clone().negate() : CR.clone());
      const t = T.clone(), off = t.clone().sub(feet[o].c).setY(0).dot(sd); if (off < IMP_STEP.minWidth) t.addScaledVector(sd, IMP_STEP.minWidth - off);
      const dl = t.clone().sub(feet[s].c).setY(0), need = dl.length(); if (need > IMP_STEP.maxLen) dl.setLength(IMP_STEP.maxLen);
      if (!best || need < best.need) best = { s, dl, need };
    }
    if (best && S.fell == null && best.need > 2 * IMP_STEP.maxLen) S.fell = f;      // no step can catch it: a fall
    else if (best && S.fell == null && ANIM.phys.autoStep !== false && S.nSteps < IMP_STEP.max) {
      S.stepping = { s: best.s, f0: f, f1: f + Ts, from: S.foot[best.s].clone(), to: S.foot[best.s].clone().add(best.dl) }; S.nSteps++;
      S.steps.push({ s: best.s, f0: f, f1: f + Ts, cm: Math.round(best.dl.length() / CM_W), to: feet[best.s].c.clone().add(best.dl).setY(0).toArray() });
    } else if (best && ANIM.phys.autoStep === false) { if (!S.need.length || f - S.need[S.need.length - 1].f > 6) S.need.push({ f, s: best.s, to: feet[best.s].c.clone().add(best.dl).setY(0).toArray(), cm: Math.round(worse / CM_W) }); }
    else if (S.fell == null && S.nSteps >= IMP_STEP.max && !S.stepping) S.fell = f;
  }
  if (S.fell != null) S.v.multiplyScalar(0.6);       // beyond 3 steps it is a fall (step 2: ragdoll); here the slide stops
  // pose: hips (turn + move), trunk / head / free arms (spring offsets), legs back onto the (stepped) feet, prop + hand
  const ed = edited; edited = new Set();
  { let rv = new V3(); const capR = THREE.MathUtils.degToRad(IMP_SPR.rootRot.limit) * S.spRot.w * fps;
    for (const h of S.hits) { const w = h.r.w.clone(); if (w.length() > capR) w.setLength(capR); for (let k = 0; k < h.dur; k++) rv.addScaledVector(w, impG(S.spRot, f - h.f - k) / fps / h.dur); }
    const a = rv.length(); if (a > 1e-9) rv.multiplyScalar(softLimit(a, THREE.MathUtils.degToRad(IMP_SPR.rootRot.limit)) / a);
    const q = qrv(rv), pr = wp(root), c = comKey, to = c.clone().add(pr.clone().sub(c).applyQuaternion(q)).add(S.x);   // turn about the CoM, then move
    rotateWorld(root, q); root.parent.updateMatrixWorld(true); root.position.copy(root.parent.worldToLocal(to)); model.updateMatrixWorld(true); }
  for (const s of S.segs) {
    if (!s.par || /^(Hip|Knee|Ankle)_/.test(s.k) || partB.has(s.k)) continue;
    if (followArm && /^(Shoulder|Elbow|Wrist)_/.test(s.k) && s.k.endsWith(followArm)) continue;
    const sp = S.sp[s.k], loc = new V3();
    const capW = THREE.MathUtils.degToRad(impSpring(s.k).limit) * sp.w * fps;   // rad/s that swings exactly to the limit
    for (const h of S.hits) { const q = h.parQ[s.k]; if (!q) continue; const wl = h.r.rel[s.k].clone().applyQuaternion(q.clone().invert()); if (wl.length() > capW) wl.setLength(capW);
      for (let k = 0; k < h.dur; k++) loc.addScaledVector(wl, impG(sp, f - h.f - k) / fps / h.dur); }
    const a = loc.length(); if (a < 1e-9) continue; loc.multiplyScalar(softLimit(a, THREE.MathUtils.degToRad(impSpring(s.k).limit)) / a);
    rotateWorld(B[s.k], qrv(loc.applyQuaternion(wq(B[s.par])))); model.updateMatrixWorld(true);
  }
  for (const s of ["L", "R"]) if (keyAnk[s]) { solve2(LEGS[s], keyAnk[s].p.clone().add(S.foot[s]), keyAnk[s].q); model.updateMatrixWorld(true); }
  if (rel) propHandTo(B[P.follow.to].matrixWorld.clone().multiply(relM(rel.w)), relM(rel.h));
  edited = ed; model.updateMatrixWorld(true);
}
// ---------------------------------------------------------------- ragdoll (step 2 of docs/poselab_physics_p5_impact.md)
// Each body segment = a rigid core capsule (phase 2 shape; mass = volume x 1000 kg/m3, at least 4 kg), joined to its parent
// segment by a ball joint at the child bone's origin; the neck rides the chest; a held prop is part of its hand's body.
// XPBD (Mueller et al. 2020), 20 sub-steps per frame. Positions: muscles (each joint pulled toward the key pose's turn,
// softness from the "Sức" curve), then 2 passes of joint limits (bend / spread / twist box around the rest pose, measured on
// the approved clips) and joint positions, then the floor (surface points, static friction). Velocities: floor bounce 15 %
// + sliding friction, body vs body and a loose prop vs the cores (velocity only), rolling resistance, inelastic limits,
// joint damping. A limp body that has stopped sleeps. Twin: tools/physics_sim.py (--ragdoll).
const RAG_MMIN = 4, RAG_IMIN = 0.02, RAG_PASSIVE = 8, RAG_ROLL = 12;   // passive joint damping and rolling resistance on the floor (1/s): a limp Gaygor settles ~1 s after landing
const RAG_LIM_A = 0, RAG_LIM_D = 100, RAG_SLEEP_CM = 2.5, RAG_SLEEP_F = 6;   // joint limit softness (rad / N m), extra damping on a joint at its limit (1/s)
const RAG_BSEP = 0.1, RAG_BBIAS = 2, RAG_SLOP = 0.005;   // body contacts: separating speed (m/s) per metre of depth past 5 mm, at most 0.1 m/s (more kept a leg resting on the other one twitching)
const RAG_LIM_OVER = { Head_M: [-80, 80, -60, 60, -90, 90] };   // head on the chest: the neck's range + the head's
const RAG_SUB = 20, RAG_JIT = 2, RAG_C0 = 1e-6, RAG_MU_S = 0.8, RAG_MU_D = 0.6, RAG_DAMP = 18, RAG_PTS = 400, RAG_PTS_PROP = 400,   /* every surface point (fewer let the lying armor sink 3-10 cm between them) */ RAG_REST_CM = 1;
// strength per part (step 3): trunk, head, each arm, each leg (older settings had arms / legs for both sides)
const RAG_GROUP = n => n === "Head_M" ? "head" : /^(Hip|Knee|Ankle)_/.test(n) ? "leg" + n.slice(-1) : /^(Shoulder|Elbow|Wrist)_/.test(n) ? "arm" + n.slice(-1) : "trunk";
const RAG_GROUP_LABEL = { trunk: "Thân", head: "Đầu", armL: "Tay trái", armR: "Tay phải", legL: "Chân trái", legR: "Chân phải" };
const ragGroupF = (gm, g) => gm[g] ?? gm[g === "head" ? "trunk" : g.startsWith("arm") ? "arms" : g.startsWith("leg") ? "legs" : g] ?? 1;
// balance (step 3): while there is strength in the legs, a foot on the floor and the capture point inside the feet (+ the
// 8 cm hip strategy), the hips are pulled toward the key pose's hips (turn + the floor plane), no faster than the feet's
// friction can push the whole body (mu g). Outside the feet nothing holds it: it falls ("cần bước", as in step 1).
const RAG_CB = 1e-6, RAG_CBP = 2e-5, RAG_SOLE = 0.02;
// limits per joint (deg): bend about the bone's local Z (lo, hi), spread about the other axis (lo, hi), twist (lo, hi)
const ragLimits = () => (charPhys() || {}).limits || {};
function ragAxes(k) {                     // twist axis (segment direction) + the two swing axes, in the child bone frame
  const c = BODY.caps[k], t = c.b.clone().sub(c.a).normalize();
  let e1 = new V3(0, 0, 1); e1.sub(t.clone().multiplyScalar(e1.dot(t))); if (e1.lengthSq() < 1e-6) { e1 = new V3(1, 0, 0); e1.sub(t.clone().multiplyScalar(e1.dot(t))); }
  e1.normalize(); return { t, e1, e2: t.clone().cross(e1) };
}
function ragSplit(d, ax) {                // deviation from rest (child frame) -> [bend, spread, twist] (rad)
  const dq = d.w < 0 ? new Q(-d.x, -d.y, -d.z, -d.w) : d.clone();
  let tw = 2 * Math.atan2(dq.x * ax.t.x + dq.y * ax.t.y + dq.z * ax.t.z, dq.w); if (tw > Math.PI) tw -= 2 * Math.PI; if (tw < -Math.PI) tw += 2 * Math.PI;
  const sw = dq.clone().multiply(new Q().setFromAxisAngle(ax.t, tw).invert()), s = qlog(sw);
  return [s.dot(ax.e1), s.dot(ax.e2), tw];
}
function ragJoin(a, ax) { return qrv(ax.e1.clone().multiplyScalar(a[0]).add(ax.e2.clone().multiplyScalar(a[1]))).multiply(new Q().setFromAxisAngle(ax.t, a[2])); }
function qlog(q) {                        // rotation vector of a unit quaternion (shortest)
  const w = q.w < 0 ? -1 : 1, x = q.x * w, y = q.y * w, z = q.z * w, s = Math.sqrt(x * x + y * y + z * z); if (s < 1e-12) return new V3();
  const a = 2 * Math.atan2(s, q.w * w); return new V3(x, y, z).multiplyScalar(a / s);
}
// the neck (core 2 cm, 0.3 kg) is not a body: it rides the chest and the head hangs on the chest (limits = neck + head)
const RAG_SKIP = new Set(["Neck_M"]);
function ragSegs() {
  const ks = Object.keys(BODY.caps).filter(k => B[k] && !RAG_SKIP.has(k)), has = new Set(ks);
  const par = k => { let o = B[k].parent; while (o && o.isBone) { if (has.has(o.name)) return o.name; o = o.parent; } return null; };
  const out = ks.map(k => ({ k, par: par(k) })), depth = s => { let d = 0, x = s.par; while (x) { d++; x = out.find(o => o.k === x).par; } return d; };
  out.forEach(s => s.d = depth(s)); return out.sort((a, b) => a.d - b.d);
}
function ragRest() {                       // rest-pose relative turns per joint (child frame of the parent segment)
  const segs = ragSegs(), ch = charPhys() || {}, q0 = {};
  withPose(ch.rest || null, () => { for (const s of segs) if (s.par) q0[s.k] = wq(B[s.par]).invert().multiply(wq(B[s.k])); });
  return q0;
}
function ragRel(k, par, q0) { return q0.clone().invert().multiply(wq(B[par]).invert().multiply(wq(B[k]))); }
// ---- strength curve: points [frame, %] -> 0..1 at any frame (smooth between points, held outside)
function ragStrength(f) {
  const R = ANIM.phys.rag; const pts = (R && R.pts || []).slice().sort((a, b) => a[0] - b[0]); if (!pts.length) return 1;
  if (f <= pts[0][0]) return pts[0][1] / 100; if (f >= pts[pts.length - 1][0]) return pts[pts.length - 1][1] / 100;
  let i = 0; while (i < pts.length - 2 && pts[i + 1][0] <= f) i++;
  const [a, b] = [pts[i], pts[i + 1]], u = smooth01((f - a[0]) / Math.max(1e-6, b[0] - a[0])); return (a[1] + (b[1] - a[1]) * u) / 100;
}
const ragOn = () => !!(ANIM.phys && ANIM.phys.rag && ANIM.phys.rag.on && !P.loop);
// ---- bodies
function ragBuild(q0) {                    // bodies from the pose on screen: segments (+ prop), joints, contact points
  const { m, pm } = impMass(), segs = ragSegs(), bodies = {}, R = ANIM.phys.rag, lim = { ...ragLimits(), ...RAG_LIM_OVER };
  const mk = (k, mass, cLoc, Iloc, pts) => {
    const q = wq(B[k]), x = cLoc.clone().applyQuaternion(q).add(wp(B[k]));
    const Ii = Iloc.clone().invert();
    return { k, m: mass, im: 1 / mass, c: cLoc, I: Iloc.clone(), Ii, x, q, v: new V3(), w: new V3(), xp: x.clone(), qp: q.clone(), pts, vn: [] };
  };
  // contact points: farthest-point sampling (every corner of the armor gets one; an even stride let a lying body sink 7-10 cm
  // between its 22 points, Gaygor Die 2026-10-25)
  const sample = (sh, n) => { if (sh.length <= n) return sh.slice(); const c = sh.reduce((a, p) => a.add(p), new V3()).divideScalar(sh.length);
    let i0 = 0; sh.forEach((p, i) => { if (p.distanceToSquared(c) > sh[i0].distanceToSquared(c)) i0 = i; });
    const out = [sh[i0]], d = sh.map(p => p.distanceToSquared(sh[i0]));
    while (out.length < n) { let k = 0; for (let i = 1; i < sh.length; i++) if (d[i] > d[k]) k = i; out.push(sh[k]); for (let i = 0; i < sh.length; i++) d[i] = Math.min(d[i], sh[i].distanceToSquared(sh[k])); }
    return out; };
  for (const s of segs) {
    const c = BODY.caps[s.k], L = c.a.distanceTo(c.b), mm = m[s.k], u = c.b.clone().sub(c.a).normalize(), uu = [u.x, u.y, u.z];
    const ip = Math.max(mm * (3 * c.r * c.r + L * L) / 12, RAG_IMIN), ia = Math.max(0.5 * mm * c.r * c.r, RAG_IMIN), I = new THREE.Matrix3();
    I.set(...[0, 1, 2].flatMap(r => [0, 1, 2].map(q => ip * ((r === q ? 1 : 0) - uu[r] * uu[q]) + ia * uu[r] * uu[q])));
    const cl = c.a.clone().add(c.b).multiplyScalar(0.5), sh = sample(BODY.shells[s.k] || [], RAG_PTS).map(p => p.clone().sub(cl));
    bodies[s.k] = mk(s.k, Math.max(mm, RAG_MMIN), cl, I, sh); bodies[s.k].cap = { a: c.a.clone().sub(cl), b: c.b.clone().sub(cl), r: c.r };
  }
  const prop = BODY.props[0], hand = "Wrist_" + impHand();
  if (prop && pm > 0 && B[prop] && BODY.shells[prop] && bodies[hand]) {
    const sh = BODY.shells[prop], cl = sh.reduce((a, p) => a.add(p), new V3()).divideScalar(sh.length);
    const I = new THREE.Matrix3(), e = [0, 0, 0, 0, 0, 0, 0, 0, 0], w = pm / sh.length;
    for (const p of sh) { const d = p.clone().sub(cl), dl = [d.x, d.y, d.z], l2 = d.lengthSq(); for (let r = 0; r < 3; r++) for (let q = 0; q < 3; q++) e[r * 3 + q] += w * ((r === q ? l2 : 0) - dl[r] * dl[q]); }
    for (let r = 0; r < 3; r++) e[r * 3 + r] += 1e-4 * pm; I.set(...e);
    bodies[prop] = mk(prop, pm, cl, I, sample(sh, RAG_PTS_PROP).map(p => p.clone().sub(cl))); bodies[prop].prop = true;
  }
  const joints = [];
  for (const s of segs) if (s.par) {
    const pb = bodies[s.par], cb = bodies[s.k];
    const rP = wp(B[s.k]).sub(wp(B[s.par])).applyQuaternion(wq(B[s.par]).invert()).sub(pb.c);     // child origin in the parent body frame
    const L = lim[s.k] || [-180, 180, -180, 180, -180, 180];
    joints.push({ k: s.k, par: s.par, c: cb, p: pb, rC: cb.c.clone().negate(), rP, q0: q0[s.k], ax: ragAxes(s.k), lim: L.map(THREE.MathUtils.degToRad), grp: RAG_GROUP(s.k) });
  }
  // body pairs (cores) that may collide, never deeper than at the start
  const pairs = [];
  for (const [a, b] of BODY.pairs) if (bodies[a] && bodies[b] && !bodies[a].prop && !bodies[b].prop) pairs.push({ a: bodies[a], b: bodies[b], allow: 0 });
  const relBone = bodies[prop] ? wmat4(B[hand]).invert().multiply(wmat4(B[prop])) : null;   // prop bone in the hand bone (held)
  return { bodies, list: Object.values(bodies), joints, pairs, hand, prop, relBone, root: segs[0].k };
}
// held prop = part of the hand body (one rigid body: a 170 kg mace welded to a 19 kg hand made the solver pump energy)
const ragAddI = (I, m, d) => { const e = I.elements, l2 = d.lengthSq(), dl = [d.x, d.y, d.z]; for (let r = 0; r < 3; r++) for (let c = 0; c < 3; c++) e[c * 3 + r] += m * ((r === c ? l2 : 0) - dl[r] * dl[c]); return I; };
function ragMerge(RG) {
  const h = RG.bodies[RG.hand], pr = RG.bodies[RG.prop]; if (!h || !pr) return;
  const qrel = h.q.clone().invert().multiply(pr.q), cP = pr.x.clone().sub(h.x).applyQuaternion(h.q.clone().invert()), M = h.m + pr.m, d = cP.clone().multiplyScalar(pr.m / M);
  const Rr = new THREE.Matrix3().setFromMatrix4(new THREE.Matrix4().makeRotationFromQuaternion(qrel)), Ip = Rr.clone().multiply(pr.I).multiply(Rr.clone().transpose());
  const I = h.I.clone(); ragAddI(I, h.m, d.clone().negate()); for (let i = 0; i < 9; i++) I.elements[i] += Ip.elements[i]; ragAddI(I, pr.m, cP.clone().sub(d));
  RG.hold = { qrel, cP, d, h0: { m: h.m, im: h.im, c: h.c.clone(), I: h.I.clone(), Ii: h.Ii.clone(), pts: h.pts, cap: h.cap } };
  const v = h.v.clone().multiplyScalar(h.m).addScaledVector(pr.v, pr.m).divideScalar(M);
  h.x.add(d.clone().applyQuaternion(h.q)); h.v.copy(v); h.m = M; h.im = 1 / M; h.c = h.c.clone().add(d); h.I = I; h.Ii = I.clone().invert();
  h.ppts = pr.pts.map(p => p.clone().applyQuaternion(qrel).add(cP).sub(d)); h.pts = [...h.pts.map(p => p.clone().sub(d)), ...h.ppts];
  h.cap = { a: h.cap.a.clone().sub(d), b: h.cap.b.clone().sub(d), r: h.cap.r };
  RG.list = RG.list.filter(b => b !== pr);
  for (const j of RG.joints) if (j.c === h) j.rC = h.c.clone().negate();
}
function ragSplitProp(RG) {               // "Buông chùy": the prop leaves the hand with the speed it had there
  const H = RG.hold, h = RG.bodies[RG.hand], pr = RG.bodies[RG.prop]; if (!H || !h || !pr) return;
  const rp = H.cP.clone().sub(H.d).applyQuaternion(h.q), rh = H.d.clone().negate().applyQuaternion(h.q);
  pr.x.copy(h.x).add(rp); pr.q.copy(h.q).multiply(H.qrel); pr.v.copy(h.v).add(h.w.clone().cross(rp)); pr.w.copy(h.w);
  const vh = h.v.clone().add(h.w.clone().cross(rh)); h.x.add(rh); h.v.copy(vh);
  Object.assign(h, H.h0); h.ppts = null; RG.hold = null; RG.list.push(pr);
  for (const j of RG.joints) if (j.c === h) j.rC = h.c.clone().negate();
}
// ---- XPBD helpers (world inverse inertia: R Ii R^T)
function ragIiW(b, v) { return v.clone().applyQuaternion(b.q.clone().invert()).applyMatrix3(b.Ii).applyQuaternion(b.q); }
function ragW(b, r, n) { if (!b || !b.im) return 0; const rn = r.clone().cross(n); return b.im + rn.dot(ragIiW(b, rn)); }
function ragRot(b, dth) { const q = b.q, d = new Q(dth.x * 0.5, dth.y * 0.5, dth.z * 0.5, 0).multiply(q); q.x += d.x; q.y += d.y; q.z += d.z; q.w += d.w; q.normalize(); }
// move world point (r1 from body 1's com) by +c along n relative to point r2 of body 2 (null = the world)
function ragPos(b1, r1, b2, r2, n, c, alpha, h) {
  const w = ragW(b1, r1, n) + ragW(b2, r2, n), at = alpha / (h * h); if (w + at < 1e-12) return 0;
  const dl = c / (w + at), p = n.clone().multiplyScalar(dl);
  if (b1 && b1.im) { b1.x.addScaledVector(p, b1.im); ragRot(b1, ragIiW(b1, r1.clone().cross(p))); }
  if (b2 && b2.im) { b2.x.addScaledVector(p, -b2.im); ragRot(b2, ragIiW(b2, r2.clone().cross(p)).negate()); }
  return dl;
}
function ragAng(b1, b2, phi, alpha, h) {   // turn body 1 by phi (world) relative to body 2
  const th = phi.length(); if (th < 1e-10) return; const n = phi.clone().divideScalar(th);
  const w = (b1 ? n.dot(ragIiW(b1, n)) : 0) + (b2 ? n.dot(ragIiW(b2, n)) : 0), at = alpha / (h * h); if (w + at < 1e-12) return;
  const p = n.multiplyScalar(th / (w + at));
  if (b1) ragRot(b1, ragIiW(b1, p)); if (b2) ragRot(b2, ragIiW(b2, p).negate());
}
const ragPt = (b, r) => r.clone().applyQuaternion(b.q).add(b.x);
function ragVrel(A, rA, Bb, rB, n) { return A.v.clone().add(A.w.clone().cross(rA)).sub(Bb.v).sub(Bb.w.clone().cross(rB)).dot(n); }
// bend / spread / twist kept continuous in time (the same turn read the way nearest the last one): a wrist twisted 178 deg
// that went to 181 read -179, was clamped to the far limit and spun 240 deg in one sub-step (2026-10-25: up to 12 kJ)
function ragUnwrap(a, prev) {
  if (!prev) return a; const out = a.slice(), m = Math.hypot(a[0], a[1]);
  if (m > 1e-9) { const k = (m - 2 * Math.PI) / m, alt = [a[0] * k, a[1] * k]; if (Math.hypot(alt[0] - prev[0], alt[1] - prev[1]) < Math.hypot(a[0] - prev[0], a[1] - prev[1])) { out[0] = alt[0]; out[1] = alt[1]; } }
  while (out[2] - prev[2] > Math.PI) out[2] -= 2 * Math.PI; while (out[2] - prev[2] < -Math.PI) out[2] += 2 * Math.PI;
  return out;
}
function ragJointTurn(j, keep) { const t = ragUnwrap(ragSplit(j.q0.clone().invert().multiply(j.p.q.clone().invert().multiply(j.c.q)), j.ax), j.prev); if (keep) j.prev = t; return t; }
// one frame of simulation: kicks = [{b, rLoc, j (N s)}], targets = per joint deviation quaternions (key pose), s = strength 0..1
function ragFrame(RG, targets, sOf, kicks, fps, bal) {
  const h = 1 / fps / RAG_SUB, g = -BAL_G, stats = { pen: 0, lim: 0 };
  for (const k of kicks) { const b = k.b, r = k.rLoc.clone().applyQuaternion(b.q); b.v.addScaledVector(k.j, b.im); b.w.add(ragIiW(b, r.clone().cross(k.j))); }
  for (let sub = 0; sub < RAG_SUB; sub++) {
    for (const b of RG.list) {
      b.xp.copy(b.x); b.qp.copy(b.q); b.v.y += g * h; b.x.addScaledVector(b.v, h);
      const d = new Q(b.w.x * 0.5 * h, b.w.y * 0.5 * h, b.w.z * 0.5 * h, 0).multiply(b.q); b.q.x += d.x; b.q.y += d.y; b.q.z += d.z; b.q.w += d.w; b.q.normalize();
    }
    // muscles: toward the key pose's joint turn
    for (const j of RG.joints) {
      const s = sOf(j); if (s < 0.02) continue;
      const want = j.p.q.clone().multiply(j.q0).multiply(targets[j.k]), phi = qlog(want.multiply(j.c.q.clone().invert()));
      ragAng(j.c, j.p, phi, RAG_C0 / (s * s * s), h);
    }
    if (bal && bal.s >= 0.02) ragBalance(RG, bal, h);
    // joints: limits (turns), then positions last (Mueller 2020 order: a limit turn after the position left the joint open
    // until the next sub-step, and closing it there became speed)
    RG.lims = [];
    for (let it = 0; it < RAG_JIT; it++) {
    for (const j of RG.joints) {
      const t = ragJointTurn(j, true), cl = [Math.max(j.lim[0], Math.min(j.lim[1], t[0])), Math.max(j.lim[2], Math.min(j.lim[3], t[1])), Math.max(j.lim[4], Math.min(j.lim[5], t[2]))];
      if (cl[0] !== t[0] || cl[1] !== t[1] || cl[2] !== t[2]) {
        const want = j.p.q.clone().multiply(j.q0).multiply(ragJoin(cl, j.ax)), phi = qlog(want.multiply(j.c.q.clone().invert())), th = phi.length();
        if (th > 1e-10) { const n = phi.clone().divideScalar(th); RG.lims.push({ j, n, vpre: j.c.w.clone().sub(j.p.w).dot(n) }); }
        ragAng(j.c, j.p, phi, RAG_LIM_A, h);
      }
    }
    for (const j of RG.joints) {
      const a = ragPt(j.c, j.rC), b2 = ragPt(j.p, j.rP), d = b2.sub(a), c = d.length();
      if (c > 1e-9) ragPos(j.c, j.rC.clone().applyQuaternion(j.c.q), j.p, j.rP.clone().applyQuaternion(j.p.q), d.divideScalar(c), c, 0, h);
    }
    }
    // floor: surface points (bounce + friction in the velocity pass)
    for (const b of RG.list) {
      b.vn.length = 0;
      for (const pl of b.pts) {
        const r = pl.clone().applyQuaternion(b.q), y = b.x.y + r.y; if (y >= 0) continue;
        const rp = pl.clone().applyQuaternion(b.qp), prev = rp.add(b.xp), vpre = b.v.y + b.w.z * r.x - b.w.x * r.z;   // (v + w x r).y before the solve
        const dl = ragPos(b, r, null, null, new V3(0, 1, 0), -y, 0, h);
        const cur = ragPt(b, pl), dt = cur.clone().sub(prev); dt.y = 0; const lt = dt.length();
        if (lt > 1e-9 && lt < RAG_MU_S * -y) ragPos(b, pl.clone().applyQuaternion(b.q), null, null, dt.divideScalar(lt).negate(), lt, 0, h);
        b.vn.push({ pl, dl, vpre });
      }
    }
    // velocities
    for (const b of RG.list) {
      b.v.copy(b.x).sub(b.xp).divideScalar(h);
      const dq = b.q.clone().multiply(b.qp.clone().invert()); b.w.set(dq.x, dq.y, dq.z).multiplyScalar(2 / h); if (dq.w < 0) b.w.negate();
    }
    // floor: bounce 15 % above a small speed, sliding friction
    for (const b of RG.list) for (const { pl, dl, vpre } of b.vn) {
      const r = pl.clone().applyQuaternion(b.q), vp = b.v.clone().add(b.w.clone().cross(r)), vn = vp.y, vt = vp.clone(); vt.y = 0;
      const lt = vt.length(), fn = dl / (h * h);
      // normal: bounce / no pop. Sliding friction as an IMPULSE <= mu x the normal impulse (fn h): a velocity change
      // divided by the point's effective mass made it 3-5x too weak far from the centre (a lying Gaygor slid 2 m, Die b50)
      const vT = vpre < -2 * BAL_G * h ? -FLOOR_BOUNCE * vpre : Math.max(0, vpre), up = new V3(0, 1, 0), wn = ragW(b, r, up);
      if (Math.abs(vT - vn) > 1e-12) { const p = up.clone().multiplyScalar((vT - vn) / wn); b.v.addScaledVector(p, b.im); b.w.add(ragIiW(b, r.clone().cross(p))); }
      if (lt > 1e-9) { const t = vt.divideScalar(lt), vt2 = b.v.clone().add(b.w.clone().cross(r)).dot(t), wt = ragW(b, r, t); if (vt2 <= 0) continue;
        const jt = Math.min(h * RAG_MU_D * Math.abs(fn), vt2 / wt), p = t.multiplyScalar(-jt); b.v.addScaledVector(p, b.im); b.w.add(ragIiW(b, r.clone().cross(p))); }
    }
    // body vs body (cores) and a loose prop's points vs the cores: velocity only. Two parts going into each other are
    // stopped (inelastic) and get a small separating speed for how deep they are (<= 0.1 m/s). Position pushes inside the
    // closed loops of the joints pumped 2-9 kJ into a limp body (2026-10-25); a velocity constraint cannot.
    const vHit = (A, rA, Bb, rB, n, depth) => {
      const vr = ragVrel(A, rA, Bb, rB, n), vT = Math.min(RAG_BSEP, RAG_BBIAS * Math.max(0, depth - RAG_SLOP)); if (vr >= vT) return;
      const w = ragW(A, rA, n) + ragW(Bb, rB, n), p = n.clone().multiplyScalar((vT - vr) / w);
      A.v.addScaledVector(p, A.im); A.w.add(ragIiW(A, rA.clone().cross(p))); Bb.v.addScaledVector(p, -Bb.im); Bb.w.sub(ragIiW(Bb, rB.clone().cross(p)));
    };
    for (const pr of RG.pairs) {
      const A = pr.a, Bb = pr.b, [pa, pb] = segClosest(ragPt(A, A.cap.a), ragPt(A, A.cap.b), ragPt(Bb, Bb.cap.a), ragPt(Bb, Bb.cap.b));
      const d = pa.clone().sub(pb), dist = d.length(), need = A.cap.r + Bb.cap.r - pr.allow;
      if (dist < need && dist > 1e-9) vHit(A, pa.clone().sub(A.x).addScaledVector(d, -A.cap.r / dist), Bb, pb.clone().sub(Bb.x).addScaledVector(d, Bb.cap.r / dist), d.divideScalar(dist), need - dist);
    }
    if (RG.prop && RG.bodies[RG.prop] && !RG.hold) {
      const P_ = RG.bodies[RG.prop];
      for (const b of RG.list) {
        if (b === P_ || !b.cap) continue; const a0 = ragPt(b, b.cap.a), a1 = ragPt(b, b.cap.b), need = b.cap.r - (RG.propAllow[b.k] || 0);
        for (const pl of P_.pts) { const p = ragPt(P_, pl), cpt = closestOnSeg(p, a0, a1), d = p.clone().sub(cpt), dist = d.length();
          if (dist < need && dist > 1e-9) vHit(P_, pl.clone().applyQuaternion(P_.q), b, cpt.sub(b.x), d.divideScalar(dist), need - dist); }
      }
    }
    // rolling resistance: a part lying on the floor loses its turn speed (soft tissue, armor scraping)
    { const kr = Math.min(1, RAG_ROLL * h); for (const b of RG.list) if (b.vn.length) b.w.multiplyScalar(1 - kr); }
    // joint limits: inelastic like the contacts - the turn that pushed a joint back inside its limit must not leave a turn
    // speed out of it above the one before (a fast prop forced the elbow out every sub-step, the push back became spin:
    // free fall from Attack F30 gained 24-29 kJ)
    for (const L of RG.lims) {
      const { j, n } = L, vr = j.c.w.clone().sub(j.p.w).dot(n), vT = Math.max(0, L.vpre);
      if (vr > vT) { const w = n.dot(ragIiW(j.c, n)) + n.dot(ragIiW(j.p, n)), p = n.clone().multiplyScalar((vT - vr) / w); j.c.w.add(ragIiW(j.c, p)); j.p.w.sub(ragIiW(j.p, p)); }
      const kd = RAG_LIM_D; if (!kd) continue;      // a joint on its limit also loses part of its other turn speed (it chattered on the edge)
      const dw = j.c.w.clone().sub(j.p.w), l = dw.length(); if (l < 1e-9) continue; const m = dw.clone().divideScalar(l);
      const w2 = m.dot(ragIiW(j.c, m)) + m.dot(ragIiW(j.p, m)), p2 = m.multiplyScalar(-Math.min(1, kd * h) * l / w2); j.c.w.add(ragIiW(j.c, p2)); j.p.w.sub(ragIiW(j.p, p2));
    }
    // joint damping: passive (tissue, always) + muscles (scaled by strength) on each joint's relative turn speed
    for (const j of RG.joints) {
      const s = sOf(j), kk = RAG_PASSIVE + (s < 0.02 ? 0 : RAG_DAMP * s);
      const dw = j.c.w.clone().sub(j.p.w), k = Math.min(1, kk * h), l = dw.length(); if (l < 1e-9) continue;
      const n = dw.clone().divideScalar(l), w = n.dot(ragIiW(j.c, n)) + n.dot(ragIiW(j.p, n)), p = n.multiplyScalar(-k * l / w);
      j.c.w.add(ragIiW(j.c, p)); j.p.w.sub(ragIiW(j.p, p));
    }
  }
  for (const j of RG.joints) { const t = ragJointTurn(j); for (let a = 0; a < 3; a++) { const e = Math.max(j.lim[2 * a] - t[a], t[a] - j.lim[2 * a + 1]); if (e > stats.lim) { stats.lim = e; stats.limAt = j.k + "/" + a; } } }
  for (const b of RG.list) for (const pl of b.pts) stats.pen = Math.max(stats.pen, -(b.x.y + pl.clone().applyQuaternion(b.q).y));
  return stats;
}
function ragBalance(RG, bal, h) {
  // support: every sole point within 2 cm of the floor (the points pushed out of the floor in one sub-step were 1-3 and
  // made the feet a dot: a still standing body read 30-40 cm "outside")
  const pts = []; for (const k of ["Ankle_L", "Ankle_R"]) { const b = RG.bodies[k]; if (b && b.vn.length) for (const pl of b.pts) { const p = ragPt(b, pl); if (p.y < RAG_SOLE) pts.push([p.x, p.z]); } }
  if (!pts.length) return;                                   // no foot on the floor
  let M = 0; const c = new V3(), v = new V3(); for (const b of RG.list) { c.addScaledVector(b.x, b.m); v.addScaledVector(b.v, b.m); M += b.m; } c.divideScalar(M); v.divideScalar(M);
  const w0 = Math.sqrt(BAL_G / Math.max(0.3, c.y)), cp = [c.x + v.x / w0, c.z + v.z / w0];
  const mg = polyMargin(hull2(pts), cp); RG.balMg = Math.min(RG.balMg ?? 1e9, mg);
  if (mg <= -IMP_HIP) { RG.balOut = true; return; }
  const rb = RG.bodies[RG.root], s3 = bal.s * bal.s * bal.s; RG.balOn = true;
  ragAng(rb, null, qlog(bal.qt.clone().multiply(rb.q.clone().invert())), RAG_CB / s3, h);
  const d = bal.xt.clone().sub(rb.x); d.y = 0; const cc = d.length();
  if (cc > 1e-9) ragPos(rb, new V3(), null, null, d.divideScalar(cc), Math.min(cc, RAG_MU_D * BAL_G * h * h * M / rb.m), RAG_CBP / s3, h);
}
function segClosest(p1, q1, p2, q2) {      // closest points of two segments
  const d1 = q1.clone().sub(p1), d2 = q2.clone().sub(p2), r = p1.clone().sub(p2), a = d1.dot(d1), e = d2.dot(d2), f = d2.dot(r);
  const c = d1.dot(r), b = d1.dot(d2), den = a * e - b * b;
  let s = den > 1e-12 ? Math.min(1, Math.max(0, (b * f - c * e) / den)) : 0, t = e > 1e-12 ? (b * s + f) / e : 0;
  if (t < 0) { t = 0; s = a > 1e-12 ? Math.min(1, Math.max(0, -c / a)) : 0; } else if (t > 1) { t = 1; s = a > 1e-12 ? Math.min(1, Math.max(0, (b - c) / a)) : 0; }
  return [p1.clone().addScaledVector(d1, s), p2.clone().addScaledVector(d2, t)];
}
// write the bodies onto the bones: root position + every segment's turn (others keep the key pose's locals)
function ragApply(RG, segs) {
  const root = RG.bodies[segs[0].k];
  for (const s of segs) {
    const b = RG.bodies[s.k], bone = B[s.k];
    if (!s.par) { const ws = new V3(); bone.getWorldScale(ws); setWorldMat(bone, new THREE.Matrix4().compose(b.x.clone().sub(b.c.clone().applyQuaternion(b.q)), b.q, ws)); }
    else setWorldQuat(bone, b.q);
    model.updateMatrixWorld(true);
  }
  if (RG.prop && RG.hold && RG.relBone) { setWorldMat(B[RG.prop], wmat4(B[RG.hand]).multiply(RG.relBone)); }
  else if (RG.prop && RG.bodies[RG.prop]) { const b = RG.bodies[RG.prop], ws = new V3(); B[RG.prop].getWorldScale(ws); setWorldMat(B[RG.prop], new THREE.Matrix4().compose(b.x.clone().sub(b.c.clone().applyQuaternion(b.q)), b.q, ws)); }
  model.updateMatrixWorld(true);
}
// the ragdoll stage of computePhysCore: from frame `from` the bodies take over (start = the pose shown at from-1, speed
// from from-2 -> from-1); every frame the key pose gives the muscles' targets, the hits at or after `from` kick the bodies
function ragPrepare() {
  if (!ragOn()) return null;
  const R = ANIM.phys.rag, from = Math.max(2, Math.min(NFR(), Math.round(R.from || 2)));
  return { from, q0: ragRest(), segs: ragSegs(), RG: null, rows: {}, pen: 0, lim: 0 };
}
function ragStage(G, f, out, fps) {
  const R = ANIM.phys.rag;
  if (!G.RG) {
    const setPose = o => { for (const n of BN) if (o && o[n]) { B[n].quaternion.fromArray(o[n], 0); B[n].position.fromArray(o[n], 4); } model.updateMatrixWorld(true); };
    const p1 = out[f - 1], p0 = out[f - 2] || p1, names = [...G.segs.map(s => s.k), ...BODY.props.filter(p => B[p])];
    setPose(p0); const w0 = {}; for (const k of names) w0[k] = { p: wp(B[k]), q: wq(B[k]) };
    setPose(p1); const RG = ragBuild(G.q0); G.RG = RG;
    for (const b of RG.list) { const a = w0[b.k]; if (!a) continue; const x0 = b.c.clone().applyQuaternion(a.q).add(a.p);
      b.v.copy(b.x).sub(x0).multiplyScalar(fps); b.w.copy(qlog(b.q.clone().multiply(a.q.clone().invert()))).multiplyScalar(fps); }
    for (const pr of RG.pairs) { const [pa, pb] = segClosest(ragPt(pr.a, pr.a.cap.a), ragPt(pr.a, pr.a.cap.b), ragPt(pr.b, pr.b.cap.a), ragPt(pr.b, pr.b.cap.b)); pr.allow = Math.max(0, pr.a.cap.r + pr.b.cap.r - pa.distanceTo(pb)); }
    for (const j of RG.joints) {                     // the start pose is always allowed
      const t = ragJointTurn(j, true);
      if (Math.hypot(t[0], t[1]) > Math.PI / 2 || Math.abs(t[2]) > Math.PI / 2) {
        // far from rest (Attack's team blocking: left arm turned 180 deg, elbow bent the other way): near 180 deg the
        // bend / spread / twist split is singular and the limit spun the arm (11-29 kJ). Limits around the START pose instead.
        j.q0 = j.q0.clone().multiply(ragJoin(t, j.ax)); j.prev = [0, 0, 0];
        for (let a = 0; a < 3; a++) { const w = (j.lim[2 * a + 1] - j.lim[2 * a]) / 2; j.lim[2 * a] = -w; j.lim[2 * a + 1] = w; }
        continue;
      }
      for (let a = 0; a < 3; a++) { j.lim[2 * a] = Math.min(j.lim[2 * a], t[a]); j.lim[2 * a + 1] = Math.max(j.lim[2 * a + 1], t[a]); }
    }
    RG.propAllow = {};
    if (RG.prop && RG.bodies[RG.prop]) { const P_ = RG.bodies[RG.prop];
      for (const b of RG.list) if (b.cap) { const a0 = ragPt(b, b.cap.a), a1 = ragPt(b, b.cap.b); let m = 0; for (const pl of P_.pts) { const p = ragPt(P_, pl); m = Math.max(m, b.cap.r - p.distanceTo(closestOnSeg(p, a0, a1))); } RG.propAllow[b.k] = m; } }
    if (R.test) for (const b of RG.list) { if (R.test.lift) b.x.y += R.test.lift; if (R.test.still) { b.v.set(0, 0, 0); b.w.set(0, 0, 0); } }   // acceptance tests only
    if (RG.prop && RG.bodies[RG.prop]) ragMerge(RG);
    if (window.__ragRec) G.trace = { init: ragSnap(RG), frames: {} };   // cross-check with tools/physics_sim.py --ragdoll
    if (ragGoalOn()) {                                // "Về đích": the muscles' end target = the last key's joint turns
      const E = ragGoalFrame(); evalPose(E); model.updateMatrixWorld(true); G.goalT = {};
      for (const j of RG.joints) { const t = ragUnwrap(ragSplit(ragRel(j.k, j.par, j.q0), j.ax), j.prev); for (let a = 0; a < 3; a++) t[a] = Math.max(j.lim[2 * a], Math.min(j.lim[2 * a + 1], t[a])); G.goalT[j.k] = ragJoin(t, j.ax); }
      G.landBone = B.Chest_M ? "Chest_M" : RG.root; G.endY = wp(B[G.landBone]).y;
    }
    evalPose(f); model.updateMatrixWorld(true);
  }
  const RG = G.RG, targets = {};
  for (const j of RG.joints) { const t = ragUnwrap(ragSplit(ragRel(j.k, j.par, j.q0), j.ax), j.prev); for (let a = 0; a < 3; a++) t[a] = Math.max(j.lim[2 * a], Math.min(j.lim[2 * a + 1], t[a])); targets[j.k] = ragJoin(t, j.ax); }
  const kicks = [], { M } = impMass();
  for (const i of impList()) {
    if (i.f < G.from || f < i.f || f >= i.f + impDur(i)) continue;
    let b = RG.bodies[i.seg]; if (!b) continue; let rLoc = new V3(...i.p).sub(b.c);
    if (i.seg === RG.prop && RG.hold) { rLoc = rLoc.applyQuaternion(RG.hold.qrel).add(RG.hold.cP).sub(RG.hold.d); b = RG.bodies[RG.hand]; }
    const { d } = impPointW(i); kicks.push({ b, rLoc, j: d.multiplyScalar(impDV(i) * M / impDur(i)) });
  }
  const GL = ragGoalOn() ? R.goal : null;
  if (GL && GL.push && f === G.from) {               // step 1: one push of the whole body (velocity vx/vz m/s + yaw rad/s)
    const pu = GL.push, com = new V3(); let mt = 0; for (const b of RG.list) { com.addScaledVector(b.x, b.m); mt += b.m; } com.divideScalar(mt);
    const dv = new V3(pu.vx || 0, 0, pu.vz || 0), w = new V3(0, pu.wy || 0, 0);   /* the push is kept in both modes (user 2026-10-26: it is part of the hit); chỉ dáng only stops the end blend from dragging the hips back */
    for (const b of RG.list) kicks.push({ b, rLoc: new V3(), j: dv.clone().add(w.clone().cross(b.x.clone().sub(com))).multiplyScalar(b.m) });
  }
  if (R.release != null && f >= R.release && RG.hold) { ragSplitProp(RG); RG.released = true; }
  if (R.test && R.test.rigid) { RG.rigidT ||= Object.fromEntries(RG.joints.map(j => [j.k, ragJoin(ragJointTurn(j), j.ax)])); Object.assign(targets, RG.rigidT); }   // acceptance: joints locked
  const gm = R.groups || {}, s0 = R.test && R.test.rigid ? 1e6 : ragStrength(f);
  // step 2 (v2, user "hơi cứng và thiếu tự nhiên" on goal_v1: the body fell as one block, then posed itself at one constant
  // speed after landing - right knee 121->164, spine 20->59 deg over F26-36, hips pushed up 10 cm - and froze from F38):
  // a) while falling the muscles lean a little toward the last key (pre-shape, weak), so most of the shape change happens
  //    in the big motion; b) after landing each joint eases (smoothstep) to the last key with its own duration (by angle)
  //    and delay (trunk, legs, arms, head last), at a lower strength; c) then the muscles let go over 10 frames and the
  //    body settles on its own (what is left is blended at the end, step 3)
  let gs = 0;
  if (GL && G.goalT) {
    if (G.landAt == null) {                                     // a) falling
      const u = smooth01((f - G.from) / Math.max(1, GL.preF ?? 16)), a = (GL.pre ?? 0.5) * u; gs = (GL.preS ?? 0.12) * u;
      if (a > 0) for (const j of RG.joints) if (G.goalT[j.k]) targets[j.k] = targets[j.k].clone().slerp(G.goalT[j.k], a);
    } else {                                                     // b) + c) landed
      if (!G.goalPlan) {
        const DELAY = { trunk: 0, legL: 2, legR: 2, armL: 3, armR: 3, head: 5 }; G.goalPlan = {}; G.goalEnd = 0;
        for (const j of RG.joints) { const q = ragJoin(ragJointTurn(j), j.ax), g = G.goalT[j.k]; if (!g) continue;
          const d = Math.max(6, Math.min(22, THREE.MathUtils.radToDeg(q.angleTo(g)) / 3)), st = G.landAt + (DELAY[j.grp] ?? 2);
          G.goalPlan[j.k] = { q, st, d }; G.goalEnd = Math.max(G.goalEnd, st + d); }
      }
      const fade = 1 - smooth01((f - G.goalEnd - 2) / Math.max(1, GL.letGo ?? 10));
      const hold = GL.hold ?? 0.25;                              // a little tone stays: limp to 0, the head rolled 80 deg off the last key
      gs = (GL.gs ?? 0.35) * smooth01((f - G.landAt) / 4) * (hold + (1 - hold) * fade);
      for (const j of RG.joints) { const pl = G.goalPlan[j.k]; if (!pl) continue;
        const c = pl.q.clone().slerp(G.goalT[j.k], smooth01((f - pl.st) / pl.d));
        targets[j.k] = targets[j.k].clone().slerp(c, Math.min(1, gs / Math.max(1e-6, s0 + gs))); }
    }
  }
  if (kicks.length || s0 + gs >= 0.05) { RG.asleep = false; RG.calm = 0; }
  const sOf = j => R.test && R.test.rigid ? 1e6 : Math.min(1.5, s0 * ragGroupF(gm, j.grp) + gs);   // the goal drive is not scaled by the loose fall groups
  const rb = RG.bodies[RG.root], kq = wq(B[RG.root]);       // balance target: the key pose's hips (the key pose is on screen)
  const bal = R.test && R.test.rigid ? null : { s: Math.min(1.5, s0 * (ragGroupF(gm, "legL") + ragGroupF(gm, "legR")) / 2), qt: kq, xt: rb.c.clone().applyQuaternion(kq).add(wp(B[RG.root])) };
  if (G.trace) G.trace.frames[f] = { asleep: !!RG.asleep, released: !!RG.released, bal: bal && { s: bal.s, qt: bal.qt.toArray(), xt: bal.xt.toArray() }, t: Object.fromEntries(Object.entries(targets).map(([k, q]) => [k, q.toArray()])),
    s: Object.fromEntries(RG.joints.map(j => [j.k, sOf(j)])), kicks: kicks.map(k => ({ b: k.b.k, r: k.rLoc.toArray(), j: k.j.toArray() })) };
  RG.balOut = false; RG.balOn = false; RG.balMg = null;
  const st = RG.asleep ? { pen: 0, lim: 0 } : ragFrame(RG, targets, sOf, kicks, fps, bal);
  RG.outRun = RG.balOut && !RG.balOn && bal && bal.s >= 0.02 ? (RG.outRun || 0) + 1 : 0;   // strength left but the feet cannot hold it (3 frames running)
  if (RG.outRun >= 3 && G.needStep == null) G.needStep = f - 2;
  G.pen = Math.max(G.pen, st.pen); if (st.lim > G.lim) { G.lim = st.lim; G.limAt = st.limAt + " F" + f; }
  ragApply(RG, G.segs);
  if (GL && G.goalT && G.landAt == null && f > G.from && wp(B[G.landBone]).y < G.endY + 0.15) G.landAt = f;   // landed
  let sp = 0, ke = 0, pe = 0, cy = 0, mt = 0;
  for (const b of RG.list) { sp = Math.max(sp, b.v.length() + b.w.length() * 0.4); ke += 0.5 * b.m * b.v.lengthSq() + 0.5 * b.w.dot(b.w.clone().applyQuaternion(b.q.clone().invert()).applyMatrix3(b.I).applyQuaternion(b.q)); pe += b.m * BAL_G * b.x.y; cy += b.m * b.x.y; mt += b.m; }
  if (RG.asleep) { sp = 0; ke = 0; }
  else if (s0 + gs < 0.05 && sp * 100 / fps < RAG_SLEEP_CM) { if (++RG.calm >= RAG_SLEEP_F) { RG.asleep = true; for (const b of RG.list) { b.v.set(0, 0, 0); b.w.set(0, 0, 0); } } } else RG.calm = 0;
  G.rows[f] = { sp: sp * 100 / fps, s: s0, e: ke + pe, ke, cy: cy / mt, sleep: !!RG.asleep, bal: RG.balOn ? 1 : RG.balOut ? -1 : 0, mg: RG.balMg };
  if (window.__ragRec) G.rows[f].bx = Object.fromEntries(RG.list.map(b => [b.k, [...b.x.toArray(), ...b.q.toArray()]]));   // cross-check with tools/physics_sim.py
}
function ragSnap(RG) {                   // the bodies, joints and contacts as plain data (for the Python twin)
  const A = v => v.toArray(), b2 = b => ({ k: b.k, m: b.m, c: A(b.c), I: [...b.I.elements], x: A(b.x), q: A(b.q), v: A(b.v), w: A(b.w), pts: b.pts.map(A), ppts: b.ppts ? b.ppts.map(A) : null, cap: b.cap ? { a: A(b.cap.a), b: A(b.cap.b), r: b.cap.r } : null });
  return { list: RG.list.map(b => b.k), bodies: Object.fromEntries(Object.values(RG.bodies).map(b => [b.k, b2(b)])),
    joints: RG.joints.map(j => ({ k: j.k, c: j.c.k, p: j.p.k, rC: A(j.rC), rP: A(j.rP), q0: A(j.q0), t: A(j.ax.t), e1: A(j.ax.e1), e2: A(j.ax.e2), lim: j.lim, prev: j.prev })),
    pairs: RG.pairs.map(p => ({ a: p.a.k, b: p.b.k, allow: p.allow })), propAllow: RG.propAllow, hand: RG.hand, prop: RG.prop, root: RG.root,
    hold: RG.hold ? { qrel: A(RG.hold.qrel), cP: A(RG.hold.cP), d: A(RG.hold.d), h0: { m: RG.hold.h0.m, c: A(RG.hold.h0.c), I: [...RG.hold.h0.I.elements], pts: RG.hold.h0.pts.map(A), cap: { a: A(RG.hold.h0.cap.a), b: A(RG.hold.h0.cap.b), r: RG.hold.h0.cap.r } } } : null };
}
function ragSummary(G) {
  if (!G) return null; const fs = Object.keys(G.rows).map(Number).sort((a, b) => a - b); let restAt = null;
  for (let i = fs.length - 1; i >= 0; i--) { if (G.rows[fs[i]].sp >= RAG_REST_CM && !G.rows[fs[i]].sleep) break; restAt = fs[i]; }
  if (restAt != null) { const i0 = fs.indexOf(restAt); let i = i0; while (i > 0 && G.rows[fs[i - 1]].sp < RAG_SLEEP_CM) i--; restAt = fs[i]; }
  // "cần bước" only when a fall follows (the CoM goes down > 25 cm within a second): a body that stays up only swayed
  let needStep = G.needStep ?? null;
  if (needStep != null) { const y0 = G.rows[needStep] && G.rows[needStep].cy, lo = Math.min(...fs.filter(f => f >= needStep && f <= needStep + 30).map(f => G.rows[f].cy));
    if (y0 == null || y0 - lo < 0.25) needStep = null; }
  return { from: G.from, goal: G.goal || null, landAt: G.landAt ?? null, restAt, needStep, pen: +(G.pen / CM_W).toFixed(1), lim: +THREE.MathUtils.radToDeg(Math.max(0, G.lim)).toFixed(1), limAt: G.limAt || "", rows: G.rows, trace: G.trace || null };
}
function computePhys() {               // keeps the edit state and hand targets even if the simulation throws
  const ed0 = edited, hq = handQ;
  try { computePhysCore(); } finally { edited = ed0; handQ = hq; }
}
function computePhysCore() {
  physDirty = false; PHYS = null;
  if (!physOn()) return;
  const t0 = performance.now(), cfg = ANIM.phys, ed = edited, N = PER(), last = P.loop ? N : NFR();
  const hq0 = handQ; handQ = {};
  const pins = PINS, pinW = f => {                            // 0 on pinned frames, smooth back to 1 over PIN_RAMP frames
    if (!pins.size) return 1; let d = 1e9;
    for (const p of pins) { const x = P.loop ? Math.min(Math.abs(p - f), N - Math.abs(p - f)) : Math.abs(p - f); if (x < d) d = x; }
    return d >= PIN_RAMP ? 1 : smooth01(d / PIN_RAMP);
  };
  const endW = f => { const E = P.loop ? 0 : Math.max(0, cfg.end | 0); return !E || f <= last - E ? 1 : 1 - smooth01((f - (last - E)) / E); };
  const cp0 = charPhys(), apParts = apOn("sec") && !cfg.parts.length && cp0 ? cp0.parts : cfg.parts, secK = apOn("sec") ? 2 * apV("sec") : 1;
  const parts = apParts.filter(p => B[p.bone]).map(p => {
    const x = physPart(p), z = Math.max(0, Math.min(0.98, 1 - x.bounce)), w0 = 2 * Math.PI / Math.max(2, x.period);
    const side = x.type === "swing" ? x.bone.slice(-1) : (x.hand || "L");
    return { ...x, K: w0 * w0, C: 2 * z * w0, L: THREE.MathUtils.degToRad(x.limit), side, S: null, vel: new V3(), th: 0, Tp: null, aux: null, ord: x.type === "prop" ? 1e3 : x.type === "swing" ? 2e3 : boneDepth(x.bone) };
  }).sort((a, b) => a.ord - b.ord);
  const cols = (apOn("sec") && !cfg.parts.length && cp0 ? cp0.colliders || [] : cfg.colliders || []).filter(c => B[c.bone]);
  if (!BODY) BODY = buildBody();
  const IMP = impPrepare(), pre = {}, RAG = ragPrepare(), fpsR = P.fps || 30;
  let netN = 0; const seq = []; for (let r = 0; r < (P.loop ? 2 : 1); r++) for (let f = 1; f <= last; f++) seq.push([f, r === (P.loop ? 1 : 0)]);
  const out = {}, base = {}, series = parts.map(() => ({ out: {}, base: {}, contact: new Set(), peak: 0, peakF: 1 }));
  const pack = n => packBone(B[n].quaternion, B[n].position), h = 1 / PHYS_SUB;
  const TOL = 0.05 * CM_W;
  for (const [f, rec] of seq) {
    evalPose(f); model.updateMatrixWorld(true);
    const first = !P.loop && f === 1;                         // F1 of a one-shot clip is the key pose (state starts there)
    const bl = {}; for (const n of BN) bl[n] = pack(n);
    const wp_ = pinW(f), we = endW(f);
    if (RAG && f >= RAG.from) { ragStage(RAG, f, out, fpsR); if (rec) { const ol = {}; for (const n of BN) ol[n] = pack(n); out[f] = ol; base[f] = bl; } continue; }
    if (IMP) { impApply(IMP, f, first); if (rec) { const o = {}; for (const n of BN) o[n] = pack(n); pre[f] = o; } }
    parts.forEach((p, pi) => {
      const sr = series[pi];
      if (p.type === "joint" || p.type === "hinge") {
        const bone = B[p.bone], T = wq(bone);
        if (!p.S) { p.S = T.clone(); p.Tp = T.clone(); }
        { const iw = first ? null : impInject(IMP, f, p.bone), cap = p.L * Math.sqrt(p.K) / (iw ? Math.max(1, (IMP.hits.find(h => f >= h.f && f < h.f + h.dur) || { dur: 1 }).dur) : 1);
          if (iw) { if (iw.length() > cap) iw.setLength(cap); p.vel.add(iw); if (rec) ((IMP.inj ||= {})[f] ||= {})[p.bone] = iw.toArray(); } }
        const link = p.link || (p.link = bodyLink(p.bone)), pivot = wp(bone), mp = bodyMovPts(p.bone, link), ob = bodyObsWorld(link);
        const allow = bodyAllow(T, pivot, mp, ob, link); let hitB = false;
        for (let s = 1; s <= (first ? 0 : PHYS_SUB); s++) {
          const tg = p.Tp.clone().slerp(T, s * h), err = rvec(p.S, tg);
          p.vel.add(err.multiplyScalar(p.K * h)).sub(p.vel.clone().multiplyScalar(p.C * h)); p.S.premultiply(qrv(p.vel.clone().multiplyScalar(h)));
          if (ob.length && bodyPush(p, pivot, mp, ob, link, allow)) hitB = true;
        }
        let d = rvec(T, p.S), a = d.length();
        if (a > 1e-9) { const a2 = softLimit(a, p.L); p.S = qrv(d.multiplyScalar(a2 / a)).multiply(T); }
        if (wp_ < 1) { p.S = T.clone().slerp(p.S, wp_); p.vel.multiplyScalar(wp_); }
        let o = T.clone().slerp(p.S, we * secK);
        if (p.type === "hinge") { const ax = new V3(0, 0, 1).applyQuaternion(T), dd = rvec(T, o); o = qrv(ax.multiplyScalar(dd.dot(ax))).multiply(T); }
        { const [o2, used] = bodySafe(T, o, pivot, mp, ob, link, allow); if (used) { o = o2; netN++; hitB = true; } }
        setWorldQuat(bone, o); model.updateMatrixWorld(true);
        if (rec) { sr.out[f] = o.clone(); sr.base[f] = T.clone(); if (hitB) sr.contact.add(f); const g = rvec(T, o).length(); if (g > sr.peak) { sr.peak = g; sr.peakF = f; } }
        p.Tp = T;
      } else if (p.type === "prop") {
        const bone = B[p.bone], wr = B[ARMS[p.side][2]]; if (!wr) return;
        const T = wq(bone), g = wp(wr), Gm = wmat4(bone).invert().multiply(wmat4(wr)), Gp = new V3().setFromMatrixPosition(Gm);
        const Gq = new Q().setFromRotationMatrix(new THREE.Matrix4().extractRotation(Gm));
        const pts = cols.length ? propPoints(p.bone) : [], cs = cols.map(c => wp(B[c.bone]));
        const at = (q, gg) => gg.clone().sub(Gp.clone().applyQuaternion(q));          // prop origin with the grip at gg
        const need = cs.map((c, ci) => {                                               // never closer than at rest / in the key pose
          const g0 = pts.length ? propGap(pts, T, at(T, g), c)[0] : 1e9;
          if (!p.aux) p.aux = {}; if (p.aux["rest" + ci] == null) p.aux["rest" + ci] = g0;
          return Math.min(p.aux["rest" + ci], g0);
        });
        const allPts = propPoints(p.bone);                                           // floor: never below 0 or the key pose
        const floorY = allPts.length ? Math.min(0, ...allPts.map(q => q.clone().applyQuaternion(T).add(at(T, g)).y)) : -1e9;
        if (!p.S) { p.S = T.clone(); p.Tp = T.clone(); p.gp = g.clone(); p.cp = cs.map(c => c.clone()); p.fp = floorY; }
        { const iw = first ? null : impInject(IMP, f, p.bone), cap = p.L * Math.sqrt(p.K) / (iw ? Math.max(1, (IMP.hits.find(h => f >= h.f && f < h.f + h.dur) || { dur: 1 }).dur) : 1);
          if (iw) { if (iw.length() > cap) iw.setLength(cap); p.vel.add(iw); if (rec) ((IMP.inj ||= {})[f] ||= {})[p.bone] = iw.toArray(); } }
        // contact = inelastic constraint, no bounce, no force before touching: the points past the floor (a collider: closer
        // than at rest / in the key pose; the ground: below it) turn the prop out about the grip by their depth (weighted
        // over all of them) and the speed into it is removed. Tried 2026-10-24: soft pads (force by depth) were chaotic -
        // 1e-6 noise grew to 12 deg (a stiff spring on a bumpy mesh bounces) - and hovered the prop off the shoulder.
        const PA = new Float64Array(allPts.length * 3); allPts.forEach((q, i) => { PA[3 * i] = q.x; PA[3 * i + 1] = q.y; PA[3 * i + 2] = q.z; });
        if (!p.pax && allPts.length) {                  // the prop's long axis + radius (unit frame), for pruning
          const m = allPts.reduce((a, q) => a.add(q), new V3()).divideScalar(allPts.length); let far = allPts[0];
          for (const q of allPts) if (q.distanceTo(m) > far.distanceTo(m)) far = q;
          const dir = far.clone().sub(m).normalize(); let lo = 0, hi = 0;
          for (const q of allPts) { const t = q.clone().sub(m).dot(dir); lo = Math.min(lo, t); hi = Math.max(hi, t); }
          const a = m.clone().addScaledVector(dir, lo), b = m.clone().addScaledVector(dir, hi);
          p.pax = { a, b, r: Math.max(...allPts.map(q => q.distanceTo(closestOnSeg(q, a, b)))) };
        }
        // body cores the prop may not go into deeper than in the key pose; the hands holding it (a prop point within 6 cm
        // of the hand's core) and the prop's own hand are not obstacles. Plain numbers: this runs every frame.
        const capW = k => { const c = BODY.caps[k], M = wmat4(B[k]); return { a: c.a.clone().applyMatrix4(M), b: c.b.clone().applyMatrix4(M), r: c.r }; };
        const KP0 = allPts.map(q => q.clone().applyQuaternion(T).add(at(T, g)));
        const depthIn = (c, list) => { let m = -1e9; const ex = c.b.x - c.a.x, ey = c.b.y - c.a.y, ez = c.b.z - c.a.z, L2 = Math.max(ex * ex + ey * ey + ez * ez, 1e-12);
          for (const w of list) { let t = ((w.x - c.a.x) * ex + (w.y - c.a.y) * ey + (w.z - c.a.z) * ez) / L2; t = t < 0 ? 0 : t > 1 ? 1 : t;
            const d = Math.hypot(c.a.x + ex * t - w.x, c.a.y + ey * t - w.y, c.a.z + ez * t - w.z); if (c.r - d > m) m = c.r - d; } return m; };
        const held = new Set([p.side]);
        for (const hs of ["L", "R"]) if (BODY.caps["Wrist_" + hs] && depthIn({ ...capW("Wrist_" + hs), r: BODY.caps["Wrist_" + hs].r + GRIP_CM * CM_W }, KP0) > 0) held.add(hs);
        const paxW = p.pax ? { a: p.pax.a.clone().applyQuaternion(T).add(at(T, g)), b: p.pax.b.clone().applyQuaternion(T).add(at(T, g)) } : null;
        const bobs = Object.keys(BODY.caps).filter(k => !(/^(Wrist|Elbow)_/.test(k) && held.has(k.slice(-1)))).map(k => {
          const c = capW(k), near = paxW && segSegDist(paxW.a, paxW.b, c.a, c.b) <= p.pax.r + c.r;
          return { a: c.a, b: c.b, r: c.r, need: c.r - (near ? Math.max(0, depthIn(c, KP0)) : 0) };
        });
        const contact = (org, gg, cc, need0) => {        // cc null = the floor at height need0; else a sphere (cc, need0) or a body core
          const e = new THREE.Matrix4().makeRotationFromQuaternion(p.S).elements, step = cc && cc.b ? 6 : 3;   // body cores: half the points
          let tx = 0, ty = 0, tz = 0, cx = 0, cy = 0, cz = 0, sw = 0;
          for (let i = 0; i < PA.length; i += step) {
            const x = PA[i], y = PA[i + 1], z = PA[i + 2];
            const wx = e[0] * x + e[4] * y + e[8] * z + org.x, wy = e[1] * x + e[5] * y + e[9] * z + org.y, wz = e[2] * x + e[6] * y + e[10] * z + org.z;
            let pen, axx, axy, axz;
            const rx = wx - gg.x, ry = wy - gg.y, rz = wz - gg.z;
            if (!cc) { pen = need0 - wy; if (pen <= 0) continue; axx = rz; axy = 0; axz = -rx; }          // (w - g) x down
            else if (cc.b) {                                                                             // a body core
              const ax0 = cc.a.x, ay0 = cc.a.y, az0 = cc.a.z, ex = cc.b.x - ax0, ey = cc.b.y - ay0, ez = cc.b.z - az0;
              let t = ((wx - ax0) * ex + (wy - ay0) * ey + (wz - az0) * ez) / Math.max(ex * ex + ey * ey + ez * ez, 1e-12); t = t < 0 ? 0 : t > 1 ? 1 : t;
              const dx = ax0 + ex * t - wx, dy = ay0 + ey * t - wy, dz = az0 + ez * t - wz; pen = need0 - Math.sqrt(dx * dx + dy * dy + dz * dz); if (pen <= 0) continue;
              axx = ry * dz - rz * dy; axy = rz * dx - rx * dz; axz = rx * dy - ry * dx;
            } else {
              const dx = cc.x - wx, dy = cc.y - wy, dz = cc.z - wz; pen = need0 - Math.sqrt(dx * dx + dy * dy + dz * dz); if (pen <= 0) continue;
              axx = ry * dz - rz * dy; axy = rz * dx - rx * dz; axz = rx * dy - ry * dx;
            }
            const l = Math.sqrt(axx * axx + axy * axy + axz * axz); if (l < 1e-9) continue;
            const k = pen * pen / l; tx += axx * k; ty += axy * k; tz += axz * k; cx += wx * pen; cy += wy * pen; cz += wz * pen; sw += pen;
          }
          if (!sw) return false;
          const ax = new V3(tx / sw, ty / sw, tz / sw), pen = ax.length(); ax.divideScalar(pen);
          const lever = Math.max(new V3(cx / sw, cy / sw, cz / sw).distanceTo(gg), CM_W);
          p.S.premultiply(new Q().setFromAxisAngle(ax, -pen / lever));
          const vin = p.vel.dot(ax); if (vin > 0) p.vel.sub(ax.multiplyScalar(vin * (cc ? 1 : 1 + FLOOR_BOUNCE)));   // floor: small bounce
          return true;
        };
        let hit = false; const NS = PHYS_SUBP, h = 1 / NS;   // fine steps: each contact correction stays tiny
        for (let s = 1; s <= (first ? 0 : NS); s++) {
          const u = s * h, tg = p.Tp.clone().slerp(T, u), gg = p.gp.clone().lerp(g, u), err = rvec(p.S, tg);
          p.vel.add(err.multiplyScalar(p.K * h)).sub(p.vel.clone().multiplyScalar(p.C * h)); p.S.premultiply(qrv(p.vel.clone().multiplyScalar(h)));
          const fy = p.fp + (floorY - p.fp) * u;
          if (PA.length && contact(at(p.S, gg), gg, null, fy)) hit = true;
          cs.forEach((c, ci) => { if (pts.length && contact(at(p.S, gg), gg, p.cp[ci].clone().lerp(c, u), need[ci])) hit = true; });
          if (PA.length && bobs.length && (s % PHYS_BODY_EVERY === 0 || s === NS)) {     // body cores: every 4th sub-step (cost)
            const org = at(p.S, gg), pa = p.pax.a.clone().applyQuaternion(p.S).add(org), pb2 = p.pax.b.clone().applyQuaternion(p.S).add(org);
            for (const bo of bobs) if (segSegDist(pa, pb2, bo.a, bo.b) <= p.pax.r + bo.r && contact(org, gg, bo, bo.need)) hit = true;
          }
        }
        let d = rvec(T, p.S), a = d.length();
        if (a > 1e-9) { const a2 = softLimit(a, p.L); p.S = qrv(d.multiplyScalar(a2 / a)).multiply(T); }
        if (wp_ < 1) { p.S = T.clone().slerp(p.S, wp_); p.vel.multiplyScalar(wp_); }
        let o = T.clone().slerp(p.S, we * secK);
        cs.forEach((c, ci) => {                                                       // safety net only (contacts keep it clear)
          if (!pts.length || propGap(pts, o, at(o, g), c)[0] >= need[ci] - TOL) return;
          let lo = 0, hi = 1; for (let k = 0; k < 20; k++) { const m = (lo + hi) / 2, q = T.clone().slerp(o, m); if (propGap(pts, q, at(q, g), c)[0] >= need[ci] - TOL) lo = m; else hi = m; }
          o = T.clone().slerp(o, lo); netN++;
        });
        const ws = new V3(); bone.getWorldScale(ws);
        setWorldMat(bone, new THREE.Matrix4().compose(at(o, g), o, ws)); model.updateMatrixWorld(true);
        const hq = o.clone().multiply(Gq); handQ[p.side] = hq; solveArm(p.side, g); model.updateMatrixWorld(true);
        if (rec) { sr.out[f] = o.clone(); sr.base[f] = T.clone(); if (hit) sr.contact.add(f); const gg = rvec(T, o).length(); if (gg > sr.peak) { sr.peak = gg; sr.peakF = f; } }
        p.Tp = T; p.gp = g.clone(); p.cp = cs.map(c => c.clone()); p.fp = floorY;
      } else if (p.type === "swing") {
        const [sn, en, wn] = ARMS[p.side]; if (!B[sn] || !B[en] || !B[wn]) return;
        const S_ = wp(B[sn]), E = wp(B[en]), Wr = wp(B[wn]), u = Wr.clone().sub(S_).normalize();
        const dv = E.clone().sub(S_); dv.sub(u.clone().multiplyScalar(dv.dot(u))).normalize();
        if (!p.aux) p.aux = { ref: dv.clone() };
        const r = p.aux.ref.clone(); r.sub(u.clone().multiplyScalar(r.dot(u))).normalize();
        const th = Math.atan2(r.clone().cross(dv).dot(u), r.dot(dv));
        if (p.S === null) { p.S = th; p.Tp = th; p.v = 0; }
        const wrap = x => { while (x > Math.PI) x -= 2 * Math.PI; while (x < -Math.PI) x += 2 * Math.PI; return x; };
        for (let s = 1; s <= (first ? 0 : PHYS_SUB); s++) { const tg = p.Tp + wrap(th - p.Tp) * s * h; p.v += h * (p.K * wrap(tg - p.S) - p.C * p.v); p.S += p.v * h; }
        let off = wrap(p.S - th); off = Math.sign(off) * softLimit(Math.abs(off), p.L);
        off *= wp_; p.v *= wp_; p.S = th + off;
        let o = off * we * secK; const wq0 = wq(B[wn]), T = wq(B[sn]);
        { const link = p.link || (p.link = bodyLink(sn)), mp = bodyMovPts(sn, link), ob = bodyObsWorld(link), allow = bodyAllow(T, S_, mp, ob, link);
          const [, used, m] = bodySafe(T, new Q().setFromAxisAngle(u, o).multiply(T), S_, mp, ob, link, allow);
          if (used) { o *= m; p.S = th + o; p.v = 0; netN++; if (rec) sr.contact.add(f); } }
        rotateWorld(B[sn], new Q().setFromAxisAngle(u, o)); model.updateMatrixWorld(true); setWorldQuat(B[wn], wq0); model.updateMatrixWorld(true);
        if (rec) { sr.out[f] = wq(B[sn]); sr.base[f] = T; if (Math.abs(o) > sr.peak) { sr.peak = Math.abs(o); sr.peakF = f; } }
        p.Tp = th;
      }
    });
    if (rec) { const ol = {}; for (const n of BN) ol[n] = pack(n); out[f] = ol; base[f] = bl; }
  }
  if (P.loop) { out[NFR()] = out[1]; base[NFR()] = base[1]; series.forEach(s => { s.out[NFR()] = s.out[1]; s.base[NFR()] = s.base[1]; }); }
  let AP = null;
  if (apAny()) { AP = apPost(out, last, RAG, parts.map(p => p.bone), base); if (P.loop) out[NFR()] = out[1]; }
  if (RAG && RAG.RG && ragGoalOn()) ragGoalFinish(RAG, out, last);
  edited = ed; handQ = hq0;
  PHYS = { net: netN, out, base, series, ap: AP, parts: parts.map(p => ({ bone: p.bone, type: p.type })), ms: performance.now() - t0,
    rag: ragSummary(RAG), imp: IMP ? { steps: IMP.steps, need: IMP.need, fell: IMP.fell, rec: IMP.rec, pre, inj: IMP.inj || {}, hits: IMP.hits.map(h => ({ f: h.f, dur: h.dur, seg: h.i.seg, x: h.x.toArray(), j: h.j.toArray(), v: h.r.v.toArray(), w: h.r.w.toArray(), ke: h.r.ke })) } : null };
}
function applyPhys(f) {
  if (physDirty) {
    try { computePhys(); } catch (e) { PHYS = null; $("p_status").textContent = "Vật lý lỗi, đang hiện pose key: " + (e && e.message || e); console.error(e); }
    if (physOn()) evalPose(f);
  }
  if (!PHYS || !physOn()) return;
  const o = PHYS.out[f] || PHYS.out[cyc(f)]; if (!o) return;
  for (const n of BN) if (o[n]) { B[n].quaternion.fromArray(o[n], 0); B[n].position.fromArray(o[n], 4); }
  model.updateMatrixWorld(true);
}
const nearPk = (a, b) => a && b && a.every((x, i) => Math.abs(x - b[i]) < (i < 4 ? 2e-5 : 2e-4));
function unphys(f, pose) {         // a key never stores the physics offset: physics comes on top of the key again
  if (!PHYS || !physOn()) return pose;
  const o = PHYS.out[f], b = PHYS.base[f]; if (!o || !b) return pose;
  const r = { ...pose };
  for (const n of Object.keys(r)) {
    if (!o[n] || !b[n] || nearPk(o[n], b[n])) continue;
    if (nearPk(r[n], o[n])) { r[n] = b[n]; continue; }          // untouched: the key pose
    // edited on top of the physics: keep the edit relative to what was shown (key = edit * out^-1 * base)
    const qe = new Q().fromArray(r[n]), qo = new Q().fromArray(o[n]), qb = new Q().fromArray(b[n]);
    const qk = qe.multiply(qo.invert()).multiply(qb); r[n] = [...qk.toArray().map(x => +x.toFixed(6)), ...r[n].slice(4)];
  }
  return r;
}
// ---------------------------------------------------------------- body collision (docs/poselab_physics_p2.md)
// Shapes built once per model from its skinned mesh, in the character's REST pose (Idle F1, CHAR_PHYS.<char>.rest):
// a thin core capsule per body segment (bone -> child joint, radius = 40th percentile of the distance of the vertices
// whose main weight is on that segment, 10-90 % along it; a segment 30 % thicker than its mirror takes the mirror's)
// and ~160 surface points of that segment (armor included); props (Weapon / gun) are surface points only. Depth =
// how far one segment's surface reaches into the other's core. Measured 2026-10-25: capsules at
// the 60th percentile with armor inside flagged the shield 10 cm into the knee and the mace 13 cm into the head where
// nothing intersects. Depth is reported RELATIVE to the rest pose (armpits, inner thighs touch at rest).
const BODY_SEG = { Root_M: "Spine1_M", Spine1_M: "Chest_M", Chest_M: "Neck_M", Neck_M: "Head_M", Head_M: "HeadEnd_M",
  Shoulder_L: "Elbow_L", Elbow_L: "Wrist_L", Wrist_L: "MiddleFinger2_L", Shoulder_R: "Elbow_R", Elbow_R: "Wrist_R", Wrist_R: "MiddleFinger2_R",
  Hip_L: "Knee_L", Knee_L: "Ankle_L", Ankle_L: "ToesEnd_L", Hip_R: "Knee_R", Knee_R: "Ankle_R", Ankle_R: "ToesEnd_R" };
const BODY_LABEL = { Root_M: "hông", Spine1_M: "bụng", Chest_M: "ngực", Neck_M: "cổ", Head_M: "đầu", Shoulder_L: "cánh tay trái",
  Elbow_L: "cẳng tay trái", Wrist_L: "bàn tay trái", Shoulder_R: "cánh tay phải", Elbow_R: "cẳng tay phải", Wrist_R: "bàn tay phải",
  Hip_L: "đùi trái", Knee_L: "cẳng chân trái", Ankle_L: "bàn chân trái", Hip_R: "đùi phải", Knee_R: "cẳng chân phải", Ankle_R: "bàn chân phải",
  Weapon: "vũ khí", slingshot_0: "vũ khí" };
const bodyName = n => BODY_LABEL[n] || physName(n);
const BODY_PCT = 0.4, BODY_TH_CM = 2, GRIP_CM = 6, FLOOR_TH_CM = 2;
let BODY = null, BODYSCAN = null, bodyDirty = true;
const bodyGroup = n => /Finger/.test(n) ? "Wrist_" + n.slice(-1) : /^Toes/.test(n) ? "Ankle_" + n.slice(-1) : n === "HeadEnd_M" ? "Head_M"
  : /^Scapula_/.test(n) ? "Chest_M" : n;     // the trapezius hump beside the head belongs to the torso, not the arm
function withPose(packs, fn) {        // run fn with the model in another pose (locals), then put the pose back
  const keep = {}; for (const n of BN.length ? BN : Object.keys(B)) keep[n] = [B[n].quaternion.clone(), B[n].position.clone()];
  try {
    if (packs) for (const [n, v] of Object.entries(packs)) if (B[n]) { B[n].quaternion.fromArray(v, 0); B[n].position.fromArray(v, 4); }
    model.updateMatrixWorld(true); return fn();
  } finally { for (const [n, [q, p]] of Object.entries(keep)) { B[n].quaternion.copy(q); B[n].position.copy(p); } model.updateMatrixWorld(true); }
}
function bodyPairs(props) {
  const torso = ["Root_M", "Spine1_M", "Chest_M", "Neck_M", "Head_M"], legs = ["Hip_L", "Knee_L", "Ankle_L", "Hip_R", "Knee_R", "Ankle_R"], P2 = [];
  for (const s of ["L", "R"]) for (const a of ["Shoulder_", "Elbow_", "Wrist_"].map(x => x + s)) for (const b of [...torso, ...legs]) {
    if (a.startsWith("Shoulder_") && ["Spine1_M", "Chest_M", "Neck_M"].includes(b)) continue;     // attached there
    P2.push([a, b]);
  }
  for (const a of ["Elbow_L", "Wrist_L"]) for (const b of ["Elbow_R", "Wrist_R"]) P2.push([a, b]);
  P2.push(["Knee_L", "Knee_R"], ["Ankle_L", "Ankle_R"], ["Knee_L", "Ankle_R"], ["Knee_R", "Ankle_L"]);
  for (const p of props) for (const b of Object.keys(BODY_SEG)) P2.push([p, b]);
  return P2.filter(([a, b]) => B[a] && B[b]);
}
function buildBody() {
  const RSc = (RIGSET() && RIGSET().colliders) || {}, rigR = Object.fromEntries(Object.entries(RSc).map(([k, c]) => [k, c.r]));
  const ch = charPhys() || {}, over = { ...rigR, ...((ANIM.phys && ANIM.phys.bodyR) || {}) };
  return withPose(ch.rest || null, () => {
    const pts = {}, own = {}; for (const k of Object.keys(BODY_SEG)) { pts[k] = []; own[k] = []; }   // own: for the core radius
    model.traverse(m => {
      if (!m.isSkinnedMesh) return;
      const sk = m.skeleton, si = m.geometry.attributes.skinIndex, sw = m.geometry.attributes.skinWeight, pos = m.geometry.attributes.position;
      for (let v = 0; v < pos.count; v++) {
        let bi = -1, bw = 0; for (let c = 0; c < 4; c++) { const w = comp(sw, v, c); if (w > bw) { bw = w; bi = comp(si, v, c); } }
        if (bi < 0) continue; const nm = sk.bones[bi].name, g = bodyGroup(nm); if (!pts[g]) continue;
        const p = new V3().fromBufferAttribute(pos, v); m.boneTransform(v, p); m.localToWorld(p); pts[g].push(p);
        if (!/^Scapula_/.test(nm)) own[g].push(p);
      }
    });
    const caps = {}, shells = {}, raw = {};
    const geo = b => { const A = wp(B[b]), E = wp(B[BODY_SEG[b]]), ab = E.clone().sub(A), L2 = Math.max(ab.lengthSq(), 1e-9);
      return { A, E, dOf: p => { const t = Math.min(1, Math.max(0, p.clone().sub(A).dot(ab) / L2)); return [p.distanceTo(A.clone().addScaledVector(ab, t)), t]; } }; };
    for (const b of Object.keys(BODY_SEG)) {
      if (!B[b] || !B[BODY_SEG[b]]) continue;
      const { dOf } = geo(b), ds = [];
      for (const p of own[b]) { const [d, t] = dOf(p); if (t > 0.1 && t < 0.9) ds.push(d); }
      ds.sort((x, y) => x - y); raw[b] = ds.length ? ds[Math.floor(ds.length * BODY_PCT)] : 0.02;
    }
    for (const [b, c] of Object.entries(BODY_SEG)) {
      if (raw[b] == null) continue;
      const { A, E, dOf } = geo(b), m = /_[LR]$/.test(b) ? b.slice(0, -1) + (b.endsWith("L") ? "R" : "L") : null;
      // a shield wraps the whole right forearm (even its closest 5 % of vertices are 17 cm out): a segment 30 % thicker
      // than its mirror takes the mirror's radius, the rest is armor
      let r = m && raw[m] != null && raw[b] > 1.3 * raw[m] ? raw[m] : raw[b];
      if (over[b] != null) r = over[b] * CM_W;
      const inv = wmat4(B[b]).invert(), rc = RSc[b] || {}, dd = E.clone().sub(A).normalize();   // Rig 6: nới / rút hai đầu capsule (cm)
      const A2 = A.clone().addScaledVector(dd, -(rc.e0 || 0) * CM_W), E2 = E.clone().addScaledVector(dd, (rc.e1 || 0) * CM_W);
      caps[b] = { a: A2.applyMatrix4(inv), b: E2.applyMatrix4(inv), r };
      // surface points of the segment (armor included): another segment's surface inside this thin core = a real
      // intersection (capsule-vs-capsule flagged the head 17 cm into the arm where the meshes only touch)
      const st = Math.max(1, Math.floor(pts[b].length / 160)); shells[b] = pts[b].filter((_, i) => i % st === 0).map(p => p.clone().applyMatrix4(inv));
      if (RSc[b] && RSc[b].on === false) delete shells[b];   // Rig tắt collider đoạn này: không va chạm (khối lượng vẫn tính)
    }
    const props = [B.Weapon ? "Weapon" : null, B[GUN] ? GUN : null].filter(Boolean);
    for (const p of props) { const pp = propPoints(p); if (pp.length) shells[p] = pp; }
    const reach = {};                // farthest surface point from the segment's own core axis (props: from their centroid)
    for (const [k, sh] of Object.entries(shells)) {
      const c = caps[k]; if (c) { reach[k] = Math.max(c.r, ...sh.map(p => p.distanceTo(closestOnSeg(p, c.a, c.b)))); continue; }
      const m = sh.reduce((a, p) => a.add(p), new V3()).divideScalar(sh.length); reach[k] = { m, r: Math.max(...sh.map(p => p.distanceTo(m))) };
    }
    const body = { caps, shells, reach, props, pairs: bodyPairs(props.filter(p => shells[p])), rest: {} };
    const W = bodyWorld(body);
    for (const [a, b] of body.pairs) body.rest[a + "~" + b] = pairDepth(W, a, b);
    return body;
  });
}
function bodyWorld(body) {            // capsules (world a, b, r), surface points and bounds at the current pose
  const caps = {}, shells = {}, bound = {};
  for (const [k, c] of Object.entries(body.caps)) { const M = wmat4(B[k]); caps[k] = { a: c.a.clone().applyMatrix4(M), b: c.b.clone().applyMatrix4(M), r: c.r }; }
  for (const [k, s] of Object.entries(body.shells)) { const M = wmat4(B[k]); shells[k] = s.map(p => p.clone().applyMatrix4(M)); }
  for (const [k, r] of Object.entries(body.reach || {})) bound[k] = typeof r === "number" ? { a: caps[k].a, b: caps[k].b, r } : { a: r.m.clone().applyMatrix4(wmat4(B[k])), b: null, r: r.r };
  return { caps, shells, bound };
}
function farApart(W, x, y) {           // the two bounds do not even touch: no point can be inside the other's core
  const u = W.bound[x], v = W.bound[y]; if (!u || !v) return false;
  const d = u.b && v.b ? segSegDist(u.a, u.b, v.a, v.b) : u.b ? v.a.distanceTo(closestOnSeg(v.a, u.a, u.b)) : v.b ? u.a.distanceTo(closestOnSeg(u.a, v.a, v.b)) : u.a.distanceTo(v.a);
  return d > u.r + v.r;
}
function closestOnSeg(p, a, b) { const ab = b.clone().sub(a), t = Math.min(1, Math.max(0, p.clone().sub(a).dot(ab) / Math.max(ab.lengthSq(), 1e-12))); return a.clone().addScaledVector(ab, t); }
function segSegDist(p1, q1, p2, q2) {
  const d1 = q1.clone().sub(p1), d2 = q2.clone().sub(p2), r = p1.clone().sub(p2), a = d1.dot(d1), e = d2.dot(d2), f = d2.dot(r);
  const c = d1.dot(r), b = d1.dot(d2), den = a * e - b * b;
  let s = den > 1e-12 ? Math.min(1, Math.max(0, (b * f - c * e) / den)) : 0, t = e > 1e-12 ? (b * s + f) / e : 0;
  if (t < 0) { t = 0; s = a > 1e-12 ? Math.min(1, Math.max(0, -c / a)) : 0; } else if (t > 1) { t = 1; s = a > 1e-12 ? Math.min(1, Math.max(0, (b - c) / a)) : 0; }
  return p1.clone().addScaledVector(d1, s).distanceTo(p2.clone().addScaledVector(d2, t));
}
function pairDepth(W, x, y) {          // how deep x's surface goes into y's core or y's surface into x's core (m; <= 0 = apart)
  let d = -1e9; const cx = W.caps[x], cy = W.caps[y], sx = W.shells[x], sy = W.shells[y];
  if (W.bound && farApart(W, x, y)) return d;
  if (sx && cy) for (const p of sx) d = Math.max(d, cy.r - p.distanceTo(closestOnSeg(p, cy.a, cy.b)));
  if (sy && cx) for (const p of sy) d = Math.max(d, cx.r - p.distanceTo(closestOnSeg(p, cx.a, cx.b)));
  return d;
}
function gripping(W, prop) {           // hands holding the prop this frame (a hand on the haft is not a collision):
  const s = W.shells[prop], out = new Set(); if (!s) return out;   // a prop point within 6 cm of the hand's core
  for (const h of ["L", "R"]) { const c = W.caps["Wrist_" + h]; if (!c) continue;
    if (s.some(q => q.distanceTo(closestOnSeg(q, c.a, c.b)) < c.r + GRIP_CM * CM_W)) out.add(h); }
  return out;
}
function bodyIssues(W, body) {         // pairs deeper than at rest by more than the threshold -> [{a, b, cm}]
  const out = [], grip = {}, cols = new Set(((ANIM.phys && ANIM.phys.colliders) || []).map(c => c.bone));
  for (const p of body.props) grip[p] = gripping(W, p);
  for (const [a, b] of body.pairs) {
    if (body.props.includes(a)) {
      const s = b.slice(-1);
      if ((b.startsWith("Wrist_") || b.startsWith("Elbow_")) && grip[a].has(s)) continue;     // held
      if (cols.has(b) || cols.has(b.replace("Shoulder_", "Scapula_"))) continue;               // declared rest (mace on shoulder)
    }
    const d = pairDepth(W, a, b) - Math.max(0, body.rest[a + "~" + b] ?? 0);
    if (d > BODY_TH_CM * CM_W) out.push({ a, b, cm: Math.round(d / CM_W) });
  }
  for (const [k, sh] of Object.entries(W.shells)) {   // fall pack: nothing sinks into the floor (the feet stand at ~0)
    let lo = 1e9; for (const p of sh) if (p.y < lo) lo = p.y;
    if (-lo > FLOOR_TH_CM * CM_W) out.push({ a: k, b: "floor", cm: Math.round(-lo / CM_W) });
  }
  return out;
}
// ---------------------------------------------------------------- balance (phase 3, docs/poselab_physics_p3.md)
// Mass of each body segment ~ the volume of its core capsule (phase 2 shapes); a held prop weighs a share of the body
// (CHAR_PHYS.<char>.propMass %, Gaygor 15). Support = convex hull on the floor of the foot surface points (and prop
// points) less than 5 cm above it - or, if the clip has painted contact lanes, the feet painted on that frame.
// Capture point = CoM + horizontal velocity / w, w = sqrt(g / CoM height). Measured 2026-10-25: a plain "CoM inside the
// feet" test flags every step (Hit F7/F20, Walk single support) and the mace planted on the ground (Attack F33-49), so
// a run of frames with the capture point outside the support is judged at its end: something lands under it = a step
// caught in time (fine); nothing lands within 3 frames = leaning too far; it lands but does not hold the CoM = missed.
const BAL_G = 9.81, BAL_GROUND_CM = 5, BAL_OUT_CM = 5, BAL_RUN = 3;
let BAL = null;
const balPropPct = () => (ANIM.phys && ANIM.phys.propMass != null) ? ANIM.phys.propMass : ((charPhys() || {}).propMass ?? 10);
function hull2(pts) {                  // convex hull of [x, z] points (counter-clockwise)
  pts = pts.slice().sort((a, b) => a[0] - b[0] || a[1] - b[1]); if (pts.length < 3) return pts;
  const cr = (o, a, b) => (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0]), lo = [], up = [];
  for (const p of pts) { while (lo.length >= 2 && cr(lo[lo.length - 2], lo[lo.length - 1], p) <= 0) lo.pop(); lo.push(p); }
  for (let i = pts.length - 1; i >= 0; i--) { const p = pts[i]; while (up.length >= 2 && cr(up[up.length - 2], up[up.length - 1], p) <= 0) up.pop(); up.push(p); }
  return lo.slice(0, -1).concat(up.slice(0, -1));
}
function polyMargin(poly, q) {         // signed distance (m) of q to the polygon: + inside, - outside
  if (!poly.length) return -1e9;
  if (poly.length < 3) { let d = 1e9; for (let i = 0; i < poly.length; i++) { const a = poly[i], b = poly[(i + 1) % poly.length], ex = b[0] - a[0], ey = b[1] - a[1], L2 = ex * ex + ey * ey;
      const t = L2 > 1e-12 ? Math.max(0, Math.min(1, ((q[0] - a[0]) * ex + (q[1] - a[1]) * ey) / L2)) : 0; d = Math.min(d, Math.hypot(a[0] + ex * t - q[0], a[1] + ey * t - q[1])); } return -d; }
  let inside = true, md = 1e9;
  for (let i = 0; i < poly.length; i++) {
    const a = poly[i], b = poly[(i + 1) % poly.length], ex = b[0] - a[0], ey = b[1] - a[1];
    if (ex * (q[1] - a[1]) - ey * (q[0] - a[0]) < 0) inside = false;
    const t = Math.max(0, Math.min(1, ((q[0] - a[0]) * ex + (q[1] - a[1]) * ey) / Math.max(ex * ex + ey * ey, 1e-12)));
    md = Math.min(md, Math.hypot(a[0] + ex * t - q[0], a[1] + ey * t - q[1]));
  }
  return inside ? md : -md;
}
function balFrame(W, fr) {             // this pose -> {com, h, sup (hull), touch: Set of L/R/P}
  let M = 0; const c = new V3();
  for (const cp of Object.values(W.caps)) { const L = cp.a.distanceTo(cp.b), r = cp.r, v = Math.PI * r * r * L + 4 / 3 * Math.PI * r ** 3; M += v; c.addScaledVector(cp.a.clone().add(cp.b).multiplyScalar(0.5), v); }
  const pm = M * balPropPct() / 100;
  for (const p of BODY.props) { const s = W.shells[p]; if (!s || !s.length || pm <= 0) continue;
    const m = s.reduce((a, q) => a.add(q), new V3()).divideScalar(s.length); c.addScaledVector(m, pm); M += pm; }
  c.divideScalar(M);
  const lanes = CT.L.size + CT.R.size > 0, f = cyc(fr), touch = new Set(), pts = [], feetPts = [], G = BAL_GROUND_CM * CM_W;
  for (const s of ["L", "R"]) {
    const sh = W.shells["Ankle_" + s] || []; if (!sh.length) continue;
    const lo = Math.min(...sh.map(p => p.y)), on = lanes ? CT[s].has(f) : lo < G;
    if (!on) continue; touch.add(s); for (const p of sh) if (p.y < (lanes ? lo + 0.03 : G)) { pts.push([p.x, p.z]); feetPts.push([p.x, p.z]); }
  }
  for (const p of BODY.props) { const sh = W.shells[p] || []; const low = sh.filter(q => q.y < G); if (low.length) { touch.add("P"); for (const q of low) pts.push([q.x, q.z]); } }
  let bodyLow = 1e9;
  for (const [k, sh] of Object.entries(W.shells)) {   // lying / kneeling: body segments on the floor hold the body too
    if (BODY.props.includes(k) || /^Ankle_/.test(k)) continue;
    for (const q of sh) if (q.y < bodyLow) bodyLow = q.y;
    const low = sh.filter(q => q.y < G); if (low.length) { touch.add("T:" + k); for (const q of low) pts.push([q.x, q.z]); }
  }
  return { com: c, h: Math.max(0.3, c.y), sup: hull2(pts), feet: feetPts, touch, bodyLow };
}
function balAnalyse(rows) {            // per-frame rows -> capture points, margins, runs, issues
  const N = rows.length, fps = P.fps || 30, loop = !!P.loop, out = [];
  const at = i => loop ? rows[((i % N) + N) % N] : rows[Math.max(0, Math.min(N - 1, i))];
  rows.forEach((r, i) => {
    const a = at(i - 1), b = at(i + 1), span = loop ? 2 : (Math.min(N - 1, i + 1) - Math.max(0, i - 1)) || 1;
    const vx = (b.com.x - a.com.x) * fps / span, vz = (b.com.z - a.com.z) * fps / span, w = Math.sqrt(BAL_G / r.h);
    r.cap = [r.com.x + vx / w, r.com.z + vz / w]; r.mCom = polyMargin(r.sup, [r.com.x, r.com.z]); r.mCap = polyMargin(r.sup, r.cap);
    r.out = r.sup.length > 0 && r.mCap < -BAL_OUT_CM * CM_W; r.state = "ok";
  });
  const issues = [];
  for (let i = 0; i < N;) {             // runs of "capture point outside", each ended by a landing or by coming back
    if (!rows[i].out) { i++; continue; }
    let j = i, land = -1;
    while (true) {                      // a foot / the prop that lands closes the run (a step), the next frames start anew
      const nk = j + 1; if (nk >= N && !loop) break; if (nk >= N + i) break;
      const prev = at(j), cur = at(nk), news = [...cur.touch].filter(t => !prev.touch.has(t));
      if (news.length) { land = nk; break; }
      if (!cur.out || nk >= N) break;
      j = nk;
    }
    const len = j - i + 1, run = rows.slice(i, j + 1), worst = run.reduce((m, r) => r.mCap < m.mCap ? r : m);
    const comOut = run.some(r => r.mCom < -BAL_OUT_CM * CM_W);     // the CoM itself, not only its momentum
    let kind = null;
    if (land >= 0) { const L = at(land); if (polyMargin(L.sup, [L.com.x, L.com.z]) <= -BAL_OUT_CM * CM_W) kind = "missed"; }
    else if (len > BAL_RUN) kind = comOut ? "lean" : "momentum";
    for (const r of run) r.state = kind ? "bad" : "step";
    if (kind === "lean") { const w2 = run.reduce((m, r) => r.mCom < m.mCom ? r : m); issues.push({ kind, from: rows[i].f, to: rows[j].f, cm: Math.round(-w2.mCom / CM_W), at: w2.f }); }
    else if (kind) issues.push({ kind, from: rows[i].f, to: rows[j].f, cm: Math.round(-worst.mCap / CM_W), at: worst.f });
    i = j + 1;
  }
  for (let i = 0; i < N;) {             // airborne: nothing touches -> the CoM must fall with g
    if (rows[i].touch.size) { i++; continue; }
    let j = i; while (j + 1 < N && !rows[j + 1].touch.size) j++;
    if (j - i + 1 >= 3) {
      let acc = 0, n = 0; for (let k = i; k <= j; k++) { const a = at(k - 1), b = at(k + 1); acc += (b.com.y - 2 * rows[k].com.y + a.com.y) * fps * fps; n++; }
      const ratio = -acc / n / BAL_G;
      if (ratio < 0.7 || ratio > 1.3) { for (let k = i; k <= j; k++) rows[k].state = "bad"; issues.push({ kind: "air", from: rows[i].f, to: rows[j].f, ratio: +ratio.toFixed(2), at: rows[i].f }); }
    }
    i = j + 1;
  }
  return issues;
}
// ---------------------------------------------------------------- falls (fall/death pack, docs/poselab_physics_p4_fall.md)
// A fall = a run of frames with the capture point outside the support that ends when a BODY segment lands on the floor.
// Reference: the whole body as one rigid block toppling about the support edge nearest the CoM, from the clip's own tilt
// and tilt speed at the first frame (theta'' = g h / (h^2 + k^2) sin theta, k = 0.3 m), until the CoM is as low as in the
// clip when it lands; a mostly vertical drop (collapse) uses free fall from the clip's own vertical speed. Gaygor
// (2026-10-25): 28-43 F toppling from standing, 13-20 F when knocked, 9-12 F collapsing - the start speed decides.
const FALL_K = 0.3, FALL_TOL_F = 2;
function fallRef(rows, i, land, fps) {
  const r0 = rows[i], prev = rows[Math.max(0, i - 1)], nxt = rows[Math.min(rows.length - 1, i + 1)], L = rows[land];
  const src = prev.feet.length ? prev : r0, sup = src.feet.length ? src.feet : src.sup;   // a body topples about its FEET
  // the fall direction (CoM start -> landing, on the floor) and the support edge on that side = the pivot
  const dir = new V3(L.com.x - r0.com.x, 0, L.com.z - r0.com.z); if (dir.lengthSq() < 1e-8) dir.set(1, 0, 0); dir.normalize();
  let piv = sup[0] || [r0.com.x, r0.com.z]; for (const p of sup) if (p[0] * dir.x + p[1] * dir.z > piv[0] * dir.x + piv[1] * dir.z) piv = p;
  const P0 = new V3(piv[0], 0, piv[1]), arm = c => c.clone().sub(P0), planar = a => Math.hypot(a.x * dir.x + a.z * dir.z, a.y), h = planar(arm(r0.com));   // in the fall plane (sideways offset does not fall)
  const tilt = c => { const a = arm(c); return Math.atan2(a.x * dir.x + a.z * dir.z, a.y); };   // signed: + = beyond the edge
  const th0 = tilt(r0.com), w0 = (tilt(nxt.com) - tilt(prev.com)) / Math.max(1, Math.min(rows.length - 1, i + 1) - Math.max(0, i - 1)) * fps;
  const horiz = Math.hypot(L.com.x - r0.com.x, L.com.z - r0.com.z), drop = r0.com.y - L.com.y;
  const kind = horiz < 0.3 * drop ? "collapse" : "topple", curve = [];
  let tHit = null;
  if (kind === "topple") {
    let th = th0, w = w0, t = 0; const dt = 1 / (fps * 50), yLand = L.com.y, A = BAL_G * h / (h * h + FALL_K * FALL_K);
    for (let s = 0; s < fps * 50 * 6; s++) {
      if (s % 50 === 0) curve.push({ y: h * Math.cos(th), th });
      if (h * Math.cos(th) <= yLand || th >= Math.PI / 2) { tHit = t; break; }
      w += A * Math.sin(th) * dt; th += w * dt; t += dt;
    }
  } else {
    const v0 = Math.min(0, (nxt.com.y - prev.com.y) / Math.max(1, Math.min(rows.length - 1, i + 1) - Math.max(0, i - 1)) * fps);   // m/s, down < 0
    tHit = (v0 + Math.sqrt(v0 * v0 + 2 * BAL_G * Math.max(0, drop))) / BAL_G;      // drop = -v0 t + g t^2 / 2 (v0 <= 0)
    for (let k = 0; k <= Math.ceil(tHit * fps); k++) { const t = Math.min(tHit, k / fps); curve.push({ y: r0.com.y + v0 * t - 0.5 * BAL_G * t * t }); }
  }
  const animF = L.f - r0.f, refF = tHit == null ? null : tHit * fps;
  // ease-out: the clip's CoM slows down in the last frames before the landing (a real fall is fastest there)
  const vs = []; for (let k = i + 1; k <= land; k++) vs.push(-(rows[k].com.y - rows[k - 1].com.y) * fps);
  const peak = Math.max(...vs, 0), lastV = vs.length ? vs[vs.length - 1] : 0, easeOut = vs.length >= 3 && peak > 0.5 && lastV < 0.6 * peak;
  return { kind, from: r0.f, to: L.f, animF, refF: refF == null ? null : +refF.toFixed(1), th0, w0, h, pivot: P0, dir, curve, easeOut };
}
function balFalls(rows) {              // a BODY segment reaches the floor (lowest point <= 2 cm) after the CoM has dropped
  const out = [], fps = P.fps || 30;   // > 25 cm; the fall starts where the CoM begins to go down without stopping
  for (let k = 1; k < rows.length; k++) {
    if (!(rows[k].bodyLow <= FLOOR_TH_CM * CM_W && rows[k - 1].bodyLow > FLOOR_TH_CM * CM_W)) continue;
    let s = k; while (s > 0 && rows[s - 1].com.y >= rows[s].com.y - 0.002 && k - s < 2 * fps) s--;
    while (s < k && !rows[s].out && rows[s].mCom > 0.05) s++;           // still standing well inside the feet: not falling yet
    if (s >= k || rows[s].com.y - rows[k].com.y < 0.25) continue;
    out.push(fallRef(rows, s, k, fps));
  }
  return out;
}
function scanBody() {                  // every frame as shown (physics included) -> BODYSCAN[f] = issues
  if (!keysMode() || !model || editedList().length) return;   // never over an unsaved edit on screen
  bodyDirty = false; BODYSCAN = null;
  if (!BODY) BODY = buildBody();
  const t0 = performance.now(), out = {}, keep = frame, rows = [];
  for (let f = 1; f <= NFR(); f++) {
    sampleAt(f); model.updateMatrixWorld(true); const W = bodyWorld(BODY); out[f] = bodyIssues(W, BODY);
    if (!P.loop || f < NFR()) rows.push({ f, ...balFrame(W, f), pose: poseNow() });   // loop: the last frame is F1
  }
  sampleAt(keep); model.updateMatrixWorld(true);
  BODYSCAN = { issues: out, ms: performance.now() - t0 };
  BAL = { rows, issues: balAnalyse(rows) }; BAL.falls = balFalls(rows);
  BAL.issues = BAL.issues.filter(it => !BAL.falls.some(fl => it.from <= fl.to && it.to >= fl.from));   // inside a fall: the fall itself
  for (const fl of BAL.falls) {          // a fall is judged against the physics: late / early landing, slowing down before it
    const d = fl.refF == null ? 0 : fl.animF - fl.refF;
    if (Math.abs(d) >= FALL_TOL_F || fl.easeOut) BAL.issues.push({ kind: "fall", from: fl.from, to: fl.to, cm: null, d: +d.toFixed(1), refF: fl.refF, animF: fl.animF, easeOut: fl.easeOut, fk: fl.kind, at: fl.from });
  }
}
// shapes on the model ("Hiện vùng va chạm"): capsules see-through, armor / prop shells as dots; the pairs that go
// deeper than at rest on this frame are red
let bodyViz = null, bodyVizOn = false;
const VIZ_OK = 0x5aa9ff, VIZ_BAD = 0xff4b3e;
function drawBodyViz() {
  if (bodyViz) { scene.remove(bodyViz); bodyViz.traverse(o => { if (o.geometry) o.geometry.dispose(); if (o.material) o.material.dispose(); }); bodyViz = null; }
  if (!bodyVizOn || !model || !keysMode()) return;
  if (!BODY) BODY = buildBody();
  model.updateMatrixWorld(true);
  const W = bodyWorld(BODY), bad = new Set();
  for (const it of bodyIssues(W, BODY)) { bad.add(it.a); bad.add(it.b); }
  bodyViz = new THREE.Group(); bodyViz.renderOrder = 3;
  const mat = c => new THREE.MeshBasicMaterial({ color: c, transparent: true, opacity: bad.size && c === VIZ_BAD ? 0.45 : 0.16, depthWrite: false });
  for (const [k, c] of Object.entries(W.caps)) {
    const col = bad.has(k) ? VIZ_BAD : VIZ_OK, len = c.a.distanceTo(c.b), mid = c.a.clone().add(c.b).multiplyScalar(0.5);
    const cyl = new THREE.Mesh(new THREE.CylinderGeometry(c.r, c.r, len, 16, 1, true), mat(col));
    cyl.position.copy(mid); if (len > 1e-6) cyl.quaternion.setFromUnitVectors(new V3(0, 1, 0), c.b.clone().sub(c.a).normalize());
    bodyViz.add(cyl);
    for (const e of [c.a, c.b]) { const sp = new THREE.Mesh(new THREE.SphereGeometry(c.r, 14, 10), mat(col)); sp.position.copy(e); bodyViz.add(sp); }
  }
  for (const [k, pts] of Object.entries(W.shells)) {
    if (!bad.has(k) && !BODY.props.includes(k)) continue;
    const g = new THREE.BufferGeometry().setFromPoints(pts);
    bodyViz.add(new THREE.Points(g, new THREE.PointsMaterial({ color: bad.has(k) ? VIZ_BAD : 0xf2b134, size: 4, sizeAttenuation: false, depthTest: false })));
  }
  scene.add(bodyViz);
}
function setKey(f, pose) { f = cyc(f); pose = liveOut(unphys(f, pose)); KEYS.set(f, { pose, at: new Date().toISOString(), ...(KEYS.get(f) && KEYS.get(f).main ? { main: true, ...(KEYS.get(f).phase ? { phase: KEYS.get(f).phase } : {}) } : {}) }); dirtyKeys.add(f); keysChanged(); }
function keysChanged() { buildTracks(); keySig = sigOf(KEYS); scheduleFlush(); renderStrip(); bodyChanged(); }
function reEval() {       // show the new evaluation of this frame (keeps the undo history)
  if (!model || editedList().length) { renderStrip(); return; }
  sampleAt(frame); model.updateMatrixWorld(true); if (ghost) ghost.updateMatrixWorld(true);
  rebase(); captureFeet(); attachGizmo(); refresh();
}
function commitEdit() {   // Auto key: an edit that ended becomes the key of this frame
  if (!keysMode() || !autoKey || !model || !editedList().length) return;
  setKey(frame, poseNow()); delete drafts[frame]; edited = new Set(); rebase(); captureFeet(); refresh();
  $("p_status").textContent = "Đã đặt key F" + cyc(frame) + ".";
}
function setAnim(patch) {
  Object.assign(ANIM, patch); animAt = new Date().toISOString(); animDirty = true; ANK = {}; physDirty = true; bodyDirty = true;
  scheduleFlush(); reEval(); bodyChanged();
}
$("kSet").onclick = () => {
  if (!model || !keysMode()) return;
  stopPlay(); pushUndo(); setKey(frame, poseNow()); delete drafts[frame]; edited = new Set(); rebase(); captureFeet(); refresh();
  $("p_status").textContent = "Đã đặt key F" + cyc(frame) + (cyc(frame) !== frame ? " (frame cuối = F1 của vòng lặp)" : "") + ".";
};
$("kDel").onclick = () => {
  const f = cyc(frame);
  if (!model || !keysMode() || !KEYS.has(f)) return;
  if (KEYS.size <= 1) { $("p_status").textContent = "Clip cần ít nhất 1 key."; return; }
  stopPlay(); pushUndo(); KEYS.delete(f); dirtyKeys.add(f); delete drafts[frame]; edited = new Set(); keysChanged(); reEval();
  $("p_status").textContent = "Đã xoá key F" + f + " (Ctrl+Z để lấy lại).";
};
$("kAuto").onclick = () => { autoKey = !autoKey; refresh(); };
$("kInterp").onclick = () => { setAnim({ interp: ANIM.interp === "step" ? "spline" : "step" }); refresh(); };
$("kLock").onclick = () => { setAnim({ lock: !ANIM.lock }); refresh(); };
$("kAutoCt").onclick = () => {
  if (!TR || TR.ks.length < 2) { $("p_status").textContent = "Cần ít nhất 2 key để dò chạm đất."; return; }
  const ks = TR.ks, m = ks.length, N = PER();
  for (const s of ["L", "R"]) {
    const hs = ks.map(k => ankW(k)[s].p.y), lo = Math.min(...hs), on = hs.map(h => h < lo + 0.03);   // within 3 cm of the lowest
    const S = new Set();
    for (let i = 0; i < m; i++) {
      if (!on[i]) continue;
      S.add(ks[i]);
      const nx = i + 1 < m ? i + 1 : (P.loop ? 0 : -1);
      if (nx < 0 || !on[nx]) continue;
      const end = nx > i ? ks[nx] : ks[nx] + N;
      for (let u = ks[i]; u <= end; u++) S.add(cyc(u));
    }
    CT[s] = S;
  }
  setAnim({}); refresh();
  $("p_status").textContent = "Đã dò chạm đất từ " + m + " key: trái " + (fmtSet(CT.L) || "không") + " · phải " + (fmtSet(CT.R) || "không") + ". Kéo trên dải màu để sửa.";
};
let paint = null;
const laneSet = s => s === "P" ? PINS : CT[s];
for (const s of ["L", "R", "P"]) {
  const el = $("lane" + s);
  el.addEventListener("pointerdown", e => {
    if (!keysMode() || !model) return;
    e.preventDefault(); try { el.setPointerCapture(e.pointerId); } catch {}
    const f = frameAtX(e.clientX); paint = { s, on: !laneSet(s).has(cyc(f)) }; paintAt(f);
  });
  el.addEventListener("pointermove", e => { if (paint && paint.s === s) paintAt(frameAtX(e.clientX)); });
  const end = () => { if (!paint) return; const ps = paint.s; paint = null; if (ps === "P") physChanged(); else setAnim({}); };
  el.addEventListener("pointerup", end); el.addEventListener("pointercancel", end);
}
function paintAt(f) {      // fills every frame between the last painted one and f (a fast drag skips cells)
  const a = paint.last ?? f; paint.last = f;
  for (let u = Math.min(a, f); u <= Math.max(a, f); u++) paint.on ? laneSet(paint.s).add(cyc(u)) : laneSet(paint.s).delete(cyc(u));
  renderLanes();
}

function scheduleFlush() { clearTimeout(flushT); flushT = setTimeout(flush, 700); }
async function flush() {
  if (!P || !keysMode()) return;
  const id = idOf(P.clip, P.version), clip = P.clip, version = P.version;
  if (!db) { saveLocal(); dirtyKeys = new Set(); animDirty = false; return; }
  if (!canWrite) { $("p_status").textContent = "Bạn đang ở quyền chỉ xem: key chỉ đổi trên máy bạn, không lưu được."; return; }
  if (!keysInDb) for (const f of KEYS.keys()) dirtyKeys.add(f);       // first save of this version: write every key
  const fs = [...dirtyKeys]; dirtyKeys = new Set();
  const wasAnim = animDirty; animDirty = false; flushing = true;
  try {
    for (const f of fs) {
      const ref = db.doc("keys/" + id + "-F" + f), k = KEYS.get(f);
      if (k) await ref.set({ clip, version, frame: f, pose: k.pose, at: k.at, ...(k.main ? { main: true } : {}), ...(k.phase ? { phase: k.phase } : {}), ...(myId ? { by: myId } : {}) });
      else await ref.delete();
    }
    keysInDb = true;
    if (wasAnim || !remoteAnims[id]) await db.doc("anims/" + id).set({ clip, version, interp: ANIM.interp, lock: ANIM.lock,
      contacts: { L: fmtSet(CT.L), R: fmtSet(CT.R) }, phys: ANIM.phys, at: animAt || new Date().toISOString(), ...(myId ? { by: myId } : {}) });
    $("p_status").textContent = "Đã lưu " + KEYS.size + " key (" + fmtTime(new Date().toISOString()) + ").";
  } catch (e) { fs.forEach(f => dirtyKeys.add(f)); if (wasAnim) animDirty = true; fail(e); }
  finally { flushing = false; quietUntil = Date.now() + 2500; setTimeout(applyRemote, 2700); }
}
function applyRemote() {    // keys / settings from the db (another viewer, or Claude) replace the local ones
  if (!ready || !keysMode() || !model || dirtyKeys.size || animDirty || flushing || gizmo.dragging || paint) return;
  if (Date.now() < quietUntil) return;     // echoes of our own key writes arrive one doc at a time: wait for the last one
  const id = idOf(P.clip, P.version);
  let src = remoteKeys[id], seeded = false;
  if (!src && P.seedFrom) { src = remoteKeys[idOf(P.clip, P.seedFrom)]; seeded = !!src; }
  let changed = false;
  if (src) {
    const m = new Map(Object.values(src).map(d => [d.frame, { pose: d.pose, at: d.at, ...(d.main ? { main: true } : {}), ...(d.phase ? { phase: d.phase } : {}) }]));
    keysInDb = !seeded;
    if (sigOf(m) !== keySig) { KEYS = m; keySig = sigOf(m); changed = true; }
  }
  const an = remoteAnims[id];
  // an OLDER copy (the echo of our own earlier save arriving late) must not undo a newer local change: user 2026-10-26
  // "không xóa được tác động" - the × removed the impact, then the echo of the slider save put it back and it was saved again
  if (an && an.at !== animAt && !(animAt && an.at < animAt)) {
    ANIM.interp = an.interp || "spline"; ANIM.lock = an.lock !== false; animAt = an.at;
    CT = { L: parseSet((an.contacts || {}).L), R: parseSet((an.contacts || {}).R) }; changed = true;
    if (an.phys) { ANIM.phys = JSON.parse(JSON.stringify(an.phys)); PINS = parseSet(an.phys.pin); }   // a copy: db data is frozen on claude.ai ("+ Tác động" push threw "object is not extensible")
  }
  if (changed) { buildTracks(); reEval(); renderPhys(); bodyChanged(true); }
}

// ---------------------------------------------------------------- fit to ref ("Khớp ref", no Blender)
// The ref videos are orthographic playblasts: 305.3 px per metre, floor at y 934.5 (1920x1080). POSES ref.cal holds per
// view the look direction, up vector and the pixel (u0, v0) where the world origin lands, calibrated on P0 vs ref F1
// (calibrateRef). The model is rendered white-on-black through that CAM() at half the sprite-cell size and compared
// with the ref silhouette (sprite cell, grey > 90, 3x3 open) by IoU. Stage "legs": hip move/turn, both feet (IK), knee
// twist, low region (below 0.96 m) of the 4 side views. Stage "body": spine / chest / head bends, mace on the shoulder,
// right hand, high region + top view. Coordinate search with a line search per parameter, step x0.55 per sweep.
const PPM = 305.3, FIT_K = 1, HIP_H = 0.96;
const CR = new V3(-1, 0, 0), CF = new V3(0, 0, 1), CU = new V3(0, 1, 0);       // character right / forward / up (glTF)
const rad = THREE.MathUtils.degToRad;
const cvec = (x, y, z) => CR.clone().multiplyScalar(x).add(CF.clone().multiplyScalar(y)).add(CU.clone().multiplyScalar(z));
const qAx = (ax, d) => new Q().setFromAxisAngle(ax, rad(d));
const fitCam = new THREE.OrthographicCamera(-1, 1, 1, -1, 0.1, 80);
const fitMat = new THREE.MeshBasicMaterial({ color: 0xffffff, skinning: true, side: THREE.DoubleSide });
const greyMat = new THREE.MeshLambertMaterial({ color: 0xb4b4b4, skinning: true });    // compare view: grey like the playblast
let fitRT = null, fitRun = null;
const refImgs = {}, refMasks = {}, fitCv = document.createElement("canvas");
const SIDE_VIEWS = ["front", "back", "left", "right"];
function cellOf(v) {
  const m = P.ref.views[v], c = m.crop, s = m.h / (c[3] - c[1]);
  return { m, c, s, w: Math.round(m.w * FIT_K), h: Math.round(m.h * FIT_K) };
}
function loadRefImg(v) {
  return refImgs[v] || (refImgs[v] = new Promise((res, rej) => { const im = new Image(); im.onload = () => res(im); im.onerror = rej; im.src = P.ref.dir + "/" + P.ref.views[v].file; }));
}
function open3(a, w, h) {
  const er = new Uint8Array(w * h), out = new Uint8Array(w * h);
  for (let y = 1; y < h - 1; y++) for (let x = 1; x < w - 1; x++) {
    let k = 1; for (let dy = -1; dy <= 1 && k; dy++) for (let dx = -1; dx <= 1; dx++) if (!a[(y + dy) * w + x + dx]) { k = 0; break; }
    er[y * w + x] = k;
  }
  for (let y = 1; y < h - 1; y++) for (let x = 1; x < w - 1; x++) {
    let k = 0; for (let dy = -1; dy <= 1 && !k; dy++) for (let dx = -1; dx <= 1; dx++) if (er[(y + dy) * w + x + dx]) { k = 1; break; }
    out[y * w + x] = k;
  }
  return out;
}
async function refMask(v, f) {
  const key = v + "|" + cyc(f); if (refMasks[key]) return refMasks[key];
  const { m, w, h } = cellOf(v), im = await loadRefImg(v);
  const nf = m.frames, i = (((f - 1 + (P.ref.offset || 0)) % nf) + nf) % nf, col = i % m.cols, row = Math.floor(i / m.cols);
  fitCv.width = w; fitCv.height = h; const cx = fitCv.getContext("2d", { willReadFrequently: true });
  cx.clearRect(0, 0, w, h); cx.drawImage(im, col * m.w, row * m.h, m.w, m.h, 0, 0, w, h);
  const d = cx.getImageData(0, 0, w, h).data, a = new Uint8Array(w * h);
  for (let k = 0; k < w * h; k++) a[k] = d[k * 4] * 0.299 + d[k * 4 + 1] * 0.587 + d[k * 4 + 2] * 0.114 > 90 ? 1 : 0;
  return (refMasks[key] = open3(a, w, h));
}
function setFitCam(v, cal) {
  const { m, c, s } = cellOf(v); cal = cal || P.ref.cal[v];
  const u0 = (cal.u0 - c[0]) * s, v0 = (cal.v0 - c[1]) * s, ppm = PPM * s;
  fitCam.left = -u0 / ppm; fitCam.right = (m.w - u0) / ppm; fitCam.top = v0 / ppm; fitCam.bottom = -(m.h - v0) / ppm;
  const dir = new V3(...cal.dir).normalize();
  fitCam.position.copy(dir.clone().multiplyScalar(-30)); fitCam.up.set(...cal.up); fitCam.lookAt(0, 0, 0);
  fitCam.updateProjectionMatrix(); fitCam.updateMatrixWorld(true);
}
function renderView(v, shaded, cal) {    // -> {w, h, px: RGBA rows top-down} through the ref CAM() of view v
  const { w, h } = cellOf(v), W = shaded ? P.ref.views[v].w : w, H = shaded ? P.ref.views[v].h : h;
  if (!fitRT || fitRT.width !== W || fitRT.height !== H) { if (fitRT) fitRT.dispose(); fitRT = new THREE.WebGLRenderTarget(W, H); }
  setFitCam(v, cal);
  const vis = [ghost.visible, grid.visible]; ghost.visible = false; grid.visible = false; ONION.list.forEach(o => o.root.visible = false);
  scene.overrideMaterial = shaded ? greyMat : fitMat;
  const cc = renderer.getClearColor(new THREE.Color()), ca = renderer.getClearAlpha();
  renderer.setRenderTarget(fitRT); renderer.setClearColor(0x000000, 1); renderer.clear(); renderer.render(scene, fitCam);
  const buf = new Uint8Array(W * H * 4); renderer.readRenderTargetPixels(fitRT, 0, 0, W, H, buf);
  renderer.setRenderTarget(null); renderer.setClearColor(cc, ca); scene.overrideMaterial = null;
  ghost.visible = vis[0]; grid.visible = vis[1];
  const px = new Uint8ClampedArray(W * H * 4);
  for (let y = 0; y < H; y++) px.set(buf.subarray((H - 1 - y) * W * 4, (H - y) * W * 4), y * W * 4);
  return { w: W, h: H, px };
}
function renderMask(v, cal) {
  const r = renderView(v, false, cal), a = new Uint8Array(r.w * r.h);
  for (let k = 0; k < a.length; k++) a[k] = r.px[k * 4] > 127 ? 1 : 0;
  return a;
}
function floorRow(v) { const { c, s } = cellOf(v); return Math.round((P.ref.cal[v].v0 - c[1]) * s * FIT_K); }
function hipRow(v) { const { c, s } = cellOf(v), cal = P.ref.cal[v]; return Math.max(0, Math.round((cal.v0 - HIP_H * PPM - c[1]) * s * FIT_K)); }
// Each foot's lowest point in the front / back views (columns split at the projected hip): IoU alone cannot tell which
// foot is lifted a few cm (first Walk fit lifted the wrong one), so the legs stage also matches these two rows to the ref.
function splitCol(v) { setFitCam(v); const { w } = cellOf(v), p = wp(B.Root_M).project(fitCam); return Math.round((p.x + 1) / 2 * w); }
function footLows(a, w, h, r0, sc) {
  const low = (c0, c1) => { for (let y = h - 1; y >= r0; y--) for (let x = c0; x < c1; x++) if (a[y * w + x]) return y; return r0; };
  return [low(0, sc), low(sc, w)];
}
function iouRows(a, b, w, r0, r1) {
  let i = 0, u = 0; for (let k = r0 * w; k < r1 * w; k++) { const x = a[k], y = b[k]; i += x & y; u += x | y; }
  return u ? i / u : 1;
}

const FIT_LEGS = { names: ["rt_x", "rt_y", "rt_z", "rt_yaw", "rt_pitch", "rt_roll", "R_x", "R_y", "R_z", "R_yaw", "R_pitch",
  "L_x", "L_y", "L_z", "L_yaw", "L_pitch", "kR", "kL", "R_heel", "L_heel"],
  step: [.03, .03, .03, 4, 4, 4, .04, .04, .02, 6, 6, .04, .04, .02, 6, 6, 8, 8, 6, 6],
  reg: { rt_yaw: .0025, rt_pitch: .0012, rt_roll: .0012, R_yaw: .002, L_yaw: .002, R_pitch: .0005, L_pitch: .0005, kR: .0004, kL: .0004,
         rt_x: .3, rt_y: .3,     // Walk F29 first fit: hip 20 cm forward + foot turned 28 deg to force the silhouette
         R_x: 1.5, L_x: 1.5, R_heel: .0003, L_heel: .0003 } };   // feet do not drift sideways (Walk F22/F29: right foot 26-35 cm out)
const FIT_BODY = { names: ["sp_fwd", "sp_side", "sp_twist", "ch_fwd", "ch_side", "ch_twist", "hd_fwd", "hd_side", "hd_twist",
  "wp_x", "wp_y", "wp_z", "wp_pitch", "wp_yaw", "hR_x", "hR_y", "hR_z"],
  step: [3, 3, 3, 3, 3, 3, 5, 5, 5, .03, .03, .03, 5, 5, .04, .04, .04],
  reg: { sp_fwd: .0008, sp_side: .0008, sp_twist: .0008, ch_fwd: .0008, ch_side: .0008, ch_twist: .0008, hd_fwd: .0005,
         hd_side: .0005, hd_twist: .0005, wp_pitch: .0006, wp_yaw: .0006, hR_x: .3, hR_y: .3, hR_z: .3 } };
const bendQ = (fwd, side, twist) => qAx(CU, twist).multiply(qAx(CF, side)).multiply(qAx(CR, -fwd));   // fwd + = toward the facing
function fitApply(S, legs, body) {     // start locals S + params -> pose on B (prop + grip follow)
  for (const [n, [p, q]] of Object.entries(S.loc)) { B[n].position.copy(p); B[n].quaternion.copy(q); }
  model.updateMatrixWorld(true);
  const ed = edited; edited = new Set();
  if (legs) {
    const L = legs, r = B.Root_M;
    setWorldPosB(r, wp(r).add(cvec(L.rt_x, L.rt_y, L.rt_z)));
    if (L.rt_yaw || L.rt_pitch || L.rt_roll) rotateWorld(r, qAx(CU, L.rt_yaw).multiply(qAx(CF, L.rt_roll)).multiply(qAx(CR, L.rt_pitch)));
    model.updateMatrixWorld(true);
    for (const s of ["L", "R"]) {
      const d = cvec(L[s + "_x"], L[s + "_y"], L[s + "_z"]);
      let t = S.ank[s].p.clone().add(d);
      let q = qAx(CU, L[s + "_yaw"]).multiply(qAx(CR, L[s + "_pitch"])).multiply(S.ank[s].q);
      if (L[s + "_heel"] && S.toe[s]) {      // heel roll: the foot turns about its toe tip (heel up +, down -), toe stays put
        const pv = S.toe[s].clone().add(d), fd = S.toe[s].clone().sub(S.ank[s].p); fd.y = 0; fd.normalize();
        const R = new Q().setFromAxisAngle(new V3().crossVectors(fd, CU).normalize(), rad(L[s + "_heel"]));
        t = t.sub(pv).applyQuaternion(R).add(pv); q = R.multiply(q);
      }
      solve2(LEGS[s], t, q);
      if (L["k" + s]) {
        const hip = B[LEGS[s][0]], ax = wp(B[LEGS[s][2]]).sub(wp(hip)).normalize();
        rotateWorld(hip, new Q().setFromAxisAngle(ax, rad(L["k" + s]))); setWorldQuat(B[LEGS[s][2]], q);
      }
    }
  }
  if (body) {
    const U = body;
    for (const [n, pre] of [["Spine1_M", "sp"], ["Chest_M", "ch"], ["Head_M", "hd"]])
      if (B[n] && (U[pre + "_fwd"] || U[pre + "_side"] || U[pre + "_twist"])) rotateWorld(B[n], bendQ(U[pre + "_fwd"], U[pre + "_side"], U[pre + "_twist"]));
    model.updateMatrixWorld(true);
    if (U.hR_x || U.hR_y || U.hR_z) { handQ.R = wq(B.Wrist_R); solveArm("R", wp(B.Wrist_R).add(cvec(U.hR_x, U.hR_y, U.hR_z))); }
  }
  if (S.rel) {
    let M = B[P.follow.to].matrixWorld.clone().multiply(S.rel.w);
    if (body && (body.wp_x || body.wp_y || body.wp_z || body.wp_pitch || body.wp_yaw)) {
      const p = new V3(), q = new Q(), sc = new V3(); M.decompose(p, q, sc);
      q.premultiply(qAx(CU, body.wp_yaw).multiply(qAx(CR, body.wp_pitch))); p.add(cvec(body.wp_x, body.wp_y, body.wp_z));
      M = new THREE.Matrix4().compose(p, q, sc);
    }
    propHandTo(M, S.rel.h);
  }
  edited = ed; model.updateMatrixWorld(true);
}
function setWorldPosB(o, p) { o.parent.updateMatrixWorld(true); o.position.copy(o.parent.worldToLocal(p.clone())); o.updateMatrixWorld(true); }
function fitStart() {
  model.updateMatrixWorld(true);
  const S = { loc: Object.fromEntries(Object.keys(B).map(n => [n, [B[n].position.clone(), B[n].quaternion.clone()]])), ank: {} };
  S.toe = {};
  for (const s of ["L", "R"]) { S.ank[s] = { p: wp(B[LEGS[s][2]]), q: wq(B[LEGS[s][2]]) }; if (B["ToesEnd_" + s]) S.toe[s] = wp(B["ToesEnd_" + s]); }
  if (hasFollow()) { const c = P.follow, Wp = B[c.prop].matrixWorld;
    S.rel = { w: B[c.to].matrixWorld.clone().invert().multiply(Wp), h: Wp.clone().invert().multiply(B[ARMS[c.hand][2]].matrixWorld) }; }
  return S;
}
async function fitStage(stage, S, legsP, onStep) {
  const D = stage === "legs" ? FIT_LEGS : FIT_BODY, f = frame;
  const views = stage === "legs" ? SIDE_VIEWS : [...SIDE_VIEWS, "top"];
  const refs = {}; for (const v of views) refs[v] = await refMask(v, f);
  const toObj = p => Object.fromEntries(D.names.map((n, i) => [n, p[i]]));
  let evals = 0;
  const FOOT_W = 0.006 / FIT_K;                       // IoU points per mask pixel of foot-height error
  const score = p => {
    const o = toObj(p);
    fitApply(S, stage === "legs" ? o : legsP, stage === "legs" ? null : o);
    let sum = 0, foot = 0, band = 0;
    for (const v of views) {
      const { w, h } = cellOf(v), a = renderMask(v), r = hipRow(v);
      if (stage === "legs" && (v === "left" || v === "right")) {   // floor band 0-6 cm: which part of each foot touches
        const fl = floorRow(v); band += iouRows(a, refs[v], w, fl - Math.round(0.06 * PPM * cellOf(v).s * FIT_K), fl + 2);
      }
      sum += v === "top" ? iouRows(a, refs[v], w, 0, h) : stage === "legs" ? iouRows(a, refs[v], w, r, h) : iouRows(a, refs[v], w, 0, Math.min(h, r + 20));
      if (stage === "legs" && (v === "front" || v === "back")) {
        const sc = splitCol(v), m = footLows(a, w, h, r, sc), f0 = footLows(refs[v], w, h, r, sc);
        foot += Math.abs(m[0] - f0[0]) + Math.abs(m[1] - f0[1]);
      }
    }
    // which foot is in front cannot be read from the silhouettes (side views overlap the feet): POSES fitFeet gives the
    // toe joint's forward position per key (world cm = front edge of that foot's 0-6 cm floor band in the side ref + 2;
    // planted feet slide back 2.1 cm/F), 0.003 per cm off
    const hint = stage === "legs" && P.fitFeet && P.fitFeet[cyc(f)];
    if (hint) for (const s of ["L", "R"]) if (hint[s] != null && B["ToesEnd_" + s]) foot += Math.abs(wp(B["ToesEnd_" + s]).z * 100 - hint[s]) * 0.003 / FOOT_W;
    evals++;
    return sum / views.length + 0.1 * band - FOOT_W * foot - D.names.reduce((acc, n, i) => acc + (D.reg[n] || 0) * Math.abs(p[i]), 0);
  };
  let p = new Array(D.names.length).fill(0);
  const hint0 = stage === "legs" && P.fitFeet && P.fitFeet[cyc(f)];
  if (hint0) for (const s of ["L", "R"]) if (hint0[s] != null && B["ToesEnd_" + s]) {   // start with the toe where the ref puts it
    fitApply(S, null, null); p[D.names.indexOf(s + "_y")] = (hint0[s] - wp(B["ToesEnd_" + s]).z * 100) / 100;
  }
  let best = score(p), step = D.step.slice();
  const start = best;
  for (let sw = 0; sw < (fitRun.sweeps || 4); sw++) {
    for (let i = 0; i < p.length; i++) {
      if (fitRun.stop) break;
      for (const sg of [1, -1]) {
        let moved = false;
        for (let k = 0; k < 8; k++) {
          const q = p.slice(); q[i] += sg * step[i];
          const sc = score(q);
          if (sc > best + 1e-4) { best = sc; p = q; moved = true; } else break;
        }
        if (moved) break;
      }
      if (evals % 6 === 0) { onStep(stage, sw, best); await new Promise(r => setTimeout(r)); }
    }
    step = step.map(x => x * 0.55);
  }
  return { params: toObj(p), score: best, start, evals };
}
async function fitRef() {
  if (!model || !keysMode() || !P.ref || !P.ref.cal) return;
  if (fitRun) { fitRun.stop = true; return; }
  stopPlay(); pushUndo();
  fitRun = { stop: false, sweeps: 4 }; $("kFit").textContent = "Dừng khớp";
  const t0 = performance.now(), f = frame;
  const say = (st, sw, sc) => { $("p_status").textContent = "Khớp ref F" + f + ": " + (st === "legs" ? "hông + chân" : "thân, đầu, chùy, tay") + " · lượt " + (sw + 1) + "/" + fitRun.sweeps + " · khớp " + (sc * 100).toFixed(1) + "%"; };
  try {
    const S = fitStart();
    const a = await fitStage("legs", S, null, say);
    let b = null; if (!fitRun.stop) b = await fitStage("body", S, a.params, say);
    fitApply(S, a.params, b ? b.params : null);
    FIT_LOG[cyc(f)] = { legs: a, body: b };
    if (!fitRun.stop) {
      for (const n of Object.keys(B)) edited.add(n);
      setKey(f, poseNow()); delete drafts[f]; edited = new Set(); rebase(); captureFeet();
    }
    $("p_status").textContent = (fitRun.stop ? "Đã dừng khớp ref F" : "Đã khớp ref và đặt key F") + f + ": hông/chân " + (a.start * 100).toFixed(0) + "→" + (a.score * 100).toFixed(0) +
      "%" + (b ? ", thân/tay " + (b.start * 100).toFixed(0) + "→" + (b.score * 100).toFixed(0) + "%" : "") + " (" + ((performance.now() - t0) / 1000).toFixed(0) + " s). Soi lại bằng mắt trước khi duyệt.";
  } catch (e) { $("p_status").textContent = "Khớp ref lỗi: " + (e && e.message || e); }
  finally { fitRun = null; $("kFit").textContent = "Khớp ref"; refresh(); renderRef(); }
}
const FIT_LOG = {};
async function calibrateRef(views, f = 1) {   // dev: search u0 (and v0 / up for top) so P0 at F1 matches the ref
  const out = {};
  for (const v of views) {
    const ref = await refMask(v, f), { w, h, c } = cellOf(v), base = P.ref.cal[v];
    const ups = v === "top" ? [[0, 0, 1], [0, 0, -1], [1, 0, 0], [-1, 0, 0]] : [base.up];
    let best = { s: -1 };
    for (const up of ups) {
      const tryCal = (u0, v0) => { const cal = { ...base, up, u0, v0 }; return { s: iouRows(renderMask(v, cal), ref, w, 0, h), cal }; };
      let cur = tryCal(base.u0, base.v0);
      for (const st of [80, 40, 20, 10, 5, 2, 1, 0.5]) {
        let moved = true;
        while (moved) {
          moved = false;
          for (const [du, dv] of v === "top" ? [[st, 0], [-st, 0], [0, st], [0, -st]] : [[st, 0], [-st, 0]]) {
            const t = tryCal(cur.cal.u0 + du, cur.cal.v0 + dv);
            if (t.s > cur.s + 1e-5) { cur = t; moved = true; }
          }
        }
      }
      if (cur.s > best.s) best = cur;
    }
    out[v] = { ...best.cal, iou: +best.s.toFixed(4) };
  }
  return out;
}
$("kFit").onclick = fitRef;

// ---------------------------------------------------------------- feet on the floor (mesh, not joints)
// The lowest skinned vertex of each foot (vertices whose main weight is on Ankle / Toes / ToesEnd) must sit on the floor
// when that foot is planted (contact lanes) and never below it (user 2026-10-23 screenshots: right foot sunk 4 cm at F22,
// planted left foot 2 cm in the air at F36 / F42). The foot moves straight up / down (leg IK, orientation kept).
let FOOTV = null;
function footVerts() {
  if (FOOTV && FOOTV.model === model) return FOOTV;
  FOOTV = { model, L: [], R: [] };
  model.traverse(m => {
    if (!m.isSkinnedMesh) return;
    const sk = m.skeleton, si = m.geometry.attributes.skinIndex.array, sw = m.geometry.attributes.skinWeight.array, n = m.geometry.attributes.position.count;
    const idx = Object.fromEntries(["L", "R"].map(s => [s, ["Ankle_", "Toes_", "ToesEnd_"].map(b => sk.bones.findIndex(x => x.name === b + s))]));
    for (let v = 0; v < n; v++) {
      let bi = -1, bw = 0; for (let k = 0; k < 4; k++) if (sw[v * 4 + k] > bw) { bw = sw[v * 4 + k]; bi = si[v * 4 + k]; }
      for (const s of ["L", "R"]) if (bi >= 0 && idx[s].includes(bi)) FOOTV[s].push([m, v]);
    }
  });
  return FOOTV;
}
function footLowY(s) {
  const t = new V3(); let lo = Infinity;
  for (const [m, v] of footVerts()[s]) { m.boneTransform(v, t); t.applyMatrix4(m.matrixWorld); if (t.y < lo) lo = t.y; }
  return lo;
}
function floorKey(f) {     // -> {L, R}: cm moved
  goto(f, true); model.updateMatrixWorld(true);
  const moved = {}, rel = hasFollow() ? fitStart().rel : null;
  for (const s of ["L", "R"]) {
    const lo = footLowY(s), planted = CT[s].has(cyc(f)), dy = planted ? -lo : Math.max(0, -lo);
    if (Math.abs(dy) < 0.003) continue;
    const a = B[LEGS[s][2]], q = wq(a), ed = edited; solve2(LEGS[s], wp(a).add(new V3(0, dy, 0)), q); edited = ed;
    moved[s] = +(dy * 100).toFixed(1);
  }
  if (Object.keys(moved).length) {
    if (rel) propHandTo(B[P.follow.to].matrixWorld.clone().multiply(rel.w), rel.h);
    for (const n of Object.keys(B)) edited.add(n); setKey(f, poseNow()); edited = new Set(); rebase();
  }
  return moved;
}
$("kFloor").onclick = () => {
  if (!model || !keysMode()) return;
  stopPlay(); pushUndo(); const cur = frame, out = [];
  for (const f of [...KEYS.keys()].sort((a, b) => a - b)) { const m = floorKey(f); if (Object.keys(m).length) out.push("F" + f + " " + Object.entries(m).map(([s, d]) => (s === "L" ? "trái " : "phải ") + (d > 0 ? "+" : "") + d + " cm").join(", ")); }
  goto(cur, true);
  $("p_status").textContent = out.length ? "Đã đặt chân lên sàn: " + out.join(" · ") + "." : "Mọi key đã chạm sàn đúng (chân chống ở 0 cm, không xuyên sàn).";
};

// ---------------------------------------------------------------- reference frames beside the model
// One sprite sheet per view (work/pose_lab/make_ref_sprites.py), the cell of the current frame is shown top-right.
// "Theo CAM()": Right / Front / Top CAM() -> the same ref view (3/4 keeps the last one).
let refOn = true, refView = "auto", refSize = 1, refLast = "right", refCmp = false;
const REF_H = [190, 290, 440], REF_LBL = { front: "Trước", back: "Sau", left: "Trái", right: "Phải", top: "Trên" };
function setupRef() {
  const r = P.ref; $("tRef").hidden = !r;
  if (!r) { $("refbox").hidden = true; return; }
  for (const v of Object.values(r.views)) { const im = new Image(); im.src = r.dir + "/" + v.file; }
  const bar = $("rbar"); bar.innerHTML = "";
  for (const v of ["auto", ...Object.keys(r.views)]) {
    const b = document.createElement("button"); b.dataset.v = v; b.className = "ibtn"; b.textContent = v === "auto" ? "Theo CAM()" : REF_LBL[v] || v; b.title = b.textContent;
    b.onclick = () => { refView = v; renderRef(); }; bar.append(b);
  }
  if (r.cal) {              // REF | ANIM: the model rendered through the same calibrated ref CAM(), next to the ref
    const b = document.createElement("button"); b.id = "rCmp"; b.className = "ibtn"; b.textContent = "So cạnh nhau";
    b.title = "So cạnh nhau: hiện model qua đúng CAM() của video ref, đặt cạnh ảnh ref (không chồng lên nhau)";
    b.onclick = () => { refCmp = !refCmp; renderRef(); }; bar.append(b);
  }
  renderRef();
}
function renderRef() {
  const r = P && P.ref, box = $("refbox");
  box.hidden = !r || !refOn; $("tRef").classList.toggle("on", !!r && refOn);
  if (box.hidden) return;
  const cm = ({ right: "right", left: "left", front: "front", back: "back", top: "top", ...(r.cams || {}) })[curCam];   // page CAM() -> ref view seen from the same side
  if (refView === "auto" && cm && r.views[cm]) refLast = cm;
  const v = refView === "auto" ? refLast : refView, m = r.views[v]; if (!m) return;
  for (const b of $("rbar").children) b.classList.toggle("on", b.dataset.v === refView);
  const nf = m.frames, i = (((frame - 1 + (r.offset || 0)) % nf) + nf) % nf, col = i % m.cols, row = Math.floor(i / m.cols);
  const h = REF_H[refSize], w = Math.round(h * m.w / m.h), rows = Math.ceil(nf / m.cols);
  Object.assign($("rimg").style, { width: w + "px", height: h + "px", backgroundImage: 'url("' + r.dir + "/" + m.file + '")',
    backgroundSize: m.cols * w + "px " + rows * h + "px", backgroundPosition: -col * w + "px " + -row * h + "px" });
  $("rcap").textContent = "Ref " + (REF_LBL[v] || v) + " · F" + (i + 1) + (refCmp && r.cal ? "  |  model F" + frame : "");
  const cv = $("ranim"); cv.hidden = !(refCmp && r.cal && r.cal[v] && model && !playing);
  if ($("rCmp")) $("rCmp").classList.toggle("on", refCmp);
  if (!cv.hidden) {
    const im = renderView(v, true); cv.width = im.w; cv.height = im.h; cv.style.width = w + "px"; cv.style.height = h + "px";
    cv.getContext("2d").putImageData(new ImageData(im.px, im.w, im.h), 0, 0);
  }
}
$("rimg").onclick = () => { refSize = (refSize + 1) % REF_H.length; renderRef(); };
$("tRef").onclick = () => { refOn = !refOn; renderRef(); };
// side panes can be hidden to give the viewport the full width (user 2026-10-23); the choice is kept in this browser
const PANES = { list: true, side: true };
try { Object.assign(PANES, JSON.parse(localStorage.getItem("poselab:panes") || "{}")); } catch {}
function applyPanes() {
  const m = document.querySelector(".main"), l = document.querySelector(".list"), sd = document.querySelector(".side");
  l.hidden = !PANES.list; sd.hidden = !PANES.side;
  m.style.gridTemplateColumns = (PANES.list ? "220px " : "") + "minmax(0, 1fr)" + (PANES.side ? " 310px" : "");
  $("tList").classList.toggle("on", PANES.list); $("tSide").classList.toggle("on", PANES.side);
  try { localStorage.setItem("poselab:panes", JSON.stringify(PANES)); } catch {}
  window.dispatchEvent(new Event("resize"));
}
if (host.panes) {   // Studio (user 2026-10-29 "hai nút này đang không hoạt động"): [ = cột trái (Outliner / Phiên bản), ] = dock phải của Studio
  const sync = () => { $("tList").classList.toggle("on", host.panes.on("list")); $("tSide").classList.toggle("on", host.panes.on("side")); };
  $("tList").onclick = () => { host.panes.toggle("list"); sync(); };
  $("tSide").onclick = () => { host.panes.toggle("side"); sync(); };
  $("tList").title = "Ẩn / hiện cột trái (Outliner, Phiên bản) ( [ )"; $("tSide").title = "Ẩn / hiện dock phải (Khớp, Vật lý, Góp ý cho AI) ( ] )";
  host.panes.onChange(sync); sync();
} else {
  $("tList").onclick = () => { PANES.list = !PANES.list; applyPanes(); };
  $("tSide").onclick = () => { PANES.side = !PANES.side; applyPanes(); };
  applyPanes();
}

// ---------------------------------------------------------------- vẽ ghi chú trên viewport (một ảnh mỗi lần lưu, tải lên assets)
const DV = { on: false, color: "#ff4d4d", strokes: [], cur: null };
const dvCv = $("drawCv");
function dvDraw(c, W, H, k) {
  for (const s of DV.cur ? DV.strokes.concat([DV.cur]) : DV.strokes) {
    c.strokeStyle = s.c; c.lineWidth = 3 * k; c.lineCap = c.lineJoin = "round"; c.beginPath();
    s.p.forEach(([x, y], i) => i ? c.lineTo(x * W, y * H) : c.moveTo(x * W, y * H));
    if (s.p.length === 1) c.lineTo(s.p[0][0] * W + 0.1, s.p[0][1] * H);
    c.stroke();
  }
}
function dvRender() {
  const dpr = Math.min(devicePixelRatio, 2), w = Math.round(viewer.clientWidth * dpr), h = Math.round(viewer.clientHeight * dpr);
  if (dvCv.width !== w || dvCv.height !== h) { dvCv.width = w; dvCv.height = h; }
  const c = dvCv.getContext("2d"); c.clearRect(0, 0, w, h); dvDraw(c, w, h, dpr);
  $("dvClear").disabled = $("dvUndo").disabled = !DV.strokes.length;
}
const dvPt = e => { const r = viewer.getBoundingClientRect(); return [(e.clientX - r.left) / r.width, (e.clientY - r.top) / r.height]; };
$("dvOn").onclick = () => { DV.on = !DV.on; viewer.classList.toggle("drawing", DV.on); $("dvOn").classList.toggle("on", DV.on); $("dvTools").hidden = !DV.on; dvRender(); };
for (const b of document.querySelectorAll("#dvTools .sw")) b.onclick = () => { DV.color = b.dataset.c; dvCursor(); document.querySelectorAll("#dvTools .sw").forEach(x => x.classList.toggle("on", x === b)); };
function dvCursor() {   // round brush cursor in the stroke colour with a white + black halo (a thin + was hard to see on the dark viewport)
  const c = DV.color, svg = "<svg xmlns='http://www.w3.org/2000/svg' width='28' height='28'><circle cx='14' cy='14' r='7' fill='none' stroke='black' stroke-width='4' opacity='.7'/><circle cx='14' cy='14' r='7' fill='none' stroke='white' stroke-width='2.5'/><circle cx='14' cy='14' r='2.2' fill='" + c + "' stroke='white' stroke-width='1'/></svg>";
  dvCv.style.cursor = 'url("data:image/svg+xml,' + encodeURIComponent(svg) + '") 14 14, crosshair';
}
dvCursor();
$("dvUndo").onclick = () => { DV.strokes.pop(); dvRender(); refresh(); };
$("dvClear").onclick = () => { DV.strokes = []; dvRender(); refresh(); };
dvCv.addEventListener("pointerdown", e => { if (!DV.on || e.button !== 0) return; dvCv.setPointerCapture(e.pointerId); DV.cur = { c: DV.color, p: [dvPt(e)] }; dvRender(); });
dvCv.addEventListener("pointermove", e => { if (DV.cur) { DV.cur.p.push(dvPt(e)); dvRender(); } });
dvCv.addEventListener("pointerup", () => { if (DV.cur) { DV.strokes.push(DV.cur); DV.cur = null; dvRender(); refresh(); } });
window.addEventListener("resize", dvRender);
// the shot = what the viewport shows now + the strokes, 1000 px wide JPEG; CAM() is saved with it so the AI can rebuild the view
function snapNote() {
  host.renderNow();   // same tick: the GL canvas is still readable
  const sc = Math.min(1, 1000 / renderer.domElement.width), W = Math.round(renderer.domElement.width * sc), H = Math.round(renderer.domElement.height * sc);
  const o = document.createElement("canvas"); o.width = W; o.height = H; const c = o.getContext("2d");
  c.fillStyle = "#23272e"; c.fillRect(0, 0, W, H); c.drawImage(renderer.domElement, 0, 0, W, H);
  dvDraw(c, W, H, W / viewer.clientWidth);
  c.font = "bold 14px sans-serif"; c.fillStyle = "#fff"; c.strokeStyle = "#000"; c.lineWidth = 3;
  const tag = P.clip.replace(/_/g, " ") + " · " + P.version + " · F" + frame + " · " + curCam; c.strokeText(tag, 10, 22); c.fillText(tag, 10, 22);
  return new Promise(r => o.toBlob(r, "image/jpeg", 0.85));
}
const camNow = () => ({ name: curCam, fov: CAM().fov, pos: CAM().position.toArray().map(v => +v.toFixed(3)), target: orbit.target.toArray().map(v => +v.toFixed(3)) });
let assetsNS;
async function getAssets() { if (assetsNS === undefined) { try { assetsNS = window.claude && claude.use ? await claude.use("assets") : null; } catch (e) { assetsNS = null; } } return assetsNS; }

async function saveKeysMode() {
  const fs = draftFrames(), text = $("text").value.trim(), cur = frame;
  stashDraft();
  if (fs.length) pushUndo();
  for (const f of fs) { goto(f, true); setKey(f, poseNow()); delete drafts[f]; }
  goto(cur, true);
  let msg = fs.length ? "Đã đặt key " + fs.map(f => "F" + f).join(", ") + "." : "";
  if ((text || DV.strokes.length) && db) {
    const body = { clip: P.clip, version: P.version, frame: cur, kind: "note", bones: {}, local: {}, text, status: "open", createdAt: new Date().toISOString() };
    if (DV.strokes.length) try {         // a shot only when something was drawn (user: không vẽ thì không cần gửi hình ảnh)
      const as = await getAssets();
      if (as) { const up = await as.upload(await snapNote()); body.img = { id: up.id, url: up.url }; body.cam = camNow(); }
      else msg += " Không có quyền tải ảnh nên ghi chú chưa kèm ảnh.";
    } catch (e) { console.error(e); msg += " Chưa tải được ảnh kèm."; }
    if (myId) body.author = myId;
    try { await db.collection("adjusts").add(body); adjs.push({ ...body }); $("text").value = ""; DV.strokes = []; dvRender(); msg += " Đã lưu ghi chú ở F" + cur + (body.img ? " (kèm ảnh)." : "."); }
    catch (e) { fail(e); return; }
  }
  $("p_status").textContent = msg.trim(); renderAdjs(); refresh();
}

// ---------------------------------------------------------------- boot
// ---------------------------------------------------------------- FBX export (animation-only FBX: skeleton + every frame, edits included)
// Every frame = original pose + saved adjustments + unsaved drafts, exactly what the viewport shows. The FBX world rule was
// calibrated against Blender's own FBX of the same rig (work/pose_lab/fbx/fbxexport.js, verified 0.00 cm on all bones).
async function exportFBX() {
  if (!model) return;
  const btn = $("expFbx"), say = t => $("p_status").textContent = t;
  stashDraft(); const cur = frame; stopPlay();
  const root = B["root"]; if (!root) { say("Model không có xương 'root', không xuất được FBX."); return; }
  const bones = [], list = [];
  (function walk(o, parent) { const i = bones.length; bones.push({ name: o.name, parent }); list.push(o); o.children.forEach(c => { if (c.isBone) walk(c, i); }); })(root, -1);
  const worlds = [];
  btn.disabled = true; say("Đang dựng FBX…");
  try {
    for (let f = 1; f <= (P.frames || 1); f++) {
      sampleAt(f);
      if (drafts[f]) for (const [n, v] of Object.entries(drafts[f])) { B[n].quaternion.copy(v.q); B[n].position.copy(v.p); }
      model.updateMatrixWorld(true);
      const w = new Float64Array(list.length * 16); list.forEach((o, i) => w.set(o.matrixWorld.elements, i * 16)); worlds.push(w);
    }
    const take = (P.clip + "_" + P.version).replace(/[^A-Za-z0-9_\-]/g, "_");
    const bytes = PoseLabFBX.build({ take, bones, worlds });
    const dl = window.claude && claude.use ? await claude.use("downloads").catch(() => null) : host.downloads;   // Studio: tải thẳng về máy
    if (!dl) { say("Trang này không cho tải file (mở trên claude.ai)."); return; }
    await dl.save({ filename: take + "_FBX.zip", data: PoseLabFBX.zip(take + ".fbx", bytes) });
    say("Đã xuất " + worlds.length + " frame → " + take + "_FBX.zip (giải nén ra .fbx).");
  } catch (e) {
    say(e && e.code === "declined" ? "Đã huỷ tải." : "Không xuất được FBX: " + (e && (e.message || e.code) || e));
  } finally { btn.disabled = false; goto(cur, true); }
}
$("expFbx").onclick = exportFBX;



// fall graph (CoM height: clip vs rigid physics) and the "falls like physics" ghost
let fallGhostOn = false;
const fallAt = f => (BAL && BAL.falls || []).find(fl => f >= fl.from && f <= fl.to + 6) || null;
function drawFallGraph() {
  const cv = $("fallGraph"); if (!cv) return; const fl = fallAt(frame) || (BAL && BAL.falls && BAL.falls[0]);
  cv.hidden = !fl; if (!fl) return;
  const g = cv.getContext("2d"), W = cv.width, H = cv.height, fps = P.fps || 30; g.clearRect(0, 0, W, H);
  const f0 = fl.from, f1 = Math.max(fl.to, f0 + Math.ceil(fl.refF || 0)) + 4, rows = BAL.rows.filter(r => r.f >= f0 && r.f <= f1);
  const ys = [...rows.map(r => r.com.y), ...fl.curve.map(c => c.y)], top = Math.max(...ys) * 1.05, X = f => 10 + (f - f0) / Math.max(1, f1 - f0) * (W - 20), Y = y => H - 20 - y / top * (H - 34);
  g.fillStyle = "#1fa37a33"; if (frame >= f0 && frame <= f1) g.fillRect(X(frame) - 3, 0, 6, H);
  g.strokeStyle = "#8b93a1"; g.lineWidth = 2; g.setLineDash([8, 6]); g.beginPath(); fl.curve.forEach((c, k) => { const x = X(f0 + k), y = Y(c.y); k ? g.lineTo(x, y) : g.moveTo(x, y); }); g.stroke(); g.setLineDash([]);
  g.strokeStyle = css("--accent"); g.lineWidth = 3.5; g.beginPath(); rows.forEach((r, k) => { const x = X(r.f), y = Y(r.com.y); k ? g.lineTo(x, y) : g.moveTo(x, y); }); g.stroke();
  g.fillStyle = css("--muted"); g.font = "20px " + css("--font-num"); g.fillText("F" + f0, 10, H - 2); g.fillText("F" + f1, W - 60, H - 2); g.fillText("cao trọng tâm · xanh: anim · nét đứt: vật lý", 12, 22);
}
function applyFallGhost(f) {           // ghost = the fall's first pose, toppled rigidly (or dropped) as physics would
  if (!ghost) return; ghost.position.set(0, 0, 0); ghost.quaternion.set(0, 0, 0, 1);
  const fl = fallGhostOn && fallAt(f); if (!fl) return;
  const r0 = BAL.rows.find(r => r.f === fl.from); if (!r0 || !r0.pose) return;
  for (const [n, v] of Object.entries(r0.pose)) if (gB[n]) { gB[n].quaternion.fromArray(v, 0); gB[n].position.fromArray(v, 4); }
  const k = Math.min(fl.curve.length - 1, Math.max(0, f - fl.from)), c = fl.curve[k];
  if (fl.kind === "topple") {
    const R = new Q().setFromAxisAngle(new V3(0, 1, 0).cross(fl.dir).normalize(), c.th - fl.th0);   // tips toward the fall direction
    ghost.quaternion.copy(R); ghost.position.copy(fl.pivot.clone().sub(fl.pivot.clone().applyQuaternion(R)));
  } else ghost.position.set(0, c.y - r0.com.y, 0);
  ghost.updateMatrixWorld(true);
}
$("fallGhost").onclick = () => { fallGhostOn = !fallGhostOn; $("fallGhost").classList.toggle("primary", fallGhostOn); if (fallGhostOn && ghost) { ghost.visible = true; $("tGhost").classList.add("on"); } goto(frame, true); };
// ---------------------------------------------------------------- balance panel + floor drawing
const BAL_KIND = { fall: "cú ngã", lean: "nghiêng quá, cần bước hoặc chống", momentum: "đà quá mạnh, cần bước theo hoặc vung chậm lại", missed: "bước hụt (chân đặt xuống không đỡ được)", air: "rời đất nhưng rơi không đúng trọng lực" };
let balVizOn = false, balViz = null;
const balRow = f => BAL && BAL.rows.find(r => r.f === cyc(f));
function renderBal() {
  const box = $("balIssues"); if (!box) return; box.innerHTML = "";
  $("balViz").classList.toggle("primary", balVizOn);
  const pm = balPropPct(); $("balProp").value = pm; $("balPropOut").textContent = pm + " %";
  $("balProp").disabled = !(BODY && BODY.props.length);
  if (!BAL) { $("balInfo").textContent = ""; return; }
  for (const it of BAL.issues) {
    const b = mkEl("button");
    if (it.kind === "fall") {
      const txt = (it.fk === "collapse" ? "sụp xuống" : "đổ người") + " chạm đất sau " + it.animF + " frame, vật lý " + it.refF + " frame";
      b.append(mkEl("span", "", "F" + it.from + "–F" + it.to + " " + txt + (Math.abs(it.d) >= FALL_TOL_F ? (it.d > 0 ? ": chậm hơn " : ": nhanh hơn ") : "")),
        mkEl("b", "", (Math.abs(it.d) >= FALL_TOL_F ? Math.abs(it.d).toFixed(0) + " frame" : "") + (it.easeOut ? (Math.abs(it.d) >= FALL_TOL_F ? ", " : "") + "chậm dần trước khi chạm đất" : "")));
    } else b.append(mkEl("span", "", "F" + it.from + (it.to > it.from ? "–F" + it.to : "") + " " + BAL_KIND[it.kind] + (it.cm != null ? ", ra ngoài " : ", gia tốc rơi = ")), mkEl("b", "", it.cm != null ? it.cm + " cm" : Math.round(it.ratio * 100) + " % g"));
    b.onclick = () => { stopPlay(); goto(it.at); }; box.append(b);
  }
  for (const fl of BAL.falls || []) if (!BAL.issues.some(i => i.kind === "fall" && i.from === fl.from)) {
    const b = mkEl("button"); b.append(mkEl("span", "", "F" + fl.from + "–F" + fl.to + " " + (fl.kind === "collapse" ? "sụp xuống" : "đổ người") + " chạm đất sau " + fl.animF + " frame, vật lý " + fl.refF + " frame: khớp"));
    b.onclick = () => { stopPlay(); goto(fl.from); }; box.append(b);
  }
  drawFallGraph();
  const steps = BAL.rows.filter(r => r.state === "step").length, lanes = CT.L.size + CT.R.size > 0;
  $("balInfo").textContent = (BAL.issues.length ? BAL.issues.length + " chỗ cần xem" : "Không chỗ nào mất cân bằng") + (steps ? " · " + steps + " frame trọng tâm ra ngoài chân nhưng bước kịp" : "") +
    ". Chạm đất theo " + (lanes ? "dải chạm đất đã tô" : "độ cao bàn chân (dưới " + BAL_GROUND_CM + " cm)") + ", vũ khí chống đất cũng là điểm đỡ.";
}
function drawBalViz() {
  if (balViz) { scene.remove(balViz); balViz.traverse(o => { if (o.geometry) o.geometry.dispose(); if (o.material) o.material.dispose(); }); balViz = null; }
  if (!balVizOn || !model || !keysMode() || !BAL) return;
  const r = balRow(frame); if (!r) return;
  const col = r.state === "bad" ? 0xff4b3e : r.state === "step" ? 0xf2b134 : 0x4cc287, y = 0.006;
  balViz = new THREE.Group();
  if (r.sup.length >= 3) {
    const sh = new THREE.Shape(r.sup.map(p => new THREE.Vector2(p[0], -p[1])));
    const m = new THREE.Mesh(new THREE.ShapeGeometry(sh), new THREE.MeshBasicMaterial({ color: col, transparent: true, opacity: 0.28, depthWrite: false, side: THREE.DoubleSide }));
    m.rotation.x = -Math.PI / 2; m.position.y = y; balViz.add(m);
  }
  const dot = new THREE.Mesh(new THREE.CircleGeometry(0.05, 20), new THREE.MeshBasicMaterial({ color: col, depthTest: false }));
  dot.rotation.x = -Math.PI / 2; dot.position.set(r.com.x, y + 0.002, r.com.z); dot.renderOrder = 4; balViz.add(dot);
  const line = new THREE.Line(new THREE.BufferGeometry().setFromPoints([new V3(r.com.x, y + 0.004, r.com.z), new V3(r.cap[0], y + 0.004, r.cap[1])]), new THREE.LineBasicMaterial({ color: col, depthTest: false }));
  line.renderOrder = 4; balViz.add(line);
  const tip = new THREE.Mesh(new THREE.RingGeometry(0.035, 0.05, 20), new THREE.MeshBasicMaterial({ color: col, depthTest: false, side: THREE.DoubleSide }));
  tip.rotation.x = -Math.PI / 2; tip.position.set(r.cap[0], y + 0.004, r.cap[1]); tip.renderOrder = 4; balViz.add(tip);
  const up = new THREE.Line(new THREE.BufferGeometry().setFromPoints([new V3(r.com.x, y, r.com.z), r.com.clone()]), new THREE.LineDashedMaterial({ color: col, dashSize: 0.04, gapSize: 0.03, depthTest: false }));
  up.computeLineDistances(); up.renderOrder = 4; balViz.add(up);
  scene.add(balViz);
}
$("balViz").onclick = () => { balVizOn = !balVizOn; drawBalViz(); renderBal(); };
$("balProp").oninput = () => {
  const v = +$("balProp").value; $("balPropOut").textContent = v + " %";
  ANIM.phys.propMass = v; animAt = new Date().toISOString(); animDirty = true; scheduleFlush(); bodyChanged();
};
$("laneBl").addEventListener("click", e => { stopPlay(); goto(frameAtX(e.clientX)); });
// "Đưa trọng tâm vào chân": move the hips sideways (feet locked by leg IK, props carried with the body) until the CoM is
// 3 cm inside the support of this frame, then key it. A few Newton steps: moving the hips moves only part of the mass.
$("balFix").onclick = () => {
  if (!model || !keysMode()) return;
  stopPlay(); if (!BODY) BODY = buildBody();
  if (editedList().length) { $("p_status").textContent = "Đặt key hoặc bỏ chỉnh sửa đang dở ở frame này trước."; return; }
  const W0 = bodyWorld(BODY), r0 = balFrame(W0, frame);
  if (r0.sup.length < 3) { $("p_status").textContent = "Frame này không có vùng đỡ (không chân nào chạm đất): không dời hông được."; return; }
  const inner = q => polyMargin(r0.sup, q) >= 0.03;
  if (inner([r0.com.x, r0.com.z])) { $("p_status").textContent = "Trọng tâm ở F" + cyc(frame) + " đã nằm trong vùng chân."; return; }
  pushUndo(); captureFeet();
  const cen = r0.sup.reduce((a, p) => [a[0] + p[0] / r0.sup.length, a[1] + p[1] / r0.sup.length], [0, 0]);
  const props = BODY.props.filter(p => B[p]), ed = edited; edited = new Set();
  let moved = new V3();
  for (let it = 0; it < 6; it++) {
    const r = balFrame(bodyWorld(BODY), frame); if (polyMargin(r0.sup, [r.com.x, r.com.z]) >= 0.03) break;
    // target: the point 3 cm inside the support on the line from the CoM to the support's centre
    let lo = 0, hi = 1; const c = [r.com.x, r.com.z];
    for (let k = 0; k < 24; k++) { const m = (lo + hi) / 2, q = [c[0] + (cen[0] - c[0]) * m, c[1] + (cen[1] - c[1]) * m]; if (inner(q)) hi = m; else lo = m; }
    const tx = c[0] + (cen[0] - c[0]) * hi, tz = c[1] + (cen[1] - c[1]) * hi, d = new V3(tx - c[0], 0, tz - c[1]);
    const root = B.Root_M; root.parent.updateMatrixWorld(true);
    const step = d.clone().multiplyScalar(1.25);                    // the legs stay: overshoot the hips a little
    root.position.copy(root.parent.worldToLocal(wp(root).add(step))); model.updateMatrixWorld(true);
    for (const p of props) { B[p].parent.updateMatrixWorld(true); B[p].position.copy(B[p].parent.worldToLocal(wp(B[p]).add(step))); }
    model.updateMatrixWorld(true); solveLeg("L"); solveLeg("R"); model.updateMatrixWorld(true); moved.add(step);
  }
  for (const n of Object.keys(B)) edited.add(n);
  setKey(frame, poseNow()); edited = new Set(); rebase(); captureFeet(); refresh();
  const r1 = balFrame(bodyWorld(BODY), frame);
  $("p_status").textContent = "Đã dời hông " + Math.round(moved.length() * 100) + " cm và đặt key F" + cyc(frame) + ": trọng tâm " +
    (polyMargin(r0.sup, [r1.com.x, r1.com.z]) >= 0 ? "đã vào" : "vẫn chưa vào hẳn") + " vùng chân. Ctrl+Z để bỏ.";
};
// ---------------------------------------------------------------- body collision panel
let bodyT = 0;
function bodyChanged(rebuild) {        // re-scan a moment after the animation / shapes changed (not while dragging)
  if (rebuild) BODY = null; bodyDirty = true; clearTimeout(bodyT);
  bodyT = setTimeout(() => { if (gizmo.dragging || playing) { bodyChanged(); return; } scanBody(); renderBody(); renderBal(); renderLanes(); drawBodyViz(); drawBalViz(); }, 250);
}
function issueRanges() {               // [{a, b, from, to, cm, at}] ranges of consecutive frames per pair
  if (!BODYSCAN) return [];
  const runs = {}, out = [];
  for (let f = 1; f <= NFR(); f++) for (const it of BODYSCAN.issues[f] || []) {
    const k = it.a + "~" + it.b, r = runs[k];
    if (r && r.to === f - 1) { r.to = f; if (it.cm > r.cm) { r.cm = it.cm; r.at = f; } }
    else { if (r) out.push(r); runs[k] = { a: it.a, b: it.b, from: f, to: f, cm: it.cm, at: f }; }
  }
  return out.concat(Object.values(runs)).sort((x, y) => x.from - y.from);
}
function renderBody() {
  const box = $("bodyIssues"); if (!box) return; box.innerHTML = "";
  $("bodyViz").classList.toggle("primary", bodyVizOn);
  const rs = issueRanges();
  for (const r of rs) {
    const b = mkEl("button"); b.append(mkEl("span", "", "F" + r.from + (r.to > r.from ? "–F" + r.to : "") + " " + bodyName(r.a) + (r.b === "floor" ? " lún sàn" : " vào " + bodyName(r.b)) + ", sâu "), mkEl("b", "", r.cm + " cm"));
    b.title = "Tới F" + r.at + " (sâu nhất)"; b.onclick = () => { stopPlay(); goto(r.at); }; box.append(b);
  }
  $("bodyInfo").textContent = !BODYSCAN ? "" : (rs.length ? rs.length + " chỗ lẹm sâu hơn lúc nghỉ quá " + BODY_TH_CM + " cm" : "Không chỗ nào lẹm sâu hơn lúc nghỉ quá " + BODY_TH_CM + " cm") +
    " (quét " + NFR() + " frame, " + Math.round(BODYSCAN.ms) + " ms). Chạm cố ý như tay nắm vũ khí không tính.";
  const seg = sel && BODY && BODY.caps[sel] ? sel : null; $("bodyRBox").hidden = !seg;
  if (seg) { const r = Math.round(BODY.caps[seg].r / CM_W); $("bodyRName").textContent = "Lõi " + bodyName(seg); $("bodyR").value = r; $("bodyROut").textContent = r + " cm"; }
}
$("bodyViz").onclick = () => { bodyVizOn = !bodyVizOn; drawBodyViz(); renderBody(); };
$("bodyRebuild").onclick = () => { bodyChanged(true); };
$("bodyR").oninput = () => {
  if (!sel || !BODY || !BODY.caps[sel]) return;
  const v = +$("bodyR").value; $("bodyROut").textContent = v + " cm";
  ANIM.phys.bodyR = { ...(ANIM.phys.bodyR || {}), [sel]: v }; BODY.caps[sel].r = v * CM_W;
  animAt = new Date().toISOString(); animDirty = true; scheduleFlush(); physDirty = true; bodyChanged(true);
};
for (const i of [$("laneX")]) i.addEventListener("click", e => { const f = frameAtX(e.clientX); stopPlay(); goto(f); });
// ---------------------------------------------------------------- impacts panel, picking, arrows (p5 step 1)
let impPick = false, impAim = false, impSelI = -1, impViz = null;
const impSegName = k => bodyName(k);
function impPickAt(x, y) {               // nearest surface point to the click -> a new impact on this frame
  // the surface points are sparse (Gaygor's chest: 182 points, 28+ px apart on screen): a fixed 14 px radius missed clicks
  // right on the chest (user "không thêm được tác động"). Now: the closest point within 45 px, and among the points about
  // as close (+12 px) the one nearest the CAM() (a click on the front of the body, not the back)
  if (!BODY) BODY = buildBody();
  const W = bodyWorld(BODY), cand = []; let d0 = 1e9;
  for (const [k, sh] of Object.entries(W.shells)) {
    if (!BODY.caps[k] && !BODY.props.includes(k)) continue;
    sh.forEach((p, i) => { const s = toScreen(p); if (!s.front) return; const d = Math.hypot(s.x - x, s.y - y); if (d > 45) return; cand.push({ k, i, d, z: CAM().position.distanceTo(p) }); if (d < d0) d0 = d; });
  }
  let best = null, bz = 1e9; for (const c of cand) if (c.d <= d0 + 12 && c.z < bz) { bz = c.z; best = c; }
  if (!best) return false;
  const cfg = ANIM.phys; cfg.impacts = cfg.impacts || [];
  const q = BODY.shells[best.k][best.i];
  cfg.impacts.push({ f: frame, seg: best.k, p: [+q.x.toFixed(5), +q.y.toFixed(5), +q.z.toFixed(5)], level: "medium", dirMode: "normal", mul: 1 });
  cfg.on = true; impSelI = cfg.impacts.length - 1; physChanged(true);
  $("p_status").textContent = "Đã đặt tác động ở " + impSegName(best.k) + ", F" + frame + ". Chọn mức lực và hướng trong bảng Tác động.";
  return true;
}
function impAimAt(x, y, done) {          // the force comes FROM the clicked / dragged screen point toward the hit point
  const i = (ANIM.phys.impacts || [])[impSelI]; if (!i || !B[i.seg]) return;
  const { x: P0 } = impPointW(i), r = canvas.getBoundingClientRect(), rc = new THREE.Raycaster();
  rc.setFromCamera(new THREE.Vector2(x / r.width * 2 - 1, 1 - y / r.height * 2), CAM());
  const n = CAM().getWorldDirection(new V3()), pl = new THREE.Plane().setFromNormalAndCoplanarPoint(n, P0), tip = new V3();
  if (!rc.ray.intersectPlane(pl, tip)) return;
  const d = P0.clone().sub(tip); if (d.length() < 0.02) return;
  i.dir = d.normalize().toArray().map(v => +v.toFixed(4)); i.dirMode = "drag";
  if (done) { impAim = false; $("impAim").classList.remove("primary"); physChanged(true); $("p_status").textContent = "Đã đặt hướng lực cho tác động F" + i.f + "."; } else drawImpacts();
}
function impAt(f) { return (ANIM.phys.impacts || []).findIndex(i => f >= i.f && f < i.f + impDur(i)); }
function drawImpacts() {
  if (impViz) { overlay.remove(impViz); impViz.traverse(o => { if (o.geometry) o.geometry.dispose(); if (o.material) o.material.dispose(); }); impViz = null; }
  if (!model || !keysMode() || !ANIM.phys) return;
  const L = ANIM.phys.impacts || []; if (!L.length) return;
  if (!BODY) BODY = buildBody();
  impViz = new THREE.Group(); impViz.renderOrder = 12;
  L.forEach((i, k) => {
    if (!B[i.seg] || (k !== impSelI && (frame < i.f - 2 || frame > i.f + impDur(i) + 3))) return;
    const { x, d } = impPointW(i), len = Math.min(1.2, 0.45 + 0.15 * impDV(i)), col = k === impSelI ? 0xff6b3d : 0xffa36b;
    const mat = new THREE.MeshBasicMaterial({ color: col, depthTest: false, transparent: true, opacity: 0.95 }), hl = 0.14;
    const shaft = new THREE.Mesh(new THREE.CylinderGeometry(0.018, 0.018, len - hl, 10), mat), head = new THREE.Mesh(new THREE.ConeGeometry(0.055, hl, 14), mat.clone());
    const ar = new THREE.Group(); shaft.position.y = (len - hl) / 2; head.position.y = len - hl / 2; ar.add(shaft, head);   // +Y = the push
    ar.position.copy(x.clone().addScaledVector(d, -len)); ar.quaternion.setFromUnitVectors(new V3(0, 1, 0), d);
    ar.traverse(o => { o.renderOrder = 12; }); impViz.add(ar);
    const dot = new THREE.Mesh(new THREE.SphereGeometry(0.02, 10, 8), new THREE.MeshBasicMaterial({ color: col, depthTest: false })); dot.position.copy(x); dot.renderOrder = 12; impViz.add(dot);
  });
  const I = PHYS && PHYS.imp;
  const ring = (p, col, dash) => { const m = new THREE.Mesh(new THREE.RingGeometry(0.1, dash ? 0.12 : 0.14, 32), new THREE.MeshBasicMaterial({ color: col, depthTest: false, transparent: true, opacity: dash ? 0.6 : 0.9, side: THREE.DoubleSide }));
    m.rotation.x = -Math.PI / 2; m.position.set(p[0], 0.004, p[2]); m.renderOrder = 12; impViz.add(m); };
  if (I) {
    for (const s of I.steps) if (frame >= s.f0 - 2 && frame <= s.f1 + 6) ring(s.to, s.s === "L" ? 0x3fb6ff : 0xb07cff);
    for (const s of I.need) if (frame >= s.f - 2 && frame <= s.f + 12) ring(s.to, 0xff4b3e, true);
  }
  overlay.add(impViz);
}
function renderImpacts() {
  const box = $("impList"); if (!box) return; box.innerHTML = "";
  const cfg = ANIM.phys, L = cfg.impacts || [];
  $("impStep").textContent = "Tự bước: " + (cfg.autoStep !== false ? "bật" : "tắt"); $("impStep").classList.toggle("primary", cfg.autoStep !== false);
  $("impAdd").classList.toggle("primary", impPick); $("impAim").classList.toggle("primary", impAim); $("impAim").disabled = !L[impSelI];
  if (!L.length) box.append(mkEl("div", "pinfo", P.loop ? "Tác động chỉ dùng cho clip không lặp." : "Bấm \"+ Tác động\" rồi bấm lên người ở frame trúng đòn."));
  L.forEach((i, k) => {
    const row = mkEl("div", "ppart" + (k === impSelI ? " on" : "")), ph = mkEl("div", "ph");
    const nm = mkEl("b", "", "F" + i.f + " · " + impSegName(i.seg)); nm.title = "Tới frame trúng đòn";
    nm.onclick = () => { impSelI = k; stopPlay(); goto(i.f); renderImpacts(); drawImpacts(); };
    const lv = mkEl("select"); lv.title = "Mức lực (tốc độ trọng tâm bị đẩy)";
    for (const [key, v] of Object.entries(IMP_LEVEL)) { const o = mkEl("option", "", v.label); o.value = key; lv.append(o); }
    const cu = mkEl("option", "", "Tự chỉnh"); cu.value = ""; lv.append(cu); lv.value = IMP_LEVEL[i.level] ? i.level : "";
    lv.onchange = () => { if (!lv.value) return; i.level = lv.value; delete i.dv; delete i.dur; impSelI = k; physChanged(true); };
    const dr = mkEl("select"); dr.title = "Lực đến từ đâu";
    for (const [key, v] of Object.entries(IMP_DIRS)) { const o = mkEl("option", "", v); o.value = key; dr.append(o); }
    dr.value = i.dirMode || "normal";
    dr.onchange = () => { impSelI = k; if (dr.value === "drag") { impAim = true; renderImpacts(); $("p_status").textContent = "Bấm (hoặc kéo) trên màn hình ở chỗ lực đến, mũi tên chỉ vào điểm trúng."; return; }
      i.dirMode = dr.value; const pd = impDirPreset(dr.value); if (pd) i.dir = pd.toArray(); else delete i.dir; physChanged(true); };
    const rm = mkEl("button", "pX", "×"); rm.title = "Bỏ tác động này";
    rm.onclick = () => {     // by identity, or by frame + part when the settings were replaced by a db copy since this row was drawn
      const A = ANIM.phys.impacts || [], j = A.indexOf(i); if (j >= 0) A.splice(j, 1); else ANIM.phys.impacts = A.filter(x => x.f !== i.f || x.seg !== i.seg); impSelI = -1; physChanged(true); };
    ph.append(nm, lv, dr, rm); row.append(ph);
    for (const [key, lab, lo, hi, st, unit, get] of [["f", "Frame", 1, NFR(), 1, "", () => i.f], ["dv", "Đẩy", 0.1, 8, 0.1, " m/s", () => impDV(i) / (i.mul ?? 1)],
      ["dur", "Thời gian", 1, 8, 1, " F", () => impDur(i)], ["mul", "Phóng đại", 0.25, 3, 0.05, "×", () => i.mul ?? 1]]) {
      const l = mkEl("label", "psl"), r = mkEl("input"), out = mkEl("output"); r.type = "range"; r.min = lo; r.max = hi; r.step = st; r.value = get();
      const fmt = v => (st < 1 ? (+v).toFixed(st < 0.1 ? 2 : 1) : v) + unit; out.textContent = fmt(get());
      r.oninput = () => { out.textContent = fmt(r.value); impSelI = k;
        if (key === "f") i.f = +r.value; else if (key === "mul") i.mul = +r.value;
        else { if (IMP_LEVEL[i.level]) { i.dv = IMP_LEVEL[i.level].dv; i.dur = IMP_LEVEL[i.level].dur; } i.level = ""; i[key] = +r.value; lv.value = ""; }
        physChanged(false); };
      if (key === "f") r.onchange = () => { stopPlay(); goto(i.f); };
      l.append(mkEl("span", "", lab), r, out); row.append(l);
    }
    box.append(row);
  });
  impInfo();
}
function impInfo() {
  const el = $("impInfo"); if (!el) return; el.innerHTML = ""; const L = (ANIM.phys && ANIM.phys.impacts) || []; if (!L.length || !BODY) return;
  const add = (t, b) => { const sp = mkEl("span", "", t); if (b) sp.append(mkEl("b", "", b)); el.append(sp); };
  const { M } = impMass(); add("Gaygor nặng khoảng ", Math.round(M) + " kg"); add(" (lõi thân, có vũ khí). ");
  const i = L[impSelI] || L[0]; if (i) { const J = impDV(i) * M; add("Tác động F" + i.f + ": trọng tâm bị đẩy ", impDV(i).toFixed(1) + " m/s"); add(" ≈ " + Math.round(J) + " N·s ngoài đời (đấm người ~20, đạn ~3, xe 1,5 t ở 30 km/h ~5800). "); }
  const I = PHYS && PHYS.imp; if (!I || !physOn()) { if (!physOn()) add("Bật vật lý để xem kết quả."); return; }
  for (const s of I.steps) add((s.s === "L" ? "Bước chân trái" : "Bước chân phải") + " F" + s.f0 + "–F" + s.f1 + ", ", s.cm + " cm"), add(". ");
  for (const s of I.need) add("Cần bước F" + s.f + " (" + (s.s === "L" ? "chân trái" : "chân phải") + ", trọng tâm ra ngoài " + s.cm + " cm): ", "vòng đỏ là chỗ đặt chân"), add(". ");
  if (I.fell != null) add("Bước " + IMP_STEP.max + " lần vẫn không giữ được: ", "ngã từ F" + I.fell), add(" (bước 2 sẽ dùng ragdoll từ đây). ");
  if (!I.steps.length && !I.need.length && I.fell == null) add("Không cần bước. ");
}
$("impAdd").onclick = () => {
  if (P.loop) { $("p_status").textContent = "Tác động chỉ dùng cho clip không lặp."; return; }
  impPick = !impPick; impAim = false; renderImpacts(); if (impPick) $("p_status").textContent = "Bấm lên người ở chỗ trúng đòn (F" + frame + ").";
};
$("impAim").onclick = () => { impAim = !impAim; impPick = false; renderImpacts(); if (impAim) $("p_status").textContent = "Bấm (hoặc kéo) trên màn hình ở chỗ lực đến, mũi tên chỉ vào điểm trúng."; };
$("impStep").onclick = () => { ANIM.phys.autoStep = ANIM.phys.autoStep === false; physChanged(true); };
$("laneI").addEventListener("click", e => { const f = frameAtX(e.clientX), k = impAt(f); stopPlay(); if (k >= 0) impSelI = k; goto(f); renderImpacts(); });
// ---------------------------------------------------------------- ragdoll panel: on / from, strength curve, groups, release, length, limit view
let ragDrag = null, ragLimOn = false, ragLimViz = null;
const ragCfg = () => ((ANIM.phys ||= physDefault()).rag ||= {   // non-keys versions (polish bakes) have no phys: "Xem ngay" broke on reading rag
   on: false, from: null, pts: [], groups: {}, release: null, len: 0 });
function ragLen() {                     // clip length: the version's own, or longer when the ragdoll needs time to settle
  if (!P || !keysMode()) return; if (P.frames0 == null) P.frames0 = P.frames;
  const R = ANIM.phys && ANIM.phys.rag, want = Math.max(P.frames0, R && R.on && R.len ? R.len : 0);
  if (P.frames !== want) { P.frames = want; buildStrip(); physDirty = true; if (frame > want) goto(want, true); renderStrip(); }
}
function ragDefaultPts(from) { return [[from, 100], [from + 6, 20], [from + 20, 0]]; }
function renderRag() {
  const box = $("ragBox"); if (!box) return; const R = ragCfg(), on = !!R.on;
  $("ragOn").textContent = "Ragdoll: " + (on ? "bật" : "tắt"); $("ragOn").classList.toggle("primary", on); $("ragOn").disabled = !!P.loop;
  $("ragFrom").value = R.from || frame; $("ragFrom").max = NFR();
  $("ragRelease").textContent = R.release != null ? "Buông chùy từ F" + R.release + " (bấm để bỏ)" : "Buông chùy ở F đang xem";
  $("ragRelease").disabled = !(BODY ? BODY.props.length : (B.Weapon || B[GUN]));
  { const g = R.goal && R.goal.on; $("ragGoal").textContent = "Về đích: " + (g ? "bật, F" + ragGoalFrame() : "tắt"); $("ragGoal").classList.toggle("primary", !!g); $("ragGoal").disabled = !on; $("ragGoalFind").disabled = !on;
    $("ragMatchBox").hidden = !g; $("ragGoalRoot").hidden = !g; $("ragGoalRoot").textContent = ragGoalPoseOnly() ? "Đích: chỉ dáng" : "Đích: dáng + vị trí"; const m = R.goal && R.goal.match != null ? R.goal.match : 0.5; $("ragMatch").value = m; $("ragMatchOut").textContent = Math.round(m * 100) + " %"; }
  const gb = $("ragGroups"); gb.innerHTML = "";
  for (const [g, lab] of Object.entries(RAG_GROUP_LABEL)) {
    const l = mkEl("label", "psl"), r = mkEl("input"), o = mkEl("output"), v = ragGroupF(R.groups || {}, g);
    r.type = "range"; r.min = 0; r.max = 1.5; r.step = 0.05; r.value = v; o.textContent = Math.round(v * 100) + " %";
    r.oninput = () => { R.groups = { ...(R.groups || {}), [g]: +r.value }; o.textContent = Math.round(+r.value * 100) + " %"; physChanged(false); };
    l.append(mkEl("span", "", lab), r, o); gb.append(l);
  }
  $("ragLim").classList.toggle("primary", ragLimOn);
  drawRagGraph(); ragInfo();
}
function ragInfo() {
  const el = $("ragInfo"); if (!el) return; el.innerHTML = ""; const R = ragCfg();
  const add = (t, b) => { const sp = mkEl("span", "", t); if (b) sp.append(mkEl("b", "", b)); el.append(sp); };
  if (P.loop) { add("Ragdoll chỉ dùng cho clip không lặp."); return; }
  if (!R.on) { add("Bật ragdoll: từ frame chọn, cơ thể thành các khối nối khớp, mất sức theo đường \"Sức\" rồi đổ, đập sàn và lắng. Lực ở frame đó trở đi (Tác động) đẩy ragdoll."); return; }
  const G = PHYS && PHYS.rag; if (!G || physDirty) return;
  add("Ragdoll từ F" + G.from + ". ");
  if (G.needStep != null) add("Còn sức nhưng chân không giữ nổi từ ", "F" + G.needStep), add(" (cần bước). ");
  if (G.restAt != null) add("Nằm yên từ ", "F" + G.restAt), add(". ");
  else { add("Chưa nằm yên ở cuối clip. "); const b = mkEl("button", "btn", "Kéo dài clip tới lúc nằm yên"); b.onclick = ragExtend; el.append(b); }
  add(" Lún sàn tối đa " + G.pen + " cm, vượt giới hạn khớp tối đa " + G.lim + "°" + (G.lim > 2 && G.limAt ? " (" + bodyName(G.limAt.split("/")[0]) + ")" : "") + ". ");
  if (R.len && R.len > (P.frames0 || 0)) add("Clip dài thêm " + (R.len - P.frames0) + " frame (giữ key cuối). ");
  if (G.goal) { const g = G.goal, far = (!g.poseOnly && g.dxz > 30) || g.dang > 30;
    add(" Về đích F" + g.E + ": " + (g.land != null ? "chạm sàn F" + g.land + ", " : "chưa chạm sàn, ") + "trước khi trộn hông lệch ", g.dpos + " cm"); add(", thân xoay lệch ", g.dang + "°");
    add(", tay chân lệch tới " + g.limb + "° (" + bodyName(g.limbAt) + ")" + (g.dprop ? ", vũ khí lệch " + g.dprop + "°" : "") + "; trộn " + Math.round((ANIM.phys.rag.goal.match ?? 0.5) * 100) + " % về key cuối F" + g.blendFrom + "–F" + (g.blendTo || g.E) + " trong lúc lắng" + (g.lift ? ", nâng khỏi sàn " + g.lift + " cm" : "") + ". ");
    if (far) add("Lệch lớn: bấm \"Tìm cú đổ\". Nếu vẫn lệch, pose cuối khó đạt bằng một cú ngã (quá xa hoặc sai hướng ngã), nên sửa key cuối hoặc thêm key giữa. "); }
}
// ---- "Về đích" (user 2026-10-26: two keys, Idle and a lying pose; the physics must end exactly on the user's last key).
// 1 a push of the whole body at the ragdoll start (vx, vz, yaw) found by "Tìm cú đổ" so the body lands where / facing as in
//   the last key; 2 after landing the muscles drive toward the last key's joint turns (ragStage); 3 what is left is blended
//   onto the last key over the last frames, the body kept above the floor (ragGoalFinish). docs/poselab_physics_p5_impact.md#17
const ragGoalOn = () => ragOn() && !!(ANIM.phys.rag.goal && ANIM.phys.rag.goal.on);
function ragGoalFrame() {
  const R = ANIM.phys.rag, GL = R.goal || {};
  const last = keysMode() && KEYS.size ? Math.max(...KEYS.keys()) : NFR();
  return Math.max((R.from || 2) + 1, Math.min(NFR(), GL.f || last));
}
function ragGoalFinish(G, out, last) {
  const E = ragGoalFrame(), GL = ANIM.phys.rag.goal; if (!out[E]) return;
  const put = o => { for (const n of BN) if (o[n]) { B[n].quaternion.fromArray(o[n], 0); B[n].position.fromArray(o[n], 4); } model.updateMatrixWorld(true); };
  put(out[E]); const rQ = wq(B.Root_M), hP = wp(B.Root_M), loc = {}; for (const n of BN) loc[n] = B[n].quaternion.clone();
  const pq = {}; for (const k of BODY.props) if (B[k]) pq[k] = wq(B[k]);
  evalPose(E); model.updateMatrixWorld(true); const key = {}; for (const n of BN) key[n] = packBone(B[n].quaternion, B[n].position);
  const kH = wp(B.Root_M), kQ = wq(B.Root_M); let limb = 0, limbAt = "", dprop = 0;
  for (const k of Object.keys(pq)) dprop = Math.max(dprop, THREE.MathUtils.radToDeg(pq[k].angleTo(wq(B[k]))));   // a released prop: how turned vs the key
  for (const j of G.RG.joints) { const a = THREE.MathUtils.radToDeg(loc[j.k].angleTo(B[j.k].quaternion)); if (a > limb) { limb = a; limbAt = j.k; } }
  G.goal = { E, dpos: +(hP.distanceTo(kH) / CM_W).toFixed(1), dxz: +(Math.hypot(hP.x - kH.x, hP.z - kH.z) / CM_W).toFixed(1),
    dang: +THREE.MathUtils.radToDeg(rQ.angleTo(kQ)).toFixed(1), limb: +limb.toFixed(1), limbAt, dprop: +dprop.toFixed(1), land: G.landAt ?? null,
    dx: kH.x - hP.x, dz: kH.z - hP.z, dyaw: (() => { const d = kQ.clone().multiply(rQ.clone().invert()); let y = 2 * Math.atan2(d.y, d.w); while (y > Math.PI) y -= 2 * Math.PI; while (y < -Math.PI) y += 2 * Math.PI; return y; })() };   // signed misses (m, rad) for the search
  // the residual goes in WHILE the body still settles (landing + 4 .. resting), then the last key holds: blended over the
  // last 10 frames it moved a body that had lain still for 20 frames (4-7 deg/F at F64-70, user "thiếu tự nhiên")
  const rest = (ragSummary(G) || {}).restAt, L0 = (G.landAt ?? G.from) + 4;
  let b1 = Math.min(E, Math.max(rest ?? E, L0 + (GL.blend ?? 10))), b0 = Math.max(G.from + 1, Math.min(L0, b1 - 6));
  // "chỉ dáng" (default, user 2026-10-26: with an impact the body landed past the last key and the blend dragged the whole
  // body back): the hips keep the physics place and turn and a released prop stays where it fell; only the joints blend
  // toward the last key. "dáng + vị trí" = the old behaviour (hips and props too).
  const poseOnly = ragGoalPoseOnly(), rootBones = new Set(["root", "Root_M"]), props0 = new Set(BODY.props);
  put(out[E]); evalPose(E); model.updateMatrixWorld(true); const kRootW = wmat4(B.Root_M), kProp = {}; for (const k of props0) if (B[k]) kProp[k] = wmat4(B[k]);
  const Qa = new Q(), Qb = new Q(), Pa = new V3(), Pb = new V3(); let lift = 0;
  for (let f = b0; f <= last; f++) {
    if (!out[f]) continue;
    const w = (GL.match ?? 0.5) * (f >= b1 ? 1 : smooth01((f - b0 + 1) / (b1 - b0 + 1))), o = {};
    let tgt = key;
    if (poseOnly) { put(out[f]); const rel = wmat4(B.Root_M).multiply(kRootW.clone().invert()); tgt = { ...key };
      for (const n of rootBones) if (out[f][n]) tgt[n] = out[f][n];
      for (const k of Object.keys(kProp)) if (out[f][k]) tgt[k] = out[f][k]; }   // a released prop lies where it fell (placed with the hips it stood up in the air)
    for (const n of BN) { const a = out[f][n], b = tgt[n]; if (!a || !b) { if (a) o[n] = a; continue; }
      Qa.fromArray(a, 0); Qb.fromArray(b, 0); Pa.fromArray(a, 4); Pb.fromArray(b, 4); o[n] = packBone(Qa.clone().slerp(Qb, w), Pa.clone().lerp(Pb, w)); }
    if (f < b1) {                                   // not under the floor while blending (the last key itself is the user's)
      put(o); let W = bodyWorld(BODY); const props = new Set(BODY.props), low = ks => { let lo = 1e9; for (const k of ks) for (const q of W.shells[k] || []) if (q.y < lo) lo = q.y; return lo; };
      const lo = low(Object.keys(W.shells).filter(k => !props.has(k)));
      if (lo < -0.5 * CM_W) { const r = B.Root_M, wpn = wp(r).add(new V3(0, -lo, 0)); r.position.copy(r.parent.worldToLocal(wpn)); model.updateMatrixWorld(true); o.Root_M = packBone(r.quaternion, r.position); lift = Math.max(lift, -lo / CM_W); W = bodyWorld(BODY); }
      for (const k of props) { if (!B[k]) continue; const lp = low([k]);    // a released prop is its own bone: lift it on its own
        if (lp < -0.5 * CM_W) { const b = B[k], wpn = wp(b).add(new V3(0, -lp, 0)); b.position.copy(b.parent.worldToLocal(wpn)); model.updateMatrixWorld(true); o[k] = packBone(b.quaternion, b.position); lift = Math.max(lift, -lp / CM_W); } }
    }
    out[f] = o;
  }
  G.goal.blendFrom = b0; G.goal.blendTo = b1; G.goal.lift = +lift.toFixed(1); G.goal.poseOnly = poseOnly;
}
const ragGoalPoseOnly = () => (((ANIM.phys && ANIM.phys.rag && ANIM.phys.rag.goal) || {}).root ?? "pose") !== "full";
async function ragGoalSearch() {
  // 1 correct the push along the measured miss (where / how turned the body lies vs the last key), gain adapted;
  // 2 then a small pattern search. A pure pattern search from zero fell into a face-down landing (141 cm, 149 deg).
  const R = ragCfg(); R.goal = { ...RAG_GOAL_DEF, ...(R.goal || {}), on: true }; if (!Object.keys(R.groups || {}).length) R.groups = { ...RAG_GOAL_GROUPS };
  const GL = R.goal, btn = $("ragGoalFind"); btn.disabled = true; let n = 0; const MAXN = 60, fps = P.fps || 30; GL.releaseMoved = 0;
  const run = p => { GL.push = { vx: +p[0].toFixed(3), vz: +p[1].toFixed(3), wy: +p[2].toFixed(3) }; physDirty = true; computePhys(); n++;
    const g = PHYS && PHYS.rag && PHYS.rag.goal; return g ? { c: (ragGoalPoseOnly() ? 0 : g.dpos) + 0.5 * g.dang + 0.2 * g.dprop, g } : { c: 1e9, g: null }; };   // pose-only: the place is the physics'   // the prop counts too: a mace landing 57 deg off was turned back by the blend
  const LIM = [3, 3, 4], clamp = p => p.map((v, i) => Math.max(-LIM[i], Math.min(LIM[i], v)));
  const say = c => { $("p_status").textContent = "Tìm cú đổ: lần " + n + "/" + MAXN + ", tốt nhất lệch " + c.toFixed(1) + " (cm + độ/2)"; };
  let best = [0, 0, 0], br = run(best);
  if (GL.push && (GL.push.vx || GL.push.vz || GL.push.wy)) { const p = [GL.push.vx || 0, GL.push.vz || 0, GL.push.wy || 0], r = run(p); if (r.c < br.c) { best = p; br = r; } }
  try {
    let gain = 1;
    for (let it = 0; it < 14 && n < MAXN && br.g; it++) {
      const g = br.g, T = Math.max(0.3, ((g.land ?? (PHYS.rag.from + 15)) - PHYS.rag.from) / fps);
      const po = ragGoalPoseOnly() ? 0 : 1, p = clamp([best[0] + po * gain * g.dx / T, best[1] + po * gain * g.dz / T, best[2] + gain * g.dyaw / T]), r = run(p);
      if (r.c < br.c) { best = p; br = r; gain = Math.min(1.5, gain * 1.3); } else gain *= 0.5;
      say(br.c); await new Promise(z => setTimeout(z, 0));
      if (br.c < 2 || gain < 0.05) break;
    }
    let step = [0.25, 0.25, 0.4];
    while (n < MAXN && step.some((v, i) => v > [0.03, 0.03, 0.05][i])) {
      let moved = false;
      for (let i = ragGoalPoseOnly() ? 2 : 0; i < 3 && n < MAXN && !moved; i++) for (const sg of [1, -1]) {
        const p = best.slice(); p[i] += sg * step[i]; const q = clamp(p), r = run(q);
        if (r.c < br.c - 0.05) { br = r; best = q; moved = true; break; }
      }
      if (!moved) step = step.map(v => v / 2);
      say(br.c); await new Promise(z => setTimeout(z, 0));
    }
    // 3 a released prop that lands far off (> 15 deg): try the release a few frames earlier / later than the user's (+-4),
    // each with a short push correction; keep the best (Die goal_v1: the push alone left the mace 48 deg off)
    const rel0 = R.release;
    if (rel0 != null && br.g && br.g.dprop > 15) {
      let bestRel = rel0;
      for (const dr of [-4, -2, 2, 4]) {
        const rel = rel0 + dr; if (rel <= (R.from || 2)) continue; R.release = rel;
        let p = best.slice(), rr = run(p), gain = 1;
        for (let it = 0; it < 6 && n < MAXN + 40 && rr.g; it++) {
          const g = rr.g, T = Math.max(0.3, ((g.land ?? (PHYS.rag.from + 15)) - PHYS.rag.from) / fps);
          const po = ragGoalPoseOnly() ? 0 : 1, q = clamp([p[0] + po * gain * g.dx / T, p[1] + po * gain * g.dz / T, p[2] + gain * g.dyaw / T]), r2 = run(q);
          if (r2.c < rr.c) { p = q; rr = r2; } else gain *= 0.5;
        }
        if (rr.c < br.c) { br = rr; best = p; bestRel = rel; }
        say(br.c); await new Promise(z => setTimeout(z, 0));
      }
      R.release = bestRel; GL.releaseMoved = bestRel !== rel0 ? bestRel - rel0 : 0;
    }
  } finally {
    run(best); btn.disabled = false; physChanged(true);
    const g = PHYS && PHYS.rag && PHYS.rag.goal;
    $("p_status").textContent = g ? "Tìm xong (" + n + " lần chạy): hông lệch " + g.dpos + " cm, thân xoay lệch " + g.dang + "°" + (g.dprop ? ", vũ khí lệch " + g.dprop + "°" : "") + " trước khi trộn vào key cuối." + (GL.releaseMoved ? " Buông vũ khí dời " + (GL.releaseMoved > 0 ? "+" : "") + GL.releaseMoved + " frame (F" + R.release + ")." : "") : "Không tìm được.";
  }
}
function ragExtend() {                   // run long, find where it settles, keep a few frames more
  const R = ragCfg(), base = P.frames0 || P.frames; R.len = base + 90; ragLen(); computePhys();
  const at = PHYS && PHYS.rag && PHYS.rag.restAt; R.len = at ? Math.max(base, at + 4) : base + 90;
  physChanged(true); ragLen(); $("p_status").textContent = at ? "Clip kéo dài tới F" + R.len + " (nằm yên từ F" + at + ")." : "Sau 90 frame vẫn chưa nằm yên: clip dài " + R.len + " frame.";
}
// strength curve: x = frame, y = 0..100 %; drag a point, click to add, double-click to remove
function ragGX(f) { const cv = $("ragGraph"); return 14 + (f - 1) / Math.max(1, NFR() - 1) * (cv.width - 28); }
function ragGY(v) { const cv = $("ragGraph"); return cv.height - 22 - v / 100 * (cv.height - 40); }
function drawRagGraph() {
  const cv = $("ragGraph"); if (!cv) return; const g = cv.getContext("2d"), W = cv.width, H = cv.height, R = ragCfg(); g.clearRect(0, 0, W, H);
  g.font = "20px " + css("--font-num"); g.fillStyle = css("--muted");
  if (!R.on) { g.fillText("Bật ragdoll để vẽ đường Sức", 14, H / 2); return; }
  g.fillStyle = "#1fa37a33"; g.fillRect(ragGX(frame) - 3, 0, 6, H);
  g.fillStyle = "#ffffff10"; g.fillRect(14, ragGY(100), Math.max(0, ragGX(R.from) - 14), ragGY(0) - ragGY(100));
  g.strokeStyle = "#ffffff22"; g.lineWidth = 1; for (const v of [0, 50, 100]) { g.beginPath(); g.moveTo(14, ragGY(v)); g.lineTo(W - 14, ragGY(v)); g.stroke(); }
  g.strokeStyle = "#ff9f43"; g.lineWidth = 3.5; g.beginPath();
  for (let f = R.from; f <= NFR(); f++) { const x = ragGX(f), y = ragGY(ragStrength(f) * 100); f === R.from ? g.moveTo(x, y) : g.lineTo(x, y); } g.stroke();
  g.fillStyle = "#ff9f43"; for (const [f, v] of R.pts) { g.beginPath(); g.arc(ragGX(f), ragGY(v), 7, 0, 7); g.fill(); }
  const G = PHYS && PHYS.rag; if (G && G.restAt) { g.fillStyle = css("--accent"); g.fillRect(ragGX(G.restAt) - 1, 0, 2, H); }
  g.fillStyle = css("--muted"); g.fillText("Sức 100 %", 16, 20); g.fillText("F1", 14, H - 2); g.fillText("F" + NFR(), W - 64, H - 2);
}
function ragGraphHit(e) {
  const cv = $("ragGraph"), r = cv.getBoundingClientRect(), x = (e.clientX - r.left) * cv.width / r.width, y = (e.clientY - r.top) * cv.height / r.height;
  const f = Math.max(1, Math.min(NFR(), Math.round(1 + (x - 14) / (cv.width - 28) * (NFR() - 1)))), v = Math.max(0, Math.min(100, Math.round((cv.height - 22 - y) / (cv.height - 40) * 100)));
  const R = ragCfg(); let i = R.pts.findIndex(([pf, pv]) => Math.hypot(ragGX(pf) - x, ragGY(pv) - y) < 14);
  return { f, v, i };
}
function ragChanged() { const R = ragCfg(); R.pts.sort((a, b) => a[0] - b[0]); physChanged(false); drawRagGraph(); renderLanes(); }
$("ragGraph").addEventListener("pointerdown", e => {
  const R = ragCfg(); if (!R.on) return; const h = ragGraphHit(e);
  if (h.i < 0) { R.pts.push([Math.max(R.from, h.f), h.v]); h.i = R.pts.length - 1; ragChanged(); }
  ragDrag = R.pts[h.i]; try { $("ragGraph").setPointerCapture(e.pointerId); } catch {}
});
$("ragGraph").addEventListener("pointermove", e => { if (!ragDrag) return; const h = ragGraphHit(e), R = ragCfg(); ragDrag[0] = Math.max(R.from, h.f); ragDrag[1] = h.v; drawRagGraph(); });
$("ragGraph").addEventListener("pointerup", () => { if (ragDrag) { ragDrag = null; ragChanged(); } });
$("ragGraph").addEventListener("dblclick", e => { const R = ragCfg(), h = ragGraphHit(e); if (h.i >= 0 && R.pts.length > 1) { R.pts.splice(h.i, 1); ragChanged(); } });
$("ragOn").onclick = () => {
  const R = ragCfg(); R.on = !R.on;
  if (R.on) { if (R.from == null) { const i = (ANIM.phys.impacts || []).find(x => x.f >= frame) || (ANIM.phys.impacts || [])[0]; R.from = Math.max(2, i && Math.abs(i.f - frame) < 3 ? i.f : frame); } if (!R.pts.length) R.pts = ragDefaultPts(R.from); ANIM.phys.on = true; }
  ragLen(); physChanged(true);
};
// v3 (user "không nhất thiết phải giữ đúng pose cuối 100%... như một bức tượng đá đổ xuống"): a weak pull only, limbs and
// head nearly limp, no held tone; the last key is a direction, matched by `match` (0..1) in the blend
const RAG_GOAL_DEF = { gs: 0.15, pre: 0.3, preS: 0.04, preF: 16, letGo: 10, hold: 0, blend: 10, match: 0.5 };
const RAG_GOAL_GROUPS = { head: 0.15, armL: 0.3, armR: 0.3, legL: 0.5, legR: 0.5 };   // loose head / arms / legs: they flop, the knees give
$("ragGoal").onclick = () => { const R = ragCfg(), on = !(R.goal && R.goal.on); R.goal = { ...RAG_GOAL_DEF, ...(R.goal || {}), on };
  if (on && !Object.keys(R.groups || {}).length) R.groups = { ...RAG_GOAL_GROUPS }; physChanged(true); };
$("ragGoalFind").onclick = () => { ragGoalSearch(); };
$("ragGoalRoot").onclick = () => { const R = ragCfg(); if (!R.goal) return; R.goal.root = ragGoalPoseOnly() ? "full" : "pose"; physChanged(true); };
$("ragMatch").oninput = () => { const R = ragCfg(); if (!R.goal) return; R.goal.match = +$("ragMatch").value; $("ragMatchOut").textContent = Math.round(R.goal.match * 100) + " %"; physChanged(false); };
$("ragFrom").onchange = () => { const R = ragCfg(), f = Math.max(2, Math.min(NFR(), Math.round(+$("ragFrom").value || 2))), d = f - (R.from || f); R.from = f; R.pts = R.pts.map(([pf, v]) => [pf + d, v]); physChanged(true); };
$("ragRelease").onclick = () => { const R = ragCfg(); R.release = R.release != null ? null : Math.max(R.from || 2, frame); physChanged(true); };

$("ragLim").onclick = () => { ragLimOn = !ragLimOn; renderRag(); drawRagLimits(); };
$("laneS").addEventListener("click", e => { const f = frameAtX(e.clientX); stopPlay(); goto(f); });
// limits of the selected joint on the model: the box of allowed directions of its segment (bend x spread) as a fan of lines
function drawRagLimits() {
  if (ragLimViz) { overlay.remove(ragLimViz); ragLimViz.traverse(o => { if (o.geometry) o.geometry.dispose(); if (o.material) o.material.dispose(); }); ragLimViz = null; }
  const el = $("ragLimTxt"); if (el) el.textContent = "";
  if (!ragLimOn || !model || !sel) return; if (!BODY) BODY = buildBody();
  const segs = ragSegs(), s = segs.find(x => x.k === sel); if (!s || !s.par) { if (el) el.textContent = "Chọn một khớp (vai, khuỷu, cổ tay, hông, gối, cổ chân, thân, đầu) để xem giới hạn."; return; }
  const L = ({ ...ragLimits(), ...RAG_LIM_OVER })[s.k]; if (!L) return;
  const q0 = ragRest()[s.k], ax = ragAxes(s.k), pq = wq(B[s.par]), pv = wp(B[s.k]), c = BODY.caps[s.k], len = c.a.distanceTo(c.b) * 1.1, rad = THREE.MathUtils.degToRad;
  const dirAt = (b, sp) => ax.t.clone().applyQuaternion(pq.clone().multiply(q0).multiply(ragJoin([rad(b), rad(sp), 0], ax))).multiplyScalar(len).add(pv);
  const ring = []; const N = 12;
  for (let i = 0; i <= N; i++) ring.push(dirAt(L[0] + (L[1] - L[0]) * i / N, L[2]));
  for (let i = 0; i <= N; i++) ring.push(dirAt(L[1], L[2] + (L[3] - L[2]) * i / N));
  for (let i = 0; i <= N; i++) ring.push(dirAt(L[1] - (L[1] - L[0]) * i / N, L[3]));
  for (let i = 0; i <= N; i++) ring.push(dirAt(L[0], L[3] - (L[3] - L[2]) * i / N));
  const mat = new THREE.LineBasicMaterial({ color: 0xff9f43, depthTest: false, transparent: true });
  ragLimViz = new THREE.Group(); ragLimViz.renderOrder = 13;
  ragLimViz.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(ring), mat));
  for (const p of [ring[0], ring[N], ring[2 * N + 1], ring[3 * N + 2]]) ragLimViz.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints([pv, p]), mat.clone()));
  const now = ax.t.clone().applyQuaternion(wq(B[s.k])).multiplyScalar(len).add(pv);
  ragLimViz.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints([pv, now]), new THREE.LineBasicMaterial({ color: 0x5aa9ff, depthTest: false, transparent: true })));
  ragLimViz.traverse(o => o.renderOrder = 13); overlay.add(ragLimViz);
  if (el) el.textContent = bodyName(s.k) + ": gập " + L[0] + "…" + L[1] + "°, dang " + L[2] + "…" + L[3] + "°, xoắn " + L[4] + "…" + L[5] + "° (so với tư thế nghỉ). Cam: vùng cho phép, xanh: hướng hiện tại.";
}
// ---------------------------------------------------------------- physics panel
let physT = 0;
function physChanged(rebuild) {
  ANIM.phys.pin = fmtSet(PINS); animAt = new Date().toISOString(); animDirty = true; physDirty = true; scheduleFlush(); bodyChanged();
  if (rebuild) renderPhys();
  clearTimeout(physT); physT = setTimeout(() => { reEval(); physInfo(); drawPhysGraph(); renderLanes(); impInfo(); drawImpacts(); ragInfo(); drawRagGraph(); }, 40);
}
function guessPart(n) {
  const prop = (P.follow && P.follow.prop) || (B.Weapon ? "Weapon" : B[GUN] ? GUN : null);
  if (n === prop) return { bone: n, type: "prop", hand: (P.follow && P.follow.hand) || (n === GUN ? "R" : "L"), preset: "heavy" };
  if (/^(Elbow|Knee)_/.test(n)) return { bone: n, type: "hinge", preset: "medium" };
  return { bone: n, type: "joint", preset: /^(Wrist|Head|Neck)/.test(n) ? "light" : "medium" };
}
const charPhys = () => (RIGSET() && RIGSET().limits ? { parts: [], colliders: [], end: 8, limits: RIGSET().limits, rest: null } : null)
  || CHAR_PHYS[Object.keys(CHAR_PHYS).find(k => (P.clip || "").startsWith(k))] || null;
const mkEl = (tag, cls, txt) => { const e = document.createElement(tag); if (cls) e.className = cls; if (txt != null) e.textContent = txt; return e; };
// AutoPhysics layers on PHYS.out (page locals per frame). Order: rotation smoothing -> trajectory smoothing -> separation ->
// penetration; planted feet are put back where they were (leg IK) and a held prop stays in the hand.
const blendM = (A, Bm, t) => { const pa = new V3(), qa = new Q(), sa = new V3(), pb = new V3(), qb = new Q(), sb = new V3(); A.decompose(pa, qa, sa); Bm.decompose(pb, qb, sb);
  return new THREE.Matrix4().compose(pa.lerp(pb, t), qa.slerp(qb, t), sa.lerp(sb, t)); };
function apPost(out, last, RAG, springBones, base) {
  const t0 = performance.now(), loop = !!P.loop, N = loop ? PER() : last, end = RAG && RAG.from ? Math.min(N, RAG.from - 1) : N;
  if (end < 3) return null;
  const st = {}, Fs = []; for (let f = 1; f <= end; f++) if (out[f]) Fs.push(f);
  const put = o => { for (const n of BN) if (o[n]) { B[n].quaternion.fromArray(o[n], 0); B[n].position.fromArray(o[n], 4); } model.updateMatrixWorld(true); };
  const packAll = () => { const o = {}; for (const n of BN) o[n] = packBone(B[n].quaternion, B[n].position); return o; };
  const wrap = f => loop ? ((f - 1) % N + N) % N + 1 : Math.max(1, Math.min(end, f));
  const edge = f => loop ? 1 : smooth01(Math.min(f - 1, end - f) / 3);            // one-shot: F1 and the last frame stay the key
  // what to keep: planted feet (contact lanes, or slow + low), the held prop's grip
  const orig = {}, ank = { L: {}, R: {} }; for (const f of Fs) { orig[f] = out[f]; put(out[f]); for (const s of ["L", "R"]) if (B["Ankle_" + s]) ank[s][f] = { p: wp(B["Ankle_" + s]), q: wq(B["Ankle_" + s]) }; }
  const planted = { L: new Set(), R: new Set() };
  for (const s of ["L", "R"]) { if (!B["Ankle_" + s]) continue; const ys = Fs.map(f => ank[s][f].p.y), lo = Math.min(...ys);
    for (const f of Fs) { if (CT[s] && CT[s].size) { if (CT[s].has(f)) planted[s].add(f); continue; }
      const a = ank[s][f].p, b = ank[s][wrap(f - 1)] ? ank[s][wrap(f - 1)].p : a, c = ank[s][wrap(f + 1)] ? ank[s][wrap(f + 1)].p : a;
      if (a.y < lo + 4 * CM_W && Math.max(a.distanceTo(b), a.distanceTo(c)) < 1.5 * CM_W) planted[s].add(f); } }
  const propN = (P.follow && P.follow.prop) || (B.Weapon ? "Weapon" : B[GUN] ? GUN : null), hs = propN ? (guessPart(propN).hand || "L") : null;
  // grips per frame and hand: a prop point within 6 cm of the hand's core = holding it there (Attack: the hands slide along the
  // haft and both hold it at times; a grip fixed to F1's spot let the mace leave the hand by up to 1 m)
  const grip = { L: {}, R: {}, both: {} };
  // measured on the KEY pose (base): the springs (secondary) had already pulled Attack's right hand 67 cm off the haft
  if (propN && B[propN]) for (const f of Fs) { put(base && base[f] ? base[f] : out[f]); const W = bodyWorld(BODY), pts = W.shells[propN] || [];
    for (const sd of ["L", "R"]) { const w = B["Wrist_" + sd], c = W.caps["Wrist_" + sd]; if (!w || !c || !pts.length) continue; let dmin = 1e9;   // the hand's core + 6 cm (as the prop spring's grip test)
      for (const q of pts) dmin = Math.min(dmin, q.distanceTo(closestOnSeg(q, c.a, c.b)) - c.r);
      if (dmin < GRIP_CM * CM_W) grip[sd][f] = wmat4(w).invert().multiply(wmat4(B[propN])); }
    if (grip.L[f] && grip.R[f] && B.Chest_M) (grip.both ||= {})[f] = wmat4(B.Chest_M).invert().multiply(wmat4(B[propN])); }   // two hands: the prop rides the chest as in the key
  const skip = new Set([...springBones, ...(propN ? [propN] : [])]);
  const isLeg = n => /^(Hip|Knee|Ankle|Toes|ToesEnd)_/.test(n);
  const gauss = (vals, sig, f) => { let w = 0, acc = null; const R = Math.ceil(sig * 2.5);
    for (let d = -R; d <= R; d++) { const g = wrap(f + d); if (!loop && (f + d < 1 || f + d > end)) continue; const k = Math.exp(-0.5 * d * d / (sig * sig)), v = vals[g]; if (!v) continue;
      acc = acc ? acc.map((x, i) => x + k * v[i]) : v.map(x => k * x); w += k; } return acc ? acc.map(x => x / w) : null; };
  const series = n => { const Q4 = {}; let prev = null; for (const f of Fs) { const a = out[f][n]; if (!a) continue; let q = a.slice(0, 4); if (prev && q[0] * prev[0] + q[1] * prev[1] + q[2] * prev[2] + q[3] * prev[3] < 0) q = q.map(x => -x); Q4[f] = q; prev = q; } return Q4; };
  const setQ = (o, n, q, w) => { const a = new Q().fromArray(o[n], 0), b = new Q(q[0], q[1], q[2], q[3]).normalize(); a.slerp(b, w); o[n] = [...a.toArray().map(x => +x.toFixed(6)), ...o[n].slice(4)]; };
  // 1 rotation smoothing
  if (apOn("rot")) { const sig = 0.3 + 1.5 * apV("rot"), cap = THREE.MathUtils.degToRad(1 + 9 * apV("rot")); let mx = 0; const nw = {}; for (const f of Fs) nw[f] = { ...out[f] };
    // a capped change: the filter takes out jitter / pops; a big fast swing keeps its shape (uncapped 50 % ate 25 deg of Attack's swing)
    for (const n of BN) { if (skip.has(n) || isLeg(n) || !out[Fs[0]][n]) continue; const Q4 = series(n);
      for (const f of Fs) { const q = gauss(Q4, sig, f); if (!q) continue; const before = new Q().fromArray(out[f][n], 0), tgt = new Q(q[0], q[1], q[2], q[3]).normalize(), ang = before.angleTo(tgt);
        setQ(nw[f], n, q, edge(f) * (ang > cap ? cap / ang : 1)); mx = Math.max(mx, THREE.MathUtils.radToDeg(before.angleTo(new Q().fromArray(nw[f][n], 0)))); } }
    for (const f of Fs) out[f] = nw[f]; st.rot = +mx.toFixed(1); }
  // 2 trajectory smoothing (hips position; the feet are re-planted below)
  if (apOn("traj") && B.Root_M) { const sig = 0.3 + 1.7 * apV("traj"), P3 = {}; for (const f of Fs) P3[f] = out[f].Root_M.slice(4); let mx = 0;
    for (const f of Fs) { const v = gauss(P3, sig, f); if (!v) continue; const w = edge(f), o = { ...out[f] }, a = o.Root_M, np = a.slice(4).map((x, i) => x + (v[i] - x) * w);
      mx = Math.max(mx, Math.hypot(np[0] - a[4], np[1] - a[5], np[2] - a[6])); o.Root_M = [...a.slice(0, 4), ...np.map(x => +x.toFixed(5))]; out[f] = o; }
    put(out[Fs[0]]); const sc = B.Root_M.parent.getWorldScale(new V3()).x || 1; st.traj = +(mx * sc / CM_W).toFixed(1); }
  // 3 separation: each level of the spine / arm chains follows its own rotation curve a little later
  if (apOn("sep")) { const per = 1.2 * apV("sep"), CH = { Spine1_M: 1, Chest_M: 2, Neck_M: 3, Head_M: 4, Scapula_L: 3, Shoulder_L: 4, Elbow_L: 5, Wrist_L: 6, Scapula_R: 3, Shoulder_R: 4, Elbow_R: 5, Wrist_R: 6 };
    const nw = {}; for (const f of Fs) nw[f] = { ...out[f] }; let md = 0;
    for (const [n, lv] of Object.entries(CH)) { if (skip.has(n) || !out[Fs[0]][n]) continue; const Q4 = series(n), d = per * lv; md = Math.max(md, d);
      for (const f of Fs) { const t = f - d, f0 = Math.floor(t), u = t - f0, a = Q4[wrap(f0)], b = Q4[wrap(f0 + 1)]; if (!a || !b) continue;
        const qa = new Q(a[0], a[1], a[2], a[3]), qb = new Q(b[0], b[1], b[2], b[3]); qa.slerp(qb, u); setQ(nw[f], n, qa.toArray(), edge(f)); } }
    for (const f of Fs) out[f] = nw[f]; st.sep = +md.toFixed(1); }
  // planted feet back on their spot, the held prop back in the hand
  const fix = f => { for (const s of ["L", "R"]) if (planted[s].has(f) && B["Hip_" + s]) { const a = ank[s][f]; solve2(LEGS[s], a.p.clone(), a.q.clone()); }
    if (!propN) return; const main = grip[hs][f] ? hs : grip[hs === "L" ? "R" : "L"][f] ? (hs === "L" ? "R" : "L") : null; if (!main) return;
    const placeProp = m => { const pp = new V3(), qq = new Q(); m.decompose(pp, qq, new V3()); const b = B[propN], ws = new V3(); b.getWorldScale(ws); setWorldMat(b, new THREE.Matrix4().compose(pp, qq, ws)); model.updateMatrixWorld(true); };
    // two hands: the prop rides the chest as in the key; around a change of grip it eases in / out over 4 frames (a switch at
    // once made Attack's left hand jump 33 cm at F9 with Separation on), and the hands holding it follow it
    let wb = 0, ref = null; for (let d = -4; d <= 4; d++) { const g = wrap(f + d); if (grip.both[g] && (loop || (f + d >= 1 && f + d <= end))) { const w = smooth01(1 - Math.abs(d) / 4); if (w > wb) { wb = w; ref = g; } } }
    const fromHand = wmat4(B["Wrist_" + main]).multiply(grip[main][f]);
    if (wb > 0) { const rig = wmat4(B.Chest_M).multiply(grip.both[f] || grip.both[ref]); placeProp(blendM(fromHand, rig, wb));
      for (const sd of ["L", "R"]) if (grip[sd][f]) { const m = wmat4(B[propN]).multiply(grip[sd][f].clone().invert()), pp = new V3(), qq = new Q(); m.decompose(pp, qq, new V3()); solve2(ARMS[sd], pp, qq); }
      return; }
    placeProp(fromHand);
    const oth = main === "L" ? "R" : "L";                                  // the other hand on the haft stays on its spot
    if (grip[oth][f]) { const m = wmat4(B[propN]).multiply(grip[oth][f].clone().invert()), pp = new V3(), qq = new Q(); m.decompose(pp, qq, new V3()); solve2(ARMS[oth], pp, qq); } };
  // secondary: the springs' body-contact safety can snap a bone for one frame (Hit F13: right wrist 43 deg then back);
  // a frame far off the midway of its neighbours is pulled to it (2 passes)
  if (apOn("sec")) { let n0 = 0; for (let it = 0; it < 2; it++) for (const n of springBones) { if (!B[n] || !out[Fs[0]][n] || n === propN) continue;
      for (let i = 1; i < Fs.length - 1; i++) { const f = Fs[i], a = new Q().fromArray(out[Fs[i - 1]][n], 0), c = new Q().fromArray(out[Fs[i + 1]][n], 0), mid = a.clone().slerp(c, 0.5), q = new Q().fromArray(out[f][n], 0), off = q.angleTo(mid);
        if (off > THREE.MathUtils.degToRad(8)) { const o = { ...out[f] }; q.slerp(mid, 1 - THREE.MathUtils.degToRad(4) / off); o[n] = [...q.toArray().map(x => +x.toFixed(6)), ...o[n].slice(4)]; out[f] = o; n0++; } } }
    st.despike = n0; }
  // around a grab / release of the prop (+-6 F) the arm eases back to its own animation, so the hand arrives on the haft
  // where the key has it (Attack: the right hand lagging by Separation was snapped onto the haft at F9, 36-44 deg/F)
  const ARMB = { L: ["Scapula_L", "Shoulder_L", "Elbow_L", "Wrist_L"], R: ["Scapula_R", "Shoulder_R", "Elbow_R", "Wrist_R"] };
  if (propN) for (const sd of ["L", "R"]) { const T = []; for (const f of Fs) { const g = wrap(f - 1); if (f > Fs[0] || loop) if (!!grip[sd][f] !== !!grip[sd][g] || !!grip.both[f] !== !!grip.both[g]) T.push(f); }   // own grab / release, or one hand <-> two hands
    if (!T.length) continue;
    for (const f of Fs) { let d = 1e9; for (const t of T) d = Math.min(d, loop ? Math.min(Math.abs(f - t), N - Math.abs(f - t)) : Math.abs(f - t)); const keep = 1 - smooth01(d / 6); if (keep <= 0) continue;
      const src = base && base[f] ? base[f] : orig[f];                       // the KEY pose: the springs lag the arm too
      const o = { ...out[f] }; for (const n of ARMB[sd]) if (o[n] && src[n]) { const a = new Q().fromArray(o[n], 0).slerp(new Q().fromArray(src[n], 0), keep); o[n] = [...a.toArray().map(x => +x.toFixed(6)), ...o[n].slice(4)]; } out[f] = o; } }
  for (const f of Fs) { put(out[f]); fix(f); out[f] = packAll(); }   // every layer, the springs too: feet planted, hands on the prop
  // 4 penetration: lift off the floor (not the planted feet), push arms / free legs out of the body
  if (apOn("pen")) { const k = Math.min(1, 2 * apV("pen")), maxA = 6 + 18 * apV("pen"), cor = {}; let fl = 0, fixedB = 0, leftB = 0;
    const props = new Set(BODY.props);   // a prop on the floor is the animator's (Attack's mace slam): not a reason to lift the body
    const lowOf = (W, segs) => { let lo = 1e9; for (const sg of segs) for (const q of W.shells[sg] || []) if (q.y < lo) lo = q.y; return lo; };
    const lowNoFeet = f => { const W = bodyWorld(BODY); return lowOf(W, Object.keys(W.shells).filter(sg => !props.has(sg) && !/^Ankle_/.test(sg))); };
    // a free foot is "under the floor" only below its own planted level (Gaygor's soles sit 1.5-2 cm under 0 even in Idle)
    const footRest = {}; for (const sd of ["L", "R"]) { let m = null; for (const f of Fs) if (planted[sd].has(f)) { put(out[f]); const v = lowOf(bodyWorld(BODY), ["Ankle_" + sd]); m = m == null ? v : Math.min(m, v); } footRest[sd] = Math.min(0, m ?? 0); }
    const footDip = f => { const W = bodyWorld(BODY), o = {}; for (const sd of ["L", "R"]) if (!planted[sd].has(f) && W.shells["Ankle_" + sd]) { const lo = lowOf(W, ["Ankle_" + sd]), d = footRest[sd] - lo; if (d > 0.5 * CM_W) o[sd] = d; } return o; };
    const AX = [[1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0], [0, 0, 1], [0, 0, -1]].map(a => new V3(...a));
    const mover = it => { if ((it.a === "Head_M" || it.b === "Head_M") && it.b !== "floor") return B.Neck_M ? "Neck_M" : "Head_M";   // the head moves, not the shoulder
      for (const n of [it.a, it.b]) { const m = n.match(/^(Shoulder|Elbow|Wrist)_([LR])$/); if (m && !(grip[m[2]] && grip[m[2]][curF])) return "Shoulder_" + m[2];   /* a hand on the prop is not pushed (the grip wins) */ const l = n.match(/^(Hip|Knee|Ankle)_([LR])$/); if (l && !planted[l[2]].has(curF)) return "Hip_" + l[2]; } return null; };
    let curF = 0, penBefore = 0;
    for (const f of Fs) { curF = f; put(out[f]); const lo = lowNoFeet(f); cor[f] = {}; penBefore += bodyIssues(bodyWorld(BODY), BODY).length + (lo < -1 * CM_W ? 1 : 0) + Object.keys(footDip(f)).length;
      if (lo < -0.5 * CM_W) { cor[f].lift = -lo * k; fl++; }
      const fd = footDip(f); for (const sd of Object.keys(fd)) { cor[f]["foot" + sd] = fd[sd] * k; fl++; }
      for (const it of bodyIssues(bodyWorld(BODY), BODY)) { const bn = mover(it); if (!bn || cor[f][bn]) continue;
        const q0 = wq(B[bn]), depth = () => { const x = bodyIssues(bodyWorld(BODY), BODY).find(i => (i.a === it.a && i.b === it.b) || (i.a === it.b && i.b === it.a)); return x ? x.cm : 0; };
        let best = null;
        for (let a = 3; a <= maxA && !best; a += 3) for (const ax of AX) { setWorldQuat(B[bn], new Q().setFromAxisAngle(ax, THREE.MathUtils.degToRad(a)).multiply(q0)); model.updateMatrixWorld(true);
          if (!depth()) { best = { ax, a }; break; } }
        setWorldQuat(B[bn], q0); model.updateMatrixWorld(true);
        if (best) { cor[f][bn] = best.ax.clone().multiplyScalar(THREE.MathUtils.degToRad(best.a)); fixedB++; } else leftB++; } }
    // corrections eased over time (sigma 1.5 F) so nothing pops
    const bones = new Set(); for (const f of Fs) for (const n of Object.keys(cor[f])) if (n !== "lift" && !/^foot/.test(n)) bones.add(n);
    // full correction on the frames that need it, eased in / out over the neighbours (a plain average with the untouched
    // neighbours gave a needed frame only ~40 % of its fix: head-shoulder contacts stayed)
    const ease = (f, get) => { let acc = 0, wc = 0, kmax = 0, vec = null;
      for (let d = -6; d <= 6; d++) { const g = wrap(f + d); if (!cor[g] || (!loop && (f + d < 1 || f + d > end))) continue; const c = get(cor[g]); if (!c) continue;
        const w = Math.exp(-0.5 * d * d / 6.25); wc += w;   /* sigma 2.5 F: 1.5 F turned a one-frame arm push into a 21 deg/F jolt */ kmax = Math.max(kmax, w); if (typeof c === "number") acc += w * c; else (vec ||= new V3()).addScaledVector(c, w); }
      if (!wc) return null; return vec ? vec.divideScalar(wc).multiplyScalar(kmax) : acc / wc * kmax; };
    for (const f of Fs) { put(out[f]);
      for (const n of bones) { const v = ease(f, c => c[n]); if (!v) continue; const a = v.length(); if (a > 1e-6) setWorldQuat(B[n], new Q().setFromAxisAngle(v.clone().normalize(), a).multiply(wq(B[n]))); }
      let lift = (ease(f, c => c.lift) || 0) * edge(f); if (lift > 0) { const r = B.Root_M, p1 = wp(r).add(new V3(0, lift, 0)); r.position.copy(r.parent.worldToLocal(p1)); }
      model.updateMatrixWorld(true); fix(f);
      for (const sd of ["L", "R"]) { const fu = ease(f, c => c["foot" + sd]) || 0; if (fu > 1e-4 && !planted[sd].has(f)) { const a = B["Ankle_" + sd]; solve2(LEGS[sd], wp(a).add(new V3(0, fu, 0)), wq(a)); } }   // a free foot under the floor: that leg up
      out[f] = packAll(); }
    let left = 0; for (const f of Fs) { put(out[f]); left += bodyIssues(bodyWorld(BODY), BODY).length + (lowNoFeet(f) < -1 * CM_W ? 1 : 0) + Object.keys(footDip(f)).length; }
    st.pen = { floor: fl, body: fixedB, unfixed: leftB, before: penBefore, left }; }
  if (apOn("sec")) st.sec = { parts: springBones.length, k: +(2 * apV("sec")).toFixed(2) };
  st.ms = Math.round(performance.now() - t0); st.end = end; st.grip = propN ? { L: Object.keys(grip.L).length, R: Object.keys(grip.R).length, prop: propN, main: hs } : null;
  return st;
}
function renderAP() {
  const box = $("apRows"); if (!box) return; box.innerHTML = ""; const ap = ANIM.phys.ap || {};
  for (const [k, lab, tip, later] of AP_ROWS) {
    const row = mkEl("div", "aprow"), on = !!(ap[k] && ap[k].on) && !later, b = mkEl("button", "btn" + (on ? " primary" : ""), later ? "đợt 2" : on ? "Bật" : "Tắt");
    b.disabled = !!later; b.title = tip; b.onclick = () => { const a = (ANIM.phys.ap ||= {}); a[k] = { v: 50, ...(a[k] || {}), on: !on }; if (!on) ANIM.phys.on = true; physChanged(true); };
    const l = mkEl("label", "psl"), r = mkEl("input"), o = mkEl("output"), v = ap[k] && ap[k].v != null ? ap[k].v : 50;
    r.type = "range"; r.min = 0; r.max = 100; r.step = 5; r.value = v; r.disabled = !on; o.textContent = v;
    r.oninput = () => { o.textContent = r.value; }; r.onchange = () => { const a = (ANIM.phys.ap ||= {}); a[k] = { ...(a[k] || {}), v: +r.value }; physChanged(false); };
    const name = mkEl("span", "", lab); name.title = tip; l.append(name, r, o); row.append(b, l); box.append(row);
  }
  const info = $("apInfo"); if (!info) return; info.textContent = "";
  const A = PHYS && PHYS.ap; if (!apAny()) { info.textContent = "Bật từng mục để so trước / sau (bóng mờ là pose key). Key gốc không đổi; ưng thì Bake thành key."; return; }
  if (!A) return; const t = [];
  if (A.traj != null) t.push("hông dời tối đa " + A.traj + " cm"); if (A.rot != null) t.push("khớp xoay bớt tối đa " + A.rot + "°");
  if (A.sep != null) t.push("đầu / cổ tay trễ tới " + A.sep + " frame"); if (A.sec) t.push(A.sec.parts + " phần lò xo × " + A.sec.k);
  if (A.pen) t.push("xuyên: " + A.pen.before + " chỗ → còn " + A.pen.left + " (nâng khỏi sàn " + A.pen.floor + ", đẩy tay/chân " + A.pen.body + (A.pen.unfixed ? ", " + A.pen.unfixed + " chỗ không đẩy được" : "") + ")");
  info.textContent = "AutoPhysics F1–F" + A.end + ": " + t.join(" · ") + " (" + A.ms + " ms).";
}
function renderPhys() {
  const box = $("physBox"); box.hidden = !keysMode() || !model; if (box.hidden) return;
  const cfg = ANIM.phys; renderAP();
  $("physOn").textContent = "Vật lý: " + (cfg.on ? "bật" : "tắt"); $("physOn").classList.toggle("primary", cfg.on);
  $("physChar").disabled = !charPhys();
  const undoable = !!bakeUndo && !cfg.on; $("physBake").textContent = undoable ? "Hoàn tác bake" : "Bake thành key";
  $("physBake").disabled = !undoable && (!cfg.on || (!cfg.parts.length && !(cfg.impacts || []).length && !(cfg.rag && cfg.rag.on) && !apAny()));
  $("physEnd").value = cfg.end ?? 8; $("physEnd").disabled = !!P.loop;
  const ni = (cfg.impacts || []).length;
  $("physSum").textContent = (cfg.parts.length ? cfg.parts.length + " phần" : "chưa có phần nào") + (ni ? " · " + ni + " tác động" : "") + (cfg.rag && cfg.rag.on ? " · ragdoll" : "") + (cfg.on || !(cfg.parts.length || ni) ? "" : " · đang tắt");
  if (physSel >= cfg.parts.length) physSel = Math.max(0, cfg.parts.length - 1);
  const list = $("physParts"); list.innerHTML = "";
  if (!cfg.parts.length) list.append(mkEl("div", "pinfo", "Chọn một khớp trên model rồi bấm \"+ Thêm khớp đang chọn\", hoặc bấm \"Mức của nhân vật\"."));
  cfg.parts.forEach((p, i) => {
    const x = physPart(p), row = mkEl("div", "ppart" + (i === physSel ? " on" : "")), ph = mkEl("div", "ph");
    const nm = mkEl("b", "", physName(p.bone) + (B[p.bone] ? "" : " (không có)")); nm.title = "Chọn để xem đồ thị";
    nm.onclick = () => { physSel = i; if (B[p.bone]) select(p.bone); renderPhys(); };
    const ty = mkEl("select"); ty.title = "Loại";
    for (const [k, v] of Object.entries(PHYS_TYPES)) {
      if (k === "swing" && !/^Elbow_/.test(p.bone)) continue;
      const o = mkEl("option", "", v); o.value = k; ty.append(o);
    }
    ty.value = p.type; ty.onchange = () => { p.type = ty.value; if (p.type === "prop" && !p.hand) p.hand = "L"; physChanged(true); };
    const pr = mkEl("select"); pr.title = "Mức có sẵn";
    for (const [k, v] of Object.entries(PHYS_PRESETS)) { const o = mkEl("option", "", v.label); o.value = k; pr.append(o); }
    const custom = mkEl("option", "", "Tự chỉnh"); custom.value = ""; pr.append(custom);
    pr.value = p.period == null && p.bounce == null && p.limit == null ? (p.preset || "medium") : "";
    pr.onchange = () => { if (!pr.value) return; p.preset = pr.value; delete p.period; delete p.bounce; delete p.limit; physChanged(true); };
    const rm = mkEl("button", "pX", "×"); rm.title = "Bỏ phần này";
    rm.onclick = () => { const o = cfg.parts[i]; ANIM.phys.parts = (ANIM.phys.parts || []).filter(x => x !== o && x.bone !== o.bone); physChanged(true); };
    ph.append(nm, ty, pr, rm); row.append(ph);
    for (const [key, lab, lo, hi, st, unit] of [["period", "Độ nặng", 4, 24, 1, "F"], ["bounce", "Độ nảy", 0, 0.8, 0.01, ""], ["limit", "Giới hạn", 3, 40, 1, "°"]]) {
      const l = mkEl("label", "psl"), r = mkEl("input"), out = mkEl("output");
      r.type = "range"; r.min = lo; r.max = hi; r.step = st; r.value = x[key];
      const fmt = v => (st < 1 ? (+v).toFixed(2) : v) + unit; out.textContent = fmt(x[key]);
      r.oninput = () => { p[key] = +r.value; out.textContent = fmt(r.value); pr.value = ""; physSel = i; physChanged(false); };
      l.append(mkEl("span", "", lab), r, out); row.append(l);
    }
    if (p.type === "prop") {
      const l = mkEl("label", "psl"), hs = mkEl("select");
      for (const [k, v] of [["L", "Tay trái"], ["R", "Tay phải"]]) { const o = mkEl("option", "", v); o.value = k; hs.append(o); }
      hs.value = p.hand || "L"; hs.onchange = () => { p.hand = hs.value; physChanged(); };
      l.append(mkEl("span", "", "Tay nắm"), hs); row.append(l);
    }
    list.append(row);
  });
  const cl = $("physCols"); cl.innerHTML = "";
  if ((cfg.colliders || []).length) {
    cl.append(mkEl("span", "", "Vùng chắn:")); cl.lastChild.style.background = "none"; cl.lastChild.style.color = "var(--muted)";
    cfg.colliders.forEach((c, i) => {
      const sp = mkEl("span", "", physName(c.bone)), x = mkEl("button", "pX", "×"); x.title = "Bỏ vùng chắn";
      x.onclick = () => { ANIM.phys.colliders = (ANIM.phys.colliders || []).filter(x2 => x2 !== c && x2.bone !== c.bone); propPts = {}; physChanged(true); };
      sp.append(x); cl.append(sp);
    });
  }
  physInfo(); drawPhysGraph(); renderImpacts(); ragLen(); renderRag();
}
$("physOn").onclick = () => { ANIM.phys.on = !ANIM.phys.on; physChanged(true); };
$("physChar").onclick = () => {
  const c = charPhys(); if (!c) return;
  ANIM.phys = { ...physDefault(), ...JSON.parse(JSON.stringify(c)), on: true, pin: ANIM.phys.pin || "", impacts: ANIM.phys.impacts || [], autoStep: ANIM.phys.autoStep !== false, rag: ANIM.phys.rag }; PINS = parseSet(ANIM.phys.pin); propPts = {};
  physSel = 0; physChanged(true); $("p_status").textContent = "Đã dùng bộ lò xo của nhân vật: " + ANIM.phys.parts.map(p => physName(p.bone)).join(", ") + ".";
};
$("physAdd").onclick = () => {
  if (!sel) { $("p_status").textContent = "Chọn một khớp trên model trước."; return; }
  const cfg = ANIM.phys, i = cfg.parts.findIndex(p => p.bone === sel);
  if (i >= 0) { physSel = i; renderPhys(); return; }
  cfg.parts.push(guessPart(sel)); cfg.on = true; physSel = cfg.parts.length - 1; physChanged(true);
};
$("physColAdd").onclick = () => {
  if (!sel) { $("p_status").textContent = "Chọn khớp làm vùng chắn trước (vd vai đỡ vũ khí)."; return; }
  const cfg = ANIM.phys; cfg.colliders = cfg.colliders || [];
  if (!cfg.colliders.some(c => c.bone === sel)) cfg.colliders.push({ bone: sel });
  physChanged(true);
};
$("physEnd").onchange = () => { ANIM.phys.end = Math.max(0, Math.min(30, Math.round(+$("physEnd").value || 0))); physChanged(); };
// Bake keeps the keys it replaced until the clip changes: the button then reads "Hoàn tác bake" (Ctrl+Z history is
// cleared on every frame change, so it cannot be the way back)
let bakeUndo = null;
$("physBake").onclick = () => {
  stopPlay();
  if (bakeUndo && !ANIM.phys.on) {
    const at = new Date().toISOString();
    for (const f of new Set([...KEYS.keys(), ...bakeUndo.keys.keys()])) dirtyKeys.add(f);
    KEYS = new Map([...bakeUndo.keys].map(([f, k]) => [f, { ...k, at }])); ANIM.phys = bakeUndo.phys; ANIM.interp = bakeUndo.interp;
    PINS = parseSet(ANIM.phys.pin); bakeUndo = null; keysChanged(); setAnim({}); renderPhys(); reEval();
    $("p_status").textContent = "Đã trả lại key trước khi bake và bật lại vật lý."; return;
  }
  if (!physOn()) return;
  if (physDirty) computePhys(); if (!PHYS) return;
  bakeUndo = { keys: new Map(KEYS), phys: JSON.parse(JSON.stringify(ANIM.phys)), interp: ANIM.interp };
  const last = P.loop ? PER() : NFR(), at = new Date().toISOString();
  for (let f = 1; f <= last; f++) if (PHYS.out[f]) { KEYS.set(f, { pose: PHYS.out[f], at }); dirtyKeys.add(f); }
  ANIM.phys.on = false; PHYS = null; keysChanged(); setAnim({ interp: "spline" }); renderPhys();
  $("p_status").textContent = "Đã bake " + last + " frame thành key và tắt vật lý. Bấm \"Hoàn tác bake\" để lấy lại key cũ.";
};
function physSeries() {             // speeds (deg/F) of the selected part: with physics, and the key pose alone
  if (!PHYS || !PHYS.series[physSel]) return null;
  const sr = PHYS.series[physSel], n = NFR(), deg = THREE.MathUtils.radToDeg;
  const vo = [null], o = [null], b = [null];
  for (let f = 2; f <= n; f++) {
    const v = sr.out[f] && sr.out[f - 1] ? rvec(sr.out[f - 1], sr.out[f]) : null; vo.push(v); o.push(v ? deg(v.length()) : null);
    b.push(sr.base[f] && sr.base[f - 1] ? deg(rvec(sr.base[f - 1], sr.base[f]).length()) : null);
  }
  // flags of a speed series: stop-go = a dip under half of both neighbours (> 1 deg/F) WITHOUT a change of direction (a
  // swing turning back is not stop-go); jitter = the turn flips direction two frames in a row. Only flags that the
  // physics ADDS are shown (the key pose's own are not the physics' fault).
  const flags = (sp, v) => {
    const st = [], jt = [];
    for (let i = 2; i < sp.length - 1; i++) {
      const a = sp[i - 1], c = sp[i + 1];
      if (sp[i] != null && a != null && c != null && Math.min(a, c) > 1 && sp[i] < 0.5 * Math.min(a, c) && v[i - 1] && v[i + 1] && v[i - 1].dot(v[i + 1]) > 0) st.push(i + 1);
    }
    for (let i = 1; i < v.length - 2; i++) {
      const [a, b2, c] = [v[i], v[i + 1], v[i + 2]];
      if (a && b2 && c && a.length() > 0.005 && b2.length() > 0.005 && c.length() > 0.005 && a.dot(b2) < 0 && b2.dot(c) < 0) jt.push(i + 2);
    }
    return [st, jt];
  };
  const vb = [null]; for (let f = 2; f <= n; f++) vb.push(sr.base[f] && sr.base[f - 1] ? rvec(sr.base[f - 1], sr.base[f]) : null);
  const [so, jo] = flags(o, vo), [sb, jb] = flags(b, vb), near = (f, arr) => arr.some(x => Math.abs(x - f) <= 1);
  const hitF = [...sr.contact];          // a bounce off a contact (floor, body) is not jitter
  const stop = so.filter(f => !near(f, sb)), jit = jo.filter(f => !near(f, jb) && !near(f, hitF));
  return { o, b, stop, jit, sr };
}
function drawPhysGraph() {
  const cv = $("physGraph"); if (!cv || $("physBox").hidden) return;
  const g = cv.getContext("2d"), W = cv.width, H = cv.height, n = NFR(); g.clearRect(0, 0, W, H);
  const s = physOn() && !physDirty ? physSeries() : null; g.font = "20px " + css("--font-num");
  if (!s) { g.fillStyle = css("--muted"); g.fillText(physOn() ? "Chọn một phần để xem đồ thị" : "Bật vật lý để xem đồ thị", 14, H / 2); return; }
  // o[i] / b[i] = speed from frame i+1 to i+2 ... index i is the move INTO frame i+1
  const vals = [...s.o, ...s.b].filter(v => v != null), top = Math.max(2, ...vals) * 1.1;
  const X = f => 10 + (f - 1) / Math.max(1, n - 1) * (W - 20), Y = v => H - 22 - v / top * (H - 44);
  g.fillStyle = "#1fa37a33"; g.fillRect(X(frame) - 3, 0, 6, H);
  if (s.sr.contact.size) { g.fillStyle = "#5aa9ff26"; const cw = (W - 20) / Math.max(1, n - 1); for (const f of s.sr.contact) g.fillRect(X(f) - cw / 2, 0, cw, H - 22); }
  for (const [arr, col, w] of [[s.b, "#8b93a1", 2], [s.o, css("--accent"), 3.5]]) {
    g.strokeStyle = col; g.lineWidth = w; g.beginPath(); let pen = false;
    arr.forEach((v, i) => { if (v == null) { pen = false; return; } const x = X(i + 1), y = Y(v); pen ? g.lineTo(x, y) : g.moveTo(x, y); pen = true; });
    g.stroke();
  }
  g.fillStyle = css("--edit"); for (const f of [...s.stop, ...s.jit]) { g.beginPath(); g.arc(X(f), Y(s.o[f - 1] || 0), 6, 0, 7); g.fill(); }
  g.fillStyle = css("--muted"); g.fillText(top.toFixed(1) + "°/F", 12, 22); g.fillText("F1", 10, H - 2); g.fillText("F" + n, W - 56, H - 2);
}
function physInfo() {
  const el = $("physInfo"); if (!el) return; el.innerHTML = "";
  if (!physOn()) { el.textContent = ANIM.phys && ANIM.phys.parts.length ? "Vật lý đang tắt: model hiện đúng pose key." : ""; return; }
  if (physDirty) return;
  const s = physSeries(); if (!PHYS) return;
  const add = (t, b) => { const sp = mkEl("span", "", t); if (b) sp.append(mkEl("b", "", b)); el.append(sp); };
  add("Tính " + NFR() + " frame trong " + Math.round(PHYS.ms) + " ms. ");
  if (s) {
    const pb = PHYS.parts[physSel].bone, pk = THREE.MathUtils.radToDeg(s.sr.peak);
    add(physName(pb) + ": lệch tối đa ", pk.toFixed(1) + "° (F" + s.sr.peakF + ")"); add(". ");
    if (s.sr.contact.size) add("Chạm vùng chắn F" + fmtSet(s.sr.contact) + ". ");
    if (s.stop.length || s.jit.length) add("Cần xem: ", [s.stop.length ? "dừng-rồi-chạy F" + s.stop.join(", F") : "", s.jit.length ? "rung F" + s.jit.join(", F") : ""].filter(Boolean).join("; "));
    else add("Không có dừng-rồi-chạy, không rung.");
  }
  add(" Đồ thị: xanh = có vật lý, xám = pose key.");
}
// ---------------------------------------------------------------- motion trail (user 2026-10-26: "bật motion trail của 1 joint để
// check xem nó được làm mềm như nào"). The selected joint's world path over the whole clip: cyan = what is shown (keys +
// physics / AutoPhysics) in cyan (orange mixed with the joint dots and the red body), dashed grey = the key pose (the ghost). One dot per frame (spacing = speed), big dot = this frame.
// Rebuilt only when the joint, the keys or the physics result change; numbers in the HUD tag.
let trailOn = false, trailSig = "", trailGrp = null, trailData = null;
function trailClear() { if (trailGrp) { scene.remove(trailGrp); trailGrp.traverse(o => { if (o.geometry) o.geometry.dispose(); if (o.material) o.material.dispose(); }); trailGrp = null; } trailData = null; $("trailTag").hidden = true; }
function trailSample(n) {
  const f0 = frame, cur = [], key = []; stashDraft();
  for (let f = 1; f <= NFR(); f++) { sampleAt(f); model.updateMatrixWorld(true); if (ghost) ghost.updateMatrixWorld(true); cur.push(wp(B[n])); key.push(gB[n] ? wp(gB[n]) : null); }
  goto(f0, true); return { cur, key };
}
function trailStats(pts) {                 // speed cm/F, the sharpest turn and the biggest change of speed
  let vmax = 0, vAt = 1, turn = 0, tAt = 0, jerk = 0, jAt = 0; const v = [];
  for (let i = 1; i < pts.length; i++) v.push(pts[i].clone().sub(pts[i - 1]));
  v.forEach((d, i) => { const sp = d.length() / CM_W; if (sp > vmax) { vmax = sp; vAt = i + 2; } });
  for (let i = 1; i < v.length; i++) { const a = v[i - 1], b = v[i], la = a.length() / CM_W, lb = b.length() / CM_W;
    if (la > 0.8 && lb > 0.8) { const t = THREE.MathUtils.radToDeg(a.angleTo(b)); if (t > turn) { turn = t; tAt = i + 1; } }
    const j = b.clone().sub(a).length() / CM_W; if (j > jerk) { jerk = j; jAt = i + 1; } }
  return { vmax, vAt, turn, tAt, jerk, jAt };
}
function trailUpdate() {
  const n = sel && B[sel] ? sel : null, tag = $("trailTag");
  if (!n) { if (trailGrp) trailClear(); tag.hidden = false; tag.textContent = "Quỹ đạo: chọn một khớp"; trailSig = ""; return; }
  if (gizmo.dragging) return;
  const sig = [P.version, n, keySig, physDirty ? "d" : "", PHYS ? PHYS.ms + ":" + Object.keys(PHYS.out || {}).length : "-", physOn() ? 1 : 0, NFR()].join("|");
  if (sig !== trailSig) {
    trailSig = sig; trailClear(); trailData = trailSample(n); trailData.n = n;
    const same = trailData.key.every((k, i) => !k || k.distanceTo(trailData.cur[i]) < 0.1 * CM_W);
    trailGrp = new THREE.Group(); trailGrp.renderOrder = 10;
    const line = (pts, mat) => { const g = new THREE.BufferGeometry().setFromPoints(pts); const l = new THREE.Line(g, mat); l.renderOrder = 10; if (mat.isLineDashedMaterial) l.computeLineDistances(); return l; };
    const dots = (pts, color, size) => { const g = new THREE.BufferGeometry().setFromPoints(pts); const m = new THREE.Points(g, new THREE.PointsMaterial({ color, size, sizeAttenuation: false, depthTest: false, transparent: true, opacity: .95 })); m.renderOrder = 11; return m; };
    if (!same) { const kp = trailData.key.filter(Boolean); trailGrp.add(line(kp, new THREE.LineDashedMaterial({ color: 0xaab3c0, dashSize: 0.03, gapSize: 0.025, depthTest: false, transparent: true, opacity: .8 }))); trailGrp.add(dots(kp, 0xaab3c0, 3)); }
    trailGrp.add(line(trailData.cur, new THREE.LineBasicMaterial({ color: 0x38d6ff, depthTest: false, transparent: true, opacity: .95 })));
    trailGrp.add(dots(trailData.cur, 0x38d6ff, 5));
    const nowG = new THREE.BufferGeometry().setFromPoints([trailData.cur[0]]); trailData.now = new THREE.Points(nowG, new THREE.PointsMaterial({ color: 0xffffff, size: 11, sizeAttenuation: false, depthTest: false })); trailData.now.renderOrder = 12; trailGrp.add(trailData.now);
    scene.add(trailGrp);
    const st = trailStats(trailData.cur), sk = same ? null : trailStats(trailData.key.filter(Boolean)); let dev = 0, dAt = 1;
    if (!same) trailData.key.forEach((k, i) => { if (!k) return; const d = k.distanceTo(trailData.cur[i]) / CM_W; if (d > dev) { dev = d; dAt = i + 1; } });
    const r1 = x => (Math.round(x * 10) / 10).toString().replace(".", ",");
    trailData.text = "Quỹ đạo " + (NAMES[n] || physName(n)) + ": nhanh nhất " + r1(st.vmax) + " cm/F (F" + st.vAt + ")" + (st.turn > 1 ? ", đổi hướng gắt nhất " + Math.round(st.turn) + "° (F" + st.tAt + ")" : "") + ", đổi tốc lớn nhất " + r1(st.jerk) + " cm/F (F" + st.jAt + ")"
      + (same ? " · trùng pose key (vật lý / AutoPhysics không đổi khớp này)" : " · key: nhanh nhất " + r1(sk.vmax) + ", đổi hướng " + Math.round(sk.turn) + "°, đổi tốc " + r1(sk.jerk) + " · lệch key tối đa " + r1(dev) + " cm (F" + dAt + ")");
  }
  if (trailData) { const p = trailData.cur[Math.max(0, Math.min(trailData.cur.length - 1, frame - 1))]; const a = trailData.now.geometry.attributes.position; a.setXYZ(0, p.x, p.y, p.z); a.needsUpdate = true; tag.hidden = false; tag.textContent = trailData.text; }
}
host.onFrame(now => { tickPlay(now || performance.now()); if (model) placeMarkers(); if (model && trailOn) trailUpdate(); if (model && stripSigNow() !== stripSig) renderStrip(); });
// góc camera đã lưu (Studio, host.savedView): dùng lại thay cho góc Right mặc định, kể cả khi model nạp xong
let camInit = false;
{ const sv = host.savedView ? host.savedView() : null;
  if (sv && host.applyView && host.applyView(sv)) { camInit = true; const k = sv.cam; curCam = k && CAMS[k] ? k : "persp";
    $("camTag").innerHTML = "Camera: <b></b>"; $("camTag").querySelector("b").textContent = k && CAMS[k] ? CAMS[k].label : "persp (tự do)";
    document.querySelectorAll(".cams button").forEach(b => b.classList.toggle("on", b.dataset.cam === k)); }
  else setCam("right"); }
renderPoses(); openPose(POSES[0]);

(async () => {
  const hasClaude = !!(window.claude && window.claude.use);
  let d = null, u = null, cm = null;
  if (hasClaude) [d, u, cm] = await Promise.all([claude.use("db"), claude.use("user"), claude.use("comments")]);
  d = host.db;
  db = d; user = u; comments = cm;

  if (!db) {
    if (!hasClaude) { $("p_status").textContent = "Đây là bản chạy thử trên máy: nút Lưu sẽ tải file .json. Mở Home (tools/home) để lưu vào dự án, hoặc mở trang trên claude.ai."; return; }
    $("p_status").textContent = "Đăng nhập claude.ai để lưu điều chỉnh. Bạn vẫn chỉnh thử được trên model."; refresh(); return;
  }
  if (user) { myId = await user.id().catch(() => null); if ((await user.can("data.write").catch(() => null)) === false) canWrite = false; }
  if (!canWrite) $("p_status").textContent = "Bạn đang ở quyền chỉ xem: chỉnh thử được nhưng không lưu được.";
  db.collection("adjusts").onSnapshot(snap => { adjs = snap.docs.filter(s => s.exists).map(s => ({ id: s.id, ...s.data() })); renderAdjs(); renderRound(); renderPoses(); refresh(); });
  db.collection("rounds").onSnapshot(snap => { rounds = {}; snap.docs.filter(s => s.exists).forEach(s => rounds[s.id] = s.data()); renderRound(); renderPoses(); });
  db.collection("settings").onSnapshot(snap => { const d = snap.docs.find(s => s.exists && s.id === "aiself"); if (!d) return; const v = d.data();
    AIS.on = !!v.on; AIS.rounds = v.rounds || 2; $("asOn").checked = AIS.on; $("asRounds").value = String(AIS.rounds); maybeAutoReview(); });
  db.collection("selfplan").onSnapshot(snap => { const d = snap.docs.find(s => s.exists && s.id === planId()); AIS.plan = d ? d.data() : null; maybeAutoReview(); });
  db.collection("keys").onSnapshot(snap => {
    remoteKeys = {};
    snap.docs.filter(s => s.exists).forEach(s => { const d = s.data(); if (d && d.clip && d.frame) (remoteKeys[idOf(d.clip, d.version)] ||= {})[d.frame] = d; });
    applyRemote();
  });
  db.collection("anims").onSnapshot(snap => {
    remoteAnims = {}; snap.docs.filter(s => s.exists).forEach(s => { const d = s.data(); if (d && d.clip) remoteAnims[idOf(d.clip, d.version)] = d; });
    applyRemote();
  });
  refresh();
})();


/* UI layer: every button is an icon. The label text stays in the DOM (hidden), so existing code that sets
   textContent keeps working; here it becomes the tooltip + aria-label, and ": bật / : tắt" becomes a state. */
(function () {
  const sel = ".ibtn", T0 = "t0";
  function label(b) { const c = b.cloneNode(true); c.querySelectorAll("kbd").forEach(k => k.remove()); return c.textContent.replace(/\s+/g, " ").trim(); }
  function sync(b) {
    const t = label(b); if (b.dataset[T0] === undefined) b.dataset[T0] = b.getAttribute("title") || "";
    const dyn = /:|^(Dừng|Phát|Bậc thang|Spline)$/.test(t), t0 = b.dataset[T0];
    const tip = dyn ? (t + (t0 ? " - " + t0 : "")) : (t0 || t);
    if (b.title !== tip) b.title = tip;
    if (t) b.setAttribute("aria-label", t);
    const st = /(:\s*bật|world|^Dừng$|^Bậc thang$)/i.test(t) ? "on" : (/:\s*tắt/.test(t) ? "off" : "");
    if (b.dataset.state !== st) b.dataset.state = st;
  }
  const mo = new MutationObserver(ms => { const seen = new Set(); ms.forEach(m => { const b = (m.target.nodeType === 3 ? m.target.parentElement : m.target).closest(sel); if (b && !seen.has(b)) { seen.add(b); sync(b); } }); });
  document.querySelectorAll(sel).forEach(b => { sync(b); mo.observe(b, { childList: true, characterData: true, subtree: true }); });
  document.querySelectorAll(".cams button").forEach(b => { b.setAttribute("aria-label", b.textContent.trim()); b.title = b.textContent.trim() + (b.title ? " (" + b.title + ")" : ""); });
  document.querySelectorAll(".legend span").forEach(sp => { if (sp.textContent.trim()) sp.title = sp.textContent.trim(); });
  /* physics sections fold; the open/closed choice is remembered */
  const store = { get: k => { try { return localStorage.getItem(k); } catch (e) { return null; } }, set: (k, v) => { try { localStorage.setItem(k, v); } catch (e) {} } };
  document.querySelectorAll(".pbody > h3").forEach(h => {
    const key = "plsec:" + h.textContent.trim(), sec = document.createElement("div"); sec.className = "sec";
    let n = h.nextSibling; while (n && !(n.nodeType === 1 && n.tagName === "H3")) { const nx = n.nextSibling; sec.appendChild(n); n = nx; }
    h.after(sec); h.classList.add("sech");
    const set = open => { h.classList.toggle("open", open); sec.hidden = !open; };
    set(store.get(key) === "1");
    h.addEventListener("click", () => { const open = sec.hidden; set(open); store.set(key, open ? "1" : "0"); if (open) window.dispatchEvent(new Event("resize")); });
  });
})();

/*PLAYBLAST*/
// góc "Đang xem" (user 2026-10-29 "playblast đưa nhân vật về chính giữa, không lấy được view mong muốn"): chụp camera viewport lúc mở hộp,
// quay đúng góc đó (Gate bật: ô theo tỉ lệ Gate, khung = phần trong Gate), xong / huỷ thì trả viewport về đúng góc cũ
const viewSnap = () => { const c = CAM(); return { ortho: !!c.isOrthographicCamera, pos: c.position.clone(), q: c.quaternion.clone(), up: c.up.clone(), tgt: orbit.target.clone(), zoom: c.zoom, fov: c.fov, cam: curCam, tag: $("camTag").innerHTML }; };
function viewSet(v, frac) {
  if (host.setOrtho) host.setOrtho(v.ortho);
  const c = CAM(); c.up.copy(v.up); c.position.copy(v.pos); c.quaternion.copy(v.q); orbit.target.copy(v.tgt);
  if (c.isOrthographicCamera) c.zoom = v.zoom / (frac || 1);
  else if (v.fov) c.fov = frac ? 2 * THREE.MathUtils.radToDeg(Math.atan(Math.tan(THREE.MathUtils.degToRad(v.fov) / 2) * frac)) : v.fov;
  c.updateProjectionMatrix(); curCam = v.cam; $("camTag").innerHTML = v.tag;
  document.querySelectorAll(".cams button").forEach(b => b.classList.toggle("on", b.dataset.cam === v.cam));
}
const pbGate = () => host.gate ? host.gate() : null;   // { A: rộng/cao, frac: cao Gate / cao khung } hoặc null
const pbLabel = k => k === "view" ? "Đang xem" : CAMS[k].label;
// Quay playblast: mỗi frame goto(f) rồi vẽ N CAM() cạnh nhau (chỉ scene, không overlay) vào canvas ghép, MediaRecorder thu theo nhịp fps.
window.DDC = window.DDC || {};
window.DDC.playblast = async function (opt) {
  opt = opt || {};
  if (!ready || !model) throw new Error("Model chưa tải xong.");
  const cams = opt.cams || ["right", "left", "front", "top"], cw = opt.cw || 450, ch = opt.ch || 600, dist = opt.dist || 1, n = P.frames || 1, fps = P.fps || 30;
  const mime = ["video/webm;codecs=vp9", "video/webm;codecs=vp8", "video/webm"].find(m => window.MediaRecorder && MediaRecorder.isTypeSupported(m));
  if (!mime) throw new Error("Trình duyệt không quay được video (MediaRecorder).");
  const VIEW = opt.view || viewSnap(), G = pbGate();
  const wasFrame = frame, wasCam = curCam, wasGhost = ghost && ghost.visible, wasSize = renderer.getSize(new THREE.Vector2()), prog = opt.onProgress || (() => {});
  const out = document.createElement("canvas"); out.width = cw * cams.length; out.height = ch;
  const ctx = out.getContext("2d"), stream = out.captureStream(0), track = stream.getVideoTracks()[0];
  const rec = new MediaRecorder(stream, { mimeType: mime, videoBitsPerSecond: 8e6 }), chunks = [];
  rec.ondataavailable = e => { if (e.data && e.data.size) chunks.push(e.data); };
  const done = new Promise(r => rec.onstop = r);
  const msg = document.createElement("div"); msg.id = "pbMsg"; $("viewer").appendChild(msg);
  stopPlay(); if (ghost) ghost.visible = false; ONION.off++; goto(frame); gizmo.detach();
  const clear = css("--view") || "#101218", bg = new THREE.Color(0x15181f);
  let thumb = null; const mid = Math.max(1, Math.round(n / 2));
  try {
    rec.start();
    for (let f = 1; f <= n; f++) {
      msg.textContent = "Đang quay playblast " + f + " / " + n; prog(f, n);
      goto(f); model.updateMatrixWorld(true);
      renderer.setSize(cw, ch, false); camAspect(cw / ch);
      ctx.fillStyle = "#15181f"; ctx.fillRect(0, 0, out.width, ch);
      cams.forEach((k, i) => { if (k === "view") viewSet(VIEW, G && G.frac); else { setCam(k); if (dist !== 1) camDolly(dist); } renderer.setClearColor(bg, 1); renderer.clear(); renderer.render(scene, CAM()); ctx.drawImage(renderer.domElement, i * cw, 0, cw, ch); });
      if (f === mid) thumb = await new Promise(r => out.toBlob(r, "image/jpeg", 0.85));
      track.requestFrame();
      await new Promise(r => setTimeout(r, 1000 / fps));
    }
    await new Promise(r => setTimeout(r, 200)); rec.stop(); await done;
  } finally {
    msg.remove(); if (ghost) ghost.visible = wasGhost; ONION.off = Math.max(0, ONION.off - 1); renderer.setSize(wasSize.x, wasSize.y, false); resize(); viewSet(VIEW); goto(wasFrame); renderer.setClearColor(0x000000, 0);
  }
  return { webm: new Blob(chunks, { type: "video/webm" }), thumb, n, fps, w: cw * cams.length, h: ch, views: cams.map(k => pbLabel(k).toLowerCase()).join(" | ") };
};
$("bPB").addEventListener("click", async () => {
  try { const o = await window.DDC.askPlayblast(); if (!o) return; const r = await window.DDC.playblast(o); const u = URL.createObjectURL(r.webm), a = document.createElement("a"); a.href = u; a.download = idOf(P.clip, P.version) + ".webm"; document.body.appendChild(a); a.click(); a.remove(); setTimeout(() => URL.revokeObjectURL(u), 4000); $("p_status").textContent = "Đã quay playblast " + r.n + " frame."; }
  catch (e) { $("p_status").textContent = "Không quay được: " + (e.message || e); }
});

/*PLAYBLAST2*/
// Hộp thoại cài đặt playblast: chọn CAM() (thứ tự ghép = thứ tự tick), cỡ mỗi ô; nhớ lựa chọn trong trình duyệt.
window.DDC.askPlayblast = function () {
  return new Promise(res => {
    let saved = {}; try { saved = JSON.parse(localStorage.getItem("poselab:pb") || "{}"); } catch {}
    const view0 = viewSnap(), G = pbGate(); let dist = saved.dist >= 0.3 && saved.dist <= 3 ? saved.dist : 1;
    const order = ["view", "right", "left", "front", "back", "top", "bottom", "persp"], on = new Set(saved.cams || ["view"]);
    const ev = n => Math.max(2, Math.round(n / 2) * 2), cell = h => G ? [ev(h * G.A), h] : [h * 3 / 4, h];   // Gate bật: ô theo tỉ lệ Gate
    const sizes = { s: [...cell(400), "Nhỏ"], m: [...cell(600), "Vừa"], l: [...cell(800), "Lớn"] }; let sz = saved.size && sizes[saved.size] ? saved.size : "m";
    const back = () => viewSet(view0);
    const ov = document.createElement("div");
    ov.style.cssText = "position:fixed;inset:0;z-index:100;background:#0008;display:flex;align-items:center;justify-content:center;padding:12px";
    ov.innerHTML = '<div style="background:var(--panel,#1a1e26);color:var(--ink,#e6e9ee);border:1px solid var(--line,#2c3441);border-radius:12px;padding:16px;width:min(360px,100%);font:13px/1.45 system-ui,sans-serif">'
      + '<b style="font-size:14px">Quay playblast</b><div style="color:var(--muted,#8d97a8);margin:2px 0 10px">Chọn CAM() ghép thành một hàng trong video (xem trên Review Lab).</div>'
      + '<div id="pbCams" style="display:grid;grid-template-columns:1fr 1fr;gap:6px"></div>'
      + '<div style="margin:12px 0 6px;color:var(--muted,#8d97a8)">Cỡ mỗi ô</div><div id="pbSz" style="display:flex;gap:6px"></div>'
      + '<div style="margin:12px 0 4px;color:var(--muted,#8d97a8);display:flex;justify-content:space-between"><span>Khoảng cách CAM() tới nhân vật</span><b id="pbDv" style="color:var(--ink,#e6e9ee)"></b></div>'
      + '<input id="pbD" type="range" min="0.3" max="2.5" step="0.05" style="width:100%"><div style="display:flex;justify-content:space-between;color:var(--muted,#8d97a8);font-size:11px"><span>Gần</span><span>Xa</span></div>'
      + '<div id="pbInfo" style="margin-top:10px;color:var(--muted,#8d97a8);font-size:12px"></div>'
      + '<div style="display:flex;gap:8px;justify-content:flex-end;margin-top:14px"><button id="pbNo" style="padding:7px 14px;border-radius:8px;border:1px solid var(--line,#2c3441);background:transparent;color:inherit;cursor:pointer">Huỷ</button><button id="pbGo" style="padding:7px 16px;border-radius:8px;border:0;background:var(--accent,#2fb67d);color:#fff;font-weight:600;cursor:pointer">Quay</button></div></div>';
    document.body.appendChild(ov);
    const cams = ov.querySelector("#pbCams"), szb = ov.querySelector("#pbSz"), info = ov.querySelector("#pbInfo"), go = ov.querySelector("#pbGo");
    const dEl = ov.querySelector("#pbD"), dv = ov.querySelector("#pbDv");
    const prev = () => {   // xem thử ngay trên viewport: CAM() đầu tiên đã chọn ("Đang xem" = giữ nguyên góc của người dùng)
      const k = order.find(x => on.has(x)); if (!k || k === "view") return back(); setCam(k); if (dist !== 1) camDolly(dist);
    };
    dEl.value = dist; dv.textContent = "×" + dist.toFixed(2);
    dEl.addEventListener("input", () => { dist = +dEl.value; dv.textContent = "×" + dist.toFixed(2); prev(); });
    const refresh = () => {
      prev();
      cams.innerHTML = order.map(k => `<label style="display:flex;gap:6px;align-items:center;padding:6px 8px;border:1px solid var(--line,#2c3441);border-radius:8px;cursor:pointer;${on.has(k) ? "background:color-mix(in srgb,var(--accent,#2fb67d) 18%,transparent)" : ""}"><input type="checkbox" data-k="${k}" ${on.has(k) ? "checked" : ""}> ${pbLabel(k)}${k === "view" ? ' <small style="color:var(--muted,#8d97a8)">(góc viewport' + (G ? ", khung Gate" : "") + ")</small>" : ""}</label>`).join("");
      szb.innerHTML = Object.entries(sizes).map(([k, v]) => `<button data-s="${k}" style="flex:1;padding:6px;border-radius:8px;border:1px solid var(--line,#2c3441);cursor:pointer;color:inherit;background:${k === sz ? "var(--accent,#2fb67d)" : "transparent"}">${v[2]}<br><small>${v[0]}×${v[1]}</small></button>`).join("");
      const [w, h] = sizes[sz], n = on.size; info.textContent = n ? "Video " + (w * n) + "×" + h + " · " + (P.frames || 1) + " frame · " + (P.fps || 30) + " fps" + (on.has("view") ? (G ? " · ô theo Gate" : " · bật Gate để quay đúng khung") : "") : "Chọn ít nhất một CAM().";
      go.disabled = !n; go.style.opacity = n ? 1 : .5;
    };
    ov.addEventListener("click", e => {
      const c = e.target.closest("input[data-k]"), b = e.target.closest("button[data-s]");
      if (c) { c.checked ? on.add(c.dataset.k) : on.delete(c.dataset.k); refresh(); } else if (b) { sz = b.dataset.s; refresh(); }
      else if (e.target.closest("#pbNo") || e.target === ov) { ov.remove(); back(); res(null); }
      else if (e.target.closest("#pbGo") && on.size) {
        const list = order.filter(k => on.has(k)); try { localStorage.setItem("poselab:pb", JSON.stringify({ cams: list, size: sz, dist })); } catch {}
        ov.remove(); back(); res({ cams: list, cw: sizes[sz][0], ch: sizes[sz][1], dist, view: view0 });
      }
    });
    refresh();
  });
};

function sampleBones(f, names) {
  if (!model) return {};
  const keep = {}, gk = {}; for (const n in B) keep[n] = [B[n].position.clone(), B[n].quaternion.clone()];
  for (const n in gB) gk[n] = [gB[n].position.clone(), gB[n].quaternion.clone()];
  const out = {};
  try {
    sampleAt(Math.max(1, Math.min(P.frames || 1, Math.round(f))));
    if (f === frame && drafts[f]) for (const [n, v] of Object.entries(drafts[f])) { B[n].quaternion.copy(v.q); B[n].position.copy(v.p); }
    model.updateMatrixWorld(true);
    for (const n of names) if (B[n]) { const p = new THREE.Vector3(), q = new THREE.Quaternion(), s = new THREE.Vector3(); B[n].matrixWorld.decompose(p, q, s); out[n] = { p, q }; }
  } finally {
    for (const n in keep) { B[n].position.copy(keep[n][0]); B[n].quaternion.copy(keep[n][1]); }
    for (const n in gk) { gB[n].position.copy(gk[n][0]); gB[n].quaternion.copy(gk[n][1]); }
    model.updateMatrixWorld(true); if (ghost) ghost.updateMatrixWorld(true);
  }
  return out;
}
// ---- API cho cầu nối AI (Studio W2, modules/bridge.js): cùng đường với thao tác trên trang (chọn khớp → sửa → Auto key)
const AI = (() => {
  const r2 = x => +(+x).toFixed(2), need = (c, m) => { if (!c) throw new Error(m); };
  const joint = n => { need(model, "Anim chưa nạp xong"); need(B[n] && markers[n], "Không có khớp " + n + " (khớp có chấm chọn: " + Object.keys(markers).length + ")"); return n; };
  const edit = (n, fn) => {
    joint(n); stopPlay(); if (sel !== n || selSet.size !== 1) select(n); pushUndo();
    fn(); afterEdit(); attachGizmo(); commitEdit(); refresh();
    return { joint: n, frame: cyc(frame), keyed: keysMode() && KEYS.has(cyc(frame)), unkeyed: editedList() };
  };
  const loc = n => { const e = new THREE.Euler().setFromQuaternion(B[n].quaternion, "XYZ"); return [e.x, e.y, e.z].map(v => r2(THREE.MathUtils.radToDeg(v))); };
  const world = n => { const w = n.startsWith("Ankle_") && footT[n.slice(-1)] ? footT[n.slice(-1)] : wp(B[n]); return [w.x * 100, -w.z * 100, w.y * 100].map(r2); };   // cm, trục Blender (Z lên)
  return {
    info: () => ({ clip: P.clip, version: P.version, label: P.label || "", mode: keysMode() ? "keys" : "baked", model: LIVE ? "live" : "snap", frame: cyc(frame), frames: P.frames || 1, loop: !!P.loop, fps: P.fps || 30,
      sel, selSet: [...selSet], playing, autoKey, keys: keysMode() ? [...KEYS.keys()].sort((a, b) => a - b) : [], unkeyed: editedList(), interp: ANIM.interp || "spline" }),
    joints: () => Object.keys(markers).map(n => ({ name: n, label: NAMES[n] || "", parent: (() => { for (let o = B[n].parent; o; o = o.parent) if (markers[o.name]) return o.name; return null; })() })),
    read: names => { const L = names && names.length ? names : (sel ? [...selSet] : Object.keys(markers)); const o = {}; L.forEach(n => { joint(n); o[n] = { rot: loc(n), pos: world(n) }; }); return o; },
    select: names => { (names || []).forEach(joint); stopPlay(); if (!names || !names.length) select(null); else setSelection(names, names[names.length - 1]); return { sel, selSet: [...selSet] }; },
    rot: (n, v, abs) => edit(n, () => {
      if (n === GUN) gunGrab();
      const q = new Q().setFromEuler(new THREE.Euler(...v.map(x => THREE.MathUtils.degToRad(+x || 0)), "XYZ"));
      if (abs) B[n].quaternion.copy(q); else B[n].quaternion.multiply(q);   // xoay thêm quanh trục local của khớp
      model.updateMatrixWorld(true);
    }),
    pos: (n, d) => edit(n, () => { const c = chanPos(n); setPos(n, c.map((x, i) => x + (+d[i] || 0))); }),
    frame: f => { need(model, "Anim chưa nạp xong"); stopPlay(); goto(Math.max(1, Math.min(P.frames || 1, Math.round(+f) || 1))); refresh(); return { frame: cyc(frame) }; },
    play: on => { need(model, "Anim chưa nạp xong"); if (!!on !== playing) $("play").click(); return { playing }; },
    key: () => { need(keysMode(), "Phiên bản " + P.version + " là anim nướng sẵn, không đặt key được: mở phiên bản dạng key"); $("kSet").click(); return { frame: cyc(frame), keys: [...KEYS.keys()].sort((a, b) => a - b) }; },
    unkey: () => { need(keysMode() && KEYS.has(cyc(frame)), "F" + cyc(frame) + " không có key"); $("kDel").click(); return { frame: cyc(frame), keys: [...KEYS.keys()].sort((a, b) => a - b) }; },
    versions: () => POSES.map(p => ({ version: p.version, label: p.label || "", frames: p.frames || 1, mode: p.mode || "baked", date: p.date || "", open: p === P })),
    version: v => { const p = POSES.find(q => q.version === v); need(p, "Không có phiên bản " + v); if (p !== P) { openPose(p); renderPoses(); } return { version: p.version }; },
  };
})();
return { get: () => ({ P, frame, sel, selSet, B, markers, model, playing, mode }), select: n => select(n), setSelection, setMode, goto, undo: () => $("undo").click(),
  canUndo: () => undoStack.length > 0, openPose, reopen: () => openPose(P), isLive: () => !!LIVE, stopPlay, frameAll: typeof frameAll === "function" ? frameAll : null, setCam, NAMES, JOINTS: () => JOINTS,
  sampleBones, ai: AI, renderStrip: () => { if (model) renderStrip(); } };
};
