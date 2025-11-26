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
import json
from django.contrib.auth import get_user_model
from .utils import AIResumeProcessor
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

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def upload_resume_and_parse(request):
    """
    Synchronous upload + parse endpoint.
    Accepts multipart/form-data with field 'file' and optional 'title'.
    Returns parsed structured resume JSON and created resume id (if saved).
    """
    uploaded = request.FILES.get('file')
    title = request.data.get('title') or (uploaded.name if uploaded is not None else "uploaded_resume")
    if not uploaded:
        return Response({'detail': 'file is required'}, status=status.HTTP_400_BAD_REQUEST)

    # save temporary file
    ext = os.path.splitext(uploaded.name)[1] or '.bin'
    tmp_path = default_storage.save(f"temp/{uuid.uuid4()}{ext}", ContentFile(uploaded.read()))
    full_path = default_storage.path(tmp_path)

    try:
        processor = AIResumeProcessor()
        parsed = processor.parse_file(full_path)
    except Exception as e:
        return Response({'detail': f'parsing failed: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    finally:
        # cleanup temp file if stored on local FS
        try:
            default_storage.delete(tmp_path)
        except Exception:
            pass

    resume_id = None
    try:
        # attempt to create a Resume DB row
        # safe-create using serializer-like minimal fields
        r = Resume.objects.create(user=request.user, title=title, status='completed', processed_content=parsed)
        resume_id = str(r.id)
    except Exception:
        # best-effort: if model requires other fields, ignore persistence
        resume_id = None

    return Response({'resume_id': resume_id, 'parsed': parsed}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def calculate_score(request):
    """
    Calculate score for a resume against a given goal.
    Accepts JSON body:
      - resume_data: { ... }   OR resume_id: <uuid> (preferred)
      - goal: { required_skills: [...], min_experience_years: int, weight_skills: float }
    """
    payload = request.data or {}
    goal = payload.get('goal') or {}
    resume_data = payload.get('resume_data')

    # if resume_id provided, load from DB
    resume_id = payload.get('resume_id')
    if not resume_data and resume_id:
        try:
            r = Resume.objects.get(id=resume_id, user=request.user)
            resume_data = getattr(r, 'processed_content', None) or {}
        except Resume.DoesNotExist:
            return Response({'detail': 'resume not found'}, status=status.HTTP_404_NOT_FOUND)

    if not resume_data:
        return Response({'detail': 'resume_data or resume_id required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        processor = AIResumeProcessor()
        result = processor.calculate_score(resume_data, goal)
        return Response(result, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'detail': f'scoring failed: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def save_resume(request):
    """
    Persist edited resume JSON.
    Body: { resume_id: <uuid>, processed_content: {...} }
    """
    resume_id = request.data.get('resume_id')
    processed = request.data.get('processed_content')
    if not resume_id or processed is None:
        return Response({'detail': 'resume_id and processed_content required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        r = Resume.objects.get(id=resume_id, user=request.user)
        r.processed_content = processed
        r.status = 'completed'
        r.save()
        return Response({'detail': 'saved', 'resume_id': str(r.id)}, status=status.HTTP_200_OK)
    except Resume.DoesNotExist:
        return Response({'detail': 'resume not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'detail': f'save failed: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def resume_detail(request, resume_id):
    """
    Return processed_content for a resume id.
    """
    try:
        r = Resume.objects.get(id=resume_id, user=request.user)
        return Response({'id': str(r.id), 'processed_content': getattr(r, 'processed_content', None)}, status=status.HTTP_200_OK)
    except Resume.DoesNotExist:
        return Response({'detail': 'resume not found'}, status=status.HTTP_404_NOT_FOUND)


