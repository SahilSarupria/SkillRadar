from rest_framework import serializers
from .models import (
    SkillCategory, Skill, JobRole, JobRoleSkill, UserSkill,
    SkillGapAnalysis, SkillGap, LearningPath, LearningPathStep,
    SkillAssessment
)

class SkillCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SkillCategory
        fields = '__all__'

class SkillSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Skill
        fields = '__all__'

class JobRoleSkillSerializer(serializers.ModelSerializer):
    skill_name = serializers.CharField(source='skill.name', read_only=True)
    skill_type = serializers.CharField(source='skill.skill_type', read_only=True)
    
    class Meta:
        model = JobRoleSkill
        fields = '__all__'

class JobRoleSerializer(serializers.ModelSerializer):
    required_skills = JobRoleSkillSerializer(source='jobrole_skill_set', many=True, read_only=True)
    
    class Meta:
        model = JobRole
        fields = '__all__'

class UserSkillSerializer(serializers.ModelSerializer):
    skill_name = serializers.CharField(source='skill.name', read_only=True)
    skill_category = serializers.CharField(source='skill.category.name', read_only=True)
    skill_type = serializers.CharField(source='skill.skill_type', read_only=True)
    
    class Meta:
        model = UserSkill
        fields = '__all__'
        read_only_fields = ('user',)

class SkillGapSerializer(serializers.ModelSerializer):
    skill_name = serializers.CharField(source='skill.name', read_only=True)
    skill_category = serializers.CharField(source='skill.category.name', read_only=True)
    
    class Meta:
        model = SkillGap
        fields = '__all__'

class SkillGapAnalysisSerializer(serializers.ModelSerializer):
    skill_gaps = SkillGapSerializer(many=True, read_only=True)
    resume_title = serializers.CharField(source='resume.title', read_only=True)
    
    class Meta:
        model = SkillGapAnalysis
        fields = '__all__'
        read_only_fields = ('id', 'user', 'created_at', 'updated_at', 'processing_time')

class SkillGapAnalysisListSerializer(serializers.ModelSerializer):
    resume_title = serializers.CharField(source='resume.title', read_only=True)
    
    class Meta:
        model = SkillGapAnalysis
        fields = ('id', 'target_job_title', 'target_industry', 'target_level', 
                 'overall_match_score', 'skills_matched', 'skills_missing', 
                 'skills_to_improve', 'status', 'created_at', 'resume_title')

class LearningPathStepSerializer(serializers.ModelSerializer):
    skill_name = serializers.CharField(source='skill.name', read_only=True)
    
    class Meta:
        model = LearningPathStep
        fields = '__all__'

class LearningPathSerializer(serializers.ModelSerializer):
    steps = LearningPathStepSerializer(many=True, read_only=True)
    target_skill_names = serializers.StringRelatedField(source='target_skills', many=True, read_only=True)
    
    class Meta:
        model = LearningPath
        fields = '__all__'
        read_only_fields = ('id', 'user', 'created_at', 'updated_at')

class SkillAssessmentSerializer(serializers.ModelSerializer):
    skill_name = serializers.CharField(source='skill.name', read_only=True)
    
    class Meta:
        model = SkillAssessment
        fields = '__all__'
        read_only_fields = ('id', 'user', 'created_at')

# Request serializers
class AnalyzeSkillGapSerializer(serializers.Serializer):
    resume_id = serializers.UUIDField(help_text="ID of the resume to analyze")
    target_job_title = serializers.CharField(max_length=200, help_text="Target job title")
    target_industry = serializers.CharField(max_length=100, help_text="Target industry")
    target_level = serializers.ChoiceField(
        choices=JobRole._meta.get_field('level').choices,
        help_text="Target job level"
    )
    job_description = serializers.CharField(
        max_length=10000, 
        required=False, 
        help_text="Optional job description for more accurate analysis"
    )

class ExtractSkillsSerializer(serializers.Serializer):
    text_content = serializers.CharField(max_length=50000, help_text="Text to extract skills from")
    content_type = serializers.ChoiceField(
        choices=[
            ('resume', 'Resume'),
            ('job_description', 'Job Description'),
            ('profile', 'Profile Text'),
        ],
        default='resume',
        help_text="Type of content being analyzed"
    )

class UpdateUserSkillSerializer(serializers.Serializer):
    skill_id = serializers.IntegerField(help_text="ID of the skill")
    proficiency_level = serializers.ChoiceField(
        choices=Skill.PROFICIENCY_LEVELS,
        help_text="User's proficiency level"
    )
    years_of_experience = serializers.FloatField(default=0.0, help_text="Years of experience")
    verification_method = serializers.ChoiceField(
        choices=UserSkill._meta.get_field('verification_method').choices,
        default='self_assessed',
        help_text="How the skill was verified"
    )
    notes = serializers.CharField(max_length=500, required=False, help_text="Additional notes")

class CreateLearningPathSerializer(serializers.Serializer):
    skill_gap_analysis_id = serializers.UUIDField(help_text="ID of the skill gap analysis")
    title = serializers.CharField(max_length=200, help_text="Learning path title")
    target_skills = serializers.ListField(
        child=serializers.IntegerField(),
        help_text="List of skill IDs to include in learning path"
    )
    estimated_duration_weeks = serializers.IntegerField(default=12, help_text="Estimated duration in weeks")
    estimated_hours_per_week = serializers.IntegerField(default=5, help_text="Estimated hours per week")

class SkillSearchSerializer(serializers.Serializer):
    query = serializers.CharField(max_length=200, help_text="Search query")
    skill_type = serializers.ChoiceField(
        choices=Skill.SKILL_TYPES,
        required=False,
        help_text="Filter by skill type"
    )
    category = serializers.IntegerField(required=False, help_text="Filter by category ID")
    industry = serializers.CharField(max_length=100, required=False, help_text="Filter by industry")
