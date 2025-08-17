from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from celery.result import AsyncResult
from .models import Resume
from .serializers import (
    ResumeSerializer, 
    ResumeListSerializer, 
    TextToResumeSerializer, 
    FileUploadSerializer
)
from .tasks import process_text_to_resume, process_file_upload
import uuid
import os

class ResumeListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ResumeListSerializer
        return ResumeSerializer
    
    def get_queryset(self):
        return Resume.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ResumeDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ResumeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Resume.objects.filter(user=self.request.user)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def convert_text_to_resume(request):
    """Convert raw text to structured resume using AI"""
    
    serializer = TextToResumeSerializer(data=request.data)
    if serializer.is_valid():
        text_content = serializer.validated_data['text_content']
        title = serializer.validated_data['title']
        template_style = serializer.validated_data['template_style']
        
        # Start background task
        task = process_text_to_resume.delay(
            user_id=request.user.id,
            text_content=text_content,
            title=title,
            template_style=template_style
        )
        
        return Response({
            'task_id': task.id,
            'status': 'processing',
            'message': 'Resume conversion started. Use the task_id to check progress.'
        }, status=status.HTTP_202_ACCEPTED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def upload_resume_file(request):
    """Upload and process resume file (PDF, DOCX, TXT)"""
    
    parser_classes = [MultiPartParser, FormParser]
    serializer = FileUploadSerializer(data=request.data)
    
    if serializer.is_valid():
        uploaded_file = serializer.validated_data['file']
        title = serializer.validated_data.get('title', uploaded_file.name)
        
        # Generate unique filename
        file_extension = os.path.splitext(uploaded_file.name)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        
        # Save file temporarily
        file_path = default_storage.save(
            f"temp/{unique_filename}",
            ContentFile(uploaded_file.read())
        )
        
        # Get full file path
        full_file_path = default_storage.path(file_path)
        
        # Start background task
        task = process_file_upload.delay(
            user_id=request.user.id,
            file_path=full_file_path,
            title=title,
            file_type=uploaded_file.content_type
        )
        
        return Response({
            'task_id': task.id,
            'status': 'processing',
            'message': 'File upload started. Use the task_id to check progress.'
        }, status=status.HTTP_202_ACCEPTED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def check_task_status(request, task_id):
    """Check the status of a background task"""
    
    try:
        task_result = AsyncResult(task_id)
        
        if task_result.state == 'PENDING':
            response = {
                'state': task_result.state,
                'current': 0,
                'total': 100,
                'status': 'Task is waiting to be processed...'
            }
        elif task_result.state == 'PROGRESS':
            response = {
                'state': task_result.state,
                'current': task_result.info.get('current', 0),
                'total': task_result.info.get('total', 100),
                'status': task_result.info.get('status', '')
            }
        elif task_result.state == 'SUCCESS':
            response = {
                'state': task_result.state,
                'current': 100,
                'total': 100,
                'status': 'Task completed successfully!',
                'result': task_result.info
            }
        else:  # FAILURE
            response = {
                'state': task_result.state,
                'current': 0,
                'total': 100,
                'status': task_result.info.get('status', 'Task failed'),
                'error': str(task_result.info)
            }
        
        return Response(response)
        
    except Exception as e:
        return Response({
            'error': f'Error checking task status: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_resume_templates(request):
    """Get available resume templates"""
    
    templates = [
        {
            'id': 'professional',
            'name': 'Professional',
            'description': 'Clean and traditional layout suitable for corporate environments',
            'preview_url': '/static/templates/professional_preview.png'
        },
        {
            'id': 'modern',
            'name': 'Modern',
            'description': 'Contemporary design with subtle colors and modern typography',
            'preview_url': '/static/templates/modern_preview.png'
        },
        {
            'id': 'creative',
            'name': 'Creative',
            'description': 'Bold design for creative professionals and designers',
            'preview_url': '/static/templates/creative_preview.png'
        },
        {
            'id': 'minimal',
            'name': 'Minimal',
            'description': 'Simple and clean layout focusing on content',
            'preview_url': '/static/templates/minimal_preview.png'
        }
    ]
    
    return Response({'templates': templates})

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def regenerate_resume_section(request, resume_id):
    """Regenerate a specific section of the resume using AI"""
    
    try:
        resume = Resume.objects.get(id=resume_id, user=request.user)
        section_type = request.data.get('section_type')
        additional_context = request.data.get('additional_context', '')
        
        if not section_type:
            return Response({'error': 'section_type is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # This would trigger a background task to regenerate the specific section
        # For now, return a placeholder response
        return Response({
            'message': f'Regeneration of {section_type} section started',
            'status': 'processing'
        })
        
    except Resume.DoesNotExist:
        return Response({'error': 'Resume not found'}, status=status.HTTP_404_NOT_FOUND)
