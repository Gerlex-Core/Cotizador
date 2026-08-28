import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import CompanyView from './CompanyView';
import GeneralConfigView from './GeneralConfigView';
import { useTheme } from '../../context/ThemeContext';
import { useAuth } from '../../context/AuthContext';
import { cn } from '../../utils/cn';
import AdminDashboardView from './AdminDashboardView';

export default function SettingsHub() {
    const [activeTab, setActiveTab] = useState<'empresas' | 'general' | 'apariencia' | 'admin'>('apariencia');
    const { theme, setTheme } = useTheme();
    const { user } = useAuth();
    const isAdmin = user?.role === 'master' || user?.role === 'admin';

    return (
        <div className="space-y-6 p-6 h-full flex flex-col">
            {/* Settings Navigation */}
            <div className="flex justify-center">
                <div className="glass-panel p-1.5 rounded-full inline-flex space-x-1">
                    <button 
                        onClick={() => setActiveTab('empresas')}
                        className={cn(
                            "px-6 py-2 rounded-full text-sm font-bold transition-all",
                            activeTab === 'empresas' ? "bg-[var(--accent-primary)] text-[var(--bg-primary)] shadow-md" : "text-[var(--text-secondary)] hover:text-white"
                        )}
                    >
                        Empresas
                    </button>
                    <button 
                        onClick={() => setActiveTab('general')}
                        className={cn(
                            "px-6 py-2 rounded-full text-sm font-bold transition-all",
                            activeTab === 'general' ? "bg-[var(--accent-primary)] text-[var(--bg-primary)] shadow-md" : "text-[var(--text-secondary)] hover:text-white"
                        )}
                    >
                        Configuración General
                    </button>
                    <button 
                        onClick={() => setActiveTab('apariencia')}
                        className={cn(
                            "px-6 py-2 rounded-full text-sm font-bold transition-all",
                            activeTab === 'apariencia' ? "bg-[var(--accent-primary)] text-[var(--bg-primary)] shadow-md" : "text-[var(--text-secondary)] hover:text-white"
                        )}
                    >
                        Apariencia
                    </button>
                    {isAdmin && (
                        <button 
                            onClick={() => setActiveTab('admin')}
                            className={cn(
                                "px-6 py-2 rounded-full text-sm font-bold transition-all",
                                activeTab === 'admin' ? "bg-red-500 text-white shadow-md" : "text-[var(--text-secondary)] hover:text-white"
                            )}
                        >
                            Admin Dashboard
                        </button>
                    )}
                </div>
            </div>

            {/* Content Area */}
            <div className="flex-1 overflow-hidden relative">
                <AnimatePresence mode="wait">
                    {activeTab === 'empresas' && (
                        <motion.div
                            key="empresas"
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -20 }}
                            transition={{ type: "spring", stiffness: 300, damping: 25 }}
                            className="absolute inset-0"
                        >
                            <CompanyView />
                        </motion.div>
                    )}
                    {activeTab === 'general' && (
                        <motion.div
                            key="general"
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -20 }}
                            transition={{ type: "spring", stiffness: 300, damping: 25 }}
                            className="absolute inset-0"
                        >
                            <GeneralConfigView />
                        </motion.div>
                    )}
                    {activeTab === 'apariencia' && (
                        <motion.div
                            key="apariencia"
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -20 }}
                            transition={{ type: "spring", stiffness: 300, damping: 25 }}
                            className="absolute inset-0 flex flex-col items-center pt-10"
                        >
                            <div className="glass-panel p-10 rounded-3xl max-w-2xl w-full space-y-8">
                                <div className="text-center space-y-2">
                                    <span className="material-symbols-outlined text-6xl text-[var(--accent-primary)]">palette</span>
                                    <h2 className="text-2xl font-black">Estilo Visual</h2>
                                    <p className="text-[var(--text-secondary)]">Elige el tema que mejor se adapte a tu entorno.</p>
                                </div>
                                
                                <div className="grid grid-cols-2 gap-6">
                                    <div 
                                        onClick={() => setTheme('glass-ios')}
                                        className={cn(
                                            "cursor-pointer rounded-2xl p-6 border-2 transition-all flex flex-col items-center space-y-4",
                                            theme === 'glass-ios' ? "border-[var(--accent-primary)] bg-[var(--accent-primary)]/10 shadow-[0_0_30px_rgba(10,132,255,0.3)]" : "border-[var(--border-default)] hover:border-[var(--border-highlight)]"
                                        )}
                                    >
                                        <div className="w-24 h-24 rounded-full bg-gradient-to-tr from-blue-500 to-purple-500 flex items-center justify-center shadow-lg">
                                            <span className="material-symbols-outlined text-white text-4xl">blur_on</span>
                                        </div>
                                        <div className="text-center">
                                            <h3 className="font-bold text-lg">Liquid Glass OS</h3>
                                            <p className="text-xs text-[var(--text-secondary)] mt-1">Desenfoque profundo, vibrante, inspirado en iOS.</p>
                                        </div>
                                    </div>

                                    <div 
                                        onClick={() => setTheme('material-neo')}
                                        className={cn(
                                            "cursor-pointer rounded-2xl p-6 border-2 transition-all flex flex-col items-center space-y-4",
                                            theme === 'material-neo' ? "border-[var(--accent-primary)] bg-[var(--accent-primary)]/10 shadow-[0_0_30px_rgba(208,188,255,0.2)]" : "border-[var(--border-default)] hover:border-[var(--border-highlight)]"
                                        )}
                                    >
                                        <div className="w-24 h-24 rounded-full bg-[#2B2930] flex items-center justify-center border border-[#49454F] shadow-md">
                                            <span className="material-symbols-outlined text-[#D0BCFF] text-4xl">layers</span>
                                        </div>
                                        <div className="text-center">
                                            <h3 className="font-bold text-lg">Material Neo</h3>
                                            <p className="text-xs text-[var(--text-secondary)] mt-1">Colores sólidos, bordes definidos, estilo MD3.</p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </motion.div>
                    )}
                    {isAdmin && activeTab === 'admin' && (
                        <motion.div
                            key="admin"
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -20 }}
                            transition={{ type: "spring", stiffness: 300, damping: 25 }}
                            className="absolute inset-0"
                        >
                            <AdminDashboardView />
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>
        </div>
    );
}
