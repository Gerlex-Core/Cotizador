/**
 * Package: cotizaciones/cctv_calculator.js
 * Multi-camera, Multi-tramo, Distribution Box, Rack, Custom Macros, and .cotz Persistence Engine.
 */

let cctvCameraCounter = 0;

const CCTV_RATES_PRESETS = {
    economica: {
        base: 35.0,
        caja: 10.0,
        transporte: 25.0,
        rates: { libre: "1.2", ducto: "1.5", grapas: "2.0", pvc: "3.0", canaleta: "4.0", aereo: "3.2" }
    },
    calidad_precio: {
        base: 50.0,
        caja: 15.0,
        transporte: 30.0,
        rates: { libre: "1.5", ducto: "2.0", grapas: "2.5", pvc: "3.8", canaleta: "5.0", aereo: "4.0" }
    },
    premium: {
        base: 70.0,
        caja: 20.0,
        transporte: 40.0,
        rates: { libre: "2.0", ducto: "2.5", grapas: "3.0", pvc: "5.0", canaleta: "6.5", aereo: "5.0" }
    }
};

function openCctvCalculatorModal() {
    const modal = document.getElementById('cctvCalculatorModal');
    if (!modal) return;
    modal.classList.remove('hidden');

    const container = document.getElementById('cctvCamerasContainer');
    if (container && container.children.length === 0) {
        // Initialize with default 1st Camera
        addCctvCameraCard({
            name: 'Cámara 1 (Ubicación General)',
            cajas: 1,
            soporte: false,
            tramos: [{ meters: 15, methodRate: 5.0, riskFactor: 1.2 }]
        });
    } else {
        calculateCctvLaborTotal();
    }
}

function closeCctvCalculatorModal() {
    const modal = document.getElementById('cctvCalculatorModal');
    if (modal) modal.classList.add('hidden');
}

function applyCctvPricePreset(presetKey) {
    const preset = CCTV_RATES_PRESETS[presetKey] || CCTV_RATES_PRESETS.calidad_precio;

    if (document.getElementById('cctvGlobalDefaultBase')) document.getElementById('cctvGlobalDefaultBase').value = preset.base;
    if (document.getElementById('cctvGlobalDefaultCaja')) document.getElementById('cctvGlobalDefaultCaja').value = preset.caja;
    if (document.getElementById('cctvGlobalTransporte')) document.getElementById('cctvGlobalTransporte').value = preset.transporte;

    updateAllCameraBasesFromGlobal();
}

function updateAllCameraBasesFromGlobal() {
    const globalBase = parseFloat(document.getElementById('cctvGlobalDefaultBase').value) || 50;
    const baseInputs = document.querySelectorAll('.cctv-cam-base-input');
    baseInputs.forEach(input => {
        input.value = globalBase;
    });
    calculateCctvLaborTotal();
}

