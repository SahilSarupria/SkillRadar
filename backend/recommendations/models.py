from django.db import models
from django.contrib.auth import get_user_model
from skills.models import Skill, SkillGapAnalysis, LearningPath
import uuid

User = get_user_model()

class LearningPlatform(models.Model):
    """Learning platforms like Coursera, Udemy, etc."""
    name = models.CharField(max_length=100, unique=True)
    website_url = models.URLField()
    api_endpoint = models.URLField(blank=True, help_text="API endpoint for course data")
    logo_url = models.URLField(blank=True)
    
    # Platform characteristics
    platform_type = models.CharField(max_length=50, choices=[
        ('mooc', 'MOOC (Massive Open Online Course)'),
        ('bootcamp', 'Coding Bootcamp'),
        ('university', 'University/Academic'),
        ('corporate', 'Corporate Training'),
        ('tutorial', 'Tutorial Platform'),
        ('certification', 'Certification Provider'),
    ])
    
    # Pricing and features
    has_free_courses = models.BooleanField(default=True)
    has_paid_courses = models.BooleanField(default=True)
    has_certificates = models.BooleanField(default=True)
    has_degrees = models.BooleanField(default=False)
    
    # Integration details
    api_key_required = models.BooleanField(default=False)
    affiliate_program = models.BooleanField(default=False)
    affiliate_id = models.CharField(max_length=200, blank=True)
    
    # Quality metrics
    average_rating = models.FloatField(default=4.0, help_text="Average platform rating")
    total_courses = models.PositiveIntegerField(default=0)
    total_students = models.PositiveIntegerField(default=0)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
    


class Course(models.Model):
    """Individual courses from learning platforms"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    platform = models.ForeignKey(LearningPlatform, on_delete=models.CASCADE, related_name='courses')
    
    # Course identification
    external_id = models.CharField(max_length=200, help_text="Course ID on the platform")
    title = models.CharField(max_length=300)
    slug = models.SlugField(max_length=350, unique=True)
    description = models.TextField()
    short_description = models.CharField(max_length=500, blank=True)
    
    # Course details
    instructor_name = models.CharField(max_length=200)
    instructor_bio = models.TextField(blank=True)
    language = models.CharField(max_length=50, default='English')
    level = models.CharField(max_length=20, choices=[
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('all_levels', 'All Levels'),
    ])
    
    # Course content
    duration_hours = models.FloatField(help_text="Course duration in hours")
    total_lectures = models.PositiveIntegerField(default=0)
    has_assignments = models.BooleanField(default=False)
    has_projects = models.BooleanField(default=False)
    has_certificate = models.BooleanField(default=False)
    
    # Skills and topics
    skills_taught = models.ManyToManyField(Skill, related_name='courses', blank=True)
    topics = models.JSONField(default=list, help_text="List of topics covered")
    prerequisites = models.JSONField(default=list, help_text="Course prerequisites")
    
    # Pricing
    is_free = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    currency = models.CharField(max_length=3, default='USD')
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    # Quality metrics
    rating = models.FloatField(default=0.0, help_text="Course rating (0-5)")
    total_reviews = models.PositiveIntegerField(default=0)
    total_students = models.PositiveIntegerField(default=0)
    
    # URLs and media
    course_url = models.URLField()
    thumbnail_url = models.URLField(blank=True)
    preview_video_url = models.URLField(blank=True)
    
    # Metadata
    last_updated = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['platform', 'external_id']
        ordering = ['-rating', '-total_students']
        indexes = [
            models.Index(fields=['platform', 'level']),
            models.Index(fields=['is_free', 'rating']),
            #models.Index(fields=['skills_taught']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.platform.name}"
    
    @property
    def effective_price(self):
        """Return the effective price (discount price if available)"""
        return self.discount_price if self.discount_price else self.price
    
    @property
    def is_highly_rated(self):
        """Check if course is highly rated"""
        return self.rating >= 4.5 and self.total_reviews >= 100

class CourseRecommendation(models.Model):
    """Course recommendations for users based on skill gaps"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='course_recommendations')
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    skill_gap_analysis = models.ForeignKey(SkillGapAnalysis, on_delete=models.CASCADE, blank=True, null=True)
    learning_path = models.ForeignKey(LearningPath, on_delete=models.CASCADE, blank=True, null=True)
    
    # Recommendation details
    target_skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    recommendation_reason = models.TextField(help_text="Why this course was recommended")
    relevance_score = models.FloatField(default=0.0, help_text="How relevant this course is (0-100)")
    
    # Recommendation metadata
    recommendation_type = models.CharField(max_length=50, choices=[
        ('skill_gap', 'Skill Gap Based'),
        ('career_path', 'Career Path'),
        ('trending', 'Trending Course'),
        ('similar_users', 'Similar Users'),
        ('ai_suggested', 'AI Suggested'),
    ])
    
    priority = models.CharField(max_length=20, choices=[
        ('low', 'Low Priority'),
        ('medium', 'Medium Priority'),
        ('high', 'High Priority'),
        ('urgent', 'Urgent'),
    ], default='medium')
    
    # User interaction
    is_viewed = models.BooleanField(default=False)
    is_bookmarked = models.BooleanField(default=False)
    is_enrolled = models.BooleanField(default=False)
    is_dismissed = models.BooleanField(default=False)
    
    viewed_at = models.DateTimeField(blank=True, null=True)
    bookmarked_at = models.DateTimeField(blank=True, null=True)
    enrolled_at = models.DateTimeField(blank=True, null=True)
    dismissed_at = models.DateTimeField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'course', 'target_skill']
        ordering = ['-relevance_score', '-created_at']
        indexes = [
            models.Index(fields=['user', '-relevance_score']),
            models.Index(fields=['recommendation_type']),
            models.Index(fields=['priority']),
        ]
    
    def __str__(self):
        return f"{self.course.title} recommended for {self.user.email}"

