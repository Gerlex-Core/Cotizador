// API Configuration

// Detect if we are running inside a Tauri window
const isTauri = !!(window as any).__TAURI__ || !!(window as any).__TAURI_INTERNALS__;

let API_BASE_URL = '';

if (isTauri) {
    // Hardcoded IP for Tauri as requested
    API_BASE_URL = 'http://157.173.102.129:8000';
} else {
    // Web environment: Extract the hostname (IP) from the browser and point to port 8000
    const hostname = window.location.hostname;
    API_BASE_URL = `http://${hostname}:8000`;
}

export { API_BASE_URL };
