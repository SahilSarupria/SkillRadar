from django.urls import path
from . import views

urlpatterns = [
    # Resume CRUD
    path('', views.ResumeListCreateView.as_view(), name='resume-list-create'),
    path('<uuid:pk>/', views.ResumeDetailView.as_view(), name='resume-detail'),
    
    # AI Conversion
    path('convert-text/', views.convert_text_to_resume, name='convert-text-to-resume'),
    path('upload-file/', views.upload_resume_file, name='upload-resume-file'),
    path('task-status/<str:task_id>/', views.check_task_status, name='check-task-status'),
    
    # Templates and utilities
    path('templates/', views.get_resume_templates, name='resume-templates'),
    path('<uuid:resume_id>/regenerate-section/', views.regenerate_resume_section, name='regenerate-section'),
]