function addCctvCameraCard(initialData = null) {
    cctvCameraCounter++;
    const camId = `cctv_cam_${cctvCameraCounter}`;
    const container = document.getElementById('cctvCamerasContainer');
    if (!container) return;

    const defaultBase = parseFloat(document.getElementById('cctvGlobalDefaultBase').value) || 50;
    const name = initialData && initialData.name ? initialData.name : `Cámara ${cctvCameraCounter}`;
    const baseFee = initialData && initialData.baseFee !== undefined ? initialData.baseFee : defaultBase;
    const cajasCount = initialData && initialData.cajas !== undefined ? initialData.cajas : 1;
    const tieneSoporte = initialData && initialData.soporte !== undefined ? initialData.soporte : false;

    const card = document.createElement('div');
    card.id = camId;
    card.className = "cctv-camera-card bg-[var(--bg-primary)] border border-[var(--border-default)] rounded-2xl p-4 space-y-3 shadow-sm";

    card.innerHTML = `
        <div class="flex items-center justify-between border-b border-[var(--border-default)] pb-2 text-xs">
            <div class="flex items-center space-x-2 flex-1 mr-3">
                <span class="material-symbols-outlined text-lg text-[var(--text-primary)]">videocam</span>
                <input type="text" value="${name}" placeholder="Nombre / Ubicación de la Cámara..." class="cctv-cam-name w-full bg-[var(--bg-secondary)] border border-[var(--border-default)] rounded-xl px-2.5 py-1 text-[var(--text-primary)] font-bold focus:border-[var(--border-focus)] focus:outline-none">
            </div>

            <div class="flex items-center space-x-3">
                <div class="flex items-center space-x-1.5">
                    <span class="text-[11px] text-[var(--text-secondary)]">Base Conexión:</span>
                    <input type="number" value="${baseFee}" min="0" step="5" oninput="calculateCctvLaborTotal()" class="cctv-cam-base-input w-16 bg-[var(--bg-secondary)] border border-[var(--border-default)] rounded-xl px-2 py-1 text-center font-bold text-[var(--text-primary)]">
                    <span class="text-[11px] text-[var(--text-secondary)]">Bs</span>
                </div>
                <div class="flex items-center space-x-1">
                    <button onclick="duplicateCctvCamera('${camId}')" title="Duplicar Cámara" class="p-1 bg-[var(--bg-secondary)] hover:bg-white/10 rounded-lg text-[var(--text-primary)] transition">
                        <span class="material-symbols-outlined text-base">content_copy</span>
                    </button>
                    <button onclick="removeCctvCamera('${camId}')" title="Eliminar Cámara" class="p-1 bg-red-500/20 hover:bg-red-500/30 rounded-lg text-red-400 transition">
                        <span class="material-symbols-outlined text-base">delete</span>
                    </button>
                </div>
            </div>
        </div>

        <!-- Camera Accessories Row (Cajas de Pase & Soporte) -->
        <div class="grid grid-cols-12 gap-2 text-xs items-center bg-[var(--bg-secondary)] p-2.5 rounded-xl border border-[var(--border-default)]">
            <div class="col-span-6 flex items-center space-x-2">
                <span class="material-symbols-outlined text-base text-[var(--text-secondary)]">box</span>
                <label class="text-[11px] font-medium text-[var(--text-secondary)]">Cajas de Distribución / Pase:</label>
                <input type="number" value="${cajasCount}" min="0" step="1" oninput="calculateCctvLaborTotal()" class="cctv-cam-cajas w-14 bg-[var(--bg-primary)] border border-[var(--border-default)] rounded-lg px-1.5 py-0.5 text-center font-bold text-[var(--text-primary)]">
                <span class="text-[10px] text-[var(--text-secondary)]">caja(s)</span>
            </div>

            <div class="col-span-6 flex items-center justify-end">
                <label class="flex items-center space-x-1.5 cursor-pointer">
                    <input type="checkbox" ${tieneSoporte ? 'checked' : ''} onchange="calculateCctvLaborTotal()" class="cctv-cam-soporte w-4 h-4 rounded text-[var(--text-primary)] accent-[var(--text-primary)]">
                    <span class="text-[11px] font-bold text-[var(--text-primary)]">Montaje Brazo / Soporte Especial (+25 Bs)</span>
                </label>
            </div>
        </div>

        <!-- Tramos List Header -->
        <div class="space-y-2 text-xs">
            <div class="flex items-center justify-between">
                <span class="text-[11px] font-bold text-[var(--text-secondary)] uppercase tracking-wider">Tramos de Recorrido de Cable para esta Cámara:</span>
                <button onclick="addCctvTramoRow('${camId}')" class="px-2.5 py-1 bg-[var(--bg-secondary)] border border-[var(--border-default)] hover:bg-white/10 rounded-xl text-[11px] font-bold text-[var(--text-primary)] flex items-center space-x-1 transition">
                    <span class="material-symbols-outlined text-sm">add</span>
                    <span>Agregar Tramo</span>
                </button>
            </div>

            <div id="tramos_container_${camId}" class="space-y-2">
                <!-- Dynamic tramos rows -->
            </div>
        </div>

        <!-- Camera Subtotal Footer -->
        <div class="flex items-center justify-between pt-2 border-t border-[var(--border-default)] text-xs">
            <span class="text-[11px] text-[var(--text-secondary)] italic cctv-cam-summary-label">Subtotal Cámara: 0.00 Bs</span>
            <div class="font-extrabold text-sm text-[var(--text-primary)]">
                Subtotal Cámara: <span class="cctv-cam-subtotal-val text-emerald-400 font-mono">0.00 Bs</span>
            </div>
        </div>
    `;

    container.appendChild(card);

    // Populate initial tramos
    const tramos = initialData && initialData.tramos ? initialData.tramos : [{ meters: 15, methodRate: 5.0, riskFactor: 1.0 }];
    tramos.forEach(t => addCctvTramoRow(camId, t));

    calculateCctvLaborTotal();
}

