import openai
import PyPDF2
import docx
import json
import re
from datetime import datetime
from django.conf import settings
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class FileParser:
    """Utility class for parsing different file formats"""
    
    @staticmethod
    def extract_text_from_pdf(file_path):
        """Extract text from PDF file"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text.strip()
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            return ""
    
    @staticmethod
    def extract_text_from_docx(file_path):
        """Extract text from DOCX file"""
        try:
            doc = docx.Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            logger.error(f"Error extracting text from DOCX: {str(e)}")
            return ""
    
    @staticmethod
    def extract_text_from_txt(file_path):
        """Extract text from TXT file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read().strip()
        except Exception as e:
            logger.error(f"Error extracting text from TXT: {str(e)}")
            return ""

class AIResumeProcessor:
    """AI-powered resume processing and conversion"""
    
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
    
    def text_to_structured_resume(self, text_content: str, template_style: str = 'professional') -> Dict[str, Any]:
        """Convert raw text to structured resume data using OpenAI"""
        
        system_prompt = f"""
        You are an expert resume writer and parser. Convert the provided raw text into a well-structured resume format.
        
        Template Style: {template_style}
        
        Return a JSON object with the following structure:
        {{
            "personal_info": {{
                "full_name": "string",
                "email": "string",
                "phone": "string",
                "location": "string",
                "linkedin": "string",
                "github": "string",
                "website": "string"
            }},
            "professional_summary": "string (2-3 sentences)",
            "work_experience": [
                {{
                    "company_name": "string",
                    "position": "string",
                    "location": "string",
                    "start_date": "YYYY-MM-DD",
                    "end_date": "YYYY-MM-DD or null if current",
                    "is_current": boolean,
                    "description": "string",
                    "achievements": ["string", "string"],
                    "skills_used": ["string", "string"]
                }}
            ],
            "education": [
                {{
                    "institution": "string",
                    "degree": "string",
                    "field_of_study": "string",
                    "location": "string",
                    "start_date": "YYYY-MM-DD",
                    "end_date": "YYYY-MM-DD",
                    "gpa": "float or null",
                    "achievements": ["string", "string"]
                }}
            ],
            "skills": {{
                "technical": ["string", "string"],
                "soft": ["string", "string"],
                "languages": ["string", "string"],
                "tools": ["string", "string"]
            }},
            "projects": [
                {{
                    "name": "string",
                    "description": "string",
                    "technologies": ["string", "string"],
                    "start_date": "YYYY-MM-DD or null",
                    "end_date": "YYYY-MM-DD or null",
                    "project_url": "string or null",
                    "github_url": "string or null"
                }}
            ],
            "certifications": [
                {{
                    "name": "string",
                    "issuer": "string",
                    "date_obtained": "YYYY-MM-DD",
                    "expiry_date": "YYYY-MM-DD or null",
                    "credential_id": "string or null"
                }}
            ],
            "awards": [
                {{
                    "title": "string",
                    "issuer": "string",
                    "date": "YYYY-MM-DD",
                    "description": "string"
                }}
            ]
        }}
        
        Guidelines:
        1. Extract all relevant information from the text
        2. Infer missing dates where possible
        3. Organize achievements and responsibilities clearly
        4. Ensure all dates are in YYYY-MM-DD format
        5. If information is missing, use null or empty arrays
        6. Make the content professional and well-formatted
        7. Optimize for ATS (Applicant Tracking Systems)
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Convert this text to a structured resume:\n\n{text_content}"}
                ],
                temperature=0.3,
                max_tokens=4000
            )
            
            result = response.choices[0].message.content
            return json.loads(result)
            
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing AI response as JSON: {str(e)}")
            return self._fallback_parsing(text_content)
        except Exception as e:
            logger.error(f"Error in AI processing: {str(e)}")
            return self._fallback_parsing(text_content)
    
    def _fallback_parsing(self, text_content: str) -> Dict[str, Any]:
        """Fallback parsing method when AI fails"""
        # Basic regex-based parsing as fallback
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        phone_pattern = r'(\+\d{1,3}[-.\s]?)?$$?\d{3}$$?[-.\s]?\d{3}[-.\s]?\d{4}'
        
        email = re.search(email_pattern, text_content)
        phone = re.search(phone_pattern, text_content)
        
        return {
            "personal_info": {
                "full_name": "Unknown",
                "email": email.group() if email else "",
                "phone": phone.group() if phone else "",
                "location": "",
                "linkedin": "",
                "github": "",
                "website": ""
            },
            "professional_summary": text_content[:200] + "..." if len(text_content) > 200 else text_content,
            "work_experience": [],
            "education": [],
            "skills": {"technical": [], "soft": [], "languages": [], "tools": []},
            "projects": [],
            "certifications": [],
            "awards": []
        }
    
    def enhance_resume_content(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance resume content with AI suggestions"""
        
        system_prompt = """
        You are a professional resume writer. Enhance the provided resume data by:
        1. Improving the professional summary
        2. Making achievements more impactful with metrics
        3. Optimizing for ATS keywords
        4. Ensuring consistent formatting
        5. Adding relevant skills if missing
        
        Return the enhanced resume in the same JSON format.
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Enhance this resume data:\n\n{json.dumps(resume_data, indent=2)}"}
                ],
                temperature=0.4,
                max_tokens=3000
            )
            
            result = response.choices[0].message.content
            return json.loads(result)
            
        except Exception as e:
            logger.error(f"Error enhancing resume content: {str(e)}")
            return resume_data

class ResumeBuilder:
    """Build resume objects from structured data"""
    
    @staticmethod
    def create_resume_from_data(user, title: str, resume_data: Dict[str, Any], resume_type: str = 'converted') -> 'Resume':
        """Create Resume object and related models from structured data"""
        from .models import Resume, ResumeSection, WorkExperience, Education, Project
        
        # Create main resume object
        resume = Resume.objects.create(
            user=user,
            title=title,
            resume_type=resume_type,
            status='completed',
            processed_content=resume_data
        )
        
        # Create personal info section
        if 'personal_info' in resume_data:
            ResumeSection.objects.create(
                resume=resume,
                section_type='personal_info',
                title='Personal Information',
                content=resume_data['personal_info'],
                order=1
            )
        
        # Create professional summary section
        if 'professional_summary' in resume_data and resume_data['professional_summary']:
            ResumeSection.objects.create(
                resume=resume,
                section_type='summary',
                title='Professional Summary',
                content={'summary': resume_data['professional_summary']},
                order=2
            )
        
        # Create work experience entries
        if 'work_experience' in resume_data:
            for idx, exp in enumerate(resume_data['work_experience']):
                WorkExperience.objects.create(
                    resume=resume,
                    company_name=exp.get('company_name', ''),
                    position=exp.get('position', ''),
                    location=exp.get('location', ''),
                    start_date=exp.get('start_date'),
                    end_date=exp.get('end_date'),
                    is_current=exp.get('is_current', False),
                    description=exp.get('description', ''),
                    achievements=exp.get('achievements', []),
                    skills_used=exp.get('skills_used', [])
                )
        
        # Create education entries
        if 'education' in resume_data:
            for edu in resume_data['education']:
                Education.objects.create(
                    resume=resume,
                    institution=edu.get('institution', ''),
                    degree=edu.get('degree', ''),
                    field_of_study=edu.get('field_of_study', ''),
                    location=edu.get('location', ''),
                    start_date=edu.get('start_date'),
                    end_date=edu.get('end_date'),
                    gpa=edu.get('gpa'),
                    achievements=edu.get('achievements', [])
                )
        
        # Create skills section
        if 'skills' in resume_data:
            ResumeSection.objects.create(
                resume=resume,
                section_type='skills',
                title='Skills',
                content=resume_data['skills'],
                order=5
            )
        
        # Create projects
        if 'projects' in resume_data:
            for project in resume_data['projects']:
                Project.objects.create(
                    resume=resume,
                    name=project.get('name', ''),
                    description=project.get('description', ''),
                    technologies=project.get('technologies', []),
                    start_date=project.get('start_date'),
                    end_date=project.get('end_date'),
                    project_url=project.get('project_url', ''),
                    github_url=project.get('github_url', '')
                )
        
        # Create certifications section
        if 'certifications' in resume_data and resume_data['certifications']:
            ResumeSection.objects.create(
                resume=resume,
                section_type='certifications',
                title='Certifications',
                content={'certifications': resume_data['certifications']},
                order=7
            )
        
        # Create awards section
        if 'awards' in resume_data and resume_data['awards']:
            ResumeSection.objects.create(
                resume=resume,
                section_type='awards',
                title='Awards',
                content={'awards': resume_data['awards']},
                order=8
            )
        
        return resume
