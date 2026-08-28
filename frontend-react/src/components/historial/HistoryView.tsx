import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useQuotation } from '../../context/QuotationContext';
import { useNavigation } from '../../context/NavigationContext';
import { API_BASE_URL } from '../../config/apiConfig';

type QuotationRecord = {
    quotation_number: string;
    document_type: string;
    date: string;
    client_name: string;
    company_name: string;
    total: number;
    saldo_amount: number;
};

export default function HistoryView() {
    const [quotations, setQuotations] = useState<QuotationRecord[]>([]);
    const [loading, setLoading] = useState(false);
    const [dragActive, setDragActive] = useState(false);
    
    const { setClient, setProducts } = useQuotation();
    const { setActiveTab } = useNavigation();

    const loadQuotations = async () => {
        setLoading(true);
        try {
            // Placeholder URL, will be configured via environment
            const res = await fetch(`${API_BASE_URL}/api/quotations/db/list`);
            if (res.ok) {
                const data = await res.json();
                setQuotations(data);
            }
        } catch (error) {
            console.error("Error loading history:", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadQuotations();
    }, []);

    const handleLoadQuotation = async (q: QuotationRecord) => {
        try {
            setLoading(true);
            const res = await fetch(`${API_BASE_URL}/api/quotations/db/load/${q.quotation_number}`);
            if (res.ok) {
                const data = await res.json();
                setClient(data.client || { name: q.client_name || '', contact: '', address: '' });
                setProducts(data.products || []);
                setActiveTab(0);
            } else {
                const err = await res.text();
                console.error("Backend Error Response:", err);
                alert(`Error al cargar los detalles de la cotización: ${res.status} ${res.statusText}\n${err}`);
            }
        } catch (error) {
            console.error("Error fetching full quotation:", error);
            alert("Error de red al intentar cargar la cotización.");
        } finally {
            setLoading(false);
        }
    };

    const handleDrag = (e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === "dragenter" || e.type === "dragover") {
            setDragActive(true);
        } else if (e.type === "dragleave") {
            setDragActive(false);
        }
    };

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            handleFileUpload(e.dataTransfer.files[0]);
        }
    };

    const handleFileUpload = async (file: File) => {
        if (!file.name.endsWith('.cotz') && !file.name.endsWith('.json')) {
            alert('Solo se permiten archivos .cotz o .json');
            return;
        }

        try {
            setLoading(true);

            // Intentar leer de forma local primero si es un archivo exportado offline (JSON puro) o si no hay internet
            if (!navigator.onLine) {
                const reader = new FileReader();
                reader.onload = (e) => {
                    try {
                        const content = e.target?.result as string;
                        const data = JSON.parse(content);
                        setClient(data.client || { name: '', contact: '', address: '' });
                        setProducts(data.products || []);
                        setActiveTab(0);
                    } catch (err) {
                        alert("El archivo no pudo ser leído offline. Tal vez es un .cotz comprimido antiguo que requiere internet para procesarse en el servidor.");
                    } finally {
                        setLoading(false);
                    }
                };
                reader.readAsText(file);
                return;
            }

            const formData = new FormData();
            formData.append('file', file);
            
            const res = await fetch(`${API_BASE_URL}/api/quotations/upload`, {
                method: 'POST',
                body: formData
            });
            
            if (res.ok) {
                const data = await res.json();
                setClient(data.client || { name: '', contact: '', address: '' });
                setProducts(data.products || []);
                setActiveTab(0);
            } else {
                const errData = await res.json().catch(() => ({}));
                alert(`Error al leer archivo .cotz: ${errData.detail || res.statusText}`);
            }
        } catch (error) {
            // Fallback si el servidor está caído pero tenemos internet (PWA mode)
            const reader = new FileReader();
            reader.onload = (e) => {
                try {
                    const content = e.target?.result as string;
                    const data = JSON.parse(content);
                    setClient(data.client || { name: '', contact: '', address: '' });
                    setProducts(data.products || []);
                    setActiveTab(0);
                } catch (err) {
                    console.error("Error fetching upload:", error);
                    alert("No hay conexión con el servidor y el archivo no es un formato offline válido.");
                } finally {
                    setLoading(false);
                }
            };
            reader.readAsText(file);
        } finally {
            if (navigator.onLine) setLoading(false);
        }
    };

    return (
        <div className="space-y-6 p-6">
            
            {/* Upload Section */}
            <motion.div 
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="glass-panel rounded-3xl p-6 space-y-4"
            >
                <div className="flex items-center space-x-3 border-b border-[var(--border-default)] pb-4">
                    <span className="material-symbols-outlined text-3xl text-[var(--text-primary)]">file_open</span>
                    <h2 className="text-xl font-bold text-[var(--text-primary)]">Abrir Cotización (.cotz / .json)</h2>
                </div>

                <div 
                    className={`border-2 border-dashed rounded-3xl p-10 text-center cursor-pointer transition-all duration-300 flex flex-col items-center justify-center space-y-4 ${dragActive ? 'border-[var(--border-focus)] bg-white/10' : 'border-[var(--border-default)] bg-black/10 hover:border-[var(--border-focus)] hover:bg-white/5'}`}
                    onDragEnter={handleDrag}
                    onDragLeave={handleDrag}
                    onDragOver={handleDrag}
                    onDrop={handleDrop}
                    onClick={() => document.getElementById('file-upload')?.click()}
                >
                    <motion.div 
                        whileHover={{ scale: 1.1 }}
                        className="w-16 h-16 rounded-2xl bg-[var(--bg-secondary)] text-[var(--text-primary)] flex items-center justify-center shadow-lg"
                    >
                        <span className="material-symbols-outlined text-4xl">cloud_upload</span>
                    </motion.div>
                    <div>
                        <p className="font-bold text-lg text-[var(--text-primary)]">
                            Arrastra y suelta tu archivo <code className="text-sm bg-[var(--bg-secondary)] px-2 py-1 rounded-lg mx-1 border border-[var(--border-default)]">.cotz</code> aquí
                        </p>
                        <p className="text-sm text-[var(--text-secondary)] mt-2">o haz clic para explorar en tus archivos localmente</p>
                    </div>
                    <input 
                        type="file" 
                        id="file-upload" 
                        className="hidden" 
                        accept=".cotz,.json"
                        onChange={(e) => e.target.files && handleFileUpload(e.target.files[0])}
                    />
                </div>
            </motion.div>

            {/* History Table Section */}
            <motion.div 
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
                className="glass-panel rounded-3xl p-6 space-y-5"
            >
                <div className="flex items-center justify-between border-b border-[var(--border-default)] pb-4">
                    <div className="flex items-center space-x-3">
                        <span className="material-symbols-outlined text-3xl text-[var(--text-primary)]">history</span>
                        <h2 className="text-xl font-bold text-[var(--text-primary)]">Cotizaciones Guardadas e Historial</h2>
                    </div>
                    <button 
                        onClick={loadQuotations}
                        className="glass-button px-4 py-2 rounded-full text-sm font-bold flex items-center space-x-2"
                    >
                        <span className="material-symbols-outlined text-xl">refresh</span>
                        <span>Actualizar</span>
                    </button>
                </div>

                <div className="overflow-x-auto rounded-2xl border border-[var(--border-default)] bg-black/20 shadow-inner">
                    <table className="w-full text-left text-sm">
                        <thead className="bg-[var(--bg-secondary)] text-[var(--text-secondary)] uppercase font-semibold border-b border-[var(--border-default)]">
                            <tr>
                                <th className="p-4">N° Cotización</th>
                                <th className="p-4">Cliente</th>
                                <th className="p-4">Empresa Emisora</th>
                                <th className="p-4">Fecha</th>
                                <th className="p-4 text-right">Total</th>
                                <th className="p-4 text-center">Acciones</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-[var(--border-default)] text-[var(--text-primary)] font-medium">
                            {loading ? (
                                <tr>
                                    <td colSpan={6} className="p-8 text-center text-[var(--text-secondary)]">Cargando cotizaciones guardadas...</td>
                                </tr>
                            ) : quotations.length === 0 ? (
                                <tr>
                                    <td colSpan={6} className="p-8 text-center text-[var(--text-secondary)]">No hay cotizaciones guardadas en la base de datos.</td>
                                </tr>
                            ) : (
                                quotations.map((q) => (
                                    <motion.tr 
                                        key={q.quotation_number}
                                        whileHover={{ backgroundColor: 'rgba(255,255,255,0.05)' }}
                                        className="transition-colors"
                                    >
                                        <td className="p-4 font-mono">{q.quotation_number}</td>
                                        <td className="p-4">{q.client_name || 'N/A'}</td>
                                        <td className="p-4">{q.company_name || 'N/A'}</td>
                                        <td className="p-4">{q.date}</td>
                                        <td className="p-4 text-right font-bold">{q.total.toFixed(2)}</td>
                                        <td className="p-4 text-center">
                                            <button 
                                                onClick={() => handleLoadQuotation(q)}
                                                className="glass-button px-4 py-1.5 rounded-full font-bold shadow-md transition-colors"
                                            >
                                                Cargar
                                            </button>
                                        </td>
                                    </motion.tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            </motion.div>

        </div>
    );
}
