/**
 * Advanced PDF Editor & Merger Logic using PDF.js
 */

let uploadedDocs = {}; // docId -> { name: string, base64: string }
let editorPages = [];  // Array of { id: string, docId: string, docName: string, pageNum: number, rotation: number, thumbnail: string }

let draggedPageId = null;

function handlePdfDragOver(e) {
    e.preventDefault();
    e.stopPropagation();
    const dropZone = document.getElementById('pdfDropZone');
    if (dropZone) dropZone.classList.add('border-[var(--text-primary)]', 'bg-[var(--bg-secondary)]');
}

function handlePdfDragLeave(e) {
    e.preventDefault();
    e.stopPropagation();
    const dropZone = document.getElementById('pdfDropZone');
    if (dropZone) dropZone.classList.remove('border-[var(--text-primary)]', 'bg-[var(--bg-secondary)]');
}

function handlePdfDrop(e) {
    e.preventDefault();
    e.stopPropagation();
    const dropZone = document.getElementById('pdfDropZone');
    if (dropZone) dropZone.classList.remove('border-[var(--text-primary)]', 'bg-[var(--bg-secondary)]');

    if (e.dataTransfer && e.dataTransfer.files) {
        processPdfFiles(e.dataTransfer.files);
    }
}

function handlePdfFileSelect(e) {
    if (e.target.files) {
        processPdfFiles(e.target.files);
    }
    e.target.value = '';
}

async function processPdfFiles(files) {
    const loadingState = document.getElementById('pdfLoadingState');
    const loadingProgress = document.getElementById('pdfLoadingProgress');
    const grid = document.getElementById('pdfPagesGrid');
    const emptyState = document.getElementById('pdfFilesEmptyState');

    if (loadingState) loadingState.classList.remove('hidden');
    if (grid) grid.classList.add('hidden');
    if (emptyState) emptyState.classList.add('hidden');

    for (let i = 0; i < files.length; i++) {
        const file = files[i];
        if (file.type !== 'application/pdf' && !file.name.toLowerCase().endsWith('.pdf')) {
            alert(`El archivo ${file.name} no es un PDF válido.`);
            continue;
        }

        if (loadingProgress) loadingProgress.textContent = `Leyendo ${file.name}...`;

        try {
            const base64 = await readFileAsBase64(file);
            const docId = 'doc_' + Date.now() + '_' + Math.floor(Math.random() * 1000);
            
            uploadedDocs[docId] = {
                name: file.name,
                base64: base64
            };

            // Parse with PDF.js
            const pdfData = atob(base64);
            const loadingTask = pdfjsLib.getDocument({ data: pdfData });
            const pdf = await loadingTask.promise;

            const numPages = pdf.numPages;
            for (let pageNum = 1; pageNum <= numPages; pageNum++) {
                if (loadingProgress) loadingProgress.textContent = `Generando miniatura ${pageNum}/${numPages} de ${file.name}...`;
                
                const page = await pdf.getPage(pageNum);
                const viewport = page.getViewport({ scale: 0.5 }); // Lower scale for thumbnail

                const canvas = document.createElement('canvas');
                const context = canvas.getContext('2d');
                canvas.height = viewport.height;
                canvas.width = viewport.width;

                const renderContext = {
                    canvasContext: context,
                    viewport: viewport
                };

                await page.render(renderContext).promise;
                const thumbnailDataUrl = canvas.toDataURL('image/jpeg', 0.8);

                editorPages.push({
                    id: 'page_' + Date.now() + '_' + Math.floor(Math.random() * 10000),
                    docId: docId,
                    docName: file.name,
                    pageNum: pageNum, // 1-based for display, we'll convert to 0-based for backend
                    rotation: 0,
                    thumbnail: thumbnailDataUrl
                });
            }
        } catch (error) {
            console.error("Error reading PDF:", error);
            alert(`Error al leer el archivo ${file.name}: ${error.message}`);
        }
    }

    if (loadingState) loadingState.classList.add('hidden');
    if (grid) grid.classList.remove('hidden');
    renderPdfPagesGrid();
}

