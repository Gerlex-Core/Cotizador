/**
 * Cotizador Pro Web Application Client
 */

let appConfig = {};
let availableUnits = {};
let currentCurrency = "Bolivianos (Bs)";
let productRowCounter = 0;

document.addEventListener('DOMContentLoaded', () => {
    initApp();
});

async function initApp() {
    generateQuotationNumber();
    setCurrentDate();
    await loadAppConfig();
    await loadCompanies();
    await loadHistory();
    addProductRow(); // Add default empty row
}

function switchTab(index) {
    const pages = document.querySelectorAll('.workspace-page');
    pages.forEach((p, idx) => {
        if (idx === index) {
            p.classList.remove('hidden');
        } else {
            p.classList.add('hidden');
        }
    });

    const buttons = document.querySelectorAll('.nav-btn');
    buttons.forEach((btn, idx) => {
        if (idx === index) {
            btn.classList.add('bg-blue-600', 'text-white', 'shadow-lg', 'shadow-blue-600/30');
            btn.classList.remove('text-slate-400', 'hover:bg-white/5');
        } else {
            btn.classList.remove('bg-blue-600', 'text-white', 'shadow-lg', 'shadow-blue-600/30');
            btn.classList.add('text-slate-400', 'hover:bg-white/5');
        }
    });
}

function generateQuotationNumber() {
    const now = new Date();
    const docType = document.getElementById('docTypeSelect').value;
    const prefix = docType === 'Cotizacion' ? 'COT' : 'REC';
    const dateStr = now.getFullYear().toString() +
                    String(now.getMonth() + 1).padStart(2, '0') +
                    String(now.getDate()).padStart(2, '0');
    const timeStr = String(now.getHours()).padStart(2, '0') + String(now.getMinutes()).padStart(2, '0');
    document.getElementById('quotationNumberInput').value = `${prefix}-${dateStr}-${timeStr}`;
}

function setCurrentDate() {
    const now = new Date();
    const formatted = String(now.getDate()).padStart(2, '0') + '/' +
                      String(now.getMonth() + 1).padStart(2, '0') + '/' +
                      now.getFullYear();
    document.getElementById('dateInput').value = formatted;
}

function onDocTypeChanged() {
    generateQuotationNumber();
}

async function loadAppConfig() {
    try {
        const res = await fetch('/api/config');
        const data = await res.json();
        appConfig = data.config || {};
        availableUnits = data.units || {};
        currentCurrency = appConfig.moneda || "Bolivianos (Bs)";
        
        if (document.getElementById('configCurrencyInput')) {
            document.getElementById('configCurrencyInput').value = currentCurrency;
        }
        if (document.getElementById('configPreparedByInput')) {
            document.getElementById('configPreparedByInput').value = appConfig.prepared_by || "";
        }
    } catch (e) {
        console.error("Error loading config:", e);
    }
}

async function loadCompanies() {
    try {
        const res = await fetch('/api/companies');
        const names = await res.json();
        const select = document.getElementById('companySelect');
        select.innerHTML = '<option value="">Seleccionar Empresa</option>';
        names.forEach(name => {
            const opt = document.createElement('option');
            opt.value = name;
            opt.textContent = name;
            select.appendChild(opt);
        });
        
        if (names.length > 0) {
            select.value = names[0];
            onCompanySelectChanged();
        }
    } catch (e) {
        console.error("Error loading companies:", e);
    }
}

async function onCompanySelectChanged() {
    const name = document.getElementById('companySelect').value;
    if (!name) {
        document.getElementById('companyInfoLabel').textContent = "";
        return;
    }
    try {
        const res = await fetch(`/api/companies/${encodeURIComponent(name)}`);
        if (res.ok) {
            const data = await res.json();
            const parts = [];
            if (data.nit) parts.push(`NIT: ${data.nit}`);
            if (data.telefono) parts.push(`📞 ${data.telefono}`);
            if (data.correo) parts.push(`✉️ ${data.correo}`);
            document.getElementById('companyInfoLabel').textContent = parts.join(' | ');
            
            // Fill edit fields if present
            document.getElementById('companyNameEdit').value = data.nombre || name;
            document.getElementById('companyNitEdit').value = data.nit || "";
            document.getElementById('companyPhoneEdit').value = data.telefono || "";
            document.getElementById('companyEmailEdit').value = data.correo || "";
            document.getElementById('companyAddressEdit').value = data.direccion || "";
        }
    } catch (e) {
        console.error("Error fetching company details:", e);
    }
}

