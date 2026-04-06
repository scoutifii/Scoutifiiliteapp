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
        "kafka.kraft.mode": os.getenv("KAFKA_KRAFT_MODE"),
        "kafka.node.id": os.getenv("KAFKA_NODE_ID"),
        "cluster.id": os.getenv("CLUSTER_ID"),
        "kafka.process.roles": os.getenv("KAFKA_PROCESS_ROLES"),
        "kafka.controller.quorum.voters": os.getenv("KAFKA_CONTROLLER_QUORUM_VOTERS"),
        "kafka.offsets.topic.replication.factor": os.getenv("KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR"),
        "kafka.listeners": os.getenv("KAFKA_LISTENERS"),
        "kafka.advertised.listeners": os.getenv("KAFKA_ADVERTISED_LISTENERS"),
        "kafka.controller.listener.names": os.getenv("KAFKA_CONTROLLER_LISTENER_NAMES"),
        "kafka.log.dirs": os.getenv("KAFKA_LOG_DIRS")
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
    if err:
        print(f"Delivery failed: {err}")
    else:
        print(f"Delivered {msg.value().decode("utf-8")}") 
        print(f"Delivered to topic={msg.topic()} key={msg.key()} partition={msg.partition} : at offset {msg.offset()}")


def send_event(topic: str, key: str, payload: dict) -> None:
    p = get_producer()
    try:
        # Creates posts
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
