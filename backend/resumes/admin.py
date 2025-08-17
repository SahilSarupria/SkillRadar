from django.contrib import admin
from .models import Resume, ResumeSection, WorkExperience, Education, Project

@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'resume_type', 'status', 'created_at', 'processing_time')
    list_filter = ('resume_type', 'status', 'created_at')
    search_fields = ('title', 'user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('id', 'created_at', 'updated_at', 'processing_time')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'user', 'title', 'resume_type', 'status')
        }),
        ('Files', {
            'fields': ('original_file', 'processed_file')
        }),
        ('Content', {
            'fields': ('original_text', 'processed_content'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('file_size', 'file_type', 'processing_time', 'created_at', 'updated_at')
        }),
    )

@admin.register(ResumeSection)
class ResumeSectionAdmin(admin.ModelAdmin):
    list_display = ('resume', 'section_type', 'title', 'order', 'is_visible')
    list_filter = ('section_type', 'is_visible')
    search_fields = ('resume__title', 'title')

@admin.register(WorkExperience)
class WorkExperienceAdmin(admin.ModelAdmin):
    list_display = ('resume', 'position', 'company_name', 'start_date', 'end_date', 'is_current')
    list_filter = ('is_current', 'start_date')
    search_fields = ('position', 'company_name', 'resume__title')

@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ('resume', 'degree', 'institution', 'start_date', 'end_date')
    list_filter = ('start_date',)
    search_fields = ('degree', 'institution', 'resume__title')

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('resume', 'name', 'start_date', 'end_date')
    list_filter = ('start_date',)
    search_fields = ('name', 'resume__title')
