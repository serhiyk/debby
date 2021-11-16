#!/usr/bin/env python3
import time
import logging
import coloredlogs
from engine import Engine


class WarriorAssist(Engine):
    def __init__(self, config):
        super(WarriorAssist, self).__init__(config)
        if not self.init():
            raise WindowsError('window is not found')

    def run(self):
        time.sleep(5)
        state = 'check_assist'
        while not self.exit_flag:
            logging.info('State: %s', state)
            if state == 'check_assist':
                self.check_self_hp()
                self.check_chat()
                self.assist()
                time.sleep(1)
                target_hp = self.get_target_hp()
                if target_hp > 0:
                    logging.info('target found, hp = %d', target_hp)
                    state = 'kill_target'
                else:
                    state = 'goto_home'

            elif state == 'kill_target':
                target_name = self.get_target_name()
                logging.info("Killing %s", target_name)
                self.use_battle_skills()
                self.use_pre_skills(target_name)
                spoiled = False
                i = 0
                while self.get_target_hp() > 0:
                    self.use_battle_skills()
                    self.check_self_hp()
                    self.check_chat()
                    if i % 2 == 0:
                        self.attack()
                    i += 1
                    if self.spoiler and not spoiled:
                        time.sleep(1)
                        if 'Spoil' in ''.join(self.get_success_msg()):
                            spoiled = True
                        else:
                            self.spoil()
                    time.sleep(1)
                time.sleep(1)
                self.use_post_skills()
                state = 'check_assist'

            elif state == 'goto_home':
                self.target()
                time.sleep(0.5)
                self.attack()
                time.sleep(2)
                state = 'check_assist'

    def check_self_hp(self):
        hp = self.get_self_hp()
        self.use_hp_skills(hp)
        if hp < 20:
            self.play_sound(3)


if __name__ == '__main__':
    coloredlogs.install(fmt='%(asctime)s %(message)s', datefmt='%H:%M:%S')
    try:
        e = WarriorAssist('../config/assist.json')
        e.run()
    finally:
        e.stop()
