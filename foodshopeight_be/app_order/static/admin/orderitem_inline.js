(function () {
  // ---- helper ----
  function fmtMoney(n) {
    const x = Number(n || 0);
    // Hiển thị kiểu vi-VN (dùng dấu phẩy)
    return x.toLocaleString('vi-VN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  }

  function getMenuPriceUrl() {
    // Luôn cắt tới /admin/app_order/order/
    const p = window.location.pathname;
    const marker = '/admin/app_order/order/';
    const idx = p.indexOf(marker);
    if (idx === -1) return null;
    const base = p.slice(0, idx + marker.length); // …/admin/app_order/order/
    return base + 'menu-price/';
  }

  async function fetchPrice(menuId) {
    if (!menuId) return 0;
    const base = getMenuPriceUrl();
    if (!base) return 0;

    const url = base + '?id=' + encodeURIComponent(menuId);
    try {
      const res = await fetch(url, { credentials: 'same-origin' });
      const data = await res.json();
      return parseFloat(data.price || 0);
    } catch (e) {
      console.warn('fetchPrice error', e);
      return 0;
    }
  }

  async function recalcRow(row) {
    // TabularInline (Jazzmin): mỗi dòng là <tr class="form-row">
    // Lấy theo name để tránh phụ thuộc id
    const select = row.querySelector('select[name$="-menu_item"]');
    const qtyInput = row.querySelector('input[name$="-quantity"]');
    const totalCell = row.querySelector('td.field-total'); // readonly cell

    if (!select || !qtyInput || !totalCell) return;

    const menuId = select.value;
    const qty = parseFloat(qtyInput.value || '0');

    if (!menuId || !qty) {
      writeTotal(totalCell, 0);
      return;
    }

    const price = await fetchPrice(menuId);
    writeTotal(totalCell, price * qty);
  }

  function writeTotal(totalCell, value) {
    // Django thường render <td class="field-total readonly"><p>0,00</p></td>
    const holder = totalCell.querySelector('p, div, span') || totalCell;
    holder.textContent = fmtMoney(value);
  }

  function bindRow(row) {
    const select = row.querySelector('select[name$="-menu_item"]');
    const qtyInput = row.querySelector('input[name$="-quantity"]');
    if (!select || !qtyInput) return;

    // thay đổi món → tính lại
    select.addEventListener('change', () => recalcRow(row));
    // nhập số lượng → tính lại liên tục
    qtyInput.addEventListener('input', () => recalcRow(row));

    // tính lần đầu nếu đã có dữ liệu sẵn
    recalcRow(row);
  }

  function scanAndBind() {
    // Tất cả dòng trong inline tabular
    document.querySelectorAll('div.inline-group table tr.form-row').forEach(bindRow);
  }

  function init() {
    scanAndBind();

    // Khi ấn "Thêm một Mặt hàng" → DOM thêm hàng mới
    // Nút thường có .add-row trong Django admin
    document.body.addEventListener('click', function (e) {
      const target = e.target.closest('.add-row');
      if (target) {
        // chờ DOM add xong
        setTimeout(() => scanAndBind(), 50);
      }
    });

    // Nếu Jazzmin/django thêm hàng qua sự kiện custom, vẫn có scan định kỳ rất nhẹ
    let lastCount = 0;
    setInterval(() => {
      const rows = document.querySelectorAll('div.inline-group table tr.form-row').length;
      if (rows !== lastCount) {
        lastCount = rows;
        scanAndBind();
      }
    }, 500);
  }

  document.addEventListener('DOMContentLoaded', init);
})();