function readFileAsBase64(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => {
            const result = reader.result;
            const base64String = result.split(',')[1];
            resolve(base64String);
        };
        reader.onerror = error => reject(error);
        reader.readAsDataURL(file);
    });
}

function renderPdfPagesGrid() {
    const gridContainer = document.getElementById('pdfPagesGrid');
    const emptyState = document.getElementById('pdfFilesEmptyState');
    const countEl = document.getElementById('pdfCount');
    const mergeBtn = document.getElementById('mergePdfBtn');

    if (!gridContainer || !emptyState) return;

    if (countEl) countEl.textContent = editorPages.length;

    gridContainer.innerHTML = '';

    if (editorPages.length === 0) {
        emptyState.classList.remove('hidden');
        if (mergeBtn) {
            mergeBtn.disabled = true;
            mergeBtn.classList.add('opacity-50', 'cursor-not-allowed');
        }
        return;
    }

    emptyState.classList.add('hidden');
    if (mergeBtn) {
        if (editorPages.length >= 1) { // Allow "merging" even 1 page (useful for extracting/rotating)
            mergeBtn.disabled = false;
            mergeBtn.classList.remove('opacity-50', 'cursor-not-allowed');
        } else {
            mergeBtn.disabled = true;
            mergeBtn.classList.add('opacity-50', 'cursor-not-allowed');
        }
    }

    editorPages.forEach((page, index) => {
        const card = document.createElement('div');
        card.className = 'bg-[var(--bg-primary)] border border-[var(--border-default)] rounded-xl overflow-hidden flex flex-col relative group cursor-grab active:cursor-grabbing hover:border-[var(--border-focus)] transition-all';
        card.draggable = true;
        
        // Drag events
        card.ondragstart = (e) => {
            draggedPageId = page.id;
            e.dataTransfer.effectAllowed = 'move';
            card.classList.add('opacity-50');
        };
        card.ondragend = () => {
            draggedPageId = null;
            card.classList.remove('opacity-50');
            // Remove any drag over styling
            document.querySelectorAll('.border-blue-500').forEach(el => el.classList.remove('border-blue-500'));
        };
        card.ondragover = (e) => {
            e.preventDefault();
            e.dataTransfer.dropEffect = 'move';
            card.classList.add('border-blue-500'); // Highlight target
        };
        card.ondragleave = () => {
            card.classList.remove('border-blue-500');
        };
        card.ondrop = (e) => {
            e.preventDefault();
            card.classList.remove('border-blue-500');
            if (draggedPageId && draggedPageId !== page.id) {
                reorderPage(draggedPageId, page.id);
            }
        };

        // Thumbnail
        const imgContainer = document.createElement('div');
        imgContainer.className = 'w-full h-40 bg-black/10 flex items-center justify-center p-2 overflow-hidden';
        const img = document.createElement('img');
        img.src = page.thumbnail;
        img.className = 'max-w-full max-h-full object-contain shadow-sm transition-transform duration-300';
        img.style.transform = `rotate(${page.rotation}deg)`;
        imgContainer.appendChild(img);

        // Badge number
        const badge = document.createElement('div');
        badge.className = 'absolute top-2 left-2 bg-black/60 text-white text-[10px] font-bold px-1.5 py-0.5 rounded-md backdrop-blur-sm';
        badge.textContent = index + 1;

        // Overlay Toolbar (visible on hover)
        const toolbar = document.createElement('div');
        toolbar.className = 'absolute top-2 right-2 flex space-x-1 opacity-0 group-hover:opacity-100 transition-opacity bg-black/60 rounded-lg p-1 backdrop-blur-sm';
        toolbar.innerHTML = `
            <button onclick="rotatePageLeft('${page.id}', event)" class="p-1 hover:bg-white/20 rounded text-white transition" title="Rotar Izquierda">
                <span class="material-symbols-outlined text-[16px]">rotate_left</span>
            </button>
            <button onclick="rotatePageRight('${page.id}', event)" class="p-1 hover:bg-white/20 rounded text-white transition" title="Rotar Derecha">
                <span class="material-symbols-outlined text-[16px]">rotate_right</span>
            </button>
            <button onclick="removePage('${page.id}', event)" class="p-1 hover:bg-red-500/80 rounded text-red-200 transition" title="Eliminar Página">
                <span class="material-symbols-outlined text-[16px]">delete</span>
            </button>
        `;

        // Footer info
        const footer = document.createElement('div');
        footer.className = 'p-2 text-center border-t border-[var(--border-default)] bg-[var(--bg-secondary)]';
        footer.innerHTML = `
            <p class="text-[10px] text-[var(--text-secondary)] font-bold truncate" title="${page.docName}">${page.docName}</p>
            <p class="text-[9px] text-[var(--text-secondary)] opacity-70">Pág ${page.pageNum}</p>
        `;

        card.appendChild(imgContainer);
        card.appendChild(badge);
        card.appendChild(toolbar);
        card.appendChild(footer);

        gridContainer.appendChild(card);
    });
}