function addCctvTramoRow(camId, tramoData = null) {
    const tramosContainer = document.getElementById(`tramos_container_${camId}`);
    if (!tramosContainer) return;

    const tramoId = `tramo_${Date.now()}_${Math.random().toString(36).substr(2, 4)}`;

    const meters = tramoData && tramoData.meters !== undefined ? tramoData.meters : 10;
    const methodRate = tramoData && tramoData.methodRate !== undefined ? String(tramoData.methodRate) : "5.0";
    const riskFactor = tramoData && tramoData.riskFactor !== undefined ? String(tramoData.riskFactor) : "1.0";

    const tramoRow = document.createElement('div');
    tramoRow.id = tramoId;
    tramoRow.className = "cctv-tramo-row grid grid-cols-12 gap-2 items-center bg-[var(--bg-secondary)] p-2 rounded-xl border border-[var(--border-default)] text-xs";

    tramoRow.innerHTML = `
        <div class="col-span-2 space-y-0.5">
            <label class="text-[10px] text-[var(--text-secondary)] font-medium">Metros (m):</label>
            <input type="number" value="${meters}" min="0.5" step="1" oninput="calculateCctvLaborTotal()" class="cctv-tramo-meters w-full bg-[var(--bg-primary)] border border-[var(--border-default)] rounded-lg px-2 py-1 text-center font-bold text-[var(--text-primary)]">
        </div>

        <div class="col-span-6 space-y-0.5">
            <label class="text-[10px] text-[var(--text-secondary)] font-medium">Método de Instalación por metro:</label>
            <select onchange="calculateCctvLaborTotal()" class="cctv-tramo-metodo w-full bg-[var(--bg-primary)] border border-[var(--border-default)] rounded-lg px-2 py-1 font-semibold text-[var(--text-primary)]">
                <option value="1.5" ${methodRate == "1.5" ? 'selected' : ''}>Solo Tirado de Cable (Libre / Techo) (1.50 Bs/m)</option>
                <option value="2.0" ${methodRate == "2.0" ? 'selected' : ''}>Cablear en Ducto Existente (2.00 Bs/m)</option>
                <option value="2.5" ${methodRate == "2.5" ? 'selected' : ''}>Grapas / Tachuelas en Pared (2.50 Bs/m)</option>
                <option value="3.8" ${methodRate == "3.8" ? 'selected' : ''}>Montaje Tubo PVC + Abrazaderas (3.80 Bs/m)</option>
                <option value="5.0" ${methodRate == "5.0" ? 'selected' : ''}>Cable Canal / Canaleta (5.00 Bs/m)</option>
                <option value="4.0" ${methodRate == "4.0" ? 'selected' : ''}>Tendido Aéreo Exterior con Piola (4.00 Bs/m)</option>
            </select>
        </div>

        <div class="col-span-3 space-y-0.5">
            <label class="text-[10px] text-[var(--text-secondary)] font-medium">Altura / Riesgo:</label>
            <select onchange="calculateCctvLaborTotal()" class="cctv-tramo-riesgo w-full bg-[var(--bg-primary)] border border-[var(--border-default)] rounded-lg px-2 py-1 font-semibold text-[var(--text-primary)]">
                <option value="1.0" ${riskFactor == "1.0" ? 'selected' : ''}>Piso / Pared Baja (1.0x)</option>
                <option value="1.2" ${riskFactor == "1.2" ? 'selected' : ''}>Escalera / Media (1.2x)</option>
                <option value="1.5" ${riskFactor == "1.5" ? 'selected' : ''}>Techo Peligroso (1.5x)</option>
            </select>
        </div>

        <div class="col-span-1 text-center pt-3">
            <button onclick="removeCctvTramoRow('${camId}', '${tramoId}')" title="Eliminar Tramo" class="p-1 hover:bg-red-500/20 rounded-lg text-red-400 transition">
                <span class="material-symbols-outlined text-sm">close</span>
            </button>
        </div>
    `;

    tramosContainer.appendChild(tramoRow);
    calculateCctvLaborTotal();
}

