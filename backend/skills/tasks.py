from celery import shared_task
from django.contrib.auth import get_user_model
from resumes.models import Resume
from .models import (
    SkillGapAnalysis, SkillGap, UserSkill, Skill, JobRole, 
    LearningPath, LearningPathStep
)
from .utils import SkillExtractor, SkillGapAnalyzer, SkillMatcher, LearningPathGenerator
import time
import logging

User = get_user_model()
logger = logging.getLogger(__name__)

@shared_task(bind=True)
def analyze_skill_gaps(self, user_id, resume_id, target_job_title, target_industry, target_level, job_description=""):
    """Comprehensive skill gap analysis task"""
    
    try:
        start_time = time.time()
        
        # Get user and resume
        user = User.objects.get(id=user_id)
        resume = Resume.objects.get(id=resume_id, user=user)
        
        # Create analysis record
        analysis = SkillGapAnalysis.objects.create(
            user=user,
            resume=resume,
            target_job_title=target_job_title,
            target_industry=target_industry,
            target_level=target_level,
            status='processing'
        )
        
        self.update_state(state='PROGRESS', meta={'current': 10, 'total': 100, 'status': 'Extracting skills from resume...'})
        
        # Extract skills from resume
        skill_extractor = SkillExtractor()
        resume_text = resume.original_text or self._extract_text_from_resume(resume)
        
        if not resume_text:
            raise ValueError("No text content found in resume")
        
        extracted_skills = skill_extractor.extract_skills_from_resume(resume_text)
        
        self.update_state(state='PROGRESS', meta={'current': 30, 'total': 100, 'status': 'Analyzing job requirements...'})
        
        # Analyze job requirements
        if job_description:
            job_requirements = skill_extractor.extract_skills_from_job_description(job_description, target_job_title)
        else:
            # Use AI to generate typical requirements for the job title/industry
            job_requirements = self._generate_job_requirements(target_job_title, target_industry, target_level)
        
        self.update_state(state='PROGRESS', meta={'current': 50, 'total': 100, 'status': 'Matching skills with database...'})
        
        # Match extracted skills with database
        user_skills = self._match_and_create_user_skills(user, extracted_skills)
        
        self.update_state(state='PROGRESS', meta={'current': 70, 'total': 100, 'status': 'Performing gap analysis...'})
        
        # Perform skill gap analysis
        gap_analyzer = SkillGapAnalyzer()
        user_profile = {
            'experience_level': target_level,
            'industry_preference': target_industry,
            'career_goals': target_job_title
        }
        
        gap_analysis_results = gap_analyzer.analyze_skill_gaps(user_skills, job_requirements, target_job_title)
        
        self.update_state(state='PROGRESS', meta={'current': 85, 'total': 100, 'status': 'Creating skill gaps and recommendations...'})
        
        # Update analysis record
        analysis.overall_match_score = gap_analysis_results['overall_match_score']
        analysis.skills_matched = gap_analysis_results['skills_matched']
        analysis.skills_missing = gap_analysis_results['skills_missing']
        analysis.skills_to_improve = gap_analysis_results['skills_to_improve']
        analysis.analysis_data = gap_analysis_results
        analysis.recommendations = gap_analysis_results['recommendations']
        analysis.learning_path = gap_analysis_results['learning_path']
        analysis.processing_time = time.time() - start_time
        analysis.status = 'completed'
        analysis.save()
        
        # Create individual skill gap records
        self._create_skill_gap_records(analysis, gap_analysis_results['skill_gaps'])
        
        self.update_state(state='SUCCESS', meta={'current': 100, 'total': 100, 'status': 'Skill gap analysis completed!'})
        
        return {
            'analysis_id': str(analysis.id),
            'overall_match_score': analysis.overall_match_score,
            'skills_matched': analysis.skills_matched,
            'skills_missing': analysis.skills_missing,
            'status': 'completed',
            'processing_time': analysis.processing_time
        }
        
    except Exception as e:
        logger.error(f"Error in skill gap analysis: {str(e)}")
        
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
def generate_learning_path(self, user_id, skill_gap_analysis_id, title, target_skills, duration_weeks=12, hours_per_week=5):
    """Generate personalized learning path"""
    
    try:
        start_time = time.time()
        
        # Get user and analysis
        user = User.objects.get(id=user_id)
        analysis = SkillGapAnalysis.objects.get(id=skill_gap_analysis_id, user=user)
        
        self.update_state(state='PROGRESS', meta={'current': 20, 'total': 100, 'status': 'Analyzing skill gaps...'})
        
        # Get skill gaps for target skills
        skill_gaps = list(analysis.skill_gaps.filter(skill_id__in=target_skills).values(
            'skill__name', 'gap_type', 'current_level', 'required_level', 
            'importance', 'priority', 'estimated_learning_time'
        ))
        
        # Convert to format expected by learning path generator
        formatted_gaps = []
        for gap in skill_gaps:
            formatted_gaps.append({
                'skill': gap['skill__name'],
                'gap_type': gap['gap_type'],
                'current_level': gap['current_level'],
                'required_level': gap['required_level'],
                'importance': gap['importance'],
                'priority': gap['priority'],
                'estimated_learning_time': gap['estimated_learning_time']
            })
        
        self.update_state(state='PROGRESS', meta={'current': 50, 'total': 100, 'status': 'Generating learning path...'})
        
        # Generate learning path
        path_generator = LearningPathGenerator()
        user_profile = {
            'experience_level': analysis.target_level,
            'industry': analysis.target_industry,
            'available_hours_per_week': hours_per_week
        }
        
        learning_path_data = path_generator.generate_learning_path(formatted_gaps, user_profile, duration_weeks)
        
        self.update_state(state='PROGRESS', meta={'current': 80, 'total': 100, 'status': 'Creating learning path record...'})
        
        # Create learning path record
        learning_path = LearningPath.objects.create(
            user=user,
            skill_gap_analysis=analysis,
            title=title,
            description=f"Personalized learning path for {analysis.target_job_title}",
            difficulty_level='intermediate',  # Could be determined from analysis
            estimated_duration_weeks=duration_weeks,
            estimated_hours_per_week=hours_per_week
        )
        
        # Add target skills
        target_skill_objects = Skill.objects.filter(id__in=target_skills)
        learning_path.target_skills.set(target_skill_objects)
        
        # Create learning path steps
        for phase in learning_path_data['phases']:
            for step_data in phase['steps']:
                skill = Skill.objects.filter(name__iexact=step_data['skill']).first()
                if skill:
                    LearningPathStep.objects.create(
                        learning_path=learning_path,
                        skill=skill,
                        title=f"Learn {step_data['skill']}",
                        description=f"Achieve {step_data['target_level']} proficiency in {step_data['skill']}",
                        order=step_data['step_number'],
                        estimated_hours=step_data['estimated_hours'],
                        resources=step_data['resources']
                    )
        
        self.update_state(state='SUCCESS', meta={'current': 100, 'total': 100, 'status': 'Learning path created!'})
        
        return {
            'learning_path_id': str(learning_path.id),
            'title': learning_path.title,
            'total_steps': learning_path.steps.count(),
            'estimated_duration_weeks': learning_path.estimated_duration_weeks,
            'status': 'completed'
        }
        
    except Exception as e:
        logger.error(f"Error generating learning path: {str(e)}")
        
        self.update_state(
            state='FAILURE',
            meta={'current': 0, 'total': 100, 'status': f'Learning path generation failed: {str(e)}'}
        )
        raise

