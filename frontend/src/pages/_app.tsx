import type { AppProps } from 'next/app';
import { useEffect } from 'react';
import { useAuthStore, initializeAuth } from '../stores/authStore';
import '../styles/globals.css';

function MyApp({ Component, pageProps }: AppProps) {
  const { isAuthenticated } = useAuthStore();

  useEffect(() => {
    // Initialize authentication state from localStorage
    initializeAuth();
  }, []);

  return <Component {...pageProps} />;
}

export default MyApp; 