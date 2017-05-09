import json
from bitarray import bitarray
from PIL import ImageGrab, Image

color_chat_brown = (176, 153, 121)
color_chat_yelow = (255, 251, 0)
color_chat_green = (98, 138, 0)
p_white = (220, 217, 220)
p_green = (162, 251, 171)
p_yelow = (250, 250, 145)
p_violet = (102, 151, 255)
p_blue = (162, 165, 252)
target_name_colours = (p_white, p_green, p_yelow, p_blue)


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
    def __init__(self):
        super(Window, self).__init__()

    def get_button_location(self, template, bbox=None):
        res = find_image(template, bbox)
        if res is None:
            print("{} is not found".format(template.split('/')[-1]))
            return
        _, _, x, y = res
        return x, y

    def get_window_location(self):
        res = find_image("../templates/border.bmp")
        if res is None:
            print("window location is not found")
            return
        x, y, _, _ = res
        self.get_window_location = lambda: (x, y)
        return self.get_window_location()

    def get_self_hp_location(self):
        res = self.get_window_location()
        if res is None:
            return
        x, y = res
        x += 16
        y += 41
        self.get_self_hp_location = lambda: (x, y)
        return self.get_self_hp_location()

    def get_target_window_location(self):
        res = self.get_window_location()
        if res is None:
            return
        x, y = res
        res = find_image("../templates/border.bmp", (x + 200, y, x + 1000, y + 20))
        if res is None:
            print("target window location is not found")
            return
        x, y, _, _ = res
        self.get_target_window_location = lambda: (x, y)
        return self.get_target_window_location()

    def get_target_name_location(self):
        res = self.get_target_window_location()
        if res is None:
            return
        x, y = res
        x += 20
        y += 8
        self.get_target_name_location = lambda: (x, y)
        return self.get_target_name_location()

    def get_target_hp_location(self):
        res = self.get_target_window_location()
        if res is None:
            return
        x, y = res
        x += 16
        y += 28
        self.get_target_hp_location = lambda: (x, y)
        return self.get_target_hp_location()

    def get_login_location(self):
        res = find_image("../templates/login_button.bmp")
        if res is None:
            print("login is not found")
            return
        x, y, login_button_x, login_button_y = res
        login_x = x + 100
        login_y = y - 44
        password_x = x + 100
        password_y = y - 22
        return login_x, login_y, password_x, password_y, login_button_x, login_button_y

    def get_manor_scroll_down_location(self):
        res = find_image("../templates/window_token.bmp")
        if res is None:
            print("manor window is not found")
            return
        x, y, _, _ = res
        res = find_image("../templates/arrow_down.bmp", (x + 250, y + 350, x + 310, y + 410))
        if res is None:
            print("manor dialog is not found")
            return
        _, _, x, y = res
        return x, y

    def get_manor_phrase(self):
        res = self.find_line("Tally up indigenous product", [p_violet])
        if res is None:
            print("manor phrase is not found")
            return
        _, _, x, y = res
        return x, y

    def get_manor_seed_list(self):
        res = find_image("../templates/seed_name.bmp")
        if res is None:
            print("seed name is not found")
            return
        x, y, _, _ = res
        return self.get_multiline([p_white], (x, y, x + 140, y + 200))

    def get_manor_town_list(self):
        res = find_image("../templates/territory_name.bmp")
        if res is None:
            print("territory name is not found")
            return
        x, y, _, _ = res
        res = find_image("../templates/town_choice.bmp", (x, y, x + 300, y + 220))
        if res is None:
            print("town choice is not found")
            return
        _, _, town_x, town_y = res
        result = {}
        for el in self.get_multiline([p_white], (x, y, x + 300, y + 110)):
            try:
                town, _, price, prize_type = el['line'].split()
                result[town] = {'price': int(price), 'type': int(prize_type)}
            except (TypeError, ValueError):
                pass
        return result, town_x, town_y

    def get_manor_town(self, town):
        res = find_image("../templates/town_choice.bmp")
        if res is None:
            print("town choice is not found")
            return
        x, y, _, _ = res
        x -= 12
        res = self.find_line(town, [p_white], (x, y, x + 100, y + 150))
        if res is None:
            print("town is not found")
            return
        _, _, x, y = res
        return x, y

    def get_agree_button(self, bbox=None):
        return self.get_button_location("../templates/agree_button.bmp", bbox)

    def get_start_button(self, bbox=None):
        return self.get_button_location("../templates/start_button.bmp", bbox)

    def get_manor_set_button(self, bbox=None):
        return self.get_button_location("../templates/manor_set_button.bmp", bbox)

    def get_sell_button(self, bbox=None):
        return self.get_button_location("../templates/sell_button.bmp", bbox)

    def get_accept_button(self, bbox=None):
        return self.get_button_location("../templates/accept_button.bmp", bbox)

    def get_death_button(self, bbox=None):
        return self.get_button_location("../templates/death_button.bmp", bbox)

    def get_resurrection_button(self, bbox=None):
        return self.get_button_location("../templates/resurrection_button.bmp", bbox)

    def get_system_msg(self, colour_list=[color_chat_brown]):
        if not hasattr(self, "system_msg_coordinates"):
            try:
                x, y = self.get_window_location()
                x, y, _, _ = find_image("../templates/arrow_down.bmp", (x, y, x + 25, y + 900))
                self.system_msg_coordinates = (x + 15, y - 8, x + 320, y + 8)
            except TypeError:
                print("system message is not found")
                return False
        res = self.get_line(colour_list, self.system_msg_coordinates)
        if res:
            return res[0]
        else:
            return ''

    def get_system_msg_multiline(self, colour_list=[color_chat_brown, color_chat_yelow]):
        if not hasattr(self, "system_msg_multiline_coordinates"):
            try:
                x, y = self.get_window_location()
                x, y, _, _ = find_image("../templates/arrow_down.bmp", (x, y, x + 25, y + 900))
                self.system_msg_multiline_coordinates = (x + 15, y - 100, x + 320, y + 8)
            except TypeError:
                print("system message is not found")
                return False
        res = self.get_multiline(colour_list, self.system_msg_multiline_coordinates)
        if res:
            return [t['line'] for t in res]
        else:
            return []

    def get_self_hp(self):
        res = self.get_self_hp_location()
        if res is None:
            return 0
        x, y = res
        screen = ImageGrab.grab((x, y, x + 150, y + 1))
        screen_data = list(screen.getdata())
        hp = 0
        for pixel in screen_data:
            if pixel == screen_data[0]:
                hp += 1
            else:
                break
        self.self_hp_color = getattr(self, 'self_hp_color', screen_data[0])
        if hp == 150 and self.self_hp_color != screen_data[0]:
            return 0
        return hp * 100 / 150

    def get_target_hp(self):
        res = self.get_target_hp_location()
        if res is None:
            return 0
        x, y = res
        screen = ImageGrab.grab((x, y, x + 150, y + 1))
        screen_data = list(screen.getdata())
        hp_color = getattr(self, 'target_hp_color', screen_data[0])
        hp = 0
        for pixel in screen_data:
            if pixel == hp_color:
                hp += 1
            else:
                break
        if not hasattr(self, "target_hp_color"):
            if hp > 10:
                self.target_hp_color = hp_color
            else:
                return 0
        return hp

    def get_target_name(self, colour_list=target_name_colours):
        res = self.get_target_name_location()
        if res is None:
            return ''
        x, y = res
        res = self.get_line(colour_list, (x, y, x + 150, y + 14))
        if res:
            return res[0]
        else:
            return ''


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