@shared_task
def update_skill_demand_scores():
    """Update skill demand scores based on market data"""
    # This would typically integrate with job market APIs
    # For now, just log the task
    logger.info("Updating skill demand scores...")
    
    # Placeholder logic - in practice, this would:
    # 1. Query job market APIs (Indeed, LinkedIn, etc.)
    # 2. Analyze job postings for skill mentions
    # 3. Update demand scores in the database
    
    skills_updated = Skill.objects.filter(is_active=True).count()
    logger.info(f"Updated demand scores for {skills_updated} skills")
    
    return f"Updated {skills_updated} skill demand scores"

def _extract_text_from_resume(resume):
    """Extract text from resume object"""
    if resume.original_text:
        return resume.original_text
    
    if resume.processed_content:
        # Extract text from processed content
        text_parts = []
        
        content = resume.processed_content
        if isinstance(content, dict):
            # Extract from various sections
            for section, data in content.items():
                if isinstance(data, str):
                    text_parts.append(data)
                elif isinstance(data, list):
                    text_parts.extend([str(item) for item in data])
                elif isinstance(data, dict):
                    text_parts.extend([str(value) for value in data.values() if isinstance(value, str)])
        
        return ' '.join(text_parts)
    
    return ""

def _generate_job_requirements(job_title, industry, level):
    """Generate typical job requirements using AI or predefined data"""
    # This would use AI to generate typical requirements
    # For now, return a basic structure
    return {
        'required_skills': [
            {'skill': 'Communication', 'proficiency': 'intermediate', 'importance': 'required'},
            {'skill': 'Problem Solving', 'proficiency': 'intermediate', 'importance': 'required'},
            {'skill': 'Teamwork', 'proficiency': 'intermediate', 'importance': 'required'},
        ],
        'preferred_skills': [
            {'skill': 'Leadership', 'proficiency': 'intermediate', 'importance': 'preferred'},
            {'skill': 'Project Management', 'proficiency': 'beginner', 'importance': 'nice_to_have'},
        ],
        'experience_requirements': {
            'min_years': {'entry': 0, 'mid': 2, 'senior': 5, 'lead': 8, 'executive': 10}.get(level, 2),
            'max_years': {'entry': 2, 'mid': 5, 'senior': 10, 'lead': 15, 'executive': 20}.get(level, 5),
            'level': level
        }
    }

