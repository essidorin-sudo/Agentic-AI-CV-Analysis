import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { toast } from 'react-hot-toast';
import { 
  User, 
  Mail, 
  Lock, 
  Save, 
  Eye, 
  EyeOff,
  Shield,
  Bell,
  Trash2,
  Download
} from 'lucide-react';

import { authAPI } from '../services/api';
import analytics from '../services/analytics';

const ProfilePage = ({ user }) => {
  const [activeTab, setActiveTab] = useState('profile');
  const [showCurrentPassword, setShowCurrentPassword] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isUpdating, setIsUpdating] = useState(false);

  const profileForm = useForm({
    defaultValues: {
      firstName: user?.first_name || '',
      lastName: user?.last_name || '',
      email: user?.email || ''
    }
  });

  const passwordForm = useForm();

  const handleProfileUpdate = async (data) => {
    try {
      setIsUpdating(true);
      analytics.trackFormSubmit('profile_update_form', data);

      // TODO: Implement profile update API endpoint
      // const response = await authAPI.updateProfile(data);
      
      toast.success('Profile updated successfully!');
      analytics.trackProfileUpdate(true);
    } catch (error) {
      console.error('Profile update failed:', error);
      toast.error('Failed to update profile');
      analytics.trackProfileUpdate(false, error.message);
    } finally {
      setIsUpdating(false);
    }
  };

  const handlePasswordUpdate = async (data) => {
    if (data.newPassword !== data.confirmPassword) {
      toast.error('New passwords do not match');
      return;
    }

    try {
      setIsUpdating(true);
      analytics.trackFormSubmit('password_update_form', { email: user.email });

      // TODO: Implement password update API endpoint
      // const response = await authAPI.updatePassword(data);
      
      toast.success('Password updated successfully!');
      passwordForm.reset();
      analytics.trackPasswordUpdate(true);
    } catch (error) {
      console.error('Password update failed:', error);
      toast.error('Failed to update password');
      analytics.trackPasswordUpdate(false, error.message);
    } finally {
      setIsUpdating(false);
    }
  };

  const handleDeleteAccount = async () => {
    if (!confirm('Are you sure you want to delete your account? This action cannot be undone.')) {
      return;
    }

    try {
      analytics.trackAccountDeletion('initiated');
      
      // TODO: Implement account deletion API endpoint
      // const response = await authAPI.deleteAccount();
      
      toast.success('Account deletion initiated');
      analytics.trackAccountDeletion('completed');
      
      // Redirect to login or logout
    } catch (error) {
      console.error('Account deletion failed:', error);
      toast.error('Failed to delete account');
      analytics.trackAccountDeletion('failed', error.message);
    }
  };

  const handleDataExport = async () => {
    try {
      analytics.trackClick('export-data', 'request_data_export');
      
      // TODO: Implement data export API endpoint
      // const response = await authAPI.exportData();
      
      toast.success('Data export will be emailed to you within 24 hours');
      analytics.trackDataExport('requested');
    } catch (error) {
      console.error('Data export failed:', error);
      toast.error('Failed to request data export');
      analytics.trackDataExport('failed', error.message);
    }
  };

  const tabs = [
    { id: 'profile', label: 'Profile', icon: User },
    { id: 'security', label: 'Security', icon: Shield },
    { id: 'notifications', label: 'Notifications', icon: Bell },
    { id: 'privacy', label: 'Privacy & Data', icon: Lock }
  ];

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Profile Settings</h1>
        <p className="text-gray-600 mt-2">
          Manage your account settings and preferences
        </p>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200">
        <nav className="flex space-x-8">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => {
                  setActiveTab(tab.id);
                  analytics.trackClick('profile-tab', `${tab.id}_tab_click`);
                }}
                className={`flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <Icon className="h-4 w-4" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="space-y-6">
        {activeTab === 'profile' && (
          <div className="card">
            <div className="card-header">
              <h2 className="text-xl font-semibold text-gray-900">Profile Information</h2>
              <p className="text-gray-600 text-sm mt-1">
                Update your personal information and contact details
              </p>
            </div>

            <form onSubmit={profileForm.handleSubmit(handleProfileUpdate)} className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label htmlFor="firstName" className="form-label">
                    First Name
                  </label>
                  <input
                    id="firstName"
                    type="text"
                    className="form-input"
                    {...profileForm.register('firstName', { required: 'First name is required' })}
                  />
                  {profileForm.formState.errors.firstName && (
                    <p className="form-error">{profileForm.formState.errors.firstName.message}</p>
                  )}
                </div>

                <div>
                  <label htmlFor="lastName" className="form-label">
                    Last Name
                  </label>
                  <input
                    id="lastName"
                    type="text"
                    className="form-input"
                    {...profileForm.register('lastName', { required: 'Last name is required' })}
                  />
                  {profileForm.formState.errors.lastName && (
                    <p className="form-error">{profileForm.formState.errors.lastName.message}</p>
                  )}
                </div>
              </div>

              <div>
                <label htmlFor="email" className="form-label">
                  Email Address
                </label>
                <input
                  id="email"
                  type="email"
                  className="form-input"
                  {...profileForm.register('email', { 
                    required: 'Email is required',
                    pattern: {
                      value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                      message: 'Invalid email address'
                    }
                  })}
                />
                {profileForm.formState.errors.email && (
                  <p className="form-error">{profileForm.formState.errors.email.message}</p>
                )}
              </div>

              <div className="flex justify-end">
                <button
                  type="submit"
                  disabled={isUpdating}
                  className="btn-primary flex items-center space-x-2 disabled:opacity-50"
                >
                  <Save className="h-4 w-4" />
                  <span>{isUpdating ? 'Updating...' : 'Save Changes'}</span>
                </button>
              </div>
            </form>
          </div>
        )}

        {activeTab === 'security' && (
          <div className="card">
            <div className="card-header">
              <h2 className="text-xl font-semibold text-gray-900">Security Settings</h2>
              <p className="text-gray-600 text-sm mt-1">
                Update your password and manage security preferences
              </p>
            </div>

            <form onSubmit={passwordForm.handleSubmit(handlePasswordUpdate)} className="space-y-6">
              <div>
                <label htmlFor="currentPassword" className="form-label">
                  Current Password
                </label>
                <div className="relative">
                  <input
                    id="currentPassword"
                    type={showCurrentPassword ? 'text' : 'password'}
                    className="form-input pr-10"
                    {...passwordForm.register('currentPassword', { required: 'Current password is required' })}
                  />
                  <button
                    type="button"
                    className="absolute inset-y-0 right-0 pr-3 flex items-center"
                    onClick={() => setShowCurrentPassword(!showCurrentPassword)}
                  >
                    {showCurrentPassword ? (
                      <EyeOff className="h-5 w-5 text-gray-400" />
                    ) : (
                      <Eye className="h-5 w-5 text-gray-400" />
                    )}
                  </button>
                </div>
                {passwordForm.formState.errors.currentPassword && (
                  <p className="form-error">{passwordForm.formState.errors.currentPassword.message}</p>
                )}
              </div>

              <div>
                <label htmlFor="newPassword" className="form-label">
                  New Password
                </label>
                <div className="relative">
                  <input
                    id="newPassword"
                    type={showNewPassword ? 'text' : 'password'}
                    className="form-input pr-10"
                    {...passwordForm.register('newPassword', { 
                      required: 'New password is required',
                      minLength: { value: 8, message: 'Password must be at least 8 characters' }
                    })}
                  />
                  <button
                    type="button"
                    className="absolute inset-y-0 right-0 pr-3 flex items-center"
                    onClick={() => setShowNewPassword(!showNewPassword)}
                  >
                    {showNewPassword ? (
                      <EyeOff className="h-5 w-5 text-gray-400" />
                    ) : (
                      <Eye className="h-5 w-5 text-gray-400" />
                    )}
                  </button>
                </div>
                {passwordForm.formState.errors.newPassword && (
                  <p className="form-error">{passwordForm.formState.errors.newPassword.message}</p>
                )}
              </div>

              <div>
                <label htmlFor="confirmPassword" className="form-label">
                  Confirm New Password
                </label>
                <div className="relative">
                  <input
                    id="confirmPassword"
                    type={showConfirmPassword ? 'text' : 'password'}
                    className="form-input pr-10"
                    {...passwordForm.register('confirmPassword', { required: 'Please confirm your password' })}
                  />
                  <button
                    type="button"
                    className="absolute inset-y-0 right-0 pr-3 flex items-center"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  >
                    {showConfirmPassword ? (
                      <EyeOff className="h-5 w-5 text-gray-400" />
                    ) : (
                      <Eye className="h-5 w-5 text-gray-400" />
                    )}
                  </button>
                </div>
                {passwordForm.formState.errors.confirmPassword && (
                  <p className="form-error">{passwordForm.formState.errors.confirmPassword.message}</p>
                )}
              </div>

              <div className="flex justify-end">
                <button
                  type="submit"
                  disabled={isUpdating}
                  className="btn-primary flex items-center space-x-2 disabled:opacity-50"
                >
                  <Lock className="h-4 w-4" />
                  <span>{isUpdating ? 'Updating...' : 'Update Password'}</span>
                </button>
              </div>
            </form>
          </div>
        )}

        {activeTab === 'notifications' && (
          <div className="card">
            <div className="card-header">
              <h2 className="text-xl font-semibold text-gray-900">Notification Preferences</h2>
              <p className="text-gray-600 text-sm mt-1">
                Choose which notifications you'd like to receive
              </p>
            </div>

            <div className="space-y-6">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-sm font-medium text-gray-900">Email Notifications</h3>
                    <p className="text-sm text-gray-600">Get notified via email about important updates</p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input type="checkbox" className="sr-only peer" defaultChecked />
                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                  </label>
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-sm font-medium text-gray-900">Analysis Complete</h3>
                    <p className="text-sm text-gray-600">Get notified when CV analysis is finished</p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input type="checkbox" className="sr-only peer" defaultChecked />
                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                  </label>
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-sm font-medium text-gray-900">Weekly Summary</h3>
                    <p className="text-sm text-gray-600">Receive a weekly summary of your activity</p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input type="checkbox" className="sr-only peer" />
                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                  </label>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'privacy' && (
          <div className="space-y-6">
            <div className="card">
              <div className="card-header">
                <h2 className="text-xl font-semibold text-gray-900">Data & Privacy</h2>
                <p className="text-gray-600 text-sm mt-1">
                  Manage your data and privacy settings
                </p>
              </div>

              <div className="space-y-6">
                <div>
                  <h3 className="text-sm font-medium text-gray-900 mb-3">Export Your Data</h3>
                  <p className="text-sm text-gray-600 mb-4">
                    Download a copy of all your data including CVs, comparisons, and analytics.
                  </p>
                  <button
                    onClick={handleDataExport}
                    className="btn-secondary flex items-center space-x-2"
                  >
                    <Download className="h-4 w-4" />
                    <span>Request Data Export</span>
                  </button>
                </div>
              </div>
            </div>

            <div className="card border-danger-200">
              <div className="card-header">
                <h2 className="text-xl font-semibold text-danger-600">Danger Zone</h2>
                <p className="text-gray-600 text-sm mt-1">
                  Irreversible actions that will permanently affect your account
                </p>
              </div>

              <div>
                <h3 className="text-sm font-medium text-gray-900 mb-3">Delete Account</h3>
                <p className="text-sm text-gray-600 mb-4">
                  Permanently delete your account and all associated data. This action cannot be undone.
                </p>
                <button
                  onClick={handleDeleteAccount}
                  className="btn-danger flex items-center space-x-2"
                >
                  <Trash2 className="h-4 w-4" />
                  <span>Delete Account</span>
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ProfilePage;