from django.db import models
from django.contrib.auth import get_user_model
from resumes.models import Resume
from analyzer.models import ResumeAnalysis
import uuid

User = get_user_model()

class SkillCategory(models.Model):
    """Categories for organizing skills"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Icon class or name")
    color = models.CharField(max_length=7, default="#3B82F6", help_text="Hex color code")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Skill Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Skill(models.Model):
    """Individual skills database"""
    SKILL_TYPES = [
        ('technical', 'Technical'),
        ('soft', 'Soft Skill'),
        ('language', 'Language'),
        ('certification', 'Certification'),
        ('tool', 'Tool/Software'),
    ]
    
    PROFICIENCY_LEVELS = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert'),
    ]
    
    name = models.CharField(max_length=200, unique=True)
    category = models.ForeignKey(SkillCategory, on_delete=models.CASCADE, related_name='skills')
    skill_type = models.CharField(max_length=20, choices=SKILL_TYPES)
    description = models.TextField(blank=True)
    aliases = models.JSONField(default=list, help_text="Alternative names for this skill")
    
    # Industry relevance
    industries = models.JSONField(default=list, help_text="Industries where this skill is relevant")
    job_roles = models.JSONField(default=list, help_text="Job roles that require this skill")
    
    # Skill metadata
    difficulty_level = models.CharField(max_length=20, choices=PROFICIENCY_LEVELS, default='intermediate')
    average_learning_time_hours = models.PositiveIntegerField(default=40, help_text="Average hours to learn")
    prerequisites = models.ManyToManyField('self', blank=True, symmetrical=False, related_name='dependent_skills')
    
    # Popularity and demand
    demand_score = models.FloatField(default=50.0, help_text="Market demand score (0-100)")
    popularity_score = models.FloatField(default=50.0, help_text="Popularity score (0-100)")
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['skill_type']),
            models.Index(fields=['category']),
            models.Index(fields=['demand_score']),
        ]
    
    def __str__(self):
        return self.name

class JobRole(models.Model):
    """Job roles with required skills"""
    title = models.CharField(max_length=200)
    industry = models.CharField(max_length=100)
    level = models.CharField(max_length=50, choices=[
        ('entry', 'Entry Level'),
        ('mid', 'Mid Level'),
        ('senior', 'Senior Level'),
        ('lead', 'Lead/Principal'),
        ('executive', 'Executive'),
    ])
    
    description = models.TextField(blank=True)
    required_skills = models.ManyToManyField(Skill, through='JobRoleSkill', related_name='required_for_roles')
    
    # Salary and market data
    average_salary_min = models.PositiveIntegerField(default=0)
    average_salary_max = models.PositiveIntegerField(default=0)
    job_growth_rate = models.FloatField(default=0.0, help_text="Annual job growth rate percentage")
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['title', 'industry', 'level']
        ordering = ['industry', 'title', 'level']
    
    def __str__(self):
        return f"{self.title} - {self.industry} ({self.level})"

class JobRoleSkill(models.Model):
    """Through model for JobRole-Skill relationship with importance"""
    job_role = models.ForeignKey(JobRole, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    importance = models.CharField(max_length=20, choices=[
        ('required', 'Required'),
        ('preferred', 'Preferred'),
        ('nice_to_have', 'Nice to Have'),
    ], default='required')
    min_proficiency = models.CharField(max_length=20, choices=Skill.PROFICIENCY_LEVELS, default='intermediate')
    weight = models.FloatField(default=1.0, help_text="Importance weight (0-10)")
    
    class Meta:
        unique_together = ['job_role', 'skill']
    
    def __str__(self):
        return f"{self.job_role.title} - {self.skill.name} ({self.importance})"

class UserSkill(models.Model):
    """User's current skills and proficiency levels"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='skills')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    proficiency_level = models.CharField(max_length=20, choices=Skill.PROFICIENCY_LEVELS)
    
    # Skill validation
    is_verified = models.BooleanField(default=False)
    verification_method = models.CharField(max_length=50, blank=True, choices=[
        ('self_assessed', 'Self Assessed'),
        ('resume_extracted', 'Extracted from Resume'),
        ('test_verified', 'Test Verified'),
        ('certification', 'Certification'),
        ('experience', 'Work Experience'),
    ])
    
    # Experience with skill
    years_of_experience = models.FloatField(default=0.0)
    last_used = models.DateField(blank=True, null=True)
    
    # Learning progress
    learning_status = models.CharField(max_length=20, choices=[
        ('not_started', 'Not Started'),
        ('learning', 'Currently Learning'),
        ('proficient', 'Proficient'),
        ('mastered', 'Mastered'),
    ], default='proficient')
    
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'skill']
        ordering = ['-proficiency_level', 'skill__name']
    
    def __str__(self):
        return f"{self.user.email} - {self.skill.name} ({self.proficiency_level})"

