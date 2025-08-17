from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    LearningPlatform, PlatformIntegration, Course, Skill, 
    CourseRecommendation, LearningPath, UserCourseProgress, AffiliateClick
)

@admin.register(LearningPlatform)
class LearningPlatformAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'total_courses', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    def total_courses(self, obj):
        return obj.courses.filter(is_active=True).count()
    total_courses.short_description = 'Active Courses'

@admin.register(PlatformIntegration)
class PlatformIntegrationAdmin(admin.ModelAdmin):
    list_display = ['platform']
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Hide sensitive fields in the admin
        if 'api_key' in form.base_fields:
            form.base_fields['api_key'].widget.attrs['type'] = 'password'
        return form

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'platform', 'instructor_name', 'level', 'rating', 'total_students', 'is_free', 'is_active']
    list_filter = ['platform', 'level', 'is_free', 'is_active', 'has_certificate', 'language']
    search_fields = ['title', 'instructor_name', 'description']
    readonly_fields = ['external_id', 'created_at', 'updated_at', 'last_updated']
    filter_horizontal = ['skills_taught']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('platform', 'external_id', 'title', 'description', 'instructor_name')
        }),
        ('Course Details', {
            'fields': ('duration_hours', 'level', 'language', 'has_certificate', 'is_free')
        }),
        ('Metrics', {
            'fields': ('rating', 'total_students', 'price', 'popularity_score')
        }),
        ('URLs and Media', {
            'fields': ('course_url', 'thumbnail_url')
        }),
        ('Skills and Categories', {
            'fields': ('skills_taught',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'last_updated'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('platform').prefetch_related('skills_taught')

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'course_count']
    list_filter = ['category']
    search_fields = ['name', 'description']
    
    def course_count(self, obj):
        return obj.courses.filter(is_active=True).count()
    course_count.short_description = 'Courses Teaching This Skill'

@admin.register(CourseRecommendation)
class UserRecommendationAdmin(admin.ModelAdmin):
    list_display = ['user', 'course_title', 'target_skill', 'recommendation_type', 'relevance_score', 'priority', 'is_bookmarked']
    list_filter = ['recommendation_type', 'priority', 'is_bookmarked', 'created_at']
    search_fields = ['user__email', 'course__title', 'target_skill__name']
    readonly_fields = ['created_at', 'updated_at']
    
    def course_title(self, obj):
        return obj.course.title
    course_title.short_description = 'Course'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'course', 'target_skill')

@admin.register(LearningPath)
class LearningPathAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'difficulty_level', 'estimated_duration_weeks', 'estimated_hours_per_week', 'progress_percentage']
    list_filter = ['difficulty_level', 'status', 'created_at']
    search_fields = ['title', 'user__email', 'description']
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['target_skills']  # correct field

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user').prefetch_related('target_skills')

@admin.register(UserCourseProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'learning_path_title', 'progress_percentage', 'started_at']
    list_filter = [ 'started_at']
    search_fields = ['user__email', 'learning_path__title']
    readonly_fields = ['started_at']
    
    def learning_path_title(self, obj):
        return obj.learning_path.title
    learning_path_title.short_description = 'Learning Path'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'learning_path')

@admin.register(AffiliateClick)
class AffiliateClickAdmin(admin.ModelAdmin):
    list_display = ['user', 'course_title', 'platform', 'clicked_at', 'ip_address']
    list_filter = ['clicked_at', 'course__platform']
    search_fields = ['user__email', 'course__title']
    readonly_fields = ['clicked_at']
    
    def course_title(self, obj):
        return obj.course.title
    course_title.short_description = 'Course'
    
    def platform(self, obj):
        return obj.course.platform.name
    platform.short_description = 'Platform'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'course', 'course__platform')

# Custom admin actions
def sync_platform_courses(modeladmin, request, queryset):
    """Admin action to sync courses for selected platforms"""
    from .tasks import sync_platform_courses_task
    
    for platform in queryset:
        sync_platform_courses_task.delay(platform.name)
    
    modeladmin.message_user(request, f"Course sync initiated for {queryset.count()} platforms")

sync_platform_courses.short_description = "Sync courses for selected platforms"

def analyze_course_skills(modeladmin, request, queryset):
    """Admin action to analyze skills for selected courses"""
    from .tasks import analyze_course_skills_task
    
    for course in queryset:
        analyze_course_skills_task.delay(course.id)
    
    modeladmin.message_user(request, f"Skill analysis initiated for {queryset.count()} courses")

analyze_course_skills.short_description = "Analyze skills for selected courses"

# Add actions to admin classes
LearningPlatformAdmin.actions = [sync_platform_courses]
CourseAdmin.actions = [analyze_course_skills]
