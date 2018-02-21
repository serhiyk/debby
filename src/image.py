import os
import logging
import numpy as np
import cv2
from mss import mss
from ocr import OCR


class Color(object):
    chat_brown = (176, 153, 121)
    chat_yelow = (255, 251, 0)
    chat_green = (98, 138, 0)
    p_white = (220, 217, 220)
    p_green = (162, 251, 171)
    p_yelow = (250, 250, 145)
    p_violet = (102, 151, 255)
    p_blue = (162, 165, 252)
    target_name = (p_white, p_green, p_yelow, p_blue)


def grab_screen(bbox):
    # sct.monitors[1]
    monitor = {'top': bbox[1], 'left': bbox[0], 'width': bbox[2]-bbox[0], 'height': bbox[3]-bbox[1]}
    with mss() as sct:
        data = sct.grab(monitor)
        data = data.pixels
    return np.array(data, dtype='uint8')


class Image(object):
    template_dir = os.path.join('..', 'templates')

    def __init__(self):
        super(Image, self).__init__()
        self.ocr = OCR()

    def find_template(self, template_name, bbox):
        template_path = os.path.join(self.template_dir, template_name)
        screen = grab_screen(bbox)
        screen = cv2.cvtColor(screen, cv2.COLOR_RGB2GRAY)
        template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
        res = cv2.matchTemplate(screen, template, cv2.TM_CCORR_NORMED)
        threshold = 0.99
        loc = np.where(res >= threshold)
        for x, y in zip(*loc[::-1]):
            x += bbox[0]
            y += bbox[1]
            x_center = x + template.shape[1] // 2
            y_center = y + template.shape[0] // 2
            return x, y, x_center, y_center
        logging.error('%s is not found', template_name)
        return None

    def find_template_center(self, template, bbox):
        res = self.find_template(template, bbox)
        if res is None:
            return None
        return res[2], res[3]

    def find_line(self, line, colour_list, bbox):
        line_data = self.ocr.line_to_img(line)
        line_data = np.array([[255 if p else 0 for p in row] for row in line_data], dtype='uint8')
        screen = grab_screen(bbox)
        screen = np.array([[255 if list(p) in colour_list else 0 for p in row] for row in screen], dtype='uint8')
        res = cv2.matchTemplate(screen, line_data, cv2.TM_CCORR_NORMED)
        threshold = 0.99
        loc = np.where(res >= threshold)
        for x, y in zip(*loc[::-1]):
            x += bbox[0]
            y += bbox[1]
            x_center = x + line_data.shape[1] // 2
            y_center = y + line_data.shape[0] // 2
            return x, y, x_center, y_center

    def find_line_center(self, line, colour_list, bbox):
        res = self.find_line(line, colour_list, bbox)
        if res is None:
            return None
        return res[2], res[3]

    def get_multiline(self, colour_list, bbox):
        # colour_list = np.array(colour_list)
        screen = grab_screen(bbox)
        # screen = np.where(screen in colour_list, 0, 255)
        # screen = np.where(screen in np.array([[0x40, 0x8A, 0xFF],[0x40, 0x8A, 0xFE]]), 0, 255)
        # screen = np.where(screen == [0x40, 0x8A, 0xFF], 0, 255)
        # screen = np.where(np.isin(screen, np.array([[0x40, 0x8A, 0xFF],[0x40, 0x8A, 0xFE]])), 255, 0)
        screen = [[list(p) in colour_list for p in row] for row in screen]
        # screen = [[p in colour_list for p in row] for row in screen]
        # screen = [[np.isin(p, colour_list) for p in row] for row in screen]
        # screen = [[p in [[0x40, 0x8A, 0xFF],[0x40, 0x8A, 0xFE]] for p in row] for row in screen]
        # print(screen)
        multiline = self.ocr.parse_multiline(screen)
        for line in multiline:
            line['start'][0] += bbox[0]
            line['start'][1] += bbox[1]
            line['center'][0] += bbox[0]
            line['center'][1] += bbox[1]
        return multiline

    def find_text(self, bbox):
        screen = grab_screen(bbox)
        screen[screen.shape[0]-310:, :340] = (0, 0, 0)
        screen = cv2.cvtColor(screen, cv2.COLOR_RGB2GRAY)
        _, screen = cv2.threshold(screen, 252, 255, cv2.THRESH_BINARY)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 5))
        _img = cv2.morphologyEx(screen, cv2.MORPH_CLOSE, kernel)
        _, contours, _ = cv2.findContours(_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        text = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            if w > 10 and 6 < h < 13:
                line = self.ocr.parse_line(screen[y:y+h, x-1:x+w], self.ocr.FONT12)
                if line:
                    _x = bbox[0] + x + line[1] + (line[2] - line[1]) // 2
                    _y = bbox[1] + y + h // 2
                    text.append([line[0], [_x, _y]])
        return text
