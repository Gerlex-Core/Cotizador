/**
 * Package: settings/settings.js
 * Subcategory tab switcher for Master Settings Hub (Empresas Emisoras vs Configuración General & PDF).
 */

function switchSettingsSubTab(subCategory) {
    const subCompany = document.getElementById('settingsSubCompany');
    const subGeneral = document.getElementById('settingsSubGeneral');
    const btnCompany = document.getElementById('subtab-btn-company');
    const btnGeneral = document.getElementById('subtab-btn-general');

    if (!subCompany || !subGeneral) return;

    if (subCategory === 'company') {
        subCompany.classList.remove('hidden');
        subGeneral.classList.add('hidden');

        if (btnCompany) {
            btnCompany.className = "settings-subtab-btn active px-4 py-2 rounded-2xl text-xs font-bold transition flex items-center space-x-2 bg-[var(--text-primary)] text-[var(--bg-primary)] shadow-sm";
        }
        if (btnGeneral) {
            btnGeneral.className = "settings-subtab-btn px-4 py-2 rounded-2xl text-xs font-bold transition flex items-center space-x-2 text-[var(--text-secondary)] hover:bg-[var(--bg-secondary)]";
        }
        loadCompanies();
    } else if (subCategory === 'general') {
        subCompany.classList.add('hidden');
        subGeneral.classList.remove('hidden');

        if (btnGeneral) {
            btnGeneral.className = "settings-subtab-btn active px-4 py-2 rounded-2xl text-xs font-bold transition flex items-center space-x-2 bg-[var(--text-primary)] text-[var(--bg-primary)] shadow-sm";
        }
        if (btnCompany) {
            btnCompany.className = "settings-subtab-btn px-4 py-2 rounded-2xl text-xs font-bold transition flex items-center space-x-2 text-[var(--text-secondary)] hover:bg-[var(--bg-secondary)]";
        }
        loadAppConfig();
    }
}
