from django.core.management.base import BaseCommand
from shared.events import event_bus
from notifications.models import Notification
import logging
import json

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Listen for notifications from the event bus and record them in the database.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Successfully started notification listener process."))
        
        def process_notification(event_type, data):
            if event_type == 'send_notification':
                try:
                    notification = Notification.objects.create(
                        user_id=data['user_id'],
                        title=data['title'],
                        message=data['message'],
                        notification_type=data.get('notification_type', 'info'),
                        link=data.get('link', ''),
                        data=data.get('extra_data', {})
                    )
                    logger.info(f"Notification created: ID {notification.id} for user {notification.user_id}")
                except Exception as e:
                    logger.error(f"Failed to create notification record: {e}")
            else:
                logger.debug(f"Received unknown event type: {event_type}")

        try:
            # Listening to 'notifications' channel with consumer group 'notification_service_group'
            # This allows multiple instances of the listener to share the load.
            event_bus.listen(
                channel='notifications',
                group_name='notification_service_group',
                consumer_name='notification_consumer_1',
                callback=process_notification
            )
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("Notification listener stopped by user."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Fatal error in notification listener: {e}"))
            logger.critical(f"Notification listener crashed: {e}")
