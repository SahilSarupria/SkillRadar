import openai
import json
from django.conf import settings
from typing import Dict, List, Any, Tuple
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

class SkillExtractor:
    """Extract skills from resume text and job descriptions"""
    
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
    
    def extract_skills_from_resume(self, resume_text: str) -> Dict[str, List[str]]:
        """Extract skills from resume text using AI"""
        
        system_prompt = """
        You are an expert at extracting skills from resumes. Analyze the provided resume text and extract skills categorized by type.
        
        Return a JSON object with the following structure:
        {
            "technical": ["Python", "JavaScript", "SQL", ...],
            "soft": ["Leadership", "Communication", "Problem Solving", ...],
            "tools": ["Git", "Docker", "AWS", "Photoshop", ...],
            "languages": ["English", "Spanish", "French", ...],
            "certifications": ["AWS Certified", "PMP", "Google Analytics", ...]
        }
        
        Guidelines:
        1. Extract only explicitly mentioned skills
        2. Normalize skill names (e.g., "Javascript" -> "JavaScript")
        3. Include programming languages, frameworks, tools, and methodologies
        4. Separate technical skills from soft skills
        5. Include certifications and languages if mentioned
        6. Avoid duplicates and be specific
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Extract skills from this resume:\n\n{resume_text}"}
                ],
                temperature=0.2,
                max_tokens=1000
            )
            
            result = response.choices[0].message.content
            return json.loads(result)
            
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing AI response for skill extraction: {str(e)}")
            return self._fallback_skill_extraction(resume_text)
        except Exception as e:
            logger.error(f"Error in AI skill extraction: {str(e)}")
            return self._fallback_skill_extraction(resume_text)
    
    def extract_skills_from_job_description(self, job_description: str, job_title: str = "") -> Dict[str, Any]:
        """Extract required skills from job description"""
        
        system_prompt = """
        You are an expert at analyzing job descriptions. Extract the required and preferred skills from the job description.
        
        Return a JSON object with the following structure:
        {
            "required_skills": [
                {"skill": "Python", "proficiency": "intermediate", "importance": "required"},
                {"skill": "Leadership", "proficiency": "advanced", "importance": "required"}
            ],
            "preferred_skills": [
                {"skill": "AWS", "proficiency": "beginner", "importance": "preferred"},
                {"skill": "Machine Learning", "proficiency": "intermediate", "importance": "nice_to_have"}
            ],
            "experience_requirements": {
                "min_years": 3,
                "max_years": 5,
                "level": "mid"
            },
            "education_requirements": ["Bachelor's degree", "Computer Science"],
            "certifications": ["AWS Certified", "PMP"]
        }
        
        Proficiency levels: beginner, intermediate, advanced, expert
        Importance levels: required, preferred, nice_to_have
        Experience levels: entry, mid, senior, lead, executive
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Job Title: {job_title}\n\nJob Description:\n{job_description}"}
                ],
                temperature=0.2,
                max_tokens=1500
            )
            
            result = response.choices[0].message.content
            return json.loads(result)
            
        except Exception as e:
            logger.error(f"Error extracting skills from job description: {str(e)}")
            return self._fallback_job_skill_extraction(job_description)
    
    def _fallback_skill_extraction(self, text: str) -> Dict[str, List[str]]:
        """Fallback skill extraction using keyword matching"""
        
        # Common technical skills
        technical_skills = [
            'Python', 'JavaScript', 'Java', 'C++', 'SQL', 'HTML', 'CSS', 'React',
            'Node.js', 'Django', 'Flask', 'Spring', 'Angular', 'Vue.js', 'PHP',
            'Ruby', 'Go', 'Rust', 'Swift', 'Kotlin', 'TypeScript', 'MongoDB',
            'PostgreSQL', 'MySQL', 'Redis', 'Docker', 'Kubernetes', 'AWS', 'Azure',
            'GCP', 'Git', 'Jenkins', 'Terraform', 'Ansible'
        ]
        
        # Common soft skills
        soft_skills = [
            'Leadership', 'Communication', 'Problem Solving', 'Teamwork',
            'Project Management', 'Time Management', 'Critical Thinking',
            'Adaptability', 'Creativity', 'Analytical Thinking'
        ]
        
        # Common tools
        tools = [
            'Photoshop', 'Illustrator', 'Figma', 'Sketch', 'InDesign',
            'Excel', 'PowerPoint', 'Tableau', 'Power BI', 'Salesforce',
            'Jira', 'Confluence', 'Slack', 'Trello', 'Asana'
        ]
        
        extracted_skills = {
            'technical': [],
            'soft': [],
            'tools': [],
            'languages': [],
            'certifications': []
        }
        
        text_lower = text.lower()
        
        # Extract technical skills
        for skill in technical_skills:
            if skill.lower() in text_lower:
                extracted_skills['technical'].append(skill)
        
        # Extract soft skills
        for skill in soft_skills:
            if skill.lower() in text_lower:
                extracted_skills['soft'].append(skill)
        
        # Extract tools
        for tool in tools:
            if tool.lower() in text_lower:
                extracted_skills['tools'].append(tool)
        
        return extracted_skills
    
    def _fallback_job_skill_extraction(self, job_description: str) -> Dict[str, Any]:
        """Fallback job skill extraction"""
        return {
            "required_skills": [],
            "preferred_skills": [],
            "experience_requirements": {"min_years": 0, "max_years": 10, "level": "mid"},
            "education_requirements": [],
            "certifications": []
        }

