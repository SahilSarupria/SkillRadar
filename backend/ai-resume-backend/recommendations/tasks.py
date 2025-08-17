from celery import shared_task
from django.contrib.auth import get_user_model
from django.utils import timezone
from .utils import CourseRecommendationEngine, PlatformIntegrator, CourseContentAnalyzer
from .models import LearningPlatform, Course, Skill, UserRecommendation
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

@shared_task(bind=True, max_retries=3)
def generate_user_recommendations_task(self, user_id, skill_gaps=None, learning_goals=None):
    """Generate recommendations for a user in the background"""
    try:
        user = User.objects.get(id=user_id)
        
        # Generate recommendations
        recommendation_engine = CourseRecommendationEngine()
        recommendations = recommendation_engine.generate_recommendations(
            user=user,
            skill_gaps=skill_gaps or [],
            learning_goals=learning_goals or [],
            limit=20
        )
        
        # Save recommendations to database
        saved_count = 0
        for rec in recommendations:
            user_rec, created = UserRecommendation.objects.update_or_create(
                user=user,
                course=rec['course'],
                defaults={
                    'target_skill': rec.get('target_skill'),
                    'relevance_score': rec['relevance_score'],
                    'recommendation_type': rec['recommendation_type'],
                    'recommendation_reason': rec['recommendation_reason'],
                    'priority': rec['priority']
                }
            )
            if created:
                saved_count += 1
        
        logger.info(f"Generated {saved_count} new recommendations for user {user_id}")
        return {
            'success': True,
            'user_id': user_id,
            'recommendations_generated': len(recommendations),
            'new_recommendations': saved_count
        }
        
    except User.DoesNotExist:
        logger.error(f"User {user_id} not found")
        return {'success': False, 'error': 'User not found'}
    except Exception as e:
        logger.error(f"Error generating recommendations for user {user_id}: {str(e)}")
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=60 * (self.request.retries + 1))
        return {'success': False, 'error': str(e)}

@shared_task(bind=True, max_retries=3)
def sync_platform_courses_task(self, platform_name):
    """Sync courses from a learning platform"""
    try:
        platform = LearningPlatform.objects.get(name__iexact=platform_name, is_active=True)
        
        # Initialize platform integrator
        integrator = PlatformIntegrator(platform_name)
        
        # Sync courses
        sync_result = integrator.sync_courses()
        
        if sync_result['success']:
            # Update platform last sync time
            platform.last_sync_at = timezone.now()
            platform.save()
            
            logger.info(f"Successfully synced {sync_result.get('courses_synced', 0)} courses from {platform_name}")
        else:
            logger.error(f"Failed to sync courses from {platform_name}: {sync_result.get('error')}")
        
        return sync_result
        
    except LearningPlatform.DoesNotExist:
        error_msg = f"Platform {platform_name} not found or inactive"
        logger.error(error_msg)
        return {'success': False, 'error': error_msg}
    except Exception as e:
        logger.error(f"Error syncing courses from {platform_name}: {str(e)}")
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=300 * (self.request.retries + 1))  # 5 minutes, 10 minutes, 15 minutes
        return {'success': False, 'error': str(e)}

@shared_task(bind=True, max_retries=2)
def analyze_course_skills_task(self, course_id):
    """Analyze course content and extract skills"""
    try:
        course = Course.objects.get(id=course_id)
        
        # Analyze course skills
        analyzer = CourseContentAnalyzer()
        extracted_skills = analyzer.analyze_course_skills(course.title, course.description)
        
        # Add skills to course
        skills_added = 0
        for skill_name in extracted_skills:
            skill, created = Skill.objects.get_or_create(
                name=skill_name,
                defaults={'category': 'general'}
            )
            if not course.skills_taught.filter(id=skill.id).exists():
                course.skills_taught.add(skill)
                skills_added += 1
        
        logger.info(f"Added {skills_added} skills to course {course.title}")
        return {
            'success': True,
            'course_id': course_id,
            'skills_extracted': extracted_skills,
            'skills_added': skills_added
        }
        
    except Course.DoesNotExist:
        error_msg = f"Course {course_id} not found"
        logger.error(error_msg)
        return {'success': False, 'error': error_msg}
    except Exception as e:
        logger.error(f"Error analyzing skills for course {course_id}: {str(e)}")
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=120 * (self.request.retries + 1))
        return {'success': False, 'error': str(e)}

