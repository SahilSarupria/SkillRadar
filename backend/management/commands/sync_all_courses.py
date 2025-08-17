from django.core.management.base import BaseCommand
from recommendations.models import LearningPlatform
from recommendations.tasks import sync_platform_courses_task

class Command(BaseCommand):
    help = 'Sync courses from all learning platforms'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--platform',
            type=str,
            help='Sync courses from specific platform only',
        )
        parser.add_argument(
            '--async',
            action='store_true',
            help='Run sync tasks asynchronously',
        )
    
    def handle(self, *args, **options):
        platform_name = options.get('platform')
        run_async = options.get('async', False)
        
        if platform_name:
            platforms = LearningPlatform.objects.filter(
                name__iexact=platform_name,
                is_active=True
            )
            if not platforms.exists():
                self.stdout.write(
                    self.style.ERROR(f'Platform "{platform_name}" not found or inactive')
                )
                return
        else:
            platforms = LearningPlatform.objects.filter(is_active=True)
        
        self.stdout.write(f'Syncing courses from {platforms.count()} platform(s)...')
        
        for platform in platforms:
            if run_async:
                # Run asynchronously with Celery
                task = sync_platform_courses_task.delay(platform.name)
                self.stdout.write(f'Queued sync task for {platform.name} (Task ID: {task.id})')
            else:
                # Run synchronously
                from recommendations.utils import PlatformIntegrator
                integrator = PlatformIntegrator(platform.name)
                result = integrator.sync_courses()
                
                if result['success']:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Successfully synced {result.get("courses_synced", 0)} courses from {platform.name}'
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(f'Failed to sync {platform.name}: {result.get("error")}')
                    )
        
        if not run_async:
            self.stdout.write(self.style.SUCCESS('Course sync completed!'))
