// Bảng công cụ bên phải: mỗi mục (section.sec) gập / mở bằng cách bấm tiêu đề, nhớ theo trình duyệt.
// Cả bảng bật / tắt bằng nút "Công cụ" ở đầu trang (2026-10-31: UI gọn, bỏ nút thu gọn riêng của bảng).
(() => {
  const wire = () => {
    for (const sec of document.querySelectorAll("#edPanel > .sec")) {
      if (sec.dataset.fold) continue;
      sec.dataset.fold = "1";
      const t = sec.querySelector(":scope > .secT"); if (!t) continue;
      t.title = "Bấm để gập / mở mục này";
      const set = on => { sec.classList.toggle("closed", on); store.set("sec." + sec.id, on ? "1" : "0") };
      t.addEventListener("click", ev => { if (ev.target === t || ev.target.parentElement === t) set(!sec.classList.contains("closed")) });
      sec.classList.toggle("closed", store.get("sec." + sec.id, "0") === "1");
    }
  };
  wire(); setTimeout(wire, 0); setInterval(wire, 2000);   // mục do module nạp sau chèn vào
})();
