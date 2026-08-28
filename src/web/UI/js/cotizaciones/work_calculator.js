/**
 * Package: cotizaciones/work_calculator.js
 * Comprehensive Work & Labor Calculator Engine for CCTV, Structured Cabling, Racks, Config, and Civil Works.
 */

let workCameraCounter = 0;

const WORK_RATES_PRESETS = {
    economica: {
        base: 35.0,
        caja: 10.0,
        transporte: 25.0,
        utpPoint: 25.0,
        fiberSplice: 20.0,
        rates: { libre: "1.2", ducto: "1.5", grapas: "2.0", pvc: "3.0", canaleta: "4.0", aereo: "3.2" }
    },
    calidad_precio: {
        base: 50.0,
        caja: 15.0,
        transporte: 30.0,
        utpPoint: 35.0,
        fiberSplice: 25.0,
        rates: { libre: "1.5", ducto: "2.0", grapas: "2.5", pvc: "3.8", canaleta: "5.0", aereo: "4.0" }
    },
    premium: {
        base: 70.0,
        caja: 20.0,
        transporte: 40.0,
        utpPoint: 45.0,
        fiberSplice: 35.0,
        rates: { libre: "2.0", ducto: "2.5", grapas: "3.0", pvc: "5.0", canaleta: "6.5", aereo: "5.0" }
    }
};

function showWorkCalculatorView() {
    const pages = document.querySelectorAll('.workspace-page');
    pages.forEach(p => p.classList.add('hidden'));

    const workView = document.getElementById('workCalculatorView');
    if (workView) {
        workView.classList.remove('hidden');

        const container = document.getElementById('workCamerasContainer');
        if (container && container.children.length === 0) {
            addWorkCameraCard({
                name: 'Cámara 1 (Ubicación General)',
                cajas: 1,
                soporte: false,
                tramos: [{ meters: 15, methodRate: 5.0, riskFactor: 1.2 }]
            });
        } else {
            calculateWorkLaborTotal();
        }
    }
}

function hideWorkCalculatorView() {
    const workView = document.getElementById('workCalculatorView');
    if (workView) workView.classList.add('hidden');

    const page0 = document.getElementById('page0');
    if (page0) page0.classList.remove('hidden');
}

function toggleCategorySection(categoryKey) {
    const check = document.getElementById(`workCat${categoryKey.charAt(0).toUpperCase() + categoryKey.slice(1)}Check`);
    const body = document.getElementById(`workCat${categoryKey.charAt(0).toUpperCase() + categoryKey.slice(1)}Body`);

    if (body && check) {
        if (check.checked) {
            body.classList.remove('opacity-40', 'pointer-events-none');
        } else {
            body.classList.add('opacity-40', 'pointer-events-none');
        }
    }
    calculateWorkLaborTotal();
}

function applyWorkPricePreset(presetKey) {
    const preset = WORK_RATES_PRESETS[presetKey] || WORK_RATES_PRESETS.calidad_precio;

    if (document.getElementById('workGlobalDefaultBase')) document.getElementById('workGlobalDefaultBase').value = preset.base;
    if (document.getElementById('workGlobalDefaultCaja')) document.getElementById('workGlobalDefaultCaja').value = preset.caja;
    if (document.getElementById('workGlobalTransporte')) document.getElementById('workGlobalTransporte').value = preset.transporte;

    updateAllCameraBasesFromGlobal();
}

function updateAllCameraBasesFromGlobal() {
    const globalBase = parseFloat(document.getElementById('workGlobalDefaultBase').value) || 50;
    const baseInputs = document.querySelectorAll('.work-cam-base-input');
    baseInputs.forEach(input => {
        input.value = globalBase;
    });
    calculateWorkLaborTotal();
}

