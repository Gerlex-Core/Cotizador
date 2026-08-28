import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { cleanQtHtml } from '../../utils/sanitize';
import { API_BASE_URL } from '../../config/apiConfig';

type Company = {
    nombre: string;
    nit: string;
    direccion: string;
    telefono: string;
    correo: string;
    ciudad: string;
    logo: string;
    firma: string;
    es_predeterminada: boolean;
};

export default function CompanyView() {
    const [companies, setCompanies] = useState<Company[]>([]);
    const [selectedCompany, setSelectedCompany] = useState<Company | null>(null);

    const loadCompanies = async () => {
        try {
            const res = await fetch(`${API_BASE_URL}/api/companies/details`);
            if (res.ok) {
                const data = await res.json();
                setCompanies(data);
                if (data.length > 0 && !selectedCompany) {
                    setSelectedCompany(data[0]);
                }
            }
        } catch (error) {
            console.error("Error loading companies:", error);
        }
    };

    useEffect(() => {
        loadCompanies();
    }, []);

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
        if (selectedCompany) {
            setSelectedCompany({
                ...selectedCompany,
                [e.target.name]: cleanQtHtml(e.target.value)
            });
        }
    };

    const handleSave = async () => {
        if (!selectedCompany) return;
        try {
            const res = await fetch(`${API_BASE_URL}/api/companies`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(selectedCompany)
            });
            if (res.ok) {
                alert("Empresa guardada correctamente.");
                loadCompanies();
            }
        } catch (error) {
            console.error("Error saving company:", error);
        }
    };

    const handleNewCompany = () => {
        setSelectedCompany({
            nombre: 'Nueva Empresa',
            nit: '',
            direccion: '',
            telefono: '',
            correo: '',
            ciudad: '',
            logo: '',
            firma: '',
            es_predeterminada: false
        });
    };

    return (
        <div className="flex gap-6 h-full">
            {/* List */}
            <div className="w-1/3 glass-panel rounded-3xl p-4 flex flex-col h-[60vh]">
                <div className="flex items-center justify-between mb-4 pb-2 border-b border-[var(--border-default)]">
                    <h3 className="font-bold text-[var(--text-primary)]">Empresas</h3>
                    <motion.button 
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={handleNewCompany}
                        className="glass-button p-1.5 rounded-xl text-emerald-400"
                    >
                        <span className="material-symbols-outlined text-sm">add</span>
                    </motion.button>
                </div>
                <div className="flex-1 overflow-y-auto space-y-2 pr-1">
                    {companies.map(company => (
                        <motion.button
                            key={company.nombre}
                            whileHover={{ x: 4 }}
                            onClick={() => setSelectedCompany(company)}
                            className={`w-full text-left px-4 py-3 rounded-2xl transition-all flex items-center space-x-3 ${selectedCompany?.nombre === company.nombre ? 'bg-[var(--text-primary)] text-[var(--bg-primary)] shadow-md' : 'glass-button'}`}
                        >
                            <span className="material-symbols-outlined">domain</span>
                            <span className="font-semibold text-sm truncate">{company.nombre}</span>
                        </motion.button>
                    ))}
                </div>
            </div>

            {/* Detail Form */}
            <div className="flex-1 glass-panel rounded-3xl p-6 overflow-y-auto h-[60vh]">
                {selectedCompany ? (
                    <motion.div 
                        key={selectedCompany.nombre}
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        className="space-y-4"
                    >
                        <div className="flex justify-between items-center pb-4 border-b border-[var(--border-default)]">
                            <h2 className="text-xl font-bold flex items-center space-x-2">
                                <span className="material-symbols-outlined">edit_document</span>
                                <span>Editar Detalles</span>
                            </h2>
                            <motion.button 
                                whileHover={{ scale: 1.05 }}
                                whileTap={{ scale: 0.95 }}
                                onClick={handleSave}
                                className="px-4 py-2 bg-[var(--text-primary)] text-[var(--bg-primary)] rounded-full font-bold shadow-lg flex items-center space-x-2"
                            >
                                <span className="material-symbols-outlined text-sm">save</span>
                                <span>Guardar Empresa</span>
                            </motion.button>
                        </div>

                        <div className="grid grid-cols-2 gap-4 text-sm">
                            <div className="space-y-1">
                                <label className="text-[var(--text-secondary)] font-medium text-xs">Razón Social</label>
                                <input type="text" name="nombre" value={selectedCompany.nombre} onChange={handleInputChange} className="glass-input w-full p-2.5 rounded-xl font-semibold" />
                            </div>
                            <div className="space-y-1">
                                <label className="text-[var(--text-secondary)] font-medium text-xs">NIT / Documento</label>
                                <input type="text" name="nit" value={selectedCompany.nit} onChange={handleInputChange} className="glass-input w-full p-2.5 rounded-xl font-semibold" />
                            </div>
                            <div className="col-span-2 space-y-1">
                                <label className="text-[var(--text-secondary)] font-medium text-xs">Dirección</label>
                                <input type="text" name="direccion" value={selectedCompany.direccion} onChange={handleInputChange} className="glass-input w-full p-2.5 rounded-xl font-semibold" />
                            </div>
                            <div className="space-y-1">
                                <label className="text-[var(--text-secondary)] font-medium text-xs">Teléfono</label>
                                <input type="text" name="telefono" value={selectedCompany.telefono} onChange={handleInputChange} className="glass-input w-full p-2.5 rounded-xl font-semibold" />
                            </div>
                            <div className="space-y-1">
                                <label className="text-[var(--text-secondary)] font-medium text-xs">Correo</label>
                                <input type="text" name="correo" value={selectedCompany.correo} onChange={handleInputChange} className="glass-input w-full p-2.5 rounded-xl font-semibold" />
                            </div>
                        </div>

                        {/* Dropzones for images would go here, omitting for brevity but maintaining structure */}
                        <div className="pt-4 flex gap-4">
                            <div className="flex-1 glass-button rounded-2xl p-4 text-center border-dashed border-2 flex flex-col items-center cursor-pointer">
                                <span className="material-symbols-outlined text-3xl text-[var(--text-secondary)] mb-2">image</span>
                                <span className="text-xs font-bold">Logo de Empresa</span>
                            </div>
                            <div className="flex-1 glass-button rounded-2xl p-4 text-center border-dashed border-2 flex flex-col items-center cursor-pointer">
                                <span className="material-symbols-outlined text-3xl text-[var(--text-secondary)] mb-2">draw</span>
                                <span className="text-xs font-bold">Firma Digital</span>
                            </div>
                        </div>
                    </motion.div>
                ) : (
                    <div className="h-full flex items-center justify-center text-[var(--text-secondary)]">
                        Selecciona una empresa para editar
                    </div>
                )}
            </div>
        </div>
    );
}
