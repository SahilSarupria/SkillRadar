# AI Resume Converter - Django Backend

A comprehensive Django backend for an AI-powered resume converter and analyzer platform that helps users convert text to professional resumes, analyze resume quality, identify skill gaps, and get personalized learning recommendations.

## Features

### 🔐 Authentication & User Management
- JWT-based authentication
- User registration and login
- Profile management with professional information
- Premium subscription support

### 📄 Resume Processing
- **AI Text-to-Resume Converter**: Convert raw text, PDFs, or DOCX files into structured resumes
- **Multi-format Support**: PDF, DOCX, and plain text input
- **Background Processing**: Celery-powered async processing for large files
- **Smart Parsing**: AI-powered extraction of work experience, education, skills, and projects

### 🔍 Resume Analysis
- **ATS Compatibility Scoring**: Analyze resume compatibility with Applicant Tracking Systems
- **Content Quality Analysis**: Evaluate resume content, formatting, and keyword optimization
- **Industry-specific Recommendations**: Tailored suggestions based on target industry
- **Improvement Suggestions**: Actionable feedback for resume enhancement

### 🎯 Skill Gap Analysis
- **Current Skills Extraction**: AI-powered identification of existing skills from resumes
- **Job Requirements Matching**: Compare skills against target job descriptions
- **Gap Identification**: Pinpoint missing skills and competencies
- **Learning Path Generation**: Create structured learning plans to close skill gaps

### 📚 Learning Recommendations
- **Multi-platform Integration**: Coursera, Udemy, edX, LinkedIn Learning, Pluralsight
- **Personalized Recommendations**: AI-driven course suggestions based on skill gaps
- **Learning Path Creation**: Comprehensive learning journeys with milestones
- **Progress Tracking**: Monitor course completion and learning progress
- **Affiliate Integration**: Monetization through affiliate partnerships

### 📊 User Dashboard & Analytics
- **Comprehensive Dashboard**: User activity, progress, and achievements
- **Analytics & Insights**: Detailed charts and progress tracking
- **Achievement System**: Gamification with badges and milestones
- **Activity Tracking**: Monitor user engagement and platform usage

### 🛠 Admin Features
- **System Analytics**: Platform-wide statistics and performance metrics
- **User Management**: Comprehensive user administration
- **Content Management**: Course and skill database management
- **Background Tasks**: Automated data sync and maintenance

## Technology Stack

- **Backend**: Django 4.2 + Django REST Framework
- **Database**: PostgreSQL with optimized indexing
- **Cache/Queue**: Redis + Celery for background processing
- **AI Integration**: OpenAI GPT for text processing and analysis
- **File Processing**: PyPDF2, python-docx for document parsing
- **Authentication**: JWT tokens with refresh mechanism
- **API Documentation**: Auto-generated with DRF

## Project Structure

\`\`\`
resume_converter/
├── accounts/           # User authentication and management
├── resumes/           # Resume processing and conversion
├── analyzer/          # Resume analysis and scoring
├── skills/            # Skill gap analysis
├── recommendations/   # Learning platform integration
├── dashboard/         # User dashboard and analytics
├── management/        # Custom management commands
└── resume_converter/  # Main project configuration
\`\`\`

## API Endpoints

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/refresh/` - Token refresh
- `GET /api/auth/profile/` - User profile

### Resume Processing
- `POST /api/resumes/upload/` - Upload resume file
- `POST /api/resumes/convert-text/` - Convert text to resume
- `GET /api/resumes/` - List user resumes
- `GET /api/resumes/{id}/` - Get resume details

### Analysis
- `POST /api/analyzer/analyze/` - Analyze resume
- `GET /api/analyzer/results/{id}/` - Get analysis results
- `GET /api/analyzer/suggestions/{id}/` - Get improvement suggestions

### Skill Analysis
- `POST /api/skills/analyze/` - Analyze skill gaps
- `POST /api/skills/compare-job/` - Compare with job description
- `GET /api/skills/learning-paths/` - Get learning paths

### Recommendations
- `POST /api/recommendations/generate/` - Generate course recommendations
- `GET /api/recommendations/courses/` - Browse courses
- `POST /api/recommendations/bookmark/` - Bookmark courses
- `GET /api/recommendations/my-recommendations/` - User recommendations

### Dashboard
- `GET /api/dashboard/` - User dashboard data
- `GET /api/dashboard/analytics/` - User analytics
- `GET /api/dashboard/achievements/` - User achievements
- `POST /api/dashboard/track/` - Track user activity

## Installation & Setup

### Prerequisites
- Python 3.9+
- PostgreSQL 12+
- Redis 6+
- OpenAI API key

### Environment Variables
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/resume_converter
REDIS_URL=redis://localhost:6379/0

# Django
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# OpenAI
OPENAI_API_KEY=your-openai-api-key

# Email (optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Affiliate IDs (optional)
UDEMY_AFFILIATE_ID=your-udemy-affiliate-id
COURSERA_AFFILIATE_ID=your-coursera-affiliate-id
