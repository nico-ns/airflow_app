from datetime import datetime, timedelta
import json
import atexit
import os
from apscheduler.schedulers.background import BackgroundScheduler
import logging

class CacheChecker:
    def __init__(self, func_to_schedule, interval):

        self.scheduler = BackgroundScheduler()
        self.scheduler.add_job(func=func_to_schedule, trigger="interval", seconds=interval)
        self.scheduler.start()

        atexit.register(lambda: self.scheduler.shutdown())

class Cache(dict):
    def __init__(self,*arg,**kw):
        super(Cache, self).__init__(*arg, **kw)

        self.reset_timer()
        self.BASE_CACHE_PATH = f"{os.getcwd()}/app/cached/"
        # self.TIMEOUT = timedelta(minutes=30)
        self.TIMEOUT = timedelta(seconds=40)


    @property
    def start_time(self):
        return datetime.now()

    def reset_timer(self):
        # print("resetting cache timer")
        self.time = self.start_time

    def reset(self):
        self.clear()
        self.reset_timer()

        return self

    def dump_to_file(self, log_message):
        logging.info(log_message)
        filepath = self.BASE_CACHE_PATH + f"{int(datetime.now().timestamp())}.json"

        with open(filepath, "w") as f:
            json.dump(dict(self), f)

            return self.reset()

    def is_it_time_to_dump(self):
        if self.start_time - self.time > self.TIMEOUT:
            if self:
                msg = "Cache timed-out, dumping to file and resetting timer"
                return self.dump_to_file(msg)
            else:
                logging.info("Cache timed-out, but was empty. Resetting timer")
                self.reset_timer()
        else:
            return self