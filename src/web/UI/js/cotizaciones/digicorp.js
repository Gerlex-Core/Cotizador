/**
 * Digicorp Web Integration & Scraper Controller (MD3)
 * Handles text parsing, URL scraping, full-screen frame controls, and direct product injection.
 */

function switchDigicorpMode(mode) {
    const textDiv = document.getElementById('digiModeText');
    const urlDiv = document.getElementById('digiModeUrl');
    const webDiv = document.getElementById('digiModeWeb');

    const textBtn = document.getElementById('digiTabTextBtn');
    const urlBtn = document.getElementById('digiTabUrlBtn');
    const webBtn = document.getElementById('digiTabWebBtn');

    [textDiv, urlDiv, webDiv].forEach(el => el?.classList.add('hidden'));

    [textBtn, urlBtn, webBtn].forEach(btn => {
        if (btn) btn.className = "px-4 py-2 bg-[var(--bg-secondary)] text-[var(--text-secondary)] font-bold rounded-xl hover:bg-white/10 transition flex items-center space-x-1.5";
    });

    if (mode === 'text') {
        textDiv?.classList.remove('hidden');
        if (textBtn) textBtn.className = "px-4 py-2 bg-[var(--text-primary)] text-[var(--bg-primary)] font-extrabold rounded-xl transition shadow-xs flex items-center space-x-1.5";
    } else if (mode === 'url') {
        urlDiv?.classList.remove('hidden');
        if (urlBtn) urlBtn.className = "px-4 py-2 bg-[var(--text-primary)] text-[var(--bg-primary)] font-extrabold rounded-xl transition shadow-xs flex items-center space-x-1.5";
    } else if (mode === 'web') {
        webDiv?.classList.remove('hidden');
        if (webBtn) webBtn.className = "px-4 py-2 bg-[var(--text-primary)] text-[var(--bg-primary)] font-extrabold rounded-xl transition shadow-xs flex items-center space-x-1.5";
    }
}

function clearDigiText() {
    const textarea = document.getElementById('digiTextInput');
    if (textarea) textarea.value = '';
}

function onDigiTextPasted() {
    // Helper to auto-detect if complete snippet was pasted
    const val = document.getElementById('digiTextInput')?.value || '';
    if (val.includes('Bs') && (val.includes('Código') || val.includes('detalles'))) {
        // Optional auto-parse highlight
    }
}

async function parseAndAddDigiText(addToQuotation = true) {
    const rawText = document.getElementById('digiTextInput')?.value || '';
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
            alert("Error parseando texto: " + (err.detail || "Error desconocido"));
            return;
        }

        const data = await res.json();
        const p = data.product;

        if (addToQuotation) {
            if (typeof addProductRowWithData === 'function') {
                addProductRowWithData({
                    description: p.description,
                    brand: p.brand || '',
                    sku: p.sku || '',
                    quantity: 1,
                    unit: p.unit || 'unidad (u)',
                    price: p.price || 0,
                    discount_percent: p.discount_percent || 0,
                    item_warranty: p.warranty || ''
                });
            }
            switchTab(0);
        } else {
            // Add to Catalog
            const catRes = await fetch((window.ENV?.API_BASE_URL || '') + '/api/catalog/items', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    description: p.description,
                    brand: p.brand || '',
                    sku: p.sku || '',
                    price: p.price || 0,
                    unit: p.unit || 'unidad (u)',
                    category: 'Digicorp',
                    warranty: p.warranty || ''
                })
            });
            if (catRes.ok) {
                alert("Producto agregado al catálogo correctamente.");
                if (typeof initCatalog === 'function') initCatalog();
                switchTab(1);
            }
        }
    } catch (e) {
        alert("Error de conexión con el servidor: " + e.message);
    }
}

async function scrapeDigiUrl() {
    const url = document.getElementById('digiUrlInput')?.value || '';
    if (!url.trim()) {
        alert("Por favor ingresa un enlace de producto de Digicorp.");
        return;
    }

    try {
        const res = await fetch((window.ENV?.API_BASE_URL || '') + '/api/digicorp/scrape-url', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ url: url })
        });

        if (!res.ok) {
            const err = await res.json();
            alert("Error al extraer producto de URL: " + (err.detail || "Error desconocido"));
            return;
        }

        const data = await res.json();
        const p = data.product;

        if (typeof addProductRowWithData === 'function') {
            addProductRowWithData({
                description: p.description,
                brand: p.brand || '',
                sku: p.sku || '',
                quantity: 1,
                unit: p.unit || 'unidad (u)',
                price: p.price || 0,
                discount_percent: 0,
                item_warranty: p.warranty || ''
            });
        }
        switchTab(0);
    } catch (e) {
        alert("Error de conexión con el servidor: " + e.message);
    }
}

function navigateDigiFrame() {
    const url = document.getElementById('digiWebAddressBar')?.value || 'https://digicorp.com.bo';
    const iframe = document.getElementById('digiIframe');
    if (iframe) iframe.src = url;
}

function reloadDigiFrame() {
    const iframe = document.getElementById('digiIframe');
    if (iframe) iframe.src = iframe.src;
}
