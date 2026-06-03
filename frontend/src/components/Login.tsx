import React, { useState } from 'react';
import { GoogleLogin } from '@react-oauth/google';
import { useAuth } from '../AuthContext';
import './Login.css';

const Login: React.FC = () => {
  const { login, logout, isAuthenticated, showLoginModal, closeLogin, openLogin } = useAuth();
  const [isLoginTab, setIsLoginTab] = useState(true);
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleGoogleSuccess = async (credentialResponse: any) => {
    try {
      const response = await fetch('/api/users/auth/google', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          token: credentialResponse.credential,
        }),
      });

      if (!response.ok) {
        throw new Error('Google authentication failed');
      }

      const data = await response.json();
      login(data.access_token);
    } catch (err: any) {
      setError(err.message);
    }
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    
    try {
      const response = await fetch('/api/users/token', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
          username: email, // Backend uses email as username in OAuth2PasswordRequestForm
          password: password,
        }),
      });

      if (!response.ok) {
        throw new Error('Invalid email or password');
      }

      const data = await response.json();
      login(data.access_token);
    } catch (err: any) {
      setError(err.message);
    }
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    
    try {
      const response = await fetch('/api/users', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email,
          username,
          password,
        }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Registration failed');
      }

      // Auto login after registration
      await handleLogin(e);
    } catch (err: any) {
      setError(err.message);
    }
  };

  if (isAuthenticated) {
    return (
      <button className="auth-button" onClick={logout}>Logout</button>
    );
  }

  return (
    <>
      <button className="auth-button" onClick={openLogin}>Sign In</button>

      {showLoginModal && (
        <div className="modal-overlay" onClick={closeLogin}>
          <div className="brutal-card login-modal" onClick={(e) => e.stopPropagation()}>
            <button className="close-modal" onClick={closeLogin}>&times;</button>
            
            <div className="auth-tabs">
              <button 
                className={`tab-btn ${isLoginTab ? 'active' : ''}`} 
                onClick={() => setIsLoginTab(true)}
              >
                Log In
              </button>
              <button 
                className={`tab-btn ${!isLoginTab ? 'active' : ''}`} 
                onClick={() => setIsLoginTab(false)}
              >
                Register
              </button>
            </div>

            <form onSubmit={isLoginTab ? handleLogin : handleRegister} className="login-form">
              <input 
                type="email" 
                placeholder="Email" 
                value={email} 
                onChange={(e) => setEmail(e.target.value)} 
                required 
              />
              {!isLoginTab && (
                <input 
                  type="text" 
                  placeholder="Username" 
                  value={username} 
                  onChange={(e) => setUsername(e.target.value)} 
                  required 
                />
              )}
              <input 
                type="password" 
                placeholder="Password" 
                value={password} 
                onChange={(e) => setPassword(e.target.value)} 
                required 
              />
              <button type="submit" className="brutal-btn auth-button">
                {isLoginTab ? 'Sign In' : 'Create Account'}
              </button>
            </form>

            {error && <p className="error-message">{error}</p>}

            <div className="sso-divider">OR CONTINUE WITH</div>

            <div className="google-sso-container">
              <GoogleLogin
                onSuccess={handleGoogleSuccess}
                onError={() => {
                  setError('Google Login Failed');
                }}
                useOneTap
                theme="outline"
                shape="pill"
                width="100%"
              />
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default Login;
