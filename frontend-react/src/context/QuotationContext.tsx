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
    generatePDF: () => Promise<void>;
    exportCotzFile: () => void;
}

const QuotationContext = createContext<QuotationContextType | undefined>(undefined);

export function QuotationProvider({ children }: { children: ReactNode }) {
    const [client, setClient] = useState<ClientData>({ name: '', contact: '', address: '' });
    const [products, setProducts] = useState<ProductItem[]>([]);
    const [subtotal, setSubtotal] = useState(0);
    const [ivaAmount, setIvaAmount] = useState(0);
    const [total, setTotal] = useState(0);

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
                show_exchange_rate: true,
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
                include_summary: true,
                include_details: true,
                include_bank_details: true,
                include_installation: true,
                include_warranty: true,
                include_signature: true,
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

    return (
        <QuotationContext.Provider value={{
            client, setClient,
            products, setProducts, addProduct, removeProduct, updateProduct, clearProducts,
            subtotal, ivaAmount, total,
            generatePDF, exportCotzFile
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
