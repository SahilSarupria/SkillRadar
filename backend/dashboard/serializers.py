from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from .models import UserActivity, UserStats, SystemStats

User = get_user_model()

class UserActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserActivity
        fields = [
            'id', 'activity_type', 'description', 'metadata',
            'created_at'
        ]

class UserStatsSerializer(serializers.ModelSerializer):
    engagement_score = serializers.SerializerMethodField()
    completion_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = UserStats
        fields = [
            'total_resumes', 'total_conversions', 'total_analyses',
            'total_skills_identified', 'total_skill_gaps',
            'total_recommendations_received', 'total_courses_bookmarked',
            'total_courses_started', 'total_courses_completed',
            'total_logins', 'last_active', 'streak_days',
            'engagement_score', 'completion_rate'
        ]
    
    def get_engagement_score(self, obj):
        """Calculate user engagement score (0-100)"""
        score = 0
        
        # Resume activity (30 points max)
        if obj.total_resumes > 0:
            score += min(obj.total_resumes * 5, 15)
        if obj.total_analyses > 0:
            score += min(obj.total_analyses * 3, 15)
        
        # Learning activity (40 points max)
        if obj.total_recommendations_received > 0:
            score += min(obj.total_recommendations_received * 2, 20)
        if obj.total_courses_started > 0:
            score += min(obj.total_courses_started * 4, 20)
        
        # Consistency (30 points max)
        score += min(obj.streak_days * 2, 20)
        score += min(obj.total_logins, 10)
        
        return min(score, 100)
    
    def get_completion_rate(self, obj):
        """Calculate course completion rate"""
        if obj.total_courses_started == 0:
            return 0
        return round((obj.total_courses_completed / obj.total_courses_started) * 100, 1)

class DashboardSummarySerializer(serializers.Serializer):
    """Summary data for user dashboard"""
    user_stats = UserStatsSerializer()
    recent_activities = UserActivitySerializer(many=True)
    
    # Resume summary
    recent_resumes = serializers.ListField()
    pending_analyses = serializers.IntegerField()
    
    # Skill summary
    top_skills = serializers.ListField()
    critical_skill_gaps = serializers.ListField()
    
    # Recommendation summary
    new_recommendations = serializers.IntegerField()
    bookmarked_courses = serializers.ListField()
    in_progress_courses = serializers.ListField()
    
    # Goals and progress
    weekly_goal_progress = serializers.DictField()
    monthly_achievements = serializers.ListField()

class SystemStatsSerializer(serializers.ModelSerializer):
    growth_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = SystemStats
        fields = [
            'date', 'total_users', 'new_users', 'active_users',
            'total_resumes', 'new_resumes', 'total_conversions',
            'total_analyses', 'total_recommendations', 'new_recommendations',
            'total_courses', 'total_bookmarks', 'growth_rate'
        ]
    
    def get_growth_rate(self, obj):
        """Calculate growth rate compared to previous day"""
        try:
            previous_day = SystemStats.objects.get(
                date=obj.date - timedelta(days=1)
            )
            if previous_day.total_users > 0:
                growth = ((obj.total_users - previous_day.total_users) / previous_day.total_users) * 100
                return round(growth, 2)
        except SystemStats.DoesNotExist:
            pass
        return 0

class AnalyticsSerializer(serializers.Serializer):
    """Analytics data for charts and graphs"""
    user_growth = serializers.ListField()
    resume_activity = serializers.ListField()
    skill_trends = serializers.ListField()
    recommendation_effectiveness = serializers.ListField()
    platform_popularity = serializers.ListField()
    
    # Time-based analytics
    daily_active_users = serializers.ListField()
    weekly_conversions = serializers.ListField()
    monthly_completions = serializers.ListField()
