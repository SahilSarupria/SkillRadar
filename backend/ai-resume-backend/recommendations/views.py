from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.db.models import Q, Avg, Count
from django.utils import timezone
from .models import (
    LearningPlatform, Course, Skill, UserRecommendation, 
    LearningPath, UserProgress, AffiliateClick
)
from .serializers import (
    LearningPlatformSerializer, CourseSerializer, SkillSerializer,
    UserRecommendationSerializer, LearningPathSerializer, UserProgressSerializer,
    RecommendationRequestSerializer, LearningPathRequestSerializer,
    BookmarkCourseSerializer, CourseProgressSerializer, CourseRecommendationSerializer
)
from .utils import CourseRecommendationEngine, LearningPathRecommender, AffiliateManager
from .tasks import generate_user_recommendations_task, sync_platform_courses_task
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

class LearningPlatformListView(generics.ListAPIView):
    """List all active learning platforms"""
    queryset = LearningPlatform.objects.filter(is_active=True)
    serializer_class = LearningPlatformSerializer
    permission_classes = [permissions.AllowAny]

class CourseListView(generics.ListAPIView):
    """List courses with filtering and search"""
    serializer_class = CourseSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        queryset = Course.objects.filter(is_active=True).select_related('platform').prefetch_related('skills_taught')
        
        # Filter by platform
        platform = self.request.query_params.get('platform')
        if platform:
            queryset = queryset.filter(platform__name__icontains=platform)
        
        # Filter by skill
        skill = self.request.query_params.get('skill')
        if skill:
            queryset = queryset.filter(skills_taught__name__icontains=skill)
        
        # Filter by level
        level = self.request.query_params.get('level')
        if level:
            queryset = queryset.filter(level=level)
        
        # Filter by price
        is_free = self.request.query_params.get('is_free')
        if is_free is not None:
            queryset = queryset.filter(is_free=is_free.lower() == 'true')
        
        # Search by title or description
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(description__icontains=search)
            )
        
        # Order by rating and popularity
        return queryset.order_by('-rating', '-total_students')

class CourseDetailView(generics.RetrieveAPIView):
    """Get detailed course information"""
    queryset = Course.objects.filter(is_active=True)
    serializer_class = CourseSerializer
    permission_classes = [permissions.AllowAny]

