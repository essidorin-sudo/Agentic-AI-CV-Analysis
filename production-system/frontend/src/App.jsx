import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import jwt_decode from 'jwt-decode';

// Components
import Navbar from './components/Navbar';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import DashboardPage from './pages/DashboardPage';
import AnalysisPage from './pages/AnalysisPage';
import CVLibraryPage from './pages/CVLibraryPage';
import JobDescriptionsPage from './pages/JobDescriptionsPage';
import ComparisonsPage from './pages/ComparisonsPage';
import ComparisonDetailPage from './pages/ComparisonDetailPage';
import ProfilePage from './pages/ProfilePage';

// Services
import analytics from './services/analytics';
import { authAPI } from './services/api';


function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);


  useEffect(() => {
    // Check for existing auth token and validate
    const token = localStorage.getItem('authToken');
    if (token) {
      try {
        const decoded = jwt_decode(token);
        const currentTime = Date.now() / 1000;
        
        if (decoded.exp > currentTime) {
          // Token is valid, get user profile
          loadUserProfile();
        } else {
          // Token expired
          localStorage.removeItem('authToken');
          setLoading(false);
        }
      } catch (error) {
        // Invalid token
        localStorage.removeItem('authToken');
        setLoading(false);
      }
    } else {
      setLoading(false);
    }
  }, []);

  const loadUserProfile = async () => {
    try {
      const response = await authAPI.getProfile();
      setUser(response.user);
      analytics.setUserId(response.user.id);
    } catch (error) {
      console.error('Failed to load user profile:', error);
      localStorage.removeItem('authToken');
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = (userData) => {
    setUser(userData);
    analytics.setUserId(userData.id);
    analytics.trackLogin('email', true);
  };

  const handleLogout = () => {
    analytics.trackLogout();
    setUser(null);
    authAPI.logout();
  };

  // Protected Route Component
  const ProtectedRoute = ({ children }) => {
    if (loading) {
      return (
        <div className="min-h-screen flex items-center justify-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>
      );
    }
    
    return user ? children : <Navigate to="/login" replace />;
  };

  // Public Route Component (redirect to dashboard if already logged in)
  const PublicRoute = ({ children }) => {
    if (loading) {
      return (
        <div className="min-h-screen flex items-center justify-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>
      );
    }
    
    return user ? <Navigate to="/dashboard" replace /> : children;
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <h2 className="text-xl font-semibold text-gray-700">Loading CV Analyzer...</h2>
        </div>
      </div>
    );
  }

  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        {user && <Navbar user={user} onLogout={handleLogout} />}
        
        <main style={{ paddingTop: user ? '60px' : '0' }}>
          <Routes>
            {/* Public Routes */}
            <Route 
              path="/login" 
              element={
                <PublicRoute>
                  <LoginPage onLogin={handleLogin} />
                </PublicRoute>
              } 
            />
            <Route 
              path="/register" 
              element={
                <PublicRoute>
                  <RegisterPage onRegister={handleLogin} />
                </PublicRoute>
              } 
            />

            {/* Protected Routes */}
            <Route 
              path="/dashboard" 
              element={
                <ProtectedRoute>
                  <DashboardPage user={user} />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/analysis" 
              element={
                <ProtectedRoute>
                  <AnalysisPage />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/cvs" 
              element={
                <ProtectedRoute>
                  <CVLibraryPage />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/job-descriptions" 
              element={
                <ProtectedRoute>
                  <JobDescriptionsPage />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/comparisons" 
              element={
                <ProtectedRoute>
                  <ComparisonsPage />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/comparisons/:id" 
              element={
                <ProtectedRoute>
                  <ComparisonDetailPage />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/profile" 
              element={
                <ProtectedRoute>
                  <ProfilePage user={user} />
                </ProtectedRoute>
              } 
            />

            {/* Default redirects */}
            <Route 
              path="/" 
              element={
                user ? <Navigate to="/dashboard" replace /> : <Navigate to="/login" replace />
              } 
            />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>

        {/* Toast notifications */}
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: '#363636',
              color: '#fff',
            },
            success: {
              style: {
                background: '#22c55e',
              },
            },
            error: {
              style: {
                background: '#ef4444',
              },
            },
          }}
        />
      </div>
    </Router>
  );
}

export default App;