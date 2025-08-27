import React, { useState, useEffect, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { toast } from 'react-hot-toast';
import { cvAPI } from '../services/api';

// Mock analytics to avoid circular dependency
const analytics = {
  trackPageView: () => {},
  trackFileUpload: () => {},
  trackClick: () => {},
  trackCVUpload: () => {},
  trackCVDelete: () => {},
  trackError: () => {}
};

const CVLibraryPage = () => {
  const [cvs, setCvs] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isUploading, setIsUploading] = useState(false);

  useEffect(() => {
    loadCVs();
    analytics.trackPageView('/cvs', 'CV Library');
  }, []);

  const loadCVs = async () => {
    try {
      setIsLoading(true);
      const response = await cvAPI.list();
      if (response.success) {
        setCvs(response.cvs);
      } else {
        toast.error('Failed to load CVs');
      }
    } catch (error) {
      console.error('Failed to load CVs:', error);
      toast.error('Failed to load CVs');
      analytics.trackError('cv_load_error', error.message);
    } finally {
      setIsLoading(false);
    }
  };

  const onDrop = useCallback(async (acceptedFiles) => {
    if (acceptedFiles.length > 0) {
      const file = acceptedFiles[0];
      try {
        setIsUploading(true);
        analytics.trackFileUpload(file.name, file.size, 'cv');
        
        const response = await cvAPI.upload(file);
        
        if (response.success) {
          toast.success('CV uploaded successfully!');
          analytics.trackCVUpload(file.name, file.size, true);
          loadCVs(); // Reload the list
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
    }
  }, []);

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

  const handleDelete = async (cv) => {
    if (!confirm(`Are you sure you want to delete "${cv.filename}"?`)) {
      return;
    }

    try {
      const response = await cvAPI.delete(cv.id);
      if (response.success) {
        toast.success('CV deleted successfully');
        setCvs(cvs.filter(c => c.id !== cv.id));
        analytics.trackCVDelete(cv.id, cv.filename);
      } else {
        toast.error('Failed to delete CV');
      }
    } catch (error) {
      console.error('Delete failed:', error);
      toast.error('Failed to delete CV');
      analytics.trackError('cv_delete_error', error.message);
    }
  };

  if (isLoading) {
    return (
      <div className="container" style={{ padding: '20px' }}>
        <div className="terminal-window">
          <div className="terminal-header">
            <div className="terminal-title">LOADING CV_LIBRARY...</div>
            <div className="loading">
              <span className="loading-spinner"></span>
            </div>
          </div>
          <div className="terminal-content">
            <p>Initializing CV management system...</p>
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
          <div className="terminal-title">CV_LIBRARY.SYSTEM</div>
          <div className="terminal-controls">
            <div className="terminal-dot red"></div>
            <div className="terminal-dot yellow"></div>
            <div className="terminal-dot green"></div>
          </div>
        </div>
        <div className="terminal-content">
          <h1 style={{ marginBottom: '8px' }}>CV MANAGEMENT INTERFACE</h1>
          <p style={{ color: '#666666', margin: '0' }}>
            Upload, process, and manage CV documents for analysis and job matching
          </p>
        </div>
      </div>

      {/* Upload Area */}
      <div className="terminal-window" style={{ marginBottom: '20px' }}>
        <div className="terminal-header">
          <div className="terminal-title">CV_UPLOAD.INTERFACE</div>
          <div className="terminal-controls">
            <div className="terminal-dot red"></div>
            <div className="terminal-dot yellow"></div>
            <div className="terminal-dot green"></div>
          </div>
        </div>
        <div className="terminal-content">
          <div
            {...getRootProps()}
            className={`dropzone ${isDragActive ? 'active' : ''}`}
            style={{ 
              opacity: isUploading ? 0.5 : 1,
              cursor: isUploading ? 'not-allowed' : 'pointer',
              minHeight: '120px'
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
        </div>
      </div>

      {/* CVs List */}
      {cvs.length > 0 ? (
        <div>
          <div className="panel" style={{ marginBottom: '20px' }}>
            <div className="panel-header">
              <div className="panel-title">
                <span className="status status-success">
                  <span className="status-dot"></span>
                  CV_REPOSITORY ({cvs.length} FILES)
                </span>
              </div>
            </div>
          </div>
          
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))', 
            gap: '16px' 
          }}>
            {cvs.map(cv => (
              <div key={cv.id} className="panel">
                <div className="panel-header">
                  <div className="panel-title">
                    <span style={{ fontSize: '12px', fontWeight: '700', textTransform: 'uppercase' }}>
                      {cv.filename.length > 20 ? cv.filename.substring(0, 20) + '...' : cv.filename}
                    </span>
                  </div>
                  <div style={{ display: 'flex', gap: '8px' }}>
                    <button
                      onClick={() => handleDelete(cv)}
                      className="btn btn-danger"
                      style={{ fontSize: '10px', padding: '4px 8px' }}
                      title="Delete CV"
                    >
                      [DEL]
                    </button>
                  </div>
                </div>
                <div className="panel-content">
                  <div style={{ marginBottom: '12px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <span className={`status-${cv.status || 'info'}`}>
                      <span className="status-dot"></span>
                      [{cv.status ? cv.status.toUpperCase() : 'PENDING'}]
                    </span>
                    <span style={{ fontSize: '11px', color: '#666666' }}>
                      {new Date(cv.uploaded_at).toLocaleDateString()}
                    </span>
                  </div>
                  
                  <div style={{ fontSize: '11px', color: '#666666' }}>
                    [FILE_INFO] Ready for analysis
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div className="panel">
          <div className="panel-header">
            <div className="panel-title">
              <span className="status status-info">
                <span className="status-dot"></span>
                NO_CV_FILES
              </span>
            </div>
          </div>
          <div className="panel-content" style={{ textAlign: 'center', padding: '40px 20px' }}>
            <p style={{ marginBottom: '12px', fontSize: '14px', fontWeight: '600' }}>
              [EMPTY_REPOSITORY] No CV files in system
            </p>
            <p style={{ marginBottom: '20px', fontSize: '12px', color: '#666666' }}>
              Upload CV documents to begin analysis and job matching processes
            </p>
            <div style={{ marginBottom: '16px' }}>
              <p style={{ fontSize: '11px', color: '#666666', marginBottom: '8px' }}>
                SUPPORTED_FORMATS:
              </p>
              <div style={{ display: 'flex', justifyContent: 'center', gap: '12px', fontSize: '11px' }}>
                <span>[PDF]</span>
                <span>[DOC]</span>
                <span>[DOCX]</span>
                <span>[TXT]</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CVLibraryPage;