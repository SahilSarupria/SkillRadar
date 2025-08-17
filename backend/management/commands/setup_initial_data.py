from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from recommendations.models import LearningPlatform, Skill
from dashboard.models import SystemStats
from django.utils import timezone

User = get_user_model()

class Command(BaseCommand):
    help = 'Setup initial data for the AI Resume Converter'
    
    def handle(self, *args, **options):
        self.stdout.write('Setting up initial data...')
        
        # Create learning platforms
        self.create_learning_platforms()
        
        # Create initial skills
        self.create_initial_skills()
        
        # Generate initial system stats
        self.generate_initial_stats()
        
        self.stdout.write(
            self.style.SUCCESS('Successfully set up initial data!')
        )
    
    def create_learning_platforms(self):
        """Create initial learning platforms"""
        platforms = [
            {
                'name': 'Coursera',
                'description': 'Online courses from top universities and companies',
                'website_url': 'https://www.coursera.org',
                'logo_url': 'https://d3njjcbhbojbot.cloudfront.net/api/utilities/v1/imageproxy/https://coursera-university-assets.s3.amazonaws.com/fa/03d7b0c2b711e5a1b7e3b7c0b8c7e8/coursera-logo.png'
            },
            {
                'name': 'Udemy',
                'description': 'Online learning platform with courses on various topics',
                'website_url': 'https://www.udemy.com',
                'logo_url': 'https://www.udemy.com/staticx/udemy/images/v7/logo-udemy.svg'
            },
            {
                'name': 'edX',
                'description': 'Free online courses from Harvard, MIT, and other top universities',
                'website_url': 'https://www.edx.org',
                'logo_url': 'https://www.edx.org/images/logos/edx-logo-elm.svg'
            },
            {
                'name': 'LinkedIn Learning',
                'description': 'Professional development courses',
                'website_url': 'https://www.linkedin.com/learning',
                'logo_url': 'https://static.licdn.com/sc/h/dxf91zhqd2z6b0bwg85ktm5s4'
            },
            {
                'name': 'Pluralsight',
                'description': 'Technology skills platform',
                'website_url': 'https://www.pluralsight.com',
                'logo_url': 'https://www.pluralsight.com/content/dam/pluralsight2/logos/pluralsight-logo-vrt-color-2.png'
            }
        ]
        
        for platform_data in platforms:
            platform, created = LearningPlatform.objects.get_or_create(
                name=platform_data['name'],
                defaults=platform_data
            )
            if created:
                self.stdout.write(f'Created platform: {platform.name}')
    
    def create_initial_skills(self):
        """Create initial skill categories and skills"""
        skills_data = {
            'Programming': [
                'Python', 'JavaScript', 'Java', 'C++', 'C#', 'PHP', 'Ruby', 'Go',
                'Swift', 'Kotlin', 'TypeScript', 'Rust', 'Scala', 'R'
            ],
            'Web Development': [
                'HTML', 'CSS', 'React', 'Angular', 'Vue.js', 'Node.js', 'Express.js',
                'Django', 'Flask', 'Laravel', 'Spring Boot', 'ASP.NET'
            ],
            'Data Science': [
                'Machine Learning', 'Data Analysis', 'Statistics', 'SQL', 'NoSQL',
                'Pandas', 'NumPy', 'Scikit-learn', 'TensorFlow', 'PyTorch',
                'Tableau', 'Power BI', 'Excel'
            ],
            'Cloud & DevOps': [
                'AWS', 'Azure', 'Google Cloud', 'Docker', 'Kubernetes', 'Jenkins',
                'Git', 'CI/CD', 'Terraform', 'Ansible', 'Linux', 'Bash'
            ],
            'Design': [
                'UI/UX Design', 'Photoshop', 'Illustrator', 'Figma', 'Sketch',
                'Adobe XD', 'InDesign', 'After Effects', 'Canva'
            ],
            'Business': [
                'Project Management', 'Agile', 'Scrum', 'Leadership', 'Communication',
                'Marketing', 'Sales', 'Finance', 'Strategy', 'Analytics'
            ],
            'Mobile Development': [
                'iOS Development', 'Android Development', 'React Native', 'Flutter',
                'Xamarin', 'Ionic', 'Swift', 'Kotlin'
            ],
            'Database': [
                'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Elasticsearch',
                'Oracle', 'SQL Server', 'SQLite', 'Cassandra'
            ]
        }
        
        for category, skills in skills_data.items():
            for skill_name in skills:
                skill, created = Skill.objects.get_or_create(
                    name=skill_name,
                    defaults={'category': category.lower().replace(' & ', '_').replace(' ', '_')}
                )
                if created:
                    self.stdout.write(f'Created skill: {skill.name} ({category})')
    
    def generate_initial_stats(self):
        """Generate initial system statistics"""
        today = timezone.now().date()
        stats = SystemStats.generate_daily_stats(today)
        self.stdout.write(f'Generated system stats for {today}')
