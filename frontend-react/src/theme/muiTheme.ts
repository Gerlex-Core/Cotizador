import { createTheme } from '@mui/material/styles';

export const muiMaterialNeoTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#bb86fc', // Material Design Dark Mode Accent
    },
    secondary: {
      main: '#03dac6',
    },
    background: {
      default: '#121212',
      paper: '#1e1e1e', // Elevated surfaces
    },
    text: {
      primary: '#e6e1e5',
      secondary: '#cac4d0',
    },
  },
  shape: {
    borderRadius: 16, // Modern Material 3 roundness
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    button: {
      textTransform: 'none',
      fontWeight: 600,
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 24,
          padding: '10px 24px',
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: 12,
          },
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: 'none', // Remove default white overlay in dark mode
        }
      }
    }
  },
});

export const muiGlassTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#0A84FF',
    },
    background: {
      default: '#000000',
      paper: 'transparent',
    },
    text: {
      primary: '#FFFFFF',
      secondary: 'rgba(235, 235, 245, 0.6)',
    },
  },
  shape: {
    borderRadius: 24,
  },
  typography: {
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif',
  },
  components: {
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
          boxShadow: 'none',
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: 16,
            backgroundColor: 'rgba(255, 255, 255, 0.05)',
            backdropFilter: 'blur(10px)',
            '& fieldset': {
              borderColor: 'rgba(255, 255, 255, 0.1)',
            },
            '&:hover fieldset': {
              borderColor: 'rgba(255, 255, 255, 0.2)',
            },
            '&.Mui-focused fieldset': {
              borderColor: 'rgba(255, 255, 255, 0.3)',
            },
          },
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 24,
          backgroundColor: 'rgba(255, 255, 255, 0.05)',
          backdropFilter: 'blur(10px)',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          boxShadow: '0 4px 24px rgba(0,0,0,0.4)',
          textTransform: 'none',
          '&:hover': {
            backgroundColor: 'rgba(255, 255, 255, 0.1)',
          }
        },
      },
    },
  },
});
