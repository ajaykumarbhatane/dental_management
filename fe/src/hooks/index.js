import { useState, useCallback } from 'react';
import toast from 'react-hot-toast';

export const useAsync = (asyncFunction, immediate = true) => {
  const [status, setStatus] = useState('idle');
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  const execute = useCallback(async (...args) => {
    setStatus('pending');
    setData(null);
    setError(null);

    try {
      const response = await asyncFunction(...args);
      setData(response.data || response);
      setStatus('success');
      return response;
    } catch (err) {
      setError(err);
      setStatus('error');
      throw err;
    }
  }, [asyncFunction]);

  return { execute, status, data, error };
};

export const useFetch = (url, options = {}) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const refetch = useCallback(async () => {
    setLoading(true);
    try {
      const response = await fetch(url, options);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const result = await response.json();
      setData(result);
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
  }, [url, options]);

  return { data, loading, error, refetch };
};

export const useToast = () => {
  const success = (message) => toast.success(message);
  const error = (message) => toast.error(message);
  const loading = (message) => toast.loading(message);
  const custom = (message, icon) => toast.custom(() => icon, { duration: 3000 });

  return { success, error, loading, custom };
};

export default useAsync;