class SkillGapAnalyzer:
    """Analyze skill gaps between current skills and job requirements"""
    
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
    
    def analyze_skill_gaps(self, user_skills: List[Dict], job_requirements: Dict, target_job_title: str = "") -> Dict[str, Any]:
        """Comprehensive skill gap analysis"""
        
        # Convert user skills to a more manageable format
        user_skill_map = {}
        for user_skill in user_skills:
            skill_name = user_skill.get('skill_name', '').lower()
            user_skill_map[skill_name] = {
                'proficiency': user_skill.get('proficiency_level', 'beginner'),
                'experience_years': user_skill.get('years_of_experience', 0)
            }
        
        # Analyze required skills
        required_skills = job_requirements.get('required_skills', [])
        preferred_skills = job_requirements.get('preferred_skills', [])
        
        analysis_results = {
            'overall_match_score': 0.0,
            'skills_matched': 0,
            'skills_missing': 0,
            'skills_to_improve': 0,
            'skill_gaps': [],
            'strengths': [],
            'recommendations': [],
            'learning_path': []
        }
        
        # Analyze required skills
        total_required_weight = 0
        matched_weight = 0
        
        for req_skill in required_skills:
            skill_name = req_skill.get('skill', '').lower()
            required_proficiency = req_skill.get('proficiency', 'intermediate')
            importance = req_skill.get('importance', 'required')
            
            # Weight based on importance
            weight = {'required': 3, 'preferred': 2, 'nice_to_have': 1}.get(importance, 2)
            total_required_weight += weight
            
            if skill_name in user_skill_map:
                user_proficiency = user_skill_map[skill_name]['proficiency']
                proficiency_match = self._compare_proficiency_levels(user_proficiency, required_proficiency)
                
                if proficiency_match >= 0:  # User meets or exceeds requirement
                    matched_weight += weight
                    analysis_results['skills_matched'] += 1
                    
                    if proficiency_match > 0:  # User exceeds requirement
                        analysis_results['strengths'].append({
                            'skill': req_skill.get('skill', ''),
                            'user_level': user_proficiency,
                            'required_level': required_proficiency,
                            'advantage': proficiency_match
                        })
                else:  # User has skill but insufficient proficiency
                    analysis_results['skills_to_improve'] += 1
                    analysis_results['skill_gaps'].append({
                        'skill': req_skill.get('skill', ''),
                        'gap_type': 'insufficient',
                        'current_level': user_proficiency,
                        'required_level': required_proficiency,
                        'importance': importance,
                        'priority': self._calculate_priority(importance, proficiency_match),
                        'estimated_learning_time': self._estimate_learning_time(user_proficiency, required_proficiency)
                    })
            else:  # User doesn't have the skill
                analysis_results['skills_missing'] += 1
                analysis_results['skill_gaps'].append({
                    'skill': req_skill.get('skill', ''),
                    'gap_type': 'missing',
                    'current_level': None,
                    'required_level': required_proficiency,
                    'importance': importance,
                    'priority': self._calculate_priority(importance, -2),
                    'estimated_learning_time': self._estimate_learning_time(None, required_proficiency)
                })
        
        # Calculate overall match score
        if total_required_weight > 0:
            analysis_results['overall_match_score'] = (matched_weight / total_required_weight) * 100
        
        # Generate recommendations
        analysis_results['recommendations'] = self._generate_recommendations(analysis_results, target_job_title)
        
        # Generate learning path
        analysis_results['learning_path'] = self._generate_learning_path(analysis_results['skill_gaps'])
        
        return analysis_results
    
    def _compare_proficiency_levels(self, user_level: str, required_level: str) -> int:
        """Compare proficiency levels and return difference"""
        levels = {'beginner': 1, 'intermediate': 2, 'advanced': 3, 'expert': 4}
        
        user_score = levels.get(user_level.lower(), 0)
        required_score = levels.get(required_level.lower(), 2)
        
        return user_score - required_score
    
    def _calculate_priority(self, importance: str, proficiency_gap: int) -> str:
        """Calculate priority for addressing skill gap"""
        importance_weight = {'required': 3, 'preferred': 2, 'nice_to_have': 1}.get(importance, 2)
        gap_weight = abs(proficiency_gap)
        
        total_score = importance_weight + gap_weight
        
        if total_score >= 5:
            return 'critical'
        elif total_score >= 4:
            return 'high'
        elif total_score >= 2:
            return 'medium'
        else:
            return 'low'
    
    def _estimate_learning_time(self, current_level: str, target_level: str) -> int:
        """Estimate learning time in hours"""
        if current_level is None:
            current_level = 'none'
        
        # Base learning times (hours)
        learning_matrix = {
            ('none', 'beginner'): 40,
            ('none', 'intermediate'): 80,
            ('none', 'advanced'): 160,
            ('none', 'expert'): 320,
            ('beginner', 'intermediate'): 40,
            ('beginner', 'advanced'): 120,
            ('beginner', 'expert'): 280,
            ('intermediate', 'advanced'): 80,
            ('intermediate', 'expert'): 240,
            ('advanced', 'expert'): 160,
        }
        
        return learning_matrix.get((current_level.lower(), target_level.lower()), 40)
    
    def _generate_recommendations(self, analysis_results: Dict, target_job_title: str) -> List[str]:
        """Generate personalized recommendations"""
        recommendations = []
        
        # Priority-based recommendations
        critical_gaps = [gap for gap in analysis_results['skill_gaps'] if gap['priority'] == 'critical']
        high_priority_gaps = [gap for gap in analysis_results['skill_gaps'] if gap['priority'] == 'high']
        
        if critical_gaps:
            recommendations.append(f"Focus immediately on critical skills: {', '.join([gap['skill'] for gap in critical_gaps[:3]])}")
        
        if high_priority_gaps:
            recommendations.append(f"Prioritize learning: {', '.join([gap['skill'] for gap in high_priority_gaps[:3]])}")
        
        # Match score based recommendations
        if analysis_results['overall_match_score'] < 50:
            recommendations.append("Consider gaining more experience in this field before applying")
        elif analysis_results['overall_match_score'] < 70:
            recommendations.append("Focus on closing key skill gaps to improve your candidacy")
        else:
            recommendations.append("You're well-qualified! Consider highlighting your strengths")
        
        # Strengths-based recommendations
        if analysis_results['strengths']:
            top_strengths = [s['skill'] for s in analysis_results['strengths'][:2]]
            recommendations.append(f"Emphasize your strong skills in your application: {', '.join(top_strengths)}")
        
        return recommendations
    
    def _generate_learning_path(self, skill_gaps: List[Dict]) -> List[Dict]:
        """Generate a structured learning path"""
        # Sort gaps by priority and estimated learning time
        sorted_gaps = sorted(skill_gaps, key=lambda x: (
            {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}[x['priority']],
            -x['estimated_learning_time']
        ), reverse=True)
        
        learning_path = []
        total_time = 0
        
        for i, gap in enumerate(sorted_gaps[:8]):  # Limit to top 8 skills
            step = {
                'order': i + 1,
                'skill': gap['skill'],
                'target_level': gap['required_level'],
                'estimated_hours': gap['estimated_learning_time'],
                'priority': gap['priority'],
                'resources': self._get_learning_resources(gap['skill'], gap['required_level'])
            }
            
            total_time += gap['estimated_learning_time']
            learning_path.append(step)
        
        return learning_path
    
    def _get_learning_resources(self, skill: str, level: str) -> List[Dict]:
        """Get learning resources for a specific skill"""
        # This would typically query a database of learning resources
        # For now, return generic resource types
        resources = [
            {
                'type': 'online_course',
                'title': f'{skill} for {level.title()} Level',
                'provider': 'Various Platforms',
                'estimated_hours': 20,
                'cost': 'Free - $200'
            },
            {
                'type': 'documentation',
                'title': f'Official {skill} Documentation',
                'provider': 'Official',
                'estimated_hours': 10,
                'cost': 'Free'
            },
            {
                'type': 'practice_project',
                'title': f'Build a {skill} Project',
                'provider': 'Self-directed',
                'estimated_hours': 30,
                'cost': 'Free'
            }
        ]
        
        return resources

