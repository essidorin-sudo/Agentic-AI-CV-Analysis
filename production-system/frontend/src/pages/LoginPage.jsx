import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { toast } from 'react-hot-toast';

import { authAPI } from '../services/api';
import analytics from '../services/analytics';

const LoginPage = ({ onLogin }) => {
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
    setError
  } = useForm();

  const onSubmit = async (data) => {
    setIsLoading(true);
    analytics.trackFormSubmit('login_form', data);

    try {
      const response = await authAPI.login(data);
      
      if (response.success) {
        toast.success('Login successful!');
        onLogin(response.user);
        analytics.trackLogin('email', true);
      } else {
        throw new Error(response.message || 'Login failed');
      }
    } catch (error) {
      const errorMessage = error.response?.data?.error || error.message || 'Login failed';
      
      if (errorMessage.includes('Invalid email or password')) {
        setError('email', { message: 'Invalid email or password' });
        analytics.trackFormError('login_form', 'credentials', errorMessage);
      } else {
        toast.error(errorMessage);
        analytics.trackFormError('login_form', 'general', errorMessage);
      }
      
      analytics.trackLogin('email', false);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '20px'
    }}>
      <div className="terminal-window" style={{ maxWidth: '400px', width: '100%' }}>
        {/* Terminal Header */}
        <div className="terminal-header">
          <div className="terminal-title">CV_ANALYZER.AUTH</div>
          <div className="terminal-controls">
            <div className="terminal-dot red"></div>
            <div className="terminal-dot yellow"></div>
            <div className="terminal-dot green"></div>
          </div>
        </div>

        {/* Terminal Content */}
        <div className="terminal-content">
          <div style={{ marginBottom: '24px', textAlign: 'center' }}>
            <h1 style={{ marginBottom: '8px' }}>SYSTEM LOGIN</h1>
            <p style={{ color: '#666666' }}>Enter credentials to access CV analysis system</p>
          </div>

          <form onSubmit={handleSubmit(onSubmit)}>
            <div className="form-group">
              <label htmlFor="email" className="form-label">EMAIL</label>
              <input
                id="email"
                type="email"
                autoComplete="email"
                className="form-input"
                placeholder="user@domain.com"
                {...register('email', {
                  required: 'Email is required',
                  pattern: {
                    value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                    message: 'Invalid email address'
                  }
                })}
                onClick={() => analytics.trackClick('email-input', 'email_field_focus')}
              />
              {errors.email && (
                <div className="form-error">[ERROR] {errors.email.message}</div>
              )}
            </div>

            <div className="form-group">
              <label htmlFor="password" className="form-label">PASSWORD</label>
              <div style={{ position: 'relative' }}>
                <input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  autoComplete="current-password"
                  className="form-input"
                  placeholder="••••••••••"
                  {...register('password', {
                    required: 'Password is required',
                    minLength: {
                      value: 6,
                      message: 'Password must be at least 6 characters'
                    }
                  })}
                  onClick={() => analytics.trackClick('password-input', 'password_field_focus')}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  style={{
                    position: 'absolute',
                    right: '12px',
                    top: '50%',
                    transform: 'translateY(-50%)',
                    background: 'none',
                    border: 'none',
                    color: '#666666',
                    cursor: 'pointer',
                    fontSize: '12px'
                  }}
                >
                  [{showPassword ? 'HIDE' : 'SHOW'}]
                </button>
              </div>
              {errors.password && (
                <div className="form-error">[ERROR] {errors.password.message}</div>
              )}
            </div>

            <div style={{ marginTop: '24px', marginBottom: '16px' }}>
              <button 
                type="submit" 
                disabled={isLoading}
                className="btn btn-primary w-full"
                onClick={() => analytics.trackClick('login-submit', 'login_form_submit')}
              >
                {isLoading ? (
                  <span className="loading">
                    <span className="loading-spinner"></span>
                    AUTHENTICATING...
                  </span>
                ) : (
                  'LOGIN'
                )}
              </button>
            </div>
          </form>

          <div style={{ 
            paddingTop: '16px', 
            borderTop: '1px solid #333333', 
            textAlign: 'center' 
          }}>
            <p style={{ fontSize: '12px', color: '#666666', marginBottom: '8px' }}>
              NO ACCOUNT?
            </p>
            <Link
              to="/register"
              className="btn btn-secondary"
              onClick={() => analytics.trackLinkClick('/register', 'register_link')}
              style={{ textDecoration: 'none', fontSize: '12px' }}
            >
              CREATE_ACCOUNT
            </Link>
          </div>

          <div style={{ 
            marginTop: '24px', 
            padding: '12px', 
            backgroundColor: '#0a0a0a', 
            border: '1px solid #333333' 
          }}>
            <p style={{ fontSize: '11px', color: '#666666', margin: '0' }}>
              [SYSTEM_INFO] CV Analysis Platform v2.1.0
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;