function addWorkCameraCard(initialData = null) {
    workCameraCounter++;
    const camId = `work_cam_${workCameraCounter}`;
    const container = document.getElementById('workCamerasContainer');
    if (!container) return;

    const defaultBase = parseFloat(document.getElementById('workGlobalDefaultBase').value) || 50;
    const name = initialData && initialData.name ? initialData.name : `Cámara ${workCameraCounter}`;
    const baseFee = initialData && initialData.baseFee !== undefined ? initialData.baseFee : defaultBase;
    const cajasCount = initialData && initialData.cajas !== undefined ? initialData.cajas : 1;
    const tieneSoporte = initialData && initialData.soporte !== undefined ? initialData.soporte : false;

    const card = document.createElement('div');
    card.id = camId;
    card.className = "work-camera-card bg-[var(--bg-primary)] border border-[var(--border-default)] rounded-2xl p-4 space-y-3 shadow-sm";

    card.innerHTML = `
        <div class="flex items-center justify-between border-b border-[var(--border-default)] pb-2 text-xs">
            <div class="flex items-center space-x-2 flex-1 mr-3">
                <span class="material-symbols-outlined text-lg text-[var(--text-primary)]">videocam</span>
                <input type="text" value="${name}" placeholder="Nombre / Ubicación de la Cámara..." class="work-cam-name w-full bg-[var(--bg-secondary)] border border-[var(--border-default)] rounded-xl px-2.5 py-1 text-[var(--text-primary)] font-bold focus:border-[var(--border-focus)] focus:outline-none">
            </div>

            <div class="flex items-center space-x-3">
                <div class="flex items-center space-x-1.5">
                    <span class="text-[11px] text-[var(--text-secondary)]">Base Conexión:</span>
                    <input type="number" value="${baseFee}" min="0" step="5" oninput="calculateWorkLaborTotal()" class="work-cam-base-input w-16 bg-[var(--bg-secondary)] border border-[var(--border-default)] rounded-xl px-2 py-1 text-center font-bold text-[var(--text-primary)]">
                    <span class="text-[11px] text-[var(--text-secondary)]">Bs</span>
                </div>
                <div class="flex items-center space-x-1">
                    <button onclick="duplicateWorkCamera('${camId}')" title="Duplicar Cámara" class="p-1 bg-[var(--bg-secondary)] hover:bg-white/10 rounded-lg text-[var(--text-primary)] transition">
                        <span class="material-symbols-outlined text-base">content_copy</span>
                    </button>
                    <button onclick="removeWorkCamera('${camId}')" title="Eliminar Cámara" class="p-1 bg-red-500/20 hover:bg-red-500/30 rounded-lg text-red-400 transition">
                        <span class="material-symbols-outlined text-base">delete</span>
                    </button>
                </div>
            </div>
        </div>

        <!-- Camera Accessories Row (Cajas de Pase & Soporte) -->
        <div class="grid grid-cols-12 gap-2 text-xs items-center bg-[var(--bg-secondary)] p-2.5 rounded-xl border border-[var(--border-default)]">
            <div class="col-span-6 flex items-center space-x-2">
                <span class="material-symbols-outlined text-base text-[var(--text-secondary)]">box</span>
                <label class="text-[11px] font-medium text-[var(--text-secondary)]">Cajas de Pase / Distribución:</label>
                <input type="number" value="${cajasCount}" min="0" step="1" oninput="calculateWorkLaborTotal()" class="work-cam-cajas w-14 bg-[var(--bg-primary)] border border-[var(--border-default)] rounded-lg px-1.5 py-0.5 text-center font-bold text-[var(--text-primary)]">
                <span class="text-[10px] text-[var(--text-secondary)]">caja(s)</span>
            </div>

            <div class="col-span-6 flex items-center justify-end">
                <label class="flex items-center space-x-1.5 cursor-pointer">
                    <input type="checkbox" ${tieneSoporte ? 'checked' : ''} onchange="calculateWorkLaborTotal()" class="work-cam-soporte w-4 h-4 rounded text-[var(--text-primary)] accent-[var(--text-primary)]">
                    <span class="text-[11px] font-bold text-[var(--text-primary)]">Montaje Brazo / Soporte Especial (+25 Bs)</span>
                </label>
            </div>
        </div>

        <!-- Tramos List Header -->
        <div class="space-y-2 text-xs">
            <div class="flex items-center justify-between">
                <span class="text-[11px] font-bold text-[var(--text-secondary)] uppercase tracking-wider">Tramos de Recorrido de Cable para esta Cámara:</span>
                <button onclick="addWorkTramoRow('${camId}')" class="px-2.5 py-1 bg-[var(--bg-secondary)] border border-[var(--border-default)] hover:bg-white/10 rounded-xl text-[11px] font-bold text-[var(--text-primary)] flex items-center space-x-1 transition">
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
            <span class="text-[11px] text-[var(--text-secondary)] italic work-cam-summary-label">Subtotal Cámara: 0.00 Bs</span>
            <div class="font-extrabold text-sm text-[var(--text-primary)]">
                Subtotal Cámara: <span class="work-cam-subtotal-val text-emerald-400 font-mono">0.00 Bs</span>
            </div>
        </div>
    `;

    container.appendChild(card);

    // Populate initial tramos
    const tramos = initialData && initialData.tramos ? initialData.tramos : [{ meters: 15, methodRate: 5.0, riskFactor: 1.0 }];
    tramos.forEach(t => addWorkTramoRow(camId, t));

    calculateWorkLaborTotal();
}

