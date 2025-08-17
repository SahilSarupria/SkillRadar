from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import timedelta, datetime
from .models import UserActivity, UserStats, SystemStats
from .serializers import (
    UserActivitySerializer, UserStatsSerializer, DashboardSummarySerializer,
    SystemStatsSerializer, AnalyticsSerializer
)
from .utils import DashboardDataAggregator, ActivityTracker
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

class UserDashboardView(generics.RetrieveAPIView):
    """Get comprehensive dashboard data for authenticated user"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = DashboardSummarySerializer
    
    def get_object(self):
        """Get dashboard data for current user"""
        user = self.request.user
        aggregator = DashboardDataAggregator(user)
        return aggregator.get_dashboard_data()

class UserStatsView(generics.RetrieveAPIView):
    """Get detailed user statistics"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserStatsSerializer
    
    def get_object(self):
        user_stats, created = UserStats.objects.get_or_create(user=self.request.user)
        if created or user_stats.updated_at < timezone.now() - timedelta(hours=1):
            user_stats.update_stats()
        return user_stats

class UserActivityListView(generics.ListAPIView):
    """List user's recent activities"""
    serializer_class = UserActivitySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return UserActivity.objects.filter(
            user=self.request.user
        ).order_by('-created_at')[:50]

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_analytics(request):
    """Get user analytics data for charts"""
    try:
        user = request.user
        days = int(request.GET.get('days', 30))
        
        aggregator = DashboardDataAggregator(user)
        analytics_data = aggregator.get_analytics_data(days)
        
        serializer = AnalyticsSerializer(analytics_data)
        return Response(serializer.data)
        
    except Exception as e:
        logger.error(f"Error getting user analytics: {str(e)}")
        return Response(
            {'error': 'Failed to get analytics data'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def track_activity(request):
    """Track user activity"""
    try:
        activity_type = request.data.get('activity_type')
        description = request.data.get('description', '')
        metadata = request.data.get('metadata', {})
        
        if not activity_type:
            return Response(
                {'error': 'activity_type is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Track the activity
        tracker = ActivityTracker()
        activity = tracker.track_activity(
            user=request.user,
            activity_type=activity_type,
            description=description,
            metadata=metadata,
            request=request
        )
        
        serializer = UserActivitySerializer(activity)
        return Response(serializer.data)
        
    except Exception as e:
        logger.error(f"Error tracking activity: {str(e)}")
        return Response(
            {'error': 'Failed to track activity'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_progress_summary(request):
    """Get user's overall progress summary"""
    try:
        user = request.user
        aggregator = DashboardDataAggregator(user)
        progress_data = aggregator.get_progress_summary()
        
        return Response(progress_data)
        
    except Exception as e:
        logger.error(f"Error getting progress summary: {str(e)}")
        return Response(
            {'error': 'Failed to get progress summary'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_achievements(request):
    """Get user's achievements and milestones"""
    try:
        user = request.user
        aggregator = DashboardDataAggregator(user)
        achievements = aggregator.get_achievements()
        
        return Response({'achievements': achievements})
        
    except Exception as e:
        logger.error(f"Error getting achievements: {str(e)}")
        return Response(
            {'error': 'Failed to get achievements'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# Admin views
@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def system_stats(request):
    """Get system-wide statistics"""
    try:
        days = int(request.GET.get('days', 7))
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days-1)
        
        stats = SystemStats.objects.filter(
            date__range=[start_date, end_date]
        ).order_by('date')
        
        serializer = SystemStatsSerializer(stats, many=True)
        return Response({
            'stats': serializer.data,
            'date_range': {
                'start': start_date,
                'end': end_date
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting system stats: {str(e)}")
        return Response(
            {'error': 'Failed to get system stats'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def admin_analytics(request):
    """Get comprehensive admin analytics"""
    try:
        days = int(request.GET.get('days', 30))
        
        from .utils import AdminAnalytics
        admin_analytics = AdminAnalytics()
        analytics_data = admin_analytics.get_comprehensive_analytics(days)
        
        return Response(analytics_data)
        
    except Exception as e:
        logger.error(f"Error getting admin analytics: {str(e)}")
        return Response(
            {'error': 'Failed to get admin analytics'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([permissions.IsAdminUser])
def generate_daily_stats(request):
    """Manually generate daily statistics"""
    try:
        date_str = request.data.get('date')
        if date_str:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        else:
            date = timezone.now().date()
        
        stats = SystemStats.generate_daily_stats(date)
        serializer = SystemStatsSerializer(stats)
        
        return Response({
            'message': f'Daily stats generated for {date}',
            'stats': serializer.data
        })
        
    except Exception as e:
        logger.error(f"Error generating daily stats: {str(e)}")
        return Response(
            {'error': 'Failed to generate daily stats'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def user_engagement_report(request):
    """Get user engagement report"""
    try:
        # Get engagement metrics
        total_users = User.objects.count()
        active_users_7d = UserActivity.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=7)
        ).values('user').distinct().count()
        active_users_30d = UserActivity.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=30)
        ).values('user').distinct().count()
        
        # Calculate engagement rates
        engagement_7d = (active_users_7d / total_users * 100) if total_users > 0 else 0
        engagement_30d = (active_users_30d / total_users * 100) if total_users > 0 else 0
        
        # Get top activities
        top_activities = UserActivity.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=30)
        ).values('activity_type').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        # Get user retention data
        retention_data = []
        for days in [1, 7, 14, 30]:
            cutoff = timezone.now() - timedelta(days=days)
            retained_users = User.objects.filter(
                date_joined__lt=cutoff,
                activities__created_at__gte=cutoff
            ).distinct().count()
            total_eligible = User.objects.filter(date_joined__lt=cutoff).count()
            retention_rate = (retained_users / total_eligible * 100) if total_eligible > 0 else 0
            
            retention_data.append({
                'days': days,
                'retention_rate': round(retention_rate, 2),
                'retained_users': retained_users,
                'total_eligible': total_eligible
            })
        
        return Response({
            'total_users': total_users,
            'active_users_7d': active_users_7d,
            'active_users_30d': active_users_30d,
            'engagement_rate_7d': round(engagement_7d, 2),
            'engagement_rate_30d': round(engagement_30d, 2),
            'top_activities': list(top_activities),
            'retention_data': retention_data
        })
        
    except Exception as e:
        logger.error(f"Error getting engagement report: {str(e)}")
        return Response(
            {'error': 'Failed to get engagement report'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
