from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # User dashboard endpoints
    path('', views.UserDashboardView.as_view(), name='user-dashboard'),
    path('stats/', views.UserStatsView.as_view(), name='user-stats'),
    path('activities/', views.UserActivityListView.as_view(), name='user-activities'),
    path('analytics/', views.user_analytics, name='user-analytics'),
    path('progress/', views.user_progress_summary, name='progress-summary'),
    path('achievements/', views.user_achievements, name='user-achievements'),
    
    # Activity tracking
    path('track/', views.track_activity, name='track-activity'),
    
    # Admin endpoints
    path('admin/stats/', views.system_stats, name='system-stats'),
    path('admin/analytics/', views.admin_analytics, name='admin-analytics'),
    path('admin/generate-stats/', views.generate_daily_stats, name='generate-daily-stats'),
    path('admin/engagement/', views.user_engagement_report, name='engagement-report'),
]
