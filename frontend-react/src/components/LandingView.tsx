import { motion } from 'framer-motion';
import { useNavigation } from '../context/NavigationContext';

export default function LandingView() {
    const { setActiveTab } = useNavigation();

    return (
        <div className="h-full flex items-center justify-center p-4 md:p-8">
            <motion.div 
                initial={{ opacity: 0, y: 20, scale: 0.95 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                className="glass-panel p-10 md:p-16 rounded-[3rem] text-center max-w-3xl w-full border border-white/10 shadow-2xl relative overflow-hidden"
            >
                <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] bg-[var(--accent-primary)]/20 rounded-full blur-[80px] pointer-events-none" />
                <div className="absolute bottom-[-20%] right-[-10%] w-[40%] h-[40%] bg-emerald-500/20 rounded-full blur-[80px] pointer-events-none" />

                <div className="relative z-10">
                    <div className="w-24 h-24 rounded-3xl bg-gradient-to-br from-[var(--accent-primary)] to-purple-600 mx-auto flex items-center justify-center shadow-xl mb-8">
                        <span className="material-symbols-outlined text-5xl text-white">grid_view</span>
                    </div>
                    
                    <h1 className="text-5xl md:text-6xl font-black text-white tracking-tight mb-4 drop-shadow-md">
                        Bienvenido al Sistema
                    </h1>
                    <p className="text-xl text-gray-300 font-medium mb-12 max-w-xl mx-auto">
                        Selecciona el módulo al que deseas ingresar.
                    </p>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <button 
                            onClick={() => {
                                setActiveTab(0);
                                window.history.pushState({}, "", "/Cotizador");
                            }}
                            className="group glass-button p-8 rounded-3xl flex flex-col items-center hover:bg-white/10 transition-all hover:-translate-y-2 hover:shadow-xl border border-white/5"
                        >
                            <span className="material-symbols-outlined text-6xl text-[var(--accent-primary)] mb-4 group-hover:scale-110 transition-transform">request_quote</span>
                            <span className="text-2xl font-bold text-white mb-2">Cotizador Pro</span>
                            <span className="text-gray-400 text-sm font-medium">Crear y gestionar cotizaciones, clientes y finanzas.</span>
                        </button>

                        <button 
                            onClick={() => {
                                setActiveTab(9);
                                window.history.pushState({}, "", "/store");
                            }}
                            className="group glass-button p-8 rounded-3xl flex flex-col items-center hover:bg-white/10 transition-all hover:-translate-y-2 hover:shadow-xl border border-white/5"
                        >
                            <span className="material-symbols-outlined text-6xl text-emerald-400 mb-4 group-hover:scale-110 transition-transform">shop</span>
                            <span className="text-2xl font-bold text-white mb-2">App Store</span>
                            <span className="text-gray-400 text-sm font-medium">Descargar actualizaciones y herramientas oficiales.</span>
                        </button>
                    </div>
                </div>
            </motion.div>
        </div>
    );
}
