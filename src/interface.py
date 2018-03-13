import logging
import numpy as np
import win32gui
from image import Image, grab_screen, save_screen, Color


def get_window_info(hwnd, window_info):
    if win32gui.IsWindowVisible(hwnd):
        if 'Lineage' in win32gui.GetWindowText(hwnd):
            rect = win32gui.GetWindowRect(hwnd)
            window_info['window_start_x'] = rect[0]
            window_info['window_start_y'] = rect[1]
            window_info['window_end_x'] = rect[2]
            window_info['window_end_y'] = rect[3]


class Interface(object):
    chat = []
    fishing_bbox = None
    fishing_color = None

    def __init__(self):
        super(Interface, self).__init__()
        self.img = Image()

    def init(self, correct=True):
        window_info = {}
        win32gui.EnumWindows(get_window_info, window_info)
        if not window_info:
            return False
        self.start_x = window_info['window_start_x']
        self.start_y = window_info['window_start_y']
        self.end_x = window_info['window_end_x']
        self.end_y = window_info['window_end_y']
        if correct:
            bbox = (self.start_x, self.start_y, self.start_x+100, self.start_y+100)
            res = self.img.find_template('border.bmp', bbox)
            if res is None:
                return False
            self.start_x = res[0]
            self.start_y = res[1]
        self.width = self.end_x - self.start_x
        self.hight = self.end_y - self.start_y
        self.bbox = (self.start_x, self.start_y, self.end_x, self.end_y)
        self.hp_bbox = (self.start_x+16, self.start_y+52, self.start_x+166, self.start_y+53)
        self.sys_msg_bbox = (self.start_x+20, self.end_y-222, self.start_x+350, self.end_y-200)
        self.sys_mmsg_bbox = (self.start_x+20, self.end_y-320, self.start_x+350, self.end_y-200)
        self.chat_bbox = (self.start_x+20, self.end_y-190, self.start_x+350, self.end_y-60)
        return True

    def get_self_hp(self):
        screen_data = grab_screen(self.hp_bbox)[0]
        hp = 0
        for p in screen_data:
            if (p == screen_data[0]).all():
                hp += 1
            else:
                break
        self.self_hp_color = getattr(self, 'self_hp_color', screen_data[0])
        if hp == 150 and (self.self_hp_color != screen_data[0]).any():
            return 0
        return hp * 100 // 150

    def get_target_window_location(self):
        bbox = (self.start_x+200, self.start_y, self.start_x+1000, self.start_y+20)
        res = self.img.find_template('border.bmp', bbox)
        if res is None:
            logging.error("target window location is not found")
            return None
        x, y, _, _ = res
        self.get_target_window_location = lambda: (x, y)
        return self.get_target_window_location()

    def _target_name_bbox(self):
        res = self.get_target_window_location()
        if res is None:
            return None
        x = res[0] + 20
        y = res[1] + 8
        self._target_name_bbox = lambda: (x, y, x+150, y+16)
        return self._target_name_bbox()

    def _target_hp_bbox(self):
        res = self.get_target_window_location()
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
        screen_data = grab_screen(target_hp_bbox)[0]
        hp_color = getattr(self, 'target_hp_color', screen_data[0])
        hp = 0
        for p in screen_data:
            if (p == hp_color).all():
                hp += 1
            else:
                break
        if not hasattr(self, 'target_hp_color'):
            if hp > 10:
                logging.info("Target HP color: %s", hp_color)
                self.target_hp_color = hp_color
            else:
                return 0
        return hp

    def get_target_name(self, color_list=Color.target_name):
        bbox = self._target_name_bbox()
        if bbox is None:
            return ''
        res = self.img.get_multiline(color_list, bbox)
        if res:
            return res[0]['line']
        else:
            return ''

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
        res = self.img.find_line_center('Tally up indigenous product', [Color.p_violet], self.bbox)
        if res is None:
            logging.error('manor phrase is not found')
        return res

    def get_manor_seed_list(self):
        res = self.img.find_template('seed_name.bmp', self.bbox)
        if res is None:
            logging.error('seed name is not found')
            return None
        bbox = (res[0], res[1], res[0]+140, res[1]+200)
        return self.img.get_multiline([Color.p_white], bbox)

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
        for el in self.img.get_multiline([Color.p_white], bbox):
            try:
                town, _, price, prize_type = el['line'].split()
                result[town] = {'price': int(price), 'type': int(prize_type)}
            except (TypeError, ValueError):
                pass
        return result, town_x, town_y

    def get_manor_town(self, town):
        res = self.img.find_template('town_choice.bmp', self.bbox)
        if res is None:
            logging.error('town choice is not found')
            return None
        x, y, _, _ = res
        x -= 12
        bbox = (x, y, x + 100, y + 150)
        res = self.img.find_line_center(town, [Color.p_white], bbox)
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

    def get_system_msg(self):
        color_list = [Color.sys_msg]
        res = self.img.get_multiline(color_list, self.sys_msg_bbox)
        if res:
            return res[0]['line']
        else:
            return ''

    def get_system_msg_multiline(self):
        color_list = [Color.sys_msg, Color.sys_drop]
        res = self.img.get_multiline(color_list, self.sys_mmsg_bbox)
        if res:
            return [t['line'] for t in res]
        else:
            return []

    def get_success_msg(self):
        color_list = [Color.sys_success]
        res = self.img.get_multiline(color_list, self.sys_mmsg_bbox)
        if res:
            return [t['line'] for t in res]
        else:
            return []

    def get_chat(self):
        color_list = [Color.chat_general, Color.chat_hero, Color.chat_trade, Color.chat_shout]
        res = self.img.get_multiline(color_list, self.chat_bbox)
        if not res:
            return []
        chat = [t['line'] for t in res]
        if len(chat) > len(self.chat):
            chat = chat[len(self.chat):]
        else:
            for i in range(len(chat)):
                if self.chat[-len(chat)+i:] == chat[:len(chat)-i]:
                    chat = chat[len(chat)-i:]
                    break
        self.chat.extend(chat)
        return chat

    def find_targets(self):
        bbox = list(self.bbox)
        bbox[3] -= 310
        return self.img.find_text(bbox)

    def save_screen(self, file_path):
        save_screen(file_path, self.bbox)

    def check_fishing_window(self):
        res = self.img.find_template('window_token.bmp', self.bbox)
        if res is None:
            return False
        if not self.fishing_bbox:
            self.fishing_bbox = [res[0]+12, res[1]+240, res[0]+242, res[1]+241]
        return True

    def get_fish_hp(self):
        screen_data = grab_screen(self.fishing_bbox)[0]
        if self.fishing_color is None:
            for p in screen_data[:10]:
                if not (p == screen_data[0]).all():
                    logging.warning('fish hp is not found')
                    return None
            self.fishing_color = screen_data[0]
        hp = 0
        for p in screen_data:
            if (p == self.fishing_color).all():
                hp += 1
            else:
                break
        return hp
