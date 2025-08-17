from django.db import models
from django.contrib.auth import get_user_model
from resumes.models import Resume
import uuid

User = get_user_model()

class ResumeAnalysis(models.Model):
    ANALYSIS_TYPES = [
        ('ats_scan', 'ATS Compatibility Scan'),
        ('content_analysis', 'Content Analysis'),
        ('keyword_analysis', 'Keyword Analysis'),
        ('format_analysis', 'Format Analysis'),
        ('industry_analysis', 'Industry-Specific Analysis'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='analyses')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resume_analyses')
    analysis_type = models.CharField(max_length=50, choices=ANALYSIS_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Analysis Results
    overall_score = models.FloatField(default=0.0, help_text="Overall score out of 100")
    ats_score = models.FloatField(default=0.0, help_text="ATS compatibility score out of 100")
    content_score = models.FloatField(default=0.0, help_text="Content quality score out of 100")
    format_score = models.FloatField(default=0.0, help_text="Format score out of 100")
    keyword_score = models.FloatField(default=0.0, help_text="Keyword optimization score out of 100")
    
    # Detailed Analysis Data
    analysis_data = models.JSONField(default=dict, help_text="Detailed analysis results")
    suggestions = models.JSONField(default=list, help_text="Improvement suggestions")
    strengths = models.JSONField(default=list, help_text="Resume strengths")
    weaknesses = models.JSONField(default=list, help_text="Areas for improvement")
    
    # Metadata
    processing_time = models.FloatField(default=0.0)
    target_job_title = models.CharField(max_length=200, blank=True, help_text="Target job for analysis")
    target_industry = models.CharField(max_length=100, blank=True, help_text="Target industry")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['resume', '-created_at']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"Analysis for {self.resume.title} - {self.get_analysis_type_display()}"

class KeywordAnalysis(models.Model):
    analysis = models.OneToOneField(ResumeAnalysis, on_delete=models.CASCADE, related_name='keyword_analysis')
    
    # Keyword Data
    found_keywords = models.JSONField(default=list, help_text="Keywords found in resume")
    missing_keywords = models.JSONField(default=list, help_text="Important keywords missing")
    keyword_density = models.JSONField(default=dict, help_text="Keyword frequency analysis")
    industry_keywords = models.JSONField(default=list, help_text="Industry-specific keywords")
    skill_keywords = models.JSONField(default=list, help_text="Technical skill keywords")
    
    # Scores
    keyword_match_percentage = models.FloatField(default=0.0)
    industry_relevance_score = models.FloatField(default=0.0)
    skill_coverage_score = models.FloatField(default=0.0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Keyword Analysis for {self.analysis.resume.title}"

class ATSCompatibility(models.Model):
    analysis = models.OneToOneField(ResumeAnalysis, on_delete=models.CASCADE, related_name='ats_compatibility')
    
    # ATS Factors
    has_contact_info = models.BooleanField(default=False)
    has_clear_sections = models.BooleanField(default=False)
    uses_standard_fonts = models.BooleanField(default=False)
    has_keywords = models.BooleanField(default=False)
    proper_formatting = models.BooleanField(default=False)
    no_images_or_graphics = models.BooleanField(default=False)
    readable_file_format = models.BooleanField(default=False)
    
    # Detailed Checks
    formatting_issues = models.JSONField(default=list, help_text="List of formatting issues")
    missing_sections = models.JSONField(default=list, help_text="Missing resume sections")
    optimization_tips = models.JSONField(default=list, help_text="ATS optimization tips")
    
    # Scores
    readability_score = models.FloatField(default=0.0)
    structure_score = models.FloatField(default=0.0)
    content_extraction_score = models.FloatField(default=0.0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"ATS Compatibility for {self.analysis.resume.title}"

class ContentAnalysis(models.Model):
    analysis = models.OneToOneField(ResumeAnalysis, on_delete=models.CASCADE, related_name='content_analysis')
    
    # Content Metrics
    word_count = models.PositiveIntegerField(default=0)
    sentence_count = models.PositiveIntegerField(default=0)
    paragraph_count = models.PositiveIntegerField(default=0)
    bullet_points_count = models.PositiveIntegerField(default=0)
    
    # Content Quality
    readability_score = models.FloatField(default=0.0, help_text="Flesch reading ease score")
    action_verbs_count = models.PositiveIntegerField(default=0)
    quantified_achievements = models.PositiveIntegerField(default=0)
    
    # Content Analysis
    tone_analysis = models.JSONField(default=dict, help_text="Professional tone analysis")
    grammar_issues = models.JSONField(default=list, help_text="Grammar and spelling issues")
    content_suggestions = models.JSONField(default=list, help_text="Content improvement suggestions")
    
    # Section Analysis
    section_completeness = models.JSONField(default=dict, help_text="Completeness of each section")
    section_quality_scores = models.JSONField(default=dict, help_text="Quality score for each section")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Content Analysis for {self.analysis.resume.title}"

class IndustryAnalysis(models.Model):
    analysis = models.OneToOneField(ResumeAnalysis, on_delete=models.CASCADE, related_name='industry_analysis')
    
    # Industry Matching
    detected_industries = models.JSONField(default=list, help_text="Industries the resume fits")
    industry_match_scores = models.JSONField(default=dict, help_text="Match scores for different industries")
    target_industry_fit = models.FloatField(default=0.0, help_text="Fit score for target industry")
    
    # Industry-Specific Analysis
    required_skills_present = models.JSONField(default=list, help_text="Required skills found")
    missing_skills = models.JSONField(default=list, help_text="Important skills missing")
    industry_keywords_found = models.JSONField(default=list, help_text="Industry keywords found")
    
    # Recommendations
    industry_specific_tips = models.JSONField(default=list, help_text="Industry-specific improvement tips")
    role_alignment_score = models.FloatField(default=0.0, help_text="Alignment with target role")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Industry Analysis for {self.analysis.resume.title}"

class AnalysisTemplate(models.Model):
    """Templates for different types of analysis based on job roles/industries"""
    
    name = models.CharField(max_length=200, unique=True)
    industry = models.CharField(max_length=100)
    job_role = models.CharField(max_length=200, blank=True)
    
    # Analysis Criteria
    required_keywords = models.JSONField(default=list, help_text="Keywords that should be present")
    preferred_keywords = models.JSONField(default=list, help_text="Keywords that are nice to have")
    required_sections = models.JSONField(default=list, help_text="Resume sections that must be present")
    scoring_weights = models.JSONField(default=dict, help_text="Weights for different scoring criteria")
    
    # Industry Standards
    min_experience_years = models.PositiveIntegerField(default=0)
    preferred_education_level = models.CharField(max_length=100, blank=True)
    key_skills = models.JSONField(default=list, help_text="Key skills for this role/industry")
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['industry', 'job_role']
    
    def __str__(self):
        return f"{self.name} - {self.industry}"
