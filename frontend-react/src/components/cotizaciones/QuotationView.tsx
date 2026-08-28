import { ThemePanel } from '../ui/ThemePanel';

import PersonIcon from '@mui/icons-material/Person';
import TuneIcon from '@mui/icons-material/Tune';
import ListAltIcon from '@mui/icons-material/ListAlt';
import AddCircleOutlinedIcon from '@mui/icons-material/AddCircleOutlined';
import AttachMoneyIcon from '@mui/icons-material/AttachMoney';
import AddShoppingCartIcon from '@mui/icons-material/AddShoppingCart';
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf';
import DeleteIcon from '@mui/icons-material/Delete';
import StorefrontIcon from '@mui/icons-material/Storefront';
import { useTheme } from '../../context/ThemeContext';
import { useQuotation } from '../../context/QuotationContext';
import { useNavigation } from '../../context/NavigationContext';

export default function QuotationView() {
    const { theme } = useTheme();
    const { setActiveTab } = useNavigation();
    const { 
        client, setClient, 
        products, addProduct, removeProduct, updateProduct, clearProducts,
        subtotal, ivaAmount, total,
        generatePDF, exportCotzFile
    } = useQuotation();

    const handleClientChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setClient({ ...client, [e.target.name]: e.target.value });
    };

    return (
        <div className="flex flex-col md:flex-row h-full gap-4 md:gap-6 w-full p-1 md:p-2 overflow-y-auto md:overflow-hidden">
            {/* Left Column: Client Data & Actions */}
            <div className="w-full md:w-1/4 flex flex-col space-y-4 md:space-y-6 overflow-y-visible md:overflow-y-auto pr-0 md:pr-2 shrink-0">
                
                <ThemePanel delay={0} className="flex flex-col space-y-4 shrink-0">
                    <div className="flex items-center space-x-2 border-b border-[var(--border-default)] pb-3">
                        <PersonIcon sx={{ color: 'var(--text-primary)' }} />
                        <h2 className="text-lg font-bold text-[var(--text-primary)]">Datos del Cliente</h2>
                    </div>

                    <div className="space-y-4 pt-2">
                        <div className="flex flex-col space-y-1">
                            <label className="text-xs font-bold text-[var(--text-secondary)] ml-2">Señores:</label>
                            <input 
                                className="glass-input"
                                name="name"
                                value={client.name}
                                onChange={handleClientChange}
                                placeholder="Nombre del cliente o empresa"
                            />
                        </div>
                        <div className="flex flex-col space-y-1">
                            <label className="text-xs font-bold text-[var(--text-secondary)] ml-2">Atención:</label>
                            <input 
                                className="glass-input"
                                name="contact"
                                value={client.contact}
                                onChange={handleClientChange}
                                placeholder="Contacto directo"
                            />
                        </div>
                        <div className="flex flex-col space-y-1">
                            <label className="text-xs font-bold text-[var(--text-secondary)] ml-2">Dirección:</label>
                            <input 
                                className="glass-input"
                                name="address"
                                value={client.address}
                                onChange={handleClientChange}
                                placeholder="Ubicación"
                            />
                        </div>
                    </div>
                </ThemePanel>

                <ThemePanel delay={0.1} className="flex flex-col shrink-0">
                    <div className="flex items-center justify-between border-b border-[var(--border-default)] pb-3 mb-4">
                        <div className="flex items-center space-x-2">
                            <TuneIcon sx={{ color: 'var(--text-primary)' }} />
                            <h2 className="text-lg font-bold text-[var(--text-primary)]">Controles</h2>
                        </div>
                    </div>

                    <div className="grid grid-cols-2 gap-3 mt-2">
                        <button 
                            className={theme === 'material-neo' ? "bg-[var(--accent-primary)] text-[var(--bg-primary)] p-3 rounded-lg font-bold flex flex-col items-center gap-1 shadow-md hover:opacity-90" : "glass-button p-3 flex flex-col items-center gap-1 font-bold"}
                            onClick={addProduct}
                        >
                            <AddCircleOutlinedIcon />
                            <span className="text-sm text-center">Añadir Fila</span>
                        </button>
                        <button 
                            className={theme === 'material-neo' ? "bg-[var(--bg-secondary)] text-[var(--text-primary)] border border-[var(--border-default)] p-3 rounded-lg font-bold flex flex-col items-center gap-1 hover:bg-[var(--border-default)]" : "glass-button p-3 flex flex-col items-center gap-1 font-bold"}
                            onClick={() => setActiveTab(1)}
                        >
                            <StorefrontIcon />
                            <span className="text-sm text-center">Catálogo</span>
                        </button>
                        <button 
                            className={theme === 'material-neo' ? "bg-[var(--bg-secondary)] text-[var(--text-primary)] border border-[var(--border-default)] p-3 rounded-lg font-bold flex flex-col items-center gap-1 hover:bg-[var(--border-default)]" : "glass-button p-3 flex flex-col items-center gap-1 font-bold text-blue-400"}
                            onClick={exportCotzFile}
                        >
                            <ListAltIcon />
                            <span className="text-sm text-center">Guardar Local</span>
                        </button>
                        <button 
                            className={theme === 'material-neo' ? "bg-red-500/20 text-red-400 border border-red-500/30 p-3 rounded-lg font-bold flex flex-col items-center gap-1 hover:bg-red-500/30" : "glass-button p-3 flex flex-col items-center gap-1 font-bold !text-red-400"}
                            onClick={() => { if(confirm('¿Borrar productos?')) clearProducts(); }}
                        >
                            <DeleteIcon />
                            <span className="text-sm text-center">Limpiar Todo</span>
                        </button>
                        <button 
                            className={theme === 'material-neo' ? "bg-green-500/20 text-green-400 border border-green-500/30 p-3 rounded-lg font-bold flex flex-col items-center gap-1 hover:bg-green-500/30" : "glass-button p-3 flex flex-col items-center gap-1 font-bold !text-green-400"}
                            onClick={generatePDF}
                        >
                            <PictureAsPdfIcon />
                            <span className="text-sm">PDF</span>
                        </button>
                    </div>
                </ThemePanel>
                
                {/* Totals Summary */}
                <ThemePanel delay={0.2} className="flex flex-col space-y-2 shrink-0">
                    <div className="flex items-center justify-between border-b border-[var(--border-default)] pb-2 mb-2">
                        <div className="flex items-center space-x-2">
                            <AttachMoneyIcon sx={{ color: 'var(--text-primary)' }} />
                            <h2 className="text-lg font-bold text-[var(--text-primary)]">Totales</h2>
                        </div>
                    </div>
                    <div className="flex justify-between text-sm text-[var(--text-secondary)]">
                        <span>Subtotal:</span>
                        <span>Bs {subtotal.toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between text-sm text-[var(--text-secondary)]">
                        <span>IVA (13%):</span>
                        <span>Bs {ivaAmount.toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between text-xl font-black text-[var(--text-primary)] border-t border-[var(--border-default)] pt-2 mt-2">
                        <span>TOTAL:</span>
                        <span>Bs {total.toFixed(2)}</span>
                    </div>
                </ThemePanel>

                {/* Scroll spacer to prevent bottom panel cutoff */}
                <div className="h-10 shrink-0 w-full" />
            </div>

            {/* Right Column: Products Table */}
            <div className="flex-1 flex flex-col overflow-hidden min-h-[500px] md:min-h-0">
                <ThemePanel delay={0.1} className="h-full flex flex-col space-y-4">
                    <div className="flex items-center justify-between border-b border-[var(--border-default)] pb-4">
                        <div className="flex items-center space-x-2">
                            <ListAltIcon fontSize="large" sx={{ color: 'var(--text-primary)' }} />
                            <h2 className="text-xl font-black text-[var(--text-primary)] tracking-wide">Lista de Ítems</h2>
                        </div>
                        
                        <div className="text-sm font-bold bg-[var(--bg-secondary)] px-4 py-2 rounded-xl text-[var(--text-secondary)]">
                            {products.length} ítems en cotización
                        </div>
                    </div>

                    <div className="flex-1 overflow-y-auto pb-20">
                        {products.length === 0 ? (
                            <div className="h-full flex flex-col items-center justify-center text-[var(--text-secondary)] space-y-4">
                                <AddShoppingCartIcon sx={{ fontSize: 60, opacity: 0.3 }} />
                                <p className="font-semibold text-lg">No hay productos añadidos.</p>
                                <p className="text-sm opacity-60">Usa el catálogo o haz clic en "Añadir Fila".</p>
                            </div>
                        ) : (
                            <table className="w-full text-left border-collapse">
                                <thead className="sticky top-0 bg-[var(--bg-card)] z-10">
                                    <tr className="border-b border-[var(--border-default)] text-[var(--text-secondary)] text-sm">
                                        <th className="py-3 px-2 font-semibold">Descripción</th>
                                        <th className="py-3 px-2 font-semibold w-24">Cant.</th>
                                        <th className="py-3 px-2 font-semibold w-32 text-right">Precio U.</th>
                                        <th className="py-3 px-2 font-semibold w-32 text-right">Desc %</th>
                                        <th className="py-3 px-2 font-semibold w-32 text-right">Subtotal</th>
                                        <th className="py-3 px-2 text-center w-16"></th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {products.map(p => {
                                        const amount = p.quantity * p.price * (1 - p.discount_percent / 100);
                                        return (
                                            <tr key={p.id} className="border-b border-[var(--border-default)] hover:bg-[var(--bg-secondary)] transition-colors">
                                                <td className="py-2 px-2">
                                                    <input 
                                                        className="w-full bg-transparent border-none text-[var(--text-primary)] focus:outline-none focus:ring-1 focus:ring-blue-500 rounded px-2 py-1"
                                                        value={p.description}
                                                        onChange={e => updateProduct(p.id, 'description', e.target.value)}
                                                        placeholder="Descripción del ítem"
                                                    />
                                                </td>
                                                <td className="py-2 px-2">
                                                    <input 
                                                        type="number"
                                                        min="0"
                                                        className="w-full bg-[var(--bg-primary)] border border-[var(--border-default)] text-[var(--text-primary)] rounded px-2 py-1 text-center focus:outline-none focus:border-blue-500"
                                                        value={p.quantity}
                                                        onChange={e => updateProduct(p.id, 'quantity', parseFloat(e.target.value) || 0)}
                                                    />
                                                </td>
                                                <td className="py-2 px-2">
                                                    <input 
                                                        type="number"
                                                        min="0"
                                                        className="w-full bg-[var(--bg-primary)] border border-[var(--border-default)] text-[var(--text-primary)] rounded px-2 py-1 text-right focus:outline-none focus:border-blue-500"
                                                        value={p.price}
                                                        onChange={e => updateProduct(p.id, 'price', parseFloat(e.target.value) || 0)}
                                                    />
                                                </td>
                                                <td className="py-2 px-2">
                                                    <input 
                                                        type="number"
                                                        min="0"
                                                        max="100"
                                                        className="w-full bg-[var(--bg-primary)] border border-[var(--border-default)] text-[var(--text-primary)] rounded px-2 py-1 text-right focus:outline-none focus:border-blue-500"
                                                        value={p.discount_percent}
                                                        onChange={e => updateProduct(p.id, 'discount_percent', parseFloat(e.target.value) || 0)}
                                                    />
                                                </td>
                                                <td className="py-2 px-2 text-right font-bold text-[var(--text-primary)]">
                                                    {amount.toFixed(2)}
                                                </td>
                                                <td className="py-2 px-2 text-center">
                                                    <button 
                                                        className={theme === 'material-neo' ? "text-red-500 hover:text-red-400 p-1 rounded-full hover:bg-red-500/10 transition-colors" : "glass-button p-1 !rounded-full !text-red-400 aspect-square flex items-center justify-center"} 
                                                        onClick={() => removeProduct(p.id)}
                                                    >
                                                        <DeleteIcon fontSize="small" />
                                                    </button>
                                                </td>
                                            </tr>
                                        );
                                    })}
                                </tbody>
                            </table>
                        )}
                    </div>
                </ThemePanel>
            </div>
        </div>
    );
}

