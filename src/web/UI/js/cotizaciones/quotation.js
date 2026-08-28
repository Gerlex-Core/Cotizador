/**
 * Package: cotizaciones/quotation.js
 * Logic for Product & Service rows, Quotation payload creation, PDF export, currency & TC management, and sanitization.
 */

function generateQuotationNumber() {
    const now = new Date();
    const docTypeEl = document.getElementById('docTypeSelect');
    if (!docTypeEl) return;
    const docType = docTypeEl.value;
    const prefix = docType === 'Cotizacion' ? 'COT' : 'REC';
    const dateStr = now.getFullYear().toString() +
                    String(now.getMonth() + 1).padStart(2, '0') +
                    String(now.getDate()).padStart(2, '0');
    const timeStr = String(now.getHours()).padStart(2, '0') + String(now.getMinutes()).padStart(2, '0');
    const input = document.getElementById('quotationNumberInput');
    if (input) input.value = `${prefix}-${dateStr}-${timeStr}`;
}

function setCurrentDate() {
    const now = new Date();
    const formatted = String(now.getDate()).padStart(2, '0') + '/' +
                      String(now.getMonth() + 1).padStart(2, '0') + '/' +
                      now.getFullYear();
    const input = document.getElementById('dateInput');
    if (input) input.value = formatted;
}

async function fetchBcbExchangeRate() {
    try {
        const res = await fetch((window.ENV?.API_BASE_URL || '') + '/api/bcb/exchange-rate');
        if (res.ok) {
            const data = await res.json();
            if (data.exchange_rate) {
                const tcInput = document.getElementById('exchangeRateInput');
                if (tcInput) {
                    tcInput.value = data.exchange_rate;
                    calculateTotals();
                }
                const dateInfo = data.date ? ` (${data.date})` : '';
                alert(`Tipo de Cambio Oficial obtenido desde el BCB (bcb.gob.bo): 1 USD = ${data.exchange_rate} Bs${dateInfo}`);
            }
        }
    } catch (e) {
        console.warn("[BCB FETCH ERROR]", e);
    }
}

function onDocTypeChanged() {
    generateQuotationNumber();
}

function onCurrencyChanged() {
    const select = document.getElementById('currencySelect');
    if (select) currentCurrency = select.value;
    calculateTotals();
}

function addProductRow(desc = "", qty = 1, unit = "unidad (u)", price = 0) {
    addProductRowWithData({
        description: desc,
        brand: '',
        sku: '',
        quantity: qty,
        unit: unit,
        price: price,
        discount_percent: 0,
        item_warranty: ''
    });
}

