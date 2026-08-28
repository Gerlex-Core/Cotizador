/**
 * Product & Combo Catalog Controller (MD3)
 * Handles catalog search, category filtering, custom item creation, and direct injection into quotation.
 */

let catalogItems = [];
let catalogCombos = [];
let activeCatalogTab = 'products';

async function initCatalog() {
    try {
        const [itemsRes, combosRes] = await Promise.all([
            fetch((window.ENV?.API_BASE_URL || '') + '/api/catalog/items'),
            fetch((window.ENV?.API_BASE_URL || '') + '/api/catalog/combos')
        ]);
        if (itemsRes.ok) catalogItems = await itemsRes.json();
        if (combosRes.ok) catalogCombos = await combosRes.json();
        renderCatalog();
    } catch (e) {
        console.error("Error loading catalog:", e);
    }
}

function switchCatalogTab(tab) {
    activeCatalogTab = tab;
    const prodBtn = document.getElementById('catTabProductsBtn');
    const comboBtn = document.getElementById('catTabCombosBtn');
    const prodCont = document.getElementById('catalogProductsContainer');
    const comboCont = document.getElementById('catalogCombosContainer');

    if (tab === 'products') {
        prodBtn.className = "flex-1 py-2 bg-[var(--text-primary)] text-[var(--bg-primary)] font-bold rounded-xl text-center shadow-xs transition";
        comboBtn.className = "flex-1 py-2 bg-[var(--bg-secondary)] text-[var(--text-secondary)] font-bold rounded-xl text-center hover:bg-white/10 transition";
        prodCont.classList.remove('hidden');
        comboCont.classList.add('hidden');
    } else {
        comboBtn.className = "flex-1 py-2 bg-[var(--text-primary)] text-[var(--bg-primary)] font-bold rounded-xl text-center shadow-xs transition";
        prodBtn.className = "flex-1 py-2 bg-[var(--bg-secondary)] text-[var(--text-secondary)] font-bold rounded-xl text-center hover:bg-white/10 transition";
        comboCont.classList.remove('hidden');
        prodCont.classList.add('hidden');
    }
    renderCatalog();
}

function filterCatalog() {
    renderCatalog();
}

