#!/usr/bin/env python3
import time
import logging
import coloredlogs
from engine import Engine


class Fisherman(Engine):
    fish_counter = 0

    def __init__(self, config):
        super(Fisherman, self).__init__(config)
        if not self.init():
            raise WindowsError('window is not found')

    def run(self):
        time.sleep(5)
        reeling_time = 0
        pumping_time = 0
        state = 'start_fishing'
        while not self.exit_flag:
            logging.info('State: %s', state)
            if state == 'start_fishing':
                time.sleep(3)
                self.fishing()
                time.sleep(5)
                if self.check_fishing_window():
                    state = 'wait_fish'
                else:
                    self.play_sound(3)
                    time.sleep(3)
                    break

            elif state == 'wait_fish':
                time.sleep(0.5)
                if self.check_fishing_window():
                    if self.get_fish_hp():
                        state = 'fishing'
                else:
                    logging.warning('There is no any fish')
                    state = 'check_target'

            elif state == 'fishing':
                start_time = time.time()
                fish_hp = self.get_fish_hp()
                while time.time() - start_time < 1:
                    if self.get_fish_hp() > fish_hp:
                        if time.time() - reeling_time > 2.5:
                            self.reeling()
                            logging.info('reeling')
                            reeling_time = time.time()
                            time.sleep(1)
                        else:
                            logging.info('reeling skipped')
                        break
                    time.sleep(0.1)
                else:
                    if time.time() - pumping_time > 2.5:
                        self.pumping()
                        logging.info('pumping')
                        pumping_time = time.time()
                        time.sleep(1)
                    else:
                        logging.info('pumping skipped')
                if self.get_fish_hp() == 0:
                    state = 'check_target'
                self.shot()

            elif state == 'check_target':
                self.check_chat()
                self.targetnext()
                time.sleep(1)
                if self.get_target_hp() > 0:
                    self.play_sound(3)
                    self.weapon()
                    time.sleep(0.1)
                    self.battle_skill()
                    time.sleep(1)
                    self.attack()
                    while self.get_target_hp() > 0:
                        logging.info('killing')
                        time.sleep(1)
                    time.sleep(12)
                    self.pole()
                    time.sleep(0.1)
                    self.lure()
                state = 'start_fishing'


if __name__ == "__main__":
    coloredlogs.install(fmt='%(asctime)s %(message)s', datefmt='%H:%M:%S')
    try:
        e = Fisherman('../config/test.json')
        e.run()
    finally:
        e.stop()