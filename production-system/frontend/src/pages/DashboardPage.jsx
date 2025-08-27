import React, { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { useDropzone } from 'react-dropzone';
import { useForm } from 'react-hook-form';
import { toast } from 'react-hot-toast';

import { cvAPI, jobDescriptionAPI, comparisonAPI } from '../services/api';
// Mock analytics to avoid circular dependency
const analytics = {
  trackClick: () => {},
  trackFileUpload: () => {},
  trackCVUpload: () => {},
  trackFormSubmit: () => {},
  trackError: () => {}
};

const StatPanel = ({ title, value, description, onClick, status = 'info' }) => (
  <div 
    className="panel"
    onClick={() => {
      if (onClick) {
        analytics.trackClick('stat-panel', `${title.toLowerCase()}_panel_click`);
        onClick();
      }
    }}
    style={{ cursor: onClick ? 'pointer' : 'default' }}
  >
    <div className="panel-header">
      <div className="panel-title">
        <span className={`status status-${status}`}>
          <span className="status-dot"></span>
          {title}
        </span>
      </div>
      {onClick && <span style={{ color: '#666666', fontSize: '12px' }}>[VIEW]</span>}
    </div>
    <div className="panel-content">
      <div style={{ fontSize: '32px', fontWeight: '700', marginBottom: '8px' }}>
        {value}
      </div>
      <p style={{ color: '#666666', fontSize: '12px', margin: '0' }}>
        {description}
      </p>
    </div>
  </div>
);

const ActivityItem = ({ activity }) => {
  const getStatusFromType = (type) => {
    switch (type) {
      case 'cv_upload': return 'info';
      case 'jd_created': return 'success';
      case 'comparison': return 'warning';
      default: return 'info';
    }
  };

  const getPrefix = (type) => {
    switch (type) {
      case 'cv_upload': return '[UPLOAD]';
      case 'jd_created': return '[CREATE]';
      case 'comparison': return '[ANALYZE]';
      default: return '[SYSTEM]';
    }
  };

  return (
    <div style={{
      padding: '12px',
      borderBottom: '1px solid #333333',
      display: 'flex',
      alignItems: 'flex-start',
      justifyContent: 'space-between'
    }}>
      <div style={{ flex: '1' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
          <span className={`status status-${getStatusFromType(activity.type)}`}>
            <span className="status-dot"></span>
            {getPrefix(activity.type)}
          </span>
          <span style={{ fontSize: '12px', fontWeight: '500' }}>
            {activity.title}
          </span>
        </div>
        <p style={{ fontSize: '11px', color: '#666666', margin: '0' }}>
          {activity.description}
        </p>
      </div>
      <div style={{ fontSize: '10px', color: '#666666', textAlign: 'right' }}>
        <div>{activity.timestamp}</div>
        {activity.score && (
          <div style={{ marginTop: '2px' }}>
            SCORE: {activity.score}%
          </div>
        )}
      </div>
    </div>
  );
};

const QuickAction = ({ title, description, action, onClick }) => (
  <div style={{
    padding: '16px',
    border: '1px solid #333333',
    marginBottom: '12px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between'
  }}>
    <div>
      <h4 style={{ margin: '0 0 4px 0', fontSize: '13px', fontWeight: '600' }}>
        {title}
      </h4>
      <p style={{ margin: '0', fontSize: '11px', color: '#666666' }}>
        {description}
      </p>
    </div>
    <button 
      className="btn btn-secondary"
      onClick={onClick}
      style={{ fontSize: '10px' }}
    >
      {action}
    </button>
  </div>
);

const JobDescriptionComponent = ({ onSubmit, isSubmitting }) => {
  const [inputType, setInputType] = useState('text');
  const { register, handleSubmit, formState: { errors }, reset, watch } = useForm();

  const watchedInputType = watch('inputType', 'text');
  
  useEffect(() => {
    setInputType(watchedInputType);
  }, [watchedInputType]);

  const onFormSubmit = async (data) => {
    await onSubmit(data);
    reset();
  };

  return (
    <div className="panel">
      <div className="panel-header">
        <div className="panel-title">
          <span className="status status-success">
            <span className="status-dot"></span>
            JOB_INPUT.INTERFACE
          </span>
        </div>
      </div>
      <div className="panel-content">
        <form onSubmit={handleSubmit(onFormSubmit)}>
          {/* Input Type Selection */}
          <div className="form-group" style={{ marginBottom: '16px' }}>
            <label className="form-label">INPUT_METHOD</label>
            <div style={{ display: 'flex', gap: '20px' }}>
              <label style={{ display: 'flex', alignItems: 'center', fontSize: '12px' }}>
                <input
                  type="radio"
                  value="text"
                  {...register('inputType')}
                  style={{ marginRight: '8px' }}
                  defaultChecked
                />
                <span>[MANUAL] Direct Entry</span>
              </label>
              <label style={{ display: 'flex', alignItems: 'center', fontSize: '12px' }}>
                <input
                  type="radio"
                  value="url"
                  {...register('inputType')}
                  style={{ marginRight: '8px' }}
                />
                <span>[WEB] URL Scraping</span>
              </label>
            </div>
          </div>

          {inputType === 'url' ? (
            /* URL Input */
            <div className="form-group">
              <label htmlFor="job-url" className="form-label">
                JOB_POSTING_URL
              </label>
              <input
                id="job-url"
                type="url"
                className={`form-input ${errors.jobUrl ? 'border-color: #ff5f56' : ''}`}
                placeholder="https://company.com/careers/job-id"
                {...register('jobUrl', {
                  required: inputType === 'url' ? 'Job URL is required' : false,
                  pattern: {
                    value: /^https?:\/\/.+/,
                    message: 'Please enter a valid URL'
                  }
                })}
              />
              {errors.jobUrl && (
                <div className="form-error">[ERROR] {errors.jobUrl.message}</div>
              )}
              <p style={{ fontSize: '11px', color: '#666666', marginTop: '4px' }}>
                [AUTO_EXTRACT] Job details will be scraped from URL
              </p>
            </div>
          ) : (
            /* Manual Entry Fields */
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                <div className="form-group">
                  <label htmlFor="job-title" className="form-label">
                    JOB_TITLE *
                  </label>
                  <input
                    id="job-title"
                    type="text"
                    className={`form-input ${errors.jobTitle ? 'border-color: #ff5f56' : ''}`}
                    placeholder="Senior_Software_Engineer"
                    {...register('jobTitle', {
                      required: inputType === 'text' ? 'Job title is required' : false
                    })}
                  />
                  {errors.jobTitle && (
                    <div className="form-error">[ERROR] {errors.jobTitle.message}</div>
                  )}
                </div>

                <div className="form-group">
                  <label htmlFor="company" className="form-label">
                    COMPANY
                  </label>
                  <input
                    id="company"
                    type="text"
                    className="form-input"
                    placeholder="Tech_Corp_Inc"
                    {...register('company')}
                  />
                </div>
              </div>

              <div className="form-group">
                <label htmlFor="job-description" className="form-label">
                  JOB_DESCRIPTION *
                </label>
                <textarea
                  id="job-description"
                  rows={4}
                  className={`form-input form-textarea ${errors.jobDescription ? 'border-color: #ff5f56' : ''}`}
                  placeholder="Enter complete job description..."
                  {...register('jobDescription', {
                    required: inputType === 'text' ? 'Job description is required' : false,
                    minLength: {
                      value: 50,
                      message: 'Job description must be at least 50 characters'
                    }
                  })}
                />
                {errors.jobDescription && (
                  <div className="form-error">[ERROR] {errors.jobDescription.message}</div>
                )}
              </div>
            </div>
          )}

          {/* Submit Button */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '16px' }}>
            <Link
              to="/job-descriptions"
              className="btn btn-secondary"
              style={{ fontSize: '10px', textDecoration: 'none' }}
              onClick={() => analytics.trackLinkClick('/job-descriptions', 'view_all_jobs_from_dashboard')}
            >
              [VIEW_ALL] JOB_SPECS
            </Link>
            <button
              type="submit"
              disabled={isSubmitting}
              className="btn btn-primary"
              style={{ opacity: isSubmitting ? 0.5 : 1, cursor: isSubmitting ? 'not-allowed' : 'pointer' }}
            >
              {isSubmitting ? (
                <span className="loading">
                  <span className="loading-spinner"></span>
                  PROCESSING...
                </span>
              ) : (
                '[ADD] JOB_SPEC'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

const CVUploadComponent = ({ onUpload, isUploading, onUploadSuccess }) => {
  const onDrop = useCallback((acceptedFiles) => {
    if (acceptedFiles.length > 0) {
      analytics.trackFileUpload(acceptedFiles[0].name, acceptedFiles[0].size, 'cv');
      onUpload(acceptedFiles[0]);
    }
  }, [onUpload]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt']
    },
    multiple: false,
    disabled: isUploading
  });

  return (
    <div className="panel">
      <div className="panel-header">
        <div className="panel-title">
          <span className="status status-info">
            <span className="status-dot"></span>
            CV_UPLOAD.INTERFACE
          </span>
        </div>
      </div>
      <div className="panel-content">
        <div
          {...getRootProps()}
          className={`dropzone ${isDragActive ? 'active' : ''}`}
          style={{ 
            opacity: isUploading ? 0.5 : 1,
            cursor: isUploading ? 'not-allowed' : 'pointer',
            minHeight: '100px',
            marginBottom: '12px'
          }}
        >
          <input {...getInputProps()} />
          <div style={{ textAlign: 'center' }}>
            {isUploading ? (
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '8px' }}>
                <div className="loading">
                  <span className="loading-spinner"></span>
                  PROCESSING CV...
                </div>
                <p style={{ fontSize: '11px', color: '#666666' }}>
                  Uploading and analyzing document
                </p>
              </div>
            ) : isDragActive ? (
              <div>
                <p style={{ color: '#ffffff', fontWeight: '600', marginBottom: '8px' }}>
                  [DROP_FILE] Release to upload CV
                </p>
              </div>
            ) : (
              <div>
                <p style={{ marginBottom: '8px' }}>
                  [DRAG_DROP] CV file or [CLICK] to select
                </p>
                <p style={{ fontSize: '11px', color: '#666666' }}>
                  SUPPORTED: PDF, DOC, DOCX, TXT
                </p>
              </div>
            )}
          </div>
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Link
            to="/cvs"
            className="btn btn-secondary"
            style={{ fontSize: '10px', textDecoration: 'none' }}
            onClick={() => analytics.trackLinkClick('/cvs', 'view_all_cvs_from_dashboard')}
          >
            [VIEW_ALL] CV_LIBRARY
          </Link>
        </div>
      </div>
    </div>
  );
};

const DashboardPage = ({ user }) => {
  const [stats, setStats] = useState({
    cvs: 0,
    jobDescriptions: 0,
    comparisons: 0,
    totalAnalyses: 0
  });
  const [recentActivity, setRecentActivity] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isUploading, setIsUploading] = useState(false);
  const [isJobSubmitting, setIsJobSubmitting] = useState(false);

  const loadDashboardData = async () => {
    try {
      setIsLoading(true);
      analytics.trackPageView('/dashboard', 'Dashboard');
      
      // Load statistics
      const [cvsResponse, jdsResponse, comparisonsResponse] = await Promise.all([
        cvAPI.list(),
        jobDescriptionAPI.list(),
        comparisonAPI.list()
      ]);

      setStats({
        cvs: cvsResponse.success ? cvsResponse.cvs.length : 0,
        jobDescriptions: jdsResponse.success ? jdsResponse.job_descriptions.length : 0,
        comparisons: comparisonsResponse.success ? comparisonsResponse.comparisons.length : 0,
        totalAnalyses: comparisonsResponse.success ? comparisonsResponse.comparisons.length : 0
      });

      // Generate recent activity from comparisons
      if (comparisonsResponse.success) {
        const activities = comparisonsResponse.comparisons
          .slice(0, 5)
          .map(comparison => ({
            id: comparison.id,
            type: 'comparison',
            title: 'Gap Analysis Completed',
            description: `Analyzed CV against ${comparison.job_title || 'job description'}`,
            timestamp: new Date(comparison.created_at).toLocaleDateString(),
            score: comparison.analysis_result?.overall_score || null
          }));
        
        setRecentActivity(activities);
      }

    } catch (error) {
      console.error('Failed to load dashboard data:', error);
      analytics.trackError('dashboard_load_error', error.message);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, []);

  const handleCVUpload = async (file) => {
    try {
      setIsUploading(true);
      const response = await cvAPI.upload(file);
      
      if (response.success) {
        toast.success('CV uploaded successfully!');
        analytics.trackCVUpload(file.name, file.size, true);
        // Reload dashboard data to update stats
        loadDashboardData();
      } else {
        throw new Error(response.message || 'Upload failed');
      }
    } catch (error) {
      console.error('Upload failed:', error);
      toast.error(error.message || 'Failed to upload CV');
      analytics.trackCVUpload(file.name, file.size, false, error.message);
    } finally {
      setIsUploading(false);
    }
  };

  const handleJobSubmit = async (data) => {
    try {
      setIsJobSubmitting(true);
      
      const submitData = data.inputType === 'url' ? {
        url: data.jobUrl
      } : {
        text: data.jobDescription,
        title: data.jobTitle,
        company: data.company
      };

      analytics.trackFormSubmit('job_description_form_dashboard', submitData);
      
      const response = await jobDescriptionAPI.create(submitData);
      
      if (response.success) {
        toast.success('Job description added successfully!');
        analytics.trackJobDescriptionCreate(data.inputType, true);
        // Reload dashboard data to update stats
        loadDashboardData();
      } else {
        throw new Error(response.message || 'Failed to create job description');
      }
    } catch (error) {
      console.error('Job submit failed:', error);
      toast.error(error.message || 'Failed to add job description');
      analytics.trackJobDescriptionCreate(data.inputType, false, error.message);
    } finally {
      setIsJobSubmitting(false);
    }
  };


  const quickActions = [
    {
      title: 'START_ANALYSIS',
      description: 'Begin end-to-end CV and job description analysis',
      action: 'ANALYZE',
      onClick: () => window.location.href = '/analysis'
    },
    {
      title: 'VIEW_RESULTS',
      description: 'Review previous analysis results and comparisons',
      action: 'VIEW',
      onClick: () => window.location.href = '/comparisons'
    }
  ];

  if (isLoading) {
    return (
      <div className="container" style={{ padding: '20px' }}>
        <div className="terminal-window">
          <div className="terminal-header">
            <div className="terminal-title">LOADING DASHBOARD...</div>
            <div className="loading">
              <span className="loading-spinner"></span>
            </div>
          </div>
          <div className="terminal-content">
            <p>Initializing system modules...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container" style={{ padding: '20px' }}>
      {/* Header Section */}
      <div className="terminal-window" style={{ marginBottom: '20px' }}>
        <div className="terminal-header">
          <div className="terminal-title">CV_ANALYZER.DASHBOARD</div>
          <div className="terminal-controls">
            <div className="terminal-dot red"></div>
            <div className="terminal-dot yellow"></div>
            <div className="terminal-dot green"></div>
          </div>
        </div>
        <div className="terminal-content">
          <h1 style={{ marginBottom: '8px' }}>SYSTEM OVERVIEW</h1>
          <p style={{ color: '#666666', margin: '0' }}>
            Welcome back, {user?.first_name || 'USER'}. System status: OPERATIONAL
          </p>
        </div>
      </div>

      {/* Statistics Grid */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', 
        gap: '16px',
        marginBottom: '20px'
      }}>
        <StatPanel
          title="CV_FILES"
          value={stats.cvs}
          description="Total CV documents in system"
          onClick={() => window.location.href = '/cvs'}
          status="info"
        />
        <StatPanel
          title="JOB_SPECS"
          value={stats.jobDescriptions}
          description="Job descriptions configured"
          onClick={() => window.location.href = '/job-descriptions'}
          status="success"
        />
        <StatPanel
          title="COMPARISONS"
          value={stats.comparisons}
          description="Analysis processes completed"
          onClick={() => window.location.href = '/comparisons'}
          status="warning"
        />
        <StatPanel
          title="TOTAL_ANALYSES"
          value={stats.totalAnalyses}
          description="All analysis operations"
          status="info"
        />
      </div>

      {/* CV Upload Section */}
      <div style={{ marginBottom: '20px' }}>
        <CVUploadComponent 
          onUpload={handleCVUpload} 
          isUploading={isUploading}
          onUploadSuccess={loadDashboardData}
        />
      </div>

      {/* Job Description Section */}
      <div style={{ marginBottom: '20px' }}>
        <JobDescriptionComponent 
          onSubmit={handleJobSubmit} 
          isSubmitting={isJobSubmitting}
        />
      </div>

      {/* Main Content Grid */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: '1fr 400px', 
        gap: '20px'
      }}>
        {/* Activity Log */}
        <div className="panel">
          <div className="panel-header">
            <div className="panel-title">
              <span className="status status-success">
                <span className="status-dot"></span>
                ACTIVITY_LOG
              </span>
            </div>
            <Link
              to="/comparisons"
              style={{ color: '#666666', fontSize: '11px', textDecoration: 'none' }}
              onClick={() => analytics.trackLinkClick('/comparisons', 'view_all_activity')}
            >
              [VIEW_ALL]
            </Link>
          </div>
          <div className="panel-content" style={{ padding: '0' }}>
            {recentActivity.length > 0 ? (
              recentActivity.map(activity => (
                <ActivityItem key={activity.id} activity={activity} />
              ))
            ) : (
              <div style={{ padding: '20px', textAlign: 'center', color: '#666666' }}>
                <p style={{ margin: '0' }}>[NO_RECENT_ACTIVITY]</p>
                <p style={{ fontSize: '11px', margin: '8px 0 0 0' }}>
                  Upload CV or create job description to begin
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Quick Actions Panel */}
        <div className="panel">
          <div className="panel-header">
            <div className="panel-title">
              <span className="status status-warning">
                <span className="status-dot"></span>
                QUICK_ACTIONS
              </span>
            </div>
          </div>
          <div className="panel-content">
            {quickActions.map((action, index) => (
              <QuickAction key={index} {...action} />
            ))}
          </div>
        </div>
      </div>

      {/* Getting Started Section */}
      {stats.cvs === 0 && stats.jobDescriptions === 0 && (
        <div className="panel" style={{ marginTop: '20px' }}>
          <div className="panel-header">
            <div className="panel-title">
              <span className="status status-info">
                <span className="status-dot"></span>
                SYSTEM_INITIALIZATION
              </span>
            </div>
          </div>
          <div className="panel-content">
            <p style={{ marginBottom: '16px' }}>
              System ready for first-time setup. Start with the analysis interface:
            </p>
            <div style={{ textAlign: 'center' }}>
              <Link
                to="/analysis"
                className="btn btn-primary"
                style={{ 
                  textDecoration: 'none', 
                  fontSize: '14px',
                  padding: '12px 24px',
                  display: 'inline-block'
                }}
                onClick={() => analytics.trackClick('getting-started', 'start_analysis')}
              >
                [START_CV_ANALYSIS] ▶
              </Link>
              <p style={{ fontSize: '11px', color: '#666666', marginTop: '12px' }}>
                Upload CV and job description in one streamlined workflow
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DashboardPage;