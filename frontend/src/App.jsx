import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import Chat from './pages/Chat';
import Analysis from './pages/Analysis';
import Reports from './pages/Reports';
import Complaints from './pages/Complaints';
import Settings from './pages/Settings';
import Login from './pages/Login';
import Register from './pages/Register';

function App() {
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [user, setUser] = useState(JSON.parse(localStorage.getItem('user')));
  const [authScreen, setAuthScreen] = useState('login'); // 'login', 'register'
  const [currentPage, setCurrentPage] = useState('dashboard');

  // Verify token validity on load
  useEffect(() => {
    if (token) {
      fetch('http://localhost:8000/api/v1/auth/me', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      .then((res) => {
        if (!res.ok) throw new Error('Session expired');
        return res.json();
      })
      .then((userData) => {
        setUser(userData);
        localStorage.setItem('user', JSON.stringify(userData));
      })
      .catch(() => {
        // Clear expired token
        handleLogout();
      });
    }
  }, [token]);

  const handleLoginSuccess = (newToken, newUser) => {
    localStorage.setItem('token', newToken);
    localStorage.setItem('user', JSON.stringify(newUser));
    setToken(newToken);
    setUser(newUser);
    setCurrentPage('dashboard');
  };

  const handleLogout = async () => {
    if (token) {
      try {
        await fetch('http://localhost:8000/api/v1/auth/logout', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
      } catch (err) {
        console.error('Failed to log out from server:', err);
      }
    }
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setToken(null);
    setUser(null);
    setAuthScreen('login');
  };

  // If not authenticated, render Login/Register auth screens
  if (!token) {
    if (authScreen === 'register') {
      return (
        <Register 
          onRegisterSuccess={handleLoginSuccess} 
          switchToLogin={() => setAuthScreen('login')} 
        />
      );
    }
    return (
      <Login 
        onLoginSuccess={handleLoginSuccess} 
        switchToRegister={() => setAuthScreen('register')} 
      />
    );
  }

  const renderPage = () => {
    switch (currentPage) {
      case 'dashboard':
        return <Dashboard />;
      case 'chat':
        return <Chat />;
      case 'analysis':
        return <Analysis />;
      case 'reports':
        return <Reports />;
      case 'complaints':
        return <Complaints />;
      case 'settings':
        return <Settings />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="flex bg-slate-950 min-h-screen">
      {/* Sidebar Navigation */}
      <Sidebar 
        currentPage={currentPage} 
        setCurrentPage={setCurrentPage} 
        currentUser={user}
        onLogout={handleLogout}
      />
      
      {/* Main Workspace Area */}
      <main className="flex-1 p-8 overflow-x-hidden">
        <div className="max-w-7xl mx-auto">
          {renderPage()}
        </div>
      </main>
    </div>
  );
}

export default App;
