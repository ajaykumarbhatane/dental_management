import { useEffect, useState, useCallback } from 'react';
import Cookies from 'js-cookie';
import useAuthStore from '../store/authStore';
import { authService } from '../services/api';

export const useAuth = () => {
  const { user, isAuthenticated, setUser, setLoading, setError, logout } =
    useAuthStore();
  const [isInitialized, setIsInitialized] = useState(false);

  // Initialize auth state on mount
  useEffect(() => {
    const initAuth = async () => {
      try {
        const response = await authService.me();
        // Handle nested data structure
        const userData = response.data.data?.user || response.data.user || response.data;
        setUser(userData);
      } catch (error) {
        logout();
      } finally {
        setIsInitialized(true);
      }
    };

    if (isAuthenticated && !user) {
      initAuth();
    } else {
      setIsInitialized(true);
    }
  }, [isAuthenticated, user, setUser, logout]);

  const login = useCallback(async (email, password) => {
    setLoading(true);
    setError(null);
    try {
      const response = await authService.login(email, password);
      // Response structure: { success, message, data: { user, access, refresh } }
      const respData = response.data.data || response.data;

      // save tokens in cookies so interceptor can send them
      if (respData.access) {
        Cookies.set('access_token', respData.access, { expires: 7 });
      }
      if (respData.refresh) {
        Cookies.set('refresh_token', respData.refresh, { expires: 30 });
      }

      const userData = respData.user || response.data.user;
      setUser(userData);
      return respData;
    } catch (error) {
      const message = error.response?.data?.detail || 'Login failed';
      setError(message);
      throw error;
    } finally {
      setLoading(false);
    }
  }, [setUser, setLoading, setError]);

  const handleLogout = useCallback(async () => {
    try {
      await authService.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // remove tokens from cookies as well
      Cookies.remove('access_token');
      Cookies.remove('refresh_token');
      logout();
    }
  }, [logout]);

  return {
    user,
    isAuthenticated,
    isInitialized,
    login,
    logout: handleLogout,
  };
};

export default useAuth;
