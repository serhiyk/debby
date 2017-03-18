import json
import time
import socket
import thread
import winsound
from kb import KB
from screen import Window

UDP_PORT = 5005


class State(object):
    check_target = 0
    kill_target = 1
    wait_target = 2
    resurrection = 3
    seed_squash = 4
    pollen = 5


def play_sound_thread(duration, frequency):
    for i in range(duration):
        winsound.Beep(frequency, 500)
        time.sleep(0.5)


class Engine(KB, Window):
    def __init__(self, config):
        super(Engine, self).__init__()
        self.recv_sock = None
        self.send_sock = None
        with open(config) as f:
            self.config = json.load(f)
        self.exit_flag = False
        self.init_variables()
        self.init_general_skills()
        self.init_hp_skills()
        self.init_battle_skills()
        self.init_pre_skills()
        self.init_post_skills()

    def stop(self):
        self.exit_flag = True

    def play_sound(self, duration, frequency=1000):
        thread.start_new_thread(play_sound_thread, (duration, frequency))

    def send_remote(self, **kwargs):
        if self.send_sock is None:
            self.send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.send_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.send_sock.sendto(json.dumps(kwargs), ('255.255.255.255', UDP_PORT))

    def recv_remote(self):
        if self.recv_sock is None:
            self.recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.recv_sock.bind(('0.0.0.0', UDP_PORT))
        data, addr = self.recv_sock.recvfrom(1024)
        return json.loads(data)

    def init_variables(self):
        if 'variables' not in self.config:
            return
        for variable, value in self.config['variables'].iteritems():
            setattr(self, variable, value)

    def init_general_skills(self):
        if 'general_skills' not in self.config:
            return
        for skill, func in self.config['general_skills'].iteritems():
            setattr(self, skill, getattr(self, func))

    def init_hp_skills(self):
        if 'hp_skills' not in self.config:
            self.use_hp_skills = lambda: None
            return
        self.hp_skills = []
        for skill in self.config['hp_skills']:
            _skill = {'name': skill['name']}
            _skill['func'] = getattr(self, skill['func'])
            _skill['hp'] = skill['hp']
            _skill['timeout'] = skill['timeout']
            _skill['wait'] = skill['wait']
            _skill['last_use'] = 0
            self.hp_skills.append(_skill)

    def use_hp_skills(self, hp):
        self.send_remote(hp=hp)
        if hp == 0:
            return
        for skill in self.hp_skills:
            if hp < skill['hp']:
                if time.time() > (skill['timeout'] + skill['last_use']):
                    skill['func']()
                    skill['last_use'] = time.time()
                    time.sleep(skill['wait'])

    def init_battle_skills(self):
        if 'battle_skills' not in self.config:
            self.use_battle_skills = lambda: None
            return
        self.battle_skills = []
        for skill in self.config['battle_skills']:
            _skill = {'name': skill['name']}
            _skill['func'] = getattr(self, skill['func'])
            if 'first_use' in skill and skill['first_use']:
                _skill['last_use'] = 0
            else:
                _skill['last_use'] = time.time()
            _skill['timeout'] = skill['timeout']
            _skill['wait'] = skill['wait']
            self.battle_skills.append(_skill)

    def use_battle_skills(self):
        for skill in self.battle_skills:
            if time.time() > (skill['timeout'] + skill['last_use']):
                skill['func']()
                skill['last_use'] = time.time()
                time.sleep(skill['wait'])

    def init_pre_skills(self):
        if 'pre_skills' not in self.config:
            self.use_pre_skills = lambda: None
            return
        self.pre_skills = []
        for skill in self.config['pre_skills']:
            _skill = {'name': skill['name']}
            _skill['func'] = getattr(self, skill['func'])
            if 'first_use' in skill and skill['first_use']:
                _skill['last_use'] = 0
            else:
                _skill['last_use'] = time.time()
            _skill['skip_target'] = skill.get('skip_target', '')
            _skill['timeout'] = skill['timeout']
            _skill['wait'] = skill['wait']
            self.pre_skills.append(_skill)

    def use_pre_skills(self, target_name=''):
        for skill in self.pre_skills:
            if len(skill['skip_target']) > 0 and target_name.startswith(skill['skip_target']):
                continue
            if time.time() > (skill['timeout'] + skill['last_use']):
                skill['func']()
                skill['last_use'] = time.time()
                time.sleep(skill['wait'])

    def init_post_skills(self):
        if 'post_skills' not in self.config:
            self.use_post_skills = lambda: None
            return
        self.post_skills = []
        for skill in self.config['post_skills']:
            _skill = {'name': skill['name']}
            _skill['func'] = getattr(self, skill['func'])
            _skill['timeout'] = skill['timeout']
            _skill['wait'] = skill['wait']
            _skill['last_use'] = 0
            self.post_skills.append(_skill)

    def use_post_skills(self):
        for skill in self.post_skills:
            if time.time() > (skill['timeout'] + skill['last_use']):
                skill['func']()
                skill['last_use'] = time.time()
                time.sleep(skill['wait'])

    def client(self):
        while not self.exit_flag:
            data = self.recv_remote()
            for key in data:
                setattr(self, key, data[key])
            # func = getattr(self, data)
            # func()


class Engine1(Engine):
    def __init__(self, config):
        super(Engine1, self).__init__(config)

    def suicider(self):
        window = Window()
        state = State.check_target
        while not self.exit_flag:
            if state == State.check_target:
                self.target()
                time.sleep(0.3)
                state = State.kill_target

            elif state == State.kill_target:
                self.use_pre_skills()
                while window.check_death() is False:
                    self.attackforce()
                    time.sleep(1)
                self.use_post_skills()
                state = State.resurrection

            elif state == State.resurrection:
                while window.check_resurrection() is False:
                    time.sleep(1)
                self.click()
                time.sleep(2)
                state = State.check_target

    def halloween(self):
        window = Window()
        feed_counter = 0
        state = State.seed_squash
        while not self.exit_flag:
            if state == State.seed_squash:
                self.use_sword()
                time.sleep(0.3)
                self.use_pre_skills()
                self.use_tool()
                time.sleep(0.3)
                self.squash()
                state = State.check_target

            elif state == State.check_target:
                self.targetnext()
                time.sleep(0.3)
                if window.get_target_hp() > 0:
                    print 'Found next mob'
                    feed_counter = 0
                    state = State.pollen

            elif state == State.pollen:
                self.pollen()
                time.sleep(1)
                feed_counter += 1
                if feed_counter == 5:
                    state = State.wait_target

            elif state == State.wait_target:
                self.targetnext()
                time.sleep(0.3)
                if window.get_target_hp() > 0:
                    print 'Found next mob'
                    self.send_remote('targetnext')
                    time.sleep(0.3)
                    self.send_remote('attack')
                    state = State.kill_target

            elif state == State.kill_target:
                while window.get_target_hp() > 0:
                    self.attack()
                    time.sleep(2)
                time.sleep(1)
                self.use_post_skills()
                state = State.seed_squash


if __name__ == '__main__':
    with open('../config/servus.json') as data_file:
        config = json.load(data_file)
    e = Engine(config, daemon=False)
    try:
        while True:
            time.sleep(1)
    finally:
        e.stop()
