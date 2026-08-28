/**
 * Package: cotizaciones/finance.js
 * Financial event handlers and calculation triggers.
 */

document.addEventListener('DOMContentLoaded', () => {
    const discountInput = document.getElementById('discountPercentInput');
    const ivaInput = document.getElementById('ivaPercentInput');
    const paidInput = document.getElementById('paidAmountInput');
    const shippingInput = document.getElementById('shippingAmountInput');

    if (discountInput) discountInput.addEventListener('input', () => calculateTotals());
    if (ivaInput) ivaInput.addEventListener('input', () => calculateTotals());
    if (paidInput) paidInput.addEventListener('input', () => calculateTotals());
    if (shippingInput) shippingInput.addEventListener('input', () => calculateTotals());
});
