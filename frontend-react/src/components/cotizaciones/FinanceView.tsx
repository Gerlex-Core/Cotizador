export default function FinanceView() {
    return (
        <div className="flex h-full gap-4">
            <div className="w-1/2 glass-panel rounded-3xl p-6 flex flex-col space-y-6">
                <div className="flex items-center space-x-2 border-b border-[var(--border-default)] pb-3">
                    <span className="material-symbols-outlined text-2xl text-[var(--text-primary)]">account_balance_wallet</span>
                    <h2 className="text-lg font-bold text-[var(--text-primary)]">Resumen Financiero</h2>
                </div>
                
                <div className="space-y-4">
                    <div className="flex justify-between items-center bg-white/5 p-4 rounded-xl border border-[var(--border-default)]">
                        <span className="font-bold">Subtotal:</span>
                        <span className="font-mono text-lg">0.00 Bs</span>
                    </div>
                    <div className="flex justify-between items-center bg-white/5 p-4 rounded-xl border border-[var(--border-default)] text-red-400">
                        <span className="font-bold flex items-center space-x-2">
                            <input type="checkbox" className="w-4 h-4 rounded" /> 
                            <span>Descuento (%)</span>
                        </span>
                        <input type="number" defaultValue="0" className="glass-input w-20 p-1 text-right rounded-lg font-mono text-red-400" />
                    </div>
                    <div className="flex justify-between items-center bg-white/5 p-4 rounded-xl border border-[var(--border-default)] text-emerald-400">
                        <span className="font-bold flex items-center space-x-2">
                            <input type="checkbox" className="w-4 h-4 rounded" /> 
                            <span>Impuestos (%)</span>
                        </span>
                        <input type="number" defaultValue="0" className="glass-input w-20 p-1 text-right rounded-lg font-mono text-emerald-400" />
                    </div>
                    
                    <div className="flex justify-between items-center p-4 rounded-xl border-2 border-[var(--text-primary)] bg-[var(--text-primary)] text-[var(--bg-primary)] shadow-lg">
                        <span className="font-black text-xl uppercase tracking-wider">Total a Pagar:</span>
                        <span className="font-black font-mono text-2xl">0.00 Bs</span>
                    </div>
                </div>
            </div>

            <div className="w-1/2 glass-panel rounded-3xl p-6 flex flex-col space-y-6">
                <div className="flex items-center space-x-2 border-b border-[var(--border-default)] pb-3">
                    <span className="material-symbols-outlined text-2xl text-[var(--text-primary)]">payments</span>
                    <h2 className="text-lg font-bold text-[var(--text-primary)]">Control de Pagos y Saldo</h2>
                </div>

                <div className="space-y-4 flex-1">
                    <div className="space-y-1">
                        <label className="text-xs font-bold text-[var(--text-secondary)]">A Cuenta (Bs):</label>
                        <input type="number" defaultValue="0" className="glass-input w-full p-3 rounded-xl font-mono font-bold text-lg" />
                    </div>
                    
                    <div className="mt-8 p-6 rounded-2xl bg-red-500/10 border border-red-500/30 flex flex-col items-center justify-center space-y-2">
                        <span className="text-sm font-bold text-red-400 uppercase tracking-widest">Saldo Restante</span>
                        <span className="font-black font-mono text-4xl text-red-400">0.00 Bs</span>
                    </div>
                </div>
            </div>
        </div>
    );
}
