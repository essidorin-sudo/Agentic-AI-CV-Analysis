import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { toast } from 'react-hot-toast';
import { cvAPI, jobDescriptionAPI, comparisonAPI } from '../services/api';

// Mock analytics to avoid circular dependency
const analytics = {
  trackPageView: () => {},
  trackFileUpload: () => {},
  trackClick: () => {},
  trackComparison: () => {},
  trackError: () => {}
};

const AnalysisPage = () => {
  const [step, setStep] = useState('cv_upload'); // cv_upload, jd_upload, analyze, results
  const [cvFile, setCvFile] = useState(null);
  const [cvData, setCvData] = useState(null);
  const [jdData, setJdData] = useState(null);
  const [jobDescription, setJobDescription] = useState('');
  const [jobUrl, setJobUrl] = useState('');
  const [inputType, setInputType] = useState('text'); // text or url
  const [isProcessing, setIsProcessing] = useState(false);
  const [analysisResults, setAnalysisResults] = useState(null);
  const [progress, setProgress] = useState(0);
  const [currentTask, setCurrentTask] = useState('');

  // CV Upload handlers
  const onCVDrop = useCallback(async (acceptedFiles) => {
    if (acceptedFiles.length > 0) {
      const file = acceptedFiles[0];
      setCvFile(file);
      
      try {
        setIsProcessing(true);
        setCurrentTask('Processing CV...');
        setProgress(25);
        
        const response = await cvAPI.upload(file);
        
        if (response.success) {
          setCvData(response.cv);
          setProgress(50);
          setStep('jd_upload'); // Progress to JD upload step
          toast.success('CV processed successfully! Now add job description.');
          analytics.trackFileUpload(file.name, file.size, 'cv');
        } else {
          throw new Error(response.message || 'CV processing failed');
        }
      } catch (error) {
        console.error('CV processing failed:', error);
        toast.error(error.message || 'Failed to process CV');
        analytics.trackError('cv_processing_error', error.message);
      } finally {
        setIsProcessing(false);
        setCurrentTask('');
        setProgress(0);
      }
    }
  }, []);

  const { getRootProps: getCVRootProps, getInputProps: getCVInputProps, isDragActive: isCVDragActive } = useDropzone({
    onDrop: onCVDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt']
    },
    multiple: false,
    disabled: isProcessing
  });

  // Job Description handlers
  const handleJobSubmit = async () => {
    if (!jobDescription.trim() && !jobUrl.trim()) {
      toast.error('Please enter job description or URL');
      return;
    }

    try {
      setIsProcessing(true);
      setCurrentTask('Processing Job Description...');
      setProgress(25);

      const submitData = inputType === 'url' ? {
        url: jobUrl.trim()
      } : {
        text: jobDescription.trim(),
        title: 'Manual Entry',
        company: 'Various'
      };

      const response = await jobDescriptionAPI.create(submitData);
      
      if (response.success) {
        setJdData(response.job_description);
        setProgress(50);
        setStep('analyze'); // Progress to analysis step
        toast.success('Job description processed! Ready for analysis.');
        return response.job_description;
      } else {
        throw new Error(response.message || 'Job description processing failed');
      }
    } catch (error) {
      console.error('Job description processing failed:', error);
      
      // Enhanced error handling for URL scraping failures
      if (inputType === 'url' && error.message && error.message.includes('URL')) {
        toast.error('URL scraping failed. Please try copying the job description text directly instead.', {
          duration: 6000
        });
        // Automatically switch to text input mode for user convenience
        setInputType('text');
      } else {
        toast.error(error.message || 'Failed to process job description');
      }
      
      analytics.trackError('jd_processing_error', error.message);
      throw error;
    } finally {
      setIsProcessing(false);
      setCurrentTask('');
      setProgress(0);
    }
  };

  // Analysis workflow
  const runAnalysis = async () => {
    if (!cvData || !jdData) {
      toast.error('Please complete CV and job description steps first');
      return;
    }

    try {
      setIsProcessing(true);
      setStep('results');
      setProgress(0);
      
      // Run Comparison Analysis
      setCurrentTask('Running Gap Analysis...');
      setProgress(30);
      
      const comparisonData = {
        cv_id: cvData.id,
        job_description_id: jdData.id
      };
      
      let analysisResponse = await comparisonAPI.create(comparisonData);
      
      // Handle case where data is not ready yet (retry once after delay)
      const hasEmptyResults = analysisResponse.success && (
        analysisResponse.comparison.match_score === 0 ||
        !analysisResponse.comparison.highlighted_content ||
        !analysisResponse.comparison.highlighted_content.cv_highlighted ||
        !analysisResponse.comparison.highlighted_content.jd_highlighted
      );
      
      if (hasEmptyResults) {
        setCurrentTask('Waiting for data processing...');
        setProgress(50);
        
        // Wait 3 seconds and retry
        await new Promise(resolve => setTimeout(resolve, 3000));
        
        setCurrentTask('Retrying analysis...');
        setProgress(70);
        
        analysisResponse = await comparisonAPI.create(comparisonData);
      }
      
      if (analysisResponse.success) {
        setProgress(100);
        setCurrentTask('Analysis Complete!');
        setAnalysisResults(analysisResponse.comparison);
        toast.success('Analysis completed successfully!');
        analytics.trackComparison(cvData.id, jdData.id, analysisResponse.comparison.match_score);
      } else {
        throw new Error(analysisResponse.message || 'Analysis failed');
      }
    } catch (error) {
      console.error('Analysis failed:', error);
      toast.error(error.message || 'Analysis failed');
      analytics.trackError('analysis_error', error.message);
      setStep('analyze');
    } finally {
      setIsProcessing(false);
      setCurrentTask('');
      setProgress(0);
    }
  };

  const resetAnalysis = () => {
    setStep('cv_upload');
    setCvFile(null);
    setCvData(null);
    setJdData(null);
    setJobDescription('');
    setJobUrl('');
    setAnalysisResults(null);
    setProgress(0);
    setCurrentTask('');
  };

  const renderCVUploadStep = () => (
    <div className="terminal-window">
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
          {...getCVRootProps()}
          className={`dropzone ${isCVDragActive ? 'active' : ''}`}
          style={{ 
            opacity: isProcessing ? 0.5 : 1,
            cursor: isProcessing ? 'not-allowed' : 'pointer',
            minHeight: '200px'
          }}
        >
          <input {...getCVInputProps()} />
          <div style={{ textAlign: 'center' }}>
            {cvData ? (
              <div>
                <div style={{ color: '#00ff00', marginBottom: '12px', fontSize: '14px' }}>
                  ✓ [CV_PROCESSED] {cvFile?.name}
                </div>
                <div style={{ fontSize: '11px', color: '#666666' }}>
                  CV successfully processed! Proceed to job description step.
                </div>
              </div>
            ) : isProcessing ? (
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '8px' }}>
                <div className="loading">
                  <span className="loading-spinner"></span>
                  PROCESSING CV...
                </div>
                <p style={{ fontSize: '11px', color: '#666666' }}>
                  Analyzing document structure and content
                </p>
              </div>
            ) : isCVDragActive ? (
              <div>
                <p style={{ color: '#ffffff', fontWeight: '600', marginBottom: '8px' }}>
                  [DROP_FILE] Release to upload CV
                </p>
              </div>
            ) : (
              <div>
                <p style={{ marginBottom: '8px', fontSize: '16px' }}>
                  [STEP_1] Upload your CV to begin analysis
                </p>
                <p style={{ fontSize: '11px', color: '#666666', marginBottom: '12px' }}>
                  SUPPORTED: PDF, DOC, DOCX, TXT
                </p>
                <div style={{ fontSize: '10px', color: '#888888' }}>
                  Drag and drop your resume file or click to select
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );

  const renderJDUploadStep = () => (
    <div>
      <div className="terminal-window" style={{ marginBottom: '20px' }}>
        <div className="terminal-header">
          <div className="terminal-title">JOB_DESCRIPTION.INPUT</div>
          <div className="terminal-controls">
            <div className="terminal-dot red"></div>
            <div className="terminal-dot yellow"></div>
            <div className="terminal-dot green"></div>
          </div>
        </div>
        <div className="terminal-content">
          {/* Input Type Toggle */}
          <div style={{ marginBottom: '16px' }}>
            <div style={{ display: 'flex', gap: '8px', marginBottom: '8px' }}>
              <button
                onClick={() => setInputType('text')}
                className={`btn ${inputType === 'text' ? 'btn-primary' : ''}`}
                style={{ fontSize: '10px', padding: '4px 12px' }}
              >
                [TEXT]
              </button>
              <button
                onClick={() => setInputType('url')}
                className={`btn ${inputType === 'url' ? 'btn-primary' : ''}`}
                style={{ fontSize: '10px', padding: '4px 12px' }}
              >
                [URL]
              </button>
            </div>
          </div>

          {inputType === 'text' ? (
            <div>
              <textarea
                value={jobDescription}
                onChange={(e) => setJobDescription(e.target.value)}
                className="form-input"
                rows={8}
                placeholder="Paste job description content here..."
                style={{ 
                  width: '100%', 
                  resize: 'vertical',
                  fontFamily: 'monospace',
                  fontSize: '11px'
                }}
              />
              <div style={{ fontSize: '10px', color: '#666666', marginTop: '8px' }}>
                Copy and paste the complete job description for analysis
              </div>
            </div>
          ) : (
            <div>
              <input
                type="url"
                value={jobUrl}
                onChange={(e) => setJobUrl(e.target.value)}
                className="form-input"
                placeholder="https://company.com/job-posting"
                style={{ width: '100%', marginBottom: '8px' }}
              />
              <div style={{ fontSize: '10px', color: '#666666' }}>
                Enter job posting URL for automatic content extraction<br/>
                If URL scraping fails, switch to [TEXT] mode and paste content manually
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Submit JD Button */}
      <div className="panel">
        <div className="panel-content" style={{ textAlign: 'center', padding: '20px' }}>
          <button
            onClick={handleJobSubmit}
            disabled={isProcessing || (!jobDescription.trim() && !jobUrl.trim())}
            className="btn btn-primary"
            style={{ fontSize: '14px', padding: '12px 24px' }}
          >
            {isProcessing ? 'PROCESSING...' : '[PROCESS_JOB_DESCRIPTION] ▶'}
          </button>
          <div style={{ fontSize: '11px', color: '#666666', marginTop: '8px' }}>
            Process job description to enable analysis
          </div>
        </div>
      </div>
    </div>
  );

  const renderAnalyzeStep = () => (
    <div className="panel">
      <div className="panel-header">
        <div className="panel-title">
          <span className="status status-success">
            <span className="status-dot"></span>
            READY_FOR_ANALYSIS
          </span>
        </div>
      </div>
      <div className="panel-content" style={{ textAlign: 'center', padding: '40px' }}>
        <div style={{ marginBottom: '20px' }}>
          <div style={{ fontSize: '14px', marginBottom: '12px' }}>
            ✓ CV processed: {cvFile?.name}
          </div>
          <div style={{ fontSize: '14px', marginBottom: '20px' }}>
            ✓ Job description processed
          </div>
        </div>
        <button
          onClick={runAnalysis}
          disabled={isProcessing}
          className="btn btn-primary"
          style={{ fontSize: '16px', padding: '16px 32px' }}
        >
          {isProcessing ? 'ANALYZING...' : '[START_ANALYSIS] ▶'}
        </button>
        <div style={{ fontSize: '11px', color: '#666666', marginTop: '12px' }}>
          Execute comprehensive CV-Job Description matching analysis
        </div>
      </div>
    </div>
  );

  const renderAnalysisStep = () => (
    <div className="terminal-window">
      <div className="terminal-header">
        <div className="terminal-title">ANALYSIS_ENGINE.PROCESSING</div>
        <div className="terminal-controls">
          <div className="terminal-dot red"></div>
          <div className="terminal-dot yellow"></div>
          <div className="terminal-dot green"></div>
        </div>
      </div>
      <div className="terminal-content" style={{ textAlign: 'center', padding: '40px 20px' }}>
        <div className="loading" style={{ marginBottom: '20px' }}>
          <span className="loading-spinner"></span>
          {currentTask}
        </div>
        
        <div style={{ marginBottom: '20px' }}>
          <div style={{ 
            width: '100%', 
            height: '8px', 
            backgroundColor: '#333333',
            border: '1px solid #666666',
            marginBottom: '8px'
          }}>
            <div style={{
              width: `${progress}%`,
              height: '100%',
              backgroundColor: '#00ff00',
              transition: 'width 0.3s ease'
            }}></div>
          </div>
          <div style={{ fontSize: '12px', color: '#666666' }}>
            PROGRESS: {progress}%
          </div>
        </div>

        <div style={{ fontSize: '11px', color: '#666666' }}>
          <p>• Parsing CV structure and extracting key information</p>
          <p>• Processing job description requirements</p>
          <p>• Running intelligent matching algorithms</p>
          <p>• Generating comprehensive gap analysis</p>
        </div>
      </div>
    </div>
  );

  const renderResultsStep = () => (
    <div style={{ display: 'grid', gap: '20px' }}>
      {/* Results Header */}
      <div className="terminal-window">
        <div className="terminal-header">
          <div className="terminal-title">ANALYSIS_RESULTS.COMPLETE</div>
          <div style={{ display: 'flex', gap: '8px' }}>
            <button
              onClick={resetAnalysis}
              className="btn btn-secondary"
              style={{ fontSize: '10px', padding: '4px 8px' }}
            >
              [NEW_ANALYSIS]
            </button>
            <div className="terminal-controls">
              <div className="terminal-dot red"></div>
              <div className="terminal-dot yellow"></div>
              <div className="terminal-dot green"></div>
            </div>
          </div>
        </div>
        <div className="terminal-content">
          {!analysisResults ? (
            <div style={{ textAlign: 'center', padding: '40px 20px' }}>
              <div className="loading" style={{ marginBottom: '20px' }}>
                <span className="loading-spinner"></span>
                {currentTask || 'Loading analysis results...'}
              </div>
              <div style={{ fontSize: '11px', color: '#666666' }}>
                Analysis in progress - results will appear when ready
              </div>
            </div>
          ) : (
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '20px', textAlign: 'center' }}>
              <div>
                <div style={{ fontSize: '24px', color: '#00ff00', marginBottom: '4px' }}>
                  {Math.round(analysisResults.match_score)}%
                </div>
                <div style={{ fontSize: '11px', color: '#666666' }}>OVERALL MATCH</div>
              </div>
              <div>
                <div style={{ fontSize: '24px', color: '#ffff00', marginBottom: '4px' }}>
                  {Math.round(analysisResults.gap_analysis?.match_score?.skills_score || 0)}%
                </div>
                <div style={{ fontSize: '11px', color: '#666666' }}>SKILLS MATCH</div>
              </div>
              <div>
                <div style={{ fontSize: '24px', color: '#ff6666', marginBottom: '4px' }}>
                  {Math.round(analysisResults.gap_analysis?.match_score?.experience_score || 0)}%
                </div>
                <div style={{ fontSize: '11px', color: '#666666' }}>EXPERIENCE MATCH</div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Detailed Analysis */}
      {analysisResults?.gap_analysis && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
          {/* Strengths and Gaps */}
          <div className="panel">
            <div className="panel-header">
              <div className="panel-title">
                <span className="status status-success">
                  <span className="status-dot"></span>
                  ANALYSIS_SUMMARY
                </span>
              </div>
            </div>
            <div className="panel-content">
              {analysisResults.gap_analysis.match_score?.strengths && (
                <div style={{ marginBottom: '16px' }}>
                  <div style={{ fontSize: '13px', fontWeight: '600', marginBottom: '8px', color: '#00ff00' }}>
                    [STRENGTHS]
                  </div>
                  <ul style={{ fontSize: '11px', lineHeight: '1.6', paddingLeft: '16px' }}>
                    {analysisResults.gap_analysis.match_score.strengths.map((strength, index) => (
                      <li key={index} style={{ marginBottom: '4px' }}>{strength}</li>
                    ))}
                  </ul>
                </div>
              )}
              {analysisResults.gap_analysis.match_score?.gaps && (
                <div>
                  <div style={{ fontSize: '13px', fontWeight: '600', marginBottom: '8px', color: '#ff6666' }}>
                    [GAPS]
                  </div>
                  <ul style={{ fontSize: '11px', lineHeight: '1.6', paddingLeft: '16px' }}>
                    {analysisResults.gap_analysis.match_score.gaps.map((gap, index) => (
                      <li key={index} style={{ marginBottom: '4px' }}>{gap}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>

          {/* Recommendations */}
          <div className="panel">
            <div className="panel-header">
              <div className="panel-title">
                <span className="status status-warning">
                  <span className="status-dot"></span>
                  RECOMMENDATIONS
                </span>
              </div>
            </div>
            <div className="panel-content">
              {analysisResults.gap_analysis.match_score?.recommendations && (
                <ul style={{ fontSize: '11px', lineHeight: '1.6', paddingLeft: '16px' }}>
                  {analysisResults.gap_analysis.match_score.recommendations.map((rec, index) => (
                    <li key={index} style={{ marginBottom: '8px' }}>{rec}</li>
                  ))}
                </ul>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Side-by-side highlighted content */}
      {analysisResults?.highlighted_content && (
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: '1fr 1fr', 
          gap: '20px', 
          marginTop: '20px',
          alignItems: 'start',
          minHeight: 'fit-content'
        }}>
          {/* CV Highlighted */}
          <div className="panel">
            <div className="panel-header">
              <div className="panel-title">
                <span className="status status-info">
                  <span className="status-dot"></span>
                  CV_ANALYSIS
                </span>
              </div>
            </div>
            <div className="panel-content">
              {analysisResults.highlighted_content.cv_highlighted ? (
                <div 
                  dangerouslySetInnerHTML={{ __html: analysisResults.highlighted_content.cv_highlighted }}
                />
              ) : (
                <div style={{ fontSize: '11px', color: '#666666', fontStyle: 'italic' }}>
                  CV highlighting not available
                </div>
              )}
            </div>
          </div>

          {/* JD Highlighted */}
          <div className="panel">
            <div className="panel-header">
              <div className="panel-title">
                <span className="status status-success">
                  <span className="status-dot"></span>
                  JOB_DESCRIPTION_ANALYSIS
                </span>
              </div>
            </div>
            <div className="panel-content">
              {analysisResults.highlighted_content.jd_highlighted ? (
                <div 
                  dangerouslySetInnerHTML={{ __html: analysisResults.highlighted_content.jd_highlighted }}
                />
              ) : (
                <div style={{ fontSize: '11px', color: '#666666', fontStyle: 'italic' }}>
                  Job description highlighting not available
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );


  return (
    <div className="container" style={{ padding: '20px' }}>
      {/* Page Header */}
      <div className="terminal-window" style={{ marginBottom: '20px' }}>
        <div className="terminal-header">
          <div className="terminal-title">CV_JD_ANALYSIS.SYSTEM</div>
          <div className="terminal-controls">
            <div className="terminal-dot red"></div>
            <div className="terminal-dot yellow"></div>
            <div className="terminal-dot green"></div>
          </div>
        </div>
        <div className="terminal-content">
          <h1 style={{ marginBottom: '8px' }}>INTELLIGENT CV-JOB MATCHING INTERFACE</h1>
          <p style={{ color: '#666666', margin: '0' }}>
            Upload your CV and job description for comprehensive gap analysis and matching insights
          </p>
        </div>
      </div>

      {/* Step Indicator */}
      <div className="panel" style={{ marginBottom: '20px' }}>
        <div className="panel-content">
          <div style={{ display: 'flex', gap: '20px' }}>
            <span className={step === 'cv_upload' ? 'status-warning' : cvData ? 'status-success' : 'status-info'}>
              <span className="status-dot"></span>
              [STEP_1] UPLOAD_CV
            </span>
            <span className={step === 'jd_upload' ? 'status-warning' : jdData ? 'status-success' : 'status-info'}>
              <span className="status-dot"></span>
              [STEP_2] ADD_JOB_DESCRIPTION
            </span>
            <span className={step === 'analyze' ? 'status-warning' : step === 'results' ? 'status-success' : 'status-info'}>
              <span className="status-dot"></span>
              [STEP_3] RUN_ANALYSIS
            </span>
            <span className={step === 'results' ? 'status-success' : 'status-info'}>
              <span className="status-dot"></span>
              [STEP_4] VIEW_RESULTS
            </span>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div style={{ marginBottom: '20px' }}>
        {step === 'cv_upload' && renderCVUploadStep()}
        {step === 'jd_upload' && renderJDUploadStep()}
        {step === 'analyze' && renderAnalyzeStep()}
        {step === 'results' && renderResultsStep()}
      </div>
    </div>
  );
};

export default AnalysisPage;