function renderCatalog() {
    const searchText = (document.getElementById('catalogSearchInput')?.value || '').toLowerCase();
    const categoryFilter = document.getElementById('catalogCategoryFilter')?.value || 'ALL';

    if (activeCatalogTab === 'products') {
        const container = document.getElementById('catalogProductsContainer');
        if (!container) return;

        const filtered = catalogItems.filter(item => {
            const matchCat = categoryFilter === 'ALL' || item.category === categoryFilter;
            const matchSearch = item.description.toLowerCase().includes(searchText) ||
                                (item.brand || '').toLowerCase().includes(searchText) ||
                                (item.sku || '').toLowerCase().includes(searchText);
            return matchCat && matchSearch;
        });

        if (filtered.length === 0) {
            container.innerHTML = `<div class="col-span-12 py-10 text-center text-xs text-[var(--text-secondary)]">No se encontraron productos en el catálogo.</div>`;
            return;
        }

        container.innerHTML = filtered.map(item => `
            <div class="col-span-4 bg-[var(--bg-card)] border border-[var(--border-default)] rounded-3xl p-4 flex flex-col justify-between space-y-3 hover:border-[var(--border-focus)] transition shadow-sm">
                <div class="space-y-1">
                    <div class="flex items-center justify-between">
                        <span class="text-[10px] font-bold text-emerald-400 uppercase tracking-wider bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/20">${escapeHtml(item.category)}</span>
                        <span class="text-[10px] text-[var(--text-secondary)] font-mono">${escapeHtml(item.brand || 'Genérico')}</span>
                    </div>
                    <h3 class="text-xs font-bold text-[var(--text-primary)] leading-snug line-clamp-2">${escapeHtml(item.description)}</h3>
                    <p class="text-[10px] text-[var(--text-secondary)] font-mono">SKU: ${escapeHtml(item.sku || 'N/A')}</p>
                </div>
                <div class="flex items-center justify-between pt-2 border-t border-[var(--border-default)]">
                    <div>
                        <span class="text-[10px] text-[var(--text-secondary)] block">Precio Unit.</span>
                        <span class="text-sm font-black text-emerald-400">${item.price.toFixed(2)} Bs</span>
                    </div>
                    <button onclick='addCatalogItemToQuotation(${JSON.stringify(item).replace(/'/g, "&apos;")})' class="px-3 py-1.5 bg-[var(--text-primary)] text-[var(--bg-primary)] rounded-full text-xs font-bold hover:opacity-90 transition flex items-center space-x-1">
                        <span class="material-symbols-outlined text-base">add</span>
                        <span>Agregar</span>
                    </button>
                </div>
            </div>
        `).join('');
    } else {
        const container = document.getElementById('catalogCombosContainer');
        if (!container) return;

        const filtered = catalogCombos.filter(combo => {
            const matchCat = categoryFilter === 'ALL' || combo.category === categoryFilter;
            const matchSearch = combo.name.toLowerCase().includes(searchText) || combo.description.toLowerCase().includes(searchText);
            return matchCat && matchSearch;
        });

        if (filtered.length === 0) {
            container.innerHTML = `<div class="col-span-12 py-10 text-center text-xs text-[var(--text-secondary)]">No se encontraron combos/kits en el catálogo.</div>`;
            return;
        }

        container.innerHTML = filtered.map(combo => {
            const comboTotal = combo.products.reduce((acc, p) => acc + (p.quantity * p.price), 0);
            return `
                <div class="col-span-6 bg-[var(--bg-card)] border border-[var(--border-default)] rounded-3xl p-5 space-y-3 hover:border-[var(--border-focus)] transition shadow-sm">
                    <div class="flex items-center justify-between">
                        <span class="text-[10px] font-bold text-purple-400 uppercase tracking-wider bg-purple-500/10 px-2.5 py-0.5 rounded-full border border-purple-500/20">${escapeHtml(combo.category)}</span>
                        <span class="text-xs font-black text-emerald-400 font-mono">${comboTotal.toFixed(2)} Bs</span>
                    </div>
                    <div>
                        <h3 class="text-sm font-extrabold text-[var(--text-primary)]">${escapeHtml(combo.name)}</h3>
                        <p class="text-[11px] text-[var(--text-secondary)] mt-0.5">${escapeHtml(combo.description)}</p>
                    </div>
                    <div class="bg-[var(--bg-primary)] rounded-2xl p-3 space-y-1.5 text-[11px] border border-[var(--border-default)]">
                        <span class="font-bold text-[var(--text-secondary)] block text-[10px]">Contenido del Kit:</span>
                        ${combo.products.map(p => `
                            <div class="flex justify-between text-[var(--text-primary)] border-b border-white/5 pb-1">
                                <span>${p.quantity}x ${escapeHtml(p.description)}</span>
                                <span class="font-mono font-semibold">${(p.quantity * p.price).toFixed(2)} Bs</span>
                            </div>
                        `).join('')}
                    </div>
                    <div class="flex justify-end pt-2">
                        <button onclick='addComboToQuotation(${JSON.stringify(combo).replace(/'/g, "&apos;")})' class="px-4 py-2 bg-[var(--text-primary)] text-[var(--bg-primary)] rounded-full text-xs font-extrabold shadow hover:opacity-90 transition flex items-center space-x-1.5">
                            <span class="material-symbols-outlined text-base">post_add</span>
                            <span>Inyectar Kit Completo</span>
                        </button>
                    </div>
                </div>
            `;
        }).join('');
    }
}

function addCatalogItemToQuotation(item) {
    if (typeof addProductRowWithData === 'function') {
        addProductRowWithData({
            description: item.description,
            brand: item.brand || '',
            sku: item.sku || '',
            quantity: 1,
            unit: item.unit || 'unidad (u)',
            price: item.price || 0,
            discount_percent: 0,
            item_warranty: item.warranty || ''
        });
    } else {
        addProductRow();
    }
    switchTab(0);
}

function addComboToQuotation(combo) {
    if (combo && combo.products) {
        combo.products.forEach(p => {
            addProductRowWithData({
                description: p.description,
                brand: p.brand || '',
                sku: p.sku || '',
                quantity: p.quantity || 1,
                unit: p.unit || 'unidad (u)',
                price: p.price || 0,
                discount_percent: 0,
                item_warranty: ''
            });
        });
    }
    switchTab(0);
}

function toggleNewCatalogItemModal() {
    const modal = document.getElementById('newCatalogItemModal');
    if (modal) modal.classList.toggle('hidden');
}

async function saveNewCatalogItem() {
    const desc = document.getElementById('newItemDesc')?.value.trim();
    if (!desc) {
        alert("Por favor ingresa la descripción del producto.");
        return;
    }

    const newItem = {
        description: desc,
        category: document.getElementById('newItemCategory')?.value || 'General',
        brand: document.getElementById('newItemBrand')?.value.trim() || '',
        sku: document.getElementById('newItemSku')?.value.trim() || '',
        price: parseFloat(document.getElementById('newItemPrice')?.value) || 0,
        unit: document.getElementById('newItemUnit')?.value.trim() || 'unidad (u)'
    };

    try {
        const res = await fetch((window.ENV?.API_BASE_URL || '') + '/api/catalog/items', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(newItem)
        });
        if (res.ok) {
            const data = await res.json();
            catalogItems.push(data.item);
            toggleNewCatalogItemModal();
            renderCatalog();
        }
    } catch (e) {
        console.error("Error saving catalog item:", e);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    initCatalog();
});
