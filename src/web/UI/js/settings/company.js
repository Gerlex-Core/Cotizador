/**
 * Package: settings/company.js
 * Company manager logic (.emp files, company selection, logos, digital signatures, and dropzones).
 */

async function loadCompanies() {
    try {
        const res = await fetch((window.ENV?.API_BASE_URL || '') + '/api/companies/details');
        registeredCompanies = await res.json();
        
        const select = document.getElementById('companySelect');
        const grid = document.getElementById('companiesGrid');
        
        if (select) {
            select.innerHTML = '<option value="">Seleccionar Empresa</option>';
            registeredCompanies.forEach(c => {
                const opt = document.createElement('option');
                opt.value = c.nombre;
                opt.textContent = c.nombre + (c.es_predeterminada ? ' (Predeterminada)' : '');
                select.appendChild(opt);
            });
            if (registeredCompanies.length > 0) {
                select.value = registeredCompanies[0].nombre;
                onCompanySelectChanged();
            }
        }

        if (grid) {
            if (registeredCompanies.length === 0) {
                grid.innerHTML = '<div class="col-span-12 text-center text-slate-500 italic py-6">No hay empresas registradas. Haz clic en "Nueva Empresa" para agregar una.</div>';
                return;
            }
            grid.innerHTML = '';
            registeredCompanies.forEach(c => {
                const card = document.createElement('div');
                card.className = "col-span-6 bg-[var(--bg-primary)] border border-[var(--border-default)] rounded-2xl p-4 space-y-2 shadow-sm flex flex-col justify-between";
                card.innerHTML = `
                    <div>
                        <div class="flex items-center justify-between">
                            <h4 class="font-extrabold text-sm text-[var(--text-primary)]">${c.nombre}</h4>
                            ${c.es_predeterminada ? '<span class="px-2 py-0.5 bg-emerald-500/20 text-emerald-400 rounded-full text-[10px] font-bold">Predeterminada</span>' : ''}
                        </div>
                        <p class="text-xs text-[var(--text-secondary)] mt-1">NIT: ${c.nit || 'Sin NIT'} | Tel: ${c.telefono || 'Sin Teléfono'}</p>
                        <p class="text-xs text-[var(--text-secondary)]">Correo: ${c.correo || 'N/A'}</p>
                        <p class="text-xs text-[var(--text-secondary)]">Dirección: ${c.direccion || 'N/A'}</p>
                    </div>
                    <div class="flex items-center justify-end space-x-2 pt-3 border-t border-[var(--border-default)] mt-2">
                        ${!c.es_predeterminada ? `<button onclick="setDefaultCompany('${c.nombre}')" class="px-3 py-1 bg-[var(--bg-secondary)] hover:bg-white/10 text-[var(--text-primary)] rounded-full text-xs font-semibold">Predeterminada</button>` : ''}
                        <button onclick="downloadCompanyEmpFile('${c.nombre}')" title="Descargar .emp" class="px-3 py-1 bg-[var(--bg-secondary)] hover:bg-white/10 text-[var(--text-primary)] rounded-full text-xs font-semibold">.emp</button>
                        <button onclick="editCompany('${c.nombre}')" class="px-3 py-1 bg-[var(--bg-secondary)] hover:bg-white/10 text-[var(--text-primary)] rounded-full text-xs font-semibold">Editar</button>
                        <button onclick="deleteCompany('${c.nombre}')" class="px-3 py-1 bg-red-500/20 hover:bg-red-500/30 text-red-400 rounded-full text-xs font-semibold">Eliminar</button>
                    </div>
                `;
                grid.appendChild(card);
            });
        }
    } catch (e) {
        console.error("Error loading companies:", e);
    }
}

async function onCompanySelectChanged() {
    const select = document.getElementById('companySelect');
    if (!select) return;
    const name = select.value;
    const infoLabel = document.getElementById('companyInfoLabel');
    if (!name) {
        if (infoLabel) infoLabel.textContent = "";
        return;
    }
    const c = registeredCompanies.find(comp => comp.nombre === name);
    if (c && infoLabel) {
        const parts = [];
        if (c.nit) parts.push(`NIT: ${c.nit}`);
        if (c.telefono) parts.push(`📞 ${c.telefono}`);
        if (c.correo) parts.push(`✉️ ${c.correo}`);
        infoLabel.textContent = parts.join(' | ');
    }
}

function openCompanyModal(companyData = null) {
    const modal = document.getElementById('companyModal');
    if (!modal) return;
    modal.classList.remove('hidden');

    if (companyData) {
        document.getElementById('companyModalTitle').textContent = "Editar Empresa: " + companyData.nombre;
        document.getElementById('modalCompName').value = companyData.nombre;
        document.getElementById('modalCompNit').value = companyData.nit || '';
        document.getElementById('modalCompPhone').value = companyData.telefono || '';
        document.getElementById('modalCompEmail').value = companyData.correo || '';
        document.getElementById('modalCompCity').value = companyData.ciudad || '';
        document.getElementById('modalCompAddress').value = companyData.direccion || '';
        document.getElementById('modalCompIsDefault').checked = companyData.es_predeterminada || false;
    } else {
        document.getElementById('companyModalTitle').textContent = "Agregar Nueva Empresa Emisora";
        document.getElementById('companyForm').reset();
    }
}