function removeCctvTramoRow(camId, tramoId) {
    const tramo = document.getElementById(tramoId);
    if (tramo) {
        tramo.remove();
        calculateCctvLaborTotal();
    }
}

function addCctvCustomMacroRow(macroData = null) {
    const container = document.getElementById('cctvCustomMacrosContainer');
    if (!container) return;

    const macroId = `macro_${Date.now()}_${Math.random().toString(36).substr(2, 4)}`;

    const name = macroData && macroData.name ? macroData.name : 'Perforación de Muro / Trabajo Especial';
    const qty = macroData && macroData.qty !== undefined ? macroData.qty : 1;
    const price = macroData && macroData.price !== undefined ? macroData.price : 40.0;

    const row = document.createElement('div');
    row.id = macroId;
    row.className = "cctv-macro-row grid grid-cols-12 gap-2 items-center bg-[var(--bg-secondary)] p-2 rounded-xl border border-[var(--border-default)] text-xs";

    row.innerHTML = `
        <div class="col-span-6 space-y-0.5">
            <label class="text-[10px] text-[var(--text-secondary)] font-medium">Nombre del Macro / Servicio Especial:</label>
            <input type="text" value="${name}" placeholder="Descripción del cobro especial..." oninput="calculateCctvLaborTotal()" class="cctv-macro-name w-full bg-[var(--bg-primary)] border border-[var(--border-default)] rounded-lg px-2.5 py-1 font-semibold text-[var(--text-primary)]">
        </div>

        <div class="col-span-2 space-y-0.5">
            <label class="text-[10px] text-[var(--text-secondary)] font-medium">Cantidad:</label>
            <input type="number" value="${qty}" min="1" step="1" oninput="calculateCctvLaborTotal()" class="cctv-macro-qty w-full bg-[var(--bg-primary)] border border-[var(--border-default)] rounded-lg px-2 py-1 text-center font-bold text-[var(--text-primary)]">
        </div>

        <div class="col-span-3 space-y-0.5">
            <label class="text-[10px] text-[var(--text-secondary)] font-medium">Precio Unit. (Bs):</label>
            <input type="number" value="${price}" min="0" step="5" oninput="calculateCctvLaborTotal()" class="cctv-macro-price w-full bg-[var(--bg-primary)] border border-[var(--border-default)] rounded-lg px-2 py-1 text-right font-bold text-[var(--text-primary)]">
        </div>

        <div class="col-span-1 text-center pt-3">
            <button onclick="removeCctvCustomMacroRow('${macroId}')" title="Eliminar Macro" class="p-1 hover:bg-red-500/20 rounded-lg text-red-400 transition">
                <span class="material-symbols-outlined text-sm">close</span>
            </button>
        </div>
    `;

    container.appendChild(row);
    calculateCctvLaborTotal();
}

function removeCctvCustomMacroRow(macroId) {
    const row = document.getElementById(macroId);
    if (row) {
        row.remove();
        calculateCctvLaborTotal();
    }
}