function addWorkTramoRow(camId, tramoData = null) {
    const tramosContainer = document.getElementById(`tramos_container_${camId}`);
    if (!tramosContainer) return;

    const tramoId = `tramo_${Date.now()}_${Math.random().toString(36).substr(2, 4)}`;

    const meters = tramoData && tramoData.meters !== undefined ? tramoData.meters : 10;
    const methodRate = tramoData && tramoData.methodRate !== undefined ? String(tramoData.methodRate) : "5.0";
    const riskFactor = tramoData && tramoData.riskFactor !== undefined ? String(tramoData.riskFactor) : "1.0";

    const tramoRow = document.createElement('div');
    tramoRow.id = tramoId;
    tramoRow.className = "work-tramo-row grid grid-cols-12 gap-2 items-center bg-[var(--bg-secondary)] p-2 rounded-xl border border-[var(--border-default)] text-xs";

    tramoRow.innerHTML = `
        <div class="col-span-2 space-y-0.5">
            <label class="text-[10px] text-[var(--text-secondary)] font-medium">Metros (m):</label>
            <input type="number" value="${meters}" min="0.5" step="1" oninput="calculateWorkLaborTotal()" class="work-tramo-meters w-full bg-[var(--bg-primary)] border border-[var(--border-default)] rounded-lg px-2 py-1 text-center font-bold text-[var(--text-primary)]">
        </div>

        <div class="col-span-6 space-y-0.5">
            <label class="text-[10px] text-[var(--text-secondary)] font-medium">Método de Instalación por metro:</label>
            <select onchange="calculateWorkLaborTotal()" class="work-tramo-metodo w-full bg-[var(--bg-primary)] border border-[var(--border-default)] rounded-lg px-2 py-1 font-semibold text-[var(--text-primary)]">
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
            <select onchange="calculateWorkLaborTotal()" class="work-tramo-riesgo w-full bg-[var(--bg-primary)] border border-[var(--border-default)] rounded-lg px-2 py-1 font-semibold text-[var(--text-primary)]">
                <option value="1.0" ${riskFactor == "1.0" ? 'selected' : ''}>Piso / Pared Baja (1.0x)</option>
                <option value="1.2" ${riskFactor == "1.2" ? 'selected' : ''}>Escalera / Media (1.2x)</option>
                <option value="1.5" ${riskFactor == "1.5" ? 'selected' : ''}>Techo Peligroso (1.5x)</option>
            </select>
        </div>

        <div class="col-span-1 text-center pt-3">
            <button onclick="removeWorkTramoRow('${camId}', '${tramoId}')" title="Eliminar Tramo" class="p-1 hover:bg-red-500/20 rounded-lg text-red-400 transition">
                <span class="material-symbols-outlined text-sm">close</span>
            </button>
        </div>
    `;

    tramosContainer.appendChild(tramoRow);
    calculateWorkLaborTotal();
}

function removeWorkTramoRow(camId, tramoId) {
    const tramo = document.getElementById(tramoId);
    if (tramo) {
        tramo.remove();
        calculateWorkLaborTotal();
    }
}

