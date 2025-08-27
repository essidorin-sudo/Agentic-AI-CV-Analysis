import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { toast } from 'react-hot-toast';

import { jobDescriptionAPI } from '../services/api';
import analytics from '../services/analytics';

const JobDescriptionCard = ({ jobDescription, onView, onDelete, onStartComparison }) => {
  const getStatusColor = (status) => {
    switch (status) {
      case 'processed': return 'status-success';
      case 'processing': return 'status-warning';
      case 'failed': return 'status-error';
      default: return 'status-info';
    }
  };

  const getStatusPrefix = (status) => {
    switch (status) {
      case 'processed': return '[READY]';
      case 'processing': return '[PROC]';
      case 'failed': return '[ERROR]';
      default: return '[PEND]';
    }
  };

  const getSourcePrefix = (sourceType) => {
    return sourceType === 'url' ? '[WEB]' : '[MANUAL]';
  };

  return (
    <div className="panel">
      <div className="panel-header">
        <div className="panel-title">
          <span style={{ fontSize: '12px', fontWeight: '700', textTransform: 'uppercase' }}>
            {(jobDescription.job_title || 'UNTITLED_JOB').length > 18 
              ? (jobDescription.job_title || 'UNTITLED_JOB').substring(0, 18) + '...' 
              : (jobDescription.job_title || 'UNTITLED_JOB')}
          </span>
        </div>
        <div style={{ display: 'flex', gap: '8px' }}>
          <button
            onClick={() => {
              analytics.trackClick('job-view', 'view_job_details');
              onView(jobDescription);
            }}
            className="btn"
            style={{ fontSize: '10px', padding: '4px 8px' }}
            title="View Details"
          >
            [VIEW]
          </button>
          <button
            onClick={() => {
              analytics.trackClick('job-compare', 'start_comparison_from_job');
              onStartComparison(jobDescription);
            }}
            className="btn"
            style={{ fontSize: '10px', padding: '4px 8px' }}
            title="Start Comparison"
            disabled={jobDescription.status !== 'processed'}
          >
            [ANALYZE]
          </button>
          <button
            onClick={() => {
              analytics.trackClick('job-delete', 'delete_job');
              onDelete(jobDescription);
            }}
            className="btn btn-danger"
            style={{ fontSize: '10px', padding: '4px 8px' }}
            title="Delete Job"
          >
            [DEL]
          </button>
        </div>
      </div>
      <div className="panel-content">
        <div style={{ marginBottom: '12px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <span className={`${getStatusColor(jobDescription.status)}`}>
            <span className="status-dot"></span>
            {getStatusPrefix(jobDescription.status)} {jobDescription.status.toUpperCase()}
          </span>
          <span style={{ fontSize: '11px', color: '#666666' }}>
            {getSourcePrefix(jobDescription.source_type)} {new Date(jobDescription.created_at).toLocaleDateString()}
          </span>
        </div>

        {/* Job Details */}
        {jobDescription.parsed_data ? (
          <div style={{ fontSize: '11px' }}>
            {jobDescription.parsed_data.company && (
              <div style={{ marginBottom: '4px', color: '#cccccc' }}>
                COMPANY: {jobDescription.parsed_data.company}
              </div>
            )}
            
            {jobDescription.parsed_data.location && (
              <div style={{ marginBottom: '4px', color: '#cccccc' }}>
                LOCATION: {jobDescription.parsed_data.location}
              </div>
            )}

            {jobDescription.parsed_data.salary && (
              <div style={{ marginBottom: '4px', color: '#cccccc' }}>
                SALARY: {jobDescription.parsed_data.salary}
              </div>
            )}

            {jobDescription.parsed_data.job_type && (
              <div style={{ marginBottom: '4px', color: '#cccccc' }}>
                TYPE: {jobDescription.parsed_data.job_type}
              </div>
            )}

            {jobDescription.parsed_data.required_skills?.length > 0 && (
              <div>
                <div style={{ marginBottom: '4px', color: '#cccccc' }}>
                  REQ_SKILLS: {jobDescription.parsed_data.required_skills.length}
                </div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
                  {jobDescription.parsed_data.required_skills.slice(0, 3).map((skill, index) => (
                    <span 
                      key={index} 
                      style={{ 
                        backgroundColor: '#333333', 
                        color: '#ffffff', 
                        fontSize: '10px', 
                        padding: '2px 6px',
                        border: '1px solid #666666'
                      }}
                    >
                      {skill}
                    </span>
                  ))}
                  {jobDescription.parsed_data.required_skills.length > 3 && (
                    <span style={{ color: '#666666', fontSize: '10px' }}>
                      +{jobDescription.parsed_data.required_skills.length - 3} more
                    </span>
                  )}
                </div>
              </div>
            )}

            {jobDescription.source_url && (
              <div style={{ marginTop: '8px', fontSize: '10px' }}>
                <a 
                  href={jobDescription.source_url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  style={{ color: '#666666', textDecoration: 'none' }}
                  onClick={() => analytics.trackLinkClick(jobDescription.source_url, 'job_source_link')}
                >
                  [SOURCE_URL] {jobDescription.source_url.length > 40 
                    ? jobDescription.source_url.substring(0, 40) + '...' 
                    : jobDescription.source_url}
                </a>
              </div>
            )}
          </div>
        ) : (
          <div style={{ fontSize: '11px', color: '#666666' }}>
            [NO_DATA] Processing incomplete or failed
          </div>
        )}
      </div>
    </div>
  );
};

const CreateJobForm = ({ onSubmit, isSubmitting }) => {
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
    <div className="terminal-window">
      <div className="terminal-header">
        <div className="terminal-title">JOB_INPUT.INTERFACE</div>
        <div className="terminal-controls">
          <div className="terminal-dot red"></div>
          <div className="terminal-dot yellow"></div>
          <div className="terminal-dot green"></div>
        </div>
      </div>
      <div className="terminal-content">
        <div style={{ marginBottom: '20px' }}>
          <h2 style={{ marginBottom: '8px' }}>ADD JOB DESCRIPTION</h2>
          <p style={{ fontSize: '12px', color: '#666666', margin: '0' }}>
            Manual entry or URL scraping for job data extraction
          </p>
        </div>
        <form onSubmit={handleSubmit(onFormSubmit)}>

          {/* Input Type Selection */}
          <div className="form-group">
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

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                <div className="form-group">
                  <label htmlFor="location" className="form-label">
                    LOCATION
                  </label>
                  <input
                    id="location"
                    type="text"
                    className="form-input"
                    placeholder="San_Francisco_CA"
                    {...register('location')}
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="salary" className="form-label">
                    SALARY_RANGE
                  </label>
                  <input
                    id="salary"
                    type="text"
                    className="form-input"
                    placeholder="100000-150000_USD"
                    {...register('salary')}
                  />
                </div>
              </div>

              <div className="form-group">
                <label htmlFor="job-description" className="form-label">
                  JOB_DESCRIPTION *
                </label>
                <textarea
                  id="job-description"
                  rows={8}
                  className={`form-input form-textarea ${errors.jobDescription ? 'border-color: #ff5f56' : ''}`}
                  placeholder="Enter complete job description including responsibilities, requirements, qualifications, benefits..."
                  {...register('jobDescription', {
                    required: inputType === 'text' ? 'Job description is required' : false,
                    minLength: {
                      value: 100,
                      message: 'Job description must be at least 100 characters'
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
          <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '20px' }}>
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
                '[ADD] JOB_DESCRIPTION'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

const JobDetailModal = ({ jobDescription, isOpen, onClose }) => {
  if (!isOpen || !jobDescription) return null;

  const renderSection = (title, data) => {
    if (!data || (Array.isArray(data) && data.length === 0)) return null;

    return (
      <div style={{ marginBottom: '20px' }}>
        <div className="panel">
          <div className="panel-header">
            <div className="panel-title">
              <span className="status status-info">
                <span className="status-dot"></span>
                {title.toUpperCase().replace(' ', '_')}
              </span>
            </div>
          </div>
          <div className="panel-content">
            {Array.isArray(data) ? (
              <div style={{ fontSize: '12px' }}>
                {data.map((item, index) => (
                  <div key={index} style={{ 
                    marginBottom: '8px', 
                    padding: '8px', 
                    backgroundColor: '#0a0a0a', 
                    border: '1px solid #333333' 
                  }}>
                    <p style={{ margin: '0', color: '#cccccc' }}>{item}</p>
                  </div>
                ))}
              </div>
            ) : (
              <div style={{ 
                padding: '12px', 
                backgroundColor: '#0a0a0a', 
                border: '1px solid #333333',
                fontSize: '12px',
                color: '#cccccc',
                whiteSpace: 'pre-wrap'
              }}>
                {String(data)}
              </div>
            )}
          </div>
        </div>
      </div>
    );
  };

  return (
    <div style={{ 
      position: 'fixed', 
      inset: '0', 
      backgroundColor: 'rgba(0, 0, 0, 0.8)', 
      display: 'flex', 
      alignItems: 'center', 
      justifyContent: 'center', 
      zIndex: 50, 
      padding: '20px' 
    }}>
      <div className="terminal-window" style={{ maxWidth: '900px', width: '100%', maxHeight: '90vh' }}>
        {/* Header */}
        <div className="terminal-header">
          <div className="terminal-title">
            JOB_DETAIL.{(jobDescription.job_title || 'UNTITLED').replace(/\s+/g, '_').toUpperCase()}
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div className="terminal-controls">
              <div className="terminal-dot red"></div>
              <div className="terminal-dot yellow"></div>
              <div className="terminal-dot green"></div>
            </div>
            <button
              onClick={onClose}
              className="btn"
              style={{ fontSize: '10px', padding: '4px 8px' }}
            >
              [CLOSE]
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="terminal-content custom-scrollbar" style={{ 
          maxHeight: 'calc(90vh - 60px)', 
          overflowY: 'auto' 
        }}>
          {jobDescription.parsed_data ? (
            <div>
              {/* Job Info */}
              {jobDescription.parsed_data.company && (
                <div style={{ marginBottom: '8px', fontSize: '12px' }}>
                  <span style={{ color: '#cccccc' }}>COMPANY: {jobDescription.parsed_data.company}</span>
                </div>
              )}
              
              {jobDescription.parsed_data.location && (
                <div style={{ marginBottom: '8px', fontSize: '12px' }}>
                  <span style={{ color: '#cccccc' }}>LOCATION: {jobDescription.parsed_data.location}</span>
                </div>
              )}

              {jobDescription.parsed_data.salary && (
                <div style={{ marginBottom: '16px', fontSize: '12px' }}>
                  <span style={{ color: '#cccccc' }}>SALARY: {jobDescription.parsed_data.salary}</span>
                </div>
              )}

              {renderSection('Job Description', jobDescription.parsed_data.description)}
              {renderSection('Responsibilities', jobDescription.parsed_data.responsibilities)}
              {renderSection('Required Skills', jobDescription.parsed_data.required_skills)}
              {renderSection('Preferred Skills', jobDescription.parsed_data.preferred_skills)}
              {renderSection('Qualifications', jobDescription.parsed_data.qualifications)}
              {renderSection('Benefits', jobDescription.parsed_data.benefits)}
            </div>
          ) : (
            <div style={{ textAlign: 'center', padding: '40px 20px' }}>
              <p style={{ color: '#666666', marginBottom: '8px' }}>[NO_DATA] Job parsing incomplete</p>
              <p style={{ fontSize: '11px', color: '#666666' }}>
                Document may still be processing or processing failed
              </p>
            </div>
          )}

          {jobDescription.source_url && (
            <div style={{ 
              marginTop: '20px', 
              paddingTop: '20px', 
              borderTop: '1px solid #333333' 
            }}>
              <div style={{ fontSize: '11px', color: '#666666' }}>
                <span style={{ marginRight: '8px' }}>[SOURCE_URL]</span>
                <a 
                  href={jobDescription.source_url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  style={{ color: '#666666', textDecoration: 'none' }}
                >
                  {jobDescription.source_url}
                </a>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

const JobDescriptionsPage = () => {
  const [jobDescriptions, setJobDescriptions] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [selectedJob, setSelectedJob] = useState(null);
  const [showDetailModal, setShowDetailModal] = useState(false);

  useEffect(() => {
    loadJobDescriptions();
    analytics.trackPageView('/job-descriptions', 'Job Descriptions');
  }, []);

  const loadJobDescriptions = async () => {
    try {
      setIsLoading(true);
      const response = await jobDescriptionAPI.list();
      if (response.success) {
        setJobDescriptions(response.job_descriptions);
      } else {
        toast.error('Failed to load job descriptions');
      }
    } catch (error) {
      console.error('Failed to load job descriptions:', error);
      toast.error('Failed to load job descriptions');
      analytics.trackError('job_load_error', error.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = async (data) => {
    try {
      setIsSubmitting(true);
      
      const submitData = data.inputType === 'url' ? {
        url: data.jobUrl
      } : {
        text: data.jobDescription,
        title: data.jobTitle,
        company: data.company
      };

      analytics.trackFormSubmit('job_description_form', submitData);
      
      const response = await jobDescriptionAPI.create(submitData);
      
      if (response.success) {
        toast.success('Job description added successfully!');
        analytics.trackJobDescriptionCreate(data.inputType, true);
        loadJobDescriptions(); // Reload the list
      } else {
        throw new Error(response.message || 'Failed to create job description');
      }
    } catch (error) {
      console.error('Submit failed:', error);
      toast.error(error.message || 'Failed to add job description');
      analytics.trackJobDescriptionCreate(data.inputType, false, error.message);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = async (jobDescription) => {
    if (!confirm(`Are you sure you want to delete "${jobDescription.job_title || 'this job description'}"?`)) {
      return;
    }

    try {
      const response = await jobDescriptionAPI.delete(jobDescription.id);
      if (response.success) {
        toast.success('Job description deleted successfully');
        setJobDescriptions(jobDescriptions.filter(jd => jd.id !== jobDescription.id));
        analytics.trackJobDescriptionDelete(jobDescription.id, jobDescription.job_title);
      } else {
        toast.error('Failed to delete job description');
      }
    } catch (error) {
      console.error('Delete failed:', error);
      toast.error('Failed to delete job description');
      analytics.trackError('job_delete_error', error.message);
    }
  };

  const handleView = (jobDescription) => {
    setSelectedJob(jobDescription);
    setShowDetailModal(true);
  };

  const handleStartComparison = (jobDescription) => {
    // Navigate to comparisons page with selected job
    window.location.href = `/comparisons?jd_id=${jobDescription.id}`;
  };

  if (isLoading) {
    return (
      <div className="container" style={{ padding: '20px' }}>
        <div className="terminal-window">
          <div className="terminal-header">
            <div className="terminal-title">LOADING JOB_DESCRIPTIONS...</div>
            <div className="loading">
              <span className="loading-spinner"></span>
            </div>
          </div>
          <div className="terminal-content">
            <p>Initializing job management system...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container" style={{ padding: '20px' }}>
      {/* Page Header */}
      <div className="terminal-window" style={{ marginBottom: '20px' }}>
        <div className="terminal-header">
          <div className="terminal-title">JOB_DESCRIPTIONS.SYSTEM</div>
          <div className="terminal-controls">
            <div className="terminal-dot red"></div>
            <div className="terminal-dot yellow"></div>
            <div className="terminal-dot green"></div>
          </div>
        </div>
        <div className="terminal-content">
          <h1 style={{ marginBottom: '8px' }}>JOB MANAGEMENT INTERFACE</h1>
          <p style={{ color: '#666666', margin: '0' }}>
            Create, process, and manage job descriptions for CV analysis and matching
          </p>
        </div>
      </div>

      {/* Create Form */}
      <div style={{ marginBottom: '20px' }}>
        <CreateJobForm onSubmit={handleSubmit} isSubmitting={isSubmitting} />
      </div>

      {/* Job Descriptions List */}
      {jobDescriptions.length > 0 ? (
        <div>
          <div className="panel" style={{ marginBottom: '20px' }}>
            <div className="panel-header">
              <div className="panel-title">
                <span className="status status-success">
                  <span className="status-dot"></span>
                  JOB_REPOSITORY ({jobDescriptions.length} ENTRIES)
                </span>
              </div>
            </div>
          </div>
          
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))', 
            gap: '16px' 
          }}>
            {jobDescriptions.map(jobDescription => (
              <JobDescriptionCard
                key={jobDescription.id}
                jobDescription={jobDescription}
                onView={handleView}
                onDelete={handleDelete}
                onStartComparison={handleStartComparison}
              />
            ))}
          </div>
        </div>
      ) : (
        <div className="panel">
          <div className="panel-header">
            <div className="panel-title">
              <span className="status status-info">
                <span className="status-dot"></span>
                NO_JOB_DESCRIPTIONS
              </span>
            </div>
          </div>
          <div className="panel-content" style={{ textAlign: 'center', padding: '40px 20px' }}>
            <p style={{ marginBottom: '12px', fontSize: '14px', fontWeight: '600' }}>
              [EMPTY_REPOSITORY] No job descriptions in system
            </p>
            <p style={{ marginBottom: '20px', fontSize: '12px', color: '#666666' }}>
              Add job descriptions to enable CV analysis and matching workflows
            </p>
            <div style={{ marginBottom: '16px' }}>
              <p style={{ fontSize: '11px', color: '#666666', marginBottom: '8px' }}>
                AVAILABLE_METHODS:
              </p>
              <div style={{ display: 'flex', justifyContent: 'center', gap: '12px', fontSize: '11px' }}>
                <span>[MANUAL] Direct entry</span>
                <span>[WEB] URL scraping</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Job Detail Modal */}
      <JobDetailModal
        jobDescription={selectedJob}
        isOpen={showDetailModal}
        onClose={() => {
          setShowDetailModal(false);
          setSelectedJob(null);
        }}
      />
    </div>
  );
};

export default JobDescriptionsPage;