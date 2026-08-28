import { createContext, useContext, useState, useEffect } from 'react';
import type { ReactNode } from 'react';
import { ThemeProvider as MuiThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { muiMaterialNeoTheme, muiGlassTheme } from '../theme/muiTheme';

type Theme = 'glass-ios' | 'material-neo';

interface ThemeContextType {
    theme: Theme;
    setTheme: (theme: Theme) => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export function ThemeProvider({ children }: { children: ReactNode }) {
    const [theme, setTheme] = useState<Theme>(() => {
        const savedTheme = localStorage.getItem('app-theme') as Theme;
        return savedTheme || 'glass-ios';
    });

    useEffect(() => {
        localStorage.setItem('app-theme', theme);
        const root = document.documentElement;
        
        root.classList.remove('theme-glass-ios', 'theme-material-neo');
        root.classList.add(`theme-${theme}`);
    }, [theme]);

    const activeMuiTheme = theme === 'glass-ios' ? muiGlassTheme : muiMaterialNeoTheme;

    return (
        <ThemeContext.Provider value={{ theme, setTheme }}>
            <MuiThemeProvider theme={activeMuiTheme}>
                <CssBaseline />
                {children}
            </MuiThemeProvider>
        </ThemeContext.Provider>
    );
}

export function useTheme() {
    const context = useContext(ThemeContext);
    if (context === undefined) {
        throw new Error('useTheme must be used within a ThemeProvider');
    }
    return context;
}