class SkillGapAnalysis(models.Model):
    """Analysis of skill gaps for specific job targets"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='skill_gap_analyses')
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, blank=True, null=True)
    resume_analysis = models.ForeignKey(ResumeAnalysis, on_delete=models.CASCADE, blank=True, null=True)
    
    # Target job information
    target_job_role = models.ForeignKey(JobRole, on_delete=models.CASCADE, blank=True, null=True)
    target_job_title = models.CharField(max_length=200)
    target_industry = models.CharField(max_length=100)
    target_level = models.CharField(max_length=50, choices=JobRole._meta.get_field('level').choices)
    
    # Analysis results
    overall_match_score = models.FloatField(default=0.0, help_text="Overall skill match percentage")
    skills_matched = models.PositiveIntegerField(default=0)
    skills_missing = models.PositiveIntegerField(default=0)
    skills_to_improve = models.PositiveIntegerField(default=0)
    
    # Detailed analysis data
    analysis_data = models.JSONField(default=dict, help_text="Detailed gap analysis results")
    recommendations = models.JSONField(default=list, help_text="Skill development recommendations")
    learning_path = models.JSONField(default=list, help_text="Suggested learning path")
    
    # Metadata
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ], default='pending')
    processing_time = models.FloatField(default=0.0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"Skill Gap Analysis - {self.target_job_title} for {self.user.email}"

class SkillGap(models.Model):
    """Individual skill gaps identified in analysis"""
    analysis = models.ForeignKey(SkillGapAnalysis, on_delete=models.CASCADE, related_name='skill_gaps')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    
    gap_type = models.CharField(max_length=20, choices=[
        ('missing', 'Missing Skill'),
        ('insufficient', 'Insufficient Proficiency'),
        ('outdated', 'Outdated Knowledge'),
        ('improvement', 'Needs Improvement'),
    ])
    
    current_level = models.CharField(max_length=20, choices=Skill.PROFICIENCY_LEVELS, blank=True, null=True)
    required_level = models.CharField(max_length=20, choices=Skill.PROFICIENCY_LEVELS)
    importance = models.CharField(max_length=20, choices=JobRoleSkill._meta.get_field('importance').choices)
    
    # Gap metrics
    gap_score = models.FloatField(default=0.0, help_text="Gap severity score (0-100)")
    priority = models.CharField(max_length=20, choices=[
        ('low', 'Low Priority'),
        ('medium', 'Medium Priority'),
        ('high', 'High Priority'),
        ('critical', 'Critical'),
    ], default='medium')
    
    # Learning recommendations
    estimated_learning_time = models.PositiveIntegerField(default=0, help_text="Estimated hours to close gap")
    learning_resources = models.JSONField(default=list, help_text="Recommended learning resources")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['analysis', 'skill']
        ordering = ['-gap_score', 'skill__name']
    
    def __str__(self):
        return f"{self.skill.name} - {self.gap_type} ({self.priority})"

class LearningPath(models.Model):
    """Structured learning paths for skill development"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='learning_paths')
    skill_gap_analysis = models.ForeignKey(SkillGapAnalysis, on_delete=models.CASCADE, blank=True, null=True)
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    target_skills = models.ManyToManyField(Skill, related_name='learning_paths')
    
    # Path metadata
    difficulty_level = models.CharField(max_length=20, choices=Skill.PROFICIENCY_LEVELS)
    estimated_duration_weeks = models.PositiveIntegerField(default=12)
    estimated_hours_per_week = models.PositiveIntegerField(default=5)
    
    # Progress tracking
    status = models.CharField(max_length=20, choices=[
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('paused', 'Paused'),
    ], default='not_started')
    
    progress_percentage = models.FloatField(default=0.0)
    started_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.user.email}"

class LearningPathStep(models.Model):
    """Individual steps in a learning path"""
    learning_path = models.ForeignKey(LearningPath, on_delete=models.CASCADE, related_name='steps')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    order = models.PositiveIntegerField()
    
    # Step requirements
    prerequisites = models.ManyToManyField('self', blank=True, symmetrical=False)
    estimated_hours = models.PositiveIntegerField(default=10)
    
    # Resources and materials
    resources = models.JSONField(default=list, help_text="Learning resources for this step")
    
    # Progress tracking
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['learning_path', 'order']
        ordering = ['order']
    
    def __str__(self):
        return f"{self.learning_path.title} - Step {self.order}: {self.title}"

class SkillAssessment(models.Model):
    """Skill assessments and tests"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='skill_assessments')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    
    assessment_type = models.CharField(max_length=20, choices=[
        ('self_assessment', 'Self Assessment'),
        ('quiz', 'Quiz'),
        ('practical', 'Practical Test'),
        ('project', 'Project-based'),
    ])
    
    # Assessment results
    score = models.FloatField(default=0.0, help_text="Assessment score (0-100)")
    proficiency_determined = models.CharField(max_length=20, choices=Skill.PROFICIENCY_LEVELS, blank=True)
    
    # Assessment data
    questions_total = models.PositiveIntegerField(default=0)
    questions_correct = models.PositiveIntegerField(default=0)
    time_taken_minutes = models.PositiveIntegerField(default=0)
    
    assessment_data = models.JSONField(default=dict, help_text="Detailed assessment results")
    feedback = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.skill.name} Assessment ({self.score}%)"
