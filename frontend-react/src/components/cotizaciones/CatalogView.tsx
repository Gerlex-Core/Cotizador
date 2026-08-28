import { useState } from 'react';
import { motion } from 'framer-motion';

export default function CatalogView() {
    const [search, setSearch] = useState('');
    const [category, setCategory] = useState('Todas');
    const [products] = useState<any[]>([]);

    const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
        setSearch(e.target.value);
    };

    return (
        <div className="flex h-full gap-4">
            {/* Sidebar / Filters */}
            <div className="w-1/4 glass-panel rounded-3xl p-6 flex flex-col space-y-4">
                <div className="flex items-center space-x-2 border-b border-[var(--border-default)] pb-3">
                    <span className="material-symbols-outlined text-2xl text-[var(--text-primary)]">category</span>
                    <h2 className="text-lg font-bold text-[var(--text-primary)]">Categorías</h2>
                </div>
                
                <div className="flex flex-col space-y-2 flex-1 overflow-y-auto pr-2">
                    {['Todas', 'Cámaras', 'Grabadores', 'Accesorios', 'Redes', 'Combos'].map(cat => (
                        <motion.button
                            key={cat}
                            whileHover={{ x: 4 }}
                            onClick={() => setCategory(cat)}
                            className={`w-full text-left px-4 py-2.5 rounded-2xl transition-all font-semibold text-sm ${category === cat ? 'bg-[var(--text-primary)] text-[var(--bg-primary)] shadow-md' : 'glass-button'}`}
                        >
                            {cat}
                        </motion.button>
                    ))}
                </div>
            </div>

            {/* Catalog Grid */}
            <div className="flex-1 glass-panel rounded-3xl p-6 flex flex-col space-y-4">
                {/* Search Header */}
                <div className="flex items-center justify-between border-b border-[var(--border-default)] pb-4">
                    <div className="relative w-1/2">
                        <span className="material-symbols-outlined absolute left-3 top-2.5 text-[var(--text-secondary)]">search</span>
                        <input 
                            type="text" 
                            value={search}
                            onChange={handleSearch}
                            placeholder="Buscar productos en el catálogo local..." 
                            className="glass-input w-full pl-10 p-2.5 rounded-2xl font-semibold"
                        />
                    </div>
                    
                    <motion.button 
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        className="px-5 py-2 bg-[var(--text-primary)] text-[var(--bg-primary)] rounded-full font-bold shadow-lg flex items-center space-x-2"
                    >
                        <span className="material-symbols-outlined text-sm">sync</span>
                        <span>Sincronizar DB</span>
                    </motion.button>
                </div>

                {/* Grid */}
                <div className="flex-1 overflow-y-auto">
                    {products.length === 0 ? (
                        <div className="h-full flex flex-col items-center justify-center text-[var(--text-secondary)] space-y-4">
                            <span className="material-symbols-outlined text-6xl opacity-30">inventory_2</span>
                            <p className="font-semibold">No hay productos en esta categoría.</p>
                            <button className="glass-button px-4 py-2 rounded-xl text-sm font-bold">Cargar Catálogo</button>
                        </div>
                    ) : (
                        <div className="grid grid-cols-3 gap-4">
                            {/* Product cards will be mapped here */}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
