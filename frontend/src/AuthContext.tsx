import React, { createContext, useState, useContext } from 'react';

interface AuthContextType {
  token: string | null;
  login: (token: string) => void;
  logout: () => void;
  isAuthenticated: boolean;
  showLoginModal: boolean;
  openLogin: () => void;
  closeLogin: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'));
  const [showLoginModal, setShowLoginModal] = useState(false);

  const login = (newToken: string) => {
    setToken(newToken);
    localStorage.setItem('token', newToken);
    setShowLoginModal(false);
  };

  const logout = () => {
    setToken(null);
    localStorage.removeItem('token');
  };

  const openLogin = () => setShowLoginModal(true);
  const closeLogin = () => setShowLoginModal(false);

  const isAuthenticated = !!token;

  return (
    <AuthContext.Provider value={{ 
      token, 
      login, 
      logout, 
      isAuthenticated, 
      showLoginModal, 
      openLogin, 
      closeLogin 
    }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