class UserCourseProgress(models.Model):
    """Track user progress in courses"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='course_progress')
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    recommendation = models.ForeignKey(CourseRecommendation, on_delete=models.SET_NULL, blank=True, null=True)
    
    # Progress tracking
    status = models.CharField(max_length=20, choices=[
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('paused', 'Paused'),
        ('dropped', 'Dropped'),
    ], default='not_started')
    
    progress_percentage = models.FloatField(default=0.0, help_text="Progress percentage (0-100)")
    lectures_completed = models.PositiveIntegerField(default=0)
    assignments_completed = models.PositiveIntegerField(default=0)
    projects_completed = models.PositiveIntegerField(default=0)
    
    # Time tracking
    total_time_spent_minutes = models.PositiveIntegerField(default=0)
    last_accessed = models.DateTimeField(blank=True, null=True)
    
    # Completion details
    started_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    certificate_earned = models.BooleanField(default=False)
    certificate_url = models.URLField(blank=True)
    
    # User feedback
    user_rating = models.FloatField(blank=True, null=True, help_text="User's rating of the course (1-5)")
    user_review = models.TextField(blank=True)
    would_recommend = models.BooleanField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'course']
        ordering = ['-last_accessed', '-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.course.title} ({self.progress_percentage}%)"

class LearningGoal(models.Model):
    """User's learning goals and targets"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='learning_goals')
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    target_skills = models.ManyToManyField(Skill, related_name='learning_goals')
    
    # Goal details
    goal_type = models.CharField(max_length=50, choices=[
        ('career_change', 'Career Change'),
        ('skill_upgrade', 'Skill Upgrade'),
        ('certification', 'Get Certified'),
        ('promotion', 'Job Promotion'),
        ('personal', 'Personal Interest'),
    ])
    
    priority = models.CharField(max_length=20, choices=[
        ('low', 'Low Priority'),
        ('medium', 'Medium Priority'),
        ('high', 'High Priority'),
    ], default='medium')
    
    # Timeline
    target_completion_date = models.DateField(blank=True, null=True)
    estimated_hours_per_week = models.PositiveIntegerField(default=5)
    
    # Progress
    status = models.CharField(max_length=20, choices=[
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], default='active')
    
    progress_percentage = models.FloatField(default=0.0)
    
    # Recommended courses for this goal
    recommended_courses = models.ManyToManyField(Course, through='GoalCourseRecommendation', blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-priority', '-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.user.email}"

