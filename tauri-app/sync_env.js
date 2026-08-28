import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const envPath = path.resolve(__dirname, '../.env');
const outPath = path.resolve(__dirname, '../src/web/UI/js/env.js');

try {
    const envFile = fs.readFileSync(envPath, 'utf8');
    let apiBaseUrl = '';
    for (const line of envFile.split('\n')) {
        if (line.startsWith('API_BASE_URL=')) {
            apiBaseUrl = line.split('=')[1].trim();
        }
    }
    
    const jsContent = `window.ENV = { API_BASE_URL: "${apiBaseUrl}" };\n`;
    fs.writeFileSync(outPath, jsContent);
    console.log('✅ Generated env.js from .env');
} catch (e) {
    console.error('Error syncing env:', e.message);
}
