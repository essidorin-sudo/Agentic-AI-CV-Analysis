# CV Analyzer Production System

A comprehensive multi-agent AI system for intelligent CV analysis with production-ready frontend, admin interface, and comprehensive analytics tracking.

## 🏗️ System Architecture

```
production-system/
├── backend/                 # Flask API with authentication & analytics
│   ├── app.py              # Main API server
│   ├── models.py           # Database models (SQLAlchemy)
│   ├── analytics.py        # Analytics tracking system
│   └── requirements.txt    # Python dependencies
├── frontend/               # React frontend application
│   ├── src/
│   │   ├── components/     # Reusable UI components
│   │   ├── pages/          # Application pages
│   │   ├── services/       # API & analytics services
│   │   └── utils/          # Utility functions
│   └── package.json        # Node.js dependencies
└── admin-interface/        # Admin dashboard (separate app)
    ├── src/
    │   ├── components/     # Admin-specific components
    │   ├── pages/          # Admin dashboard pages
    │   └── services/       # Admin API services
    └── package.json
```

## 🎯 Key Features

### User Application
- **Multi-CV Management**: Upload, store, and manage multiple CVs
- **Job Description Processing**: Text input or URL scraping
- **AI-Powered Gap Analysis**: Smart CV-JD matching with color-coded insights
- **Comparison History**: Track and review past analyses
- **User Authentication**: Secure login/registration system
- **Responsive Design**: Works on desktop, tablet, and mobile

### Admin Interface
- **User Management**: View and manage user accounts
- **Usage Analytics**: Comprehensive tracking of user interactions
- **System Performance**: Monitor AI agent performance and usage
- **Dashboard Insights**: Real-time statistics and trends
- **Event Tracking**: Every click, upload, and action is tracked

### Analytics System
- **Click Tracking**: Every button click and interaction
- **Performance Monitoring**: Page load times, API response times
- **User Journey**: Track user paths and behavior patterns
- **Error Tracking**: Capture and analyze system errors
- **Feature Usage**: Monitor which features are most used

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- PostgreSQL (production) or SQLite (development)

### Backend Setup
```bash
cd backend/
pip install -r requirements.txt

# Set environment variables
export ANTHROPIC_API_KEY="your-anthropic-key"
export SECRET_KEY="your-secret-key"
export JWT_SECRET_KEY="your-jwt-secret"

# Start the API server
python app.py
# Server runs on http://localhost:8000
```

### Frontend Setup
```bash
cd frontend/
npm install
npm run dev
# App runs on http://localhost:3000
```

### Admin Interface Setup
```bash
cd admin-interface/
npm install
npm run dev
# Admin runs on http://localhost:3001
```

## 📊 Analytics Tracking

### Automatic Tracking
- **Page Views**: Every page navigation
- **Button Clicks**: All button interactions with element IDs
- **Form Submissions**: Form completion and errors
- **File Uploads**: CV uploads with metadata
- **Scroll Depth**: User engagement measurement
- **Performance**: Page load and API response times

### Custom Events
```javascript
import analytics from './services/analytics';

// Track custom events
analytics.trackCVUpload(fileName, fileSize, parseSuccess, parseTime);
analytics.trackComparison(cvId, jdId, matchScore, analysisTime);
analytics.trackFeatureUsage('gap_analysis', 'completed');
```

### Event Types
- **click**: Button clicks, link clicks, menu interactions
- **upload**: File uploads (CVs, documents)
- **analysis**: CV parsing, JD processing, gap analysis
- **navigation**: Page views, route changes
- **form**: Form submissions, validation errors
- **error**: Application errors, API failures
- **performance**: Timing measurements
- **engagement**: Feature usage, time spent

## 🔐 Authentication & Security

### User Authentication
- JWT-based authentication
- Password hashing with bcrypt
- Session management
- Token expiration handling

### Admin Access
- Role-based access control
- Admin-only routes and features
- Separate admin interface
- User management capabilities

### Default Admin Account
```
Email: admin@cvanalyzer.com
Password: admin123
```
**⚠️ Change this password in production!**

## 🗄️ Database Schema

### Users Table
- User accounts with authentication
- Role-based permissions (admin/user)
- Profile information

### CVs Table
- Uploaded CV files and metadata
- Parsed content from CV Parser Agent
- User associations

### Job Descriptions Table
- Job postings (text or URL)
- Parsed content from JD Parser Agent
- Source tracking

