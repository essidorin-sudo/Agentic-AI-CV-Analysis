import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { toast } from 'react-hot-toast';
import { Eye, EyeOff, BarChart3, UserPlus, CheckCircle } from 'lucide-react';

import { authAPI } from '../services/api';
import analytics from '../services/analytics';

const RegisterPage = ({ onLogin }) => {
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
    setError,
    watch
  } = useForm();

  const watchPassword = watch('password');

  const onSubmit = async (data) => {
    setIsLoading(true);
    analytics.trackFormSubmit('register_form', { email: data.email });

    try {
      const response = await authAPI.register(data);
      
      if (response.success) {
        toast.success('Registration successful! Welcome to CV Analyzer!');
        onLogin(response.user);
        analytics.trackRegister('email', true);
      } else {
        throw new Error(response.message || 'Registration failed');
      }
    } catch (error) {
      const errorMessage = error.response?.data?.error || error.message || 'Registration failed';
      
      if (errorMessage.includes('email already exists')) {
        setError('email', { message: 'An account with this email already exists' });
        analytics.trackFormError('register_form', 'email_exists', errorMessage);
      } else {
        toast.error(errorMessage);
        analytics.trackFormError('register_form', 'general', errorMessage);
      }
      
      analytics.trackRegister('email', false);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex">
      {/* Left side - Registration Form */}
      <div className="flex-1 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-md w-full space-y-8">
          {/* Header */}
          <div className="text-center">
            <div className="flex justify-center">
              <BarChart3 className="h-12 w-12 text-primary-600" />
            </div>
            <h2 className="mt-6 text-3xl font-bold text-gray-900">
              Create your account
            </h2>
            <p className="mt-2 text-sm text-gray-600">
              Join CV Analyzer and start optimizing your job applications
            </p>
          </div>

          {/* Registration Form */}
          <form className="mt-8 space-y-6" onSubmit={handleSubmit(onSubmit)}>
            <div className="space-y-4">
              {/* Name Fields */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label htmlFor="first-name" className="form-label">
                    First name *
                  </label>
                  <input
                    id="first-name"
                    type="text"
                    autoComplete="given-name"
                    className={`form-input ${errors.firstName ? 'border-danger-500' : ''}`}
                    placeholder="John"
                    {...register('firstName', {
                      required: 'First name is required',
                      minLength: {
                        value: 2,
                        message: 'First name must be at least 2 characters'
                      }
                    })}
                    onClick={() => analytics.trackClick('firstname-input', 'firstname_field_focus')}
                  />
                  {errors.firstName && (
                    <p className="form-error">{errors.firstName.message}</p>
                  )}
                </div>

                <div>
                  <label htmlFor="last-name" className="form-label">
                    Last name *
                  </label>
                  <input
                    id="last-name"
                    type="text"
                    autoComplete="family-name"
                    className={`form-input ${errors.lastName ? 'border-danger-500' : ''}`}
                    placeholder="Doe"
                    {...register('lastName', {
                      required: 'Last name is required',
                      minLength: {
                        value: 2,
                        message: 'Last name must be at least 2 characters'
                      }
                    })}
                    onClick={() => analytics.trackClick('lastname-input', 'lastname_field_focus')}
                  />
                  {errors.lastName && (
                    <p className="form-error">{errors.lastName.message}</p>
                  )}
                </div>
              </div>

              {/* Email */}
              <div>
                <label htmlFor="email" className="form-label">
                  Email address *
                </label>
                <input
                  id="email"
                  type="email"
                  autoComplete="email"
                  className={`form-input ${errors.email ? 'border-danger-500' : ''}`}
                  placeholder="john.doe@example.com"
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
                  <p className="form-error">{errors.email.message}</p>
                )}
              </div>

              {/* Password */}
              <div>
                <label htmlFor="password" className="form-label">
                  Password *
                </label>
                <div className="relative">
                  <input
                    id="password"
                    type={showPassword ? 'text' : 'password'}
                    autoComplete="new-password"
                    className={`form-input pr-10 ${errors.password ? 'border-danger-500' : ''}`}
                    placeholder="Create a strong password"
                    {...register('password', {
                      required: 'Password is required',
                      minLength: {
                        value: 8,
                        message: 'Password must be at least 8 characters'
                      },
                      pattern: {
                        value: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/,
                        message: 'Password must contain at least one uppercase letter, one lowercase letter, and one number'
                      }
                    })}
                    onClick={() => analytics.trackClick('password-input', 'password_field_focus')}
                  />
                  <button
                    type="button"
                    className="absolute inset-y-0 right-0 pr-3 flex items-center"
                    onClick={() => {
                      setShowPassword(!showPassword);
                      analytics.trackClick('toggle-password', 'password_visibility_toggle');
                    }}
                  >
                    {showPassword ? (
                      <EyeOff className="h-5 w-5 text-gray-400" />
                    ) : (
                      <Eye className="h-5 w-5 text-gray-400" />
                    )}
                  </button>
                </div>
                {errors.password && (
                  <p className="form-error">{errors.password.message}</p>
                )}
              </div>

              {/* Confirm Password */}
              <div>
                <label htmlFor="confirm-password" className="form-label">
                  Confirm password *
                </label>
                <div className="relative">
                  <input
                    id="confirm-password"
                    type={showConfirmPassword ? 'text' : 'password'}
                    autoComplete="new-password"
                    className={`form-input pr-10 ${errors.confirmPassword ? 'border-danger-500' : ''}`}
                    placeholder="Confirm your password"
                    {...register('confirmPassword', {
                      required: 'Please confirm your password',
                      validate: value => 
                        value === watchPassword || 'Passwords do not match'
                    })}
                    onClick={() => analytics.trackClick('confirm-password-input', 'confirm_password_field_focus')}
                  />
                  <button
                    type="button"
                    className="absolute inset-y-0 right-0 pr-3 flex items-center"
                    onClick={() => {
                      setShowConfirmPassword(!showConfirmPassword);
                      analytics.trackClick('toggle-confirm-password', 'confirm_password_visibility_toggle');
                    }}
                  >
                    {showConfirmPassword ? (
                      <EyeOff className="h-5 w-5 text-gray-400" />
                    ) : (
                      <Eye className="h-5 w-5 text-gray-400" />
                    )}
                  </button>
                </div>
                {errors.confirmPassword && (
                  <p className="form-error">{errors.confirmPassword.message}</p>
                )}
              </div>

              {/* Terms and Privacy */}
              <div>
                <label className="flex items-start space-x-3">
                  <input
                    type="checkbox"
                    className={`mt-1 ${errors.agreeToTerms ? 'border-danger-500' : ''}`}
                    {...register('agreeToTerms', {
                      required: 'You must agree to the terms and privacy policy'
                    })}
                    onClick={() => analytics.trackClick('terms-checkbox', 'terms_agreement_toggle')}
                  />
                  <span className="text-sm text-gray-600">
                    I agree to the{' '}
                    <a href="#" className="text-primary-600 hover:text-primary-500 underline">
                      Terms of Service
                    </a>{' '}
                    and{' '}
                    <a href="#" className="text-primary-600 hover:text-primary-500 underline">
                      Privacy Policy
                    </a>
                  </span>
                </label>
                {errors.agreeToTerms && (
                  <p className="form-error">{errors.agreeToTerms.message}</p>
                )}
              </div>
            </div>

            {/* Submit Button */}
            <div>
              <button
                type="submit"
                disabled={isLoading}
                className="w-full btn-primary flex justify-center items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
                id="register-button"
              >
                {isLoading ? (
                  <>
                    <div className="loading-spinner h-4 w-4"></div>
                    <span>Creating account...</span>
                  </>
                ) : (
                  <>
                    <UserPlus className="h-4 w-4" />
                    <span>Create Account</span>
                  </>
                )}
              </button>
            </div>

            {/* Login Link */}
            <div className="text-center">
              <p className="text-sm text-gray-600">
                Already have an account?{' '}
                <Link
                  to="/login"
                  className="font-medium text-primary-600 hover:text-primary-500"
                  onClick={() => analytics.trackLinkClick('/login', 'login_link')}
                >
                  Sign in here
                </Link>
              </p>
            </div>
          </form>
        </div>
      </div>

      {/* Right side - Benefits showcase */}
      <div className="hidden lg:flex flex-1 bg-gradient-to-br from-primary-600 to-primary-800">
        <div className="flex items-center justify-center p-12">
          <div className="max-w-md text-white">
            <h3 className="text-2xl font-bold mb-6">
              Start Your Career Journey
            </h3>
            <div className="space-y-4">
              <div className="flex items-start space-x-3">
                <div className="flex-shrink-0 w-6 h-6 bg-white/20 rounded-full flex items-center justify-center">
                  <CheckCircle className="w-4 h-4 text-white" />
                </div>
                <div>
                  <h4 className="font-medium">AI-Powered Analysis</h4>
                  <p className="text-primary-100 text-sm">
                    Get intelligent insights into how your CV matches job requirements
                  </p>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <div className="flex-shrink-0 w-6 h-6 bg-white/20 rounded-full flex items-center justify-center">
                  <CheckCircle className="w-4 h-4 text-white" />
                </div>
                <div>
                  <h4 className="font-medium">Gap Identification</h4>
                  <p className="text-primary-100 text-sm">
                    Discover exactly what skills and experience you're missing
                  </p>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <div className="flex-shrink-0 w-6 h-6 bg-white/20 rounded-full flex items-center justify-center">
                  <CheckCircle className="w-4 h-4 text-white" />
                </div>
                <div>
                  <h4 className="font-medium">Personalized Recommendations</h4>
                  <p className="text-primary-100 text-sm">
                    Get actionable advice to improve your job application success rate
                  </p>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <div className="flex-shrink-0 w-6 h-6 bg-white/20 rounded-full flex items-center justify-center">
                  <CheckCircle className="w-4 h-4 text-white" />
                </div>
                <div>
                  <h4 className="font-medium">Multiple CV Management</h4>
                  <p className="text-primary-100 text-sm">
                    Upload and compare multiple versions of your CV for different roles
                  </p>
                </div>
              </div>
            </div>
            
            <div className="mt-8 p-4 bg-white/10 rounded-lg">
              <p className="text-sm text-primary-100">
                "CV Analyzer helped me identify the exact skills I needed to develop. 
                I landed my dream job within 2 months of using the platform!"
              </p>
              <p className="text-xs text-primary-200 mt-2">
                — Sarah M., Software Engineer
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RegisterPage;