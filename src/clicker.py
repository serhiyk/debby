#!/usr/bin/env python3
import time
import random
import logging
import coloredlogs
from engine import Engine


class Clicker(Engine):
    def __init__(self):
        super(Clicker, self).__init__('')
        if not self.init():
            raise WindowsError('window is not found')
        self.hp = 100
        self.last_time = 0
        self.click_period = 5

    def run(self):
        time.sleep(5)
        while not self.exit_flag:
            self.check_self_hp()
            self.check_chat()
            self.check_clicker()
            time.sleep(1)

    def check_self_hp(self):
        hp = self.get_self_hp()
        if hp < 50:
            self.play_sound(3)

    def check_clicker(self):
        if time.time() - self.last_time < self.click_period + random.randrange(-10, 10) / 10:
            return
        self.last_time = time.time()

        # self.click()
        self.f11()


if __name__ == '__main__':
    coloredlogs.install(fmt='%(asctime)s %(message)s', datefmt='%H:%M:%S')
    try:
        e = Clicker()
        e.run()
    finally:
        e.stop()
