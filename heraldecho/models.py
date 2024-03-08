"""Models."""

from __future__ import annotations

import json
import jsonschema
from pathlib import Path


SCHEMA_DEFAULT = {
    "type": "object",
    "properties": {
        "hook": {"type": "string"},
        "message": {"type": "string"},
        "frequency": {"type": "number"},
        "tag": {"type": "string"},
    },
}
"""Job serialization format."""


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Configuration(metaclass=Singleton):
    """Jobs collection."""

    conf_path = Path.cwd() / "config.json"
    jobs = None

    @classmethod
    def ensure_config(cls) -> None:
        cls.conf_path.read_text
        if not cls.conf_path.exists() or not cls.conf_path.read_text():
            cls.conf_path.write_text("[]")

    @classmethod
    def load(cls) -> list[Job]:
        cls.ensure_config()
        cls.jobs = set(map(Job, json.loads(cls.conf_path.read_text())))

    @classmethod
    def save(cls) -> None:
        cls.ensure_config()
        existing = set(map(Job, json.loads(cls.conf_path.read_text())))
        cls.conf_path.write_text(
            json.dumps(
                [j.to_json() for j in sorted(existing | cls.jobs, key=lambda j: j.hook)],
                sort_keys=True,
                indent=2,
            ),
            encoding="utf-8",
        )


class Job:
    """Represents a reccurent message emitter."""

    def __init__(self, data: dict = None) -> None:
        jsonschema.validate(instance=data, schema=SCHEMA_DEFAULT)
        self.hook = data["hook"]
        self.message = data["message"]
        self.frequency = data["frequency"]
        self.tag = data["tag"]
        self._validate()

    def _validate(self) -> None: ...

    def __hash__(self) -> str:
        return hash("_".join(map(str, (self.hook, self.message, self.frequency))))

    def __eq__(self, other) -> bool:
        return isinstance(other, Job) and self.__hash__() == other.__hash__()

    def __repr__(self) -> str:
        return self.tag

    def to_json(self) -> dict:
        return {
            "hook": self.hook,
            "message": self.message,
            "frequency": self.frequency,
            "tag": self.tag,
        }
