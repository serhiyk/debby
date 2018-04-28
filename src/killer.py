#!/usr/bin/env python3
import time
import logging
import coloredlogs
from engine import Engine


class Warrior(Engine):
    def __init__(self, config):
        super(Warrior, self).__init__(config)
        if not self.init():
            raise WindowsError('window is not found')

    def run(self):
        time.sleep(5)
        state = 'check_target'
        while not self.exit_flag:
            logging.info('State: %s', state)
            if state == 'check_target':
                self.target()
                state = 'kill_target'

            elif state == 'kill_target':
                if self.get_death_button():
                    self.move(-100, -100)
                    state = 'resurrection'
                else:
                    self.send_remote(hp=99)
                    self.attackforce()

            elif state == 'resurrection':
                coordinates = self.get_resurrection_button()
                if coordinates:
                    self.move_to(coordinates)
                    self.click()
                    time.sleep(2)
                    state = 'check_target'
                else:
                    self.send_remote(hp=1)

            time.sleep(1)


if __name__ == '__main__':
    coloredlogs.install(fmt='%(asctime)s %(message)s', datefmt='%H:%M:%S')
    try:
        e = Warrior('../config/killer.json')
        e.run()
    finally:
        e.stop()
