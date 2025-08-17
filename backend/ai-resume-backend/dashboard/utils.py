from django.contrib.auth import get_user_model
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import timedelta, datetime
from .models import UserActivity, UserStats
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

class DashboardDataAggregator:
    """Aggregate data for user dashboard"""
    
    def __init__(self, user):
        self.user = user
    
    def get_dashboard_data(self):
        """Get comprehensive dashboard data"""
        return {
            'user_stats': self._get_user_stats(),
            'recent_activities': self._get_recent_activities(),
            'recent_resumes': self._get_recent_resumes(),
            'pending_analyses': self._get_pending_analyses(),
            'top_skills': self._get_top_skills(),
            'critical_skill_gaps': self._get_critical_skill_gaps(),
            'new_recommendations': self._get_new_recommendations(),
            'bookmarked_courses': self._get_bookmarked_courses(),
            'in_progress_courses': self._get_in_progress_courses(),
            'weekly_goal_progress': self._get_weekly_goal_progress(),
            'monthly_achievements': self._get_monthly_achievements()
        }
    
    def _get_user_stats(self):
        """Get or create user stats"""
        user_stats, created = UserStats.objects.get_or_create(user=self.user)
        if created or user_stats.updated_at < timezone.now() - timedelta(hours=1):
            user_stats.update_stats()
        return user_stats
    
    def _get_recent_activities(self):
        """Get recent user activities"""
        return UserActivity.objects.filter(
            user=self.user
        ).order_by('-created_at')[:10]
    
    def _get_recent_resumes(self):
        """Get recent resumes"""
        from resumes.models import Resume
        
        resumes = Resume.objects.filter(
            user=self.user
        ).order_by('-created_at')[:5]
        
        return [
            {
                'id': resume.id,
                'title': resume.title,
                'status': resume.conversion_status,
                'created_at': resume.created_at,
                'file_type': resume.file_type
            }
            for resume in resumes
        ]
    
    def _get_pending_analyses(self):
        """Get count of pending analyses"""
        from resumes.models import Resume
        
        return Resume.objects.filter(
            user=self.user,
            conversion_status='completed'
        ).exclude(
            analyses__isnull=False
        ).count()
    
    def _get_top_skills(self):
        """Get user's top skills"""
        from skills.models import SkillGapAnalysis
        
        analyses = SkillGapAnalysis.objects.filter(user=self.user)
        skill_counts = {}
        
        for analysis in analyses:
            for skill_data in analysis.current_skills:
                skill_name = skill_data.get('skill', '')
                level = skill_data.get('level', 'beginner')
                
                if skill_name not in skill_counts:
                    skill_counts[skill_name] = {'count': 0, 'max_level': level}
                
                skill_counts[skill_name]['count'] += 1
                # Update max level if current is higher
                levels = ['beginner', 'intermediate', 'advanced', 'expert']
                if levels.index(level) > levels.index(skill_counts[skill_name]['max_level']):
                    skill_counts[skill_name]['max_level'] = level
        
        # Sort by count and return top 10
        top_skills = sorted(
            [
                {'skill': skill, 'level': data['max_level'], 'frequency': data['count']}
                for skill, data in skill_counts.items()
            ],
            key=lambda x: x['frequency'],
            reverse=True
        )[:10]
        
        return top_skills
    
    def _get_critical_skill_gaps(self):
        """Get critical skill gaps"""
        from skills.models import SkillGapAnalysis
        
        analyses = SkillGapAnalysis.objects.filter(user=self.user).order_by('-created_at')[:3]
        critical_gaps = []
        
        for analysis in analyses:
            for gap in analysis.skill_gaps:
                if gap.get('priority') in ['critical', 'high']:
                    critical_gaps.append({
                        'skill': gap.get('skill', ''),
                        'priority': gap.get('priority', 'medium'),
                        'required_level': gap.get('required_level', 'intermediate'),
                        'current_level': gap.get('current_level', 'none'),
                        'analysis_date': analysis.created_at
                    })
        
        return critical_gaps[:5]
    
    def _get_new_recommendations(self):
        """Get count of new recommendations"""
        from recommendations.models import UserRecommendation
        
        return UserRecommendation.objects.filter(
            user=self.user,
            created_at__gte=timezone.now() - timedelta(days=7)
        ).count()
    
    def _get_bookmarked_courses(self):
        """Get bookmarked courses"""
        from recommendations.models import UserRecommendation
        
        bookmarks = UserRecommendation.objects.filter(
            user=self.user,
            is_bookmarked=True
        ).select_related('course').order_by('-created_at')[:5]
        
        return [
            {
                'id': rec.course.id,
                'title': rec.course.title,
                'platform': rec.course.platform.name,
                'rating': rec.course.rating,
                'is_free': rec.course.is_free,
                'bookmarked_at': rec.updated_at
            }
            for rec in bookmarks
        ]
    
    def _get_in_progress_courses(self):
        """Get courses in progress"""
        from recommendations.models import UserRecommendation
        
        in_progress = UserRecommendation.objects.filter(
            user=self.user,
            progress_percentage__gt=0,
            progress_percentage__lt=100
        ).select_related('course').order_by('-updated_at')[:5]
        
        return [
            {
                'id': rec.course.id,
                'title': rec.course.title,
                'platform': rec.course.platform.name,
                'progress': rec.progress_percentage,
                'last_updated': rec.updated_at
            }
            for rec in in_progress
        ]
    
    def _get_weekly_goal_progress(self):
        """Get weekly goal progress"""
        week_start = timezone.now().date() - timedelta(days=timezone.now().weekday())
        
        # Count activities this week
        weekly_activities = UserActivity.objects.filter(
            user=self.user,
            created_at__date__gte=week_start
        ).count()
        
        # Set weekly goal (could be user-configurable)
        weekly_goal = 10
        progress_percentage = min((weekly_activities / weekly_goal) * 100, 100)
        
        return {
            'current': weekly_activities,
            'goal': weekly_goal,
            'percentage': round(progress_percentage, 1),
            'week_start': week_start
        }
    
    def _get_monthly_achievements(self):
        """Get monthly achievements"""
        month_start = timezone.now().replace(day=1).date()
        
        achievements = []
        
        # Resume achievements
        monthly_resumes = self.user.resumes.filter(created_at__date__gte=month_start).count()
        if monthly_resumes >= 5:
            achievements.append({
                'title': 'Resume Master',
                'description': f'Uploaded {monthly_resumes} resumes this month',
                'type': 'resume',
                'earned_at': timezone.now()
            })
        
        # Learning achievements
        from recommendations.models import UserRecommendation
        monthly_completions = UserRecommendation.objects.filter(
            user=self.user,
            is_completed=True,
            completed_at__date__gte=month_start
        ).count()
        
        if monthly_completions >= 3:
            achievements.append({
                'title': 'Learning Champion',
                'description': f'Completed {monthly_completions} courses this month',
                'type': 'learning',
                'earned_at': timezone.now()
            })
        
        # Streak achievements
        user_stats = self._get_user_stats()
        if user_stats.streak_days >= 7:
            achievements.append({
                'title': 'Consistency King',
                'description': f'{user_stats.streak_days} day login streak',
                'type': 'engagement',
                'earned_at': timezone.now()
            })
        
        return achievements
    
    def get_analytics_data(self, days=30):
        """Get analytics data for charts"""
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days-1)
        
        return {
            'user_growth': self._get_user_activity_trend(start_date, end_date),
            'resume_activity': self._get_resume_activity_trend(start_date, end_date),
            'skill_trends': self._get_skill_trends(start_date, end_date),
            'recommendation_effectiveness': self._get_recommendation_effectiveness(),
            'platform_popularity': self._get_platform_popularity(),
            'daily_active_users': self._get_daily_activity(start_date, end_date),
            'weekly_conversions': self._get_weekly_conversions(start_date, end_date),
            'monthly_completions': self._get_monthly_completions()
        }
    
    def _get_user_activity_trend(self, start_date, end_date):
        """Get user activity trend over time"""
        activities = UserActivity.objects.filter(
            user=self.user,
            created_at__date__range=[start_date, end_date]
        ).extra(
            select={'day': 'date(created_at)'}
        ).values('day').annotate(
            count=Count('id')
        ).order_by('day')
        
        return [
            {'date': item['day'], 'count': item['count']}
            for item in activities
        ]
    
    def _get_resume_activity_trend(self, start_date, end_date):
        """Get resume activity trend"""
        from resumes.models import Resume
        
        resumes = Resume.objects.filter(
            user=self.user,
            created_at__date__range=[start_date, end_date]
        ).extra(
            select={'day': 'date(created_at)'}
        ).values('day').annotate(
            count=Count('id')
        ).order_by('day')
        
        return [
            {'date': item['day'], 'count': item['count']}
            for item in resumes
        ]
    
    def _get_skill_trends(self, start_date, end_date):
        """Get skill analysis trends"""
        from skills.models import SkillGapAnalysis
        
        analyses = SkillGapAnalysis.objects.filter(
            user=self.user,
            created_at__date__range=[start_date, end_date]
        )
        
        skill_counts = {}
        for analysis in analyses:
            for skill_data in analysis.current_skills:
                skill = skill_data.get('skill', '')
                if skill not in skill_counts:
                    skill_counts[skill] = 0
                skill_counts[skill] += 1
        
        return [
            {'skill': skill, 'count': count}
            for skill, count in sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        ]
    
    def _get_recommendation_effectiveness(self):
        """Get recommendation effectiveness metrics"""
        from recommendations.models import UserRecommendation
        
        recommendations = UserRecommendation.objects.filter(user=self.user)
        total = recommendations.count()
        
        if total == 0:
            return {'total': 0, 'bookmarked': 0, 'started': 0, 'completed': 0}
        
        bookmarked = recommendations.filter(is_bookmarked=True).count()
        started = recommendations.filter(progress_percentage__gt=0).count()
        completed = recommendations.filter(is_completed=True).count()
        
        return {
            'total': total,
            'bookmarked': bookmarked,
            'started': started,
            'completed': completed,
            'bookmark_rate': round((bookmarked / total) * 100, 1),
            'start_rate': round((started / total) * 100, 1),
            'completion_rate': round((completed / total) * 100, 1) if started > 0 else 0
        }
    
    def _get_platform_popularity(self):
        """Get platform popularity for user"""
        from recommendations.models import UserRecommendation
        
        platforms = UserRecommendation.objects.filter(
            user=self.user
        ).values(
            'course__platform__name'
        ).annotate(
            count=Count('id')
        ).order_by('-count')
        
        return [
            {'platform': item['course__platform__name'], 'count': item['count']}
            for item in platforms
        ]
    
    def _get_daily_activity(self, start_date, end_date):
        """Get daily activity counts"""
        activities = UserActivity.objects.filter(
            user=self.user,
            created_at__date__range=[start_date, end_date]
        ).extra(
            select={'day': 'date(created_at)'}
        ).values('day').annotate(
            count=Count('id')
        ).order_by('day')
        
        return [
            {'date': item['day'], 'activities': item['count']}
            for item in activities
        ]
    
    def _get_weekly_conversions(self, start_date, end_date):
        """Get weekly conversion counts"""
        from resumes.models import Resume
        
        # Group by week
        conversions = Resume.objects.filter(
            user=self.user,
            conversion_status='completed',
            created_at__date__range=[start_date, end_date]
        ).extra(
            select={'week': 'date_trunc(\'week\', created_at)'}
        ).values('week').annotate(
            count=Count('id')
        ).order_by('week')
        
        return [
            {'week': item['week'], 'conversions': item['count']}
            for item in conversions
        ]
    
    def _get_monthly_completions(self):
        """Get monthly course completions"""
        from recommendations.models import UserRecommendation
        
        completions = UserRecommendation.objects.filter(
            user=self.user,
            is_completed=True
        ).extra(
            select={'month': 'date_trunc(\'month\', completed_at)'}
        ).values('month').annotate(
            count=Count('id')
        ).order_by('month')
        
        return [
            {'month': item['month'], 'completions': item['count']}
            for item in completions
        ]
    
    def get_progress_summary(self):
        """Get overall progress summary"""
        user_stats = self._get_user_stats()
        
        return {
            'resume_progress': {
                'total_uploaded': user_stats.total_resumes,
                'total_converted': user_stats.total_conversions,
                'total_analyzed': user_stats.total_analyses,
                'conversion_rate': round((user_stats.total_conversions / user_stats.total_resumes) * 100, 1) if user_stats.total_resumes > 0 else 0
            },
            'learning_progress': {
                'recommendations_received': user_stats.total_recommendations_received,
                'courses_bookmarked': user_stats.total_courses_bookmarked,
                'courses_started': user_stats.total_courses_started,
                'courses_completed': user_stats.total_courses_completed,
                'completion_rate': round((user_stats.total_courses_completed / user_stats.total_courses_started) * 100, 1) if user_stats.total_courses_started > 0 else 0
            },
            'skill_progress': {
                'skills_identified': user_stats.total_skills_identified,
                'skill_gaps_found': user_stats.total_skill_gaps,
                'improvement_areas': user_stats.total_skill_gaps - user_stats.total_courses_completed
            },
            'engagement': {
                'total_logins': user_stats.total_logins,
                'current_streak': user_stats.streak_days,
                'last_active': user_stats.last_active
            }
        }
    
    def get_achievements(self):
        """Get user achievements"""
        user_stats = self._get_user_stats()
        achievements = []
        
        # Resume achievements
        if user_stats.total_resumes >= 1:
            achievements.append({
                'id': 'first_resume',
                'title': 'First Steps',
                'description': 'Uploaded your first resume',
                'category': 'resume',
                'earned': True,
                'progress': 100
            })
        
        if user_stats.total_resumes >= 5:
            achievements.append({
                'id': 'resume_collector',
                'title': 'Resume Collector',
                'description': 'Uploaded 5 resumes',
                'category': 'resume',
                'earned': True,
                'progress': 100
            })
        
        if user_stats.total_conversions >= 10:
            achievements.append({
                'id': 'conversion_master',
                'title': 'Conversion Master',
                'description': 'Converted 10 resumes',
                'category': 'resume',
                'earned': True,
                'progress': 100
            })
        
        # Learning achievements
        if user_stats.total_courses_completed >= 1:
            achievements.append({
                'id': 'first_completion',
                'title': 'Learning Begins',
                'description': 'Completed your first course',
                'category': 'learning',
                'earned': True,
                'progress': 100
            })
        
        if user_stats.total_courses_completed >= 5:
            achievements.append({
                'id': 'dedicated_learner',
                'title': 'Dedicated Learner',
                'description': 'Completed 5 courses',
                'category': 'learning',
                'earned': True,
                'progress': 100
            })
        
        # Engagement achievements
        if user_stats.streak_days >= 7:
            achievements.append({
                'id': 'week_streak',
                'title': 'Week Warrior',
                'description': '7 day login streak',
                'category': 'engagement',
                'earned': True,
                'progress': 100
            })
        
        if user_stats.streak_days >= 30:
            achievements.append({
                'id': 'month_streak',
                'title': 'Monthly Master',
                'description': '30 day login streak',
                'category': 'engagement',
                'earned': True,
                'progress': 100
            })
        
        # Progress achievements (not yet earned)
        if user_stats.total_courses_completed < 10:
            achievements.append({
                'id': 'course_champion',
                'title': 'Course Champion',
                'description': 'Complete 10 courses',
                'category': 'learning',
                'earned': False,
                'progress': (user_stats.total_courses_completed / 10) * 100
            })
        
        return achievements

