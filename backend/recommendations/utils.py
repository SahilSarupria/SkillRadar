import requests
import openai
import json
from django.conf import settings
from django.utils import timezone
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class CourseRecommendationEngine:
    """Main engine for generating course recommendations"""
    
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
    
    def generate_recommendations(self, user, skill_gaps: List[Dict], learning_goals: List[Dict] = None, limit: int = 10) -> List[Dict]:
        """Generate personalized course recommendations"""
        
        recommendations = []
        
        # Get recommendations based on skill gaps
        for skill_gap in skill_gaps[:5]:  # Limit to top 5 skill gaps
            skill_recommendations = self._get_skill_based_recommendations(
                user, skill_gap, limit_per_skill=3
            )
            recommendations.extend(skill_recommendations)
        
        # Get recommendations based on learning goals
        if learning_goals:
            goal_recommendations = self._get_goal_based_recommendations(
                user, learning_goals, limit_per_goal=2
            )
            recommendations.extend(goal_recommendations)
        
        # Get trending and popular recommendations
        trending_recommendations = self._get_trending_recommendations(user, limit=3)
        recommendations.extend(trending_recommendations)
        
        # Remove duplicates and sort by relevance
        unique_recommendations = self._deduplicate_recommendations(recommendations)
        sorted_recommendations = sorted(unique_recommendations, key=lambda x: x['relevance_score'], reverse=True)
        
        return sorted_recommendations[:limit]
    
    def _get_skill_based_recommendations(self, user, skill_gap: Dict, limit_per_skill: int = 3) -> List[Dict]:
        """Get course recommendations for a specific skill gap"""
        from .models import Course, Skill
        
        skill_name = skill_gap.get('skill', '')
        required_level = skill_gap.get('required_level', 'intermediate')
        priority = skill_gap.get('priority', 'medium')
        
        # Find skill in database
        try:
            skill = Skill.objects.get(name__iexact=skill_name)
        except Skill.DoesNotExist:
            logger.warning(f"Skill not found: {skill_name}")
            return []
        
        # Find courses that teach this skill
        courses = Course.objects.filter(
            skills_taught=skill,
            is_active=True,
            level__in=self._get_appropriate_levels(required_level)
        ).order_by('-rating', '-total_students')[:limit_per_skill * 2]  # Get more to filter
        
        recommendations = []
        for course in courses:
            relevance_score = self._calculate_skill_relevance_score(course, skill_gap, user)
            
            if relevance_score > 50:  # Only recommend if relevance is above threshold
                recommendations.append({
                    'course_id': course.id,
                    'course': course,
                    'target_skill': skill,
                    'relevance_score': relevance_score,
                    'recommendation_type': 'skill_gap',
                    'recommendation_reason': f"Recommended to learn {skill_name} for your target role",
                    'priority': priority
                })
        
        return recommendations[:limit_per_skill]
    
    def _get_goal_based_recommendations(self, user, learning_goals: List[Dict], limit_per_goal: int = 2) -> List[Dict]:
        """Get course recommendations based on learning goals"""
        recommendations = []
        
        for goal in learning_goals:
            goal_recommendations = self._recommend_courses_for_goal(user, goal, limit_per_goal)
            recommendations.extend(goal_recommendations)
        
        return recommendations
    
    def _get_trending_recommendations(self, user, limit: int = 3) -> List[Dict]:
        """Get trending course recommendations"""
        from .models import Course
        
        # Get highly rated courses with recent high enrollment
        trending_courses = Course.objects.filter(
            is_active=True,
            rating__gte=4.0,
            total_students__gte=1000
        ).order_by('-total_students', '-rating')[:limit * 2]
        
        recommendations = []
        for course in trending_courses:
            # Check if course is relevant to user's profile
            relevance_score = self._calculate_trending_relevance_score(course, user)
            
            if relevance_score > 40:
                recommendations.append({
                    'course_id': course.id,
                    'course': course,
                    'target_skill': None,
                    'relevance_score': relevance_score,
                    'recommendation_type': 'trending',
                    'recommendation_reason': "Popular course in your field of interest",
                    'priority': 'low'
                })
        
        return recommendations[:limit]
    
    def _calculate_skill_relevance_score(self, course, skill_gap: Dict, user) -> float:
        """Calculate how relevant a course is for a specific skill gap"""
        score = 50.0  # Base score
        
        # Course rating bonus
        if course.rating >= 4.5:
            score += 15
        elif course.rating >= 4.0:
            score += 10
        elif course.rating >= 3.5:
            score += 5
        
        # Student count bonus (popularity)
        if course.total_students >= 10000:
            score += 10
        elif course.total_students >= 1000:
            score += 5
        
        # Level appropriateness
        required_level = skill_gap.get('required_level', 'intermediate')
        if course.level == required_level:
            score += 15
        elif self._is_level_appropriate(course.level, required_level):
            score += 10
        
        # Priority bonus
        priority = skill_gap.get('priority', 'medium')
        priority_bonus = {'critical': 20, 'high': 15, 'medium': 10, 'low': 5}
        score += priority_bonus.get(priority, 10)
        
        # Free course bonus for beginners
        if course.is_free and required_level in ['beginner', 'intermediate']:
            score += 10
        
        # Certificate bonus
        if course.has_certificate:
            score += 5
        
        # Recent update bonus
        if course.last_updated and course.last_updated > timezone.now() - timedelta(days=365):
            score += 5
        
        return min(score, 100.0)
    
    def _calculate_trending_relevance_score(self, course, user) -> float:
        """Calculate relevance score for trending courses"""
        score = 30.0  # Lower base score for trending
        
        # Course quality
        if course.rating >= 4.5:
            score += 20
        elif course.rating >= 4.0:
            score += 15
        
        # Popularity
        if course.total_students >= 50000:
            score += 15
        elif course.total_students >= 10000:
            score += 10
        
        # Free course bonus
        if course.is_free:
            score += 10
        
        return min(score, 100.0)
    
    def _get_appropriate_levels(self, required_level: str) -> List[str]:
        """Get appropriate course levels for a required skill level"""
        level_mapping = {
            'beginner': ['beginner', 'all_levels'],
            'intermediate': ['beginner', 'intermediate', 'all_levels'],
            'advanced': ['intermediate', 'advanced', 'all_levels'],
            'expert': ['advanced', 'all_levels']
        }
        return level_mapping.get(required_level, ['all_levels'])
    
    def _is_level_appropriate(self, course_level: str, required_level: str) -> bool:
        """Check if course level is appropriate for required level"""
        return course_level in self._get_appropriate_levels(required_level)
    
    def _recommend_courses_for_goal(self, user, goal: Dict, limit: int) -> List[Dict]:
        """Recommend courses for a specific learning goal"""
        # This would be more sophisticated in practice
        return []
    
    def _deduplicate_recommendations(self, recommendations: List[Dict]) -> List[Dict]:
        """Remove duplicate course recommendations"""
        seen_courses = set()
        unique_recommendations = []
        
        for rec in recommendations:
            course_id = rec['course_id']
            if course_id not in seen_courses:
                seen_courses.add(course_id)
                unique_recommendations.append(rec)
        
        return unique_recommendations

