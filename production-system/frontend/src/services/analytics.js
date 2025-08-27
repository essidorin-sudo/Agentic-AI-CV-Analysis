// Simple analytics without API dependency to prevent circular imports

class AnalyticsService {
  constructor() {
    this.sessionId = this.generateSessionId();
    this.userId = null;
    this.eventQueue = [];
    this.isOnline = navigator.onLine;
    
    // Listen for online/offline events
    window.addEventListener('online', () => {
      this.isOnline = true;
      this.flushEventQueue();
    });
    
    window.addEventListener('offline', () => {
      this.isOnline = false;
    });
    
    // Auto-flush queue periodically
    setInterval(() => this.flushEventQueue(), 10000); // Every 10 seconds
    
    // Flush queue before page unload
    window.addEventListener('beforeunload', () => this.flushEventQueue());
    
    // Track page view on initialization
    this.trackPageView();
  }

  generateSessionId() {
    return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
  }

  setUserId(userId) {
    this.userId = userId;
  }

  getCurrentPageInfo() {
    return {
      page_url: window.location.href,
      page_title: document.title,
      timestamp: new Date().toISOString()
    };
  }

  // ============================================================================
  // CORE TRACKING METHODS
  // ============================================================================

  async trackEvent(eventType, eventAction, eventLabel = null, elementId = null, metadata = null) {
    const eventData = {
      event_type: eventType,
      event_action: eventAction,
      event_label: eventLabel,
      element_id: elementId,
      metadata: {
        ...metadata,
        user_agent: navigator.userAgent,
        viewport: {
          width: window.innerWidth,
          height: window.innerHeight
        },
        session_id: this.sessionId
      },
      ...this.getCurrentPageInfo()
    };

    // Add to queue for batch processing
    this.eventQueue.push(eventData);

    // If online and queue is getting full, flush immediately
    if (this.isOnline && this.eventQueue.length >= 5) {
      this.flushEventQueue();
    }

    console.log('📊 Analytics Event:', eventType, eventAction, eventLabel);
  }

  async flushEventQueue() {
    if (!this.isOnline || this.eventQueue.length === 0) return;

    const eventsToSend = [...this.eventQueue];
    this.eventQueue = [];

    try {
      // Simple console logging instead of API calls to prevent circular dependency
      console.log('📊 Sending analytics batch:', eventsToSend.length, 'events');
      // TODO: Re-implement API tracking after fixing circular dependency
    } catch (error) {
      console.warn('Failed to send analytics events:', error);
    }
  }

  // ============================================================================
  // CLICK TRACKING
  // ============================================================================

  trackClick(elementId, eventLabel = null, metadata = null) {
    this.trackEvent('click', 'button_click', eventLabel, elementId, metadata);
  }

  trackLinkClick(url, eventLabel = null) {
    this.trackEvent('click', 'link_click', eventLabel, null, { target_url: url });
  }

  trackMenuClick(menuItem) {
    this.trackEvent('click', 'menu_click', menuItem);
  }

  // ============================================================================
  // NAVIGATION TRACKING
  // ============================================================================

  trackPageView(customPageInfo = null) {
    const pageInfo = customPageInfo || this.getCurrentPageInfo();
    this.trackEvent('navigation', 'page_view', pageInfo.page_title, null, {
      page_path: window.location.pathname,
      referrer: document.referrer
    });
  }

  trackNavigation(from, to) {
    this.trackEvent('navigation', 'route_change', `${from} -> ${to}`, null, {
      from_page: from,
      to_page: to
    });
  }

  // ============================================================================
  // USER INTERACTION TRACKING
  // ============================================================================

  trackFormSubmit(formName, formData = null) {
    this.trackEvent('form', 'form_submit', formName, null, {
      form_fields: formData ? Object.keys(formData) : null
    });
  }

  trackFormError(formName, errorField, errorMessage) {
    this.trackEvent('form', 'form_error', formName, null, {
      error_field: errorField,
      error_message: errorMessage
    });
  }

  trackSearch(searchTerm, resultsCount = null) {
    this.trackEvent('search', 'search_query', searchTerm, null, {
      results_count: resultsCount
    });
  }

  trackFilter(filterType, filterValue) {
    this.trackEvent('filter', 'filter_apply', filterType, null, {
      filter_value: filterValue
    });
  }

  // ============================================================================
  // FILE & UPLOAD TRACKING
  // ============================================================================

  trackFileUpload(fileType, fileName, fileSize, uploadTime = null) {
    this.trackEvent('upload', 'file_upload', fileType, null, {
      file_name: fileName,
      file_size: fileSize,
      upload_time: uploadTime
    });
  }

  trackFileDownload(fileName, fileType) {
    this.trackEvent('download', 'file_download', fileType, null, {
      file_name: fileName
    });
  }

  trackFileDelete(fileName, fileType) {
    this.trackEvent('delete', 'file_delete', fileType, null, {
      file_name: fileName
    });
  }

  // ============================================================================
  // CV ANALYZER SPECIFIC TRACKING
  // ============================================================================

