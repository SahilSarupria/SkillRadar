from celery import shared_task
from django.contrib.auth import get_user_model
from resumes.models import Resume
from .models import (
    ResumeAnalysis, KeywordAnalysis, ATSCompatibility, 
    ContentAnalysis, IndustryAnalysis
)
from .utils import ResumeAnalyzer
import time
import logging

User = get_user_model()
logger = logging.getLogger(__name__)

@shared_task(bind=True)
def analyze_resume_comprehensive(self, user_id, resume_id, target_job_title="", target_industry=""):
    """Comprehensive resume analysis task"""
    
    try:
        start_time = time.time()
        
        # Get user and resume
        user = User.objects.get(id=user_id)
        resume = Resume.objects.get(id=resume_id, user=user)
        
        # Create analysis record
        analysis = ResumeAnalysis.objects.create(
            resume=resume,
            user=user,
            analysis_type='comprehensive',
            status='processing',
            target_job_title=target_job_title,
            target_industry=target_industry
        )
        
        self.update_state(state='PROGRESS', meta={'current': 10, 'total': 100, 'status': 'Starting analysis...'})
        
        # Get resume text
        resume_text = resume.original_text or ""
        if not resume_text and resume.processed_content:
            # Extract text from processed content if original text is not available
            resume_text = self._extract_text_from_processed_content(resume.processed_content)
        
        if not resume_text:
            raise ValueError("No text content found in resume")
        
        # Initialize analyzer
        analyzer = ResumeAnalyzer()
        
        self.update_state(state='PROGRESS', meta={'current': 20, 'total': 100, 'status': 'Analyzing ATS compatibility...'})
        
        # Perform comprehensive analysis
        analysis_results = analyzer.analyze_resume(resume_text, target_job_title, target_industry)
        
        self.update_state(state='PROGRESS', meta={'current': 60, 'total': 100, 'status': 'Processing results...'})
        
        # Update main analysis record
        analysis.overall_score = analysis_results['overall_score']
        analysis.ats_score = analysis_results['ats_analysis']['score']
        analysis.content_score = analysis_results['content_analysis']['score']
        analysis.keyword_score = analysis_results['keyword_analysis']['score']
        analysis.format_score = analysis_results['format_analysis']['score']
        analysis.analysis_data = analysis_results
        analysis.suggestions = analysis_results['overall_suggestions']
        analysis.processing_time = time.time() - start_time
        analysis.status = 'completed'
        analysis.save()
        
        self.update_state(state='PROGRESS', meta={'current': 80, 'total': 100, 'status': 'Creating detailed analysis...'})
        
        # Create detailed analysis records
        self._create_keyword_analysis(analysis, analysis_results['keyword_analysis'])
        self._create_ats_compatibility(analysis, analysis_results['ats_analysis'])
        self._create_content_analysis(analysis, analysis_results['content_analysis'])
        self._create_industry_analysis(analysis, analysis_results['industry_analysis'])
        
        self.update_state(state='SUCCESS', meta={'current': 100, 'total': 100, 'status': 'Analysis completed!'})
        
        return {
            'analysis_id': str(analysis.id),
            'overall_score': analysis.overall_score,
            'status': 'completed',
            'processing_time': analysis.processing_time
        }
        
    except Exception as e:
        logger.error(f"Error in comprehensive resume analysis: {str(e)}")
        
        # Update analysis status to failed
        if 'analysis' in locals():
            analysis.status = 'failed'
            analysis.save()
        
        self.update_state(
            state='FAILURE',
            meta={'current': 0, 'total': 100, 'status': f'Analysis failed: {str(e)}'}
        )
        raise

@shared_task(bind=True)
def analyze_resume_specific(self, user_id, resume_id, analysis_type, target_job_title="", target_industry=""):
    """Specific type of resume analysis"""
    
    try:
        start_time = time.time()
        
        # Get user and resume
        user = User.objects.get(id=user_id)
        resume = Resume.objects.get(id=resume_id, user=user)
        
        # Create analysis record
        analysis = ResumeAnalysis.objects.create(
            resume=resume,
            user=user,
            analysis_type=analysis_type,
            status='processing',
            target_job_title=target_job_title,
            target_industry=target_industry
        )
        
        self.update_state(state='PROGRESS', meta={'current': 20, 'total': 100, 'status': f'Starting {analysis_type}...'})
        
        # Get resume text
        resume_text = resume.original_text or ""
        if not resume_text and resume.processed_content:
            resume_text = self._extract_text_from_processed_content(resume.processed_content)
        
        if not resume_text:
            raise ValueError("No text content found in resume")
        
        # Initialize analyzer
        analyzer = ResumeAnalyzer()
        
        self.update_state(state='PROGRESS', meta={'current': 50, 'total': 100, 'status': f'Performing {analysis_type}...'})
        
        # Perform specific analysis
        if analysis_type == 'ats_scan':
            results = analyzer.analyze_ats_compatibility(resume_text)
            analysis.ats_score = results['score']
            analysis.overall_score = results['score']
            self._create_ats_compatibility(analysis, results)
            
        elif analysis_type == 'content_analysis':
            results = analyzer.analyze_content_quality(resume_text)
            analysis.content_score = results['score']
            analysis.overall_score = results['score']
            self._create_content_analysis(analysis, results)
            
        elif analysis_type == 'keyword_analysis':
            results = analyzer.analyze_keywords(resume_text, target_job_title, target_industry)
            analysis.keyword_score = results['score']
            analysis.overall_score = results['score']
            self._create_keyword_analysis(analysis, results)
            
        elif analysis_type == 'industry_analysis':
            results = analyzer.analyze_industry_fit(resume_text, target_industry)
            analysis.overall_score = results['score']
            self._create_industry_analysis(analysis, results)
        
        # Update analysis record
        analysis.analysis_data = results
        analysis.processing_time = time.time() - start_time
        analysis.status = 'completed'
        analysis.save()
        
        self.update_state(state='SUCCESS', meta={'current': 100, 'total': 100, 'status': 'Analysis completed!'})
        
        return {
            'analysis_id': str(analysis.id),
            'overall_score': analysis.overall_score,
            'status': 'completed',
            'processing_time': analysis.processing_time
        }
        
    except Exception as e:
        logger.error(f"Error in specific resume analysis: {str(e)}")
        
        # Update analysis status to failed
        if 'analysis' in locals():
            analysis.status = 'failed'
            analysis.save()
        
        self.update_state(
            state='FAILURE',
            meta={'current': 0, 'total': 100, 'status': f'Analysis failed: {str(e)}'}
        )
        raise