class SkillMatcher:
    """Match skills between different formats and sources"""
    
    def __init__(self):
        self.skill_aliases = self._load_skill_aliases()
    
    def normalize_skill_name(self, skill_name: str) -> str:
        """Normalize skill name to standard format"""
        skill_lower = skill_name.lower().strip()
        
        # Check aliases
        for standard_name, aliases in self.skill_aliases.items():
            if skill_lower in [alias.lower() for alias in aliases]:
                return standard_name
        
        # Return title case if no alias found
        return skill_name.title()
    
    def find_similar_skills(self, skill_name: str, skill_list: List[str], threshold: float = 0.8) -> List[str]:
        """Find similar skills using fuzzy matching"""
        from difflib import SequenceMatcher
        
        similar_skills = []
        skill_lower = skill_name.lower()
        
        for skill in skill_list:
            similarity = SequenceMatcher(None, skill_lower, skill.lower()).ratio()
            if similarity >= threshold:
                similar_skills.append(skill)
        
        return similar_skills
    
    def _load_skill_aliases(self) -> Dict[str, List[str]]:
        """Load skill aliases mapping"""
        return {
            'JavaScript': ['js', 'javascript', 'ecmascript', 'node.js', 'nodejs'],
            'Python': ['python', 'python3', 'py'],
            'Machine Learning': ['ml', 'machine learning', 'artificial intelligence', 'ai'],
            'Project Management': ['pm', 'project management', 'project manager'],
            'User Experience': ['ux', 'user experience', 'ux design'],
            'User Interface': ['ui', 'user interface', 'ui design'],
            'Search Engine Optimization': ['seo', 'search engine optimization'],
            'Customer Relationship Management': ['crm', 'customer relationship management'],
            'Application Programming Interface': ['api', 'apis', 'rest api', 'restful api'],
            'Database': ['db', 'databases', 'database management'],
            'Cloud Computing': ['cloud', 'cloud computing', 'cloud services'],
        }