function addProductRow(desc = "", qty = 1, unit = "unidad (u)", price = 0) {
    productRowCounter++;
    const rowId = `row_${productRowCounter}`;
    const tbody = document.getElementById('productsTbody');

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
        <td class="p-3 text-center text-slate-500 font-mono">${tbody.children.length + 1}</td>
        <td class="p-3">
            <input type="text" value="${desc}" placeholder="Descripción del producto o servicio..." class="prod-desc w-full bg-[#0B0E14] border border-white/10 rounded-lg px-2.5 py-1.5 text-white focus:border-blue-500">
        </td>
        <td class="p-3">
            <input type="number" value="${qty}" min="0.01" step="1" oninput="calculateTotals()" class="prod-qty w-full bg-[#0B0E14] border border-white/10 rounded-lg px-2 py-1.5 text-center text-white font-bold focus:border-blue-500">
        </td>
        <td class="p-3">
            <select class="prod-unit w-full bg-[#0B0E14] border border-white/10 rounded-lg px-2 py-1.5 text-white focus:border-blue-500">
                ${unitOptionsHtml}
            </select>
        </td>
        <td class="p-3">
            <input type="number" value="${price}" min="0" step="0.5" oninput="calculateTotals()" class="prod-price w-full bg-[#0B0E14] border border-white/10 rounded-lg px-2.5 py-1.5 text-right text-white font-bold focus:border-blue-500">
        </td>
        <td class="p-3 text-right font-bold text-white prod-amount">
            0.00
        </td>
        <td class="p-3 text-center space-x-1">
            <button onclick="duplicateRow('${rowId}')" title="Duplicar" class="p-1 bg-white/5 hover:bg-white/10 rounded-lg text-slate-300 transition">
                <i data-lucide="copy" class="w-3.5 h-3.5"></i>
            </button>
            <button onclick="removeRow('${rowId}')" title="Eliminar" class="p-1 bg-red-500/20 hover:bg-red-500/30 rounded-lg text-red-400 transition">
                <i data-lucide="x" class="w-3.5 h-3.5"></i>
            </button>
        </td>
    `;

    tbody.appendChild(tr);
    lucide.createIcons();
    calculateTotals();
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
        const desc = row.querySelector('.prod-desc').value;
        const qty = parseFloat(row.querySelector('.prod-qty').value) || 1;
        const unit = row.querySelector('.prod-unit').value;
        const price = parseFloat(row.querySelector('.prod-price').value) || 0;
        addProductRow(desc, qty, unit, price);
    }
}

function clearProductRows() {
    if (confirm("¿Desea borrar todos los productos de la lista?")) {
        document.getElementById('productsTbody').innerHTML = '';
        calculateTotals();
    }
}

function reindexRows() {
    const rows = document.querySelectorAll('#productsTbody tr');
    rows.forEach((row, idx) => {
        row.children[0].textContent = idx + 1;
    });
}

function collectProductsData() {
    const rows = document.querySelectorAll('#productsTbody tr');
    const products = [];
    rows.forEach(row => {
        const desc = row.querySelector('.prod-desc').value.trim();
        const qty = parseFloat(row.querySelector('.prod-qty').value) || 0;
        const unit = row.querySelector('.prod-unit').value;
        const price = parseFloat(row.querySelector('.prod-price').value) || 0;
        if (desc || qty > 0 || price > 0) {
            products.push({
                description: desc,
                quantity: qty,
                unit: unit,
                price: price
            });
        }
    });
    return products;
}

function collectPayload() {
    const products = collectProductsData();
    return {
        document_type: document.getElementById('docTypeSelect').value,
        quotation_number: document.getElementById('quotationNumberInput').value,
        company_name: document.getElementById('companySelect').value,
        date: document.getElementById('dateInput').value,
        validity: parseInt(document.getElementById('validityInput').value) || 15,
        client: {
            name: document.getElementById('clientNameInput').value,
            contact: document.getElementById('clientContactInput').value,
            address: document.getElementById('clientAddressInput').value
        },
        products: products,
        apply_discount: document.getElementById('applyDiscountCheck').checked,
        discount_percent: parseFloat(document.getElementById('discountPercentInput').value) || 0,
        apply_iva: document.getElementById('applyIvaCheck').checked,
        iva_percent: parseFloat(document.getElementById('ivaPercentInput').value) || 13,
        enable_shipping: document.getElementById('enableShippingCheck').checked,
        shipping: parseFloat(document.getElementById('shippingAmountInput').value) || 0,
        shipping_type: document.getElementById('shippingTypeSelect').value,
        apply_payment: document.getElementById('applyPaymentCheck').checked,
        paid_amount: parseFloat(document.getElementById('paidAmountInput').value) || 0,
        notes: document.getElementById('internalNotesInput').value,
        bank_details: document.getElementById('bankDetailsInput').value,
        installation_terms: document.getElementById('installationTermsInput').value,
        include_bank_details: document.getElementById('includeBankDetailsCheck').checked,
        terms_data: {
            validez_dias: parseInt(document.getElementById('validityInput').value) || 15
        }
    };
}

function calculateTotals() {
    const payload = collectPayload();

    let subtotal = 0;
    const rows = document.querySelectorAll('#productsTbody tr');
    rows.forEach(row => {
        const qty = parseFloat(row.querySelector('.prod-qty').value) || 0;
        const price = parseFloat(row.querySelector('.prod-price').value) || 0;
        const amount = qty * price;
        row.querySelector('.prod-amount').textContent = amount.toFixed(2);
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
    document.getElementById('displaySubtotal').textContent = `${subtotal.toFixed(2)} ${currentCurrency}`;
    document.getElementById('displayDiscountAmount').textContent = `- ${discountAmount.toFixed(2)}`;
    document.getElementById('displayIvaAmount').textContent = `+ ${ivaAmount.toFixed(2)}`;
    document.getElementById('displayTotal').textContent = `${total.toFixed(2)} ${currentCurrency}`;
    document.getElementById('displaySaldoAmount').textContent = `${saldoAmount.toFixed(2)} ${currentCurrency}`;

    // Footer
    document.getElementById('footSubtotal').textContent = subtotal.toFixed(2);
    document.getElementById('footShipping').textContent = shippingAmount.toFixed(2);
    document.getElementById('footPaid').textContent = paidAmount.toFixed(2);
    document.getElementById('footTotal').textContent = `${total.toFixed(2)} ${currentCurrency}`;
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
        const res = await fetch('/api/quotations/pdf', {
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
    } catch (e) {
        alert("Error de conexión al generar PDF: " + e.message);
    }
}

async function saveCotzFile() {
    const payload = collectPayload();
    try {
        const res = await fetch('/api/quotations/save', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await res.json();
        if (res.ok) {
            alert(`Archivo guardado exitosamente: ${data.filename}`);
            loadHistory();
        } else {
            alert("Error al guardar archivo: " + data.detail);
        }
    } catch (e) {
        alert("Error de conexión al guardar archivo: " + e.message);
    }
}

function newQuotation() {
    if (confirm("¿Desea reiniciar el formulario para una nueva cotización?")) {
        document.getElementById('clientNameInput').value = '';
        document.getElementById('clientContactInput').value = '';
        document.getElementById('clientAddressInput').value = '';
        document.getElementById('productsTbody').innerHTML = '';
        document.getElementById('applyPaymentCheck').checked = false;
        document.getElementById('paidAmountInput').value = '0.00';
        generateQuotationNumber();
        addProductRow();
        calculateTotals();
    }
}

async function saveCompanyProfile() {
    const company = {
        nombre: document.getElementById('companyNameEdit').value,
        nit: document.getElementById('companyNitEdit').value,
        telefono: document.getElementById('companyPhoneEdit').value,
        correo: document.getElementById('companyEmailEdit').value,
        direccion: document.getElementById('companyAddressEdit').value
    };

    if (!company.nombre) {
        alert("El nombre de la empresa es obligatorio.");
        return;
    }

    try {
        const res = await fetch('/api/companies', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(company)
        });
        if (res.ok) {
            alert("Perfil de empresa guardado exitosamente.");
            loadCompanies();
        }
    } catch (e) {
        alert("Error al guardar empresa: " + e.message);
    }
}

async function saveGlobalConfig() {
    const payload = {
        moneda: document.getElementById('configCurrencyInput').value,
        prepared_by: document.getElementById('configPreparedByInput').value
    };

    try {
        const res = await fetch('/api/config', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (res.ok) {
            alert("Configuración global guardada correctamente.");
            currentCurrency = payload.moneda;
            calculateTotals();
        }
    } catch (e) {
        alert("Error al guardar configuración: " + e.message);
    }
}

async function loadHistory() {
    try {
        const res = await fetch('/api/history/recent');
        const files = await res.json();
        const container = document.getElementById('historyList');
        if (files.length === 0) {
            container.innerHTML = '<p class="text-slate-500 italic">No hay archivos recientes.</p>';
            return;
        }
        container.innerHTML = '';
        files.forEach(file => {
            const div = document.createElement('div');
            div.className = 'p-3 bg-white/5 border border-white/10 rounded-xl flex items-center justify-between text-slate-300 font-mono';
            div.innerHTML = `
                <span>📄 ${file}</span>
                <span class="text-xs text-blue-400 font-sans">Guardado</span>
            `;
            container.appendChild(div);
        });
    } catch (e) {
        console.error("Error loading history:", e);
    }
}
