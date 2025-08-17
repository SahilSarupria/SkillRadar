from celery import shared_task
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from .models import Resume
from .utils import FileParser, AIResumeProcessor, ResumeBuilder
import time
import logging
import os

User = get_user_model()
logger = logging.getLogger(__name__)

@shared_task(bind=True)
def process_text_to_resume(self, user_id, text_content, title, template_style='professional'):
    """Background task to convert text to structured resume"""
    
    try:
        start_time = time.time()
        
        # Get user
        user = User.objects.get(id=user_id)
        
        # Create initial resume object
        resume = Resume.objects.create(
            user=user,
            title=title,
            resume_type='converted',
            status='processing',
            original_text=text_content
        )
        
        # Update task progress
        self.update_state(state='PROGRESS', meta={'current': 25, 'total': 100, 'status': 'Processing text...'})
        
        # Process with AI
        ai_processor = AIResumeProcessor()
        structured_data = ai_processor.text_to_structured_resume(text_content, template_style)
        
        self.update_state(state='PROGRESS', meta={'current': 50, 'total': 100, 'status': 'Structuring resume...'})
        
        # Enhance content
        enhanced_data = ai_processor.enhance_resume_content(structured_data)
        
        self.update_state(state='PROGRESS', meta={'current': 75, 'total': 100, 'status': 'Building resume...'})
        
        # Update resume with processed data
        resume.processed_content = enhanced_data
        resume.status = 'completed'
        resume.processing_time = time.time() - start_time
        resume.save()
        
        # Create related objects
        ResumeBuilder.create_resume_from_data(user, title, enhanced_data, 'converted')
        
        self.update_state(state='SUCCESS', meta={'current': 100, 'total': 100, 'status': 'Resume created successfully!'})
        
        return {
            'resume_id': str(resume.id),
            'status': 'completed',
            'processing_time': resume.processing_time
        }
        
    except Exception as e:
        logger.error(f"Error processing text to resume: {str(e)}")
        
        # Update resume status to failed
        if 'resume' in locals():
            resume.status = 'failed'
            resume.save()
        
        self.update_state(
            state='FAILURE',
            meta={'current': 0, 'total': 100, 'status': f'Error: {str(e)}'}
        )
        raise

@shared_task(bind=True)
def process_file_upload(self, user_id, file_path, title, file_type):
    """Background task to process uploaded resume file"""
    
    try:
        start_time = time.time()
        
        # Get user
        user = User.objects.get(id=user_id)
        
        # Create initial resume object
        resume = Resume.objects.create(
            user=user,
            title=title,
            resume_type='uploaded',
            status='processing',
            file_type=file_type,
            file_size=os.path.getsize(file_path)
        )
        
        self.update_state(state='PROGRESS', meta={'current': 20, 'total': 100, 'status': 'Extracting text...'})
        
        # Extract text based on file type
        if file_type == 'application/pdf':
            text_content = FileParser.extract_text_from_pdf(file_path)
        elif file_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
            text_content = FileParser.extract_text_from_docx(file_path)
        elif file_type == 'text/plain':
            text_content = FileParser.extract_text_from_txt(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
        
        resume.original_text = text_content
        resume.save()
        
        self.update_state(state='PROGRESS', meta={'current': 40, 'total': 100, 'status': 'Processing with AI...'})
        
        # Process with AI
        ai_processor = AIResumeProcessor()
        structured_data = ai_processor.text_to_structured_resume(text_content)
        
        self.update_state(state='PROGRESS', meta={'current': 70, 'total': 100, 'status': 'Enhancing content...'})
        
        # Enhance content
        enhanced_data = ai_processor.enhance_resume_content(structured_data)
        
        self.update_state(state='PROGRESS', meta={'current': 90, 'total': 100, 'status': 'Finalizing...'})
        
        # Update resume
        resume.processed_content = enhanced_data
        resume.status = 'completed'
        resume.processing_time = time.time() - start_time
        resume.save()
        
        # Create related objects
        ResumeBuilder.create_resume_from_data(user, title, enhanced_data, 'uploaded')
        
        self.update_state(state='SUCCESS', meta={'current': 100, 'total': 100, 'status': 'Resume processed successfully!'})
        
        return {
            'resume_id': str(resume.id),
            'status': 'completed',
            'processing_time': resume.processing_time
        }
        
    except Exception as e:
        logger.error(f"Error processing file upload: {str(e)}")
        
        # Update resume status to failed
        if 'resume' in locals():
            resume.status = 'failed'
            resume.save()
        
        self.update_state(
            state='FAILURE',
            meta={'current': 0, 'total': 100, 'status': f'Error: {str(e)}'}
        )
        raise
    
    finally:
        # Clean up temporary file
        if os.path.exists(file_path):
            os.remove(file_path)

@shared_task
def cleanup_failed_resumes():
    """Periodic task to clean up failed resume processing attempts"""
    from datetime import timedelta
    from django.utils import timezone
    
    # Delete failed resumes older than 24 hours
    cutoff_time = timezone.now() - timedelta(hours=24)
    failed_resumes = Resume.objects.filter(
        status='failed',
        created_at__lt=cutoff_time
    )
    
    count = failed_resumes.count()
    failed_resumes.delete()
    
    logger.info(f"Cleaned up {count} failed resume processing attempts")
    return f"Cleaned up {count} failed resumes"
