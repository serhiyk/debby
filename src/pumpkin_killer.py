#!/usr/bin/env python3
import time
import logging
import difflib
from random import randint
import coloredlogs
import _thread
from engine import Engine


class Warrior(Engine):
    def __init__(self, config):
        super(Warrior, self).__init__(config)
        if not self.init():
            raise WindowsError('window is not found')

    def run(self):
        time.sleep(5)
        self.target_counter = 0
        self.killed_counter = 0
        state = 'kill_target'
        while not self.exit_flag:
            logging.info('State: %s', state)
            if state == 'kill_target':
                self.targetnext()
                time.sleep(1)
                logging.info(f"Killing {self.killed_counter}")
                i = 0
                while self.get_target_hp() > 0:
                    if i % 2 == 0:
                        self.attack()
                    i += 1
                    time.sleep(1)
                time.sleep(1)
                self.killed_counter += 1
                state = 'kill_target'


if __name__ == '__main__':
    coloredlogs.install(fmt='%(asctime)s %(message)s', datefmt='%H:%M:%S')
    try:
        e = Warrior('../config/pumpkin_killer.json')
        e.run()
    finally:
        e.stop()
