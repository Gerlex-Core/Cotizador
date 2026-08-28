import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface AppRelease {
    id: string;
    name: string;
    version: string;
    date: string;
    apk_url: string;
    icon_url: string;
    size_bytes: number;
}

export default function StoreView({ onClose }: { onClose: () => void }) {
    const [apps, setApps] = useState<AppRelease[]>([]);
    const [loading, setLoading] = useState(true);
    const [apiUrl, setApiUrl] = useState('');

    useEffect(() => {
        const fetchApps = async () => {
            try {
                const { API_BASE_URL } = await import('../../config/apiConfig');
                setApiUrl(API_BASE_URL);
                const response = await fetch(`${API_BASE_URL}/api/store/apps`);
                if (response.ok) {
                    const data = await response.json();
                    setApps(data.apps || []);
                }
            } catch (error) {
                console.error("Error fetching apps", error);
            } finally {
                setLoading(false);
            }
        };
        fetchApps();
    }, []);

    return (
        <AnimatePresence>
            <motion.div 
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm"
            >
                <motion.div 
                    initial={{ scale: 0.9, y: 20 }}
                    animate={{ scale: 1, y: 0 }}
                    exit={{ scale: 0.9, y: 20 }}
                    className="glass-panel w-full max-w-3xl rounded-3xl overflow-hidden shadow-2xl border border-white/10 flex flex-col"
                    style={{ maxHeight: '90vh' }}
                >
                    {/* Header */}
                    <div className="px-6 py-4 border-b border-white/10 flex justify-between items-center bg-white/5">
                        <div className="flex items-center space-x-3">
                            <span className="material-symbols-outlined text-3xl text-emerald-400">shop</span>
                            <h2 className="text-xl font-bold text-white">Tienda de Aplicaciones</h2>
                        </div>
                        <button onClick={onClose} className="p-2 hover:bg-white/10 rounded-full transition-colors text-gray-400 hover:text-white">
                            <span className="material-symbols-outlined">close</span>
                        </button>
                    </div>

                    {/* Content */}
                    <div className="p-6 overflow-y-auto flex-1">
                        {loading ? (
                            <div className="flex justify-center items-center py-20">
                                <span className="material-symbols-outlined animate-spin text-4xl text-[var(--accent-primary)]">progress_activity</span>
                            </div>
                        ) : apps.length === 0 ? (
                            <div className="text-center py-20 text-gray-400">
                                <span className="material-symbols-outlined text-6xl mb-4 opacity-50">sentiment_dissatisfied</span>
                                <p className="text-lg">No hay versiones publicadas aún.</p>
                                <p className="text-sm mt-2 opacity-70">Usa el CLI (Opción 4 -&gt; 3) para compilar y subir la app móvil.</p>
                            </div>
                        ) : (
                            <div className="space-y-6">
                                {apps.map((app, index) => (
                                    <div key={app.id} className={`glass-panel p-6 rounded-2xl flex flex-col md:flex-row items-center gap-6 ${index === 0 ? 'border-2 border-emerald-500/50 relative overflow-hidden' : 'opacity-80'}`}>
                                        {index === 0 && (
                                            <div className="absolute top-0 right-0 bg-emerald-500 text-white text-[10px] font-bold px-3 py-1 rounded-bl-xl uppercase tracking-wider">
                                                Última Versión
                                            </div>
                                        )}
                                        <div className="relative">
                                            <img src={`${apiUrl}${app.icon_url}`} alt="App Icon" className="w-24 h-24 rounded-2xl shadow-lg object-cover bg-white/10" onError={(e) => { e.currentTarget.src = 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="128" height="128" viewBox="0 0 24 24"><path fill="%23fff" d="M17.523 15.3414c-.5511 0-.9993-.4486-.9993-.9997s.4483-.9993.9993-.9993c.5511 0 .9993.4482.9993.9993.0001.5511-.4482.9997-.9993.9997zm-11.046 0c-.5511 0-.9993-.4486-.9993-.9997s.4482-.9993.9993-.9993c.5511 0 .9993.4482.9993.9993 0 .5511-.4482.9997-.9993.9997zm11.4045-6.02l1.9973-3.4592a.416.416 0 00-.1517-.5677.416.416 0 00-.5677.1517l-2.0315 3.5173c-1.4243-.65-3.0456-1.0263-4.7876-1.0263-1.7416 0-3.3633.3763-4.7872 1.0263l-2.0315-3.5173a.416.416 0 00-.5677-.1517.416.416 0 00-.1517.5677l1.9973 3.4592C4.3821 10.5902 2.5937 13.1118 2 16.1906h20c-.5937-3.0788-2.3821-5.6004-4.1185-6.8692z"/></svg>'; }} />
                                        </div>
                                        <div className="flex-1 text-center md:text-left">
                                            <h3 className="text-2xl font-bold text-white mb-1">{app.name}</h3>
                                            <div className="flex items-center justify-center md:justify-start space-x-3 text-sm text-gray-300 mb-3">
                                                <span className="bg-white/10 px-2 py-0.5 rounded-lg font-mono">v{app.version}</span>
                                                <span>{(app.size_bytes / 1024 / 1024).toFixed(1)} MB</span>
                                            </div>
                                            <p className="text-xs text-gray-400">Publicado: {new Date(app.date).toLocaleDateString()} {new Date(app.date).toLocaleTimeString()}</p>
                                        </div>
                                        <button 
                                            onClick={() => window.open(`${apiUrl}${app.apk_url}`, '_blank')}
                                            className={`px-6 py-3 rounded-2xl font-bold flex items-center space-x-2 transition-all shadow-lg hover:scale-105 active:scale-95 ${index === 0 ? 'bg-emerald-500 hover:bg-emerald-400 text-white' : 'glass-button text-gray-200'}`}
                                        >
                                            <span className="material-symbols-outlined">{index === 0 ? 'download' : 'history'}</span>
                                            <span>{index === 0 ? 'Instalar Ahora' : 'Descargar'}</span>
                                        </button>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                </motion.div>
            </motion.div>
        </AnimatePresence>
    );
}
