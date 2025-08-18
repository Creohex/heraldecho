"""Tests for models module."""

import json
import tempfile
import time
from pathlib import Path
from unittest.mock import patch

import pytest

from heraldecho.models import Message, Scheduler, Configuration


class TestMessage:
    def test_message_initialization(self):
        msg = Message("Test message", 1.5)
        assert msg.content == "Test message"
        assert msg.coefficient == 1.5
        assert msg.last_sent == 0.0
        assert msg.send_count == 0

    def test_message_default_coefficient(self):
        msg = Message("Test message")
        assert msg.coefficient == 1.0

    def test_message_identifier_short(self):
        msg = Message("Short")
        assert msg.identifier == "Short"

    def test_message_identifier_long(self):
        msg = Message("This is a very long message that exceeds twenty characters")
        assert msg.identifier == "This is a very long "
        assert len(msg.identifier) == 20

    def test_calculate_priority(self):
        msg = Message("Test", 2.0)
        current_time = 1000.0
        msg.last_sent = 900.0

        with patch('random.uniform', return_value=1.0):
            priority = msg.calculate_priority(current_time)
            expected = (current_time - msg.last_sent) / msg.coefficient
            assert priority == expected

    def test_calculate_priority_with_zero_coefficient(self):
        msg = Message("Test", 0.0)
        current_time = 1000.0
        msg.last_sent = 900.0

        with patch('random.uniform', return_value=1.0):
            priority = msg.calculate_priority(current_time)
            expected = (current_time - msg.last_sent) / 0.1
            assert priority == expected

    def test_mark_sent(self):
        msg = Message("Test")
        current_time = 1000.0

        msg.mark_sent(current_time)

        assert msg.last_sent == current_time
        assert msg.send_count == 1

    def test_to_dict(self):
        msg = Message("Test message", 1.5)
        result = msg.to_dict()

        expected = {
            "content": "Test message",
            "coefficient": 1.5
        }
        assert result == expected


class TestScheduler:
    def test_scheduler_initialization(self):
        messages = [
            {"content": "Message 1", "coefficient": 1.0},
            {"content": "Message 2", "coefficient": 2.0}
        ]

        scheduler = Scheduler("test_scheduler", 3600, "http://webhook.test", messages)

        assert scheduler.name == "test_scheduler"
        assert scheduler.period == 3600
        assert scheduler.webhook == "http://webhook.test"
        assert len(scheduler.messages) == 2
        assert scheduler.messages[0].content == "Message 1"
        assert scheduler.messages[1].coefficient == 2.0

    def test_scheduler_default_coefficient(self):
        messages = [{"content": "Message without coefficient"}]

        scheduler = Scheduler("test_scheduler", 3600, "http://webhook.test", messages)

        assert scheduler.messages[0].coefficient == 1.0

    def test_get_next_message(self):
        messages = [
            {"content": "Message 1", "coefficient": 1.0},
            {"content": "Message 2", "coefficient": 0.5}
        ]

        scheduler = Scheduler("test_scheduler", 3600, "http://webhook.test", messages)

        with patch('time.time', return_value=1000.0):
            message = scheduler.get_next_message()

        assert message is not None
        assert message.send_count == 1
        assert message.last_sent == 1000.0

    def test_get_next_message_empty_queue(self):
        scheduler = Scheduler("test_scheduler", 3600, "http://webhook.test", [])

        message = scheduler.get_next_message()

        assert message is None

    def test_get_message_stats(self):
        messages = [
            {"content": "Message 1", "coefficient": 1.0},
            {"content": "Message 2", "coefficient": 2.0}
        ]

        scheduler = Scheduler("test_scheduler", 3600, "http://webhook.test", messages)

        with patch('time.time', return_value=1000.0):
            scheduler.get_next_message()

        stats = scheduler.get_message_stats()

        assert len(stats) == 2
        assert all("identifier" in stat for stat in stats)
        assert all("content" in stat for stat in stats)
        assert all("coefficient" in stat for stat in stats)
        assert all("send_count" in stat for stat in stats)
        assert all("last_sent" in stat for stat in stats)