function duplicateCctvCamera(camId) {
    const originalCard = document.getElementById(camId);
    if (!originalCard) return;

    const originalName = originalCard.querySelector('.cctv-cam-name').value;
    const originalBase = parseFloat(originalCard.querySelector('.cctv-cam-base-input').value) || 50;
    const originalCajas = parseInt(originalCard.querySelector('.cctv-cam-cajas').value) || 0;
    const originalSoporte = originalCard.querySelector('.cctv-cam-soporte').checked;

    const tramosData = [];
    originalCard.querySelectorAll('.cctv-tramo-row').forEach(row => {
        tramosData.push({
            meters: parseFloat(row.querySelector('.cctv-tramo-meters').value) || 10,
            methodRate: parseFloat(row.querySelector('.cctv-tramo-metodo').value) || 5.0,
            riskFactor: parseFloat(row.querySelector('.cctv-tramo-riesgo').value) || 1.0
        });
    });

    addCctvCameraCard({
        name: `${originalName} (Copia)`,
        baseFee: originalBase,
        cajas: originalCajas,
        soporte: originalSoporte,
        tramos: tramosData
    });
}

function removeCctvCamera(camId) {
    const card = document.getElementById(camId);
    if (card) {
        card.remove();
        calculateCctvLaborTotal();
    }
}

