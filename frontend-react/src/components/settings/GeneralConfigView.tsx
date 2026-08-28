import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { API_BASE_URL } from '../../config/apiConfig';

export default function GeneralConfigView() {
    const [config, setConfig] = useState<any>({});
    
    useEffect(() => {
        const loadConfig = async () => {
            try {
                const res = await fetch(`${API_BASE_URL}/api/config`);
                if (res.ok) {
                    const data = await res.json();
                    setConfig(data.config || {});
                }
            } catch (error) {
                console.error("Error loading config:", error);
            }
        };
        loadConfig();
    }, []);

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
        const value = e.target.type === 'checkbox' ? (e.target as HTMLInputElement).checked : e.target.value;
        setConfig({ ...config, [e.target.name]: value });
    };

    const handleSave = async () => {
        try {
            const res = await fetch(`${API_BASE_URL}/api/config`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(config)
            });
            if (res.ok) {
                alert("Configuración guardada correctamente.");
            }
        } catch (error) {
            console.error("Error saving config:", error);
        }
    };

    return (
        <div className="glass-panel rounded-3xl p-6 overflow-y-auto h-[60vh] space-y-6">
            <div className="flex justify-between items-center border-b border-[var(--border-default)] pb-4">
                <h2 className="text-xl font-bold flex items-center space-x-2">
                    <span className="material-symbols-outlined">settings_applications</span>
                    <span>Configuración General & PDF</span>
                </h2>
                <motion.button 
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={handleSave}
                    className="px-5 py-2 bg-[var(--text-primary)] text-[var(--bg-primary)] rounded-full font-bold shadow-lg flex items-center space-x-2"
                >
                    <span className="material-symbols-outlined text-sm">save</span>
                    <span>Guardar Cambios</span>
                </motion.button>
            </div>

            <div className="grid grid-cols-2 gap-8">
                {/* PDF Margins */}
                <div className="space-y-4">
                    <h3 className="font-bold flex items-center space-x-2 text-[var(--text-secondary)]">
                        <span className="material-symbols-outlined text-lg">margin</span>
                        <span>Márgenes PDF (pt)</span>
                    </h3>
                    <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-1">
                            <label className="text-xs">Superior</label>
                            <input type="number" name="margin_top" value={config.margin_top || 40} onChange={handleChange} className="glass-input w-full p-2 rounded-xl text-center" />
                        </div>
                        <div className="space-y-1">
                            <label className="text-xs">Inferior</label>
                            <input type="number" name="margin_bottom" value={config.margin_bottom || 40} onChange={handleChange} className="glass-input w-full p-2 rounded-xl text-center" />
                        </div>
                        <div className="space-y-1">
                            <label className="text-xs">Izquierdo</label>
                            <input type="number" name="margin_left" value={config.margin_left || 40} onChange={handleChange} className="glass-input w-full p-2 rounded-xl text-center" />
                        </div>
                        <div className="space-y-1">
                            <label className="text-xs">Derecho</label>
                            <input type="number" name="margin_right" value={config.margin_right || 40} onChange={handleChange} className="glass-input w-full p-2 rounded-xl text-center" />
                        </div>
                    </div>
                </div>

                {/* General Settings */}
                <div className="space-y-4">
                    <h3 className="font-bold flex items-center space-x-2 text-[var(--text-secondary)]">
                        <span className="material-symbols-outlined text-lg">tune</span>
                        <span>Preferencias</span>
                    </h3>
                    <div className="space-y-3">
                        <div className="space-y-1">
                            <label className="text-xs">Moneda Predeterminada</label>
                            <select name="moneda" value={config.moneda || 'Bolivianos (Bs)'} onChange={handleChange} className="glass-input w-full p-2 rounded-xl">
                                <option value="Bolivianos (Bs)">Bolivianos (Bs)</option>
                                <option value="Dólares ($us)">Dólares ($us)</option>
                            </select>
                        </div>
                        <div className="space-y-1">
                            <label className="text-xs">Fuente de PDF</label>
                            <select name="fuente" value={config.fuente || 'Roboto'} onChange={handleChange} className="glass-input w-full p-2 rounded-xl">
                                <option value="Roboto">Roboto</option>
                                <option value="Arial">Arial</option>
                                <option value="Helvetica">Helvetica</option>
                            </select>
                        </div>
                        <div className="space-y-1">
                            <label className="text-xs">Preparado Por (Default)</label>
                            <input type="text" name="prepared_by" value={config.prepared_by || ''} onChange={handleChange} className="glass-input w-full p-2 rounded-xl" placeholder="Nombre del vendedor" />
                        </div>
                        <label className="flex items-center space-x-3 mt-4 cursor-pointer">
                            <input type="checkbox" name="watermark_enabled" checked={config.watermark_enabled || false} onChange={handleChange} className="w-4 h-4 rounded" />
                            <span className="text-sm font-semibold">Habilitar Marca de Agua</span>
                        </label>
                    </div>
                </div>
            </div>
        </div>
    );
}
