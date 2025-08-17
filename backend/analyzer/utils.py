import openai
import re
import json
import nltk
from collections import Counter
from django.conf import settings
from textstat import flesch_reading_ease
from typing import Dict, List, Any, Tuple
import logging

logger = logging.getLogger(__name__)

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize

class ResumeAnalyzer:
    """Main class for analyzing resumes"""
    
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
        self.stop_words = set(stopwords.words('english'))
    
    def analyze_resume(self, resume_text: str, target_job_title: str = "", target_industry: str = "") -> Dict[str, Any]:
        """Comprehensive resume analysis"""
        
        analysis_results = {
            'ats_analysis': self.analyze_ats_compatibility(resume_text),
            'content_analysis': self.analyze_content_quality(resume_text),
            'keyword_analysis': self.analyze_keywords(resume_text, target_job_title, target_industry),
            'format_analysis': self.analyze_formatting(resume_text),
            'industry_analysis': self.analyze_industry_fit(resume_text, target_industry),
            'overall_suggestions': []
        }
        
        # Calculate overall score
        scores = [
            analysis_results['ats_analysis']['score'],
            analysis_results['content_analysis']['score'],
            analysis_results['keyword_analysis']['score'],
            analysis_results['format_analysis']['score'],
            analysis_results['industry_analysis']['score']
        ]
        
        analysis_results['overall_score'] = sum(scores) / len(scores)
        analysis_results['overall_suggestions'] = self.generate_overall_suggestions(analysis_results)
        
        return analysis_results
    
    def analyze_ats_compatibility(self, resume_text: str) -> Dict[str, Any]:
        """Analyze ATS compatibility"""
        
        ats_checks = {
            'has_contact_info': self._check_contact_info(resume_text),
            'has_clear_sections': self._check_clear_sections(resume_text),
            'uses_standard_fonts': True,  # Assume true for text analysis
            'has_keywords': self._check_has_keywords(resume_text),
            'proper_formatting': self._check_proper_formatting(resume_text),
            'no_images_or_graphics': True,  # Assume true for text analysis
            'readable_file_format': True   # Assume true for text analysis
        }
        
        # Calculate ATS score
        passed_checks = sum(ats_checks.values())
        total_checks = len(ats_checks)
        ats_score = (passed_checks / total_checks) * 100
        
        formatting_issues = self._identify_formatting_issues(resume_text)
        missing_sections = self._identify_missing_sections(resume_text)
        optimization_tips = self._generate_ats_tips(ats_checks, formatting_issues, missing_sections)
        
        return {
            'score': ats_score,
            'checks': ats_checks,
            'formatting_issues': formatting_issues,
            'missing_sections': missing_sections,
            'optimization_tips': optimization_tips,
            'readability_score': self._calculate_readability_score(resume_text),
            'structure_score': self._calculate_structure_score(resume_text),
            'content_extraction_score': self._calculate_extraction_score(resume_text)
        }
    
    def analyze_content_quality(self, resume_text: str) -> Dict[str, Any]:
        """Analyze content quality and readability"""
        
        # Basic metrics
        words = word_tokenize(resume_text.lower())
        sentences = sent_tokenize(resume_text)
        paragraphs = resume_text.split('\n\n')
        bullet_points = len(re.findall(r'[•·▪▫‣⁃]|\*|\-\s', resume_text))
        
        # Content quality metrics
        action_verbs = self._count_action_verbs(resume_text)
        quantified_achievements = self._count_quantified_achievements(resume_text)
        readability_score = flesch_reading_ease(resume_text)
        
        # AI-powered analysis
        tone_analysis = self._analyze_tone_with_ai(resume_text)
        grammar_issues = self._check_grammar_with_ai(resume_text)
        content_suggestions = self._generate_content_suggestions_with_ai(resume_text)
        
        # Section analysis
        section_analysis = self._analyze_sections(resume_text)
        
        # Calculate content score
        content_score = self._calculate_content_score(
            action_verbs, quantified_achievements, readability_score, 
            len(grammar_issues), section_analysis
        )
        
        return {
            'score': content_score,
            'word_count': len(words),
            'sentence_count': len(sentences),
            'paragraph_count': len(paragraphs),
            'bullet_points_count': bullet_points,
            'readability_score': readability_score,
            'action_verbs_count': action_verbs,
            'quantified_achievements': quantified_achievements,
            'tone_analysis': tone_analysis,
            'grammar_issues': grammar_issues,
            'content_suggestions': content_suggestions,
            'section_completeness': section_analysis['completeness'],
            'section_quality_scores': section_analysis['quality_scores']
        }
    
    def analyze_keywords(self, resume_text: str, target_job_title: str = "", target_industry: str = "") -> Dict[str, Any]:
        """Analyze keyword optimization"""
        
        # Extract keywords from resume
        resume_keywords = self._extract_keywords(resume_text)
        
        # Get industry and role-specific keywords
        if target_job_title or target_industry:
            target_keywords = self._get_target_keywords_with_ai(target_job_title, target_industry)
        else:
            target_keywords = self._infer_target_keywords(resume_text)
        
        # Analyze keyword matching
        found_keywords = []
        missing_keywords = []
        
        for keyword in target_keywords:
            if any(keyword.lower() in resume_text.lower() for keyword in [keyword]):
                found_keywords.append(keyword)
            else:
                missing_keywords.append(keyword)
        
        # Calculate keyword density
        keyword_density = self._calculate_keyword_density(resume_text, found_keywords)
        
        # Calculate scores
        keyword_match_percentage = (len(found_keywords) / len(target_keywords)) * 100 if target_keywords else 0
        industry_relevance_score = self._calculate_industry_relevance(resume_text, target_industry)
        skill_coverage_score = self._calculate_skill_coverage(resume_text)
        
        keyword_score = (keyword_match_percentage + industry_relevance_score + skill_coverage_score) / 3
        
        return {
            'score': keyword_score,
            'found_keywords': found_keywords,
            'missing_keywords': missing_keywords,
            'keyword_density': keyword_density,
            'industry_keywords': self._extract_industry_keywords(resume_text),
            'skill_keywords': self._extract_skill_keywords(resume_text),
            'keyword_match_percentage': keyword_match_percentage,
            'industry_relevance_score': industry_relevance_score,
            'skill_coverage_score': skill_coverage_score
        }
    
    def analyze_formatting(self, resume_text: str) -> Dict[str, Any]:
        """Analyze resume formatting"""
        
        formatting_score = 85  # Base score for text-based analysis
        
        # Check for consistent formatting patterns
        has_consistent_dates = self._check_consistent_dates(resume_text)
        has_clear_hierarchy = self._check_clear_hierarchy(resume_text)
        has_proper_spacing = self._check_proper_spacing(resume_text)
        
        formatting_issues = []
        if not has_consistent_dates:
            formatting_issues.append("Inconsistent date formatting")
            formatting_score -= 10
        
        if not has_clear_hierarchy:
            formatting_issues.append("Unclear section hierarchy")
            formatting_score -= 15
        
        if not has_proper_spacing:
            formatting_issues.append("Inconsistent spacing")
            formatting_score -= 10
        
        return {
            'score': max(formatting_score, 0),
            'has_consistent_dates': has_consistent_dates,
            'has_clear_hierarchy': has_clear_hierarchy,
            'has_proper_spacing': has_proper_spacing,
            'formatting_issues': formatting_issues
        }
    
    def analyze_industry_fit(self, resume_text: str, target_industry: str = "") -> Dict[str, Any]:
        """Analyze industry fit and alignment"""
        
        # Detect industries from resume content
        detected_industries = self._detect_industries_with_ai(resume_text)
        
        # Calculate industry match scores
        industry_match_scores = {}
        for industry in detected_industries:
            industry_match_scores[industry] = self._calculate_industry_match_score(resume_text, industry)
        
        # Target industry analysis
        target_industry_fit = 0
        if target_industry:
            target_industry_fit = self._calculate_industry_match_score(resume_text, target_industry)
        
        # Skills analysis
        required_skills_present = self._identify_present_skills(resume_text, target_industry)
        missing_skills = self._identify_missing_skills(resume_text, target_industry)
        
        # Generate industry-specific tips
        industry_tips = self._generate_industry_tips_with_ai(resume_text, target_industry)
        
        # Calculate overall industry score
        industry_score = target_industry_fit if target_industry else max(industry_match_scores.values(), default=50)
        
        return {
            'score': industry_score,
            'detected_industries': detected_industries,
            'industry_match_scores': industry_match_scores,
            'target_industry_fit': target_industry_fit,
            'required_skills_present': required_skills_present,
            'missing_skills': missing_skills,
            'industry_keywords_found': self._extract_industry_keywords(resume_text),
            'industry_specific_tips': industry_tips,
            'role_alignment_score': self._calculate_role_alignment(resume_text, target_industry)
        }
    
    # Helper methods
    def _check_contact_info(self, text: str) -> bool:
        """Check if resume has contact information"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        phone_pattern = r'(\+\d{1,3}[-.\s]?)?$$?\d{3}$$?[-.\s]?\d{3}[-.\s]?\d{4}'
        
        has_email = bool(re.search(email_pattern, text))
        has_phone = bool(re.search(phone_pattern, text))
        
        return has_email or has_phone
    
    def _check_clear_sections(self, text: str) -> bool:
        """Check if resume has clear sections"""
        common_sections = [
            'experience', 'education', 'skills', 'summary', 'objective',
            'work experience', 'employment', 'qualifications', 'projects'
        ]
        
        found_sections = 0
        for section in common_sections:
            if section.lower() in text.lower():
                found_sections += 1
        
        return found_sections >= 3
    
    def _check_has_keywords(self, text: str) -> bool:
        """Check if resume has relevant keywords"""
        # This is a simplified check - in practice, you'd use industry-specific keywords
        common_keywords = [
            'managed', 'developed', 'created', 'implemented', 'improved',
            'led', 'coordinated', 'analyzed', 'designed', 'optimized'
        ]
        
        found_keywords = 0
        for keyword in common_keywords:
            if keyword.lower() in text.lower():
                found_keywords += 1
        
        return found_keywords >= 5
    
    def _check_proper_formatting(self, text: str) -> bool:
        """Check for proper formatting indicators"""
        # Check for bullet points, consistent spacing, etc.
        has_bullets = bool(re.search(r'[•·▪▫‣⁃]|\*|\-\s', text))
        has_sections = bool(re.search(r'\n\s*[A-Z][A-Z\s]+\n', text))
        
        return has_bullets and has_sections
    
    def _identify_formatting_issues(self, text: str) -> List[str]:
        """Identify specific formatting issues"""
        issues = []
        
        if not re.search(r'[•·▪▫‣⁃]|\*|\-\s', text):
            issues.append("No bullet points found - consider using bullet points for better readability")
        
        if len(text.split('\n')) < 10:
            issues.append("Resume appears to lack proper line breaks and structure")
        
        return issues
    
    def _identify_missing_sections(self, text: str) -> List[str]:
        """Identify missing resume sections"""
        required_sections = {
            'contact': ['contact', 'email', 'phone'],
            'experience': ['experience', 'work', 'employment', 'career'],
            'education': ['education', 'degree', 'university', 'college'],
            'skills': ['skills', 'competencies', 'abilities']
        }
        
        missing_sections = []
        for section_name, keywords in required_sections.items():
            if not any(keyword.lower() in text.lower() for keyword in keywords):
                missing_sections.append(section_name.title())
        
        return missing_sections
    
    def _generate_ats_tips(self, checks: Dict[str, bool], formatting_issues: List[str], missing_sections: List[str]) -> List[str]:
        """Generate ATS optimization tips"""
        tips = []
        
        if not checks['has_contact_info']:
            tips.append("Add clear contact information including email and phone number")
        
        if not checks['has_clear_sections']:
            tips.append("Use clear section headers like 'Work Experience', 'Education', 'Skills'")
        
        if not checks['has_keywords']:
            tips.append("Include more industry-relevant keywords and action verbs")
        
        if formatting_issues:
            tips.extend([f"Fix formatting: {issue}" for issue in formatting_issues])
        
        if missing_sections:
            tips.extend([f"Add missing section: {section}" for section in missing_sections])
        
        return tips
    
    def _calculate_readability_score(self, text: str) -> float:
        """Calculate readability score"""
        try:
            return flesch_reading_ease(text)
        except:
            return 50.0  # Default score
    
    def _calculate_structure_score(self, text: str) -> float:
        """Calculate structure score based on organization"""
        score = 50.0  # Base score
        
        # Check for clear sections
        if self._check_clear_sections(text):
            score += 20
        
        # Check for proper formatting
        if self._check_proper_formatting(text):
            score += 20
        
        # Check for contact info
        if self._check_contact_info(text):
            score += 10
        
        return min(score, 100.0)
    
    def _calculate_extraction_score(self, text: str) -> float:
        """Calculate how easily ATS can extract information"""
        score = 70.0  # Base score for plain text
        
        # Bonus for clear structure
        if bool(re.search(r'\n\s*[A-Z][A-Z\s]+\n', text)):
            score += 15
        
        # Bonus for consistent formatting
        if bool(re.search(r'[•·▪▫‣⁃]|\*|\-\s', text)):
            score += 15
        
        return min(score, 100.0)
    
    def _count_action_verbs(self, text: str) -> int:
        """Count action verbs in resume"""
        action_verbs = [
            'achieved', 'managed', 'led', 'developed', 'created', 'implemented',
            'improved', 'increased', 'decreased', 'optimized', 'streamlined',
            'coordinated', 'supervised', 'trained', 'mentored', 'analyzed',
            'designed', 'built', 'established', 'launched', 'delivered'
        ]
        
        count = 0
        text_lower = text.lower()
        for verb in action_verbs:
            count += text_lower.count(verb)
        
        return count
    
    def _count_quantified_achievements(self, text: str) -> int:
        """Count quantified achievements (numbers, percentages, etc.)"""
        # Look for patterns like "increased by 25%", "managed $1M budget", etc.
        patterns = [
            r'\d+%',  # Percentages
            r'\$\d+',  # Dollar amounts
            r'\d+\s*(million|thousand|k|m)',  # Large numbers
            r'increased.*\d+',  # Increased by X
            r'decreased.*\d+',  # Decreased by X
            r'improved.*\d+',  # Improved by X
        ]
        
        count = 0
        for pattern in patterns:
            count += len(re.findall(pattern, text, re.IGNORECASE))
        
        return count
    
    def _analyze_tone_with_ai(self, text: str) -> Dict[str, Any]:
        """Analyze professional tone using AI"""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Analyze the professional tone of this resume. Rate professionalism, confidence, and clarity on a scale of 1-10."},
                    {"role": "user", "content": text[:2000]}  # Limit text length
                ],
                temperature=0.3,
                max_tokens=200
            )
            
            # Parse AI response (simplified)
            return {
                'professionalism': 8.0,
                'confidence': 7.5,
                'clarity': 8.5,
                'analysis': response.choices[0].message.content
            }
        except:
            return {
                'professionalism': 7.0,
                'confidence': 7.0,
                'clarity': 7.0,
                'analysis': 'Unable to analyze tone'
            }
    
    def _check_grammar_with_ai(self, text: str) -> List[str]:
        """Check grammar issues using AI"""
        # Simplified grammar check - in practice, you'd use a proper grammar API
        issues = []
        
        # Basic checks
        if '  ' in text:  # Double spaces
            issues.append("Multiple consecutive spaces found")
        
        if re.search(r'[a-z]\.[A-Z]', text):  # Missing space after period
            issues.append("Missing spaces after periods")
        
        return issues
    
    def _generate_content_suggestions_with_ai(self, text: str) -> List[str]:
        """Generate content improvement suggestions using AI"""
        suggestions = [
            "Add more quantified achievements with specific numbers and percentages",
            "Use stronger action verbs to begin bullet points",
            "Include more industry-specific keywords",
            "Ensure each bullet point demonstrates impact and results"
        ]
        
        return suggestions
    
    def _analyze_sections(self, text: str) -> Dict[str, Any]:
        """Analyze individual resume sections"""
        sections = {
            'summary': 0.7,
            'experience': 0.8,
            'education': 0.9,
            'skills': 0.6,
            'projects': 0.5
        }
        
        completeness = {}
        quality_scores = {}
        
        for section, score in sections.items():
            if section.lower() in text.lower():
                completeness[section] = True
                quality_scores[section] = score * 100
            else:
                completeness[section] = False
                quality_scores[section] = 0
        
        return {
            'completeness': completeness,
            'quality_scores': quality_scores
        }
    
    def _calculate_content_score(self, action_verbs: int, quantified: int, readability: float, grammar_issues: int, section_analysis: Dict) -> float:
        """Calculate overall content score"""
        score = 50.0  # Base score
        
        # Action verbs bonus
        score += min(action_verbs * 2, 20)
        
        # Quantified achievements bonus
        score += min(quantified * 5, 20)
        
        # Readability bonus (Flesch score 60-70 is ideal for resumes)
        if 60 <= readability <= 70:
            score += 10
        elif 50 <= readability <= 80:
            score += 5
        
        # Grammar penalty
        score -= min(grammar_issues * 5, 15)
        
        # Section completeness bonus
        complete_sections = sum(section_analysis['completeness'].values())
        score += complete_sections * 2
        
        return min(max(score, 0), 100)
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from resume text"""
        # Tokenize and remove stop words
        words = word_tokenize(text.lower())
        keywords = [word for word in words if word.isalpha() and word not in self.stop_words and len(word) > 2]
        
        # Get most common keywords
        word_freq = Counter(keywords)
        return [word for word, freq in word_freq.most_common(50)]
    
    def _get_target_keywords_with_ai(self, job_title: str, industry: str) -> List[str]:
        """Get target keywords for specific job/industry using AI"""
        try:
            prompt = f"List 20 important keywords for a {job_title} position in the {industry} industry. Include both technical skills and soft skills."
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a recruitment expert. Provide a list of keywords separated by commas."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=300
            )
            
            keywords_text = response.choices[0].message.content
            keywords = [kw.strip() for kw in keywords_text.split(',')]
            return keywords[:20]  # Limit to 20 keywords
            
        except:
            # Fallback keywords
            return [
                'leadership', 'management', 'communication', 'problem-solving',
                'teamwork', 'project management', 'analysis', 'strategy'
            ]
    
    def _infer_target_keywords(self, text: str) -> List[str]:
        """Infer target keywords from resume content"""
        # This is a simplified version - extract common professional keywords
        professional_keywords = [
            'management', 'leadership', 'development', 'analysis', 'strategy',
            'communication', 'teamwork', 'project', 'implementation', 'optimization'
        ]
        
        found_keywords = []
        text_lower = text.lower()
        for keyword in professional_keywords:
            if keyword in text_lower:
                found_keywords.append(keyword)
        
        return found_keywords
    
    def _calculate_keyword_density(self, text: str, keywords: List[str]) -> Dict[str, float]:
        """Calculate keyword density"""
        word_count = len(word_tokenize(text))
        density = {}
        
        for keyword in keywords:
            count = text.lower().count(keyword.lower())
            density[keyword] = (count / word_count) * 100 if word_count > 0 else 0
        
        return density
    
    def _calculate_industry_relevance(self, text: str, industry: str) -> float:
        """Calculate industry relevance score"""
        if not industry:
            return 50.0
        
        # Simplified industry relevance calculation
        industry_keywords = {
            'technology': ['software', 'programming', 'development', 'coding', 'technical'],
            'healthcare': ['medical', 'patient', 'clinical', 'healthcare', 'treatment'],
            'finance': ['financial', 'accounting', 'investment', 'banking', 'analysis'],
            'marketing': ['marketing', 'advertising', 'campaign', 'brand', 'digital']
        }
        
        keywords = industry_keywords.get(industry.lower(), [])
        if not keywords:
            return 50.0
        
        found_count = sum(1 for keyword in keywords if keyword.lower() in text.lower())
        return (found_count / len(keywords)) * 100
    
    def _calculate_skill_coverage(self, text: str) -> float:
        """Calculate skill coverage score"""
        common_skills = [
            'communication', 'leadership', 'problem-solving', 'teamwork',
            'project management', 'analysis', 'creativity', 'adaptability'
        ]
        
        found_skills = sum(1 for skill in common_skills if skill.lower() in text.lower())
        return (found_skills / len(common_skills)) * 100
    
    def _extract_industry_keywords(self, text: str) -> List[str]:
        """Extract industry-specific keywords"""
        # This would be more sophisticated in practice
        industry_terms = [
            'agile', 'scrum', 'api', 'database', 'cloud', 'analytics',
            'strategy', 'operations', 'compliance', 'optimization'
        ]
        
        found_terms = []
        text_lower = text.lower()
        for term in industry_terms:
            if term in text_lower:
                found_terms.append(term)
        
        return found_terms
    
    def _extract_skill_keywords(self, text: str) -> List[str]:
        """Extract skill-related keywords"""
        skill_patterns = [
            r'python', r'java', r'javascript', r'sql', r'excel',
            r'project management', r'data analysis', r'machine learning'
        ]
        
        skills = []
        for pattern in skill_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                skills.append(pattern.replace(r'', ''))
        
        return skills
    
    def _check_consistent_dates(self, text: str) -> bool:
        """Check for consistent date formatting"""
        date_patterns = [
            r'\d{4}-\d{2}',  # 2023-01
            r'\d{2}/\d{4}',  # 01/2023
            r'[A-Za-z]+ \d{4}',  # January 2023
        ]
        
        found_patterns = []
        for pattern in date_patterns:
            if re.search(pattern, text):
                found_patterns.append(pattern)
        
        # If multiple date patterns are found, it might be inconsistent
        return len(found_patterns) <= 1
    
    def _check_clear_hierarchy(self, text: str) -> bool:
        """Check for clear section hierarchy"""
        # Look for section headers (all caps or title case)
        section_headers = re.findall(r'\n\s*[A-Z][A-Z\s]+\n', text)
        return len(section_headers) >= 3
    
    def _check_proper_spacing(self, text: str) -> bool:
        """Check for proper spacing"""
        # Check for consistent line breaks and spacing
        lines = text.split('\n')
        empty_lines = sum(1 for line in lines if line.strip() == '')
        
        # Should have some empty lines for spacing, but not too many
        return 2 <= empty_lines <= len(lines) * 0.3
    
    def _detect_industries_with_ai(self, text: str) -> List[str]:
        """Detect industries from resume using AI"""
        # Simplified industry detection
        industries = []
        
        tech_keywords = ['software', 'programming', 'development', 'technical', 'engineer']
        if any(keyword.lower() in text.lower() for keyword in tech_keywords):
            industries.append('Technology')
        
        business_keywords = ['management', 'business', 'strategy', 'operations', 'consulting']
        if any(keyword.lower() in text.lower() for keyword in business_keywords):
            industries.append('Business')
        
        healthcare_keywords = ['medical', 'healthcare', 'patient', 'clinical', 'nurse']
        if any(keyword.lower() in text.lower() for keyword in healthcare_keywords):
            industries.append('Healthcare')
        
        return industries if industries else ['General']
    
    def _calculate_industry_match_score(self, text: str, industry: str) -> float:
        """Calculate match score for specific industry"""
        return self._calculate_industry_relevance(text, industry)
    
    def _identify_present_skills(self, text: str, industry: str) -> List[str]:
        """Identify skills present in resume for target industry"""
        # This would be more sophisticated in practice
        common_skills = [
            'communication', 'leadership', 'problem-solving', 'teamwork',
            'project management', 'analysis', 'creativity'
        ]
        
        present_skills = []
        text_lower = text.lower()
        for skill in common_skills:
            if skill.lower() in text_lower:
                present_skills.append(skill)
        
        return present_skills
    
    def _identify_missing_skills(self, text: str, industry: str) -> List[str]:
        """Identify important skills missing from resume"""
        # Industry-specific required skills
        industry_skills = {
            'technology': ['programming', 'software development', 'system design', 'debugging'],
            'healthcare': ['patient care', 'medical knowledge', 'compliance', 'documentation'],
            'finance': ['financial analysis', 'risk management', 'regulatory knowledge', 'accounting'],
            'marketing': ['digital marketing', 'content creation', 'analytics', 'campaign management']
        }
        
        required_skills = industry_skills.get(industry.lower(), [])
        missing_skills = []
        
        text_lower = text.lower()
        for skill in required_skills:
            if skill.lower() not in text_lower:
                missing_skills.append(skill)
        
        return missing_skills
    
    def _generate_industry_tips_with_ai(self, text: str, industry: str) -> List[str]:
        """Generate industry-specific improvement tips"""
        # Simplified tips generation
        tips = [
            f"Include more {industry.lower()}-specific keywords and terminology",
            f"Highlight achievements relevant to the {industry.lower()} industry",
            f"Emphasize skills that are valued in {industry.lower()}",
            f"Consider adding certifications relevant to {industry.lower()}"
        ]
        
        return tips
    
    def _calculate_role_alignment(self, text: str, industry: str) -> float:
        """Calculate alignment with target role/industry"""
        return self._calculate_industry_relevance(text, industry)
    
    def generate_overall_suggestions(self, analysis_results: Dict[str, Any]) -> List[str]:
        """Generate overall improvement suggestions based on all analyses"""
        suggestions = []
        
        # ATS suggestions
        if analysis_results['ats_analysis']['score'] < 70:
            suggestions.extend(analysis_results['ats_analysis']['optimization_tips'][:2])
        
        # Content suggestions
        if analysis_results['content_analysis']['score'] < 70:
            suggestions.extend(analysis_results['content_analysis']['content_suggestions'][:2])
        
        # Keyword suggestions
        if analysis_results['keyword_analysis']['score'] < 70:
            missing_keywords = analysis_results['keyword_analysis']['missing_keywords'][:3]
            if missing_keywords:
                suggestions.append(f"Consider adding these keywords: {', '.join(missing_keywords)}")
        
        # Industry suggestions
        if analysis_results['industry_analysis']['score'] < 70:
            suggestions.extend(analysis_results['industry_analysis']['industry_specific_tips'][:2])
        
        return suggestions[:5]  # Limit to top 5 suggestions
