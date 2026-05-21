from typing import Dict, List, Any, Callable
from datetime import datetime
import uuid


class Message:
    def __init__(
        self,
        sender: str,
        recipient: str,
        topic: str,
        payload: Dict[str, Any],
        message_id: str = None,
        timestamp: datetime = None,
    ):
        self.message_id = message_id or str(uuid.uuid4())
        self.sender = sender
        self.recipient = recipient
        self.topic = topic
        self.payload = payload
        self.timestamp = timestamp or datetime.now()


class MessageBus:
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}
        self.message_history: List[Message] = []

    def subscribe(self, topic: str, handler: Callable):
        if topic not in self.subscribers:
            self.subscribers[topic] = []
        if handler not in self.subscribers[topic]:
            self.subscribers[topic].append(handler)

    def unsubscribe(self, topic: str, handler: Callable):
        if topic in self.subscribers and handler in self.subscribers[topic]:
            self.subscribers[topic].remove(handler)

    def publish(self, message: Message):
        self.message_history.append(message)

        if message.recipient:
            directed_topic = f"{message.topic}.{message.recipient}"
            if directed_topic in self.subscribers:
                for handler in self.subscribers[directed_topic]:
                    handler(message)

        if message.topic in self.subscribers:
            for handler in self.subscribers[message.topic]:
                handler(message)

    def broadcast(self, topic: str, payload: Dict[str, Any], sender: str):
        message = Message(
            sender=sender,
            recipient="",
            topic=topic,
            payload=payload,
        )
        self.publish(message)

    def get_history(self, topic: str = None) -> List[Message]:
        if topic:
            return [m for m in self.message_history if m.topic == topic]
        return self.message_history