  trackCVUpload(fileName, fileSize, parseSuccess, parseTime) {
    this.trackEvent('cv_analysis', 'cv_upload', fileName, 'cv-upload-button', {
      file_size: fileSize,
      parse_success: parseSuccess,
      parse_time: parseTime
    });
  }

  trackJDSubmission(submissionType, source, parseSuccess) {
    // submissionType: 'text' or 'url'
    this.trackEvent('jd_analysis', 'jd_submit', submissionType, 'jd-submit-button', {
      source: source,
      parse_success: parseSuccess
    });
  }

  trackComparison(cvId, jdId, matchScore, analysisTime) {
    this.trackEvent('gap_analysis', 'cv_jd_comparison', 'gap_analysis_run', 'compare-button', {
      cv_id: cvId,
      jd_id: jdId,
      match_score: matchScore,
      analysis_time: analysisTime
    });
  }

  trackComparisonView(comparisonId, viewDuration = null) {
    this.trackEvent('gap_analysis', 'comparison_view', comparisonId, null, {
      view_duration: viewDuration
    });
  }

  // ============================================================================
  // ERROR TRACKING
  // ============================================================================

  trackError(errorType, errorMessage, stackTrace = null, context = null) {
    this.trackEvent('error', 'application_error', errorType, null, {
      error_message: errorMessage,
      stack_trace: stackTrace,
      context: context
    });
  }

  trackAPIError(endpoint, statusCode, errorMessage) {
    this.trackEvent('error', 'api_error', endpoint, null, {
      status_code: statusCode,
      error_message: errorMessage
    });
  }

  // ============================================================================
  // PERFORMANCE TRACKING
  // ============================================================================

  trackPerformance(action, duration, metadata = null) {
    this.trackEvent('performance', 'timing', action, null, {
      duration_ms: duration,
      ...metadata
    });
  }

  trackPageLoad() {
    // Track page load performance
    if (window.performance) {
      const navigation = performance.getEntriesByType('navigation')[0];
      if (navigation) {
        this.trackPerformance('page_load', navigation.loadEventEnd - navigation.loadEventStart, {
          dom_content_loaded: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
          dom_interactive: navigation.domInteractive - navigation.domContentLoadedEventStart
        });
      }
    }
  }

  // ============================================================================
  // USER ENGAGEMENT TRACKING
  // ============================================================================

  trackFeatureUsage(featureName, usageType = 'used') {
    this.trackEvent('engagement', 'feature_usage', featureName, null, {
      usage_type: usageType
    });
  }

  trackTimeSpent(pageName, timeSpent) {
    this.trackEvent('engagement', 'time_spent', pageName, null, {
      time_spent_seconds: timeSpent
    });
  }

  trackScrollDepth(percentage) {
    this.trackEvent('engagement', 'scroll_depth', `${percentage}%`, null, {
      scroll_percentage: percentage
    });
  }

  // ============================================================================
  // AUTH TRACKING
  // ============================================================================

  trackLogin(method = 'email', success = true) {
    this.trackEvent('auth', 'login', method, 'login-button', {
      success: success
    });
  }

  trackRegistration(success = true) {
    this.trackEvent('auth', 'registration', success ? 'success' : 'failed', 'register-button', {
      success: success
    });
  }

  trackLogout() {
    this.trackEvent('auth', 'logout', 'user_initiated', 'logout-button');
  }

  // ============================================================================
  // SETUP ELEMENT TRACKING
  // ============================================================================

  setupAutoTracking() {
    // Auto-track all button clicks
    document.addEventListener('click', (event) => {
      const element = event.target;
      
      // Track button clicks
      if (element.tagName === 'BUTTON' || element.closest('button')) {
        const button = element.tagName === 'BUTTON' ? element : element.closest('button');
        const buttonId = button.id || button.className || 'unnamed-button';
        const buttonText = button.textContent?.trim() || 'no-text';
        
        this.trackClick(buttonId, buttonText);
      }
      
      // Track link clicks
      if (element.tagName === 'A' || element.closest('a')) {
        const link = element.tagName === 'A' ? element : element.closest('a');
        const href = link.href;
        const linkText = link.textContent?.trim() || 'no-text';
        
        this.trackLinkClick(href, linkText);
      }
    });

    // Track form submissions
    document.addEventListener('submit', (event) => {
      const form = event.target;
      const formId = form.id || form.className || 'unnamed-form';
      
      this.trackFormSubmit(formId);
    });

    // Track scroll depth
    let maxScrollDepth = 0;
    window.addEventListener('scroll', () => {
      const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
      const docHeight = document.documentElement.scrollHeight - window.innerHeight;
      const scrollPercent = Math.round((scrollTop / docHeight) * 100);
      
      if (scrollPercent > maxScrollDepth && scrollPercent % 25 === 0) {
        maxScrollDepth = scrollPercent;
        this.trackScrollDepth(scrollPercent);
      }
    });

    // Track page load performance
    window.addEventListener('load', () => {
      setTimeout(() => this.trackPageLoad(), 1000);
    });
  }
}

// Create and export singleton instance
const analytics = new AnalyticsService();

// Setup auto-tracking when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => analytics.setupAutoTracking());
} else {
  analytics.setupAutoTracking();
}

export default analytics;