function duplicateWorkCamera(camId) {
    const originalCard = document.getElementById(camId);
    if (!originalCard) return;

    const originalName = originalCard.querySelector('.work-cam-name').value;
    const originalBase = parseFloat(originalCard.querySelector('.work-cam-base-input').value) || 50;
    const originalCajas = parseInt(originalCard.querySelector('.work-cam-cajas').value) || 0;
    const originalSoporte = originalCard.querySelector('.work-cam-soporte').checked;

    const tramosData = [];
    originalCard.querySelectorAll('.work-tramo-row').forEach(row => {
        tramosData.push({
            meters: parseFloat(row.querySelector('.work-tramo-meters').value) || 10,
            methodRate: parseFloat(row.querySelector('.work-tramo-metodo').value) || 5.0,
            riskFactor: parseFloat(row.querySelector('.work-tramo-riesgo').value) || 1.0
        });
    });

    addWorkCameraCard({
        name: `${originalName} (Copia)`,
        baseFee: originalBase,
        cajas: originalCajas,
        soporte: originalSoporte,
        tramos: tramosData
    });
}

function removeWorkCamera(camId) {
    const card = document.getElementById(camId);
    if (card) {
        card.remove();
        calculateWorkLaborTotal();
    }
}

function addWorkCustomMacroRow(macroData = null) {
    const container = document.getElementById('workCustomMacrosContainer');
    if (!container) return;

    const macroId = `macro_${Date.now()}_${Math.random().toString(36).substr(2, 4)}`;

    const name = macroData && macroData.name ? macroData.name : 'Perforación de Muro de Hormigón / Trabajo Especial';
    const qty = macroData && macroData.qty !== undefined ? macroData.qty : 1;
    const price = macroData && macroData.price !== undefined ? macroData.price : 40.0;

    const row = document.createElement('div');
    row.id = macroId;
    row.className = "work-macro-row grid grid-cols-12 gap-2 items-center bg-[var(--bg-primary)] p-2.5 rounded-2xl border border-[var(--border-default)] text-xs";

    row.innerHTML = `
        <div class="col-span-6 space-y-0.5">
            <label class="text-[10px] text-[var(--text-secondary)] font-medium">Nombre del Macro / Trabajo Especial:</label>
            <input type="text" value="${name}" placeholder="Descripción del cobro especial..." oninput="calculateWorkLaborTotal()" class="work-macro-name w-full bg-[var(--bg-secondary)] border border-[var(--border-default)] rounded-lg px-2.5 py-1 font-semibold text-[var(--text-primary)]">
        </div>

        <div class="col-span-2 space-y-0.5">
            <label class="text-[10px] text-[var(--text-secondary)] font-medium">Cantidad:</label>
            <input type="number" value="${qty}" min="1" step="1" oninput="calculateWorkLaborTotal()" class="work-macro-qty w-full bg-[var(--bg-secondary)] border border-[var(--border-default)] rounded-lg px-2 py-1 text-center font-bold text-[var(--text-primary)]">
        </div>

        <div class="col-span-3 space-y-0.5">
            <label class="text-[10px] text-[var(--text-secondary)] font-medium">Precio Unit. (Bs):</label>
            <input type="number" value="${price}" min="0" step="5" oninput="calculateWorkLaborTotal()" class="work-macro-price w-full bg-[var(--bg-secondary)] border border-[var(--border-default)] rounded-lg px-2 py-1 text-right font-bold text-[var(--text-primary)]">
        </div>

        <div class="col-span-1 text-center pt-3">
            <button onclick="removeWorkCustomMacroRow('${macroId}')" title="Eliminar Macro" class="p-1 hover:bg-red-500/20 rounded-lg text-red-400 transition">
                <span class="material-symbols-outlined text-sm">close</span>
            </button>
        </div>
    `;

    container.appendChild(row);
    calculateWorkLaborTotal();
}

function removeWorkCustomMacroRow(macroId) {
    const row = document.getElementById(macroId);
    if (row) {
        row.remove();
        calculateWorkLaborTotal();
    }
}

