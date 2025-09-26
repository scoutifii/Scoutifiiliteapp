# scoutifiiapp/management/commands/kafka_events.py
from django.core.management.base import BaseCommand
from dotenv import load_dotenv
import os
from scoutifiiapp.kafka.consumer import KafkaRunner

load_dotenv()

TOPIC_POST_CREATED = os.getenv("KAFKA_TOPIC_POST_CREATED", "scoutifii.post.created")
TOPIC_COMMENT_CREATED = os.getenv("KAFKA_TOPIC_COMMENT_CREATED", "scoutifii.comment.created")
TOPIC_LIKE_CREATED = os.getenv("KAFKA_TOPIC_LIKE_CREATED", "scoutifii.like.created")
TOPIC_NOTIFICATION = os.getenv("KAFKA_TOPIC_NOTIFICATION", "scoutifii.notification")
TOPIC_AUDIT = os.getenv("KAFKA_TOPIC_AUDIT", "scoutifii.audit")

def handle_event(topic: str, key: str, payload: dict):
    if topic == TOPIC_POST_CREATED:
        print("handle post_created", key, payload)
        # TODO: call your service
    elif topic == TOPIC_COMMENT_CREATED:
        print("handle comment_created", key, payload)
    elif topic == TOPIC_LIKE_CREATED:
        print("handle like_created", key, payload)
    elif topic == TOPIC_NOTIFICATION:
        print("handle notification", key, payload)
    elif topic == TOPIC_AUDIT:
        print("handle audit", key, payload)
    else:
        print("unhandled", topic)

class Command(BaseCommand):
    help = "Run Kafka event consumer"

    def handle(self, *args, **options):
        topics = [
            TOPIC_POST_CREATED,
            TOPIC_COMMENT_CREATED,
            TOPIC_LIKE_CREATED,
            TOPIC_NOTIFICATION,
            TOPIC_AUDIT,
        ]
        runner = KafkaRunner(group_id="scoutifii.events.v1", topics=topics)
        runner.start(handle_event)
