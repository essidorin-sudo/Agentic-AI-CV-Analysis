import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { toast } from 'react-hot-toast';
import { 
  BarChart3, 
  Play, 
  Eye, 
  Trash2, 
  Calendar,
  User,
  Building,
  Target,
  TrendingUp,
  AlertCircle,
  CheckCircle,
  Clock,
  FileText,
  Upload,
  Plus,
  Download
} from 'lucide-react';

import { cvAPI, jobDescriptionAPI, comparisonAPI } from '../services/api';
import analytics from '../services/analytics';

const ScoreCard = ({ score, label, color }) => (
  <div className="text-center">
    <div className={`text-3xl font-bold ${color}`}>{score}%</div>
    <div className="text-sm text-gray-600 mt-1">{label}</div>
  </div>
);

const ComparisonCard = ({ comparison, onView, onDelete }) => {
  const getScoreColor = (score) => {
    if (score >= 80) return 'text-success-600';
    if (score >= 60) return 'text-warning-600';
    return 'text-danger-600';
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'status-success';
      case 'processing': return 'status-warning';
      case 'failed': return 'status-danger';
      default: return 'status-info';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed': return CheckCircle;
      case 'processing': return Clock;
      case 'failed': return AlertCircle;
      default: return BarChart3;
    }
  };

  const StatusIcon = getStatusIcon(comparison.status);
  const overallScore = comparison.analysis_result?.overall_score || 0;

  return (
    <div className="card hover:shadow-md transition-shadow duration-200">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          {/* Header */}
          <div className="flex items-start space-x-3">
            <div className="p-2 bg-purple-100 rounded-lg">
              <BarChart3 className="h-6 w-6 text-purple-600" />
            </div>
            <div className="flex-1 min-w-0">
              <h3 className="text-lg font-medium text-gray-900 truncate">
                {comparison.job_title || 'Untitled Comparison'}
              </h3>
              <div className="flex items-center space-x-2 mt-1">
                <span className={`${getStatusColor(comparison.status)}`}>
                  <StatusIcon className="h-3 w-3 mr-1" />
                  {comparison.status}
                </span>
                <span className="text-sm text-gray-500">
                  {new Date(comparison.created_at).toLocaleDateString()}
                </span>
              </div>
            </div>
          </div>

          {/* Details */}
          <div className="mt-4 space-y-2">
            {comparison.cv_filename && (
              <div className="flex items-center text-sm text-gray-600">
                <User className="h-4 w-4 mr-2" />
                {comparison.cv_filename}
              </div>
            )}
            
            {comparison.company && (
              <div className="flex items-center text-sm text-gray-600">
                <Building className="h-4 w-4 mr-2" />
                {comparison.company}
              </div>
            )}

            {comparison.status === 'completed' && comparison.analysis_result && (
              <div className="mt-3 p-3 bg-gray-50 rounded-lg">
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium text-gray-700">Overall Match</span>
                  <span className={`text-lg font-bold ${getScoreColor(overallScore)}`}>
                    {overallScore}%
                  </span>
                </div>
                
                {comparison.analysis_result.scores && (
                  <div className="grid grid-cols-3 gap-4 mt-3 text-xs">
                    <ScoreCard 
                      score={comparison.analysis_result.scores.skills || 0}
                      label="Skills"
                      color={getScoreColor(comparison.analysis_result.scores.skills || 0)}
                    />
                    <ScoreCard 
                      score={comparison.analysis_result.scores.experience || 0}
                      label="Experience"
                      color={getScoreColor(comparison.analysis_result.scores.experience || 0)}
                    />
                    <ScoreCard 
                      score={comparison.analysis_result.scores.education || 0}
                      label="Education"
                      color={getScoreColor(comparison.analysis_result.scores.education || 0)}
                    />
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Actions */}
        <div className="flex flex-col space-y-2 ml-4">
          <button
            onClick={() => {
              analytics.trackClick('comparison-view', 'view_comparison_details');
              onView(comparison);
            }}
            className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
            title="View Details"
          >
            <Eye className="h-4 w-4" />
          </button>
          <button
            onClick={() => {
              analytics.trackClick('comparison-delete', 'delete_comparison');
              onDelete(comparison);
            }}
            className="p-2 text-danger-600 hover:text-danger-900 hover:bg-danger-50 rounded-lg transition-colors"
            title="Delete Comparison"
          >
            <Trash2 className="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
  );
};

const CreateComparisonForm = ({ onSubmit, isSubmitting, preSelectedCVId, preSelectedJDId }) => {
  const [cvs, setCvs] = useState([]);
  const [jobDescriptions, setJobDescriptions] = useState([]);
  const [selectedCV, setSelectedCV] = useState(preSelectedCVId || '');
  const [selectedJD, setSelectedJD] = useState(preSelectedJDId || '');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [cvsResponse, jdsResponse] = await Promise.all([
        cvAPI.list(),
        jobDescriptionAPI.list()
      ]);

      if (cvsResponse.success) {
        setCvs(cvsResponse.cvs.filter(cv => cv.status === 'processed'));
      }
      if (jdsResponse.success) {
        setJobDescriptions(jdsResponse.job_descriptions.filter(jd => jd.status === 'processed'));
      }
    } catch (error) {
      console.error('Failed to load data:', error);
      toast.error('Failed to load CVs and job descriptions');
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!selectedCV || !selectedJD) {
      toast.error('Please select both a CV and job description');
      return;
    }
    onSubmit({ cv_id: selectedCV, job_description_id: selectedJD });
  };

  return (
    <form onSubmit={handleSubmit} className="card space-y-6">
      <div className="card-header">
        <h2 className="text-xl font-semibold text-gray-900">Create New Comparison</h2>
        <p className="text-gray-600 text-sm mt-1">
          Select a CV and job description to analyze compatibility and identify gaps.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* CV Selection */}
        <div>
          <label htmlFor="cv-select" className="form-label">
            Select CV
          </label>
          <select
            id="cv-select"
            value={selectedCV}
            onChange={(e) => setSelectedCV(e.target.value)}
            className="form-input"
            required
          >
            <option value="">Choose a CV...</option>
            {cvs.map(cv => (
              <option key={cv.id} value={cv.id}>
                {cv.filename} {cv.parsed_data?.personal_information?.name ? `(${cv.parsed_data.personal_information.name})` : ''}
              </option>
            ))}
          </select>
          {cvs.length === 0 && (
            <p className="text-sm text-gray-500 mt-1">
              No processed CVs available. <a href="/cvs" className="text-primary-600 hover:underline">Upload a CV first</a>.
            </p>
          )}
        </div>

        {/* Job Description Selection */}
        <div>
          <label htmlFor="jd-select" className="form-label">
            Select Job Description
          </label>
          <select
            id="jd-select"
            value={selectedJD}
            onChange={(e) => setSelectedJD(e.target.value)}
            className="form-input"
            required
          >
            <option value="">Choose a job description...</option>
            {jobDescriptions.map(jd => (
              <option key={jd.id} value={jd.id}>
                {jd.job_title} {jd.parsed_data?.company ? `at ${jd.parsed_data.company}` : ''}
              </option>
            ))}
          </select>
          {jobDescriptions.length === 0 && (
            <p className="text-sm text-gray-500 mt-1">
              No job descriptions available. <a href="/job-descriptions" className="text-primary-600 hover:underline">Add a job description first</a>.
            </p>
          )}
        </div>
      </div>

      {/* Submit Button */}
      <div className="flex justify-end">
        <button
          type="submit"
          disabled={isSubmitting || !selectedCV || !selectedJD}
          className="btn-primary flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isSubmitting ? (
            <>
              <div className="loading-spinner h-4 w-4"></div>
              <span>Analyzing...</span>
            </>
          ) : (
            <>
              <Play className="h-4 w-4" />
              <span>Start Analysis</span>
            </>
          )}
        </button>
      </div>
    </form>
  );
};

