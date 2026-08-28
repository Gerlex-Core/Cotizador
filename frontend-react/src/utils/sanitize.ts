/**
 * Utilidad de sanitización para limpiar etiquetas HTML de Qt
 * y asegurar la compatibilidad con archivos .cotz
 */

export function cleanQtHtml(text: string | null | undefined): string {
    if (!text) return '';
    
    // Remueve etiquetas HTML comunes inyectadas por Qt
    let clean = text.replace(/<[^>]*>?/gm, '');
    
    // Remueve espacios múltiples innecesarios
    clean = clean.replace(/\s{2,}/g, ' ').trim();
    
    return clean;
}

export function cleanObjectStrings<T>(obj: T): T {
    if (obj === null || obj === undefined) return obj;
    
    if (typeof obj === 'string') {
        return cleanQtHtml(obj) as unknown as T;
    }
    
    if (Array.isArray(obj)) {
        return obj.map(item => cleanObjectStrings(item)) as unknown as T;
    }
    
    if (typeof obj === 'object') {
        const newObj: any = {};
        for (const [key, value] of Object.entries(obj)) {
            newObj[key] = cleanObjectStrings(value);
        }
        return newObj as T;
    }
    
    return obj;
}
