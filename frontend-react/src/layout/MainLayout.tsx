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

export default function MainLayout() {
    const { activeTab } = useNavigation();

    const renderContent = () => {
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
            
            default: return null;
        }
    };

    return (
        <div className="flex flex-col h-screen w-full theme-bg overflow-hidden relative">
            {/* Animated Background Blobs for Liquid Effect (Only visible if theme allows it) */}
            <div className="absolute top-[-10%] left-[-10%] w-[40vw] h-[40vw] bg-purple-500/20 rounded-full mix-blend-screen filter blur-[100px] opacity-70 animate-[pulse_8s_ease-in-out_infinite]" />
            <div className="absolute bottom-[-10%] right-[-5%] w-[35vw] h-[35vw] bg-blue-500/20 rounded-full mix-blend-screen filter blur-[100px] opacity-70 animate-[pulse_10s_ease-in-out_infinite_reverse]" />
            <div className="absolute top-[20%] right-[15%] w-[25vw] h-[25vw] bg-pink-500/20 rounded-full mix-blend-screen filter blur-[80px] opacity-50 animate-[pulse_12s_ease-in-out_infinite]" />

            {/* Background Overlay for better contrast on glass theme */}
            <div className="absolute inset-0 theme-bg-overlay z-0 pointer-events-none transition-colors duration-500"></div>

            {/* Top Menu Strip */}
            <MenuStrip />
            
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
