import time
import thread
from engine import Engine


class Support(Engine):
    def __init__(self, config):
        super(Support, self).__init__(config)
        self.hp = 100
        thread.start_new_thread(self.client, ())

    def run(self):
        time.sleep(5)
        while not self.exit_flag:
            self.use_hp_skills(self.hp)
            self.use_post_skills()
            self.check_self_hp()
            time.sleep(0.5)

    def check_self_hp(self):
        hp = self.get_self_hp()
        if hp < 50:
            self.play_sound(3)


if __name__ == '__main__':
    try:
        e = Support('../config/test.json')
        e.run()
    finally:
        e.stop()