@shared_task
def bulk_analyze_course_skills_task():
    """Analyze skills for all courses that haven't been analyzed"""
    try:
        # Get courses without skills
        courses_without_skills = Course.objects.filter(
            is_active=True,
            skills_taught__isnull=True
        ).distinct()[:100]  # Process in batches
        
        total_processed = 0
        for course in courses_without_skills:
            # Queue individual analysis tasks
            analyze_course_skills_task.delay(course.id)
            total_processed += 1
        
        logger.info(f"Queued skill analysis for {total_processed} courses")
        return {
            'success': True,
            'courses_queued': total_processed
        }
        
    except Exception as e:
        logger.error(f"Error in bulk skill analysis: {str(e)}")
        return {'success': False, 'error': str(e)}

@shared_task
def update_course_popularity_scores_task():
    """Update popularity scores for all courses"""
    try:
        from django.db.models import Count, Avg
        
        # Update courses with recommendation counts and ratings
        courses = Course.objects.filter(is_active=True)
        updated_count = 0
        
        for course in courses:
            # Calculate popularity score based on various factors
            recommendation_count = UserRecommendation.objects.filter(course=course).count()
            bookmark_count = UserRecommendation.objects.filter(course=course, is_bookmarked=True).count()
            completion_count = UserRecommendation.objects.filter(course=course, is_completed=True).count()
            
            # Simple popularity score calculation
            popularity_score = (
                (recommendation_count * 1) +
                (bookmark_count * 2) +
                (completion_count * 3) +
                (course.total_students / 1000) +  # Normalize student count
                (course.rating * 10)  # Rating bonus
            )
            
            # Update course if score changed significantly
            if abs(course.popularity_score - popularity_score) > 5:
                course.popularity_score = popularity_score
                course.save(update_fields=['popularity_score'])
                updated_count += 1
        
        logger.info(f"Updated popularity scores for {updated_count} courses")
        return {
            'success': True,
            'courses_updated': updated_count
        }
        
    except Exception as e:
        logger.error(f"Error updating course popularity scores: {str(e)}")
        return {'success': False, 'error': str(e)}

@shared_task
def cleanup_old_recommendations_task():
    """Clean up old recommendations that are no longer relevant"""
    try:
        from datetime import timedelta
        
        # Delete recommendations older than 30 days that are not bookmarked or completed
        cutoff_date = timezone.now() - timedelta(days=30)
        
        old_recommendations = UserRecommendation.objects.filter(
            created_at__lt=cutoff_date,
            is_bookmarked=False,
            is_completed=False
        )
        
        deleted_count = old_recommendations.count()
        old_recommendations.delete()
        
        logger.info(f"Cleaned up {deleted_count} old recommendations")
        return {
            'success': True,
            'recommendations_deleted': deleted_count
        }
        
    except Exception as e:
        logger.error(f"Error cleaning up old recommendations: {str(e)}")
        return {'success': False, 'error': str(e)}

@shared_task
def send_recommendation_notifications_task():
    """Send notifications to users about new recommendations"""
    try:
        # This would integrate with a notification system
        # For now, just log the activity
        
        recent_recommendations = UserRecommendation.objects.filter(
            created_at__gte=timezone.now() - timezone.timedelta(hours=24),
            notification_sent=False
        ).select_related('user', 'course')
        
        notification_count = 0
        for recommendation in recent_recommendations:
            # Here you would send actual notifications (email, push, etc.)
            # For now, just mark as sent
            recommendation.notification_sent = True
            recommendation.save(update_fields=['notification_sent'])
            notification_count += 1
        
        logger.info(f"Processed {notification_count} recommendation notifications")
        return {
            'success': True,
            'notifications_sent': notification_count
        }
        
    except Exception as e:
        logger.error(f"Error sending recommendation notifications: {str(e)}")
        return {'success': False, 'error': str(e)}