function closeCompanyModal() {
    const modal = document.getElementById('companyModal');
    if (modal) modal.classList.add('hidden');
}

async function handleSaveCompany(e) {
    e.preventDefault();
    const company = {
        nombre: document.getElementById('modalCompName').value.trim(),
        nit: document.getElementById('modalCompNit').value.trim(),
        telefono: document.getElementById('modalCompPhone').value.trim(),
        correo: document.getElementById('modalCompEmail').value.trim(),
        ciudad: document.getElementById('modalCompCity').value.trim(),
        direccion: document.getElementById('modalCompAddress').value.trim(),
        es_predeterminada: document.getElementById('modalCompIsDefault').checked
    };

    try {
        const res = await fetch((window.ENV?.API_BASE_URL || '') + '/api/companies', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(company)
        });
        if (res.ok) {
            closeCompanyModal();
            loadCompanies();
        } else {
            alert("Error al guardar empresa.");
        }
    } catch (err) {
        alert("Error de conexión: " + err.message);
    }
}

async function setDefaultCompany(name) {
    try {
        const res = await fetch(`${window.ENV?.API_BASE_URL || ''}/api/companies/${encodeURIComponent(name)}/set-default`, { method: 'POST' });
        if (res.ok) loadCompanies();
    } catch (e) {
        console.error(e);
    }
}

function editCompany(name) {
    const c = registeredCompanies.find(comp => comp.nombre === name);
    if (c) openCompanyModal(c);
}

async function deleteCompany(name) {
    if (confirm(`¿Desea eliminar la empresa '${name}'?`)) {
        try {
            const res = await fetch(`${window.ENV?.API_BASE_URL || ''}/api/companies/${encodeURIComponent(name)}`, { method: 'DELETE' });
            if (res.ok) loadCompanies();
        } catch (e) {
            console.error(e);
        }
    }
}

async function handleUploadCompanyFile(input) {
    if (!input.files || !input.files[0]) return;
    const formData = new FormData();
    formData.append("file", input.files[0]);

    try {
        const res = await fetch((window.ENV?.API_BASE_URL || '') + '/api/companies/upload', {
            method: 'POST',
            body: formData
        });
        if (res.ok) {
            const data = await res.json();
            alert(data.message);
            loadCompanies();
        } else {
            alert("No se pudo importar el archivo de empresa.");
        }
    } catch (e) {
        alert("Error al importar empresa: " + e.message);
    }
}

function downloadCompanyEmpFile(name) {
    window.open(`/api/companies/${encodeURIComponent(name)}/download`, '_blank');
}

function handleDropCompanyFile(e) {
    e.preventDefault();
    e.stopPropagation();
    const dropzone = document.getElementById('companyEmpDropzone');
    if (dropzone) handleDragLeave(e, dropzone);

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
        const file = e.dataTransfer.files[0];
        const input = document.getElementById('uploadCompanyFileInput');
        if (input) {
            const dataTransfer = new DataTransfer();
            dataTransfer.items.add(file);
            input.files = dataTransfer.files;
            handleUploadCompanyFile(input);
        }
    }
}

function handleDropLogo(e) {
    e.preventDefault();
    e.stopPropagation();
    const dropzone = document.getElementById('logoDropzone');
    if (dropzone) handleDragLeave(e, dropzone);

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
        const file = e.dataTransfer.files[0];
        const input = document.getElementById('modalCompLogoFile');
        if (input) {
            const dataTransfer = new DataTransfer();
            dataTransfer.items.add(file);
            input.files = dataTransfer.files;
            previewImage(input, 'modalCompLogoPreview');
        }
    }
}

function handleDropSignature(e) {
    e.preventDefault();
    e.stopPropagation();
    const dropzone = document.getElementById('signatureDropzone');
    if (dropzone) handleDragLeave(e, dropzone);

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
        const file = e.dataTransfer.files[0];
        const input = document.getElementById('modalCompSignatureFile');
        if (input) {
            const dataTransfer = new DataTransfer();
            dataTransfer.items.add(file);
            input.files = dataTransfer.files;
            previewImage(input, 'modalCompSigPreview');
        }
    }
}

function previewImage(input, previewId) {
    const container = document.getElementById(previewId);
    if (!container) return;
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function(e) {
            container.innerHTML = `<img src="${e.target.result}" class="max-h-14 rounded-lg object-contain">`;
        };
        reader.readAsDataURL(input.files[0]);
    }
}
