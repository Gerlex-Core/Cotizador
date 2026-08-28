import { motion } from 'framer-motion';

export default function Header() {
    return (
        <header className="glass-panel rounded-3xl px-4 py-3 flex flex-col md:flex-row items-center justify-between gap-4 shrink-0 shadow-sm relative z-20">
            {/* Document Parameters */}
            <div className="flex flex-wrap justify-center md:justify-start gap-4 text-sm w-full md:w-auto">
                <div className="flex items-center space-x-2">
                    <span className="material-symbols-outlined text-xl text-[var(--text-secondary)]">file_present</span>
                    <label className="text-[var(--text-secondary)] font-medium">Tipo:</label>
                    <select className="glass-input rounded-xl px-3 py-1.5 font-bold cursor-pointer transition-colors hover:bg-white/10 w-full sm:w-auto">
                        <option value="Cotizacion">Cotización</option>
                        <option value="Recibo">Recibo</option>
                    </select>
                </div>

                <div className="flex items-center space-x-2">
                    <label className="text-[var(--text-secondary)] font-medium">N° Documento:</label>
                    <div className="flex items-center space-x-1">
                        <input type="text" className="glass-input rounded-xl px-3 py-1.5 font-mono font-bold w-40" defaultValue="COT-20260828-001" />
                        <motion.button 
                            whileHover={{ rotate: 90 }}
                            whileTap={{ scale: 0.9 }}
                            title="Regenerar Código" 
                            className="p-1.5 glass-button rounded-xl transition"
                        >
                            <span className="material-symbols-outlined text-lg">autorenew</span>
                        </motion.button>
                    </div>
                </div>

                <div className="flex items-center space-x-2">
                    <label className="text-[var(--text-secondary)] font-medium">Fecha:</label>
                    <input type="text" className="glass-input rounded-xl px-3 py-1.5 font-bold w-28 text-center" defaultValue="28/08/2026" />
                </div>

                <div className="flex items-center space-x-2">
                    <label className="text-[var(--text-secondary)] font-medium">Validez:</label>
                    <div className="relative">
                        <input type="number" defaultValue="15" min="1" max="365" className="glass-input rounded-xl pl-3 pr-8 py-1.5 font-bold w-24 text-center" />
                        <span className="absolute right-3 top-1.5 text-[var(--text-secondary)] pointer-events-none">d</span>
                    </div>
                </div>
            </div>
            
            <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-2 text-[var(--text-secondary)] text-xs font-semibold">
                    <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                    <span className="hidden md:inline">Guardado Automático</span>
                </div>
            </div>
        </header>
    );
}