const ComparisonDetailModal = ({ comparison, isOpen, onClose }) => {
  if (!isOpen || !comparison) return null;

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-success-600';
    if (score >= 60) return 'text-warning-600';
    return 'text-danger-600';
  };

  const renderHighlightedContent = (content) => {
    if (!content) return <p className="text-gray-500">No content available</p>;
    
    return (
      <div 
        className="prose max-w-none text-sm"
        dangerouslySetInnerHTML={{ __html: content }}
      />
    );
  };

  const analysis = comparison.analysis_result;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-6xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="bg-gray-50 px-6 py-4 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-semibold text-gray-900">
                {comparison.job_title || 'Comparison Analysis'}
              </h2>
              {comparison.company && (
                <p className="text-gray-600 mt-1">{comparison.company}</p>
              )}
            </div>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600"
            >
              ✕
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto max-h-[calc(90vh-100px)]">
          {analysis ? (
            <div className="p-6 space-y-8">
              {/* Overall Scores */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <div className={`text-3xl font-bold ${getScoreColor(analysis.overall_score || 0)}`}>
                    {analysis.overall_score || 0}%
                  </div>
                  <div className="text-sm text-gray-600 mt-1">Overall Match</div>
                </div>
                
                {analysis.scores && Object.entries(analysis.scores).map(([key, score]) => (
                  <div key={key} className="text-center p-4 bg-gray-50 rounded-lg">
                    <div className={`text-3xl font-bold ${getScoreColor(score || 0)}`}>
                      {score || 0}%
                    </div>
                    <div className="text-sm text-gray-600 mt-1 capitalize">
                      {key.replace('_', ' ')}
                    </div>
                  </div>
                ))}
              </div>

              {/* Analysis Summary */}
              {analysis.summary && (
                <div className="card">
                  <h3 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
                    <Target className="h-5 w-5 mr-2" />
                    Analysis Summary
                  </h3>
                  <p className="text-gray-700 whitespace-pre-wrap">{analysis.summary}</p>
                </div>
              )}

              {/* Highlighted Content */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* CV Content */}
                {analysis.highlighted_cv && (
                  <div className="card">
                    <h3 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
                      <User className="h-5 w-5 mr-2" />
                      CV Analysis
                    </h3>
                    <div className="custom-scrollbar max-h-96 overflow-y-auto">
                      {renderHighlightedContent(analysis.highlighted_cv)}
                    </div>
                  </div>
                )}

                {/* Job Description Content */}
                {analysis.highlighted_jd && (
                  <div className="card">
                    <h3 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
                      <Building className="h-5 w-5 mr-2" />
                      Job Requirements
                    </h3>
                    <div className="custom-scrollbar max-h-96 overflow-y-auto">
                      {renderHighlightedContent(analysis.highlighted_jd)}
                    </div>
                  </div>
                )}
              </div>

              {/* Gaps and Recommendations */}
              {(analysis.gaps || analysis.recommendations) && (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                  {analysis.gaps && (
                    <div className="card">
                      <h3 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
                        <AlertCircle className="h-5 w-5 mr-2 text-danger-600" />
                        Identified Gaps
                      </h3>
                      <div className="space-y-2">
                        {analysis.gaps.map((gap, index) => (
                          <div key={index} className="p-3 bg-danger-50 border border-danger-200 rounded-lg">
                            <p className="text-danger-800 text-sm">{gap}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {analysis.recommendations && (
                    <div className="card">
                      <h3 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
                        <TrendingUp className="h-5 w-5 mr-2 text-success-600" />
                        Recommendations
                      </h3>
                      <div className="space-y-2">
                        {analysis.recommendations.map((rec, index) => (
                          <div key={index} className="p-3 bg-success-50 border border-success-200 rounded-lg">
                            <p className="text-success-800 text-sm">{rec}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Raw Analysis Data (for debugging) */}
              {process.env.NODE_ENV === 'development' && (
                <details className="card">
                  <summary className="cursor-pointer text-gray-600 text-sm">Raw Analysis Data (Debug)</summary>
                  <pre className="mt-4 text-xs bg-gray-100 p-4 rounded overflow-auto">
                    {JSON.stringify(analysis, null, 2)}
                  </pre>
                </details>
              )}
            </div>
          ) : (
            <div className="p-6 text-center">
              <BarChart3 className="h-16 w-16 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-500">Analysis data not available</p>
              <p className="text-sm text-gray-400 mt-1">
                The comparison may still be processing or processing failed
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

const ComparisonsPage = () => {
  const [searchParams] = useSearchParams();
  const [comparisons, setComparisons] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [selectedComparison, setSelectedComparison] = useState(null);
  const [showDetailModal, setShowDetailModal] = useState(false);

  const preSelectedCVId = searchParams.get('cv_id');
  const preSelectedJDId = searchParams.get('jd_id');

  useEffect(() => {
    loadComparisons();
    analytics.trackPageView('/comparisons', 'Comparisons');
  }, []);

  const loadComparisons = async () => {
    try {
      setIsLoading(true);
      const response = await comparisonAPI.list();
      if (response.success) {
        setComparisons(response.comparisons);
      } else {
        toast.error('Failed to load comparisons');
      }
    } catch (error) {
      console.error('Failed to load comparisons:', error);
      toast.error('Failed to load comparisons');
      analytics.trackError('comparison_load_error', error.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = async (data) => {
    try {
      setIsSubmitting(true);
      analytics.trackFormSubmit('comparison_form', data);
      
      const response = await comparisonAPI.create(data);
      
      if (response.success) {
        toast.success('Analysis started successfully!');
        analytics.trackComparisonCreate(data.cv_id, data.job_description_id, true);
        loadComparisons(); // Reload the list
        
        // Clear URL parameters
        if (preSelectedCVId || preSelectedJDId) {
          window.history.replaceState({}, '', '/comparisons');
        }
      } else {
        throw new Error(response.message || 'Failed to create comparison');
      }
    } catch (error) {
      console.error('Submit failed:', error);
      toast.error(error.message || 'Failed to start analysis');
      analytics.trackComparisonCreate(data.cv_id, data.job_description_id, false, error.message);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = async (comparison) => {
    if (!confirm(`Are you sure you want to delete this comparison?`)) {
      return;
    }

    try {
      const response = await comparisonAPI.delete(comparison.id);
      if (response.success) {
        toast.success('Comparison deleted successfully');
        setComparisons(comparisons.filter(c => c.id !== comparison.id));
        analytics.trackComparisonDelete(comparison.id);
      } else {
        toast.error('Failed to delete comparison');
      }
    } catch (error) {
      console.error('Delete failed:', error);
      toast.error('Failed to delete comparison');
      analytics.trackError('comparison_delete_error', error.message);
    }
  };

  const handleView = async (comparison) => {
    try {
      // Fetch full comparison details
      const response = await comparisonAPI.get(comparison.id);
      if (response.success) {
        setSelectedComparison(response.comparison);
        setShowDetailModal(true);
      } else {
        toast.error('Failed to load comparison details');
      }
    } catch (error) {
      console.error('Failed to load comparison details:', error);
      toast.error('Failed to load comparison details');
    }
  };

  if (isLoading) {
    return (
      <div className="p-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
          <div className="h-64 bg-gray-200 rounded mb-8"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3].map(i => (
              <div key={i} className="h-48 bg-gray-200 rounded-lg"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-8">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">CV Comparisons</h1>
        <p className="text-gray-600 mt-2">
          Analyze how well your CVs match job descriptions with AI-powered gap analysis and scoring.
        </p>
      </div>

      {/* Create Form */}
      <CreateComparisonForm 
        onSubmit={handleSubmit} 
        isSubmitting={isSubmitting}
        preSelectedCVId={preSelectedCVId}
        preSelectedJDId={preSelectedJDId}
      />

      {/* Comparisons List */}
      {comparisons.length > 0 ? (
        <div>
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-gray-900">
              Your Comparisons ({comparisons.length})
            </h2>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {comparisons.map(comparison => (
              <ComparisonCard
                key={comparison.id}
                comparison={comparison}
                onView={handleView}
                onDelete={handleDelete}
              />
            ))}
          </div>
        </div>
      ) : (
        <div className="text-center py-12">
          <BarChart3 className="h-16 w-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No comparisons yet</h3>
          <p className="text-gray-600 mb-6">
            Create your first comparison to analyze how well your CV matches job descriptions.
          </p>
          <div className="space-y-2">
            <p className="text-sm text-gray-500">You'll need:</p>
            <div className="flex justify-center space-x-4 text-sm text-gray-600">
              <span>• At least one processed CV</span>
              <span>• At least one job description</span>
            </div>
          </div>
        </div>
      )}

      {/* Comparison Detail Modal */}
      <ComparisonDetailModal
        comparison={selectedComparison}
        isOpen={showDetailModal}
        onClose={() => {
          setShowDetailModal(false);
          setSelectedComparison(null);
        }}
      />
    </div>
  );
};

export default ComparisonsPage;