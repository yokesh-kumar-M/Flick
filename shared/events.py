import os
import json
import redis
import logging

logger = logging.getLogger(__name__)

def get_redis_client():
    redis_url = os.environ.get('REDIS_URL', 'redis://redis:6379/0')
    # Default to docker network alias 'redis' if running locally without env
    if 'localhost' in redis_url and not os.path.exists('/.dockerenv'):
        pass # use localhost
    elif 'localhost' in redis_url:
        redis_url = redis_url.replace('localhost', 'redis')
    return redis.from_url(redis_url)

class EventBus:
    """
    A lightweight message broker using Redis Pub/Sub Streams.
    Used for inter-service communication.
    """
    def __init__(self):
        self.redis = get_redis_client()
        
    def publish(self, channel, event_type, data):
        """
        Publish an event to a Redis channel.
        """
        try:
            payload = {
                'event_type': event_type,
                'data': data
            }
            # We use xadd to use Redis Streams instead of basic Pub/Sub for persistence and consumer groups
            self.redis.xadd(channel, {'payload': json.dumps(payload)})
            logger.info(f"Published event '{event_type}' to channel '{channel}'")
        except Exception as e:
            logger.error(f"Failed to publish event: {str(e)}")

    def listen(self, channel, group_name, consumer_name, callback):
        """
        Listen to a Redis Stream using Consumer Groups.
        """
        try:
            # Create consumer group if it doesn't exist
            try:
                self.redis.xgroup_create(channel, group_name, id='0', mkstream=True)
            except redis.exceptions.ResponseError as e:
                if "BUSYGROUP Consumer Group name already exists" not in str(e):
                    raise e

            logger.info(f"Started listening to '{channel}' as '{consumer_name}' in group '{group_name}'")
            
            while True:
                # Read 1 message, block for 5 seconds
                messages = self.redis.xreadgroup(group_name, consumer_name, {channel: '>'}, count=1, block=5000)
                
                if messages:
                    for stream, event_list in messages:
                        for event_id, event_data in event_list:
                            try:
                                payload_str = event_data.get(b'payload')
                                if payload_str:
                                    payload = json.loads(payload_str)
                                    callback(payload.get('event_type'), payload.get('data'))
                                # Acknowledge successful processing
                                self.redis.xack(channel, group_name, event_id)
                            except Exception as e:
                                logger.error(f"Error processing event {event_id}: {str(e)}")
        except Exception as e:
            logger.error(f"Listener failed: {str(e)}")

event_bus = EventBus()
