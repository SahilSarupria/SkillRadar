import os
import re
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

from tempfile import NamedTemporaryFile

from difflib import get_close_matches

from django.conf import settings

logger = logging.getLogger(__name__)

# Optional libs (import lazily to avoid hard failure)
try:
    import spacy
    _SPACY_AVAILABLE = True
except Exception:
    spacy = None
    _SPACY_AVAILABLE = False

try:
    import PyPDF2
except Exception:
    PyPDF2 = None

try:
    import docx
except Exception:
    docx = None


class FileParser:
    """Utility for extracting text from uploaded resume files."""

    @staticmethod
    def extract_text_from_pdf(file_path: str) -> str:
        if PyPDF2 is None:
            logger.warning("PyPDF2 not installed; PDF parsing unavailable.")
            return ""
        try:
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                pages = []
                for p in reader.pages:
                    pages.append(p.extract_text() or "")
                return "\n".join(pages).strip()
        except Exception as e:
            logger.exception("PDF extraction failed: %s", e)
            return ""

    @staticmethod
    def extract_text_from_docx(file_path: str) -> str:
        if docx is None:
            logger.warning("python-docx not installed; DOCX parsing unavailable.")
            return ""
        try:
            d = docx.Document(file_path)
            return "\n".join([p.text for p in d.paragraphs]).strip()
        except Exception as e:
            logger.exception("DOCX extraction failed: %s", e)
            return ""

    @staticmethod
    def extract_text_from_txt(file_path: str) -> str:
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        except Exception as e:
            logger.exception("TXT extraction failed: %s", e)
            return ""