function calculateCctvLaborTotal() {
    const cameraCards = document.querySelectorAll('.cctv-camera-card');
    const globalCajaPrice = parseFloat(document.getElementById('cctvGlobalDefaultCaja').value) || 15;
    
    let totalMetersAll = 0;
    let sumCamarasSubtotal = 0;
    const cameraResults = [];

    cameraCards.forEach(card => {
        const name = card.querySelector('.cctv-cam-name').value.trim() || 'Cámara';
        const baseFee = parseFloat(card.querySelector('.cctv-cam-base-input').value) || 0;
        const cajasCount = Math.max(0, parseInt(card.querySelector('.cctv-cam-cajas').value) || 0);
        const tieneSoporte = card.querySelector('.cctv-cam-soporte').checked;

        const cajasCost = cajasCount * globalCajaPrice;
        const soporteCost = tieneSoporte ? 25.0 : 0.0;

        let camMeters = 0;
        let camTramosCost = 0;
        const tramosInfo = [];

        const tramoRows = card.querySelectorAll('.cctv-tramo-row');
        tramoRows.forEach(row => {
            const m = Math.max(0, parseFloat(row.querySelector('.cctv-tramo-meters').value) || 0);
            const precioMetodo = parseFloat(row.querySelector('.cctv-tramo-metodo').value) || 5.0;
            const factorRiesgo = parseFloat(row.querySelector('.cctv-tramo-riesgo').value) || 1.0;

            const tramoCost = m * precioMetodo * factorRiesgo;
            camMeters += m;
            camTramosCost += tramoCost;

            let metodoLabel = "Canaleta";
            if (precioMetodo === 1.5) metodoLabel = "Libre";
            else if (precioMetodo === 2.0) metodoLabel = "Ducto";
            else if (precioMetodo === 2.5) metodoLabel = "Grapas";
            else if (precioMetodo === 3.8) metodoLabel = "Tubo PVC";
            else if (precioMetodo === 4.0) metodoLabel = "Aéreo";

            tramosInfo.push(`${m}m ${metodoLabel} (${factorRiesgo}x)`);
        });

        const camTotalSubtotal = baseFee + cajasCost + soporteCost + camTramosCost;
        sumCamarasSubtotal += camTotalSubtotal;
        totalMetersAll += camMeters;

        // Update card UI
        const subtotalEl = card.querySelector('.cctv-cam-subtotal-val');
        if (subtotalEl) subtotalEl.textContent = `${camTotalSubtotal.toFixed(2)} Bs`;

        const summaryLabelEl = card.querySelector('.cctv-cam-summary-label');
        if (summaryLabelEl) {
            let accInfo = [];
            if (cajasCount > 0) accInfo.push(`${cajasCount} caja(s)`);
            if (tieneSoporte) accInfo.push(`soporte especial`);
            const accText = accInfo.length > 0 ? ` + ${accInfo.join(', ')}` : '';
            summaryLabelEl.textContent = `Base: ${baseFee} Bs${accText} | Tramos (${camMeters}m): ${camTramosCost.toFixed(2)} Bs`;
        }

        cameraResults.push({
            name,
            baseFee,
            cajasCount,
            cajasCost,
            tieneSoporte,
            camMeters,
            camTotalSubtotal,
            tramosInfo
        });
    });

    // Central Infrastructure & Rack Costs
    const rackCost = parseFloat(document.getElementById('cctvRackSelect').value) || 0;
    const patchCost = document.getElementById('cctvPatchPanelCheck').checked ? 50.0 : 0.0;
    const dvrConfigCost = document.getElementById('cctvDvrConfigCheck').checked ? 60.0 : 0.0;

    // Custom Macros Costs
    let customMacrosSubtotal = 0;
    const customMacroRows = document.querySelectorAll('.cctv-macro-row');
    const customMacrosList = [];

    customMacroRows.forEach(row => {
        const macroName = row.querySelector('.cctv-macro-name').value.trim() || 'Servicio Especial';
        const qty = Math.max(1, parseInt(row.querySelector('.cctv-macro-qty').value) || 1);
        const price = Math.max(0, parseFloat(row.querySelector('.cctv-macro-price').value) || 0);
        const rowTotal = qty * price;

        customMacrosSubtotal += rowTotal;
        customMacrosList.push({ name: macroName, qty, price, total: rowTotal });
    });

    const totalRackConfigMacros = rackCost + patchCost + dvrConfigCost + customMacrosSubtotal;

    const transporte = Math.max(0, parseFloat(document.getElementById('cctvGlobalTransporte').value) || 0);
    const factorGarantia = parseFloat(document.getElementById('cctvGlobalGarantia').value) || 1.0;

    const totalConTransporte = sumCamarasSubtotal + totalRackConfigMacros + transporte;
    const totalFinalGeneral = totalConTransporte * factorGarantia;

    // Update Global Summary UI
    if (document.getElementById('cctvSummaryStats')) {
        document.getElementById('cctvSummaryStats').textContent = `${cameraCards.length} Cámaras | ${totalMetersAll}m Cableado | ${customMacrosList.length} Macro(s)`;
    }
    if (document.getElementById('cctvDispSubtotalCamaras')) {
        document.getElementById('cctvDispSubtotalCamaras').textContent = `${sumCamarasSubtotal.toFixed(2)} Bs`;
    }
    if (document.getElementById('cctvDispRackConfig')) {
        document.getElementById('cctvDispRackConfig').textContent = `${totalRackConfigMacros.toFixed(2)} Bs`;
    }
    if (document.getElementById('cctvDispGarantia')) {
        let pct = "0%";
        if (factorGarantia === 1.15) pct = "15%";
        else if (factorGarantia === 1.25) pct = "25%";
        document.getElementById('cctvDispGarantia').textContent = `${transporte} Bs (${factorGarantia}x)`;
    }
    if (document.getElementById('cctvTotalCalculado')) {
        document.getElementById('cctvTotalCalculado').textContent = `${totalFinalGeneral.toFixed(2)} ${typeof currentCurrency !== 'undefined' ? currentCurrency : 'Bs'}`;
    }

    return {
        numCamaras: cameraCards.length,
        totalMetersAll,
        sumCamarasSubtotal,
        totalRackConfigMacros,
        rackCost,
        patchCost,
        dvrConfigCost,
        customMacrosSubtotal,
        customMacrosList,
        transporte,
        factorGarantia,
        totalFinalGeneral,
        cameraResults
    };
}

/**
 * Collects JSON-serializable snapshot of calculator state for saving in .cotz files and SQLite DB.
 */
