#!/usr/bin/env python3
import logging
import time
import difflib
from random import randint
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
        state = 'check_target'
        while not self.exit_flag:
            logging.info('State: %s', state)
            if state == 'check_target':
                self.targetnext()
                time.sleep(0.5)
                target_hp = self.get_target_hp()
                if target_hp > 0:
                    self.target_counter += 1
                    logging.info('target %d found, hp = %d', self.target_counter, target_hp)
                    state = 'kill_target'
                else:
                    state = 'search_target'

            elif state == 'kill_target':
                target_name = self.get_target_name()
                if hasattr(self, 'skip_target'):
                    if target_name.startswith(self.skip_target):
                        logging.info("Skip %s", target_name)
                        self.targetnext()
                        time.sleep(0.5)
                        target_name = self.get_target_name()
                logging.info("Killing %s", target_name)
                self.use_battle_skills()
                self.use_pre_skills(target_name)
                i = 0
                while self.get_target_hp() > 0:
                    self.use_battle_skills()
                    self.check_self_hp()
                    if i % 2 == 0:
                        self.attack()
                    i += 1
                    time.sleep(1)
                time.sleep(1)
                self.use_post_skills()
                self.killed_counter += 1
                state = 'check_target'

            elif state == 'search_target':
                if self.target_counter > 0:
                    for _ in range(self.target_counter * 4):
                        self.pickup()
                        time.sleep(0.3)
                    self.target()
                    time.sleep(0.5)
                    self.attack()
                    time.sleep(3)
                    self.target_counter = 0
                    state = 'check_target'
                    continue
                self.check_self_hp()
                location = []
                for target_name, target_location in self.find_targets():
                    if difflib.get_close_matches(target_name, self.config['members']):
                        continue
                    if difflib.get_close_matches(target_name, self.config['mobs']):
                        location = target_location
                    else:
                        logging.info('unknown target %s', target_name)
                        self.play_sound(5)
                if location:
                    location[1] += 100
                    _t = time.time()
                    self.move_to(location)
                    if time.time() - _t > 0.5:
                        state = 'check_target'
                        continue
                    self.click()
                else:
                    x = self.start_x + self.width // 2 + randint(-50, 50)
                    y = self.start_y + self.hight // 2 + randint(-50, 50)
                    self.move_to((x, y))
                    time.sleep(0.1)
                    self.mouse_pres_right()
                    time.sleep(0.1)
                    self.move(randint(-250, -200), 0)
                    time.sleep(0.1)
                    self.mouse_release_right()
                time.sleep(1)
                state = 'check_target'

    def check_self_hp(self):
        hp = self.get_self_hp()
        self.use_hp_skills(hp)
        if hp < 20:
            self.play_sound(3)

    def check_drop(self):
        def _check_drop_thread(parent):
            time.sleep(1)
            for line in parent.get_system_msg_multiline():
                if 'drop' in line:
                    parent.play_sound(5)
        _thread.start_new_thread(_check_drop_thread, (self,))


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        e = Warrior('../config/test.json')
        e.run()
    finally:
        e.stop()
