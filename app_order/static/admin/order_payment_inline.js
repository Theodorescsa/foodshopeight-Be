(function () {
  const $ = (window.django && django.jQuery) ? django.jQuery : null;

  // ---- helpers ----
  function parseMoney(text) {
    if (typeof text !== 'string') text = String(text ?? '');
    text = text.trim(); if (!text) return 0;
    // "1.234,56" -> 1234.56 ; "1,234.56" -> 1234.56
    if (text.match(/\d\.\d{3}/) && text.includes(',')) {
      return parseFloat(text.replace(/\./g, '').replace(',', '.')) || 0;
    }
    return parseFloat(text.replace(/,/g, '')) || 0;
  }
  const toFixedMoney = (n) => Number(n || 0).toFixed(2);

  function getItemsTotal() {
    let sum = 0;
    document.querySelectorAll('div.inline-group table tr.form-row td.field-total')
      .forEach(td => {
        const el = td.querySelector('p, span, div') || td;
        sum += parseMoney(el.textContent || el.value || '0');
      });
    return sum;
  }

  function paymentAmountInputs() {
    // HỖ TRỢ CẢ 2 PREFIX: payments- và payment_set-
    return Array.from(document.querySelectorAll(
      'input[name^="payments-"][name$="-amount"], input[name^="payment_set-"][name$="-amount"]'
    ));
  }

  function remainingToPay() {
    const itemsTotal = getItemsTotal();
    const paid = paymentAmountInputs().reduce((s, i) => s + parseMoney(i.value || '0'), 0);
    return Math.max(itemsTotal - paid, 0);
  }

  function fillIntoInput(inp) {
    if (!inp) return;
    const val = remainingToPay();
    inp.value = toFixedMoney(val);                    // 1234.56 để DecimalField nuốt chắc
    inp.dispatchEvent(new Event('change', { bubbles: true }));
  }

  function autoFillPayments() {
    const inputs = paymentAmountInputs();
    if (inputs.length === 0) return;
    const target = inputs.find(i => !i.value || parseMoney(i.value) === 0);
    if (target) setTimeout(() => fillIntoInput(target), 50);
  }

  function bindItemChangeHandlers() {
    document.querySelectorAll('select[name$="-menu_item"], input[name$="-quantity"]').forEach(el => {
      if (el.__bound) return;
      el.addEventListener('change', () => setTimeout(autoFillPayments, 60));
      el.addEventListener('input',  () => setTimeout(autoFillPayments, 60));
      el.__bound = true;
    });
  }

  function bindInlineAdded() {
    if ($) {
      // Django admin jQuery event khi thêm 1 inline row
      $(document).on('formset:added', function (event, $row, prefix) {
        const pref = String(prefix || '');
        // Nếu thêm Payment → fill ngay số tiền cho dòng mới
        if (pref.startsWith('payments') || pref.startsWith('payment_set')) {
          const inp = $row[0].querySelector('input[name$="-amount"]');
          if (inp && (!inp.value || parseMoney(inp.value) === 0)) {
            setTimeout(() => fillIntoInput(inp), 60);
          }
        }
        // Nếu thêm OrderItem → rebind và tính lại tổng rồi fill payment
        if (pref.startsWith('orderitem') || pref.includes('items')) {
          bindItemChangeHandlers();
          setTimeout(autoFillPayments, 120);
        }
      });
    } else {
      // Fallback nếu thiếu jQuery: quan sát DOM
      const mo = new MutationObserver(muts => {
        muts.forEach(m => m.addedNodes.forEach(node => {
          if (!(node instanceof HTMLElement)) return;
          // Payment row mới
          if (node.matches('tr.form-row') &&
              node.querySelector('input[name$="-amount"]') &&
             (node.querySelector('input[name^="payments-"]') ||
              node.querySelector('input[name^="payment_set-"]'))) {
            const inp = node.querySelector('input[name$="-amount"]');
            if (inp && (!inp.value || parseMoney(inp.value) === 0)) {
              setTimeout(() => fillIntoInput(inp), 60);
            }
          }
        }));
      });
      mo.observe(document.body, { childList: true, subtree: true });
    }
  }

  function bindTabSwitchFill() {
    // khi chuyển sang tab "Thanh toán" thì fill lại (Jazzmin dùng .nav-link)
    document.querySelectorAll('.nav-link, a[data-toggle="tab"]').forEach(a => {
      if (a.__boundTab) return;
      a.addEventListener('click', () => setTimeout(autoFillPayments, 120));
      a.__boundTab = true;
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    bindItemChangeHandlers();
    bindInlineAdded();
    bindTabSwitchFill();
    // fill lần đầu khi mở form
    setTimeout(autoFillPayments, 150);
  });
})();
