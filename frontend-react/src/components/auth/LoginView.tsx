import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { API_BASE_URL } from '../../config/apiConfig';
import { useAuth } from '../../context/AuthContext';
import { useTheme } from '../../context/ThemeContext';

interface LoginViewProps {
  onSuccess: () => void;
}

const LoginView: React.FC<LoginViewProps> = ({ onSuccess }) => {
  const [isRegistering, setIsRegistering] = useState(false);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [masterKey, setMasterKey] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  
  const { login } = useAuth();
  const { theme } = useTheme();
  const isDark = theme === 'glass-ios';

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    const endpoint = isRegistering ? `${API_BASE_URL}/api/auth/register` : `${API_BASE_URL}/api/auth/login`;
    
    const payload = isRegistering 
      ? { username, password, master_key: masterKey }
      : { username, password };

    try {
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Ocurrió un error en la autenticación');
      }

      if (isRegistering) {
        setIsRegistering(false);
        setPassword('');
        setMasterKey('');
        setError('Usuario creado exitosamente. Por favor inicia sesión.');
      } else {
        login(data.access_token, data.user);
        onSuccess();
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={`min-h-screen flex items-center justify-center p-4 transition-colors duration-500`}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className={`w-full max-w-md p-8 rounded-3xl backdrop-blur-2xl border shadow-2xl relative overflow-hidden ${
          isDark 
            ? 'bg-black/40 border-white/10 shadow-black/50 text-white' 
            : 'bg-white/70 border-white/40 shadow-gray-200/50 text-gray-900'
        }`}
      >
        <div className="absolute top-0 right-0 p-6 opacity-10 pointer-events-none">
          <span className="material-symbols-outlined text-9xl">admin_panel_settings</span>
        </div>
        
        <h2 className="text-3xl font-bold mb-2">
          {isRegistering ? 'Crear Cuenta' : 'Bienvenido'}
        </h2>
        <p className={`mb-8 ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
          {isRegistering 
            ? 'Ingresa tu Master API Key para registrarte' 
            : 'Inicia sesión para acceder a Cotizador Pro'}
        </p>

        {error && (
          <div className={`p-4 rounded-xl mb-6 flex items-start gap-3 ${
            error.includes('exitosa') ? 'bg-green-500/10 text-green-500' : 'bg-red-500/10 text-red-500'
          }`}>
            <span className="material-symbols-outlined shrink-0">
              {error.includes('exitosa') ? 'check_circle' : 'error'}
            </span>
            <p className="text-sm font-medium">{error}</p>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-5">
          <div className="space-y-1.5">
            <label className={`text-sm font-medium ${isDark ? 'text-gray-300' : 'text-gray-700'}`}>
              Usuario
            </label>
            <div className="relative">
              <span className={`absolute left-4 top-1/2 -translate-y-1/2 material-symbols-outlined ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>
                person
              </span>
              <input
                type="text"
                required
                value={username}
                onChange={e => setUsername(e.target.value)}
                className={`w-full pl-11 pr-4 py-3 rounded-2xl outline-none transition-all ${
                  isDark 
                    ? 'bg-white/5 border border-white/10 focus:bg-white/10 focus:border-blue-500 text-white' 
                    : 'bg-white/50 border border-gray-200 focus:bg-white focus:border-blue-500 text-gray-900'
                }`}
                placeholder="Ej. admin"
              />
            </div>
          </div>

          <div className="space-y-1.5">
            <label className={`text-sm font-medium ${isDark ? 'text-gray-300' : 'text-gray-700'}`}>
              Contraseña
            </label>
            <div className="relative">
              <span className={`absolute left-4 top-1/2 -translate-y-1/2 material-symbols-outlined ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>
                lock
              </span>
              <input
                type="password"
                required
                value={password}
                onChange={e => setPassword(e.target.value)}
                className={`w-full pl-11 pr-4 py-3 rounded-2xl outline-none transition-all ${
                  isDark 
                    ? 'bg-white/5 border border-white/10 focus:bg-white/10 focus:border-blue-500 text-white' 
                    : 'bg-white/50 border border-gray-200 focus:bg-white focus:border-blue-500 text-gray-900'
                }`}
                placeholder="••••••••"
              />
            </div>
          </div>

          {isRegistering && (
            <motion.div 
              initial={{ opacity: 0, height: 0 }} 
              animate={{ opacity: 1, height: 'auto' }}
              className="space-y-1.5"
            >
              <label className={`text-sm font-medium flex items-center gap-2 ${isDark ? 'text-blue-400' : 'text-blue-600'}`}>
                <span className="material-symbols-outlined text-[18px]">key</span>
                Master API Key
              </label>
              <div className="relative">
                <input
                  type="password"
                  required={isRegistering}
                  value={masterKey}
                  onChange={e => setMasterKey(e.target.value)}
                  className={`w-full px-4 py-3 rounded-2xl outline-none transition-all border ${
                    isDark 
                      ? 'bg-blue-500/5 border-blue-500/30 focus:border-blue-400 text-blue-100' 
                      : 'bg-blue-50 border-blue-200 focus:border-blue-500 text-blue-900'
                  }`}
                  placeholder="Requerido para crear cuenta"
                />
              </div>
            </motion.div>
          )}

          <button
            type="submit"
            disabled={loading}
            className={`w-full py-3.5 rounded-2xl font-semibold flex items-center justify-center gap-2 transition-all active:scale-[0.98] mt-4 ${
              isDark 
                ? 'bg-white text-black hover:bg-gray-100' 
                : 'bg-black text-white hover:bg-gray-900'
            } disabled:opacity-50`}
          >
            {loading ? (
              <span className="material-symbols-outlined animate-spin">refresh</span>
            ) : (
              <>
                {isRegistering ? 'Crear Cuenta' : 'Ingresar'}
                <span className="material-symbols-outlined text-[20px]">
                  {isRegistering ? 'person_add' : 'arrow_forward'}
                </span>
              </>
            )}
          </button>
        </form>

        <div className="mt-8 text-center">
          <button
            type="button"
            onClick={() => {
              setIsRegistering(!isRegistering);
              setError('');
            }}
            className={`text-sm font-medium hover:underline transition-colors ${
              isDark ? 'text-gray-400 hover:text-white' : 'text-gray-500 hover:text-black'
            }`}
          >
            {isRegistering 
              ? '¿Ya tienes cuenta? Inicia sesión aquí' 
              : '¿No tienes cuenta? Regístrate con la Master Key'}
          </button>
        </div>
      </motion.div>
    </div>
  );
};

export default LoginView;
