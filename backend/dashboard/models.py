from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

class UserActivity(models.Model):
    """Track user activity and engagement"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=50, choices=[
        ('login', 'Login'),
        ('resume_upload', 'Resume Upload'),
        ('resume_convert', 'Resume Convert'),
        ('resume_analyze', 'Resume Analyze'),
        ('skill_analysis', 'Skill Analysis'),
        ('view_recommendations', 'View Recommendations'),
        ('bookmark_course', 'Bookmark Course'),
        ('start_course', 'Start Course'),
        ('complete_course', 'Complete Course'),
    ])
    description = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'activity_type']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.activity_type} at {self.created_at}"

class UserStats(models.Model):
    """Aggregated user statistics"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='stats')
    
    # Resume stats
    total_resumes = models.IntegerField(default=0)
    total_conversions = models.IntegerField(default=0)
    total_analyses = models.IntegerField(default=0)
    
    # Skill stats
    total_skills_identified = models.IntegerField(default=0)
    total_skill_gaps = models.IntegerField(default=0)
    
    # Recommendation stats
    total_recommendations_received = models.IntegerField(default=0)
    total_courses_bookmarked = models.IntegerField(default=0)
    total_courses_started = models.IntegerField(default=0)
    total_courses_completed = models.IntegerField(default=0)
    
    # Engagement stats
    total_logins = models.IntegerField(default=0)
    last_active = models.DateTimeField(null=True, blank=True)
    streak_days = models.IntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Stats for {self.user.email}"
    
    def update_stats(self):
        """Update all statistics for this user"""
        from resumes.models import Resume, ResumeAnalysis
        from skills.models import SkillGapAnalysis
        from recommendations.models import UserRecommendation
        
        # Resume stats
        self.total_resumes = Resume.objects.filter(user=self.user).count()
        self.total_conversions = Resume.objects.filter(user=self.user, conversion_status='completed').count()
        self.total_analyses = ResumeAnalysis.objects.filter(resume__user=self.user).count()
        
        # Skill stats
        skill_analyses = SkillGapAnalysis.objects.filter(user=self.user)
        self.total_skills_identified = sum(len(analysis.current_skills) for analysis in skill_analyses)
        self.total_skill_gaps = sum(len(analysis.skill_gaps) for analysis in skill_analyses)
        
        # Recommendation stats
        recommendations = UserRecommendation.objects.filter(user=self.user)
        self.total_recommendations_received = recommendations.count()
        self.total_courses_bookmarked = recommendations.filter(is_bookmarked=True).count()
        self.total_courses_started = recommendations.filter(progress_percentage__gt=0).count()
        self.total_courses_completed = recommendations.filter(is_completed=True).count()
        
        # Activity stats
        activities = UserActivity.objects.filter(user=self.user)
        self.total_logins = activities.filter(activity_type='login').count()
        
        # Calculate streak
        self.streak_days = self._calculate_streak()
        
        self.save()
    
    def _calculate_streak(self):
        """Calculate current login streak"""
        activities = UserActivity.objects.filter(
            user=self.user,
            activity_type='login'
        ).order_by('-created_at')
        
        if not activities.exists():
            return 0
        
        streak = 0
        current_date = timezone.now().date()
        
        for activity in activities:
            activity_date = activity.created_at.date()
            
            if activity_date == current_date or activity_date == current_date - timedelta(days=streak):
                if activity_date == current_date - timedelta(days=streak):
                    streak += 1
                current_date = activity_date
            else:
                break
        
        return streak

class SystemStats(models.Model):
    """System-wide statistics"""
    date = models.DateField(unique=True)
    
    # User stats
    total_users = models.IntegerField(default=0)
    new_users = models.IntegerField(default=0)
    active_users = models.IntegerField(default=0)
    
    # Resume stats
    total_resumes = models.IntegerField(default=0)
    new_resumes = models.IntegerField(default=0)
    total_conversions = models.IntegerField(default=0)
    total_analyses = models.IntegerField(default=0)
    
    # Recommendation stats
    total_recommendations = models.IntegerField(default=0)
    new_recommendations = models.IntegerField(default=0)
    
    # Course stats
    total_courses = models.IntegerField(default=0)
    total_bookmarks = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date']
    
    def __str__(self):
        return f"System stats for {self.date}"
    
    @classmethod
    def generate_daily_stats(cls, date=None):
        """Generate daily statistics"""
        if date is None:
            date = timezone.now().date()
        
        from resumes.models import Resume, ResumeAnalysis
        from recommendations.models import UserRecommendation, Course
        
        # Calculate stats
        total_users = User.objects.count()
        new_users = User.objects.filter(date_joined__date=date).count()
        active_users = UserActivity.objects.filter(
            created_at__date=date
        ).values('user').distinct().count()
        
        total_resumes = Resume.objects.count()
        new_resumes = Resume.objects.filter(created_at__date=date).count()
        total_conversions = Resume.objects.filter(conversion_status='completed').count()
        total_analyses = ResumeAnalysis.objects.count()
        
        total_recommendations = UserRecommendation.objects.count()
        new_recommendations = UserRecommendation.objects.filter(created_at__date=date).count()
        
        total_courses = Course.objects.filter(is_active=True).count()
        total_bookmarks = UserRecommendation.objects.filter(is_bookmarked=True).count()
        
        # Create or update stats
        stats, created = cls.objects.update_or_create(
            date=date,
            defaults={
                'total_users': total_users,
                'new_users': new_users,
                'active_users': active_users,
                'total_resumes': total_resumes,
                'new_resumes': new_resumes,
                'total_conversions': total_conversions,
                'total_analyses': total_analyses,
                'total_recommendations': total_recommendations,
                'new_recommendations': new_recommendations,
                'total_courses': total_courses,
                'total_bookmarks': total_bookmarks,
            }
        )
        
        return stats
