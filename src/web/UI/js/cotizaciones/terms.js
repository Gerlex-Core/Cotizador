/**
 * Package: cotizaciones/terms.js
 * Commercial terms, warranty presets, and PDF inclusion checkbox sync handlers.
 */

function syncTermCheck(primaryId, secondaryId, isChecked) {
    const el1 = document.getElementById(primaryId);
    const el2 = document.getElementById(secondaryId);
    if (el1) el1.checked = isChecked;
    if (el2) el2.checked = isChecked;
}

function syncAllTermCheckboxes() {
    const sum = document.getElementById('includeSummaryCheck');
    const bank = document.getElementById('includeBankDetailsCheck');
    const inst = document.getElementById('includeInstallationCheck');
    const warr = document.getElementById('includeWarrantyCheck');

    if (sum && document.getElementById('includeSummaryCheckHeader')) {
        document.getElementById('includeSummaryCheckHeader').checked = sum.checked;
    }
    if (bank && document.getElementById('includeBankCheckHeader')) {
        document.getElementById('includeBankCheckHeader').checked = bank.checked;
    }
    if (inst && document.getElementById('includeInstallationCheckHeader')) {
        document.getElementById('includeInstallationCheckHeader').checked = inst.checked;
    }
    if (warr && document.getElementById('includeWarrantyCheckHeader')) {
        document.getElementById('includeWarrantyCheckHeader').checked = warr.checked;
    }
}

function applyTermsPreset(method, days, warranty) {
    if (document.getElementById('termsPaymentMethodSelect')) document.getElementById('termsPaymentMethodSelect').value = method;
    if (document.getElementById('termsEstimatedDaysInput')) document.getElementById('termsEstimatedDaysInput').value = days;
    if (document.getElementById('warrantyCoversInput')) document.getElementById('warrantyCoversInput').value = warranty;
}
