import { motion, AnimatePresence } from 'framer-motion';
import { useNavigation } from '../context/NavigationContext';
import MenuStrip from './MenuStrip';
import Header from './Header';
import HistoryView from '../components/historial/HistoryView';
import SettingsHub from '../components/settings/SettingsHub';
import QuotationView from '../components/cotizaciones/QuotationView';
import CatalogView from '../components/cotizaciones/CatalogView';
import DesignerView from '../components/cotizaciones/DesignerView';
import DigicorpView from '../components/cotizaciones/DigicorpView';
import FinanceView from '../components/cotizaciones/FinanceView';
import TermsView from '../components/cotizaciones/TermsView';
import PDFEditorView from '../components/cotizaciones/PDFEditorView';
import StoreView from '../components/store/StoreView';
import LandingView from '../components/LandingView';
import LoginView from '../components/auth/LoginView';
import { useState, useEffect } from 'react';
import { useTheme } from '../context/ThemeContext';
import { useAuth } from '../context/AuthContext';

const WALLPAPERS = [
    'https://images.unsplash.com/photo-1493515322954-4fa727e97985?fm=jpg&q=60&w=3000&auto=format&fit=crop',
    'https://images.unsplash.com/photo-1542051842-87b468437d36?fm=jpg&q=80&w=3000&auto=format&fit=crop', // Tokyo neon
    'https://images.unsplash.com/photo-1513407030348-c9d4a3b76c8c?fm=jpg&q=80&w=3000&auto=format&fit=crop', // Dark city
    'https://images.unsplash.com/photo-1502602898657-3e91760cbb34?fm=jpg&q=80&w=3000&auto=format&fit=crop', // Paris night
    'https://images.unsplash.com/photo-1518684079-3c830dcef090?fm=jpg&q=80&w=3000&auto=format&fit=crop' // Dubai night
];

export default function MainLayout() {
    const { activeTab } = useNavigation();
    const { theme } = useTheme();
    const { isAuthenticated } = useAuth();
    const [currentBg, setCurrentBg] = useState(0);

    useEffect(() => {
        const interval = setInterval(() => {
            setCurrentBg((prev) => (prev + 1) % WALLPAPERS.length);
        }, 60000); // Change every 60 seconds
        return () => clearInterval(interval);
    }, []);

    const renderContent = () => {
        if (!isAuthenticated && ![9, 10].includes(activeTab)) {
            return <LoginView onSuccess={() => {}} />;
        }
        
        switch (activeTab) {
            case 0: return <QuotationView />;
            case 1: return <CatalogView />;
            case 2: return <DesignerView />;
            case 3: return <DigicorpView />;
            case 4: return <FinanceView />;
            case 5: return <TermsView />;
            case 8: return <PDFEditorView />;
            
            // System Tabs
            case 6: return <HistoryView />;
            case 7: return <SettingsHub />;
            case 9: return <StoreView />;
            case 10: return <LandingView />;
            
            default: return null;
        }
    };

    return (
        <div className="flex flex-col h-screen w-full theme-bg overflow-hidden relative">
            {/* Dynamic Background Slideshow */}
            {theme === 'glass-ios' && WALLPAPERS.map((url, index) => (
                <div
                    key={url}
                    className="absolute inset-0 z-0 bg-cover bg-center bg-no-repeat transition-opacity duration-[2000ms] ease-in-out"
                    style={{ 
                        backgroundImage: `url('${url}')`,
                        opacity: index === currentBg ? 1 : 0
                    }}
                />
            ))}

            {/* Animated Background Blobs for Liquid Effect (Only visible if theme allows it) */}
            <div className="absolute top-[-10%] left-[-10%] w-[40vw] h-[40vw] bg-purple-500/20 rounded-full mix-blend-screen filter blur-[100px] opacity-70 animate-[pulse_8s_ease-in-out_infinite] z-0" />
            <div className="absolute bottom-[-10%] right-[-5%] w-[35vw] h-[35vw] bg-blue-500/20 rounded-full mix-blend-screen filter blur-[100px] opacity-70 animate-[pulse_10s_ease-in-out_infinite_reverse] z-0" />
            <div className="absolute top-[20%] right-[15%] w-[25vw] h-[25vw] bg-pink-500/20 rounded-full mix-blend-screen filter blur-[80px] opacity-50 animate-[pulse_12s_ease-in-out_infinite] z-0" />

            {/* Background Overlay for better contrast on glass theme */}
            <div className="absolute inset-0 theme-bg-overlay z-0 pointer-events-none transition-colors duration-500"></div>

            {/* Top Menu Strip */}
            {activeTab !== 9 && activeTab !== 10 && <MenuStrip />}
            
            {/* Main Application Area */}
            <main className="flex-1 flex flex-col h-full overflow-hidden p-2 md:p-6 space-y-2 md:space-y-4 relative z-10">
                {/* Header is only shown if we are in QuotationView (0), Designer(2), Finance(4), Terms(5), PDF(8) */}
                {[0, 2, 4, 5, 8].includes(activeTab) && (
                    <motion.div
                        initial={{ opacity: 0, y: -20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -20 }}
                    >
                        <Header />
                    </motion.div>
                )}
                
                {/* Content Workspace */}
                <div className="flex-1 overflow-hidden relative">
                    <AnimatePresence mode="wait">
                        <motion.div
                            key={activeTab}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -20 }}
                            transition={{ duration: 0.3, type: "spring", bounce: 0.2 }}
                            className="absolute inset-0 overflow-y-auto"
                        >
                            {renderContent()}
                        </motion.div>
                    </AnimatePresence>
                </div>
            </main>
        </div>
    );
}