function calculateWorkLaborTotal() {
    const catCctvActive = document.getElementById('workCatCctvCheck') ? document.getElementById('workCatCctvCheck').checked : true;
    const catNetActive = document.getElementById('workCatNetCheck') ? document.getElementById('workCatNetCheck').checked : true;
    const catRackActive = document.getElementById('workCatRackCheck') ? document.getElementById('workCatRackCheck').checked : true;
    const catConfigActive = document.getElementById('workCatConfigCheck') ? document.getElementById('workCatConfigCheck').checked : true;
    const catCustomActive = document.getElementById('workCatCustomCheck') ? document.getElementById('workCatCustomCheck').checked : true;

    // 1. CCTV Subtotal
    let subtotalCctv = 0;
    let totalMetersAll = 0;
    const cameraCards = document.querySelectorAll('.work-camera-card');
    const globalCajaPrice = parseFloat(document.getElementById('workGlobalDefaultCaja').value) || 15;
    const cameraResults = [];

    if (catCctvActive) {
        cameraCards.forEach(card => {
            const name = card.querySelector('.work-cam-name').value.trim() || 'Cámara';
            const baseFee = parseFloat(card.querySelector('.work-cam-base-input').value) || 0;
            const cajasCount = Math.max(0, parseInt(card.querySelector('.work-cam-cajas').value) || 0);
            const tieneSoporte = card.querySelector('.work-cam-soporte').checked;

            const cajasCost = cajasCount * globalCajaPrice;
            const soporteCost = tieneSoporte ? 25.0 : 0.0;

            let camMeters = 0;
            let camTramosCost = 0;
            const tramosInfo = [];

            const tramoRows = card.querySelectorAll('.work-tramo-row');
            tramoRows.forEach(row => {
                const m = Math.max(0, parseFloat(row.querySelector('.work-tramo-meters').value) || 0);
                const precioMetodo = parseFloat(row.querySelector('.work-tramo-metodo').value) || 5.0;
                const factorRiesgo = parseFloat(row.querySelector('.work-tramo-riesgo').value) || 1.0;

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
            subtotalCctv += camTotalSubtotal;
            totalMetersAll += camMeters;

            const subtotalEl = card.querySelector('.work-cam-subtotal-val');
            if (subtotalEl) subtotalEl.textContent = `${camTotalSubtotal.toFixed(2)} Bs`;

            cameraResults.push({ name, baseFee, cajasCount, tieneSoporte, camMeters, camTotalSubtotal, tramosInfo });
        });
    }

    // 2. Redes Subtotal
    let subtotalNet = 0;
    if (catNetActive) {
        const netPoints = Math.max(0, parseInt(document.getElementById('netPointsQty').value) || 0);
        const fiberSplices = Math.max(0, parseInt(document.getElementById('netFiberSplicesQty').value) || 0);
        const certPoints = Math.max(0, parseInt(document.getElementById('netCertPointsQty').value) || 0);

        subtotalNet = (netPoints * 35.0) + (fiberSplices * 25.0) + (certPoints * 15.0);
    }

    if (document.getElementById('workCatNetSubtotal')) {
        document.getElementById('workCatNetSubtotal').textContent = `${subtotalNet.toFixed(2)} Bs`;
    }

    // 3. Racks Subtotal
    let subtotalRack = 0;
    if (catRackActive) {
        const rackTypePrice = parseFloat(document.getElementById('rackTypeSelect').value) || 0;
        const patchPrice = document.getElementById('rackPatchCheck').checked ? 50.0 : 0.0;
        const pduPrice = document.getElementById('rackPduCheck').checked ? 40.0 : 0.0;
        const upsPrice = document.getElementById('rackUpsCheck').checked ? 45.0 : 0.0;

        subtotalRack = rackTypePrice + patchPrice + pduPrice + upsPrice;
    }

    if (document.getElementById('workCatRackSubtotal')) {
        document.getElementById('workCatRackSubtotal').textContent = `${subtotalRack.toFixed(2)} Bs`;
    }

    // 4. Configuración Subtotal
    let subtotalConfig = 0;
    if (catConfigActive) {
        const dvrPrice = document.getElementById('configDvrCheck').checked ? 60.0 : 0.0;
        const routerPrice = document.getElementById('configRouterCheck').checked ? 80.0 : 0.0;
        const apQty = Math.max(0, parseInt(document.getElementById('configApQty').value) || 0);
        const apPrice = apQty * 45.0;

        subtotalConfig = dvrPrice + routerPrice + apPrice;
    }

    if (document.getElementById('workCatConfigSubtotal')) {
        document.getElementById('workCatConfigSubtotal').textContent = `${subtotalConfig.toFixed(2)} Bs`;
    }

    // 5. Custom Macros Subtotal
    let subtotalCustom = 0;
    const customMacrosList = [];
    if (catCustomActive) {
        const customMacroRows = document.querySelectorAll('.work-macro-row');
        customMacroRows.forEach(row => {
            const macroName = row.querySelector('.work-macro-name').value.trim() || 'Trabajo Especial';
            const qty = Math.max(1, parseInt(row.querySelector('.work-macro-qty').value) || 1);
            const price = Math.max(0, parseFloat(row.querySelector('.work-macro-price').value) || 0);
            const rowTotal = qty * price;

            subtotalCustom += rowTotal;
            customMacrosList.push({ name: macroName, qty, price, total: rowTotal });
        });
    }

    // Global Totals
    const subtotalInfraNet = subtotalNet + subtotalRack + subtotalConfig + subtotalCustom;
    const transporte = Math.max(0, parseFloat(document.getElementById('workGlobalTransporte').value) || 0);
    const factorGarantia = parseFloat(document.getElementById('workGlobalGarantia').value) || 1.0;

    const totalConTransporte = subtotalCctv + subtotalInfraNet + transporte;
    const totalFinalGeneral = totalConTransporte * factorGarantia;

    // Update Global Summary UI
    if (document.getElementById('workSummaryStats')) {
        document.getElementById('workSummaryStats').textContent = `${cameraCards.length} Cámaras | ${totalMetersAll}m Cableado`;
    }
    if (document.getElementById('workDispSubtotalCctv')) {
        document.getElementById('workDispSubtotalCctv').textContent = `${subtotalCctv.toFixed(2)} Bs`;
    }
    if (document.getElementById('workDispSubtotalInfra')) {
        document.getElementById('workDispSubtotalInfra').textContent = `${subtotalInfraNet.toFixed(2)} Bs`;
    }
    if (document.getElementById('workDispGarantia')) {
        document.getElementById('workDispGarantia').textContent = `${transporte} Bs (${factorGarantia}x)`;
    }
    if (document.getElementById('workTotalCalculado')) {
        document.getElementById('workTotalCalculado').textContent = `${totalFinalGeneral.toFixed(2)} ${typeof currentCurrency !== 'undefined' ? currentCurrency : 'Bs'}`;
    }

    return {
        catCctvActive,
        catNetActive,
        catRackActive,
        catConfigActive,
        catCustomActive,
        numCamaras: cameraCards.length,
        totalMetersAll,
        subtotalCctv,
        subtotalNet,
        subtotalRack,
        subtotalConfig,
        subtotalCustom,
        subtotalInfraNet,
        transporte,
        factorGarantia,
        totalFinalGeneral,
        cameraResults,
        customMacrosList
    };
}

function collectWorkCalculatorData() {
    const calc = calculateWorkLaborTotal();

    const camerasData = [];
    document.querySelectorAll('.work-camera-card').forEach(card => {
        const name = card.querySelector('.work-cam-name').value;
        const baseFee = parseFloat(card.querySelector('.work-cam-base-input').value) || 50;
        const cajas = parseInt(card.querySelector('.work-cam-cajas').value) || 0;
        const soporte = card.querySelector('.work-cam-soporte').checked;

        const tramos = [];
        card.querySelectorAll('.work-tramo-row').forEach(row => {
            tramos.push({
                meters: parseFloat(row.querySelector('.work-tramo-meters').value) || 10,
                methodRate: parseFloat(row.querySelector('.work-tramo-metodo').value) || 5.0,
                riskFactor: parseFloat(row.querySelector('.work-tramo-riesgo').value) || 1.0
            });
        });

        camerasData.push({ name, baseFee, cajas, soporte, tramos });
    });

    const macrosData = [];
    document.querySelectorAll('.work-macro-row').forEach(row => {
        macrosData.push({
            name: row.querySelector('.work-macro-name').value,
            qty: parseInt(row.querySelector('.work-macro-qty').value) || 1,
            price: parseFloat(row.querySelector('.work-macro-price').value) || 0
        });
    });

    return {
        preset: document.getElementById('workPresetSelect') ? document.getElementById('workPresetSelect').value : 'calidad_precio',
        globalBase: parseFloat(document.getElementById('workGlobalDefaultBase').value) || 50,
        globalCaja: parseFloat(document.getElementById('workGlobalDefaultCaja').value) || 15,
        transporte: parseFloat(document.getElementById('workGlobalTransporte').value) || 30,
        garantia: parseFloat(document.getElementById('workGlobalGarantia').value) || 1.15,
        
        catCctvActive: calc.catCctvActive,
        catNetActive: calc.catNetActive,
        catRackActive: calc.catRackActive,
        catConfigActive: calc.catConfigActive,
        catCustomActive: calc.catCustomActive,

        netPointsQty: parseInt(document.getElementById('netPointsQty').value) || 0,
        netFiberSplicesQty: parseInt(document.getElementById('netFiberSplicesQty').value) || 0,
        netCertPointsQty: parseInt(document.getElementById('netCertPointsQty').value) || 0,

        rackType: parseFloat(document.getElementById('rackTypeSelect').value) || 0,
        rackPatch: document.getElementById('rackPatchCheck').checked,
        rackPdu: document.getElementById('rackPduCheck').checked,
        rackUps: document.getElementById('rackUpsCheck').checked,

        configDvr: document.getElementById('configDvrCheck').checked,
        configRouter: document.getElementById('configRouterCheck').checked,
        configApQty: parseInt(document.getElementById('configApQty').value) || 0,

        cameras: camerasData,
        customMacros: macrosData,
        totalFinalGeneral: calc.totalFinalGeneral
    };
}

function restoreWorkCalculatorData(data) {
    if (!data) return;

    if (data.preset && document.getElementById('workPresetSelect')) document.getElementById('workPresetSelect').value = data.preset;
    if (data.globalBase !== undefined && document.getElementById('workGlobalDefaultBase')) document.getElementById('workGlobalDefaultBase').value = data.globalBase;
    if (data.globalCaja !== undefined && document.getElementById('workGlobalDefaultCaja')) document.getElementById('workGlobalDefaultCaja').value = data.globalCaja;
    if (data.transporte !== undefined && document.getElementById('workGlobalTransporte')) document.getElementById('workGlobalTransporte').value = data.transporte;
    if (data.garantia !== undefined && document.getElementById('workGlobalGarantia')) document.getElementById('workGlobalGarantia').value = data.garantia;

    if (data.catCctvActive !== undefined && document.getElementById('workCatCctvCheck')) document.getElementById('workCatCctvCheck').checked = !!data.catCctvActive;
    if (data.catNetActive !== undefined && document.getElementById('workCatNetCheck')) document.getElementById('workCatNetCheck').checked = !!data.catNetActive;
    if (data.catRackActive !== undefined && document.getElementById('workCatRackCheck')) document.getElementById('workCatRackCheck').checked = !!data.catRackActive;
    if (data.catConfigActive !== undefined && document.getElementById('workCatConfigCheck')) document.getElementById('workCatConfigCheck').checked = !!data.catConfigActive;
    if (data.catCustomActive !== undefined && document.getElementById('workCatCustomCheck')) document.getElementById('workCatCustomCheck').checked = !!data.catCustomActive;

    if (data.netPointsQty !== undefined && document.getElementById('netPointsQty')) document.getElementById('netPointsQty').value = data.netPointsQty;
    if (data.netFiberSplicesQty !== undefined && document.getElementById('netFiberSplicesQty')) document.getElementById('netFiberSplicesQty').value = data.netFiberSplicesQty;
    if (data.netCertPointsQty !== undefined && document.getElementById('netCertPointsQty')) document.getElementById('netCertPointsQty').value = data.netCertPointsQty;

    if (data.rackType !== undefined && document.getElementById('rackTypeSelect')) document.getElementById('rackTypeSelect').value = data.rackType;
    if (data.rackPatch !== undefined && document.getElementById('rackPatchCheck')) document.getElementById('rackPatchCheck').checked = !!data.rackPatch;
    if (data.rackPdu !== undefined && document.getElementById('rackPduCheck')) document.getElementById('rackPduCheck').checked = !!data.rackPdu;
    if (data.rackUps !== undefined && document.getElementById('rackUpsCheck')) document.getElementById('rackUpsCheck').checked = !!data.rackUps;

    if (data.configDvr !== undefined && document.getElementById('configDvrCheck')) document.getElementById('configDvrCheck').checked = !!data.configDvr;
    if (data.configRouter !== undefined && document.getElementById('configRouterCheck')) document.getElementById('configRouterCheck').checked = !!data.configRouter;
    if (data.configApQty !== undefined && document.getElementById('configApQty')) document.getElementById('configApQty').value = data.configApQty;

    // Restore Cameras
    const camContainer = document.getElementById('workCamerasContainer');
    if (camContainer) camContainer.innerHTML = '';
    workCameraCounter = 0;

    if (data.cameras && data.cameras.length > 0) {
        data.cameras.forEach(cam => addWorkCameraCard(cam));
    }

    // Restore Custom Macros
    const macroContainer = document.getElementById('workCustomMacrosContainer');
    if (macroContainer) macroContainer.innerHTML = '';

    if (data.customMacros && data.customMacros.length > 0) {
        data.customMacros.forEach(m => addWorkCustomMacroRow(m));
    }

    toggleCategorySection('cctv');
    toggleCategorySection('net');
    toggleCategorySection('rack');
    toggleCategorySection('config');
    toggleCategorySection('custom');

    calculateWorkLaborTotal();
}

function addWorkLaborToQuotation(mode = 'single') {
    const calc = calculateWorkLaborTotal();
    if (calc.totalFinalGeneral === 0) {
        alert("Por favor active al menos una categoría de trabajo con monto superior a cero.");
        return;
    }

    let garantiaPct = "0%";
    if (calc.factorGarantia === 1.15) garantiaPct = "15%";
    else if (calc.factorGarantia === 1.25) garantiaPct = "25%";

    if (mode === 'single') {
        const activeCats = [];
        if (calc.catCctvActive && calc.subtotalCctv > 0) activeCats.push(`${calc.numCamaras} Cámaras (${calc.totalMetersAll}m)`);
        if (calc.catNetActive && calc.subtotalNet > 0) activeCats.push("Redes/Fibra");
        if (calc.catRackActive && calc.subtotalRack > 0) activeCats.push("Montaje Racks");
        if (calc.catConfigActive && calc.subtotalConfig > 0) activeCats.push("Configuración");
        if (calc.catCustomActive && calc.subtotalCustom > 0) activeCats.push(`${calc.customMacrosList.length} Macro(s)`);

        const catText = activeCats.length > 0 ? `: ${activeCats.join(' + ')}` : '';
        const description = `Servicio Especializado de Instalación y Mano de Obra${catText} | Incluye pasajes (${calc.transporte} Bs) y Garantía (${garantiaPct})`;

        addProductRow(description, 1, 'servicio (srv)', parseFloat(calc.totalFinalGeneral.toFixed(2)));
    } else if (mode === 'per_category') {
        // Inject per-category items
        if (calc.catCctvActive && calc.subtotalCctv > 0) {
            const priceCctv = calc.subtotalCctv * calc.factorGarantia;
            addProductRow(`Mano de Obra CCTV: Instalación de ${calc.numCamaras} Cámaras y ${calc.totalMetersAll}m de cableado por tramos`, 1, 'servicio (srv)', parseFloat(priceCctv.toFixed(2)));
        }

        if (calc.catNetActive && calc.subtotalNet > 0) {
            const priceNet = calc.subtotalNet * calc.factorGarantia;
            addProductRow(`Mano de Obra Redes & Fibra Óptica: Puntos UTP / Fusiones / Certificación`, 1, 'servicio (srv)', parseFloat(priceNet.toFixed(2)));
        }

        if (calc.catRackActive && calc.subtotalRack > 0) {
            const priceRack = calc.subtotalRack * calc.factorGarantia;
            addProductRow(`Mano de Obra Racks & Energía: Montaje de Rack telecom, patch panel y organizadores`, 1, 'servicio (srv)', parseFloat(priceRack.toFixed(2)));
        }

        if (calc.catConfigActive && calc.subtotalConfig > 0) {
            const priceConfig = calc.subtotalConfig * calc.factorGarantia;
            addProductRow(`Servicio de Configuración & Programación: Grabador DVR/NVR, red, router y Wi-Fi`, 1, 'servicio (srv)', parseFloat(priceConfig.toFixed(2)));
        }

        if (calc.catCustomActive && calc.subtotalCustom > 0) {
            const priceCustom = (calc.subtotalCustom + calc.transporte) * calc.factorGarantia;
            addProductRow(`Obras Civiles & Servicios Especiales a Medida: ${calc.customMacrosList.map(m => m.name).join(', ')}`, 1, 'servicio (srv)', parseFloat(priceCustom.toFixed(2)));
        }
    }

    hideWorkCalculatorView();
}
