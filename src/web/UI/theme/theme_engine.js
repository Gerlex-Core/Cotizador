/**
 * Advanced Dynamic Material Design 3 Theme Engine
 * Loads JSON theme files dynamically from /api/themes and injects CSS properties.
 */

const ThemeEngine = {
    currentThemeId: "md3_monochrome_dark",
    availableThemes: [],

    async fetchAvailableThemes() {
        try {
            const res = await fetch((window.ENV?.API_BASE_URL || '') + '/api/themes');
            if (res.ok) {
                this.availableThemes = await res.json();
                this.populateThemeSelectors();
            }
        } catch (e) {
            console.error("Error fetching themes list:", e);
        }
    },

    async loadAndApplyTheme(themeId) {
        if (!themeId) themeId = "md3_monochrome_dark";
        this.currentThemeId = themeId;

        try {
            const res = await fetch(`${window.ENV?.API_BASE_URL || ''}/api/themes/${encodeURIComponent(themeId)}`);
            if (res.ok) {
                const themeData = await res.json();
                this.applyThemeJSON(themeData);
                localStorage.setItem('cotizador_active_theme', themeId);
            }
        } catch (e) {
            console.error(`Error loading theme ${themeId}:`, e);
        }
    },

    applyThemeJSON(themeData) {
        const root = document.documentElement;
        const colors = themeData.colors || {};
        const shapes = themeData.shapes || {};

        // MD3 Color System Variables
        root.style.setProperty('--bg-primary', colors.surface || '#121318');
        root.style.setProperty('--bg-secondary', colors.surface_container || '#1D1E24');
        root.style.setProperty('--bg-card', colors.surface_variant || '#1E1F25');
        root.style.setProperty('--bg-sidebar', colors.surface_container_low || '#16171D');
        root.style.setProperty('--border-default', colors.outline_variant || 'rgba(255,255,255,0.12)');
        root.style.setProperty('--border-focus', colors.primary || '#E6E1E5');
        root.style.setProperty('--text-primary', colors.on_surface || '#E6E1E5');
        root.style.setProperty('--text-secondary', colors.on_surface_variant || '#CAC4D0');
        root.style.setProperty('--accent-primary', colors.primary || '#E6E1E5');
        root.style.setProperty('--accent-hover', colors.accent_hover || '#FFFFFF');
        root.style.setProperty('--accent-glow', colors.accent_glow || 'rgba(255,255,255,0.15)');
        root.style.setProperty('--card-shadow', colors.card_shadow || '0 8px 30px rgba(0,0,0,0.5)');

        // Corner Shapes
        root.style.setProperty('--corner-large', shapes.corner_large || '24px');
        root.style.setProperty('--corner-medium', shapes.corner_medium || '16px');

        if (themeData.is_dark) {
            root.classList.add('dark');
        } else {
            root.classList.remove('dark');
        }

        // Update badges
        const badge = document.getElementById('themeNameBadge');
        if (badge) badge.textContent = themeData.name || "MD3 Android";

        const select = document.getElementById('configThemeSelect');
        if (select) select.value = this.currentThemeId;
    },

    async cycleTheme() {
        if (this.availableThemes.length === 0) {
            await this.fetchAvailableThemes();
        }
        if (this.availableThemes.length > 0) {
            const currentIdx = this.availableThemes.findIndex(t => t.id === this.currentThemeId);
            const nextIdx = (currentIdx + 1) % this.availableThemes.length;
            const nextTheme = this.availableThemes[nextIdx];
            await this.loadAndApplyTheme(nextTheme.id);
        }
    },

    populateThemeSelectors() {
        const select = document.getElementById('configThemeSelect');
        if (select) {
            select.innerHTML = '';
            this.availableThemes.forEach(t => {
                const opt = document.createElement('option');
                opt.value = t.id;
                opt.textContent = t.name + (t.is_dark ? ' (Dark)' : ' (Light)');
                select.appendChild(opt);
            });
            select.value = this.currentThemeId;
        }
    },

    async init() {
        await this.fetchAvailableThemes();
        const saved = localStorage.getItem('cotizador_active_theme');
        await this.loadAndApplyTheme(saved || "md3_monochrome_dark");
    }
};

document.addEventListener('DOMContentLoaded', () => {
    ThemeEngine.init();
});
