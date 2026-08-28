import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { apiFetch } from '../../utils/apiClient';
import { API_BASE_URL } from '../../config/apiConfig';

type User = {
    id: number;
    username: string;
    role: string;
    created_at: string;
};

type StoreApp = {
    id: string;
    name: string;
    description: string;
};

export default function AdminDashboardView() {
    const [users, setUsers] = useState<User[]>([]);
    const [apps, setApps] = useState<StoreApp[]>([]);
    const [loading, setLoading] = useState(true);
    
    // Edit App State
    const [editingApp, setEditingApp] = useState<StoreApp | null>(null);
    const [editName, setEditName] = useState('');
    const [editDescription, setEditDescription] = useState('');

    useEffect(() => {
        const fetchData = async () => {
            try {
                const [usersRes, appsRes] = await Promise.all([
                    apiFetch(`${API_BASE_URL}/api/admin/users`),
                    fetch(`${API_BASE_URL}/api/store/apps`)
                ]);
                
                if (usersRes.ok) {
                    const data = await usersRes.json();
                    setUsers(data);
                }
                
                if (appsRes.ok) {
                    const data = await appsRes.json();
                    setApps(data.apps || []);
                }
            } catch (err) {
                console.error("Error fetching admin data", err);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, []);

    const handleEditApp = (app: StoreApp) => {
        setEditingApp(app);
        setEditName(app.name);
        setEditDescription(app.description);
    };

    const handleSaveApp = async () => {
        if (!editingApp) return;
        try {
            const res = await apiFetch(`${API_BASE_URL}/api/admin/store-apps/${editingApp.id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: editName, description: editDescription })
            });
            if (res.ok) {
                setApps(prev => prev.map(a => a.id === editingApp.id ? { ...a, name: editName, description: editDescription } : a));
                setEditingApp(null);
            }
        } catch (err) {
            console.error("Error saving app", err);
        }
    };

    if (loading) {
        return (
            <div className="flex h-full items-center justify-center">
                <span className="material-symbols-outlined animate-spin text-6xl text-[var(--accent-primary)]">progress_activity</span>
            </div>
        );
    }

    return (
        <div className="h-full flex flex-col space-y-8 overflow-y-auto pr-2 custom-scrollbar">
            {/* Users Section */}
            <div className="glass-panel p-6 rounded-3xl">
                <h2 className="text-2xl font-black text-white mb-6 flex items-center space-x-2">
                    <span className="material-symbols-outlined text-[var(--accent-primary)]">group</span>
                    <span>Usuarios Registrados</span>
                </h2>
                
                <div className="overflow-x-auto rounded-xl border border-white/10">
                    <table className="w-full text-left border-collapse bg-white/5">
                        <thead>
                            <tr className="border-b border-white/10 text-gray-300">
                                <th className="p-4 font-semibold">ID</th>
                                <th className="p-4 font-semibold">Usuario</th>
                                <th className="p-4 font-semibold">Rol</th>
                                <th className="p-4 font-semibold">Fecha de Creación</th>
                            </tr>
                        </thead>
                        <tbody>
                            {users.map(u => (
                                <tr key={u.id} className="border-b border-white/5 hover:bg-white/5 transition-colors text-gray-200">
                                    <td className="p-4">{u.id}</td>
                                    <td className="p-4 font-bold text-white">{u.username}</td>
                                    <td className="p-4">
                                        <span className={`px-2 py-1 rounded-full text-xs font-bold ${u.role === 'master' ? 'bg-red-500/20 text-red-400' : 'bg-blue-500/20 text-blue-400'}`}>
                                            {u.role.toUpperCase()}
                                        </span>
                                    </td>
                                    <td className="p-4 text-sm text-gray-400">{new Date(u.created_at).toLocaleString()}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Store Apps Section */}
            <div className="glass-panel p-6 rounded-3xl flex-1 mb-8">
                <h2 className="text-2xl font-black text-white mb-6 flex items-center space-x-2">
                    <span className="material-symbols-outlined text-[var(--accent-primary)]">shop</span>
                    <span>Administrar Tienda</span>
                </h2>
                
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {apps.map(app => (
                        <div key={app.id} className="bg-white/5 border border-white/10 p-6 rounded-2xl flex flex-col justify-between">
                            <div>
                                <h3 className="text-xl font-bold text-white mb-2">{app.name}</h3>
                                <p className="text-gray-400 text-sm mb-4 line-clamp-3">{app.description}</p>
                            </div>
                            <button 
                                onClick={() => handleEditApp(app)}
                                className="self-end bg-[var(--accent-primary)]/20 hover:bg-[var(--accent-primary)]/30 text-[var(--accent-primary)] font-bold py-2 px-4 rounded-xl transition-colors flex items-center space-x-2"
                            >
                                <span className="material-symbols-outlined text-sm">edit</span>
                                <span>Editar</span>
                            </button>
                        </div>
                    ))}
                </div>
            </div>

            {/* Edit App Modal */}
            <AnimatePresence>
                {editingApp && (
                    <motion.div 
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm"
                    >
                        <motion.div 
                            initial={{ scale: 0.95, opacity: 0 }}
                            animate={{ scale: 1, opacity: 1 }}
                            exit={{ scale: 0.95, opacity: 0 }}
                            className="glass-panel w-full max-w-lg p-8 rounded-3xl shadow-2xl relative"
                        >
                            <button 
                                onClick={() => setEditingApp(null)}
                                className="absolute top-6 right-6 text-gray-400 hover:text-white transition-colors"
                            >
                                <span className="material-symbols-outlined">close</span>
                            </button>
                            
                            <h2 className="text-2xl font-black text-white mb-6">Editar {editingApp.name}</h2>
                            
                            <div className="space-y-4">
                                <div>
                                    <label className="block text-sm font-bold text-gray-400 mb-2">Nombre de la Aplicación</label>
                                    <input 
                                        type="text"
                                        value={editName}
                                        onChange={e => setEditName(e.target.value)}
                                        className="w-full bg-white/5 border border-white/10 rounded-xl p-4 text-white placeholder-gray-500 focus:border-[var(--accent-primary)] focus:ring-1 focus:ring-[var(--accent-primary)] outline-none transition-all"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-bold text-gray-400 mb-2">Descripción</label>
                                    <textarea 
                                        value={editDescription}
                                        onChange={e => setEditDescription(e.target.value)}
                                        rows={4}
                                        className="w-full bg-white/5 border border-white/10 rounded-xl p-4 text-white placeholder-gray-500 focus:border-[var(--accent-primary)] focus:ring-1 focus:ring-[var(--accent-primary)] outline-none transition-all custom-scrollbar"
                                    />
                                </div>
                            </div>
                            
                            <div className="mt-8 flex justify-end space-x-4">
                                <button 
                                    onClick={() => setEditingApp(null)}
                                    className="px-6 py-3 rounded-xl font-bold text-gray-400 hover:text-white hover:bg-white/5 transition-colors"
                                >
                                    Cancelar
                                </button>
                                <button 
                                    onClick={handleSaveApp}
                                    className="px-6 py-3 rounded-xl font-bold bg-[var(--accent-primary)] text-[var(--bg-primary)] shadow-lg hover:shadow-[var(--accent-primary)]/30 hover:scale-105 active:scale-95 transition-all flex items-center space-x-2"
                                >
                                    <span className="material-symbols-outlined text-sm">save</span>
                                    <span>Guardar</span>
                                </button>
                            </div>
                        </motion.div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}