def _match_and_create_user_skills(user, extracted_skills):
    """Match extracted skills with database and create/update user skills"""
    skill_matcher = SkillMatcher()
    user_skills = []
    
    for skill_type, skills in extracted_skills.items():
        for skill_name in skills:
            # Normalize skill name
            normalized_name = skill_matcher.normalize_skill_name(skill_name)
            
            # Find or create skill in database
            skill, created = Skill.objects.get_or_create(
                name=normalized_name,
                defaults={
                    'skill_type': skill_type,
                    'category_id': 1,  # Default category - would be more sophisticated
                    'description': f'{normalized_name} skill'
                }
            )
            
            # Create or update user skill
            user_skill, created = UserSkill.objects.get_or_create(
                user=user,
                skill=skill,
                defaults={
                    'proficiency_level': 'intermediate',  # Default - could be inferred
                    'verification_method': 'resume_extracted',
                    'learning_status': 'proficient'
                }
            )
            
            user_skills.append({
                'skill_name': skill.name,
                'proficiency_level': user_skill.proficiency_level,
                'years_of_experience': user_skill.years_of_experience,
                'skill_type': skill.skill_type
            })
    
    return user_skills

def _create_skill_gap_records(analysis, skill_gaps):
    """Create individual skill gap records"""
    for gap_data in skill_gaps:
        # Find skill in database
        skill = Skill.objects.filter(name__iexact=gap_data['skill']).first()
        if not skill:
            # Create skill if it doesn't exist
            skill = Skill.objects.create(
                name=gap_data['skill'],
                skill_type='technical',  # Default
                category_id=1  # Default category
            )
        
        SkillGap.objects.create(
            analysis=analysis,
            skill=skill,
            gap_type=gap_data['gap_type'],
            current_level=gap_data.get('current_level'),
            required_level=gap_data['required_level'],
            importance=gap_data['importance'],
            gap_score=gap_data.get('gap_score', 50.0),
            priority=gap_data['priority'],
            estimated_learning_time=gap_data['estimated_learning_time'],
            learning_resources=gap_data.get('learning_resources', [])
        )
