import json
from bitarray import bitarray
from PIL import ImageGrab, Image

color_chat_brown = (176, 153, 121)
color_chat_yelow = (255, 251, 0)
p_white = (220, 217, 220)
p_green = (162, 251, 171)
p_yelow = (250, 250, 145)
p_violet = (102, 151, 255)
target_name_colours = (p_white, p_green, p_yelow)


class OCR(object):
    def __init__(self):
        super(OCR, self).__init__()
        with open('alphabet.json') as f:
            alphabet = json.load(f)
        self.alphabet_map = {}
        self.alphabet = {}
        for letter, data in alphabet.iteritems():
            _alphabet = self.alphabet_map
            self.alphabet[letter] = map(bitarray, data)
            if letter == ' ':
                continue
            for t in map(list, zip(*data)):
                c = bitarray(t[t.index(True):len(t) - t[::-1].index(True)])
                for k in _alphabet:
                    if k == c:
                        _alphabet = _alphabet[k]
                        break
                else:
                    _alphabet[c] = {}
                    _alphabet = _alphabet[c]
            else:
                if 'key' in _alphabet:
                    print("Warning! {} {}".format(_alphabet['key'], letter))
                _alphabet['key'] = letter

    def parse_line(self, data):
        data = map(bitarray, map(list, zip(*data)))
        line = ''
        counter = 0
        x1 = None
        x2 = None
        letter_data = []
        _alphabet = self.alphabet_map
        for i in xrange(len(data)):
            if True not in data[i]:
                counter += 1
                if len(letter_data) > 0:
                    if 'key' in _alphabet:
                        line += _alphabet['key']
                        x2 = i
                    else:
                        print('Unknown letter: {}'.format(letter_data))
                letter_data = []
                _alphabet = self.alphabet_map
                continue
            if x1 is None:
                x1 = i
            if counter > 3 and len(line) > 0:
                line += ' '
            counter = 0
            letter_data.append(data[i])
            for k, v in _alphabet.iteritems():
                if k == 'key':
                    continue
                if k.count() == data[i].count() and k in data[i]:
                    _alphabet = v
                    break
            else:
                _alphabet = {}
        if line != '':
            return line, x1, x2

    def get_line(self, colour_list, bbox=None):
        screen = ImageGrab.grab(bbox)
        screen_x_len, screen_y_len = screen.size
        data = map(lambda t: t in colour_list, screen.getdata())
        data = [data[i * screen_x_len:i * screen_x_len + screen_x_len] for i in range(screen_y_len)]
        line_y = None
        line_data = []
        for i in xrange(screen_y_len):
            if True in data[i]:
                line_data.append(data[i])
                if line_y is None:
                    line_y = i
            else:
                if line_y is not None:
                    return self.parse_line(line_data)

    def get_multiline(self, colour_list, bbox=None):
        screen = ImageGrab.grab(bbox)
        screen_x_len, screen_y_len = screen.size
        data = map(lambda t: t in colour_list, screen.getdata())
        data = [data[i * screen_x_len:i * screen_x_len + screen_x_len] for i in range(screen_y_len)]
        result = []
        y = None
        line_data = []
        for i in xrange(screen_y_len):
            if True in data[i]:
                line_data.append(data[i])
                if y is None:
                    y = i
            else:
                if y is not None:
                    try:
                        line, x1, x2 = self.parse_line(line_data)
                        if bbox is not None:
                            x1 += bbox[0]
                            x2 += bbox[0]
                            y += bbox[1]
                        result.append({'line': line, 'start': [x1, y], 'center': [x1 + (x2 - x1) / 2, y + 4]})
                    except TypeError:
                        pass
                    y = None
                    line_data = []
        return result

    def find_line(self, line, colour_list, bbox=None):
        screen = ImageGrab.grab(bbox)
        screen_x_len, screen_y_len = screen.size
        data = map(lambda t: t in colour_list, screen.getdata())
        data = [data[i * screen_x_len:i * screen_x_len + screen_x_len] for i in range(screen_y_len)]
        data = map(bitarray, data)
        _line_data = [bitarray([]) for _ in xrange(11)]
        for c in line:
            letter = self.alphabet[c]
            for i in xrange(11):
                _line_data[i].extend(letter[i])
                _line_data[i].append(False)
        line_data = []
        for el in _line_data:
            if len(line_data) > 0 or True in el:
                line_data.append(el)
        for y in xrange(screen_y_len - len(line_data)):
            for x in data[y].search(line_data[0]):
                for i in xrange(1, len(line_data) - 1):
                    if line_data[i] != data[y + i][x:x + len(line_data[i])]:
                        break
                else:
                    if bbox is not None:
                        x += bbox[0]
                        y += bbox[1]
                    return x, y, x + len(line_data[0]) / 2, y + len(line_data) / 2


