import * as DropdownMenu from '@radix-ui/react-dropdown-menu';
import { cn } from '../utils/cn';
import { useNavigation } from '../context/NavigationContext';
import { motion } from 'framer-motion';

export default function MenuStrip() {
    const { activeTab, setActiveTab } = useNavigation();

    const menuGroups = [
        {
            id: 'archivo',
            label: 'Archivo',
            items: [
                { id: 0, icon: 'receipt_long', label: 'Cotización Actual', type: 'item' },
                { id: 6, icon: 'history', label: 'Historial', type: 'item' },
                { id: 'save', icon: 'save', label: 'Guardar (.cotz)', type: 'action' },
                { id: 'sep1', type: 'separator' },
                { id: 8, icon: 'picture_as_pdf', label: 'Exportar PDF', type: 'item' }
            ]
        },
        {
            id: 'edicion',
            label: 'Edición',
            items: [
                { id: 2, icon: 'palette', label: 'Diseño Portada', type: 'item' },
                { id: 4, icon: 'account_balance_wallet', label: 'Finanzas & Saldo', type: 'item' },
                { id: 5, icon: 'gavel', label: 'Términos & Garantía', type: 'item' }
            ]
        },
        {
            id: 'herramientas',
            label: 'Herramientas',
            items: [
                { id: 1, icon: 'storefront', label: 'Catálogo Local', type: 'item' },
                { id: 3, icon: 'travel_explore', label: 'Buscar Digicorp', type: 'item' },
            ]
        },
        {
            id: 'sistema',
            label: 'Sistema',
            items: [
                { id: 7, icon: 'settings', label: 'Configuraciones', type: 'item' }
            ]
        }
    ];

    const MenuTrigger = ({ label }: { label: string }) => (
        <DropdownMenu.Trigger asChild>
            <button className="px-4 py-1.5 rounded-lg text-sm font-semibold text-[var(--text-primary)] hover:bg-white/10 transition-colors focus:outline-none focus:bg-white/10">
                {label}
            </button>
        </DropdownMenu.Trigger>
    );

    const MenuContent = ({ items }: { items: any[] }) => (
        <DropdownMenu.Portal>
            <DropdownMenu.Content 
                sideOffset={5}
                align="start"
                className="z-50 min-w-[220px] glass-panel rounded-xl p-1 shadow-2xl animate-in fade-in zoom-in-95 duration-200"
            >
                {items.map((item, idx) => {
                    if (item.type === 'separator') {
                        return <DropdownMenu.Separator key={`sep-${idx}`} className="h-[1px] bg-[var(--border-default)] m-1" />;
                    }

                    return (
                        <DropdownMenu.Item 
                            key={item.id}
                            onSelect={() => {
                                if (item.type === 'item') setActiveTab(item.id as number);
                                if (item.type === 'action' && item.id === 'save') alert('Guardando...');
                            }}
                            className={cn(
                                "flex items-center space-x-3 px-3 py-2.5 rounded-lg text-sm cursor-pointer outline-none transition-colors select-none text-[var(--text-primary)]",
                                "focus:bg-white/20 focus:shadow-[inset_0_1px_1px_rgba(255,255,255,0.5)] focus:text-[var(--text-primary)]",
                                activeTab === item.id ? "bg-white/15 shadow-[inset_0_1px_1px_rgba(255,255,255,0.3)]" : "hover:bg-white/10"
                            )}
                        >
                            <span className="material-symbols-outlined text-lg">{item.icon}</span>
                            <span className="font-medium">{item.label}</span>
                        </DropdownMenu.Item>
                    );
                })}
            </DropdownMenu.Content>
        </DropdownMenu.Portal>
    );

    return (
        <motion.div 
            initial={{ y: -50, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ type: "spring", stiffness: 300, damping: 25 }}
            className="flex items-center justify-between px-2 md:px-4 py-1.5 glass-panel border-b border-[var(--border-default)] select-none shrink-0 relative z-50"
        >
            <div className="flex items-center overflow-x-auto no-scrollbar max-w-full">
                {/* Logo/Brand Mini */}
                <div className="flex items-center space-x-2 mr-4 cursor-default shrink-0">
                    <div className="w-6 h-6 rounded-md bg-[var(--accent-primary)] text-white flex items-center justify-center shadow-[0_0_10px_var(--accent-primary)]">
                        <span className="material-symbols-outlined text-sm font-bold">description</span>
                    </div>
                    <span className="font-black tracking-wider text-sm text-[var(--text-primary)] drop-shadow-md">COTIZADOR</span>
                </div>

                {/* Dropdown Menus */}
                <div className="flex items-center space-x-1">
                    {menuGroups.map(group => (
                        <DropdownMenu.Root key={group.id}>
                            <MenuTrigger label={group.label} />
                            <MenuContent items={group.items} />
                        </DropdownMenu.Root>
                    ))}
                </div>
            </div>
            
            {/* Quick Actions / Clock placeholder */}
            <div className="flex items-center space-x-3">
                <span className="text-xs font-bold text-[var(--text-secondary)] tracking-widest">{new Date().toLocaleDateString()}</span>
            </div>
        </motion.div>
    );
}
