#!/usr/bin/env python3
import time
import logging
import coloredlogs
import _thread
from engine import Engine


class Support(Engine):
    def __init__(self, config):
        super(Support, self).__init__(config)
        if not self.init():
            raise WindowsError('window is not found')
        self.hp = 100
        _thread.start_new_thread(self.client, ())

    def run(self):
        time.sleep(5)
        state = 'wait_death'
        while not self.exit_flag:
            logging.info('State: %s', state)
            if state == 'wait_death':
                if self.hp < 50:
                    state = 'resurrect'

            elif state == 'resurrect':
                self.click()
                state = 'wait_resurrection'

            elif state == 'wait_resurrection':
                if self.hp > 50:
                    state = 'wait_death'

            time.sleep(1)


if __name__ == '__main__':
    coloredlogs.install(fmt='%(asctime)s %(message)s', datefmt='%H:%M:%S')
    try:
        e = Support(None)
        e.run()
    finally:
        e.stop()
