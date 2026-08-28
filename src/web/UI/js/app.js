/**
 * Cotizador Pro Web Application Client (MD3 Android Edition)
 * Root Launcher, Global State Manager, and Main Navigation Orchestrator.
 */

let appConfig = {};
let availableUnits = {};
let currentCurrency = "Bolivianos (Bs)";
let productRowCounter = 0;
let registeredCompanies = [];

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => initApp());
} else {
    initApp();
}

async function initApp() {
    generateQuotationNumber();
    setCurrentDate();
    await loadAppConfig();
    await loadCompanies();
    await loadHistory();
    await loadDbQuotations();
    if (document.querySelectorAll('#productsTbody tr').length === 0) {
        addProductRow();
    }
    // Start on Productos & Servicios tab by default
    switchTab(0);
}

const TAB_PAGE_MAP = {
    0: 'page0',          // Productos & Servicios
    1: 'page1_catalog',  // Catálogo & Combos
    2: 'page2_designer', // Diseñador Portada
    3: 'page3_digicorp', // Importador Digicorp
    4: 'page1',          // Finanzas & Saldo
    5: 'page2',          // Términos & Garantía
    6: 'page3',          // Historial de Cotizaciones
    7: 'page4',          // Configuraciones Hub
    8: 'page8_pdf_editor' // Edición PDF
};

function switchTab(index) {
    // Hide Work Calculator View if active
    const workView = document.getElementById('workCalculatorView');
    if (workView) workView.classList.add('hidden');

    // Toggle main tab pages by explicit ID
    Object.keys(TAB_PAGE_MAP).forEach((key) => {
        const pageId = TAB_PAGE_MAP[key];
        const pageEl = document.getElementById(pageId);
        if (pageEl) {
            if (parseInt(key) === index) {
                pageEl.classList.remove('hidden');
            } else {
                pageEl.classList.add('hidden');
            }
        }
    });

    const buttons = document.querySelectorAll('.nav-btn');
    buttons.forEach((btn) => {
        const tabData = parseInt(btn.getAttribute('data-tab'));
        if (tabData === index) {
            btn.classList.add('bg-[var(--text-primary)]', 'text-[var(--bg-primary)]', 'shadow-md');
            btn.classList.remove('text-[var(--text-secondary)]', 'hover:bg-[var(--bg-secondary)]');
        } else {
            btn.classList.remove('bg-[var(--text-primary)]', 'text-[var(--bg-primary)]', 'shadow-md');
            btn.classList.add('text-[var(--text-secondary)]', 'hover:bg-[var(--bg-secondary)]');
        }
    });

    // Auto-refresh tab data on tab switch
    if (index === 6) {
        if (typeof loadDbQuotations === 'function') loadDbQuotations();
    } else if (index === 7) {
        // Configuraciones Master Hub
        if (typeof switchSettingsSubTab === 'function') switchSettingsSubTab('company');
    }
}

// DRAG & DROP UI ENGINE HELPERS
function handleDragOver(e, element) {
    e.preventDefault();
    e.stopPropagation();
    if (element) {
        element.classList.add('border-[var(--border-focus)]', 'bg-[var(--bg-secondary)]', 'scale-[1.01]');
    }
}

function handleDragLeave(e, element) {
    e.preventDefault();
    e.stopPropagation();
    if (element) {
        element.classList.remove('border-[var(--border-focus)]', 'bg-[var(--bg-secondary)]', 'scale-[1.01]');
    }
}
