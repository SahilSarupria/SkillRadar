from rest_framework import serializers
from .models import (
    ResumeAnalysis, KeywordAnalysis, ATSCompatibility, 
    ContentAnalysis, IndustryAnalysis, AnalysisTemplate
)

class KeywordAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = KeywordAnalysis
        fields = '__all__'
        read_only_fields = ('analysis', 'created_at')

class ATSCompatibilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = ATSCompatibility
        fields = '__all__'
        read_only_fields = ('analysis', 'created_at')

class ContentAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentAnalysis
        fields = '__all__'
        read_only_fields = ('analysis', 'created_at')

class IndustryAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = IndustryAnalysis
        fields = '__all__'
        read_only_fields = ('analysis', 'created_at')

class ResumeAnalysisSerializer(serializers.ModelSerializer):
    keyword_analysis = KeywordAnalysisSerializer(read_only=True)
    ats_compatibility = ATSCompatibilitySerializer(read_only=True)
    content_analysis = ContentAnalysisSerializer(read_only=True)
    industry_analysis = IndustryAnalysisSerializer(read_only=True)
    
    class Meta:
        model = ResumeAnalysis
        fields = '__all__'
        read_only_fields = ('id', 'user', 'created_at', 'updated_at', 'processing_time')

class ResumeAnalysisListSerializer(serializers.ModelSerializer):
    resume_title = serializers.CharField(source='resume.title', read_only=True)
    
    class Meta:
        model = ResumeAnalysis
        fields = ('id', 'resume', 'resume_title', 'analysis_type', 'status', 
                 'overall_score', 'ats_score', 'content_score', 'keyword_score', 
                 'created_at', 'target_job_title', 'target_industry')

class AnalyzeResumeSerializer(serializers.Serializer):
    resume_id = serializers.UUIDField(help_text="ID of the resume to analyze")
    analysis_type = serializers.ChoiceField(
        choices=[
            ('comprehensive', 'Comprehensive Analysis'),
            ('ats_scan', 'ATS Compatibility Scan'),
            ('content_analysis', 'Content Analysis'),
            ('keyword_analysis', 'Keyword Analysis'),
            ('industry_analysis', 'Industry-Specific Analysis'),
        ],
        default='comprehensive',
        help_text="Type of analysis to perform"
    )
    target_job_title = serializers.CharField(
        max_length=200, 
        required=False, 
        help_text="Target job title for analysis"
    )
    target_industry = serializers.CharField(
        max_length=100, 
        required=False, 
        help_text="Target industry for analysis"
    )

class AnalysisTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalysisTemplate
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class QuickAnalysisSerializer(serializers.Serializer):
    """For quick analysis without saving to database"""
    resume_text = serializers.CharField(max_length=50000, help_text="Resume text to analyze")
    target_job_title = serializers.CharField(max_length=200, required=False)
    target_industry = serializers.CharField(max_length=100, required=False)
