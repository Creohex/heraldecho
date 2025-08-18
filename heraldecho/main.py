#!python3
"""Entrypoint."""

import requests
import time
from datetime import datetime

from . import constants
from .models import Configuration


def p(*args, **kwargs):
    print(*args, **kwargs, flush=True)


def send_message(webhook: str, content: str, identifier: str, scheduler_name: str):
    """Send message to webhook."""
    p(f"{str(datetime.now())}: [{scheduler_name}] Sending message '{identifier}'")
    try:
        response = requests.post(
            url=webhook,
            params={},
            json={"content": content},
            timeout=30
        )
        if response.status_code == 200:
            p(f"[{scheduler_name}] Message sent successfully: {identifier}")
        else:
            p(f"[{scheduler_name}] Warning: HTTP {response.status_code} for message: {identifier}")
    except Exception as e:
        p(f"[{scheduler_name}] Error sending message '{identifier}': {str(e)}")


if __name__ == "__main__":
    p("Initializing Herald Echo multi-scheduler...")

    config = Configuration()
    schedulers = config.load()

    p(f"Loaded {len(schedulers)} scheduler(s):")
    for scheduler in schedulers:
        p(f"  - '{scheduler.name}': period={scheduler.period}s, messages={len(scheduler.messages)}")
        for msg in scheduler.messages:
            p(f"    * '{msg.identifier}' (coefficient: {msg.coefficient})")

    # Track last dispatch time for each scheduler
    last_dispatches = {scheduler.name: 0 for scheduler in schedulers}
    p("Starting multi-scheduler dispatch loop...")

    while True:
        current_time = time.time()

        # Check each scheduler independently
        for scheduler in schedulers:
            if current_time - last_dispatches[scheduler.name] >= scheduler.period:
                message = scheduler.get_next_message()
                if message:
                    send_message(
                        scheduler.webhook,
                        message.content,
                        message.identifier,
                        scheduler.name
                    )
                    last_dispatches[scheduler.name] = current_time
                else:
                    p(f"[{scheduler.name}] Warning: No messages available to send")

        time.sleep(constants.SCHEDULER_CYCLE_SECONDS)
