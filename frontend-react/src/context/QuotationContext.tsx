import { createContext, useContext, useState, useEffect } from 'react';
import type { ReactNode } from 'react';

export interface ProductItem {
    id: string; // Used for React keys
    description: string;
    quantity: number;
    unit: string;
    price: number;
    brand: string;
    sku: string;
    discount_percent: number;
    item_warranty: string;
}

export interface ClientData {
    name: string;
    contact: string;
    address: string;
}

export interface PdfOptions {
    showExchangeRate: boolean;
    showVolatilityWarning: boolean;
    includeSummary: boolean;
    includeBankDetails: boolean;
    includeInstallation: boolean;
    includeWarranty: boolean;
    includeSignature: boolean;
}

interface QuotationContextType {
    client: ClientData;
    setClient: (client: ClientData) => void;
    products: ProductItem[];
    setProducts: (products: ProductItem[]) => void;
    addProduct: () => void;
    removeProduct: (id: string) => void;
    updateProduct: (id: string, field: keyof ProductItem, value: any) => void;
    clearProducts: () => void;
    subtotal: number;
    ivaAmount: number;
    total: number;
    pdfOptions: PdfOptions;
    setPdfOption: (key: keyof PdfOptions, value: boolean) => void;
    generatePDF: () => Promise<void>;
    exportCotzFile: () => void;
    saveToCloud: () => Promise<void>;
}

const QuotationContext = createContext<QuotationContextType | undefined>(undefined);

