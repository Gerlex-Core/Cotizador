export default function TermsView() {
    return (
        <div className="flex h-full gap-4">
            <div className="flex-1 glass-panel rounded-3xl p-6 flex flex-col space-y-4">
                <div className="flex items-center space-x-2 border-b border-[var(--border-default)] pb-3">
                    <span className="material-symbols-outlined text-2xl text-[var(--text-primary)]">gavel</span>
                    <h2 className="text-lg font-bold text-[var(--text-primary)]">Términos Comerciales</h2>
                </div>
                <div className="flex-1 flex flex-col">
                    <textarea 
                        className="glass-input flex-1 w-full p-4 rounded-2xl resize-none"
                        placeholder="Ingresa los términos y condiciones de venta aquí..."
                        defaultValue={`TÉRMINOS Y CONDICIONES:\n\n1. Los precios están expresados en Bolivianos (Bs) e incluyen impuestos de ley.\n2. La validez de la oferta es de 15 días calendario a partir de la fecha de emisión.\n3. Forma de pago: 50% anticipo, 50% contra entrega.\n4. Tiempo de entrega: Inmediato sujeto a disponibilidad de stock.`}
                    ></textarea>
                </div>
            </div>

            <div className="flex-1 glass-panel rounded-3xl p-6 flex flex-col space-y-4">
                <div className="flex items-center space-x-2 border-b border-[var(--border-default)] pb-3">
                    <span className="material-symbols-outlined text-2xl text-[var(--text-primary)]">verified</span>
                    <h2 className="text-lg font-bold text-[var(--text-primary)]">Garantía</h2>
                </div>
                <div className="flex-1 flex flex-col">
                    <textarea 
                        className="glass-input flex-1 w-full p-4 rounded-2xl resize-none"
                        placeholder="Ingresa las políticas de garantía aquí..."
                        defaultValue={`POLÍTICAS DE GARANTÍA:\n\n1. Todos los equipos cuentan con 1 año de garantía contra defectos de fábrica.\n2. La garantía no cubre daños por variaciones de voltaje, mala manipulación o desastres naturales.\n3. Todo equipo en garantía debe ser ingresado a servicio técnico con su respectiva factura y caja original.`}
                    ></textarea>
                </div>
            </div>
        </div>
    );
}