class TestConfiguration:
    def test_configuration_initialization(self):
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            config_path = f.name

        try:
            config = Configuration(config_path)
            assert config.conf_path == Path(config_path)
            assert config.schedulers == []
        finally:
            Path(config_path).unlink(missing_ok=True)

    def test_ensure_config_creates_default(self):
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            config_path = f.name

        Path(config_path).unlink()

        try:
            config = Configuration(config_path)
            config.ensure_config()

            assert Path(config_path).exists()

            with open(config_path) as f:
                data = json.load(f)

            assert isinstance(data, list)
            assert len(data) == 1
            scheduler_data = data[0]
            assert "name" in scheduler_data
            assert "period" in scheduler_data
            assert "webhook" in scheduler_data
            assert "messages" in scheduler_data

        finally:
            Path(config_path).unlink(missing_ok=True)

    def test_load_valid_config(self):
        config_data = [
            {
                "name": "test_scheduler",
                "period": 1800,
                "webhook": "http://test.webhook",
                "messages": [
                    {"content": "Test message", "coefficient": 1.5}
                ]
            }
        ]

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            json.dump(config_data, f)
            config_path = f.name

        try:
            config = Configuration(config_path)
            schedulers = config.load()

            assert len(schedulers) == 1
            scheduler = schedulers[0]
            assert scheduler.name == "test_scheduler"
            assert scheduler.period == 1800
            assert scheduler.webhook == "http://test.webhook"
            assert len(scheduler.messages) == 1
            assert scheduler.messages[0].content == "Test message"
            assert scheduler.messages[0].coefficient == 1.5

        finally:
            Path(config_path).unlink(missing_ok=True)

    def test_load_multiple_schedulers(self):
        config_data = [
            {
                "name": "scheduler_1",
                "period": 1800,
                "webhook": "http://webhook1.test",
                "messages": [
                    {"content": "Message 1", "coefficient": 1.0}
                ]
            },
            {
                "name": "scheduler_2",
                "period": 3600,
                "webhook": "http://webhook2.test",
                "messages": [
                    {"content": "Message 2", "coefficient": 2.0}
                ]
            }
        ]

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            json.dump(config_data, f)
            config_path = f.name

        try:
            config = Configuration(config_path)
            schedulers = config.load()

            assert len(schedulers) == 2
            assert schedulers[0].name == "scheduler_1"
            assert schedulers[1].name == "scheduler_2"
            assert schedulers[0].period == 1800
            assert schedulers[1].period == 3600

        finally:
            Path(config_path).unlink(missing_ok=True)

    def test_load_invalid_config_raises_validation_error(self):
        config_data = [
            {
                "period": "invalid",
                "webhook": "http://test.webhook"
            }
        ]

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            json.dump(config_data, f)
            config_path = f.name

        try:
            config = Configuration(config_path)

            with pytest.raises(Exception):
                config.load()

        finally:
            Path(config_path).unlink(missing_ok=True)

    def test_save_config(self):
        messages = [
            {"content": "Message 1", "coefficient": 1.0},
            {"content": "Message 2", "coefficient": 2.0}
        ]

        schedulers = [
            Scheduler("test_scheduler_1", 3600, "http://webhook.test", messages),
            Scheduler("test_scheduler_2", 1800, "http://webhook2.test", messages)
        ]

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            config_path = f.name

        try:
            config = Configuration(config_path)
            config.save(schedulers)

            with open(config_path) as f:
                saved_data = json.load(f)

            assert len(saved_data) == 2
            assert saved_data[0]["name"] == "test_scheduler_1"
            assert saved_data[0]["period"] == 3600
            assert saved_data[0]["webhook"] == "http://webhook.test"
            assert len(saved_data[0]["messages"]) == 2

        finally:
            Path(config_path).unlink(missing_ok=True)