function collectCctvCalculatorData() {
    const calc = calculateCctvLaborTotal();
    
    const camerasData = [];
    document.querySelectorAll('.cctv-camera-card').forEach(card => {
        const name = card.querySelector('.cctv-cam-name').value;
        const baseFee = parseFloat(card.querySelector('.cctv-cam-base-input').value) || 50;
        const cajas = parseInt(card.querySelector('.cctv-cam-cajas').value) || 0;
        const soporte = card.querySelector('.cctv-cam-soporte').checked;

        const tramos = [];
        card.querySelectorAll('.cctv-tramo-row').forEach(row => {
            tramos.push({
                meters: parseFloat(row.querySelector('.cctv-tramo-meters').value) || 10,
                methodRate: parseFloat(row.querySelector('.cctv-tramo-metodo').value) || 5.0,
                riskFactor: parseFloat(row.querySelector('.cctv-tramo-riesgo').value) || 1.0
            });
        });

        camerasData.push({ name, baseFee, cajas, soporte, tramos });
    });

    const macrosData = [];
    document.querySelectorAll('.cctv-macro-row').forEach(row => {
        macrosData.push({
            name: row.querySelector('.cctv-macro-name').value,
            qty: parseInt(row.querySelector('.cctv-macro-qty').value) || 1,
            price: parseFloat(row.querySelector('.cctv-macro-price').value) || 0
        });
    });

    return {
        preset: document.getElementById('cctvPresetSelect') ? document.getElementById('cctvPresetSelect').value : 'calidad_precio',
        globalBase: parseFloat(document.getElementById('cctvGlobalDefaultBase').value) || 50,
        globalCaja: parseFloat(document.getElementById('cctvGlobalDefaultCaja').value) || 15,
        transporte: parseFloat(document.getElementById('cctvGlobalTransporte').value) || 30,
        garantia: parseFloat(document.getElementById('cctvGlobalGarantia').value) || 1.15,
        rackSelect: parseFloat(document.getElementById('cctvRackSelect').value) || 0,
        patchPanel: document.getElementById('cctvPatchPanelCheck').checked,
        dvrConfig: document.getElementById('cctvDvrConfigCheck').checked,
        cameras: camerasData,
        customMacros: macrosData,
        totalFinalGeneral: calc.totalFinalGeneral
    };
}

/**
 * Restores full CCTV calculator state when opening a .cotz file or loading from SQLite DB.
 */
function restoreCctvCalculatorData(cctvData) {
    if (!cctvData) return;

    if (cctvData.preset && document.getElementById('cctvPresetSelect')) document.getElementById('cctvPresetSelect').value = cctvData.preset;
    if (cctvData.globalBase !== undefined && document.getElementById('cctvGlobalDefaultBase')) document.getElementById('cctvGlobalDefaultBase').value = cctvData.globalBase;
    if (cctvData.globalCaja !== undefined && document.getElementById('cctvGlobalDefaultCaja')) document.getElementById('cctvGlobalDefaultCaja').value = cctvData.globalCaja;
    if (cctvData.transporte !== undefined && document.getElementById('cctvGlobalTransporte')) document.getElementById('cctvGlobalTransporte').value = cctvData.transporte;
    if (cctvData.garantia !== undefined && document.getElementById('cctvGlobalGarantia')) document.getElementById('cctvGlobalGarantia').value = cctvData.garantia;

    if (cctvData.rackSelect !== undefined && document.getElementById('cctvRackSelect')) document.getElementById('cctvRackSelect').value = cctvData.rackSelect;
    if (cctvData.patchPanel !== undefined && document.getElementById('cctvPatchPanelCheck')) document.getElementById('cctvPatchPanelCheck').checked = !!cctvData.patchPanel;
    if (cctvData.dvrConfig !== undefined && document.getElementById('cctvDvrConfigCheck')) document.getElementById('cctvDvrConfigCheck').checked = !!cctvData.dvrConfig;

    // Restore Cameras
    const camContainer = document.getElementById('cctvCamerasContainer');
    if (camContainer) camContainer.innerHTML = '';
    cctvCameraCounter = 0;

    if (cctvData.cameras && cctvData.cameras.length > 0) {
        cctvData.cameras.forEach(cam => addCctvCameraCard(cam));
    }

    // Restore Custom Macros
    const macroContainer = document.getElementById('cctvCustomMacrosContainer');
    if (macroContainer) macroContainer.innerHTML = '';

    if (cctvData.customMacros && cctvData.customMacros.length > 0) {
        cctvData.customMacros.forEach(m => addCctvCustomMacroRow(m));
    }

    calculateCctvLaborTotal();
}

