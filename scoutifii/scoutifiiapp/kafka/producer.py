# scoutifiiapp/kafka/producer.py
import json
import threading
from confluent_kafka import Producer
import os
from dotenv import load_dotenv

load_dotenv()

_producer = None
_lock = threading.Lock()

def _get_config():
    cfg = {
        "bootstrap.servers": os.getenv("KAFKA_BOOTSTRAP_SERVERS"),
        "enable.idempotence": True,
        "acks": "all",
        "retries": 3,
        "linger.ms": 5,
        "batch.num.messages": 1000,
    }
    if os.getenv("KAFKA_SECURITY_PROTOCOL") != "PLAINTEXT":
        cfg.update({
            "security.protocol": os.getenv("KAFKA_SECURITY_PROTOCOL"),
            "sasl.mechanisms": os.getenv("KAFKA_SASL_MECHANISM"),
            "sasl.username": os.getenv("KAFKA_SASL_USERNAME"),
            "sasl.password": os.getenv("KAFKA_SASL_PASSWORD"),
        })
    return cfg

def get_producer() -> Producer:
    global _producer
    if _producer is None:
        with _lock:
            if _producer is None:
                _producer = Producer(_get_config())
    return _producer

def _delivery_report(err, msg):
    if err is not None:
        # Replace with your logger
        print(f"[kafka] delivery failed: {err} topic={msg.topic()} key={msg.key()}")
    # else: delivered OK; avoid chatty logs in prod

def send_event(topic: str, key: str, payload: dict) -> None:
    p = get_producer()
    try:
        p.produce(
            topic=topic,
            key=key.encode("utf-8") if isinstance(key, str) else key,
            value=json.dumps(payload).encode("utf-8"),
            on_delivery=_delivery_report,
        )
        p.poll(0)  # serve delivery callbacks
    except BufferError:
        p.flush(5)
        p.produce(
            topic=topic, 
            key=key, 
            value=json.dumps(payload).encode("utf-8"), 
            on_delivery=_delivery_report
        )
