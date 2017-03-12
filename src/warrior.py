import time
from engine import Engine


class Warrior(Engine):
    def __init__(self, config):
        super(Warrior, self).__init__(config)

    def run(self):
        time.sleep(5)
        self.target_counter = 0
        self.killed_counter = 0
        state = "check_target"
        while not self.exit_flag:
            print("State: {}".format(state))
            if state == "check_target":
                self.targetnext()
                time.sleep(0.5)
                if self.get_target_hp() > 0:
                    self.target_counter += 1
                    print("target found: {}".format(self.target_counter))
                    state = "kill_target"
                else:
                    state = "wait_target"

            elif state == "kill_target":
                target_name = self.get_target_name()
                if hasattr(self, 'skip_target'):
                    if target_name.startswith(self.skip_target):
                        self.targetnext()
                        time.sleep(0.5)
                        target_name = self.get_target_name()
                self.use_pre_skills(target_name)
                i = 0
                while self.get_target_hp() > 0:
                    if i % 2 == 0:
                        self.attack()
                    i += 1
                    self.check_self_hp()
                    time.sleep(1)
                time.sleep(1)
                self.use_post_skills()
                self.killed_counter += 1
                state = "check_target"

            elif state == "wait_target":
                if self.target_counter > 0:
                    for i in xrange(self.target_counter * 4):
                        self.pickup()
                        time.sleep(0.3)
                    self.target()
                    time.sleep(0.5)
                    self.attack()
                    self.target_counter = 0
                self.check_self_hp()
                time.sleep(1)
                state = "check_target"

    def check_self_hp(self):
        hp = self.get_self_hp()
        self.use_hp_skills(hp)


if __name__ == '__main__':
    try:
        e = Warrior('../config/test.json')
        e.run()
    finally:
        e.stop()