function addCctvLaborToQuotation(mode = 'single') {
    const calc = calculateCctvLaborTotal();
    if (calc.numCamaras === 0 && calc.totalRackConfigMacros === 0) {
        alert("Por favor agregue al menos una cámara o servicio de infraestructura.");
        return;
    }

    let garantiaPct = "0%";
    if (calc.factorGarantia === 1.15) garantiaPct = "15%";
    else if (calc.factorGarantia === 1.25) garantiaPct = "25%";

    if (mode === 'single') {
        // Inject 1 single summarized line item into quotation
        let rackDetails = [];
        if (calc.rackCost > 0) rackDetails.push("Rack Telecomunicaciones");
        if (calc.patchCost > 0) rackDetails.push("Patch Panel/Switch");
        if (calc.dvrConfigCost > 0) rackDetails.push("Config DVR/P2P");
        if (calc.customMacrosList.length > 0) rackDetails.push(`${calc.customMacrosList.length} Macro(s)`);

        const rackText = rackDetails.length > 0 ? ` + Central (${rackDetails.join(', ')})` : '';
        const description = `Servicio de Instalación y Mano de Obra CCTV: ${calc.numCamaras} Cámaras | Cableado Total: ${calc.totalMetersAll}m${rackText} | Incluye pasajes (${calc.transporte} Bs) y Garantía (${garantiaPct})`;
        
        addProductRow(description, 1, 'servicio (srv)', parseFloat(calc.totalFinalGeneral.toFixed(2)));
    } else if (mode === 'per_camera') {
        // Inject 1 detailed line item per camera + 1 line for Central Rack/Macros if present
        const transportePerCam = calc.numCamaras > 0 ? (calc.transporte / calc.numCamaras) : 0;

        calc.cameraResults.forEach(cam => {
            const camFinalPrice = (cam.camTotalSubtotal + transportePerCam) * calc.factorGarantia;
            const tramosDesc = cam.tramosInfo.join(' + ') || `${cam.camMeters}m`;
            let cajasText = cam.cajasCount > 0 ? ` | ${cam.cajasCount} Caja(s) Pase` : '';
            let soporteText = cam.tieneSoporte ? ' | Soporte Especial' : '';

            const description = `Mano de Obra CCTV - ${cam.name}: Base (${cam.baseFee} Bs), Tramos: ${tramosDesc}${cajasText}${soporteText}`;
            addProductRow(description, 1, 'servicio (srv)', parseFloat(camFinalPrice.toFixed(2)));
        });

        if (calc.totalRackConfigMacros > 0) {
            let rackDetails = [];
            if (calc.rackCost > 0) rackDetails.push("Rack Telecomunicaciones");
            if (calc.patchCost > 0) rackDetails.push("Patch Panel & Switch");
            if (calc.dvrConfigCost > 0) rackDetails.push("Config DVR/App P2P");
            calc.customMacrosList.forEach(m => rackDetails.push(`${m.name} (x${m.qty})`));

            const rackFinalPrice = calc.totalRackConfigMacros * calc.factorGarantia;
            const rackDescription = `Servicios de Infraestructura Central & Macros: ${rackDetails.join(' + ')}`;
            addProductRow(rackDescription, 1, 'servicio (srv)', parseFloat(rackFinalPrice.toFixed(2)));
        }
    }

    closeCctvCalculatorModal();
}