class Window(OCR):
    def __init__(self, hp_callback=None):
        super(Window, self).__init__()
        self.hp_callback = hp_callback
        self.self_hp_color = None
        self.target_hp_color = None
        self.target_hp_x = None
        self.start_x = None

    def get_button_position(self, template, bbox=None):
        try:
            x, y, _, _ = find_image(template, bbox)
            print("{} found: ({}, {})".format(template.split('/')[-1], x, y))
        except TypeError:
            print("{} is not found".format(template.split('/')[-1]))
            return False
        return x, y

    def get_window_position(self):
        if self.start_x is not None:
            return self.start_x, self.start_y
        try:
            self.start_x, self.start_y, _, _ = find_image("../templates/border.bmp")
        except TypeError:
            return False
        self.self_hp_x = self.start_x + 16
        self.self_hp_y = self.start_y + 41
        return self.start_x, self.start_y

    def get_target_position(self):
        try:
            x, y, _, _ = find_image("../templates/border.bmp", (self.start_x + 200, self.start_y, self.start_x + 1000, self.start_y + 20))
        except TypeError:
            return False
        self.target_hp_x = x + 16
        self.target_hp_y = y + 28
        self.target_name_x = x + 27
        self.target_name_y = y + 10
        return self.target_name_x, self.target_name_y

    def get_login_position(self):
        try:
            x, y, self.login_button_x, self.login_button_y = find_image("../templates/login_button.bmp")
        except TypeError:
            print("login is not found")
            return False
        self.login_x = x + 100
        self.login_y = y - 44
        self.password_x = x + 100
        self.password_y = y - 22
        print("login: ({}, {})".format(self.login_x, self.login_y))
        print("password: ({}, {})".format(self.password_x, self.password_y))
        print("login button: ({}, {})".format(self.login_button_x, self.login_button_y))
        return self.login_x, self.login_y, self.password_x, self.password_y, self.login_button_x, self.login_button_y

    def get_rules_position(self):
        try:
            _, _, self.rules_x, self.rules_y = find_image("../templates/rules_button.bmp", (400, 400, 1280, 800))
        except TypeError:
            print("rules is not found")
            return False
        print("rules: ({}, {})".format(self.rules_x, self.rules_y))
        return self.rules_x, self.rules_y

    def get_server_position(self):
        try:
            _, _, self.server_x, self.server_y = find_image("../templates/server_button.bmp", (400, 300, 1280, 800))
        except TypeError:
            print("server is not found")
            return False
        print("server: ({}, {})".format(self.server_x, self.server_y))
        return self.server_x, self.server_y

    def get_pers_position(self):
        try:
            _, _, self.pers_x, self.pers_y = find_image("../templates/pers_button.bmp", (400, 500, 1280, 1000))
        except TypeError:
            print("pers is not found")
            return False
        print("pers: ({}, {})".format(self.pers_x, self.pers_y))
        return self.pers_x, self.pers_y

    def get_manor_scroll_down_position(self):
        try:
            x, y, _, _ = find_image("../templates/window_token.bmp")
            print("manor dialog: ({}, {})".format(x, y))
            _, _, x, y = find_image("../templates/arrow_down.bmp", (x + 250, y + 350, x + 310, y + 410))
        except TypeError:
            print("manor dialog is not found")
            return False
        print("manor dialog scroll down: ({}, {})".format(x, y))
        return x, y

    def get_manor_phrase(self):
        try:
            _, _, x, y = self.find_line("Tally up indigenous product", [p_violet])
            print("manor phrase: ({}, {})".format(x, y))
        except TypeError:
            print("manor phrase is not found")
            return False
        return x, y

    def get_manor_seed_list(self):
        try:
            x, y, _, _ = find_image("../templates/seed_name.bmp")
            print("seed name: ({}, {})".format(x, y))
        except TypeError:
            print("seed name is not found")
            return False
        return self.get_multiline([p_white], (x, y, x + 140, y + 200))

    def get_manor_town_list(self):
        try:
            x, y, _, _ = find_image("../templates/territory_name.bmp")
            print("territory name: ({}, {})".format(x, y))
            _, _, town_x, town_y = find_image("../templates/town_choice.bmp", (x, y, x + 300, y + 220))
            print("town choice: ({}, {})".format(town_x, town_y))
        except TypeError:
            print("territory name is not found")
            return False
        result = {}
        for el in self.get_multiline([p_white], (x, y, x + 300, y + 110)):
            try:
                town, _, price, prize_type = el['line'].split()
                result[town] = {'price': int(price), 'type': int(prize_type)}
            except (TypeError, ValueError):
                pass
        return result, town_x, town_y

    def get_manor_town(self, town):
        try:
            x, y, _, _ = find_image("../templates/town_choice.bmp")
            x -= 12
            print("town choice: ({}, {})".format(x, y))
            _, _, x, y = self.find_line(town, [p_white], (x, y, x + 100, y + 150))
            print("town {}: ({}, {})".format(town, x, y))
        except TypeError:
            print("town is not found")
            return False
        return x, y

    def get_agree_button(self, bbox=None):
        return self.get_button_position("../templates/agree_button.bmp", bbox)

    def get_start_button(self, bbox=None):
        return self.get_button_position("../templates/start_button.bmp", bbox)

    def get_manor_set_button(self, bbox=None):
        return self.get_button_position("../templates/manor_set_button.bmp", bbox)

    def get_sell_button(self, bbox=None):
        return self.get_button_position("../templates/sell_button.bmp", bbox)

    def get_accept_button(self, bbox=None):
        return self.get_button_position("../templates/accept_button.bmp", bbox)

    def get_system_msg(self, colour_list=[color_chat_brown]):
        if not hasattr(self, "system_msg_coordinates"):
            try:
                x, y = self.get_window_position()
                x, y, _, _ = find_image("../templates/arrow_down.bmp", (x, y, x + 25, y + 900))
                self.system_msg_coordinates = (x + 15, y - 8, x + 320, y + 8)
                print self.system_msg_coordinates
            except TypeError:
                print("system message is not found")
                return False
        res = self.get_line(colour_list, self.system_msg_coordinates)
        if res:
            return res[0]
        else:
            return ''

    def get_self_hp(self):
        screen = ImageGrab.grab((self.self_hp_x, self.self_hp_y, self.self_hp_x + 150, self.self_hp_y + 1))
        screen_data = list(screen.getdata())
        if self.self_hp_color is None:
            self.self_hp_color = screen_data[0]
        hp = 0
        for pixel in screen_data:
            if pixel == self.self_hp_color:
                hp += 1
            else:
                break
        return hp * 100 / 150

    def get_target_hp(self):
        if self.target_hp_x is None:
            if self.get_target_position() is False:
                return 0
        screen = ImageGrab.grab((self.target_hp_x, self.target_hp_y, self.target_hp_x + 150, self.target_hp_y + 1))
        screen_data = list(screen.getdata())
        if self.target_hp_color is None:
            target_hp_color = screen_data[0]
        else:
            target_hp_color = self.target_hp_color
        hp = 0
        for pixel in screen_data:
            if pixel == target_hp_color:
                hp += 1
            else:
                break
        if self.target_hp_color is None:
            if hp > 10:
                self.target_hp_color = target_hp_color
            else:
                return 0
        return hp

    def check_target_name(self, name):
        screen = ImageGrab.grab((self.target_name_x, self.target_name_y, self.target_name_x + 100, self.target_name_y + 10))
        target_name_data = list(screen.getdata())
        for i in xrange(len(target_name_data)):
            if target_name_data[i] in target_name_colours:
                target_name_data[i] = 1
            else:
                target_name_data[i] = 0
        width, height = screen.size
        data = [target_name_data[i * width:(i + 1) * width] for i in xrange(height)]

        def check_equal(lst):
            for el in lst:
                if el != 0:
                    return True
            return False
        data = [x for x in data if check_equal(x)]
        data = zip(*data)
        i = 0
        n = 0

        def sublistExists(list1, list2):
            return ''.join(map(str, list2)) in ''.join(map(str, list1))
        while True:
            if i >= len(data):
                break
            if check_equal(data[i]):
                matrix = m[name[n]]
                for t in range(len(matrix)):
                    if not sublistExists(data[i + t], matrix[t]):
                        return False
                i += len(matrix)
                n += 1
                if n >= len(name):
                    return True
            i += 1
        return False

    def check_death(self):
        try:
            self.death_x, self.death_y, _, _ = find_image("../templates/death_button.bmp", (self.start_x, self.start_y, self.start_x + 1000, self.start_y + 600))
        except TypeError:
            return False
        self.check_death = self._check_death
        return True

    def _check_death(self):
        try:
            _, _, _, _ = find_image("../templates/death_button.bmp", (self.death_x, self.death_y, self.death_x + 12, self.death_y + 8))
        except TypeError:
            return False
        return True

    def check_resurrection(self):
        try:
            self.resurrection_x, self.resurrection_y, _, _ = find_image("../templates/resurrection_button.bmp", (self.start_x, self.start_y, self.start_x + 1000, self.start_y + 600))
        except TypeError:
            return False
        self.check_resurrection = self._check_resurrection
        return True

    def _check_resurrection(self):
        try:
            _, _, _, _ = find_image("../templates/resurrection_button.bmp", (self.resurrection_x, self.resurrection_y, self.resurrection_x + 12, self.resurrection_y + 10))
        except TypeError:
            return False
        return True


def find_image(image, bbox=None):
    screen = ImageGrab.grab(bbox)
    image = Image.open(image)
    screen_x_len, screen_y_len = screen.size
    image_x_len, image_y_len = image.size
    screen_data = list(screen.getdata())
    image_data = list(image.getdata())

    def cmp(x, y):
        for _y in xrange(image_y_len):
            image_offset = (y + _y) * screen_x_len + x
            subimage_offset = _y * image_x_len
            for _x in xrange(image_x_len):
                if screen_data[image_offset + _x] != image_data[subimage_offset + _x]:
                    return False
        return True

    for y in xrange(screen_y_len - image_y_len + 1):
        for x in xrange(screen_x_len - image_x_len + 1):
            if cmp(x, y) is True:
                if bbox is not None:
                    x += bbox[0]
                    y += bbox[1]
                return x, y, x + image_x_len / 2, y + image_y_len / 2


if __name__ == '__main__':
    import timeit
    print(timeit.timeit("print Window().get_system_msg()", setup="from __main__ import Window, p_white", number=1))
