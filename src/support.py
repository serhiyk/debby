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
        while not self.exit_flag:
            self.use_hp_skills(self.hp)
            self.use_post_skills()
            self.check_self_hp()
            self.check_chat()
            time.sleep(1)

    def check_self_hp(self):
        hp = self.get_self_hp()
        if hp < 50:
            self.play_sound(3)


if __name__ == '__main__':
    coloredlogs.install(fmt='%(asctime)s %(message)s', datefmt='%H:%M:%S')
    try:
        e = Support('../config/test.json')
        e.run()
    finally:
        e.stop()