### Comparisons Table
- CV-JD analysis results
- Gap analysis data
- Match scores and highlighted content

### Analytics Events Table
- All user interactions
- Event metadata and timestamps
- Session tracking

### System Usage Table
- Daily aggregated statistics
- Performance metrics
- Usage trends

## 🤖 AI Agent Integration

### CV Parser Agent (Port 5005)
- Parses uploaded CV files
- Extracts structured data
- Handles multiple file formats

### JD Parser Agent (Port 5007)
- Processes job descriptions
- Web scraping with JavaScript support
- Structured data extraction

### Gap Analyst Agent (Port 5008)
- Compares CV and JD data
- Generates match scores
- Creates color-coded insights

## 📈 Admin Dashboard Features

### Overview Dashboard
- Total users, CVs, job descriptions
- Recent activity metrics
- System health indicators

### User Analytics
- Most active users
- User behavior patterns
- Registration trends

### Feature Usage
- Popular actions and features
- Usage frequency analysis
- Performance bottlenecks

### Event Analytics
- Real-time event stream
- Filtered event views
- Custom date ranges

## 🛠️ API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/profile` - Get user profile

### CV Management
- `GET /api/cvs` - List user CVs
- `POST /api/cvs/upload` - Upload CV
- `DELETE /api/cvs/:id` - Delete CV

### Job Descriptions
- `GET /api/job-descriptions` - List job descriptions
- `POST /api/job-descriptions` - Create job description
- `DELETE /api/job-descriptions/:id` - Delete job description

### Comparisons
- `GET /api/comparisons` - List comparisons
- `POST /api/comparisons` - Create comparison
- `GET /api/comparisons/:id` - Get comparison details

### Analytics
- `POST /api/analytics/track` - Track user event

### Admin
- `GET /api/admin/dashboard` - Admin dashboard data
- `GET /api/admin/users` - User management

## 🎨 Frontend Components

### Core Components
- `Navbar` - Navigation with user menu
- `LoginPage` - Authentication form
- `DashboardPage` - Main user dashboard
- `CVLibraryPage` - CV management interface
- `ComparisonsPage` - Analysis results

### Key Features
- Responsive design with Tailwind CSS
- Form validation with react-hook-form
- File upload with drag-and-drop
- Real-time notifications
- Loading states and error handling

## 📱 Mobile Responsiveness

- Responsive navigation menu
- Touch-friendly interfaces
- Optimized for mobile upload
- Progressive Web App features

## 🚀 Deployment

### Production Environment Variables
```bash
# Backend
ANTHROPIC_API_KEY=your-production-key
DATABASE_URL=postgresql://user:pass@host:port/db
SECRET_KEY=secure-random-key
JWT_SECRET_KEY=secure-jwt-key
FLASK_ENV=production

# Frontend
VITE_API_URL=https://your-api-domain.com/api
```

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up --build

# Individual services
docker build -t cv-analyzer-backend ./backend
docker build -t cv-analyzer-frontend ./frontend
docker build -t cv-analyzer-admin ./admin-interface
```

## 📊 Monitoring & Analytics

### User Behavior Tracking
- Every click is tracked with element IDs
- Page navigation and time spent
- Feature usage patterns
- Error rates and types

### Performance Monitoring
- API response times
- Page load performance
- File upload speeds
- Agent processing times

### Business Metrics
- User registration trends
- Feature adoption rates
- Most popular job sites
- CV parsing success rates

## 🔧 Development

### Adding New Analytics Events
```javascript
// In any component
import analytics from '../services/analytics';

// Track custom business events
analytics.trackEvent('business', 'premium_feature_used', 'advanced_analysis');

// Track user interactions
analytics.trackClick('custom-button-id', 'Custom Action Label');
```

### Database Migrations
```python
# Create new migration
flask db migrate -m "Add new table"

# Apply migrations
flask db upgrade
```

## 🎯 Next Steps

1. **Enhanced UI**: Complete all remaining page components
2. **Admin Features**: Full admin dashboard implementation
3. **Real-time Updates**: WebSocket integration for live updates
4. **Advanced Analytics**: Machine learning insights
5. **API Documentation**: Swagger/OpenAPI documentation
6. **Testing**: Comprehensive unit and integration tests
7. **Performance**: Caching and optimization
8. **Security**: Advanced security features

## 📝 License

This is a proprietary CV Analyzer system. All rights reserved.

---

**Built with**: React, Flask, SQLAlchemy, Tailwind CSS, and ❤️