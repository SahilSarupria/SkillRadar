from django.urls import path
from . import views

app_name = 'recommendations'

urlpatterns = [
    # Platform and course endpoints
    path('platforms/', views.LearningPlatformListView.as_view(), name='platform-list'),
    path('courses/', views.CourseListView.as_view(), name='course-list'),
    path('courses/<int:pk>/', views.CourseDetailView.as_view(), name='course-detail'),
    path('skills/', views.SkillListView.as_view(), name='skill-list'),
    
    # Recommendation endpoints
    path('generate/', views.generate_recommendations, name='generate-recommendations'),
    path('learning-paths/generate/', views.generate_learning_paths, name='generate-learning-paths'),
    
    # User-specific endpoints
    path('my-recommendations/', views.UserRecommendationListView.as_view(), name='user-recommendations'),
    path('my-learning-paths/', views.UserLearningPathListView.as_view(), name='user-learning-paths'),
    path('my-progress/', views.UserProgressListView.as_view(), name='user-progress'),
    
    # User actions
    path('bookmark/', views.bookmark_course, name='bookmark-course'),
    path('progress/', views.update_course_progress, name='update-progress'),
    path('track-click/<int:course_id>/', views.track_affiliate_click, name='track-affiliate-click'),
    
    # Admin endpoints
    path('admin/sync-courses/', views.sync_platform_courses, name='sync-courses'),
    path('stats/', views.platform_stats, name='platform-stats'),
]