class PlatformIntegrator:
    """Integrate with various learning platforms"""
    
    def __init__(self, platform_name: str):
        self.platform_name = platform_name
        self.integration = self._get_integration_config(platform_name)
    
    def sync_courses(self) -> Dict[str, Any]:
        """Sync courses from the platform"""
        if self.platform_name.lower() == 'coursera':
            return self._sync_coursera_courses()
        elif self.platform_name.lower() == 'udemy':
            return self._sync_udemy_courses()
        elif self.platform_name.lower() == 'edx':
            return self._sync_edx_courses()
        else:
            return {'success': False, 'error': f'Platform {self.platform_name} not supported'}
    
    def _sync_coursera_courses(self) -> Dict[str, Any]:
        """Sync courses from Coursera"""
        try:
            # This would use Coursera's API
            # For now, return mock data
            return {
                'success': True,
                'courses_synced': 0,
                'message': 'Coursera sync not implemented yet'
            }
        except Exception as e:
            logger.error(f"Error syncing Coursera courses: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _sync_udemy_courses(self) -> Dict[str, Any]:
        """Sync courses from Udemy"""
        try:
            if not self.integration or not self.integration.api_key:
                return {'success': False, 'error': 'Udemy API key not configured'}
            
            # Udemy API integration
            headers = {
                'Authorization': f'Basic {self.integration.api_key}',
                'Accept': 'application/json'
            }
            
            # This is a simplified example - real implementation would be more comprehensive
            response = requests.get(
                'https://www.udemy.com/api-2.0/courses/',
                headers=headers,
                params={
                    'page_size': 100,
                    'fields[course]': 'title,headline,num_subscribers,avg_rating,price,visible_instructors'
                }
            )
            
            if response.status_code == 200:
                courses_data = response.json()
                synced_count = self._process_udemy_courses(courses_data.get('results', []))
                return {
                    'success': True,
                    'courses_synced': synced_count,
                    'message': f'Successfully synced {synced_count} Udemy courses'
                }
            else:
                return {'success': False, 'error': f'Udemy API error: {response.status_code}'}
                
        except Exception as e:
            logger.error(f"Error syncing Udemy courses: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _sync_edx_courses(self) -> Dict[str, Any]:
        """Sync courses from edX"""
        try:
            # edX has a public API for course discovery
            response = requests.get(
                'https://api.edx.org/catalog/v1/courses',
                params={'limit': 100}
            )
            
            if response.status_code == 200:
                courses_data = response.json()
                synced_count = self._process_edx_courses(courses_data.get('results', []))
                return {
                    'success': True,
                    'courses_synced': synced_count,
                    'message': f'Successfully synced {synced_count} edX courses'
                }
            else:
                return {'success': False, 'error': f'edX API error: {response.status_code}'}
                
        except Exception as e:
            logger.error(f"Error syncing edX courses: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _process_udemy_courses(self, courses_data: List[Dict]) -> int:
        """Process and save Udemy courses"""
        from .models import Course, LearningPlatform
        
        try:
            platform = LearningPlatform.objects.get(name__iexact='Udemy')
        except LearningPlatform.DoesNotExist:
            logger.error("Udemy platform not found in database")
            return 0
        
        synced_count = 0
        for course_data in courses_data:
            try:
                course, created = Course.objects.update_or_create(
                    platform=platform,
                    external_id=str(course_data.get('id', '')),
                    defaults={
                        'title': course_data.get('title', ''),
                        'description': course_data.get('headline', ''),
                        'instructor_name': self._get_instructor_names(course_data.get('visible_instructors', [])),
                        'rating': course_data.get('avg_rating', 0.0),
                        'total_students': course_data.get('num_subscribers', 0),
                        'price': course_data.get('price', 0),
                        'course_url': f"https://www.udemy.com/course/{course_data.get('url', '')}",
                        'last_updated': timezone.now(),
                        'is_free': course_data.get('price', 0) == 0,
                    }
                )
                if created:
                    synced_count += 1
            except Exception as e:
                logger.error(f"Error processing Udemy course {course_data.get('id')}: {str(e)}")
                continue
        
        return synced_count
    
    def _process_edx_courses(self, courses_data: List[Dict]) -> int:
        """Process and save edX courses"""
        from .models import Course, LearningPlatform
        
        try:
            platform = LearningPlatform.objects.get(name__iexact='edX')
        except LearningPlatform.DoesNotExist:
            logger.error("edX platform not found in database")
            return 0
        
        synced_count = 0
        for course_data in courses_data:
            try:
                course, created = Course.objects.update_or_create(
                    platform=platform,
                    external_id=course_data.get('key', ''),
                    defaults={
                        'title': course_data.get('title', ''),
                        'description': course_data.get('short_description', ''),
                        'course_url': course_data.get('marketing_url', ''),
                        'thumbnail_url': course_data.get('image', {}).get('src', ''),
                        'last_updated': timezone.now(),
                        'is_free': True,  # Most edX courses are free
                    }
                )
                if created:
                    synced_count += 1
            except Exception as e:
                logger.error(f"Error processing edX course {course_data.get('key')}: {str(e)}")
                continue
        
        return synced_count
    
    def _get_instructor_names(self, instructors: List[Dict]) -> str:
        """Extract instructor names from instructor data"""
        names = [instructor.get('display_name', '') for instructor in instructors]
        return ', '.join(filter(None, names))
    
    def _get_integration_config(self, platform_name: str):
        """Get integration configuration for platform"""
        from .models import LearningPlatform, PlatformIntegration
        
        try:
            platform = LearningPlatform.objects.get(name__iexact=platform_name)
            return platform.integration
        except (LearningPlatform.DoesNotExist, PlatformIntegration.DoesNotExist):
            return None

class LearningPathRecommender:
    """Recommend complete learning paths"""
    
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
    
    def recommend_learning_paths(self, user, skill_gaps: List[Dict], career_goal: str = "") -> List[Dict]:
        """Recommend complete learning paths based on skill gaps"""
        
        # Group related skills
        skill_groups = self._group_related_skills(skill_gaps)
        
        # Generate path recommendations for each group
        path_recommendations = []
        for group in skill_groups:
            path_rec = self._create_path_recommendation(user, group, career_goal)
            if path_rec:
                path_recommendations.append(path_rec)
        
        return sorted(path_recommendations, key=lambda x: x['relevance_score'], reverse=True)
    
    def _group_related_skills(self, skill_gaps: List[Dict]) -> List[List[Dict]]:
        """Group related skills together"""
        # This would use more sophisticated clustering in practice
        # For now, group by skill type or domain
        
        groups = {}
        for skill_gap in skill_gaps:
            skill_name = skill_gap.get('skill', '').lower()
            
            # Simple grouping logic
            if any(tech in skill_name for tech in ['python', 'javascript', 'java', 'programming']):
                group_key = 'programming'
            elif any(data in skill_name for data in ['data', 'analytics', 'sql', 'machine learning']):
                group_key = 'data_science'
            elif any(design in skill_name for design in ['design', 'ui', 'ux', 'photoshop']):
                group_key = 'design'
            elif any(mgmt in skill_name for mgmt in ['management', 'leadership', 'project']):
                group_key = 'management'
            else:
                group_key = 'general'
            
            if group_key not in groups:
                groups[group_key] = []
            groups[group_key].append(skill_gap)
        
        return list(groups.values())
    
    def _create_path_recommendation(self, user, skill_group: List[Dict], career_goal: str) -> Optional[Dict]:
        """Create a learning path recommendation for a skill group"""
        if not skill_group:
            return None
        
        # Calculate path metrics
        total_learning_time = sum(gap.get('estimated_learning_time', 40) for gap in skill_group)
        avg_priority = self._calculate_average_priority(skill_group)
        
        # Generate path details
        path_recommendation = {
            'title': self._generate_path_title(skill_group, career_goal),
            'description': self._generate_path_description(skill_group, career_goal),
            'skills': [gap.get('skill') for gap in skill_group],
            'estimated_weeks': max(total_learning_time // 10, 4),  # Assume 10 hours per week
            'estimated_cost': self._estimate_path_cost(skill_group),
            'difficulty_level': self._determine_path_difficulty(skill_group),
            'relevance_score': self._calculate_path_relevance_score(skill_group, avg_priority),
            'recommended_courses': self._get_recommended_courses_for_path(skill_group)
        }
        
        return path_recommendation
    
    def _calculate_average_priority(self, skill_group: List[Dict]) -> float:
        """Calculate average priority score for skill group"""
        priority_scores = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}
        scores = [priority_scores.get(gap.get('priority', 'medium'), 2) for gap in skill_group]
        return sum(scores) / len(scores) if scores else 2.0
    
    def _generate_path_title(self, skill_group: List[Dict], career_goal: str) -> str:
        """Generate a title for the learning path"""
        skills = [gap.get('skill', '') for gap in skill_group]
        
        if len(skills) == 1:
            return f"Master {skills[0]}"
        elif len(skills) <= 3:
            return f"Learn {', '.join(skills)}"
        else:
            # Try to find a common theme
            skill_text = ' '.join(skills).lower()
            if 'python' in skill_text or 'programming' in skill_text:
                return "Python Development Mastery"
            elif 'data' in skill_text or 'analytics' in skill_text:
                return "Data Science Fundamentals"
            elif 'design' in skill_text or 'ui' in skill_text:
                return "UI/UX Design Essentials"
            else:
                return f"Professional Development Path ({len(skills)} skills)"
    
    def _generate_path_description(self, skill_group: List[Dict], career_goal: str) -> str:
        """Generate description for the learning path"""
        skills = [gap.get('skill', '') for gap in skill_group]
        skill_count = len(skills)
        
        base_description = f"A comprehensive learning path covering {skill_count} essential skills: {', '.join(skills[:3])}"
        if skill_count > 3:
            base_description += f" and {skill_count - 3} more"
        
        if career_goal:
            base_description += f". Designed to help you achieve your goal of {career_goal}."
        else:
            base_description += ". Perfect for advancing your career and closing key skill gaps."
        
        return base_description
    
    def _estimate_path_cost(self, skill_group: List[Dict]) -> float:
        """Estimate the cost of the learning path"""
        # This would query actual course prices
        # For now, return an estimate based on skill count
        skill_count = len(skill_group)
        avg_course_cost = 50.0  # Average cost per course
        return skill_count * avg_course_cost
    
    def _determine_path_difficulty(self, skill_group: List[Dict]) -> str:
        """Determine the overall difficulty of the learning path"""
        required_levels = [gap.get('required_level', 'intermediate') for gap in skill_group]
        
        if any(level == 'expert' for level in required_levels):
            return 'advanced'
        elif any(level == 'advanced' for level in required_levels):
            return 'intermediate'
        else:
            return 'beginner'
    
    def _calculate_path_relevance_score(self, skill_group: List[Dict], avg_priority: float) -> float:
        """Calculate relevance score for the learning path"""
        base_score = 50.0
        
        # Priority bonus
        base_score += avg_priority * 10
        
        # Skill count bonus (more skills = more comprehensive)
        skill_count = len(skill_group)
        if skill_count >= 5:
            base_score += 20
        elif skill_count >= 3:
            base_score += 15
        elif skill_count >= 2:
            base_score += 10
        
        return min(base_score, 100.0)
    
    def _get_recommended_courses_for_path(self, skill_group: List[Dict]) -> List[Dict]:
        """Get recommended courses for the learning path"""
        # This would query the Course model for relevant courses
        # For now, return placeholder data
        return [
            {
                'title': f"Course for {skill_group[0].get('skill', 'Unknown')}",
                'platform': 'Coursera',
                'duration_hours': 20,
                'price': 49.99
            }
        ]

class CourseContentAnalyzer:
    """Analyze course content and match with skills"""
    
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
    
    def analyze_course_skills(self, course_title: str, course_description: str) -> List[str]:
        """Analyze course content and extract skills taught"""
        
        system_prompt = """
        You are an expert at analyzing educational content. Given a course title and description, 
        extract the specific skills that students will learn from this course.
        
        Return a JSON array of skill names. Focus on:
        1. Technical skills (programming languages, tools, frameworks)
        2. Soft skills (communication, leadership, problem-solving)
        3. Domain-specific skills (marketing, finance, design)
        4. Certifications or qualifications
        
        Example: ["Python", "Data Analysis", "Machine Learning", "Problem Solving"]
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Course Title: {course_title}\n\nDescription: {course_description}"}
                ],
                temperature=0.2,
                max_tokens=300
            )
            
            result = response.choices[0].message.content
            skills = json.loads(result)
            return skills if isinstance(skills, list) else []
            
        except Exception as e:
            logger.error(f"Error analyzing course skills: {str(e)}")
            return self._fallback_skill_extraction(course_title, course_description)
    
    def _fallback_skill_extraction(self, title: str, description: str) -> List[str]:
        """Fallback skill extraction using keyword matching"""
        text = f"{title} {description}".lower()
        
        # Common skills to look for
        skill_keywords = {
            'Python': ['python'],
            'JavaScript': ['javascript', 'js'],
            'Data Analysis': ['data analysis', 'analytics'],
            'Machine Learning': ['machine learning', 'ml', 'ai'],
            'Project Management': ['project management', 'pm'],
            'Leadership': ['leadership', 'management'],
            'Communication': ['communication'],
            'SQL': ['sql', 'database'],
            'Excel': ['excel', 'spreadsheet'],
            'Marketing': ['marketing', 'advertising'],
            'Design': ['design', 'ui', 'ux'],
            'Java': ['java'],
            'React': ['react', 'reactjs'],
            'Node.js': ['node', 'nodejs'],
            'AWS': ['aws', 'amazon web services'],
            'Docker': ['docker', 'containerization'],
        }
        
        found_skills = []
        for skill, keywords in skill_keywords.items():
            if any(keyword in text for keyword in keywords):
                found_skills.append(skill)
        
        return found_skills

class AffiliateManager:
    """Manage affiliate links and tracking"""
    
    def __init__(self):
        self.affiliate_configs = self._load_affiliate_configs()
    
    def generate_affiliate_link(self, course, user=None) -> str:
        """Generate affiliate link for a course"""
        platform_name = course.platform.name.lower()
        
        if platform_name in self.affiliate_configs:
            config = self.affiliate_configs[platform_name]
            base_url = course.course_url
            
            # Add affiliate parameters
            if config.get('affiliate_id'):
                separator = '&' if '?' in base_url else '?'
                affiliate_param = config.get('param_name', 'affiliate_id')
                affiliate_link = f"{base_url}{separator}{affiliate_param}={config['affiliate_id']}"
                
                # Add tracking parameters if user provided
                if user:
                    affiliate_link += f"&user_id={user.id}&timestamp={int(timezone.now().timestamp())}"
                
                return affiliate_link
        
        return course.course_url
    
    def track_click(self, course, user, affiliate_link: str) -> bool:
        """Track affiliate link click"""
        from .models import AffiliateClick
        
        try:
            AffiliateClick.objects.create(
                course=course,
                user=user,
                affiliate_link=affiliate_link,
                clicked_at=timezone.now(),
                ip_address=self._get_user_ip(),  # Would get from request
                user_agent=self._get_user_agent()  # Would get from request
            )
            return True
        except Exception as e:
            logger.error(f"Error tracking affiliate click: {str(e)}")
            return False
    
    def _load_affiliate_configs(self) -> Dict[str, Dict]:
        """Load affiliate configurations"""
        return {
            'udemy': {
                'affiliate_id': getattr(settings, 'UDEMY_AFFILIATE_ID', ''),
                'param_name': 'couponCode',
                'commission_rate': 0.15
            },
            'coursera': {
                'affiliate_id': getattr(settings, 'COURSERA_AFFILIATE_ID', ''),
                'param_name': 'aid',
                'commission_rate': 0.10
            },
            'edx': {
                'affiliate_id': getattr(settings, 'EDX_AFFILIATE_ID', ''),
                'param_name': 'utm_source',
                'commission_rate': 0.08
            }
        }
    
    def _get_user_ip(self) -> str:
        """Get user IP address (placeholder)"""
        return "127.0.0.1"
    
    def _get_user_agent(self) -> str:
        """Get user agent (placeholder)"""
        return "Unknown"
