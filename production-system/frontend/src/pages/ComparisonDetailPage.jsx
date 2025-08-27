import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, BarChart3, User, Building, Calendar, Download } from 'lucide-react';
import { comparisonAPI } from '../services/api';
import analytics from '../services/analytics';

const ComparisonDetailPage = () => {
  const { id } = useParams();
  const [comparison, setComparison] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadComparison();
    analytics.trackPageView(`/comparisons/${id}`, 'Comparison Detail');
  }, [id]);

  const loadComparison = async () => {
    try {
      setLoading(true);
      const response = await comparisonAPI.get(id);
      if (response.success) {
        setComparison(response.comparison);
      } else {
        setError('Failed to load comparison details');
      }
    } catch (err) {
      console.error('Failed to load comparison:', err);
      setError('Failed to load comparison details');
      analytics.trackError('comparison_detail_load_error', err.message);
    } finally {
      setLoading(false);
    }
  };

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

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/3 mb-6"></div>
          <div className="h-32 bg-gray-200 rounded mb-6"></div>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="h-64 bg-gray-200 rounded"></div>
            <div className="h-64 bg-gray-200 rounded"></div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="text-center py-12">
          <BarChart3 className="h-16 w-16 text-gray-300 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Error Loading Comparison</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <Link
            to="/comparisons"
            className="btn-primary inline-flex items-center"
            onClick={() => analytics.trackLinkClick('/comparisons', 'back_to_comparisons_error')}
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Comparisons
          </Link>
        </div>
      </div>
    );
  }

  if (!comparison) {
    return (
      <div className="p-6">
        <div className="text-center py-12">
          <BarChart3 className="h-16 w-16 text-gray-300 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Comparison Not Found</h2>
          <p className="text-gray-600 mb-4">The comparison you're looking for doesn't exist.</p>
          <Link
            to="/comparisons"
            className="btn-primary inline-flex items-center"
            onClick={() => analytics.trackLinkClick('/comparisons', 'back_to_comparisons_not_found')}
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Comparisons
          </Link>
        </div>
      </div>
    );
  }

  const analysis = comparison.analysis_result;

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Link
            to="/comparisons"
            className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
            onClick={() => analytics.trackLinkClick('/comparisons', 'back_to_comparisons')}
          >
            <ArrowLeft className="h-5 w-5" />
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              {comparison.job_title || 'Comparison Analysis'}
            </h1>
            {comparison.company && (
              <p className="text-gray-600 mt-1">{comparison.company}</p>
            )}
          </div>
        </div>
        
        <div className="flex items-center space-x-3">
          <button
            onClick={() => {
              analytics.trackClick('export-comparison', 'export_comparison_pdf');
              // TODO: Implement PDF export functionality
            }}
            className="btn-secondary inline-flex items-center"
          >
            <Download className="h-4 w-4 mr-2" />
            Export PDF
          </button>
        </div>
      </div>

      {/* Comparison Info */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">Comparison Details</h2>
          <span className="text-sm text-gray-500">
            {new Date(comparison.created_at).toLocaleDateString()}
          </span>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-3">
            <div className="flex items-center text-sm text-gray-600">
              <User className="h-4 w-4 mr-2" />
              <span className="font-medium">CV:</span>
              <span className="ml-2">{comparison.cv_filename || 'Unknown CV'}</span>
            </div>
            <div className="flex items-center text-sm text-gray-600">
              <Building className="h-4 w-4 mr-2" />
              <span className="font-medium">Job:</span>
              <span className="ml-2">{comparison.job_title || 'Unknown Job'}</span>
            </div>
            <div className="flex items-center text-sm text-gray-600">
              <Calendar className="h-4 w-4 mr-2" />
              <span className="font-medium">Analyzed:</span>
              <span className="ml-2">{new Date(comparison.created_at).toLocaleString()}</span>
            </div>
          </div>
          
          <div className="text-right">
            <div className="text-3xl font-bold text-primary-600">
              {analysis?.overall_score || 0}%
            </div>
            <div className="text-sm text-gray-600">Overall Match</div>
          </div>
        </div>
      </div>

      {analysis ? (
        <div className="space-y-6">
          {/* Score Breakdown */}
          {analysis.scores && (
            <div className="card">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Score Breakdown</h2>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {Object.entries(analysis.scores).map(([key, score]) => (
                  <div key={key} className="text-center p-4 bg-gray-50 rounded-lg">
                    <div className={`text-2xl font-bold ${getScoreColor(score || 0)}`}>
                      {score || 0}%
                    </div>
                    <div className="text-sm text-gray-600 mt-1 capitalize">
                      {key.replace('_', ' ')}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Analysis Summary */}
          {analysis.summary && (
            <div className="card">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Analysis Summary</h2>
              <div className="prose max-w-none">
                <p className="text-gray-700 whitespace-pre-wrap">{analysis.summary}</p>
              </div>
            </div>
          )}

          {/* Side-by-side Analysis */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* CV Analysis */}
            {analysis.highlighted_cv && (
              <div className="card">
                <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                  <User className="h-5 w-5 mr-2" />
                  CV Analysis
                </h2>
                <div className="max-h-96 overflow-y-auto custom-scrollbar">
                  {renderHighlightedContent(analysis.highlighted_cv)}
                </div>
              </div>
            )}

            {/* Job Requirements */}
            {analysis.highlighted_jd && (
              <div className="card">
                <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                  <Building className="h-5 w-5 mr-2" />
                  Job Requirements
                </h2>
                <div className="max-h-96 overflow-y-auto custom-scrollbar">
                  {renderHighlightedContent(analysis.highlighted_jd)}
                </div>
              </div>
            )}
          </div>

          {/* Gaps and Recommendations */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {analysis.gaps && analysis.gaps.length > 0 && (
              <div className="card">
                <h2 className="text-lg font-semibold text-gray-900 mb-4 text-danger-600">
                  Identified Gaps
                </h2>
                <div className="space-y-3">
                  {analysis.gaps.map((gap, index) => (
                    <div key={index} className="p-3 bg-danger-50 border border-danger-200 rounded-lg">
                      <p className="text-danger-800 text-sm">{gap}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {analysis.recommendations && analysis.recommendations.length > 0 && (
              <div className="card">
                <h2 className="text-lg font-semibold text-gray-900 mb-4 text-success-600">
                  Recommendations
                </h2>
                <div className="space-y-3">
                  {analysis.recommendations.map((rec, index) => (
                    <div key={index} className="p-3 bg-success-50 border border-success-200 rounded-lg">
                      <p className="text-success-800 text-sm">{rec}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      ) : (
        <div className="card text-center py-12">
          <BarChart3 className="h-16 w-16 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500">Analysis data not available</p>
          <p className="text-sm text-gray-400 mt-1">
            The comparison may still be processing or processing failed
          </p>
        </div>
      )}
    </div>
  );
};

export default ComparisonDetailPage;