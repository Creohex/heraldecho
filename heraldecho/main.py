import schedule
import time


if __name__ == "__main__":
    def job():
        print("I'm working...", flush=True)

    schedule.every(2).seconds.do(job)

    while True:
        schedule.run_pending()
        time.sleep(1)
