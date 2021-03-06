#!/usr/bin/env python3
import time
from datetime import datetime, timedelta
import logging
import coloredlogs
from engine import Engine


class Manor(Engine):
    def __init__(self):
        super(Manor, self).__init__('../config/manor.json')
        if not self.init():
            raise WindowsError('window is not found')

    def run(self):
        run_time = datetime.now()
        second_last = None
        for _ in range(15):
            run_time += timedelta(seconds=10, microseconds=100000)
            while datetime.now() < run_time:
                pass
            time_local = datetime.now()
            self.server_time()
            time.sleep(1)
            s_time = self.get_system_msg()
            if not s_time.startswith('SVR'):
                logging.warning('Wrong time: %s', s_time)
                continue
            s_time = s_time.split(' ')[-1]
            _, minute, second = s_time.split(':')
            second = int(second)
            minute = int(minute)
            time_server = time_local.replace(minute=minute, second=second, microsecond=0)
            time_diff = time_local - time_server
            logging.info('Local time: %s', time_local)
            logging.info('Server time: %s', time_server)
            logging.info('Diff: %s', time_diff)
            if second_last is not None:
                second_up = second_last + 1
                if second_up >= 60:
                    second_up = 0
            if second_last is None or second_up != second:
                second_last = second + 10
                if second_last >= 60:
                    second_last -= 60
            else:
                break
        run_time = datetime.now().replace(minute=6, second=0, microsecond=0) + time_diff + timedelta(microseconds=10000)

        logging.info('Wait to %s', run_time)
        while datetime.now() < run_time:
            pass
        self.click()
        time.sleep(0.02)
        self.click()


if __name__ == '__main__':
    coloredlogs.install(fmt='%(asctime)s %(message)s', datefmt='%H:%M:%S')
    time.sleep(5)
    try:
        e = Manor()
        e.run()
    finally:
        e.stop()