function addProductRowWithData(data = {}) {
    productRowCounter++;
    const rowId = `row_${productRowCounter}`;
    const tbody = document.getElementById('productsTbody');
    if (!tbody) return;

    const desc = data.description || '';
    const brand = data.brand || '';
    const sku = data.sku || '';
    const warranty = data.item_warranty || data.warranty || '';
    const qty = data.quantity || 1;
    const unit = data.unit || 'unidad (u)';
    const price = data.price || 0;
    const disc = data.discount_percent || 0;

    const tr = document.createElement('tr');
    tr.id = rowId;
    tr.className = "hover:bg-white/[0.02] transition";

    let unitOptionsHtml = '';
    if (Object.keys(availableUnits).length > 0) {
        for (const [category, units] of Object.entries(availableUnits)) {
            unitOptionsHtml += `<optgroup label="${category.toUpperCase()}">`;
            units.forEach(u => {
                const selected = u === unit ? 'selected' : '';
                unitOptionsHtml += `<option value="${u}" ${selected}>${u}</option>`;
            });
            unitOptionsHtml += `</optgroup>`;
        }
    } else {
        unitOptionsHtml = `<option value="unidad (u)">unidad (u)</option><option value="pieza (pz)">pieza (pz)</option><option value="servicio (srv)">servicio (srv)</option>`;
    }

    tr.innerHTML = `
        <td class="p-3 text-center text-[var(--text-secondary)] font-mono row-index">${tbody.children.length + 1}</td>
        <td class="p-3">
            <input type="text" value="${escapeHtml(desc)}" placeholder="Descripción del producto o servicio..." class="prod-desc w-full bg-[var(--bg-primary)] border border-[var(--border-default)] rounded-xl px-3 py-1.5 text-[var(--text-primary)] focus:border-[var(--border-focus)] focus:outline-none">
        </td>
        <td class="p-3">
            <div class="flex flex-col space-y-1">
                <input type="text" value="${escapeHtml(brand)}" placeholder="Marca..." class="prod-brand w-full bg-[var(--bg-primary)] border border-[var(--border-default)] rounded-lg px-2 py-1 text-[11px] text-[var(--text-primary)]">
                <input type="text" value="${escapeHtml(sku)}" placeholder="SKU/Código..." class="prod-sku w-full bg-[var(--bg-primary)] border border-[var(--border-default)] rounded-lg px-2 py-1 text-[10px] text-[var(--text-secondary)] font-mono">
            </div>
        </td>
        <td class="p-3">
            <input type="text" value="${escapeHtml(warranty)}" placeholder="Garantía..." class="prod-warranty w-full bg-[var(--bg-primary)] border border-[var(--border-default)] rounded-xl px-2 py-1.5 text-[11px] text-[var(--text-primary)] font-semibold">
        </td>
        <td class="p-3">
            <input type="number" value="${qty}" min="0.01" step="1" oninput="calculateTotals()" class="prod-qty w-full bg-[var(--bg-primary)] border border-[var(--border-default)] rounded-xl px-2 py-1.5 text-center text-[var(--text-primary)] font-bold focus:border-[var(--border-focus)] focus:outline-none">
        </td>
        <td class="p-3">
            <select class="prod-unit w-full bg-[var(--bg-primary)] border border-[var(--border-default)] rounded-xl px-2 py-1.5 text-[var(--text-primary)] focus:border-[var(--border-focus)] focus:outline-none">
                ${unitOptionsHtml}
            </select>
        </td>
        <td class="p-3">
            <input type="number" value="${price}" min="0" step="0.5" oninput="calculateTotals()" class="prod-price w-full bg-[var(--bg-primary)] border border-[var(--border-default)] rounded-xl px-3 py-1.5 text-right text-[var(--text-primary)] font-bold focus:border-[var(--border-focus)] focus:outline-none">
        </td>
        <td class="p-3">
            <input type="number" value="${disc}" min="0" max="100" step="1" oninput="calculateTotals()" placeholder="0" class="prod-discount w-full bg-[var(--bg-primary)] border border-[var(--border-default)] rounded-xl px-2 py-1.5 text-center text-[var(--text-primary)] focus:border-[var(--border-focus)] focus:outline-none">
        </td>
        <td class="p-3 text-right font-extrabold text-[var(--text-primary)] prod-amount">
            0.00
        </td>
        <td class="p-3 text-center space-x-1">
            <button onclick="openDigiUpdateModal('${rowId}')" title="Actualizar desde Digicorp" class="p-1 bg-amber-500/20 hover:bg-amber-500/30 rounded-lg text-amber-400 transition">
                <span class="material-symbols-outlined text-sm">content_paste_search</span>
            </button>
            <button onclick="moveRowUp('${rowId}')" title="Subir Fila" class="p-1 bg-[var(--bg-secondary)] hover:bg-white/10 rounded-lg text-[var(--text-primary)] transition">
                <span class="material-symbols-outlined text-sm">arrow_upward</span>
            </button>
            <button onclick="moveRowDown('${rowId}')" title="Bajar Fila" class="p-1 bg-[var(--bg-secondary)] hover:bg-white/10 rounded-lg text-[var(--text-primary)] transition">
                <span class="material-symbols-outlined text-sm">arrow_downward</span>
            </button>
            <button onclick="duplicateRow('${rowId}')" title="Duplicar" class="p-1 bg-[var(--bg-secondary)] hover:bg-white/10 rounded-lg text-[var(--text-primary)] transition">
                <span class="material-symbols-outlined text-sm">content_copy</span>
            </button>
            <button onclick="removeRow('${rowId}')" title="Eliminar" class="p-1 bg-red-500/20 hover:bg-red-500/30 rounded-lg text-red-400 transition">
                <span class="material-symbols-outlined text-sm">close</span>
            </button>
        </td>
    `;

    tbody.appendChild(tr);
    reindexRows();
    calculateTotals();
}

