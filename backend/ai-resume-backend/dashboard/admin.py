from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from .models import UserActivity, UserStats, SystemStats

@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ['user_email', 'activity_type', 'description', 'created_at', 'ip_address']
    list_filter = ['activity_type', 'created_at']
    search_fields = ['user__email', 'description', 'ip_address']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User Email'
    user_email.admin_order_field = 'user__email'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

@admin.register(UserStats)
class UserStatsAdmin(admin.ModelAdmin):
    list_display = [
        'user_email', 'total_resumes', 'total_conversions', 'total_recommendations_received',
        'total_courses_completed', 'streak_days', 'last_active'
    ]
    list_filter = ['last_active', 'created_at']
    search_fields = ['user__email']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Resume Statistics', {
            'fields': ('total_resumes', 'total_conversions', 'total_analyses')
        }),
        ('Skill Statistics', {
            'fields': ('total_skills_identified', 'total_skill_gaps')
        }),
        ('Learning Statistics', {
            'fields': (
                'total_recommendations_received', 'total_courses_bookmarked',
                'total_courses_started', 'total_courses_completed'
            )
        }),
        ('Engagement Statistics', {
            'fields': ('total_logins', 'last_active', 'streak_days')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User Email'
    user_email.admin_order_field = 'user__email'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
    
    actions = ['update_selected_stats']
    
    def update_selected_stats(self, request, queryset):
        """Update statistics for selected users"""
        updated_count = 0
        for user_stats in queryset:
            user_stats.update_stats()
            updated_count += 1
        
        self.message_user(request, f"Updated statistics for {updated_count} users")
    
    update_selected_stats.short_description = "Update statistics for selected users"

@admin.register(SystemStats)
class SystemStatsAdmin(admin.ModelAdmin):
    list_display = [
        'date', 'total_users', 'new_users', 'active_users',
        'total_resumes', 'new_resumes', 'total_recommendations'
    ]
    list_filter = ['date']
    date_hierarchy = 'date'
    ordering = ['-date']
    
    fieldsets = (
        ('Date', {
            'fields': ('date',)
        }),
        ('User Statistics', {
            'fields': ('total_users', 'new_users', 'active_users')
        }),
        ('Resume Statistics', {
            'fields': ('total_resumes', 'new_resumes', 'total_conversions', 'total_analyses')
        }),
        ('Recommendation Statistics', {
            'fields': ('total_recommendations', 'new_recommendations')
        }),
        ('Course Statistics', {
            'fields': ('total_courses', 'total_bookmarks')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )
    
    readonly_fields = ['created_at']
    
    actions = ['generate_stats_for_selected_dates']
    
    def generate_stats_for_selected_dates(self, request, queryset):
        """Generate statistics for selected dates"""
        generated_count = 0
        for stats in queryset:
            SystemStats.generate_daily_stats(stats.date)
            generated_count += 1
        
        self.message_user(request, f"Generated statistics for {generated_count} dates")
    
    generate_stats_for_selected_dates.short_description = "Regenerate statistics for selected dates"

# Custom admin views for analytics
class DashboardAdminMixin:
    """Mixin to add dashboard functionality to admin"""
    
    def changelist_view(self, request, extra_context=None):
        # Add dashboard stats to context
        extra_context = extra_context or {}
        
        # Get recent activity summary
        recent_activities = UserActivity.objects.values('activity_type').annotate(
            count=Count('id')
        ).order_by('-count')[:5]
        
        extra_context['recent_activities'] = recent_activities
        
        return super().changelist_view(request, extra_context)
