import { createContext, useContext, useState } from 'react';
import type { ReactNode } from 'react';

interface NavigationContextType {
    activeTab: number;
    setActiveTab: (tab: number) => void;
}

const NavigationContext = createContext<NavigationContextType | undefined>(undefined);

export function NavigationProvider({ children }: { children: ReactNode }) {
    const [activeTab, setActiveTab] = useState(() => {
        const path = window.location.pathname;
        if (path.startsWith('/store')) {
            return 9; // StoreView
        }
        if (path.startsWith('/Cotizador')) {
            return 0; // QuotationView
        }
        if (path === '/' || path === '') {
            return 10; // LandingView
        }
        return 0; // Default to Cotizador
    });

    const handleTabChange = (tab: number) => {
        setActiveTab(tab);
        const path = window.location.pathname;
        if (tab === 9 && !path.startsWith('/store')) {
            window.history.pushState({}, "", "/store");
        } else if (tab === 10 && path !== '/') {
            window.history.pushState({}, "", "/");
        } else if (tab >= 0 && tab <= 8 && !path.startsWith('/Cotizador')) {
            window.history.pushState({}, "", "/Cotizador");
        }
    };

    return (
        <NavigationContext.Provider value={{ activeTab, setActiveTab: handleTabChange }}>
            {children}
        </NavigationContext.Provider>
    );
}

export function useNavigation() {
    const context = useContext(NavigationContext);
    if (context === undefined) {
        throw new Error('useNavigation must be used within a NavigationProvider');
    }
    return context;
}
