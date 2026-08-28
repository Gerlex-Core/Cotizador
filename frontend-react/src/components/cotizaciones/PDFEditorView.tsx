import { motion } from 'framer-motion';

export default function PDFEditorView() {
    return (
        <div className="flex h-full gap-4">
            <div className="w-1/4 glass-panel rounded-3xl p-6 flex flex-col space-y-4">
                <div className="flex items-center space-x-2 border-b border-[var(--border-default)] pb-3">
                    <span className="material-symbols-outlined text-2xl text-[var(--text-primary)]">picture_as_pdf</span>
                    <h2 className="text-lg font-bold text-[var(--text-primary)]">Exportar PDF</h2>
                </div>
                
                <div className="flex flex-col space-y-4">
                    <motion.button 
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        className="px-6 py-4 bg-gradient-to-r from-red-500 to-red-600 text-white rounded-2xl font-black shadow-lg flex items-center justify-center space-x-2 w-full text-lg"
                    >
                        <span className="material-symbols-outlined text-2xl">download</span>
                        <span>GENERAR PDF</span>
                    </motion.button>

                    <div className="space-y-2 mt-4">
                        <label className="flex items-center space-x-3 cursor-pointer p-3 bg-white/5 rounded-xl">
                            <input type="checkbox" className="w-5 h-5 rounded text-red-500" defaultChecked />
                            <span className="font-semibold text-sm">Incluir Imágenes</span>
                        </label>
                        <label className="flex items-center space-x-3 cursor-pointer p-3 bg-white/5 rounded-xl">
                            <input type="checkbox" className="w-5 h-5 rounded text-red-500" defaultChecked />
                            <span className="font-semibold text-sm">Incluir Portada</span>
                        </label>
                        <label className="flex items-center space-x-3 cursor-pointer p-3 bg-white/5 rounded-xl">
                            <input type="checkbox" className="w-5 h-5 rounded text-red-500" />
                            <span className="font-semibold text-sm">Ocultar Precios Unitarios</span>
                        </label>
                    </div>
                </div>
            </div>

            <div className="flex-1 glass-panel rounded-3xl p-2 bg-black/40 flex items-center justify-center relative overflow-hidden">
                <div className="absolute inset-0 flex flex-col items-center justify-center text-[var(--text-secondary)] opacity-50 z-0">
                    <span className="material-symbols-outlined text-8xl">preview</span>
                    <h3 className="text-2xl font-bold mt-4">Vista Previa</h3>
                    <p>El PDF generado se mostrará aquí.</p>
                </div>
            </div>
        </div>
    );
}
