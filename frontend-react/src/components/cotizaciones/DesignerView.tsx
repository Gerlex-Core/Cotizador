export default function DesignerView() {
    return (
        <div className="flex h-full gap-4">
            <div className="w-1/4 glass-panel rounded-3xl p-6 flex flex-col space-y-4">
                <div className="flex items-center space-x-2 border-b border-[var(--border-default)] pb-3">
                    <span className="material-symbols-outlined text-2xl text-[var(--text-primary)]">style</span>
                    <h2 className="text-lg font-bold text-[var(--text-primary)]">Estilos & Portada</h2>
                </div>
                <div className="text-sm text-[var(--text-secondary)]">
                    Configuración de colores y plantillas para la portada de la cotización.
                </div>
                
                <div className="space-y-4">
                    <div className="space-y-2">
                        <label className="text-xs font-bold">Color Principal</label>
                        <div className="flex gap-2">
                            {['#1E3A8A', '#065F46', '#7F1D1D', '#4C1D95'].map(color => (
                                <button key={color} className="w-8 h-8 rounded-full border-2 border-white/20 hover:scale-110 transition-transform" style={{ backgroundColor: color }} />
                            ))}
                        </div>
                    </div>
                </div>
            </div>

            <div className="flex-1 glass-panel rounded-3xl p-6 flex items-center justify-center">
                <div className="text-center space-y-4 text-[var(--text-secondary)]">
                    <span className="material-symbols-outlined text-6xl opacity-30">drag_indicator</span>
                    <h3 className="text-xl font-bold">Lienzo de Diseño</h3>
                    <p>Arrastra elementos aquí para armar la portada personalizada.</p>
                </div>
            </div>
        </div>
    );
}
