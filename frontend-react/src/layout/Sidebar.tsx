import { motion } from 'framer-motion';

type SidebarProps = {
    activeTab: number;
    setActiveTab: (tab: number) => void;
};

export default function Sidebar({ activeTab, setActiveTab }: SidebarProps) {
    const mainTabs = [
        { id: 0, icon: 'receipt_long', label: 'Productos & Servicios' },
        { id: 1, icon: 'storefront', label: 'Catálogo & Combos' },
        { id: 2, icon: 'palette', label: 'Diseñador Portada' },
        { id: 3, icon: 'travel_explore', label: 'Importador Digicorp' },
        { id: 4, icon: 'account_balance_wallet', label: 'Finanzas & Saldo' },
        { id: 5, icon: 'gavel', label: 'Términos & Garantía' },
        { id: 8, icon: 'picture_as_pdf', label: 'Edición PDF' },
    ];

    const sysTabs = [
        { id: 6, icon: 'history', label: 'Historial de Cotizaciones' },
        { id: 7, icon: 'settings', label: 'Configuraciones' },
    ];

    const TabButton = ({ id, icon, label }: { id: number, icon: string, label: string }) => {
        const isActive = activeTab === id;
        
        return (
            <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => setActiveTab(id)}
                className={`w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-2xl text-xs font-semibold transition-all duration-300 relative ${isActive ? 'text-[var(--bg-primary)]' : 'text-[var(--text-secondary)] hover:bg-[var(--bg-secondary)] hover:text-white'}`}
            >
                {isActive && (
                    <motion.div 
                        layoutId="activeTabBackground"
                        className="absolute inset-0 bg-[var(--text-primary)] rounded-2xl shadow-lg z-0"
                        initial={false}
                        transition={{ type: "spring", stiffness: 300, damping: 30 }}
                    />
                )}
                <span className="material-symbols-outlined text-xl z-10">{icon}</span>
                <span className="z-10">{label}</span>
            </motion.button>
        );
    };

    return (
        <aside className="w-64 bg-[var(--bg-sidebar)] border-r border-[var(--border-default)] flex flex-col justify-between p-3 shrink-0 select-none z-20 h-full overflow-y-auto">
            <div className="space-y-4">
                {/* Brand */}
                <div className="flex items-center space-x-3 px-3 py-2 cursor-pointer group">
                    <motion.div 
                        whileHover={{ rotate: 180 }}
                        transition={{ duration: 0.4 }}
                        className="w-10 h-10 rounded-2xl bg-[var(--text-primary)] text-[var(--bg-primary)] flex items-center justify-center font-bold shadow-md"
                    >
                        <span className="material-symbols-outlined text-xl">description</span>
                    </motion.div>
                    <div>
                        <h1 className="text-sm font-extrabold text-[var(--text-primary)] tracking-wide group-hover:text-[var(--accent-hover)] transition-colors">Cotizador Pro</h1>
                        <span className="text-[11px] font-medium text-[var(--text-secondary)]">React Premium Engine</span>
                    </div>
                </div>

                <div className="h-px bg-[var(--border-default)] mx-2"></div>

                {/* Main section */}
                <div className="space-y-1">
                    <div className="px-3.5 py-2 text-[10px] font-extrabold uppercase tracking-wider text-[var(--text-secondary)] flex items-center space-x-1.5 opacity-80">
                        <span className="material-symbols-outlined text-sm">edit_document</span>
                        <span>DOCUMENTO ACTIVO</span>
                    </div>

                    {mainTabs.map(tab => (
                        <TabButton key={tab.id} id={tab.id} icon={tab.icon} label={tab.label} />
                    ))}
                </div>

                <div className="h-px bg-[var(--border-default)] mx-2"></div>

                {/* System section */}
                <div className="space-y-1">
                    <div className="px-3.5 py-2 text-[10px] font-extrabold uppercase tracking-wider text-[var(--text-secondary)] flex items-center space-x-1.5 opacity-80">
                        <span className="material-symbols-outlined text-sm">folder_open</span>
                        <span>HISTORIAL & SISTEMA</span>
                    </div>

                    {sysTabs.map(tab => (
                        <TabButton key={tab.id} id={tab.id} icon={tab.icon} label={tab.label} />
                    ))}
                </div>
            </div>
        </aside>
    );
}
