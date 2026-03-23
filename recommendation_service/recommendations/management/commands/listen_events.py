import os
import sys
from django.core.management.base import BaseCommand
from django.conf import settings

# Ensure we can import shared
sys.path.insert(0, os.path.join(settings.BASE_DIR.parent, 'shared'))
from events import event_bus

class Command(BaseCommand):
    help = 'Starts the Redis stream listener for recommendation service'

    def handle(self, *args, **options):
        self.stdout.write('Starting recommendation event listener...')
        
        def process_event(event_type, data):
            # Deferred import to ensure Django is fully loaded
            from recommendations.engine import RecommendationEngine
            from recommendations.models import UserPreference
            
            try:
                if event_type == 'video_started':
                    self.stdout.write(f"Processing video_started event: {data}")
                    user_id = data.get('user_id')
                    movie_id = data.get('movie_id')
                    
                    if user_id and movie_id:
                        engine = RecommendationEngine()
                        # Update preferences (simulated complex background task)
                        engine.update_preferences_for_user(user_id) 
                        self.stdout.write(f"Updated preferences for user {user_id}")
            except Exception as e:
                self.stderr.write(f"Error processing event {event_type}: {str(e)}")

        consumer_name = f"recommender-{os.environ.get('HOSTNAME', 'worker-1')}"
        
        try:
            event_bus.listen(
                channel='video_events',
                group_name='recommendation_group',
                consumer_name=consumer_name,
                callback=process_event
            )
        except KeyboardInterrupt:
            self.stdout.write('Shutting down listener.')
