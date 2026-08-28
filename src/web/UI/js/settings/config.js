/**
 * Package: settings/config.js
 * PDF page margins, currency default, font selection, watermarks, and global config persistence.
 */

async function loadAppConfig() {
    try {
        const res = await fetch((window.ENV?.API_BASE_URL || '') + '/api/config');
        const data = await res.json();
        appConfig = data.config || {};
        availableUnits = data.units || {};
        currentCurrency = appConfig.moneda || "Bolivianos (Bs)";
        
        if (document.getElementById('configCurrencyInput')) document.getElementById('configCurrencyInput').value = currentCurrency;
        if (document.getElementById('configPreparedByInput')) document.getElementById('configPreparedByInput').value = appConfig.prepared_by || "";
        if (document.getElementById('configFontSelect')) document.getElementById('configFontSelect').value = appConfig.fuente || "Roboto";
        
        if (document.getElementById('marginTopInput')) document.getElementById('marginTopInput').value = appConfig.margin_top || 40;
        if (document.getElementById('marginBottomInput')) document.getElementById('marginBottomInput').value = appConfig.margin_bottom || 40;
        if (document.getElementById('marginLeftInput')) document.getElementById('marginLeftInput').value = appConfig.margin_left || 40;
        if (document.getElementById('marginRightInput')) document.getElementById('marginRightInput').value = appConfig.margin_right || 40;

        if (document.getElementById('watermarkEnabledCheck')) document.getElementById('watermarkEnabledCheck').checked = appConfig.watermark_enabled || false;
        if (document.getElementById('watermarkTextInput')) document.getElementById('watermarkTextInput').value = appConfig.watermark_text || "";
        if (document.getElementById('watermarkOpacityInput')) {
            document.getElementById('watermarkOpacityInput').value = appConfig.watermark_opacity || 15;
            if (document.getElementById('watermarkOpacityLabel')) document.getElementById('watermarkOpacityLabel').textContent = (appConfig.watermark_opacity || 15) + '%';
        }
    } catch (e) {
        console.error("Error loading config:", e);
    }
}

async function saveGlobalConfig() {
    const payload = {
        moneda: getVal('configCurrencyInput', 'Bolivianos (Bs)'),
        prepared_by: getVal('configPreparedByInput', ''),
        fuente: getVal('configFontSelect', 'Roboto'),
        margin_top: getNumVal('marginTopInput', 40),
        margin_bottom: getNumVal('marginBottomInput', 40),
        margin_left: getNumVal('marginLeftInput', 40),
        margin_right: getNumVal('marginRightInput', 40),
        watermark_enabled: getCheckVal('watermarkEnabledCheck'),
        watermark_text: getVal('watermarkTextInput', ''),
        watermark_opacity: getNumVal('watermarkOpacityInput', 15)
    };

    try {
        const res = await fetch((window.ENV?.API_BASE_URL || '') + '/api/config', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (res.ok) {
            alert("Configuración global guardada correctamente.");
            currentCurrency = payload.moneda;
            calculateTotals();
        } else {
            alert("Error al guardar configuración.");
        }
    } catch (e) {
        alert("Error al guardar configuración: " + e.message);
    }
}
