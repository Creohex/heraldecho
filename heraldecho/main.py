#!python3
"""Entrypoint."""

import requests
import schedule
import time
from datetime import datetime
from models import Configuration


def handler(tag, hook, message):
    """Default message emitter."""

    print(f"{str(datetime.now())}: Executing job '{tag}'")
    try:
        requests.post(url=hook, params={}, json={"content": message})
    except Exception as e:
        print(f"Encountered error: {str(e)}")


if __name__ == "__main__":

    Configuration().load()
    schedule.clear()
    for job in Configuration().jobs:
        print(f"Scheduling job: {str(job)}, freq: {job.frequency}")
        schedule.every(job.frequency).hours.do(handler, job.tag, job.hook, job.message)

    print("Running...")
    while True:
        schedule.run_pending()
        time.sleep(1)