class LearningPathGenerator:
    """Generate personalized learning paths"""
    
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
    
    def generate_learning_path(self, skill_gaps: List[Dict], user_profile: Dict, target_timeline_weeks: int = 12) -> Dict[str, Any]:
        """Generate a comprehensive learning path"""
        
        # Prioritize skills based on importance and user goals
        prioritized_skills = self._prioritize_skills(skill_gaps, user_profile)
        
        # Create learning phases
        learning_phases = self._create_learning_phases(prioritized_skills, target_timeline_weeks)
        
        # Generate detailed steps for each phase
        detailed_path = []
        for phase in learning_phases:
            phase_details = self._generate_phase_details(phase, user_profile)
            detailed_path.append(phase_details)
        
        return {
            'total_duration_weeks': target_timeline_weeks,
            'total_skills': len(prioritized_skills),
            'phases': detailed_path,
            'milestones': self._generate_milestones(detailed_path),
            'success_metrics': self._generate_success_metrics(prioritized_skills)
        }
    
    def _prioritize_skills(self, skill_gaps: List[Dict], user_profile: Dict) -> List[Dict]:
        """Prioritize skills based on various factors"""
        # Add scoring based on user's career goals, current level, market demand, etc.
        for skill_gap in skill_gaps:
            score = 0
            
            # Priority weight
            priority_weights = {'critical': 10, 'high': 7, 'medium': 4, 'low': 1}
            score += priority_weights.get(skill_gap.get('priority', 'medium'), 4)
            
            # Learning time consideration (shorter learning time = higher priority for quick wins)
            learning_time = skill_gap.get('estimated_learning_time', 40)
            if learning_time <= 20:
                score += 3
            elif learning_time <= 40:
                score += 2
            elif learning_time <= 80:
                score += 1
            
            skill_gap['priority_score'] = score
        
        return sorted(skill_gaps, key=lambda x: x['priority_score'], reverse=True)
    
    def _create_learning_phases(self, prioritized_skills: List[Dict], total_weeks: int) -> List[Dict]:
        """Create learning phases"""
        phases = []
        
        # Phase 1: Foundation (weeks 1-4) - Critical and high priority skills
        foundation_skills = [s for s in prioritized_skills if s.get('priority') in ['critical', 'high']][:3]
        if foundation_skills:
            phases.append({
                'phase': 1,
                'title': 'Foundation Phase',
                'weeks': '1-4',
                'duration_weeks': 4,
                'skills': foundation_skills,
                'focus': 'Build critical foundational skills'
            })
        
        # Phase 2: Development (weeks 5-8) - Medium priority and remaining high priority
        development_skills = [s for s in prioritized_skills if s.get('priority') in ['medium', 'high']][3:6]
        if development_skills:
            phases.append({
                'phase': 2,
                'title': 'Development Phase',
                'weeks': '5-8',
                'duration_weeks': 4,
                'skills': development_skills,
                'focus': 'Develop intermediate skills and deepen knowledge'
            })
        
        # Phase 3: Specialization (weeks 9-12) - Remaining skills and advanced topics
        specialization_skills = prioritized_skills[6:9]
        if specialization_skills:
            phases.append({
                'phase': 3,
                'title': 'Specialization Phase',
                'weeks': '9-12',
                'duration_weeks': 4,
                'skills': specialization_skills,
                'focus': 'Specialize and apply skills in real projects'
            })
        
        return phases
    
    def _generate_phase_details(self, phase: Dict, user_profile: Dict) -> Dict[str, Any]:
        """Generate detailed steps for a learning phase"""
        phase_details = phase.copy()
        phase_details['steps'] = []
        
        for i, skill in enumerate(phase['skills']):
            step = {
                'step_number': i + 1,
                'skill': skill['skill'],
                'target_level': skill['required_level'],
                'estimated_hours': skill['estimated_learning_time'],
                'learning_objectives': self._generate_learning_objectives(skill),
                'resources': self._generate_learning_resources(skill),
                'assessment_criteria': self._generate_assessment_criteria(skill),
                'practical_exercises': self._generate_practical_exercises(skill)
            }
            phase_details['steps'].append(step)
        
        return phase_details
    
    def _generate_learning_objectives(self, skill: Dict) -> List[str]:
        """Generate learning objectives for a skill"""
        skill_name = skill['skill']
        target_level = skill['required_level']
        
        # This would be more sophisticated in practice
        objectives = [
            f"Understand the fundamentals of {skill_name}",
            f"Apply {skill_name} concepts in practical scenarios",
            f"Demonstrate {target_level} proficiency in {skill_name}",
            f"Complete hands-on projects using {skill_name}"
        ]
        
        return objectives
    
    def _generate_learning_resources(self, skill: Dict) -> List[Dict]:
        """Generate learning resources for a skill"""
        # This would query a comprehensive resource database
        return [
            {
                'type': 'online_course',
                'title': f"Complete {skill['skill']} Course",
                'provider': 'Coursera/Udemy',
                'duration_hours': 20,
                'cost': '$50-200',
                'difficulty': skill['required_level']
            },
            {
                'type': 'documentation',
                'title': f"Official {skill['skill']} Documentation",
                'provider': 'Official',
                'duration_hours': 5,
                'cost': 'Free',
                'difficulty': 'all_levels'
            },
            {
                'type': 'tutorial',
                'title': f"{skill['skill']} Tutorial Series",
                'provider': 'YouTube/FreeCodeCamp',
                'duration_hours': 10,
                'cost': 'Free',
                'difficulty': skill['required_level']
            }
        ]
    
    def _generate_assessment_criteria(self, skill: Dict) -> List[str]:
        """Generate assessment criteria for a skill"""
        return [
            f"Complete a {skill['skill']} project demonstrating core concepts",
            f"Pass a {skill['skill']} knowledge assessment with 80% score",
            f"Explain {skill['skill']} concepts clearly to others",
            f"Apply {skill['skill']} to solve real-world problems"
        ]
    
    def _generate_practical_exercises(self, skill: Dict) -> List[Dict]:
        """Generate practical exercises for a skill"""
        return [
            {
                'title': f"Build a {skill['skill']} Project",
                'description': f"Create a practical project using {skill['skill']}",
                'estimated_hours': 15,
                'difficulty': skill['required_level']
            },
            {
                'title': f"{skill['skill']} Code Challenges",
                'description': f"Complete coding challenges focused on {skill['skill']}",
                'estimated_hours': 5,
                'difficulty': skill['required_level']
            }
        ]
    
    def _generate_milestones(self, detailed_path: List[Dict]) -> List[Dict]:
        """Generate learning milestones"""
        milestones = []
        
        for phase in detailed_path:
            milestone = {
                'phase': phase['phase'],
                'title': f"Complete {phase['title']}",
                'week': phase['weeks'].split('-')[1],
                'criteria': [
                    f"Complete all {len(phase['steps'])} skills in this phase",
                    f"Pass phase assessment with 75% or higher",
                    f"Complete at least one practical project"
                ]
            }
            milestones.append(milestone)
        
        return milestones
    
    def _generate_success_metrics(self, prioritized_skills: List[Dict]) -> Dict[str, Any]:
        """Generate success metrics for the learning path"""
        return {
            'completion_rate': 'Complete 80% of planned learning activities',
            'skill_proficiency': 'Achieve target proficiency level for 75% of skills',
            'practical_application': 'Complete at least 3 hands-on projects',
            'assessment_scores': 'Maintain average assessment score of 75% or higher',
            'time_management': f'Complete learning path within {12} weeks'
        }
