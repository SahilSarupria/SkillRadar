from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    LearningPlatform, Course, Skill, UserRecommendation, 
    LearningPath, UserProgress, AffiliateClick
)

User = get_user_model()

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'name', 'category', 'description']

class LearningPlatformSerializer(serializers.ModelSerializer):
    total_courses = serializers.SerializerMethodField()
    
    class Meta:
        model = LearningPlatform
        fields = [
            'id', 'name', 'description', 'website_url', 'logo_url',
            'is_active', 'total_courses', 'created_at'
        ]
    
    def get_total_courses(self, obj):
        return obj.courses.filter(is_active=True).count()

class CourseSerializer(serializers.ModelSerializer):
    platform = LearningPlatformSerializer(read_only=True)
    skills_taught = SkillSerializer(many=True, read_only=True)
    affiliate_link = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = [
            'id', 'platform', 'title', 'description', 'instructor_name',
            'duration_hours', 'level', 'rating', 'total_students', 'price',
            'is_free', 'has_certificate', 'language', 'course_url',
            'affiliate_link', 'thumbnail_url', 'skills_taught', 'last_updated'
        ]
    
    def get_affiliate_link(self, obj):
        from .utils import AffiliateManager
        
        request = self.context.get('request')
        user = request.user if request and request.user.is_authenticated else None
        
        affiliate_manager = AffiliateManager()
        return affiliate_manager.generate_affiliate_link(obj, user)

class CourseRecommendationSerializer(serializers.Serializer):
    course = CourseSerializer(read_only=True)
    target_skill = SkillSerializer(read_only=True)
    relevance_score = serializers.FloatField()
    recommendation_type = serializers.CharField()
    recommendation_reason = serializers.CharField()
    priority = serializers.CharField()

class UserRecommendationSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    target_skill = SkillSerializer(read_only=True)
    
    class Meta:
        model = UserRecommendation
        fields = [
            'id', 'course', 'target_skill', 'relevance_score',
            'recommendation_type', 'recommendation_reason', 'priority',
            'is_bookmarked', 'is_completed', 'created_at'
        ]

class LearningPathSerializer(serializers.ModelSerializer):
    recommended_courses = CourseSerializer(many=True, read_only=True)
    skills = SkillSerializer(many=True, read_only=True)
    progress_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = LearningPath
        fields = [
            'id', 'title', 'description', 'skills', 'estimated_weeks',
            'estimated_cost', 'difficulty_level', 'relevance_score',
            'recommended_courses', 'progress_percentage', 'created_at'
        ]
    
    def get_progress_percentage(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return 0
        
        try:
            progress = UserProgress.objects.get(user=request.user, learning_path=obj)
            return progress.progress_percentage
        except UserProgress.DoesNotExist:
            return 0

class UserProgressSerializer(serializers.ModelSerializer):
    learning_path = LearningPathSerializer(read_only=True)
    completed_courses = CourseSerializer(many=True, read_only=True)
    
    class Meta:
        model = UserProgress
        fields = [
            'id', 'learning_path', 'progress_percentage', 'completed_courses',
            'current_course', 'started_at', 'estimated_completion_date',
            'actual_completion_date', 'is_completed'
        ]

class RecommendationRequestSerializer(serializers.Serializer):
    skill_gaps = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        help_text="List of skill gaps from skill analysis"
    )
    learning_goals = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        help_text="User's learning goals"
    )
    career_goal = serializers.CharField(
        required=False,
        max_length=500,
        help_text="User's career goal"
    )
    limit = serializers.IntegerField(
        default=10,
        min_value=1,
        max_value=50,
        help_text="Maximum number of recommendations"
    )
    include_paid = serializers.BooleanField(
        default=True,
        help_text="Include paid courses in recommendations"
    )
    include_free = serializers.BooleanField(
        default=True,
        help_text="Include free courses in recommendations"
    )
    preferred_platforms = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text="Preferred learning platforms"
    )

class LearningPathRequestSerializer(serializers.Serializer):
    skill_gaps = serializers.ListField(
        child=serializers.DictField(),
        required=True,
        help_text="List of skill gaps from skill analysis"
    )
    career_goal = serializers.CharField(
        required=False,
        max_length=500,
        help_text="User's career goal"
    )
    time_commitment_hours_per_week = serializers.IntegerField(
        default=10,
        min_value=1,
        max_value=40,
        help_text="Hours per week user can dedicate to learning"
    )
    budget_limit = serializers.DecimalField(
        required=False,
        max_digits=10,
        decimal_places=2,
        help_text="Maximum budget for learning path"
    )

class BookmarkCourseSerializer(serializers.Serializer):
    course_id = serializers.IntegerField()
    
    def validate_course_id(self, value):
        try:
            Course.objects.get(id=value, is_active=True)
            return value
        except Course.DoesNotExist:
            raise serializers.ValidationError("Course not found or inactive")

class CourseProgressSerializer(serializers.Serializer):
    course_id = serializers.IntegerField()
    progress_percentage = serializers.IntegerField(min_value=0, max_value=100)
    is_completed = serializers.BooleanField(default=False)
    
    def validate_course_id(self, value):
        try:
            Course.objects.get(id=value, is_active=True)
            return value
        except Course.DoesNotExist:
            raise serializers.ValidationError("Course not found or inactive")