class AIResumeProcessor:
    

    def __init__(self, spacy_model: str = "en_core_web_sm"):
        self.spacy_model_name = getattr(settings, "SPACY_MODEL", spacy_model)
        self._nlp = None
        self._ensure_spacy()
        # load skill list from DB if available (best-effort)
        self._skill_db = None
        try:
            from skills.models import Skill
            self._skill_db = list(Skill.objects.values_list("name", flat=True))
            logger.debug("Loaded %d skills from DB", len(self._skill_db))
        except Exception:
            self._skill_db = []

    def _ensure_spacy(self):
        if not _SPACY_AVAILABLE:
            self._nlp = None
            return None
        if self._nlp is None:
            try:
                self._nlp = spacy.load(self.spacy_model_name)
            except Exception as e:
                logger.warning("Could not load spaCy model '%s': %s", self.spacy_model_name, e)
                self._nlp = None
        return self._nlp

    # -------------------------
    # Parsing and extraction
    # -------------------------
    def parse_file(self, file_path: str) -> Dict[str, Any]:
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".pdf":
            text = FileParser.extract_text_from_pdf(file_path)
        elif ext in (".docx", ".doc"):
            text = FileParser.extract_text_from_docx(file_path)
        else:
            text = FileParser.extract_text_from_txt(file_path)
        return self.text_to_structured_resume(text)

    def text_to_structured_resume(self, text_content: str, template_style: str = "professional") -> Dict[str, Any]:
        text = (text_content or "").strip()
        # quick normalizations
        text = re.sub(r'\r\n', '\n', text)
        text = re.sub(r'\t', ' ', text)

        # Personal info
        email = self._extract_email(text)
        phone = self._extract_phone(text)
        name = self._extract_name(text)

        summary = self._extract_summary(text)
        skills = self.extract_skills_from_text(text)
        experience_years = self.extract_years_experience(text)
        work_experience = self._extract_work_experience(text)
        education = self.extract_education_keywords(text)
        certifications = self.extract_certifications(text)
        projects = self._extract_projects(text)

        structured = {
            "personal_info": {
                "full_name": name or "",
                "email": email or "",
                "phone": phone or "",
                "location": "",
                "linkedin": "",
                "github": "",
                "website": ""
            },
            "professional_summary": summary or "",
            "work_experience": work_experience,
            "education": education,
            "skills": skills,
            "projects": projects,
            "certifications": certifications,
            "awards": [],
            "experience_years": experience_years,
        }

        return structured

    # -------------------------
    # Helper extractors
    # -------------------------
    def _extract_email(self, text: str) -> Optional[str]:
        m = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b', text)
        return m.group(0) if m else None

    def _extract_phone(self, text: str) -> Optional[str]:
        m = re.search(r'(\+\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}', text)
        return m.group(0) if m else None

    def _extract_name(self, text: str) -> Optional[str]:
        # Prefer spaCy PERSON entity in the first 1200 chars
        if self._nlp:
            try:
                doc = self._nlp(text[:1500])
                for ent in doc.ents:
                    if ent.label_ == "PERSON" and 2 <= len(ent.text.split()) <= 3:
                        # avoid lines containing emails/numbers
                        if '@' in ent.text or any(ch.isdigit() for ch in ent.text):
                            continue
                        return ent.text.strip()
            except Exception:
                pass

        # fallback: first non-empty line that looks like a name
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        for line in lines[:8]:
            if 2 <= len(line.split()) <= 4 and line[0].isupper():
                if '@' in line or any(ch.isdigit() for ch in line):
                    continue
                return line
        return None

    def _extract_summary(self, text: str) -> str:
        # Use first paragraph up to 300-400 chars as summary
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        if paragraphs:
            cand = paragraphs[0]
            return cand if len(cand) <= 600 else cand[:600] + "..."
        # fallback: first 400 chars
        return text[:400] + ("..." if len(text) > 400 else "")

    def extract_years_experience(self, text: str) -> int:
        # common patterns like "5 years", "5+ years", "7 yrs"
        matches = re.findall(r'(\d{1,2})(?:\+)?\s*(?:years|yrs|year)\b', text.lower())
        if matches:
            try:
                return max(int(m) for m in matches)
            except Exception:
                pass
        # try counting date ranges like "2017 - 2020" or "2017 – Present"
        total_months = 0
        range_matches = re.findall(r'(\d{4})\s*[-–]\s*(present|\d{4})', text.lower())
        for a, b in range_matches:
            try:
                a_y = int(a)
                b_y = datetime.utcnow().year if b in ("present", "current") else int(b)
                total_months += max(0, (b_y - a_y) * 12)
            except Exception:
                continue
        if total_months:
            return max(0, total_months // 12)
        return 0

    def _extract_work_experience(self, text: str) -> List[Dict[str, Any]]:
        """
        Heuristic extraction:
         - Look for lines with year ranges and take surrounding lines as role/company/description.
         - Otherwise return empty list (frontend/editor allows adding entries).
        """
        experiences = []
        lines = [l for l in text.splitlines() if l.strip()]
        pattern = re.compile(r'(\b\d{4}\b).{0,6}[-–]\s*(present|\b\d{4}\b)', re.I)
        for idx, line in enumerate(lines):
            if pattern.search(line):
                # try to capture company and title from nearby lines
                title = lines[idx - 1].strip() if idx - 1 >= 0 else ""
                company = lines[idx - 2].strip() if idx - 2 >= 0 else ""
                dates = pattern.search(line).group(0)
                # body: collect following 3 lines as description
                desc_lines = []
                for j in range(idx + 1, min(idx + 4, len(lines))):
                    if lines[j].strip():
                        desc_lines.append(lines[j].strip())
                experiences.append({
                    "company_name": company,
                    "position": title,
                    "start_date": None,
                    "end_date": None,
                    "is_current": "present" in dates.lower() or "current" in dates.lower(),
                    "description": " ".join(desc_lines),
                    "skills_used": []
                })
        # if none found, return empty
        return experiences

    def extract_education_keywords(self, text: str) -> List[Dict[str, Any]]:
        keys = ['bachelor', 'master', 'phd', 'mba', 'b.sc', 'm.sc', 'bs', 'ms', 'associate']
        out = []
        low = text.lower()
        for k in keys:
            if k in low:
                out.append({"degree": k, "institution": None})
        return out

    def extract_certifications(self, text: str) -> List[str]:
        certs = re.findall(r'(?:certified|certificate in|certification[:\s])\s*([A-Za-z0-9\-\&\(\)\/\s]+)', text, re.I)
        return [c.strip() for c in certs] if certs else []

    def _extract_projects(self, text: str) -> List[Dict[str, Any]]:
        # simple heuristic: look for "Project" headings or "Project:" markers
        projects = []
        matches = re.findall(r'(?:project[:\s\-]+)([^\n\r]{10,200})', text, re.I)
        for m in matches:
            projects.append({"name": None, "description": m.strip(), "technologies": []})
        return projects

    def extract_skills_from_text(self, text: str) -> Dict[str, List[str]]:
        """
        Extract skills by:
         - matching against DB skill list if available (substring & fuzzy matching)
         - using spaCy noun chunks/entities as candidates otherwise
         - heuristics for tools/languages
        """
        text_l = text.lower()
        candidates = set()

        # spaCy candidates
        if self._nlp:
            try:
                doc = self._nlp(text)
                for nc in doc.noun_chunks[:400]:
                    candidates.add(nc.text.strip())
                for ent in doc.ents:
                    candidates.add(ent.text.strip())
            except Exception:
                pass

        # split on delimiters for additional candidates
        for tok in re.split(r'[\n,;/•\|\-\(\)]+', text):
            t = tok.strip()
            if 2 <= len(t) <= 80:
                candidates.add(t)

        # match against DB skill list
        technical = []
        soft = []
        languages = []
        tools = []

        skill_db_lower = [s.lower() for s in (self._skill_db or [])]

        if skill_db_lower:
            for cand in candidates:
                s = cand.lower()
                # direct substring match
                for idx, dbs in enumerate(skill_db_lower):
                    if dbs in s or s in dbs:
                        name = (self._skill_db or [])[idx]
                        technical.append(name)
                # fuzzy match: close matches
                close = get_close_matches(s, skill_db_lower, n=1, cutoff=0.88)
                if close:
                    idx = skill_db_lower.index(close[0])
                    technical.append((self._skill_db or [])[idx])
        else:
            # heuristics when DB absent
            for cand in candidates:
                s = cand.lower()
                if re.search(r'\b(python|java|c\+\+|c#|javascript|typescript|sql|django|flask|react|node|go|rust)\b', s):
                    technical.append(cand)
                elif re.search(r'\b(aws|azure|gcp|docker|kubernetes|git|github|gitlab)\b', s):
                    tools.append(cand)
                elif re.search(r'\b(communication|leadership|team|management|collaborat|problem solving)\b', s):
                    soft.append(cand)
                elif re.search(r'\b(english|spanish|french|hindi)\b', s):
                    languages.append(cand)
                else:
                    # keep short candidates as potential technical skills
                    if len(s.split()) <= 3 and re.search(r'[a-zA-Z0-9\+#\.]', s):
                        technical.append(cand)

        # normalize/dedupe preserving order
        def uniq(lst: List[str]) -> List[str]:
            seen = set()
            out = []
            for item in lst:
                if not item:
                    continue
                k = item.strip().lower()
                if k in seen:
                    continue
                seen.add(k)
                out.append(item.strip())
            return out

        return {
            "technical": uniq(technical),
            "soft": uniq(soft),
            "languages": uniq(languages),
            "tools": uniq(tools),
        }

    # -------------------------
    # Scoring
    # -------------------------
    def calculate_score(self, resume_data: Dict[str, Any], goal: Dict[str, Any]) -> Dict[str, Any]:
        """
        Score resume relative to goal:
          goal: { required_skills: [...], min_experience_years: int, weight_skills: float (0-1) }
        Returns: { score:int, breakdown: {...}, matched_skills: [...] }
        """
        required = [s.lower() for s in goal.get("required_skills", [])] if isinstance(goal.get("required_skills", []), list) else []
        # flatten user skills
        user_skills = []
        skills_section = resume_data.get("skills", {})
        if isinstance(skills_section, dict):
            for v in skills_section.values():
                if isinstance(v, list):
                    user_skills.extend([str(x).lower() for x in v])
        # skills mentioned in experience descriptions
        for we in resume_data.get("work_experience", []) or []:
            for s in we.get("skills_used", []) if isinstance(we.get("skills_used", []), list) else []:
                user_skills.append(str(s).lower())

        user_set = set(user_skills)
        req_set = set(required)

        skill_match_ratio = (len(user_set & req_set) / len(req_set)) if req_set else 1.0

        user_exp = resume_data.get("experience_years") or self.extract_years_experience(resume_data.get("professional_summary", "") or "")
        req_exp = int(goal.get("min_experience_years", 0) or 0)
        exp_ratio = (min(user_exp / req_exp, 1.0) if req_exp > 0 else 1.0)

        certs = resume_data.get("certifications") or []
        cert_bonus = min(len(certs) * 0.02, 0.06)

        w_skills = float(goal.get("weight_skills", 0.7))
        w_exp = 1.0 - w_skills

        raw = (w_skills * skill_match_ratio + w_exp * exp_ratio) + cert_bonus
        score = int(max(0, min(100, round(raw * 100))))
        breakdown = {
            "skill_match_percent": round(skill_match_ratio * 100, 2),
            "experience_match_percent": round(exp_ratio * 100, 2),
            "certification_bonus_percent": round(cert_bonus * 100, 2),
            "raw_score": raw,
        }
        matched = list(user_set & req_set)
        return {"score": score, "breakdown": breakdown, "matched_skills": matched}

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
    