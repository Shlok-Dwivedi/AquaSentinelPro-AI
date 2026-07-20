import React, { useState, useEffect } from 'react';
import { supabase } from './lib/supabase';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import Chat from './pages/Chat';
import Analysis from './pages/Analysis';
import Reports from './pages/Reports';
import Complaints from './pages/Complaints';
import Settings from './pages/Settings';
import Login from './pages/Login';
import Register from './pages/Register';
import Onboarding from './pages/Onboarding';
import Guide from './pages/Guide';

function App() {
  const [session, setSession] = useState(null);
  const [userProfile, setUserProfile] = useState(null);
  const [isCheckingProfile, setIsCheckingProfile] = useState(true);
  const [isCheckingSession, setIsCheckingSession] = useState(true);
  const [authScreen, setAuthScreen] = useState('login'); // 'login', 'register'
  const [currentPage, setCurrentPage] = useState('dashboard');

  const [chatMessages, setChatMessages] = useState(() => {
    const saved = sessionStorage.getItem('chat_messages');
    if (saved) return JSON.parse(saved);
    return [];
  });
  const [isChatLoading, setIsChatLoading] = useState(false);
  const [chatStatusMessage, setChatStatusMessage] = useState("Running Multi-Agent Pipeline...");

  useEffect(() => {
    sessionStorage.setItem('chat_messages', JSON.stringify(chatMessages));
  }, [chatMessages]);

  useEffect(() => {
    // Get initial session
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session);
      setIsCheckingSession(false);
    });

    // Listen for auth changes
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session);
      setIsCheckingSession(false);
    });

    return () => subscription.unsubscribe();
  }, []);

  // When session changes, fetch public.users profile
  useEffect(() => {
    const fetchProfile = async () => {
      if (!session) {
        setUserProfile(null);
        setIsCheckingProfile(false);
        return;
      }
      
      setIsCheckingProfile(true);
      
      try {
        const response = await fetch('http://localhost:8000/api/v1/auth/me', {
          headers: {
            'Authorization': `Bearer ${session.access_token}`
          }
        });
        
        if (response.ok) {
          const profile = await response.json();
          setUserProfile(profile);
        } else if (response.status === 404) {
          setUserProfile(null); // Needs onboarding
        } else if (response.status === 401) {
          // Token is expired or invalid
          await supabase.auth.signOut();
          setSession(null);
          setUserProfile(null);
          return;
        } else {
          console.error("Unexpected error fetching profile:", response.status);
        }
      } catch (err) {
        console.error("Error fetching profile:", err);
      } finally {
        setIsCheckingProfile(false);
      }
    };

    fetchProfile();
  }, [session?.access_token]);

  const handleLogout = async () => {
    await supabase.auth.signOut();
    setSession(null);
    setUserProfile(null);
    setAuthScreen('login');
  };

  if (isCheckingSession || (isCheckingProfile && session)) {
    return (
      <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center text-white space-y-4">
        <div className="w-12 h-12 border-4 border-aqua-500 border-t-transparent rounded-full animate-spin"></div>
        <p className="text-aqua-400 font-semibold tracking-wide animate-pulse">Initializing AquaSentinel...</p>
      </div>
    );
  }

  // If not authenticated, render Login/Register auth screens
  if (!session) {
    if (authScreen === 'register') {
      return (
        <Register 
          onRegisterSuccess={(session) => setSession(session)} 
          switchToLogin={() => setAuthScreen('login')} 
        />
      );
    }
    return (
      <Login 
        onLoginSuccess={(session) => setSession(session)} 
        switchToRegister={() => setAuthScreen('register')} 
      />
    );
  }

  // If authenticated but no profile, show onboarding
  if (!userProfile) {
    return <Onboarding session={session} onComplete={(profile) => {
      setUserProfile(profile);
      setCurrentPage('guide');
    }} />;
  }

  const renderPage = () => {
    switch (currentPage) {
      case 'dashboard': return <Dashboard session={session} setCurrentPage={setCurrentPage} />;
      case 'chat': return <Chat 
                      session={session} 
                      messages={chatMessages}
                      setMessages={setChatMessages}
                      isLoading={isChatLoading}
                      setIsLoading={setIsChatLoading}
                      statusMessage={chatStatusMessage}
                      setStatusMessage={setChatStatusMessage}
                    />;
      case 'analysis': return <Analysis session={session} />;
      case 'reports': return <Reports session={session} />;
      case 'complaints': return <Complaints session={session} />;
      case 'settings': return <Settings session={session} />;
      case 'guide': return <Guide setCurrentPage={setCurrentPage} />;
      default: return <Dashboard session={session} setCurrentPage={setCurrentPage} />;
    }
  };

  return (
    <div className="flex bg-slate-950 min-h-screen">
      <Sidebar 
        currentPage={currentPage} 
        setCurrentPage={setCurrentPage} 
        currentUser={userProfile}
        onLogout={handleLogout}
      />
      <main className="flex-1 p-8 overflow-x-hidden">
        <div className="max-w-7xl mx-auto">
          {renderPage()}
        </div>
      </main>
    </div>
  );
}

export default App;