export function QuotationProvider({ children }: { children: ReactNode }) {
    const [client, setClient] = useState<ClientData>({ name: '', contact: '', address: '' });
    const [products, setProducts] = useState<ProductItem[]>([]);
    const [subtotal, setSubtotal] = useState(0);
    const [ivaAmount, setIvaAmount] = useState(0);
    const [total, setTotal] = useState(0);
    
    const [pdfOptions, setPdfOptions] = useState<PdfOptions>({
        showExchangeRate: true,
        showVolatilityWarning: true,
        includeSummary: true,
        includeBankDetails: true,
        includeInstallation: true,
        includeWarranty: true,
        includeSignature: true
    });

    const setPdfOption = (key: keyof PdfOptions, value: boolean) => {
        setPdfOptions(prev => ({ ...prev, [key]: value }));
    };

    const applyIva = true;
    const ivaPercent = 13.0;

    // Recalculate totals whenever products change
    useEffect(() => {
        let calcSubtotal = 0;
        products.forEach(p => {
            const rawAmount = (p.quantity || 0) * (p.price || 0);
            const discAmount = rawAmount * ((p.discount_percent || 0) / 100);
            calcSubtotal += (rawAmount - discAmount);
        });

        const calcIva = applyIva ? calcSubtotal * (ivaPercent / 100) : 0;
        
        setSubtotal(calcSubtotal);
        setIvaAmount(calcIva);
        setTotal(calcSubtotal + calcIva);
    }, [products, applyIva, ivaPercent]);

    const addProduct = () => {
        setProducts(prev => [
            ...prev,
            {
                id: Math.random().toString(36).substring(7),
                description: '',
                quantity: 1,
                unit: 'unidad (u)',
                price: 0,
                brand: '',
                sku: '',
                discount_percent: 0,
                item_warranty: ''
            }
        ]);
    };

    const removeProduct = (id: string) => {
        setProducts(prev => prev.filter(p => p.id !== id));
    };

    const updateProduct = (id: string, field: keyof ProductItem, value: any) => {
        setProducts(prev => prev.map(p => {
            if (p.id === id) {
                return { ...p, [field]: value };
            }
            return p;
        }));
    };

    const clearProducts = () => setProducts([]);

    const generatePDF = async () => {
        if (products.length === 0) {
            alert('Por favor agregue al menos un producto a la cotización.');
            return;
        }
        
        try {
            const payload = {
                document_type: "Cotización",
                quotation_number: "COT-REACT-001",
                company_name: "Empresa Demo", // Default fallback
                date: new Date().toLocaleDateString(),
                currency: "Bolivianos (Bs)",
                exchange_rate: 12.02,
                show_exchange_rate: pdfOptions.showExchangeRate,
                show_volatility_warning: pdfOptions.showVolatilityWarning,
                client: client,
                products: products,
                apply_discount: false,
                discount_percent: 0,
                apply_iva: applyIva,
                iva_percent: ivaPercent,
                enable_shipping: false,
                shipping: 0,
                apply_payment: false,
                paid_amount: 0,
                include_summary: pdfOptions.includeSummary,
                include_details: true,
                include_bank_details: pdfOptions.includeBankDetails,
                include_installation: pdfOptions.includeInstallation,
                include_warranty: pdfOptions.includeWarranty,
                include_signature: pdfOptions.includeSignature,
                cover_page_enabled: false
            };

            const { API_BASE_URL } = await import('../config/apiConfig');
            const response = await fetch(`${API_BASE_URL}/api/quotations/pdf`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                const errData = await response.json().catch(() => ({}));
                alert(`Error al generar PDF: ${errData.detail || response.statusText}`);
                return;
            }

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${payload.quotation_number}.pdf`;
            document.body.appendChild(a);
            a.click();
            a.remove();
        } catch (error) {
            console.error('Error generating PDF:', error);
            alert('Error de conexión al generar el PDF.');
        }
    };

    const exportCotzFile = () => {
        const payload = {
            client,
            products,
            subtotal,
            ivaAmount,
            total,
            pdfOptions,
            version: '2.0-offline',
            date: new Date().toISOString()
        };
        const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `Cotizacion_${client.name.replace(/\s+/g, '_') || 'Offline'}.cotz`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    };

    const saveToCloud = async () => {
        if (products.length === 0) {
            alert('Por favor agregue al menos un producto a la cotización.');
            return;
        }

        const payload = {
            document_type: "Cotización",
            quotation_number: `COT-REACT-${Math.floor(Math.random() * 1000)}`,
            company_name: "Empresa Demo",
            date: new Date().toLocaleDateString(),
            currency: "Bolivianos (Bs)",
            exchange_rate: 12.02,
            show_exchange_rate: pdfOptions.showExchangeRate,
            show_volatility_warning: pdfOptions.showVolatilityWarning,
            client: client,
            products: products,
            apply_discount: false,
            discount_percent: 0,
            apply_iva: applyIva,
            iva_percent: ivaPercent,
            enable_shipping: false,
            shipping: 0,
            apply_payment: false,
            paid_amount: 0,
            include_summary: pdfOptions.includeSummary,
            include_details: true,
            include_bank_details: pdfOptions.includeBankDetails,
            include_installation: pdfOptions.includeInstallation,
            include_warranty: pdfOptions.includeWarranty,
            include_signature: pdfOptions.includeSignature,
            cover_page_enabled: false
        };

        try {
            const { API_BASE_URL } = await import('../config/apiConfig');
            const response = await fetch(`${API_BASE_URL}/api/quotations/save`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                const errData = await response.json().catch(() => ({}));
                alert(`Error al guardar en nube: ${errData.detail || response.statusText}`);
                return;
            }

            alert('¡Cotización guardada exitosamente en la base de datos web!');
        } catch (error) {
            console.error('Error saving to cloud:', error);
            alert('Error de conexión al guardar en la nube.');
        }
    };

    return (
        <QuotationContext.Provider value={{
            client, setClient,
            products, setProducts, addProduct, removeProduct, updateProduct, clearProducts,
            subtotal, ivaAmount, total,
            pdfOptions, setPdfOption,
            generatePDF, exportCotzFile, saveToCloud
        }}>
            {children}
        </QuotationContext.Provider>
    );
}

export function useQuotation() {
    const context = useContext(QuotationContext);
    if (context === undefined) {
        throw new Error('useQuotation must be used within a QuotationProvider');
    }
    return context;
}
