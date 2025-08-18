"""Models."""

from __future__ import annotations

import json
import jsonschema
import heapq
import random
import time
from pathlib import Path
from typing import List, Dict, Any, Optional


SCHEDULER_CONFIG_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "period": {"type": "number"},
            "webhook": {"type": "string"},
            "messages": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "content": {"type": "string"},
                        "coefficient": {"type": "number", "default": 1.0}
                    },
                    "required": ["content"]
                }
            }
        },
        "required": ["name", "period", "webhook", "messages"]
    }
}


class Message:
    def __init__(self, content: str, coefficient: float = 1.0):
        self.content = content
        self.coefficient = coefficient
        self.last_sent = 0.0
        self.send_count = 0

    @property
    def identifier(self) -> str:
        return self.content[:20] if len(self.content) > 20 else self.content

    def calculate_priority(self, current_time: float) -> float:
        time_since_last = current_time - self.last_sent
        base_priority = time_since_last / max(self.coefficient, 0.1)
        jitter = random.uniform(0.9, 1.1)
        return base_priority * jitter

    def mark_sent(self, current_time: float):
        self.last_sent = current_time
        self.send_count += 1

    def to_dict(self) -> dict:
        return {
            "content": self.content,
            "coefficient": self.coefficient
        }


class Scheduler:
    def __init__(self, name: str, period: float, webhook: str, messages: List[Dict[str, Any]]):
        self.name = name
        self.period = period
        self.webhook = webhook
        self.messages = [
            Message(
                content=msg["content"],
                coefficient=msg.get("coefficient", 1.0)
            )
            for msg in messages
        ]
        self._priority_queue = []
        self._init_priority_queue()

    def _init_priority_queue(self):
        current_time = time.time()
        for i, message in enumerate(self.messages):
            initial_priority = message.calculate_priority(current_time)
            heapq.heappush(self._priority_queue, (-initial_priority, i, message))

    def get_next_message(self) -> Optional[Message]:
        if not self._priority_queue:
            return None

        current_time = time.time()
        priority, index, message = heapq.heappop(self._priority_queue)

        message.mark_sent(current_time)

        new_priority = message.calculate_priority(current_time)
        heapq.heappush(self._priority_queue, (-new_priority, index, message))

        return message

    def get_message_stats(self) -> List[Dict[str, Any]]:
        return [
            {
                "identifier": msg.identifier,
                "content": msg.content,
                "coefficient": msg.coefficient,
                "send_count": msg.send_count,
                "last_sent": msg.last_sent
            }
            for msg in self.messages
        ]


class Configuration:
    """Multiple scheduler configuration manager."""

    def __init__(self, config_path: str = "config.json"):
        self.conf_path = Path(config_path)
        self.schedulers = []

    def ensure_config(self) -> None:
        if not self.conf_path.exists() or not self.conf_path.read_text().strip():
            default_config = [
                {
                    "name": "default_scheduler",
                    "period": 3600,
                    "webhook": "https://example.com/webhook",
                    "messages": [
                        {"content": "Default message", "coefficient": 1.0}
                    ]
                }
            ]
            self.conf_path.write_text(json.dumps(default_config, indent=2))

    def load(self) -> List[Scheduler]:
        self.ensure_config()
        config_data = json.loads(self.conf_path.read_text())
        jsonschema.validate(instance=config_data, schema=SCHEDULER_CONFIG_SCHEMA)

        self.schedulers = [
            Scheduler(
                name=scheduler_config["name"],
                period=scheduler_config["period"],
                webhook=scheduler_config["webhook"],
                messages=scheduler_config["messages"]
            )
            for scheduler_config in config_data
        ]
        return self.schedulers

    def save(self, schedulers: List[Scheduler]) -> None:
        config_data = [
            {
                "name": scheduler.name,
                "period": scheduler.period,
                "webhook": scheduler.webhook,
                "messages": [msg.to_dict() for msg in scheduler.messages]
            }
            for scheduler in schedulers
        ]
        self.conf_path.write_text(
            json.dumps(config_data, indent=2, sort_keys=True),
            encoding="utf-8"
        )
