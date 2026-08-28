import { createContext, useContext, useState } from 'react';
import type { ReactNode } from 'react';

interface NavigationContextType {
    activeTab: number;
    setActiveTab: (tab: number) => void;
}

const NavigationContext = createContext<NavigationContextType | undefined>(undefined);

export function NavigationProvider({ children }: { children: ReactNode }) {
    const [activeTab, setActiveTab] = useState(0);

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