let activeUpdatingRowId = null;

function openDigiUpdateModal(rowId) {
    activeUpdatingRowId = rowId;
    const row = document.getElementById(rowId);
    if (!row) return;

    const rowIdxCell = row.querySelector('.row-index');
    const rowIdx = rowIdxCell ? rowIdxCell.textContent : '';

    const titleEl = document.getElementById('digiUpdateModalTitle');
    if (titleEl) titleEl.textContent = `Actualizar Fila #${rowIdx} desde Digicorp`;

    const input = document.getElementById('digiUpdateInput');
    if (input) input.value = '';

    const modal = document.getElementById('digiUpdateModal');
    if (modal) modal.classList.remove('hidden');
}

function closeDigiUpdateModal() {
    activeUpdatingRowId = null;
    const modal = document.getElementById('digiUpdateModal');
    if (modal) modal.classList.add('hidden');
}

async function applyDigiUpdateToRow() {
    if (!activeUpdatingRowId) return;
    const row = document.getElementById(activeUpdatingRowId);
    if (!row) return;

    const rawText = document.getElementById('digiUpdateInput')?.value || '';
    if (!rawText.trim()) {
        alert("Por favor pega el texto copiado de Digicorp.");
        return;
    }

    try {
        const res = await fetch((window.ENV?.API_BASE_URL || '') + '/api/digicorp/parse-text', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ text: rawText })
        });

        if (!res.ok) {
            const err = await res.json();
            alert("Error parseando texto de Digicorp: " + (err.detail || "Error desconocido"));
            return;
        }

        const data = await res.json();
        const p = data.product;

        // Update fields in existing row
        const descInput = row.querySelector('.prod-desc');
        const brandInput = row.querySelector('.prod-brand');
        const skuInput = row.querySelector('.prod-sku');
        const warrantyInput = row.querySelector('.prod-warranty');
        const priceInput = row.querySelector('.prod-price');
        const discInput = row.querySelector('.prod-discount');

        if (descInput && p.description) descInput.value = p.description;
        if (brandInput && p.brand) brandInput.value = p.brand;
        if (skuInput && p.sku) skuInput.value = p.sku;
        if (warrantyInput && p.warranty) warrantyInput.value = p.warranty;
        if (priceInput && p.price !== undefined) priceInput.value = p.price;
        if (discInput && p.discount_percent !== undefined) discInput.value = p.discount_percent;

        calculateTotals();
        closeDigiUpdateModal();
    } catch (e) {
        alert("Error actualizando fila: " + e.message);
    }
}

