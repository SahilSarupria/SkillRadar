from rest_framework import serializers
from .models import Resume, ResumeSection, WorkExperience, Education, Project

class WorkExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkExperience
        fields = '__all__'
        read_only_fields = ('resume',)

class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = '__all__'
        read_only_fields = ('resume',)

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'
        read_only_fields = ('resume',)

class ResumeSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResumeSection
        fields = '__all__'
        read_only_fields = ('resume',)

class ResumeSerializer(serializers.ModelSerializer):
    sections = ResumeSectionSerializer(many=True, read_only=True)
    work_experiences = WorkExperienceSerializer(many=True, read_only=True)
    education = EducationSerializer(many=True, read_only=True)
    projects = ProjectSerializer(many=True, read_only=True)
    
    class Meta:
        model = Resume
        fields = '__all__'
        read_only_fields = ('user', 'id', 'created_at', 'updated_at', 'processing_time')

class ResumeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resume
        fields = ('id', 'title', 'resume_type', 'status', 'created_at', 'updated_at', 'file_size')

class TextToResumeSerializer(serializers.Serializer):
    text_content = serializers.CharField(max_length=50000, help_text="Raw text content to convert to resume")
    title = serializers.CharField(max_length=200, help_text="Title for the generated resume")
    template_style = serializers.ChoiceField(
        choices=[
            ('professional', 'Professional'),
            ('modern', 'Modern'),
            ('creative', 'Creative'),
            ('minimal', 'Minimal')
        ],
        default='professional',
        help_text="Resume template style"
    )

class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField(help_text="Resume file to upload (PDF, DOCX, TXT)")
    title = serializers.CharField(max_length=200, required=False, help_text="Optional title for the resume")
    
    def validate_file(self, value):
        allowed_types = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain']
        if value.content_type not in allowed_types:
            raise serializers.ValidationError("Only PDF, DOCX, and TXT files are allowed.")
        
        # Check file size (10MB limit)
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError("File size cannot exceed 10MB.")
        
        return value
