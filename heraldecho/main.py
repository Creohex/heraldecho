#!python3
"""Entrypoint."""

import requests
import schedule
import time
from datetime import datetime

import constants
from models import Configuration


# FIXME: temporary...
def p(*args, **kwargs):
    print(*args, **kwargs, flush=True)


def handler(tag, hook, message):
    """Default message emitter."""

    p(f"{str(datetime.now())}: Executing job '{tag}'")
    try:
        requests.post(url=hook, params={}, json={"content": message})
    except Exception as e:
        print(f"Encountered error: {str(e)}")


if __name__ == "__main__":

    Configuration().load()
    schedule.clear()

    for job in Configuration().jobs:
        p(f"Scheduling job: {str(job)}, freq: {job.frequency}")
        schedule.every(job.frequency).hours.do(handler, job.tag, job.hook, job.message)

    p("Running...")
    while True:
        schedule.run_pending()
        time.sleep(constants.SCHEDULER_CYCLE_SECONDS)
