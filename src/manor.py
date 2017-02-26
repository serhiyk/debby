import time
from datetime import datetime, timedelta
from engine import Engine


class Manor(Engine):
    def __init__(self):
        super(Manor, self).__init__('../config/manor.json')

    def run(self):
        state = "init"
        self.move_to_0()
        manor_config = self.config["manor"]
        manor_list = None
        run_time = datetime.now()
        while not self.exit_flag:
            print("State: {}".format(state))
            if state == "init":
                self.move_to((10, 10))
                self.doubleclick()
                time.sleep(10)
                self.enter()
                time.sleep(10)
                state = "login"

            elif state == "login":
                res = self.get_login_location()
                if res:
                    login_x, login_y, password_x, password_y, login_button_x, login_button_y = res
                    self.move_to((login_x, login_y))
                    self.click()
                    time.sleep(0.5)
                    self.write(self.user)
                    time.sleep(0.5)
                    self.move_to((password_x, password_y))
                    self.click()
                    time.sleep(0.5)
                    self.write(self.password)
                    time.sleep(0.5)
                    self.move_to((login_button_x, login_button_y))
                    self.click()
                    time.sleep(2)
                    state = "rules_window"

            elif state == "rules_window":
                coordinates = self.get_agree_button()
                if coordinates:
                    self.move_to(coordinates)
                    self.click()
                    state = "server_window"

            elif state == "server_window":
                coordinates = self.get_accept_button()
                if coordinates:
                    self.move_to(coordinates)
                    self.click()
                    state = "pers_window"

            elif state == "pers_window":
                coordinates = self.get_start_button()
                if coordinates:
                    self.move_to(coordinates)
                    self.click()
                    state = "game_window"

            elif state == "game_window":
                res = self.get_window_location()
                if res:
                    time.sleep(5)
                    state = "get_time"

            elif state == "get_time":
                run_time = datetime.now()
                second_last = None
                for i in range(15):
                    run_time += timedelta(seconds=10, microseconds=100000)
                    while datetime.now() < run_time:
                        pass
                    time_local = datetime.now()
                    self.server_time()
                    time.sleep(1)
                    s_time = self.get_system_msg()
                    if not s_time.startswith('SVR'):
                        print 'Wrong time:', s_time
                        continue
                    s_time = s_time.split(' ')[-1]
                    _, minute, second = s_time.split(':')
                    second = int(second)
                    minute = int(minute)
                    time_server = time_local.replace(minute=minute, second=second, microsecond=0)
                    time_diff = time_local - time_server
                    print 'Local time: ', time_local
                    print 'Server time:', time_server
                    print 'Diff:', time_diff
                    if second_last is not None:
                        second_up = second_last + 1
                        if second_up >= 60:
                            second_up = 0
                    if second_last is None or second_up != second:
                        second_last = second + 10
                        if second_last >= 60:
                            second_last -= 60
                    else:
                        break
                run_time = datetime.now().replace(minute=6, second=0, microsecond=0) + time_diff + timedelta(microseconds=10000)
                state = "select_target"

            elif state == "select_target":
                self.target()
                time.sleep(0.5)
                res = self.get_target_window_location()
                if res:
                    self.attack()
                    state = "manor_dialog_window"

            elif state == "manor_dialog_window":
                coordinates = self.get_manor_scroll_down_location()
                if coordinates:
                    self.move_to(coordinates)
                    self.click()
                    state = "find_manor_phrase"

            elif state == "find_manor_phrase":
                self.click()
                time.sleep(0.5)
                coordinates = self.get_manor_phrase()
                if coordinates:
                    self.move_to(coordinates)
                    self.click()
                    state = "manor_seed_window"

            elif state == "manor_seed_window":
                manor_list = self.get_manor_seed_list()
                if manor_list:
                    if len(manor_list) == 0:
                        print("There is no any manor")
                    state = "select_manor"

            elif state == "select_manor":
                if len(manor_list) == 0:
                    state = "finish"
                elif manor_list[0]["line"] not in manor_config:
                    print("manor {} skipped".format(manor_list[0]["line"]))
                    del manor_list[0]
                else:
                    self.move_to(manor_list[0]["center"])
                    self.doubleclick()
                    time.sleep(0.1)
                    self.move_to(manor_list[0]["center"])
                    state = "select_manor_town"
                    self.move_to((0, 0))

            elif state == "select_manor_town":
                res = self.get_manor_town_list()
                if res:
                    town_list, x, y = res
                    town_list = {k: v for k, v in town_list.iteritems() if v["type"] == manor_config[manor_list[0]["line"]]["type"]}
                    if len(town_list) == 0:
                        print("There is no any town")
                        del manor_list[0]
                        state = "accept"
                        continue
                    else:
                        if "town" in manor_config[manor_list[0]["line"]]:
                            town = manor_config[manor_list[0]["line"]]["town"]
                            if town not in town_list:
                                print("Town {} is not available".format(town))
                                del manor_list[0]
                                state = "accept"
                                continue
                        else:
                            town = max(town_list, key=lambda i: town_list[i]["price"])
                        if "min_price" in manor_config[manor_list[0]["line"]]:
                            if town_list[town]["price"] < manor_config[manor_list[0]["line"]]["min_price"]:
                                print("Price {} is too low".format(town_list[town]["price"]))
                                del manor_list[0]
                                state = "accept"
                                continue
                        self.move_to((x, y))
                        self.click()
                        coordinates = self.get_manor_town(town)
                        if coordinates:
                            self.move_to(coordinates)
                            self.click()
                            time.sleep(1)
                            coordinates = self.get_manor_set_button()
                            if coordinates:
                                self.move_to(coordinates)
                                self.click()
                                del manor_list[0]
                                state = "accept"
                                continue
                    state = "accept"

            elif state == "accept":
                coordinates = self.get_accept_button()
                if coordinates:
                    self.move_to(coordinates)
                    self.click()
                    state = "select_manor"

            elif state == "finish":
                coordinates = self.get_sell_button()
                if coordinates is None:
                    print("Sell button is not found")
                    break
                self.move_to(coordinates)
                print('Wait to {}'.format(run_time))
                while datetime.now() < run_time:
                    pass
                self.click()
                state = "done"

            elif state == "done":
                break

            time.sleep(0.5)


if __name__ == '__main__':
    time.sleep(5)
    try:
        e = Manor()
        e.run()
    finally:
        e.stop()
