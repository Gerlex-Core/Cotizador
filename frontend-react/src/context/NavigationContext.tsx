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
            return 9; // StoreView is tab 9
        }
        return 0;
    });

    // Optionally sync URL back to root if they leave the store
    const handleTabChange = (tab: number) => {
        setActiveTab(tab);
        if (tab !== 9 && window.location.pathname.includes('/store')) {
            window.history.pushState({}, "", "/");
        } else if (tab === 9 && !window.location.pathname.includes('/store')) {
            window.history.pushState({}, "", "/store");
        }
    };

    return (
        <NavigationContext.Provider value={{ activeTab, setActiveTab }}>
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
