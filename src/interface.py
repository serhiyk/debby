import logging
import numpy as np
from image import Image, grab_screen


def get_window_info(hwnd, window_info):
    if win32gui.IsWindowVisible(hwnd):
        if '' in win32gui.GetWindowText(hwnd):
            rect = win32gui.GetWindowRect(hwnd)
            window_info['window_start_x'] = rect[0]
            window_info['window_start_y'] = rect[1]
            window_info['window_end_x'] = rect[2]
            window_info['window_end_y'] = rect[3]


class Interface(object):

    def __init__(self):
        super(Interface, self).__init__()
        window_info = {}
        win32gui.EnumWindows(get_window_info, window_info)
        if not window_info:
            raise WindowsError('window is not found')
        self.start_x = window_info['window_start_x']
        self.start_y = window_info['window_start_y']
        self.end_x = window_info['window_end_x']
        self.end_y = window_info['window_end_y']
        self.width = self.end_x - self.start_x
        self.hight = self.end_y - self.start_y
        self.bbox = (self.start_x, self.start_y, self.end_x, self.end_y)
        self.hp_bbox = (self.start_x+16, self.start_y+41, self.start_x+166, self.start_y+42)
        self.img = Image()

    def get_self_hp(self):
        screen_data = grab_screen(self.hp_bbox)
        hp = np.count_nonzero(screen_data == screen_data[0])
        self.self_hp_color = getattr(self, 'self_hp_color', screen_data[0])
        if hp == 150 and self.self_hp_color != screen_data[0]:
            return 0
        return hp * 100 // 150

    def _target_window_location(self):
        bbox = (self.start_x+200, self.start_y, self.start_x+1000, self.start_y+20)
        res = self.img.find_template('border.bmp', bbox)
        if res is None:
            logging.error("target window location is not found")
            return None
        x, y, _, _ = res
        self._target_window_location = lambda: (x, y)
        return self._target_window_location()

    def _target_name_bbox(self):
        res = self._target_window_location()
        if res is None:
            return None
        x = res[0] + 20
        y = res[1] + 8
        self._target_name_bbox = lambda: (x, y, x+150, y+16)
        return self._target_name_bbox()

    def _target_hp_bbox(self):
        res = self._target_window_location()
        if res is None:
            return None
        x = res[0] + 16
        y = res[1] + 28
        self._target_hp_bbox = lambda: (x, y, x+150, y+1)
        return self._target_hp_bbox()

    def get_target_hp(self):
        target_hp_bbox = self._target_hp_bbox()
        if target_hp_bbox is None:
            return 0
        screen_data = grab_screen(target_hp_bbox)
        hp_color = getattr(self, 'target_hp_color', screen_data[0])
        hp = np.count_nonzero(screen_data == hp_color)
        if not hasattr(self, 'target_hp_color'):
            if hp > 10:
                self.target_hp_color = hp_color
            else:
                return 0
        return hp

    def get_login_location(self):
        res = self.img.find_template('login_button.bmp', self.bbox)
        if res is None:
            return None
        x, y, login_button_x, login_button_y = res
        login_x = x + 100
        login_y = y - 44
        password_x = x + 100
        password_y = y - 22
        return login_x, login_y, password_x, password_y, login_button_x, login_button_y

    def get_manor_scroll_down_location(self):
        res = self.img.find_template('window_token.bmp', self.bbox)
        if res is None:
            return None
        bbox = (res[0]+250, res[1]+350, res[0]+310, res[1]+410)
        res = self.img.find_template_center('arrow_down.bmp', bbox)
        if res is None:
            logging.error('manor dialog is not found')
        return res

    def get_manor_phrase(self):
        res = self.img.find_line_center('Tally up indigenous product', [p_violet])
        if res is None:
            logging.error('manor phrase is not found')
        return res

    def get_manor_seed_list(self):
        res = self.img.find_template('seed_name.bmp', self.bbox)
        if res is None:
            logging.error('seed name is not found')
            return None
        bbox = (res[0], res[1], res[0]+140, res[1]+200)
        return self.img.get_multiline([p_white], bbox)

    def get_manor_town_list(self):
        res = self.img.find_template('territory_name.bmp', self.bbox)
        if res is None:
            logging.error('territory name is not found')
            return None
        x, y, _, _ = res
        bbox = (x, y, x+300, y+220)
        res = self.img.find_template('town_choice.bmp', bbox)
        if res is None:
            logging.error('town choice is not found')
            return None
        _, _, town_x, town_y = res
        result = {}
        bbox = (x, y, x+300, y+110)
        for el in self.img.get_multiline([p_white], bbox):
            try:
                town, _, price, prize_type = el['line'].split()
                result[town] = {'price': int(price), 'type': int(prize_type)}
            except (TypeError, ValueError):
                pass
        return result, town_x, town_y

    def get_manor_town(self, town):
        res = self.img.find_template('town_choice.bmp')
        if res is None:
            logging.error('town choice is not found')
            return None
        x, y, _, _ = res
        x -= 12
        bbox = (x, y, x + 100, y + 150)
        res = self.img.find_line_center(town, [p_white], bbox)
        if res is None:
            logging.error('town is not found')
        return res

    def get_agree_button(self):
        return self.img.find_template_center('agree_button.bmp', self.bbox)

    def get_start_button(self):
        return self.img.find_template_center('start_button.bmp', self.bbox)

    def get_manor_set_button(self):
        return self.img.find_template_center('manor_set_button.bmp', self.bbox)

    def get_sell_button(self):
        return self.img.find_template_center('sell_button.bmp', self.bbox)

    def get_accept_button(self):
        return self.img.find_template_center('accept_button.bmp', self.bbox)

    def get_death_button(self):
        return self.img.find_template_center('death_button.bmp', self.bbox)

    def get_resurrection_button(self):
        return self.img.find_template_center('resurrection_button.bmp', self.bbox)