class GoalCourseRecommendation(models.Model):
    """Through model for learning goal course recommendations"""
    learning_goal = models.ForeignKey(LearningGoal, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(help_text="Recommended order in learning path")
    is_required = models.BooleanField(default=False, help_text="Is this course required for the goal")
    relevance_score = models.FloatField(default=0.0)
    
    class Meta:
        unique_together = ['learning_goal', 'course']
        ordering = ['order']

class PlatformIntegration(models.Model):
    """Integration settings and credentials for learning platforms"""
    platform = models.OneToOneField(LearningPlatform, on_delete=models.CASCADE, related_name='integration')
    
    # API credentials
    api_key = models.CharField(max_length=500, blank=True)
    api_secret = models.CharField(max_length=500, blank=True)
    access_token = models.TextField(blank=True)
    refresh_token = models.TextField(blank=True)
    
    # Integration settings
    is_enabled = models.BooleanField(default=True)
    sync_frequency_hours = models.PositiveIntegerField(default=24, help_text="How often to sync course data")
    last_sync = models.DateTimeField(blank=True, null=True)
    
    # Rate limiting
    requests_per_minute = models.PositiveIntegerField(default=60)
    requests_per_day = models.PositiveIntegerField(default=10000)
    
    # Error tracking
    last_error = models.TextField(blank=True)
    error_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.platform.name} Integration"

class CourseReview(models.Model):
    """User reviews and ratings for courses"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='course_reviews')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='user_reviews')
    
    # Review content
    rating = models.FloatField(help_text="Rating from 1-5")
    title = models.CharField(max_length=200, blank=True)
    review_text = models.TextField()
    
    # Review categories
    content_quality = models.FloatField(blank=True, null=True, help_text="Content quality rating (1-5)")
    instructor_quality = models.FloatField(blank=True, null=True, help_text="Instructor quality rating (1-5)")
    value_for_money = models.FloatField(blank=True, null=True, help_text="Value for money rating (1-5)")
    
    # Review metadata
    is_verified_purchase = models.BooleanField(default=False)
    is_helpful = models.BooleanField(default=False)
    helpful_votes = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'course']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Review by {self.user.email} for {self.course.title}"

class LearningPathRecommendation(models.Model):
    """Recommended learning paths for users"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='path_recommendations')
    learning_path = models.ForeignKey(LearningPath, on_delete=models.CASCADE)
    
    # Recommendation details
    recommendation_reason = models.TextField()
    relevance_score = models.FloatField(default=0.0)
    estimated_completion_weeks = models.PositiveIntegerField()
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # User interaction
    is_viewed = models.BooleanField(default=False)
    is_started = models.BooleanField(default=False)
    is_dismissed = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'learning_path']
        ordering = ['-relevance_score', '-created_at']
    
    def __str__(self):
        return f"Path recommendation: {self.learning_path.title} for {self.user.email}"


class AffiliateClick(models.Model):
    """Track affiliate link clicks for courses"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="affiliate_clicks")
    platform = models.ForeignKey(LearningPlatform, on_delete=models.CASCADE, related_name="affiliate_clicks")
    
    clicked_at = models.DateTimeField(auto_now_add=True)
    referrer_url = models.URLField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)

    class Meta:
        ordering = ['-clicked_at']

    def __str__(self):
        return f"Click on {self.course.title} ({self.platform.name})"
