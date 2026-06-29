import { createContext, useState, useContext, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext();

// ── Set token immediately from localStorage (before any component renders) ──
// This prevents 401s from components that fetch data on their first render,
// which otherwise race against the AuthProvider useEffect.
const _storedToken = localStorage.getItem('token');
if (_storedToken) {
  axios.defaults.headers.common['Authorization'] = `Bearer ${_storedToken}`;
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    // Initialise user synchronously too so PrivateRoute has it immediately
    const stored = localStorage.getItem('user');
    return stored ? JSON.parse(stored) : null;
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Axios response interceptor to automatically logout on 401 errors
    let redirecting = false;
    const interceptor = axios.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response && error.response.status === 401 && !redirecting) {
          redirecting = true;
          logout();
          // Redirect to login page
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
    return () => {
      axios.interceptors.response.eject(interceptor);
    };
  }, []);


  const login = async (email, password) => {
    const response = await axios.post('/api/auth/login', { email, password });
    const { access_token, user } = response.data;
    
    localStorage.setItem('token', access_token);
    localStorage.setItem('user', JSON.stringify(user));
    axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
    
    setUser(user);
    return user;
  };

  const signup = async (name, email, password) => {
    const response = await axios.post('/api/auth/signup', { name, email, password });
    const { access_token, user } = response.data;
    
    localStorage.setItem('token', access_token);
    localStorage.setItem('user', JSON.stringify(user));
    axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
    
    setUser(user);
    return user;
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    delete axios.defaults.headers.common['Authorization'];
    setUser(null);
  };


  return (
    <AuthContext.Provider value={{ user, login, signup, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
