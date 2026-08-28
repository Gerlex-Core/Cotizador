import { motion } from 'framer-motion';

export default function DigicorpView() {
    return (
        <div className="glass-panel rounded-3xl p-6 h-full flex flex-col space-y-4">
            <div className="flex items-center space-x-2 border-b border-[var(--border-default)] pb-3">
                <span className="material-symbols-outlined text-2xl text-[var(--text-primary)]">travel_explore</span>
                <h2 className="text-lg font-bold text-[var(--text-primary)]">Importador API Digicorp</h2>
            </div>
            
            <div className="flex items-center space-x-4">
                <input 
                    type="text" 
                    placeholder="Código de producto (ej: HFW1200T)" 
                    className="glass-input flex-1 p-3 rounded-xl font-semibold"
                />
                <motion.button 
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className="px-6 py-3 bg-[var(--text-primary)] text-[var(--bg-primary)] rounded-xl font-bold shadow-lg flex items-center space-x-2"
                >
                    <span className="material-symbols-outlined text-base">search</span>
                    <span>Buscar en Digicorp</span>
                </motion.button>
            </div>

            <div className="flex-1 flex flex-col items-center justify-center text-[var(--text-secondary)] space-y-4 border-2 border-dashed border-[var(--border-default)] rounded-3xl mt-4">
                <span className="material-symbols-outlined text-6xl opacity-30">satellite_alt</span>
                <p>Ingresa un código para consultar disponibilidad, precio y características.</p>
            </div>
        </div>
    );
}
