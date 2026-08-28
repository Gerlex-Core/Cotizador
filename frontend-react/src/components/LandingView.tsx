import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigation } from '../context/NavigationContext';

const ICONS = ['rocket', 'star', 'favorite', 'diamond', 'bolt', 'eco'];

type Card = {
    id: number;
    icon: string;
    isFlipped: boolean;
    isMatched: boolean;
};

export default function LandingView() {
    const { setActiveTab } = useNavigation();
    
    const [cards, setCards] = useState<Card[]>([]);
    const [flippedIndices, setFlippedIndices] = useState<number[]>([]);
    const [moves, setMoves] = useState(0);
    const [isWon, setIsWon] = useState(false);

    const initializeGame = () => {
        const shuffled = [...ICONS, ...ICONS]
            .sort(() => Math.random() - 0.5)
            .map((icon, idx) => ({
                id: idx,
                icon,
                isFlipped: false,
                isMatched: false
            }));
        setCards(shuffled);
        setFlippedIndices([]);
        setMoves(0);
        setIsWon(false);
    };

    useEffect(() => {
        initializeGame();
    }, []);

    const handleCardClick = (index: number) => {
        if (flippedIndices.length === 2 || cards[index].isFlipped || cards[index].isMatched) return;

        const newFlipped = [...flippedIndices, index];
        setFlippedIndices(newFlipped);
        
        const newCards = [...cards];
        newCards[index].isFlipped = true;
        setCards(newCards);

        if (newFlipped.length === 2) {
            setMoves(m => m + 1);
            const [first, second] = newFlipped;
            if (newCards[first].icon === newCards[second].icon) {
                newCards[first].isMatched = true;
                newCards[second].isMatched = true;
                setCards(newCards);
                setFlippedIndices([]);
                
                if (newCards.every(c => c.isMatched)) {
                    setIsWon(true);
                }
            } else {
                setTimeout(() => {
                    const resetCards = [...cards];
                    resetCards[first].isFlipped = false;
                    resetCards[second].isFlipped = false;
                    setCards(resetCards);
                    setFlippedIndices([]);
                }, 1000);
            }
        }
    };

    return (
        <div className="h-full flex flex-col md:flex-row items-center justify-center p-4 md:p-8 gap-8 overflow-y-auto custom-scrollbar">
            {/* Main Navigation Panel */}
            <motion.div 
                initial={{ opacity: 0, x: -20, scale: 0.95 }}
                animate={{ opacity: 1, x: 0, scale: 1 }}
                className="glass-panel p-10 md:p-12 rounded-[3rem] text-center max-w-2xl w-full border border-white/10 shadow-2xl relative overflow-hidden flex-1"
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

            {/* Mini Game Panel */}
            <motion.div 
                initial={{ opacity: 0, x: 20, scale: 0.95 }}
                animate={{ opacity: 1, x: 0, scale: 1 }}
                transition={{ delay: 0.2 }}
                className="glass-panel p-8 rounded-[3rem] max-w-md w-full border border-white/10 shadow-2xl relative overflow-hidden flex flex-col items-center justify-center"
            >
                <div className="text-center mb-6 z-10 relative">
                    <h3 className="text-2xl font-black text-white flex items-center justify-center space-x-2">
                        <span className="material-symbols-outlined text-pink-400">sports_esports</span>
                        <span>Memory Match</span>
                    </h3>
                    <div className="flex justify-between items-center mt-2 px-4 text-sm font-bold text-gray-300">
                        <span>Movimientos: <span className="text-[var(--accent-primary)]">{moves}</span></span>
                        <button onClick={initializeGame} className="text-emerald-400 hover:text-emerald-300 transition-colors flex items-center space-x-1">
                            <span className="material-symbols-outlined text-sm">refresh</span>
                            <span>Reiniciar</span>
                        </button>
                    </div>
                </div>

                <div className="grid grid-cols-4 gap-3 z-10 relative w-full">
                    <AnimatePresence>
                        {cards.map((card, idx) => (
                            <motion.div
                                key={card.id}
                                layout
                                onClick={() => handleCardClick(idx)}
                                className={`aspect-square rounded-xl cursor-pointer relative w-full h-16 sm:h-20 flex items-center justify-center transition-transform duration-300 [perspective:1000px] [transform-style:preserve-3d] ${card.isFlipped || card.isMatched ? '[transform:rotateY(180deg)] bg-white/20 shadow-[0_0_15px_rgba(255,255,255,0.1)] border border-white/30' : 'bg-white/5 hover:bg-white/10 border border-white/5 hover:scale-105'}`}
                            >
                                {(card.isFlipped || card.isMatched) ? (
                                    <span 
                                        className="material-symbols-outlined text-3xl sm:text-4xl"
                                        style={{ color: card.isMatched ? '#34d399' : 'white', transform: 'rotateY(180deg)' }}
                                    >
                                        {card.icon}
                                    </span>
                                ) : (
                                    <span className="material-symbols-outlined text-gray-500/50 text-2xl">help</span>
                                )}
                            </motion.div>
                        ))}
                    </AnimatePresence>
                </div>

                <AnimatePresence>
                    {isWon && (
                        <motion.div 
                            initial={{ opacity: 0, scale: 0.5 }}
                            animate={{ opacity: 1, scale: 1 }}
                            exit={{ opacity: 0, scale: 0.5 }}
                            className="absolute inset-0 bg-black/60 backdrop-blur-sm z-20 flex flex-col items-center justify-center rounded-[3rem]"
                        >
                            <span className="material-symbols-outlined text-6xl text-emerald-400 mb-4 animate-bounce">trophy</span>
                            <h2 className="text-3xl font-black text-white mb-2">¡Ganaste!</h2>
                            <p className="text-gray-300 font-bold mb-6">En {moves} movimientos</p>
                            <button 
                                onClick={initializeGame}
                                className="bg-[var(--accent-primary)] text-[var(--bg-primary)] px-6 py-3 rounded-2xl font-bold shadow-lg hover:scale-105 transition-transform"
                            >
                                Jugar de Nuevo
                            </button>
                        </motion.div>
                    )}
                </AnimatePresence>
            </motion.div>
        </div>
    );
}