function rotatePageLeft(id, e) {
    if (e) { e.preventDefault(); e.stopPropagation(); }
    const page = editorPages.find(p => p.id === id);
    if (page) {
        page.rotation = (page.rotation - 90) % 360;
        renderPdfPagesGrid();
    }
}

function rotatePageRight(id, e) {
    if (e) { e.preventDefault(); e.stopPropagation(); }
    const page = editorPages.find(p => p.id === id);
    if (page) {
        page.rotation = (page.rotation + 90) % 360;
        renderPdfPagesGrid();
    }
}

function removePage(id, e) {
    if (e) { e.preventDefault(); e.stopPropagation(); }
    editorPages = editorPages.filter(p => p.id !== id);
    renderPdfPagesGrid();
}

function reorderPage(draggedId, targetId) {
    const draggedIndex = editorPages.findIndex(p => p.id === draggedId);
    const targetIndex = editorPages.findIndex(p => p.id === targetId);
    
    if (draggedIndex === -1 || targetIndex === -1) return;

    const [draggedItem] = editorPages.splice(draggedIndex, 1);
    editorPages.splice(targetIndex, 0, draggedItem);
    
    renderPdfPagesGrid();
}

async function mergePDFs() {
    if (editorPages.length === 0) {
        alert("No hay páginas para combinar.");
        return;
    }

    const mergeBtn = document.getElementById('mergePdfBtn');
    if (mergeBtn) {
        mergeBtn.disabled = true;
        mergeBtn.innerHTML = '<span class="material-symbols-outlined text-lg animate-spin">sync</span><span>PROCESANDO...</span>';
    }

    // Prepare payload
    // Filter docs to only include those that are actually referenced in editorPages
    const usedDocIds = new Set(editorPages.map(p => p.docId));
    const filteredDocs = {};
    for (const docId of usedDocIds) {
        filteredDocs[docId] = uploadedDocs[docId].base64;
    }

    const pagesPayload = editorPages.map(p => ({
        doc_id: p.docId,
        page_index: p.pageNum - 1, // PyMuPDF uses 0-based page indices
        rotation: p.rotation
    }));

    try {
        const res = await fetch((window.ENV?.API_BASE_URL || '') + '/api/pdf/merge', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ docs: filteredDocs, pages: pagesPayload })
        });

        if (!res.ok) {
            const err = await res.json();
            alert("Error al combinar PDFs: " + (err.detail || "Error desconocido"));
        } else {
            const blob = await res.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `Documento_Editado_${new Date().getTime()}.pdf`;
            document.body.appendChild(a);
            a.click();
            a.remove();
        }
    } catch (e) {
        alert("Error de conexión: " + e.message);
    } finally {
        if (mergeBtn) {
            mergeBtn.disabled = false;
            mergeBtn.innerHTML = '<span class="material-symbols-outlined text-lg">merge</span><span>COMBINAR PDFs</span>';
        }
    }
}
