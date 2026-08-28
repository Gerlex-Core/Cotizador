/**
 * Package: historial/history.js
 * SQLite DB quotations history, file upload (.cotz), and history dropzone handlers.
 */

async function loadHistory() {
    try {
        const res = await fetch((window.ENV?.API_BASE_URL || '') + '/api/history/recent');
        const files = await res.json();
    } catch (e) {
        console.error("Error loading history:", e);
    }
}

async function loadDbQuotations() {
    try {
        const res = await fetch((window.ENV?.API_BASE_URL || '') + '/api/quotations/db/list');
        if (res.ok) {
            const list = await res.json();
            const tbody = document.getElementById('dbQuotationsTbody');
            if (!tbody) return;
            if (list.length === 0) {
                tbody.innerHTML = '<tr><td colspan="8" class="p-4 text-center text-slate-500 italic">No hay cotizaciones guardadas en la base de datos SQLite.</td></tr>';
                return;
            }
            tbody.innerHTML = '';
            list.forEach(q => {
                const tr = document.createElement('tr');
                tr.className = "hover:bg-white/[0.02] transition";
                tr.innerHTML = `
                    <td class="p-3 font-mono font-bold text-[var(--text-primary)]">${q.quotation_number}</td>
                    <td class="p-3 text-[var(--text-secondary)]">${q.document_type}</td>
                    <td class="p-3 text-[var(--text-secondary)]">${q.date}</td>
                    <td class="p-3 font-semibold text-[var(--text-primary)]">${q.client_name || 'N/A'}</td>
                    <td class="p-3 text-[var(--text-secondary)]">${q.company_name || 'N/A'}</td>
                    <td class="p-3 text-right font-extrabold text-[var(--text-primary)]">${q.total.toFixed(2)}</td>
                    <td class="p-3 text-right font-bold ${q.saldo_amount > 0 ? 'text-red-400' : 'text-emerald-400'}">${q.saldo_amount.toFixed(2)}</td>
                    <td class="p-3 text-center">
                        <button onclick="loadQuotationFromDb('${q.quotation_number}')" class="px-3 py-1 bg-[var(--text-primary)] text-[var(--bg-primary)] rounded-full font-bold text-xs shadow hover:opacity-90 transition">Cargar</button>
                    </td>
                `;
                tbody.appendChild(tr);
            });
        }
    } catch (e) {
        console.error("Error loading DB quotations:", e);
    }
}

async function loadQuotationFromDb(qNum) {
    try {
        const res = await fetch(`${window.ENV?.API_BASE_URL || ''}/api/quotations/db/load/${encodeURIComponent(qNum)}`);
        if (res.ok) {
            const data = await res.json();
            populateFormFromData(data);
            alert(`Cotización ${qNum} cargada correctamente.`);
        }
    } catch (e) {
        alert("Error cargando cotización: " + e.message);
    }
}

async function handleUploadCotzFile(input) {
    if (!input.files || !input.files[0]) return;
    const formData = new FormData();
    formData.append("file", input.files[0]);

    try {
        const res = await fetch((window.ENV?.API_BASE_URL || '') + '/api/quotations/upload', {
            method: 'POST',
            body: formData
        });
        if (res.ok) {
            const data = await res.json();
            populateFormFromData(data);
            alert("Cotización cargada desde archivo correctamente.");
        } else {
            alert("No se pudo leer el archivo .cotz subido.");
        }
    } catch (e) {
        alert("Error al subir archivo: " + e.message);
    }
}

function handleDropCotzFile(e) {
    e.preventDefault();
    e.stopPropagation();
    const dropzone = document.getElementById('cotzDropzone');
    if (dropzone) handleDragLeave(e, dropzone);

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
        const file = e.dataTransfer.files[0];
        const input = document.getElementById('uploadCotzFileInput');
        if (input) {
            const dataTransfer = new DataTransfer();
            dataTransfer.items.add(file);
            input.files = dataTransfer.files;
            handleUploadCotzFile(input);
        }
    }
}