class SkillListView(generics.ListAPIView):
    """List all skills"""
    queryset = Skill.objects.all().order_by('name')
    serializer_class = SkillSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by category
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)
        
        # Search by name
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search)
        
        return queryset

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def generate_recommendations(request):
    """Generate personalized course recommendations"""
    serializer = RecommendationRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Get validated data
        skill_gaps = serializer.validated_data.get('skill_gaps', [])
        learning_goals = serializer.validated_data.get('learning_goals', [])
        limit = serializer.validated_data.get('limit', 10)
        include_paid = serializer.validated_data.get('include_paid', True)
        include_free = serializer.validated_data.get('include_free', True)
        preferred_platforms = serializer.validated_data.get('preferred_platforms', [])
        
        # Generate recommendations
        recommendation_engine = CourseRecommendationEngine()
        recommendations = recommendation_engine.generate_recommendations(
            user=request.user,
            skill_gaps=skill_gaps,
            learning_goals=learning_goals,
            limit=limit
        )
        
        # Filter by price preferences
        if not include_paid:
            recommendations = [r for r in recommendations if r['course'].is_free]
        if not include_free:
            recommendations = [r for r in recommendations if not r['course'].is_free]
        
        # Filter by preferred platforms
        if preferred_platforms:
            recommendations = [
                r for r in recommendations 
                if r['course'].platform.name.lower() in [p.lower() for p in preferred_platforms]
            ]
        
        # Save recommendations to database
        saved_recommendations = []
        for rec in recommendations:
            user_rec, created = UserRecommendation.objects.update_or_create(
                user=request.user,
                course=rec['course'],
                defaults={
                    'target_skill': rec.get('target_skill'),
                    'relevance_score': rec['relevance_score'],
                    'recommendation_type': rec['recommendation_type'],
                    'recommendation_reason': rec['recommendation_reason'],
                    'priority': rec['priority']
                }
            )
            saved_recommendations.append(user_rec)
        
        # Serialize and return
        serializer = UserRecommendationSerializer(saved_recommendations, many=True, context={'request': request})
        return Response({
            'recommendations': serializer.data,
            'total_count': len(saved_recommendations),
            'generated_at': timezone.now()
        })
        
    except Exception as e:
        logger.error(f"Error generating recommendations for user {request.user.id}: {str(e)}")
        return Response(
            {'error': 'Failed to generate recommendations'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def generate_learning_paths(request):
    """Generate personalized learning paths"""
    serializer = LearningPathRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Get validated data
        skill_gaps = serializer.validated_data['skill_gaps']
        career_goal = serializer.validated_data.get('career_goal', '')
        time_commitment = serializer.validated_data.get('time_commitment_hours_per_week', 10)
        budget_limit = serializer.validated_data.get('budget_limit')
        
        # Generate learning paths
        path_recommender = LearningPathRecommender()
        path_recommendations = path_recommender.recommend_learning_paths(
            user=request.user,
            skill_gaps=skill_gaps,
            career_goal=career_goal
        )
        
        # Filter by budget if specified
        if budget_limit:
            path_recommendations = [
                path for path in path_recommendations 
                if path.get('estimated_cost', 0) <= float(budget_limit)
            ]
        
        # Adjust time estimates based on user's commitment
        for path in path_recommendations:
            original_weeks = path.get('estimated_weeks', 8)
            adjusted_weeks = max(int(original_weeks * (10 / time_commitment)), 2)
            path['estimated_weeks'] = adjusted_weeks
        
        # Save learning paths to database
        saved_paths = []
        for path_data in path_recommendations[:5]:  # Limit to top 5 paths
            learning_path, created = LearningPath.objects.update_or_create(
                user=request.user,
                title=path_data['title'],
                defaults={
                    'description': path_data['description'],
                    'estimated_weeks': path_data['estimated_weeks'],
                    'estimated_cost': path_data.get('estimated_cost', 0),
                    'difficulty_level': path_data.get('difficulty_level', 'intermediate'),
                    'relevance_score': path_data['relevance_score']
                }
            )
            
            # Add skills to the learning path
            skill_names = path_data.get('skills', [])
            for skill_name in skill_names:
                skill, _ = Skill.objects.get_or_create(name=skill_name)
                learning_path.skills.add(skill)
            
            saved_paths.append(learning_path)
        
        # Serialize and return
        serializer = LearningPathSerializer(saved_paths, many=True, context={'request': request})
        return Response({
            'learning_paths': serializer.data,
            'total_count': len(saved_paths),
            'generated_at': timezone.now()
        })
        
    except Exception as e:
        logger.error(f"Error generating learning paths for user {request.user.id}: {str(e)}")
        return Response(
            {'error': 'Failed to generate learning paths'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

class UserRecommendationListView(generics.ListAPIView):
    """List user's saved recommendations"""
    serializer_class = UserRecommendationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return UserRecommendation.objects.filter(
            user=self.request.user
        ).select_related('course', 'target_skill').order_by('-created_at')

class UserLearningPathListView(generics.ListAPIView):
    """List user's learning paths"""
    serializer_class = LearningPathSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return LearningPath.objects.filter(
            user=self.request.user
        ).prefetch_related('skills', 'recommended_courses').order_by('-created_at')

class UserProgressListView(generics.ListAPIView):
    """List user's learning progress"""
    serializer_class = UserProgressSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return UserProgress.objects.filter(
            user=self.request.user
        ).select_related('learning_path').prefetch_related('completed_courses').order_by('-started_at')

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def bookmark_course(request):
    """Bookmark or unbookmark a course"""
    serializer = BookmarkCourseSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        course_id = serializer.validated_data['course_id']
        course = Course.objects.get(id=course_id, is_active=True)
        
        # Toggle bookmark status
        recommendation, created = UserRecommendation.objects.get_or_create(
            user=request.user,
            course=course,
            defaults={
                'recommendation_type': 'manual',
                'recommendation_reason': 'User bookmarked',
                'relevance_score': 75.0,
                'priority': 'medium'
            }
        )
        
        recommendation.is_bookmarked = not recommendation.is_bookmarked
        recommendation.save()
        
        return Response({
            'bookmarked': recommendation.is_bookmarked,
            'message': 'Course bookmarked' if recommendation.is_bookmarked else 'Course unbookmarked'
        })
        
    except Course.DoesNotExist:
        return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error bookmarking course: {str(e)}")
        return Response({'error': 'Failed to bookmark course'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def update_course_progress(request):
    """Update user's progress on a course"""
    serializer = CourseProgressSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        course_id = serializer.validated_data['course_id']
        progress_percentage = serializer.validated_data['progress_percentage']
        is_completed = serializer.validated_data['is_completed']
        
        course = Course.objects.get(id=course_id, is_active=True)
        
        # Update or create recommendation with progress
        recommendation, created = UserRecommendation.objects.get_or_create(
            user=request.user,
            course=course,
            defaults={
                'recommendation_type': 'manual',
                'recommendation_reason': 'User enrolled',
                'relevance_score': 75.0,
                'priority': 'medium'
            }
        )
        
        recommendation.progress_percentage = progress_percentage
        recommendation.is_completed = is_completed
        if is_completed:
            recommendation.completed_at = timezone.now()
        recommendation.save()
        
        return Response({
            'progress_percentage': progress_percentage,
            'is_completed': is_completed,
            'message': 'Progress updated successfully'
        })
        
    except Course.DoesNotExist:
        return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error updating course progress: {str(e)}")
        return Response({'error': 'Failed to update progress'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def track_affiliate_click(request, course_id):
    """Track affiliate link click"""
    try:
        course = Course.objects.get(id=course_id, is_active=True)
        
        # Generate affiliate link
        affiliate_manager = AffiliateManager()
        affiliate_link = affiliate_manager.generate_affiliate_link(course, request.user)
        
        # Track the click
        affiliate_manager.track_click(course, request.user, affiliate_link)
        
        return Response({
            'affiliate_link': affiliate_link,
            'course_title': course.title,
            'platform': course.platform.name
        })
        
    except Course.DoesNotExist:
        return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error tracking affiliate click: {str(e)}")
        return Response({'error': 'Failed to track click'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([permissions.IsAdminUser])
def sync_platform_courses(request):
    """Manually trigger course sync for all platforms"""
    try:
        # Trigger async task for each platform
        platforms = LearningPlatform.objects.filter(is_active=True)
        
        sync_results = []
        for platform in platforms:
            task = sync_platform_courses_task.delay(platform.name)
            sync_results.append({
                'platform': platform.name,
                'task_id': task.id,
                'status': 'queued'
            })
        
        return Response({
            'message': f'Course sync initiated for {len(platforms)} platforms',
            'sync_results': sync_results
        })
        
    except Exception as e:
        logger.error(f"Error initiating course sync: {str(e)}")
        return Response({'error': 'Failed to initiate sync'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def platform_stats(request):
    """Get platform statistics"""
    try:
        stats = LearningPlatform.objects.filter(is_active=True).annotate(
            total_courses=Count('courses', filter=Q(courses__is_active=True)),
            avg_rating=Avg('courses__rating', filter=Q(courses__is_active=True)),
            total_students=Count('courses__total_students', filter=Q(courses__is_active=True))
        ).values('name', 'total_courses', 'avg_rating', 'total_students')
        
        return Response({
            'platform_stats': list(stats),
            'total_platforms': len(stats)
        })
        
    except Exception as e:
        logger.error(f"Error getting platform stats: {str(e)}")
        return Response({'error': 'Failed to get stats'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