class ActivityTracker:
    """Track user activities"""
    
    def track_activity(self, user, activity_type, description='', metadata=None, request=None):
        """Track a user activity"""
        if metadata is None:
            metadata = {}
        
        # Get IP and user agent from request if available
        ip_address = None
        user_agent = ''
        
        if request:
            ip_address = self._get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        activity = UserActivity.objects.create(
            user=user,
            activity_type=activity_type,
            description=description,
            metadata=metadata,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        # Update user stats if needed
        if activity_type == 'login':
            self._update_login_stats(user)
        
        return activity
    
    def _get_client_ip(self, request):
        """Get client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def _update_login_stats(self, user):
        """Update login-related stats"""
        user_stats, created = UserStats.objects.get_or_create(user=user)
        user_stats.total_logins += 1
        user_stats.last_active = timezone.now()
        user_stats.save()

class AdminAnalytics:
    """Admin analytics utilities"""
    
    def get_comprehensive_analytics(self, days=30):
        """Get comprehensive analytics for admin dashboard"""
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days-1)
        
        return {
            'overview': self._get_overview_stats(),
            'user_analytics': self._get_user_analytics(start_date, end_date),
            'resume_analytics': self._get_resume_analytics(start_date, end_date),
            'recommendation_analytics': self._get_recommendation_analytics(start_date, end_date),
            'platform_analytics': self._get_platform_analytics(),
            'engagement_analytics': self._get_engagement_analytics(start_date, end_date)
        }
    
    def _get_overview_stats(self):
        """Get overview statistics"""
        from resumes.models import Resume
        from recommendations.models import Course, UserRecommendation
        
        return {
            'total_users': User.objects.count(),
            'active_users_30d': UserActivity.objects.filter(
                created_at__gte=timezone.now() - timedelta(days=30)
            ).values('user').distinct().count(),
            'total_resumes': Resume.objects.count(),
            'total_courses': Course.objects.filter(is_active=True).count(),
            'total_recommendations': UserRecommendation.objects.count(),
            'total_activities': UserActivity.objects.count()
        }
    
    def _get_user_analytics(self, start_date, end_date):
        """Get user analytics"""
        new_users = User.objects.filter(
            date_joined__date__range=[start_date, end_date]
        ).extra(
            select={'day': 'date(date_joined)'}
        ).values('day').annotate(
            count=Count('id')
        ).order_by('day')
        
        return {
            'new_users_trend': [
                {'date': item['day'], 'count': item['count']}
                for item in new_users
            ]
        }
    
    def _get_resume_analytics(self, start_date, end_date):
        """Get resume analytics"""
        from resumes.models import Resume
        
        resume_uploads = Resume.objects.filter(
            created_at__date__range=[start_date, end_date]
        ).extra(
            select={'day': 'date(created_at)'}
        ).values('day').annotate(
            count=Count('id')
        ).order_by('day')
        
        return {
            'upload_trend': [
                {'date': item['day'], 'count': item['count']}
                for item in resume_uploads
            ]
        }
    
    def _get_recommendation_analytics(self, start_date, end_date):
        """Get recommendation analytics"""
        from recommendations.models import UserRecommendation
        
        recommendations = UserRecommendation.objects.filter(
            created_at__date__range=[start_date, end_date]
        ).extra(
            select={'day': 'date(created_at)'}
        ).values('day').annotate(
            count=Count('id')
        ).order_by('day')
        
        return {
            'recommendation_trend': [
                {'date': item['day'], 'count': item['count']}
                for item in recommendations
            ]
        }
    
    def _get_platform_analytics(self):
        """Get platform analytics"""
        from recommendations.models import Course
        
        platform_stats = Course.objects.filter(
            is_active=True
        ).values(
            'platform__name'
        ).annotate(
            course_count=Count('id'),
            avg_rating=Avg('rating')
        ).order_by('-course_count')
        
        return {
            'platform_distribution': [
                {
                    'platform': item['platform__name'],
                    'courses': item['course_count'],
                    'avg_rating': round(item['avg_rating'] or 0, 2)
                }
                for item in platform_stats
            ]
        }
    
    def _get_engagement_analytics(self, start_date, end_date):
        """Get engagement analytics"""
        activity_types = UserActivity.objects.filter(
            created_at__date__range=[start_date, end_date]
        ).values('activity_type').annotate(
            count=Count('id')
        ).order_by('-count')
        
        return {
            'activity_distribution': [
                {'activity': item['activity_type'], 'count': item['count']}
                for item in activity_types
            ]
        }
