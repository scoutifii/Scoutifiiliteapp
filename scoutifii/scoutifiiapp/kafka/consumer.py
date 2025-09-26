# scoutifiiapp/kafka/consumer.py
import json
import signal
import sys
from confluent_kafka import Consumer, KafkaException
import os
from dotenv import load_dotenv

load_dotenv()

class KafkaRunner:
    def __init__(self, group_id: str, topics: list[str]):
        self.topics = topics
        self.c = Consumer({
            "bootstrap.servers": os.getenv('KAFKA_BOOTSTRAP_SERVERS'),
            "group.id": group_id,
            "auto.offset.reset": "earliest",
            "enable.auto.commit": False,
        })
        self.running = True

    def start(self, handler):
        self.c.subscribe(self.topics)
        def _stop(*_):
            self.running = False
        signal.signal(signal.SIGINT, _stop)
        signal.signal(signal.SIGTERM, _stop)

        while self.running:
            msg = self.c.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                raise KafkaException(msg.error())
            try:
                payload = json.loads(msg.value().decode("utf-8"))
                key = msg.key().decode("utf-8") if msg.key() else None
                handler(topic=msg.topic(), key=key, payload=payload)
                self.c.commit(msg)
            except Exception as e:
                # log and optionally send to DLQ
                print(f"[kafka] handler error: {e} topic={msg.topic()} key={key} value={msg.value()!r}")
        self.c.close()
