/**
 * Cover Page & Layout Designer Controller (MD3)
 * Manages cover styles, project titles, watermarks, accent colors, and live mockup synchronization.
 */

let currentCoverStyle = "corporate_modern";

function setCoverStyle(style) {
    currentCoverStyle = style;
    document.querySelectorAll('.cover-style-btn').forEach(btn => {
        btn.classList.remove('border-[var(--border-focus)]', 'bg-[var(--bg-secondary)]', 'ring-2', 'ring-emerald-500');
        btn.classList.add('bg-[var(--bg-primary)]');
    });

    const activeBtn = document.getElementById(`coverStyleBtn_${style}`);
    if (activeBtn) {
        activeBtn.classList.remove('bg-[var(--bg-primary)]');
        activeBtn.classList.add('border-[var(--border-focus)]', 'bg-[var(--bg-secondary)]', 'ring-2', 'ring-emerald-500');
    }
    updateCoverPreview();
}

function updateCoverPreview() {
    const isEnabled = document.getElementById('designerCoverEnableCheck')?.checked || false;
    const docTitle = document.getElementById('designerDocTitleInput')?.value || 'PROPUESTA ECONÓMICA Y TÉCNICA';
    const subtitle = document.getElementById('designerSubtitleInput')?.value || 'Provisión e Instalación de Equipos';
    const project = document.getElementById('designerProjectNameInput')?.value || 'Proyecto General';
    const watermark = document.getElementById('designerWatermarkInput')?.value || '';
    const color = document.getElementById('designerAccentColorInput')?.value || '#10B981';

    const colorText = document.getElementById('designerAccentColorText');
    if (colorText) colorText.value = color;

    const previewTitle = document.getElementById('previewTitle');
    const previewSubtitle = document.getElementById('previewSubtitle');
    const previewProject = document.getElementById('previewProject');
    const previewClient = document.getElementById('previewClient');
    const previewCompany = document.getElementById('previewCompany');
    const previewCode = document.getElementById('previewCode');
    const previewWatermark = document.getElementById('previewWatermark');
    const previewTopBar = document.getElementById('previewTopBar');
    const badge = document.getElementById('previewStyleBadge');

    if (previewTitle) previewTitle.textContent = docTitle;
    if (previewSubtitle) previewSubtitle.textContent = subtitle;
    if (previewProject) previewProject.textContent = project;

    const clientInput = document.getElementById('clientNameInput')?.value;
    if (previewClient) previewClient.textContent = clientInput || 'Cliente Demo';

    const companySelect = document.getElementById('companySelect')?.value;
    if (previewCompany) previewCompany.textContent = companySelect || 'EMPRESA EMISORA';

    const qNumInput = document.getElementById('quotationNumberInput')?.value;
    if (previewCode) previewCode.textContent = qNumInput || 'COT-001';

    if (previewWatermark) {
        previewWatermark.textContent = watermark;
        previewWatermark.style.display = watermark ? 'flex' : 'none';
    }

    if (previewTopBar) {
        previewTopBar.style.backgroundColor = color;
    }

    if (badge) {
        badge.textContent = currentCoverStyle.replace('_', ' ').toUpperCase();
        badge.style.color = color;
        badge.style.borderColor = color;
    }
}

function getCoverDesignData() {
    return {
        enabled: document.getElementById('designerCoverEnableCheck')?.checked || false,
        cover_style: currentCoverStyle,
        document_title: document.getElementById('designerDocTitleInput')?.value || 'PROPUESTA ECONÓMICA Y TÉCNICA',
        cover_subtitle: document.getElementById('designerSubtitleInput')?.value || '',
        project_name: document.getElementById('designerProjectNameInput')?.value || '',
        project_location: document.getElementById('designerLocationInput')?.value || '',
        watermark_text: document.getElementById('designerWatermarkInput')?.value || '',
        accent_color: document.getElementById('designerAccentColorInput')?.value || '#10B981'
    };
}

function setCoverDesignData(data) {
    if (!data) return;
    const enableCheck = document.getElementById('designerCoverEnableCheck');
    if (enableCheck) enableCheck.checked = !!data.enabled;

    if (data.cover_style) setCoverStyle(data.cover_style);
    if (data.document_title) document.getElementById('designerDocTitleInput').value = data.document_title;
    if (data.cover_subtitle) document.getElementById('designerSubtitleInput').value = data.cover_subtitle;
    if (data.project_name) document.getElementById('designerProjectNameInput').value = data.project_name;
    if (data.project_location) document.getElementById('designerLocationInput').value = data.project_location;
    if (data.watermark_text) document.getElementById('designerWatermarkInput').value = data.watermark_text;
    if (data.accent_color) {
        const input = document.getElementById('designerAccentColorInput');
        if (input) input.value = data.accent_color;
    }
    updateCoverPreview();
}

document.addEventListener('DOMContentLoaded', () => {
    setCoverStyle('corporate_modern');
});
