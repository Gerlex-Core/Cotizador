import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import '@fontsource/roboto/300.css';
import '@fontsource/roboto/400.css';
import '@fontsource/roboto/500.css';
import '@fontsource/roboto/700.css';
import './index.css'
import App from './App.tsx'
import { ThemeProvider } from './context/ThemeContext.tsx'
import { NavigationProvider } from './context/NavigationContext.tsx'
import { QuotationProvider } from './context/QuotationContext.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ThemeProvider>
      <NavigationProvider>
        <QuotationProvider>
          <App />
        </QuotationProvider>
      </NavigationProvider>
    </ThemeProvider>
  </StrictMode>,
)