def _extract_text_from_processed_content(processed_content):
    """Extract text from processed resume content"""
    text_parts = []
    
    # Extract from personal info
    if 'personal_info' in processed_content:
        personal = processed_content['personal_info']
        text_parts.extend([
            personal.get('full_name', ''),
            personal.get('email', ''),
            personal.get('phone', ''),
            personal.get('location', '')
        ])
    
    # Extract professional summary
    if 'professional_summary' in processed_content:
        text_parts.append(processed_content['professional_summary'])
    
    # Extract work experience
    if 'work_experience' in processed_content:
        for exp in processed_content['work_experience']:
            text_parts.extend([
                exp.get('position', ''),
                exp.get('company_name', ''),
                exp.get('description', '')
            ])
            text_parts.extend(exp.get('achievements', []))
    
    # Extract education
    if 'education' in processed_content:
        for edu in processed_content['education']:
            text_parts.extend([
                edu.get('degree', ''),
                edu.get('institution', ''),
                edu.get('field_of_study', '')
            ])
    
    # Extract skills
    if 'skills' in processed_content:
        skills = processed_content['skills']
        for skill_type, skill_list in skills.items():
            if isinstance(skill_list, list):
                text_parts.extend(skill_list)
    
    return ' '.join(filter(None, text_parts))

def _create_keyword_analysis(analysis, results):
    """Create KeywordAnalysis record"""
    KeywordAnalysis.objects.create(
        analysis=analysis,
        found_keywords=results.get('found_keywords', []),
        missing_keywords=results.get('missing_keywords', []),
        keyword_density=results.get('keyword_density', {}),
        industry_keywords=results.get('industry_keywords', []),
        skill_keywords=results.get('skill_keywords', []),
        keyword_match_percentage=results.get('keyword_match_percentage', 0),
        industry_relevance_score=results.get('industry_relevance_score', 0),
        skill_coverage_score=results.get('skill_coverage_score', 0)
    )

def _create_ats_compatibility(analysis, results):
    """Create ATSCompatibility record"""
    ATSCompatibility.objects.create(
        analysis=analysis,
        has_contact_info=results.get('checks', {}).get('has_contact_info', False),
        has_clear_sections=results.get('checks', {}).get('has_clear_sections', False),
        uses_standard_fonts=results.get('checks', {}).get('uses_standard_fonts', True),
        has_keywords=results.get('checks', {}).get('has_keywords', False),
        proper_formatting=results.get('checks', {}).get('proper_formatting', False),
        no_images_or_graphics=results.get('checks', {}).get('no_images_or_graphics', True),
        readable_file_format=results.get('checks', {}).get('readable_file_format', True),
        formatting_issues=results.get('formatting_issues', []),
        missing_sections=results.get('missing_sections', []),
        optimization_tips=results.get('optimization_tips', []),
        readability_score=results.get('readability_score', 0),
        structure_score=results.get('structure_score', 0),
        content_extraction_score=results.get('content_extraction_score', 0)
    )

def _create_content_analysis(analysis, results):
    """Create ContentAnalysis record"""
    ContentAnalysis.objects.create(
        analysis=analysis,
        word_count=results.get('word_count', 0),
        sentence_count=results.get('sentence_count', 0),
        paragraph_count=results.get('paragraph_count', 0),
        bullet_points_count=results.get('bullet_points_count', 0),
        readability_score=results.get('readability_score', 0),
        action_verbs_count=results.get('action_verbs_count', 0),
        quantified_achievements=results.get('quantified_achievements', 0),
        tone_analysis=results.get('tone_analysis', {}),
        grammar_issues=results.get('grammar_issues', []),
        content_suggestions=results.get('content_suggestions', []),
        section_completeness=results.get('section_completeness', {}),
        section_quality_scores=results.get('section_quality_scores', {})
    )

def _create_industry_analysis(analysis, results):
    """Create IndustryAnalysis record"""
    IndustryAnalysis.objects.create(
        analysis=analysis,
        detected_industries=results.get('detected_industries', []),
        industry_match_scores=results.get('industry_match_scores', {}),
        target_industry_fit=results.get('target_industry_fit', 0),
        required_skills_present=results.get('required_skills_present', []),
        missing_skills=results.get('missing_skills', []),
        industry_keywords_found=results.get('industry_keywords_found', []),
        industry_specific_tips=results.get('industry_specific_tips', []),
        role_alignment_score=results.get('role_alignment_score', 0)
    )

@shared_task
def cleanup_old_analyses():
    """Clean up old analysis records"""
    from datetime import timedelta
    from django.utils import timezone
    
    # Delete analyses older than 30 days
    cutoff_date = timezone.now() - timedelta(days=30)
    old_analyses = ResumeAnalysis.objects.filter(created_at__lt=cutoff_date)
    
    count = old_analyses.count()
    old_analyses.delete()
    
    logger.info(f"Cleaned up {count} old resume analyses")
    return f"Cleaned up {count} old analyses"
