import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface AppVersion {
    version: string;
    apk_url: string;
    size_bytes: number;
    published_at: string;
}

interface StoreApp {
    id: string;
    name: string;
    description: string;
    icon_url: string;
    created_at: string;
    latest_version: string;
    versions: AppVersion[];
}

export default function StoreView() {
    const [apps, setApps] = useState<StoreApp[]>([]);
    const [loading, setLoading] = useState(true);
    const [apiUrl, setApiUrl] = useState('');
    const [selectedApp, setSelectedApp] = useState<StoreApp | null>(null);

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

    const handleDownload = (apk_url: string) => {
        window.open(`${apiUrl}${apk_url}`, '_blank');
    };

    if (loading) {
        return (
            <div className="flex h-full items-center justify-center">
                <span className="material-symbols-outlined animate-spin text-6xl text-[var(--accent-primary)]">progress_activity</span>
            </div>
        );
    }

    if (selectedApp) {
        return (
            <motion.div 
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                className="h-full flex flex-col p-4 md:p-8 overflow-y-auto"
            >
                <button 
                    onClick={() => setSelectedApp(null)}
                    className="self-start flex items-center space-x-2 text-gray-400 hover:text-white transition-colors mb-8"
                >
                    <span className="material-symbols-outlined">arrow_back</span>
                    <span className="font-bold">Volver al Catálogo</span>
                </button>

                <div className="flex flex-col md:flex-row gap-8 items-start">
                    <img 
                        src={`${apiUrl}${selectedApp.icon_url}`} 
                        alt="App Icon" 
                        className="w-40 h-40 rounded-3xl shadow-2xl object-cover bg-white/5 border border-white/10" 
                        onError={(e) => { e.currentTarget.src = 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="128" height="128" viewBox="0 0 24 24"><path fill="%23fff" d="M17.523 15.3414c-.5511 0-.9993-.4486-.9993-.9997s.4483-.9993.9993-.9993c.5511 0 .9993.4482.9993.9993.0001.5511-.4482.9997-.9993.9997zm-11.046 0c-.5511 0-.9993-.4486-.9993-.9997s.4482-.9993.9993-.9993c.5511 0 .9993.4482.9993.9993 0 .5511-.4482.9997-.9993.9997zm11.4045-6.02l1.9973-3.4592a.416.416 0 00-.1517-.5677.416.416 0 00-.5677.1517l-2.0315 3.5173c-1.4243-.65-3.0456-1.0263-4.7876-1.0263-1.7416 0-3.3633.3763-4.7872 1.0263l-2.0315-3.5173a.416.416 0 00-.5677-.1517.416.416 0 00-.1517.5677l1.9973 3.4592C4.3821 10.5902 2.5937 13.1118 2 16.1906h20c-.5937-3.0788-2.3821-5.6004-4.1185-6.8692z"/></svg>'; }} 
                    />
                    <div className="flex-1">
                        <h1 className="text-4xl font-black text-white mb-2">{selectedApp.name}</h1>
                        <p className="text-gray-400 mb-6 text-lg">{selectedApp.description || "Sin descripción disponible."}</p>
                        
                        <button 
                            onClick={() => handleDownload(selectedApp.versions[0].apk_url)}
                            className="bg-emerald-500 hover:bg-emerald-400 text-white font-bold py-4 px-8 rounded-2xl shadow-lg hover:shadow-emerald-500/25 transition-all hover:scale-105 active:scale-95 flex items-center space-x-3 text-lg"
                        >
                            <span className="material-symbols-outlined text-2xl">download</span>
                            <span>Descargar Última Versión (v{selectedApp.latest_version})</span>
                        </button>
                    </div>
                </div>

                <div className="mt-12">
                    <h3 className="text-xl font-bold text-white mb-6 flex items-center space-x-2">
                        <span className="material-symbols-outlined">history</span>
                        <span>Historial de Versiones</span>
                    </h3>
                    <div className="glass-panel rounded-2xl overflow-hidden border border-white/10">
                        <table className="w-full text-left border-collapse">
                            <thead>
                                <tr className="bg-white/5 border-b border-white/10">
                                    <th className="p-4 text-gray-300 font-semibold">Versión</th>
                                    <th className="p-4 text-gray-300 font-semibold">Fecha de Publicación</th>
                                    <th className="p-4 text-gray-300 font-semibold">Peso</th>
                                    <th className="p-4 text-right text-gray-300 font-semibold">Acción</th>
                                </tr>
                            </thead>
                            <tbody>
                                {selectedApp.versions.map((ver, idx) => (
                                    <tr key={ver.version} className="border-b border-white/5 hover:bg-white/5 transition-colors">
                                        <td className="p-4">
                                            <div className="flex items-center space-x-2">
                                                <span className="font-mono font-bold text-white">v{ver.version}</span>
                                                {idx === 0 && (
                                                    <span className="bg-emerald-500/20 text-emerald-400 text-xs px-2 py-0.5 rounded-full font-bold uppercase">Actual</span>
                                                )}
                                            </div>
                                        </td>
                                        <td className="p-4 text-gray-400 text-sm">
                                            {new Date(ver.published_at).toLocaleString()}
                                        </td>
                                        <td className="p-4 text-gray-400 text-sm font-mono">
                                            {(ver.size_bytes / 1024 / 1024).toFixed(1)} MB
                                        </td>
                                        <td className="p-4 text-right">
                                            <button 
                                                onClick={() => handleDownload(ver.apk_url)}
                                                className="glass-button px-4 py-2 text-sm font-bold text-gray-200 hover:text-white transition-colors flex items-center space-x-2 ml-auto"
                                            >
                                                <span className="material-symbols-outlined text-sm">download</span>
                                                <span>Descargar</span>
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            </motion.div>
        );
    }

    return (
        <div className="h-full flex flex-col p-4 md:p-8">
            <div className="flex items-center space-x-4 mb-8">
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-emerald-400 to-teal-600 flex items-center justify-center shadow-lg">
                    <span className="material-symbols-outlined text-white text-2xl">shop</span>
                </div>
                <div>
                    <h1 className="text-3xl font-black text-white tracking-tight">Tienda de Aplicaciones</h1>
                    <p className="text-gray-400">Descarga e instala las herramientas oficiales en tus dispositivos.</p>
                </div>
            </div>

            {apps.length === 0 ? (
                <div className="flex-1 flex flex-col items-center justify-center text-center">
                    <span className="material-symbols-outlined text-8xl text-gray-600 mb-4">cloud_off</span>
                    <h2 className="text-2xl font-bold text-gray-400 mb-2">No hay aplicaciones disponibles</h2>
                    <p className="text-gray-500 max-w-md">Utiliza la CLI (Opción 5) para subir archivos APK a la tienda de tu servidor.</p>
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                    <AnimatePresence>
                        {apps.map((app, i) => (
                            <motion.div
                                key={app.id}
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: i * 0.05 }}
                                onClick={() => setSelectedApp(app)}
                                className="glass-panel p-6 rounded-3xl cursor-pointer hover:bg-white/10 transition-all hover:-translate-y-1 hover:shadow-xl border border-white/5 flex flex-col items-center text-center group"
                            >
                                <img 
                                    src={`${apiUrl}${app.icon_url}`} 
                                    alt={app.name} 
                                    className="w-24 h-24 rounded-2xl mb-4 shadow-lg object-cover bg-white/5 group-hover:scale-105 transition-transform"
                                    onError={(e) => { e.currentTarget.src = 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="128" height="128" viewBox="0 0 24 24"><path fill="%23fff" d="M17.523 15.3414c-.5511 0-.9993-.4486-.9993-.9997s.4483-.9993.9993-.9993c.5511 0 .9993.4482.9993.9993.0001.5511-.4482.9997-.9993.9997zm-11.046 0c-.5511 0-.9993-.4486-.9993-.9997s.4482-.9993.9993-.9993c.5511 0 .9993.4482.9993.9993 0 .5511-.4482.9997-.9993.9997zm11.4045-6.02l1.9973-3.4592a.416.416 0 00-.1517-.5677.416.416 0 00-.5677.1517l-2.0315 3.5173c-1.4243-.65-3.0456-1.0263-4.7876-1.0263-1.7416 0-3.3633.3763-4.7872 1.0263l-2.0315-3.5173a.416.416 0 00-.5677-.1517.416.416 0 00-.1517.5677l1.9973 3.4592C4.3821 10.5902 2.5937 13.1118 2 16.1906h20c-.5937-3.0788-2.3821-5.6004-4.1185-6.8692z"/></svg>'; }} 
                                />
                                <h3 className="text-xl font-bold text-white mb-1">{app.name}</h3>
                                <span className="bg-white/10 text-gray-300 text-xs px-2 py-1 rounded-lg font-mono mb-3">
                                    v{app.latest_version}
                                </span>
                                <p className="text-sm text-gray-400 line-clamp-2">
                                    {app.description || "Haz clic para ver detalles y versiones."}
                                </p>
                            </motion.div>
                        ))}
                    </AnimatePresence>
                </div>
            )}
        </div>
    );
}
