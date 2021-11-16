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
        state = 'seed'
        while not self.exit_flag:
            logging.info('State: %s', state)
            if state == 'seed':
                if self.killed_counter % 2 == 0:
                    self.use_sword()
                    time.sleep(1)
                    self.hast()
                    time.sleep(2)
                    self.use_tool()
                    time.sleep(1)
                self.squash()
                time.sleep(1)
                state = 'check_target'
            elif state == 'check_target':
                self.targetnext()
                time.sleep(1)
                target_hp = self.get_target_hp()
                if target_hp > 0:
                    for _ in range(5):
                        self.pollen()
                        time.sleep(1)
                    self.target_counter += 1
                    logging.info('target %d found, hp = %d', self.target_counter, target_hp)
                    state = 'kill_target'
            elif state == 'kill_target':
                self.targetnext()
                time.sleep(1)
                logging.info("Killing")
                i = 0
                while self.get_target_hp() > 0:
                    if i % 2 == 0:
                        self.attack()
                    i += 1
                    time.sleep(1)
                time.sleep(1)
                self.killed_counter += 1
                state = 'seed'


if __name__ == '__main__':
    coloredlogs.install(fmt='%(asctime)s %(message)s', datefmt='%H:%M:%S')
    try:
        e = Warrior('../config/pumpkin_seeder.json')
        e.run()
    finally:
        e.stop()
