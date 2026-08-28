import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface AppVersion {
    version: string;
    apk_url: string;
    size_bytes: number;
    published_at: string;
    description?: string;
    icon_url?: string;
}

interface StoreApp {
    id: string;
    name: string;
    description: string;
    icon_url: string;
    created_at: string;
    latest_version: string;
    downloads: number;
    likes: number;
    liked_by_me: boolean;
    versions: AppVersion[];
}

export default function StoreView() {
    const [viewMode, setViewMode] = useState<'catalog' | 'app_detail' | 'version_detail'>('catalog');
    const [apps, setApps] = useState<StoreApp[]>([]);
    const [loading, setLoading] = useState(true);
    const [apiUrl, setApiUrl] = useState('');
    const [deviceId, setDeviceId] = useState('');
    const [selectedApp, setSelectedApp] = useState<StoreApp | null>(null);
    const [selectedVersion, setSelectedVersion] = useState<AppVersion | null>(null);

    useEffect(() => {
        const fetchApps = async () => {
            try {
                let dId = localStorage.getItem("store_device_id");
                if (!dId) {
                    dId = "dev_" + Math.random().toString(36).substring(2, 15) + Date.now().toString(36);
                    localStorage.setItem("store_device_id", dId);
                }
                setDeviceId(dId);

                const { API_BASE_URL } = await import('../../config/apiConfig');
                setApiUrl(API_BASE_URL);
                const response = await fetch(`${API_BASE_URL}/api/store/apps`, {
                    headers: {
                        'X-Device-ID': dId
                    }
                });
                if (response.ok) {
                    const data = await response.json();
                    const appsData = data.apps || [];
                    setApps(appsData);

                    const pathParts = window.location.pathname.split('/').filter(Boolean);
                    if (pathParts[0] === 'store' && pathParts[1]) {
                        const appId = pathParts[1];
                        const app = appsData.find((a: StoreApp) => a.id === appId);
                        if (app) {
                            setSelectedApp(app);
                            if (pathParts[2]) {
                                if (pathParts[2] === 'all') {
                                    setViewMode('app_detail');
                                } else if (pathParts[2].startsWith('v')) {
                                    const verNum = pathParts[2].substring(1);
                                    const ver = app.versions.find((v: AppVersion) => v.version === verNum);
                                    if (ver) {
                                        setSelectedVersion(ver);
                                        setViewMode('version_detail');
                                    } else {
                                        setViewMode('app_detail');
                                    }
                                } else {
                                    setViewMode('app_detail');
                                }
                            } else {
                                setViewMode('app_detail');
                            }
                        } else {
                            setViewMode('catalog');
                        }
                    } else {
                        setViewMode('catalog');
                    }
                }
            } catch (error) {
                console.error("Error fetching apps", error);
            } finally {
                setLoading(false);
            }
        };
        fetchApps();
    }, []);

    const handleSelectApp = (app: StoreApp) => {
        setSelectedApp(app);
        setViewMode('app_detail');
        window.history.pushState({}, "", `/store/${app.id}`);
    };

    const handleSelectVersion = (app: StoreApp, ver: AppVersion) => {
        setSelectedApp(app);
        setSelectedVersion(ver);
        setViewMode('version_detail');
        window.history.pushState({}, "", `/store/${app.id}/v${ver.version}`);
    };

    const handleBackToCatalog = () => {
        setSelectedApp(null);
        setSelectedVersion(null);
        setViewMode('catalog');
        window.history.pushState({}, "", `/store`);
    };

    const handleBackToApp = () => {
        setViewMode('app_detail');
        window.history.pushState({}, "", `/store/${selectedApp?.id}`);
    };

    const handleDownload = async (app: StoreApp, apk_url: string) => {
        try {
            const res = await fetch(`${apiUrl}/api/store/${app.id}/download`, { 
                method: 'POST',
                headers: { 'X-Device-ID': deviceId }
            });
            const data = await res.json();
            if (data.tracked) {
                setApps(prev => prev.map(a => a.id === app.id ? { ...a, downloads: a.downloads + 1 } : a));
                if (selectedApp?.id === app.id) {
                    setSelectedApp(prev => prev ? { ...prev, downloads: prev.downloads + 1 } : null);
                }
            }
        } catch (err) {
            console.error(err);
        }
        window.open(`${apiUrl}${apk_url}`, '_blank');
    };

    const handleLike = async (app: StoreApp, e: React.MouseEvent) => {
        e.stopPropagation();
        try {
            const res = await fetch(`${apiUrl}/api/store/${app.id}/like`, { 
                method: 'POST',
                headers: { 'X-Device-ID': deviceId }
            });
            const data = await res.json();
            
            if (data.action === "liked") {
                setApps(prev => prev.map(a => a.id === app.id ? { ...a, likes: a.likes + 1, liked_by_me: true } : a));
                if (selectedApp?.id === app.id) {
                    setSelectedApp(prev => prev ? { ...prev, likes: prev.likes + 1, liked_by_me: true } : null);
                }
            } else if (data.action === "unliked") {
                setApps(prev => prev.map(a => a.id === app.id ? { ...a, likes: a.likes - 1, liked_by_me: false } : a));
                if (selectedApp?.id === app.id) {
                    setSelectedApp(prev => prev ? { ...prev, likes: prev.likes - 1, liked_by_me: false } : null);
                }
            }
        } catch (err) {
            console.error(err);
        }
    };

    if (loading) {
        return (
            <div className="flex h-full items-center justify-center">
                <span className="material-symbols-outlined animate-spin text-6xl text-[var(--accent-primary)]">progress_activity</span>
            </div>
        );
    }

    if (viewMode === 'version_detail' && selectedApp && selectedVersion) {
        return (
            <motion.div 
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                className="h-full flex flex-col p-4 md:p-8 overflow-y-auto"
            >
                <button 
                    onClick={handleBackToApp}
                    className="self-start flex items-center space-x-2 text-gray-400 hover:text-white transition-colors mb-8"
                >
                    <span className="material-symbols-outlined">arrow_back</span>
                    <span className="font-bold">Volver a {selectedApp.name}</span>
                </button>

                <div className="flex flex-col md:flex-row gap-8 items-start">
                    <img 
                        src={`${apiUrl}${selectedVersion.icon_url || selectedApp.icon_url}`} 
                        alt="App Icon" 
                        className="w-40 h-40 rounded-3xl shadow-2xl object-cover bg-white/5 border border-white/10" 
                        onError={(e) => { e.currentTarget.src = 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="128" height="128" viewBox="0 0 24 24"><path fill="%23fff" d="M17.523 15.3414c-.5511 0-.9993-.4486-.9993-.9997s.4483-.9993.9993-.9993c.5511 0 .9993.4482.9993.9993.0001.5511-.4482.9997-.9993.9997zm-11.046 0c-.5511 0-.9993-.4486-.9993-.9997s.4482-.9993.9993-.9993c.5511 0 .9993.4482.9993.9993 0 .5511-.4482.9997-.9993.9997zm11.4045-6.02l1.9973-3.4592a.416.416 0 00-.1517-.5677.416.416 0 00-.5677.1517l-2.0315 3.5173c-1.4243-.65-3.0456-1.0263-4.7876-1.0263-1.7416 0-3.3633.3763-4.7872 1.0263l-2.0315-3.5173a.416.416 0 00-.5677-.1517.416.416 0 00-.1517.5677l1.9973 3.4592C4.3821 10.5902 2.5937 13.1118 2 16.1906h20c-.5937-3.0788-2.3821-5.6004-4.1185-6.8692z"/></svg>'; }} 
                    />
                    <div className="flex-1">
                        <h1 className="text-4xl font-black text-white mb-2">{selectedApp.name} <span className="text-emerald-400">v{selectedVersion.version}</span></h1>
                        <p className="text-gray-400 mb-6 text-lg">{selectedVersion.description || selectedApp.description || "Sin descripción disponible para esta versión."}</p>
                        
                        <div className="flex items-center space-x-6 mb-6">
                            <div className="flex items-center space-x-2 text-emerald-400">
                                <span className="material-symbols-outlined">download</span>
                                <span className="font-bold text-xl">{selectedApp.downloads}</span>
                            </div>
                            <button 
                                onClick={(e) => handleLike(selectedApp, e)}
                                className={`flex items-center space-x-2 transition-colors ${selectedApp.liked_by_me ? 'text-pink-500 hover:text-pink-400' : 'text-pink-400/50 hover:text-pink-400'}`}
                            >
                                <span className={`material-symbols-outlined font-bold ${selectedApp.liked_by_me ? 'fill-current' : ''}`} style={selectedApp.liked_by_me ? { fontVariationSettings: "'FILL' 1" } : {}}>favorite</span>
                                <span className="font-bold text-xl">{selectedApp.likes}</span>
                            </button>
                        </div>
                        <button 
                            onClick={() => handleDownload(selectedApp, selectedVersion.apk_url)}
                            className="bg-emerald-500 hover:bg-emerald-400 text-white font-bold py-4 px-8 rounded-2xl shadow-lg hover:shadow-emerald-500/25 transition-all hover:scale-105 active:scale-95 flex items-center space-x-3 text-lg"
                        >
                            <span className="material-symbols-outlined text-2xl">download</span>
                            <span>Descargar Versión (v{selectedVersion.version})</span>
                        </button>
                    </div>
                </div>
            </motion.div>
        );
    }

    if (viewMode === 'app_detail' && selectedApp) {
        return (
            <motion.div 
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                className="h-full flex flex-col p-4 md:p-8 overflow-y-auto"
            >
                <button 
                    onClick={handleBackToCatalog}
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
                        
                        <div className="flex items-center space-x-6 mb-6">
                            <div className="flex items-center space-x-2 text-emerald-400">
                                <span className="material-symbols-outlined">download</span>
                                <span className="font-bold text-xl">{selectedApp.downloads}</span>
                            </div>
                            <button 
                                onClick={(e) => handleLike(selectedApp, e)}
                                className={`flex items-center space-x-2 transition-colors ${selectedApp.liked_by_me ? 'text-pink-500 hover:text-pink-400' : 'text-pink-400/50 hover:text-pink-400'}`}
                            >
                                <span className={`material-symbols-outlined font-bold ${selectedApp.liked_by_me ? 'fill-current' : ''}`} style={selectedApp.liked_by_me ? { fontVariationSettings: "'FILL' 1" } : {}}>favorite</span>
                                <span className="font-bold text-xl">{selectedApp.likes}</span>
                            </button>
                        </div>
                        
                        <button 
                            onClick={() => handleDownload(selectedApp, selectedApp.versions[0].apk_url)}
                            className="bg-emerald-500 hover:bg-emerald-400 text-white font-bold py-4 px-8 rounded-2xl shadow-lg hover:shadow-emerald-500/25 transition-all hover:scale-105 active:scale-95 flex items-center space-x-3 text-lg"
                        >
                            <span className="material-symbols-outlined text-2xl">download</span>
                            <span>Descargar Última Versión (v{selectedApp.latest_version})</span>
                        </button>
                    </div>
                </div>

                <div className="mt-12 flex-1">
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
                                                <button 
                                                    onClick={() => handleSelectVersion(selectedApp, ver)}
                                                    className="font-mono font-bold text-emerald-400 hover:text-emerald-300 underline underline-offset-4 transition-colors cursor-pointer"
                                                >
                                                    v{ver.version}
                                                </button>
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
                                                onClick={() => handleDownload(selectedApp, ver.apk_url)}
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
        <div className="h-full p-4 md:p-8 overflow-hidden">
            <div className="glass-panel h-full flex flex-col p-6 md:p-10 relative overflow-hidden">
                {/* Decorative background glow inside the panel */}
                <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] bg-emerald-500/10 rounded-full blur-[80px] pointer-events-none" />
                <div className="absolute bottom-[-20%] right-[-10%] w-[40%] h-[40%] bg-blue-500/10 rounded-full blur-[80px] pointer-events-none" />

                <div className="flex items-center space-x-4 mb-10 relative z-10">
                    <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-emerald-400 to-teal-600 flex items-center justify-center shadow-lg border border-white/20">
                        <span className="material-symbols-outlined text-white text-3xl">shop</span>
                    </div>
                    <div>
                        <h1 className="text-4xl font-black text-white tracking-tight drop-shadow-md">Tienda de Aplicaciones</h1>
                        <p className="text-gray-300 font-medium">Descarga e instala las herramientas oficiales en tus dispositivos.</p>
                    </div>
                </div>

                {apps.length === 0 ? (
                    <div className="flex-1 flex flex-col items-center justify-center text-center relative z-10">
                        <span className="material-symbols-outlined text-8xl text-gray-500/50 mb-4 drop-shadow-lg">cloud_off</span>
                        <h2 className="text-3xl font-bold text-gray-300 mb-2">No hay aplicaciones disponibles</h2>
                        <p className="text-gray-400 max-w-md text-lg">Utiliza la CLI (Opción 5) para subir archivos APK a la tienda de tu servidor.</p>
                    </div>
                ) : (
                    <div className="flex-1 overflow-y-auto pr-2 relative z-10 custom-scrollbar">
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 pb-10">
                            <AnimatePresence>
                                {apps.map((app, i) => (
                                    <motion.div
                                        key={app.id}
                                        initial={{ opacity: 0, y: 20, scale: 0.95 }}
                                        animate={{ opacity: 1, y: 0, scale: 1 }}
                                        transition={{ delay: i * 0.05, type: "spring", stiffness: 300, damping: 25 }}
                                        onClick={() => handleSelectApp(app)}
                                        className="relative p-6 rounded-[2rem] cursor-pointer transition-all duration-300 hover:-translate-y-2 hover:shadow-2xl border border-white/10 flex flex-col items-center text-center group bg-white/5 backdrop-blur-md overflow-hidden"
                                    >
                                        {/* Subtle hover gradient */}
                                        <div className="absolute inset-0 bg-gradient-to-br from-white/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                                        
                                        <img 
                                            src={`${apiUrl}${app.icon_url}`} 
                                            alt={app.name} 
                                            className="w-28 h-28 rounded-3xl mb-5 shadow-xl object-cover bg-black/20 group-hover:scale-105 transition-transform duration-500 border border-white/10 z-10 relative"
                                            onError={(e) => { e.currentTarget.src = 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="128" height="128" viewBox="0 0 24 24"><path fill="%23fff" d="M17.523 15.3414c-.5511 0-.9993-.4486-.9993-.9997s.4483-.9993.9993-.9993c.5511 0 .9993.4482.9993.9993.0001.5511-.4482.9997-.9993.9997zm-11.046 0c-.5511 0-.9993-.4486-.9993-.9997s.4482-.9993.9993-.9993c.5511 0 .9993.4482.9993.9993 0 .5511-.4482.9997-.9993.9997zm11.4045-6.02l1.9973-3.4592a.416.416 0 00-.1517-.5677.416.416 0 00-.5677.1517l-2.0315 3.5173c-1.4243-.65-3.0456-1.0263-4.7876-1.0263-1.7416 0-3.3633.3763-4.7872 1.0263l-2.0315-3.5173a.416.416 0 00-.5677-.1517.416.416 0 00-.1517.5677l1.9973 3.4592C4.3821 10.5902 2.5937 13.1118 2 16.1906h20c-.5937-3.0788-2.3821-5.6004-4.1185-6.8692z"/></svg>'; }} 
                                        />
                                        <h3 className="text-2xl font-bold text-white mb-2 z-10 relative drop-shadow-md">{app.name}</h3>
                                        <span className="bg-emerald-500/20 text-emerald-300 text-xs px-3 py-1 rounded-full font-mono font-bold mb-4 z-10 relative border border-emerald-500/30 shadow-[0_0_10px_rgba(16,185,129,0.2)]">
                                            v{app.latest_version}
                                        </span>
                                        
                                        <div className="flex items-center space-x-4 mb-2 z-10 relative">
                                            <div className="flex items-center space-x-1 text-emerald-400 text-sm font-bold">
                                                <span className="material-symbols-outlined text-[16px]">download</span>
                                                <span>{app.downloads}</span>
                                            </div>
                                            <button 
                                                onClick={(e) => handleLike(app, e)}
                                                className={`flex items-center space-x-1 transition-colors text-sm font-bold ${app.liked_by_me ? 'text-pink-500 hover:text-pink-400' : 'text-pink-400/50 hover:text-pink-400'}`}
                                            >
                                                <span className={`material-symbols-outlined text-[16px] ${app.liked_by_me ? 'fill-current' : ''}`} style={app.liked_by_me ? { fontVariationSettings: "'FILL' 1" } : {}}>favorite</span>
                                                <span>{app.likes}</span>
                                            </button>
                                        </div>
                                        <p className="text-sm text-gray-300 line-clamp-2 z-10 relative font-medium">
                                            {app.description || "Haz clic para ver detalles y versiones."}
                                        </p>
                                    </motion.div>
                                ))}
                            </AnimatePresence>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
