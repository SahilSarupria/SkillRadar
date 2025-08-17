from celery import shared_task
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from .models import UserStats, SystemStats, UserActivity
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

@shared_task
def update_user_stats_task(user_id):
    """Update statistics for a specific user"""
    try:
        user = User.objects.get(id=user_id)
        user_stats, created = UserStats.objects.get_or_create(user=user)
        user_stats.update_stats()
        
        logger.info(f"Updated stats for user {user.email}")
        return {
            'success': True,
            'user_id': user_id,
            'stats_updated': True
        }
        
    except User.DoesNotExist:
        logger.error(f"User {user_id} not found")
        return {'success': False, 'error': 'User not found'}
    except Exception as e:
        logger.error(f"Error updating stats for user {user_id}: {str(e)}")
        return {'success': False, 'error': str(e)}

@shared_task
def update_all_user_stats_task():
    """Update statistics for all users"""
    try:
        users = User.objects.all()
        updated_count = 0
        
        for user in users:
            user_stats, created = UserStats.objects.get_or_create(user=user)
            user_stats.update_stats()
            updated_count += 1
        
        logger.info(f"Updated stats for {updated_count} users")
        return {
            'success': True,
            'users_updated': updated_count
        }
        
    except Exception as e:
        logger.error(f"Error updating all user stats: {str(e)}")
        return {'success': False, 'error': str(e)}

@shared_task
def generate_daily_system_stats_task(date_str=None):
    """Generate daily system statistics"""
    try:
        if date_str:
            from datetime import datetime
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        else:
            date = timezone.now().date()
        
        stats = SystemStats.generate_daily_stats(date)
        
        logger.info(f"Generated system stats for {date}")
        return {
            'success': True,
            'date': str(date),
            'stats_generated': True
        }
        
    except Exception as e:
        logger.error(f"Error generating daily stats: {str(e)}")
        return {'success': False, 'error': str(e)}

@shared_task
def cleanup_old_activities_task(days=90):
    """Clean up old user activities"""
    try:
        cutoff_date = timezone.now() - timedelta(days=days)
        
        old_activities = UserActivity.objects.filter(created_at__lt=cutoff_date)
        deleted_count = old_activities.count()
        old_activities.delete()
        
        logger.info(f"Cleaned up {deleted_count} old activities")
        return {
            'success': True,
            'activities_deleted': deleted_count
        }
        
    except Exception as e:
        logger.error(f"Error cleaning up old activities: {str(e)}")
        return {'success': False, 'error': str(e)}

@shared_task
def generate_weekly_reports_task():
    """Generate weekly reports for all users"""
    try:
        # This would generate and send weekly reports
        # For now, just log the activity
        
        active_users = User.objects.filter(
            activities__created_at__gte=timezone.now() - timedelta(days=7)
        ).distinct()
        
        report_count = 0
        for user in active_users:
            # Generate report data
            user_stats, created = UserStats.objects.get_or_create(user=user)
            user_stats.update_stats()
            
            # Here you would send the actual report
            # For now, just count
            report_count += 1
        
        logger.info(f"Generated weekly reports for {report_count} users")
        return {
            'success': True,
            'reports_generated': report_count
        }
        
    except Exception as e:
        logger.error(f"Error generating weekly reports: {str(e)}")
        return {'success': False, 'error': str(e)}