function escapeHtml(text) {
    if (!text) return '';
    return String(text).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

function moveRowUp(rowId) {
    const row = document.getElementById(rowId);
    if (row && row.previousElementSibling) {
        row.parentNode.insertBefore(row, row.previousElementSibling);
        reindexRows();
    }
}

function moveRowDown(rowId) {
    const row = document.getElementById(rowId);
    if (row && row.nextElementSibling) {
        row.parentNode.insertBefore(row.nextElementSibling, row);
        reindexRows();
    }
}

function removeRow(rowId) {
    const row = document.getElementById(rowId);
    if (row) {
        row.remove();
        reindexRows();
        calculateTotals();
    }
}

function duplicateRow(rowId) {
    const row = document.getElementById(rowId);
    if (row) {
        addProductRowWithData({
            description: row.querySelector('.prod-desc').value,
            brand: row.querySelector('.prod-brand')?.value || '',
            sku: row.querySelector('.prod-sku')?.value || '',
            item_warranty: row.querySelector('.prod-warranty')?.value || '',
            quantity: parseFloat(row.querySelector('.prod-qty').value) || 1,
            unit: row.querySelector('.prod-unit').value,
            price: parseFloat(row.querySelector('.prod-price').value) || 0,
            discount_percent: parseFloat(row.querySelector('.prod-discount')?.value) || 0
        });
    }
}

function clearProductRows() {
    if (confirm("¿Desea borrar todos los productos de la lista?")) {
        const tbody = document.getElementById('productsTbody');
        if (tbody) tbody.innerHTML = '';
        calculateTotals();
    }
}

function reindexRows() {
    const rows = document.querySelectorAll('#productsTbody tr');
    rows.forEach((row, idx) => {
        const idxCell = row.querySelector('.row-index');
        if (idxCell) idxCell.textContent = idx + 1;
    });
}

function collectProductsData() {
    const rows = document.querySelectorAll('#productsTbody tr');
    const products = [];
    rows.forEach(row => {
        const desc = row.querySelector('.prod-desc').value.trim();
        const brand = row.querySelector('.prod-brand')?.value.trim() || '';
        const sku = row.querySelector('.prod-sku')?.value.trim() || '';
        const warranty = row.querySelector('.prod-warranty')?.value.trim() || '';
        const qty = parseFloat(row.querySelector('.prod-qty').value) || 0;
        const unit = row.querySelector('.prod-unit').value;
        const price = parseFloat(row.querySelector('.prod-price').value) || 0;
        const disc = parseFloat(row.querySelector('.prod-discount')?.value) || 0;

        if (desc || qty > 0 || price > 0) {
            products.push({
                description: cleanHtmlToPlainText(desc),
                brand: brand,
                sku: sku,
                item_warranty: warranty,
                quantity: qty,
                unit: unit,
                price: price,
                discount_percent: disc
            });
        }
    });
    return products;
}

function cleanHtmlToPlainText(input) {
    if (!input || typeof input !== 'string') return input || '';
    if (!input.includes('<') && !input.includes('>')) return input.trim();

    try {
        const parser = new DOMParser();
        const doc = parser.parseFromString(input, 'text/html');
        doc.querySelectorAll('style, script, head').forEach(el => el.remove());
        doc.querySelectorAll('br').forEach(br => br.replaceWith('\n'));
        doc.querySelectorAll('p, div, li, tr').forEach(block => {
            block.after('\n');
        });
        const text = doc.body ? doc.body.textContent : doc.documentElement.textContent;
        return text.split('\n').map(line => line.trim()).filter((line, i, arr) => line || (i > 0 && arr[i-1])).join('\n').trim();
    } catch (e) {
        return input
            .replace(/<style[^>]*>[\s\S]*?<\/style>/gi, '')
            .replace(/<script[^>]*>[\s\S]*?<\/script>/gi, '')
            .replace(/<head[^>]*>[\s\S]*?<\/head>/gi, '')
            .replace(/<br\s*\/?>/gi, '\n')
            .replace(/<\/(p|div|li|tr)>/gi, '\n')
            .replace(/<[^>]+>/g, '')
            .replace(/&nbsp;/g, ' ')
            .replace(/&amp;/g, '&')
            .replace(/&lt;/g, '<')
            .replace(/&gt;/g, '>')
            .trim();
    }
}

function getVal(id, fallback = '') {
    const el = document.getElementById(id);
    return el ? el.value : fallback;
}

function getNumVal(id, fallback = 0) {
    const el = document.getElementById(id);
    return el ? (parseFloat(el.value) || fallback) : fallback;
}

function getCheckVal(id, fallback = false) {
    const el = document.getElementById(id);
    return el ? el.checked : fallback;
}

function setVal(id, value) {
    const el = document.getElementById(id);
    if (el) {
        let valStr = value !== undefined && value !== null ? String(value) : '';
        if (valStr.includes('<') && valStr.includes('>')) {
            valStr = cleanHtmlToPlainText(valStr);
        }
        el.value = valStr;
    }
}

function setCheckVal(id, checked) {
    const el = document.getElementById(id);
    if (el) el.checked = !!checked;
}

function collectPayload() {
    const products = collectProductsData();
    const coverData = (typeof getCoverDesignData === 'function') ? getCoverDesignData() : {};

    return {
        document_type: getVal('docTypeSelect', 'Cotización'),
        quotation_number: getVal('quotationNumberInput', 'COT-001'),
        company_name: getVal('companySelect', ''),
        date: getVal('quotationDateInput') || getVal('dateInput', ''),
        purchase_date: getVal('purchaseDateInput', ''),
        validity: parseInt(getVal('validityInput', '15')) || 15,
        currency: getVal('currencySelect', 'Bolivianos (Bs)'),
        exchange_rate: getNumVal('exchangeRateInput', 12.02),
        show_exchange_rate: getCheckVal('showExchangeRateCheck', true),
        show_dual_currency: true,
        client: {
            name: getVal('clientNameInput', ''),
            contact: getVal('clientContactInput', ''),
            address: getVal('clientAddressInput', '')
        },
        products: products,
        apply_discount: getCheckVal('applyDiscountCheck'),
        discount_percent: getNumVal('discountPercentInput', 0),
        apply_iva: getCheckVal('applyIvaCheck', true),
        iva_percent: getNumVal('ivaPercentInput', 13),
        enable_shipping: getCheckVal('enableShippingCheck'),
        shipping: getNumVal('shippingAmountInput', 0),
        shipping_type: getVal('shippingTypeSelect', 'Envío Local'),
        apply_payment: getCheckVal('applyPaymentCheck'),
        paid_amount: getNumVal('paidAmountInput', 0),
        notes: cleanHtmlToPlainText(getVal('internalNotesInput', '')),
        bank_details: cleanHtmlToPlainText(getVal('bankDetailsInput', '')),
        installation_terms: cleanHtmlToPlainText(getVal('installationTermsInput', '')),
        include_summary: getCheckVal('includeSummaryCheck', true),
        include_bank_details: getCheckVal('includeBankDetailsCheck', true),
        include_installation: getCheckVal('includeInstallationCheck', true),
        include_warranty: getCheckVal('includeWarrantyCheck', true),
        include_signature: getCheckVal('includeSignatureCheck', true),
        cover_page_enabled: coverData.enabled || false,
        cover_style: coverData.cover_style || 'corporate_modern',
        cover_subtitle: coverData.cover_subtitle || '',
        project_name: coverData.project_name || '',
        project_location: coverData.project_location || '',
        watermark_text: coverData.watermark_text || '',
        accent_color: coverData.accent_color || '#10B981',
        cover_page_data: coverData,
        terms_data: {
            validez_dias: parseInt(getVal('validityInput', '15')) || 15,
            payment_method: getVal('termsPaymentMethodSelect', 'Contado'),
            payment_type: getVal('termsPaymentTypeSelect', 'Efectivo'),
            estimated_days: parseInt(getVal('termsEstimatedDaysInput', '7')) || 7,
            warranty_covers: cleanHtmlToPlainText(getVal('warrantyCoversInput', '')),
            warranty_excludes: cleanHtmlToPlainText(getVal('warrantyExcludesInput', ''))
        },
        work_calculator_data: (typeof collectWorkCalculatorData === 'function') ? collectWorkCalculatorData() : {}
    };
}

function populateFormFromData(data) {
    if (!data) return;
    if (data.document_type) setVal('docTypeSelect', data.document_type);
    if (data.quotation_number) setVal('quotationNumberInput', data.quotation_number);
    if (data.company_name) setVal('companySelect', data.company_name);
    if (data.date) {
        setVal('dateInput', data.date);
        setVal('quotationDateInput', data.date);
    }
    if (data.purchase_date) setVal('purchaseDateInput', data.purchase_date);
    if (data.validity) setVal('validityInput', data.validity);
    if (data.currency) setVal('currencySelect', data.currency);
    if (data.exchange_rate) setVal('exchangeRateInput', data.exchange_rate);
    setCheckVal('showExchangeRateCheck', data.show_exchange_rate !== undefined ? data.show_exchange_rate : true);

    if (data.client) {
        setVal('clientNameInput', data.client.name || '');
        setVal('clientContactInput', data.client.contact || '');
        setVal('clientAddressInput', data.client.address || '');
    }

    setCheckVal('applyDiscountCheck', data.apply_discount);
    setVal('discountPercentInput', data.discount_percent || 0);
    setCheckVal('applyIvaCheck', data.apply_iva !== undefined ? data.apply_iva : true);
    setVal('ivaPercentInput', data.iva_percent || 13);
    setCheckVal('enableShippingCheck', data.enable_shipping);
    setVal('shippingAmountInput', data.shipping || 0);
    if (data.shipping_type) setVal('shippingTypeSelect', data.shipping_type);

    setCheckVal('applyPaymentCheck', data.apply_payment);
    setVal('paidAmountInput', data.paid_amount || 0);

    setVal('internalNotesInput', data.notes || '');
    setVal('bankDetailsInput', data.bank_details || '');
    setVal('installationTermsInput', data.installation_terms || '');
    
    setCheckVal('includeSummaryCheck', data.include_summary !== undefined ? data.include_summary : true);
    setCheckVal('includeBankDetailsCheck', data.include_bank_details !== undefined ? data.include_bank_details : true);
    setCheckVal('includeInstallationCheck', data.include_installation !== undefined ? data.include_installation : true);
    setCheckVal('includeWarrantyCheck', data.include_warranty !== undefined ? data.include_warranty : true);
    setCheckVal('includeSignatureCheck', data.include_signature !== undefined ? data.include_signature : true);

    if (typeof syncAllTermCheckboxes === 'function') {
        syncAllTermCheckboxes();
    }

    if (data.terms_data) {
        if (data.terms_data.payment_method) setVal('termsPaymentMethodSelect', data.terms_data.payment_method);
        if (data.terms_data.payment_type) setVal('termsPaymentTypeSelect', data.terms_data.payment_type);
        if (data.terms_data.estimated_days) setVal('termsEstimatedDaysInput', data.terms_data.estimated_days);
        if (data.terms_data.warranty_covers) setVal('warrantyCoversInput', data.terms_data.warranty_covers);
        if (data.terms_data.warranty_excludes) setVal('warrantyExcludesInput', data.terms_data.warranty_excludes);
    }

    if (data.cover_page_data && typeof setCoverDesignData === 'function') {
        setCoverDesignData(data.cover_page_data);
    }

    if (data.work_calculator_data && typeof restoreWorkCalculatorData === 'function') {
        restoreWorkCalculatorData(data.work_calculator_data);
    }

    // Populate products
    const tbody = document.getElementById('productsTbody');
    if (tbody) tbody.innerHTML = '';
    const prods = data.products || [];
    prods.forEach(p => {
        addProductRowWithData({
            description: p.description || p[0] || '',
            brand: p.brand || '',
            sku: p.sku || '',
            quantity: parseFloat(p.quantity || p[1]) || 1,
            unit: p.unit || p[2] || 'unidad (u)',
            price: parseFloat(p.price || p[3]) || 0,
            discount_percent: parseFloat(p.discount_percent) || 0
        });
    });

    calculateTotals();
    switchTab(0);
}

function calculateTotals() {
    const payload = collectPayload();
    const selectedCurrency = payload.currency;

    let subtotal = 0;
    const rows = document.querySelectorAll('#productsTbody tr');
    rows.forEach(row => {
        const qty = parseFloat(row.querySelector('.prod-qty').value) || 0;
        const price = parseFloat(row.querySelector('.prod-price').value) || 0;
        const disc = parseFloat(row.querySelector('.prod-discount')?.value) || 0;
        
        const rawAmount = qty * price;
        const discAmount = rawAmount * (disc / 100);
        const amount = rawAmount - discAmount;

        const amtEl = row.querySelector('.prod-amount');
        if (amtEl) amtEl.textContent = amount.toFixed(2);
        subtotal += amount;
    });

    const discountAmount = payload.apply_discount ? subtotal * (payload.discount_percent / 100) : 0;
    const afterDiscount = subtotal - discountAmount;
    const ivaAmount = payload.apply_iva ? afterDiscount * (payload.iva_percent / 100) : 0;
    const shippingAmount = payload.enable_shipping ? payload.shipping : 0;
    const total = afterDiscount + ivaAmount + shippingAmount;

    const paidAmount = payload.apply_payment ? payload.paid_amount : 0;
    const saldoAmount = payload.apply_payment ? Math.max(0, total - paidAmount) : 0;

    // Update displays
    if (document.getElementById('displaySubtotal')) document.getElementById('displaySubtotal').textContent = `${subtotal.toFixed(2)} ${selectedCurrency}`;
    if (document.getElementById('displayDiscountAmount')) document.getElementById('displayDiscountAmount').textContent = `- ${discountAmount.toFixed(2)}`;
    if (document.getElementById('displayIvaAmount')) document.getElementById('displayIvaAmount').textContent = `+ ${ivaAmount.toFixed(2)}`;
    if (document.getElementById('displayTotal')) document.getElementById('displayTotal').textContent = `${total.toFixed(2)} ${selectedCurrency}`;
    if (document.getElementById('displaySaldoAmount')) document.getElementById('displaySaldoAmount').textContent = `${saldoAmount.toFixed(2)} ${selectedCurrency}`;

    // Footer
    if (document.getElementById('footSubtotal')) document.getElementById('footSubtotal').textContent = subtotal.toFixed(2);
    if (document.getElementById('footShipping')) document.getElementById('footShipping').textContent = shippingAmount.toFixed(2);
    if (document.getElementById('footPaid')) document.getElementById('footPaid').textContent = paidAmount.toFixed(2);
    if (document.getElementById('footTotal')) document.getElementById('footTotal').textContent = `${total.toFixed(2)} ${selectedCurrency}`;
}

async function generatePDF() {
    const payload = collectPayload();
    if (!payload.company_name) {
        alert("Por favor seleccione una Empresa Emisora.");
        return;
    }
    if (payload.products.length === 0) {
        alert("Por favor agregue al menos un producto a la cotización.");
        return;
    }

    try {
        const res = await fetch((window.ENV?.API_BASE_URL || '') + '/api/quotations/pdf', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!res.ok) {
            const err = await res.json();
            alert("Error al generar PDF: " + (err.detail || "Error desconocido"));
            return;
        }

        const blob = await res.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${payload.quotation_number}.pdf`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        if (typeof loadDbQuotations === 'function') loadDbQuotations();
    } catch (e) {
        alert("Error de conexión al generar PDF: " + e.message);
    }
}

async function saveCotzFile() {
    const payload = collectPayload();
    try {
        const res = await fetch((window.ENV?.API_BASE_URL || '') + '/api/quotations/save', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await res.json();
        if (res.ok) {
            alert(`Archivo guardado exitosamente en SQLite y paquete .cotz: ${data.filename}`);
            if (typeof loadHistory === 'function') loadHistory();
            if (typeof loadDbQuotations === 'function') loadDbQuotations();
        } else {
            alert("Error al guardar archivo: " + data.detail);
        }
    } catch (e) {
        alert("Error de conexión al guardar archivo: " + e.message);
    }
}

function newQuotation() {
    if (confirm("¿Desea reiniciar el formulario para una nueva cotización?")) {
        if (document.getElementById('clientNameInput')) document.getElementById('clientNameInput').value = '';
        if (document.getElementById('clientContactInput')) document.getElementById('clientContactInput').value = '';
        if (document.getElementById('clientAddressInput')) document.getElementById('clientAddressInput').value = '';
        if (document.getElementById('productsTbody')) document.getElementById('productsTbody').innerHTML = '';
        if (document.getElementById('applyPaymentCheck')) document.getElementById('applyPaymentCheck').checked = false;
        if (document.getElementById('paidAmountInput')) document.getElementById('paidAmountInput').value = '0.00';
        generateQuotationNumber();
        addProductRow();
        calculateTotals();
    }
}
