import { useState, useCallback } from 'react';
import { authApi } from '../api/client';

export function useAuth() {
  const [token] = useState(() => localStorage.getItem('token'));
  const [username] = useState(() => localStorage.getItem('username'));
  const [isAuthenticated, setIsAuthenticated] = useState(() => !!localStorage.getItem('token'));
  const [authUsername, setAuthUsername] = useState(() => localStorage.getItem('username') || '');

  const login = useCallback(async (credentials) => {
    const res = await authApi.login(credentials);
    localStorage.setItem('token', res.data.access_token);
    localStorage.setItem('username', res.data.username);
    setIsAuthenticated(true);
    setAuthUsername(res.data.username);
    return res.data;
  }, []);

  const register = useCallback(async (data) => {
    const res = await authApi.register(data);
    localStorage.setItem('token', res.data.access_token);
    localStorage.setItem('username', res.data.username);
    setIsAuthenticated(true);
    setAuthUsername(res.data.username);
    return res.data;
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    setIsAuthenticated(false);
    setAuthUsername('');
  }, []);

  return { isAuthenticated, username: authUsername, token, login, register, logout };
}
