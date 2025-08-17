from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Generate sample data for testing and development'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=10,
            help='Number of sample users to create',
        )
        parser.add_argument(
            '--resumes',
            type=int,
            default=20,
            help='Number of sample resumes to create',
        )
    
    def handle(self, *args, **options):
        num_users = options['users']
        num_resumes = options['resumes']
        
        self.stdout.write('Generating sample data...')
        
        # Create sample users
        users = self.create_sample_users(num_users)
        
        # Create sample resumes
        self.create_sample_resumes(users, num_resumes)
        
        # Create sample activities
        self.create_sample_activities(users)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully generated sample data: {num_users} users, {num_resumes} resumes'
            )
        )
    
    def create_sample_users(self, count):
        """Create sample users"""
        users = []
        
        for i in range(count):
            email = f'user{i+1}@example.com'
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'first_name': f'User{i+1}',
                    'last_name': 'Test',
                    'is_active': True,
                    'date_joined': timezone.now() - timedelta(days=random.randint(1, 30))
                }
            )
            if created:
                user.set_password('testpass123')
                user.save()
                users.append(user)
                self.stdout.write(f'Created user: {email}')
        
        return users
    
    def create_sample_resumes(self, users, count):
        """Create sample resumes"""
        from resumes.models import Resume
        
        sample_titles = [
            'Software Engineer Resume',
            'Data Scientist Resume',
            'Product Manager Resume',
            'Marketing Specialist Resume',
            'UX Designer Resume',
            'DevOps Engineer Resume',
            'Business Analyst Resume',
            'Full Stack Developer Resume'
        ]
        
        for i in range(count):
            user = random.choice(users)
            title = random.choice(sample_titles)
            
            resume = Resume.objects.create(
                user=user,
                title=f'{title} - {i+1}',
                original_filename=f'resume_{i+1}.pdf',
                file_type='pdf',
                file_size=random.randint(100000, 500000),
                conversion_status=random.choice(['pending', 'processing', 'completed', 'failed']),
                created_at=timezone.now() - timedelta(days=random.randint(1, 15))
            )
            
            self.stdout.write(f'Created resume: {resume.title} for {user.email}')
    
    def create_sample_activities(self, users):
        """Create sample user activities"""
        from dashboard.models import UserActivity
        
        activity_types = [
            'login', 'resume_upload', 'resume_convert', 'resume_analyze',
            'skill_analysis', 'view_recommendations', 'bookmark_course'
        ]
        
        for user in users:
            # Create 5-15 activities per user
            num_activities = random.randint(5, 15)
            
            for _ in range(num_activities):
                activity_type = random.choice(activity_types)
                created_at = timezone.now() - timedelta(
                    days=random.randint(0, 30),
                    hours=random.randint(0, 23),
                    minutes=random.randint(0, 59)
                )
                
                UserActivity.objects.create(
                    user=user,
                    activity_type=activity_type,
                    description=f'Sample {activity_type} activity',
                    created_at=created_at
                )
            
            self.stdout.write(f'Created {num_activities} activities for {user.email}')
