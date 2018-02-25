import json
import logging
from bitarray import bitarray as _bitarray


class bitarray(_bitarray):
    def __hash__(self):
        return id(self)


class OCR(object):
    FONT11 = 'font_11'
    FONT12 = 'font_12'
    fonts = {FONT11: {},
             FONT12: {}}

    def __init__(self):
        super(OCR, self).__init__()
        for font_name, font_data in self.fonts.items():
            with open(font_name + '.json') as f:
                font_json = json.load(f)
            font_data['trie'] = {}
            font_trie = font_data['trie']
            self.font = {}
            font_data['chars'] = {}
            font_chars = font_data['chars']
            for char, data in font_json.items():
                _trie = font_trie
                font_chars[char] = list(map(bitarray, data))
                if char == ' ':
                    continue
                for t in map(list, zip(*data)):
                    c = bitarray(t[t.index(True):len(t) - t[::-1].index(True)])
                    for k in _trie:
                        if k == c:
                            _trie = _trie[k]
                            break
                    else:
                        _trie[c] = {}
                        _trie = _trie[c]
                if 'char' in _trie:
                    logging.info('Same %s %s', char, str(_trie['char']))
                _trie['char'] = char

    def parse_line(self, data, font):
        data = map(bitarray, map(list, zip(*data)))
        text = ''
        counter = 0
        x1 = None
        x2 = None
        char_data = []
        font_trie = self.fonts[font]['trie']
        _trie = font_trie
        for i, col in enumerate(data):
            if True not in col:
                counter += 1
                if char_data:
                    if 'char' in _trie:
                        text += _trie['char']
                        x2 = i
                    else:
                        logging.info('Unknown letter %s', str(char_data))
                char_data = []
                _trie = font_trie
                continue
            if x1 is None:
                x1 = i
            if counter > 3 and text:
                text += ' '
            counter = 0
            char_data.append(col)
            for k, v in _trie.items():
                if k == 'char':
                    continue
                if k.count(True) == col.count(True) and k in col:
                    _trie = v
                    break
            else:
                _trie = {}
        if text:
            return text, x1, x2
        return None

    def parse_multiline(self, data):
        data = map(bitarray, data)
        # data = bitarray(data)

        multiline = []
        line_data = []
        for i, row in enumerate(data):
            if True in row:
                line_data.append(row)
                continue
            if line_data:
                # for t in line_data:
                #     print(t)
                res = self.parse_line(line_data, 'font_11')
                if res:
                    line, x1, x2 = res
                    y = i - len(line_data)
                    multiline.append({'line': line,
                                      'start': [x1, y],
                                      'center': [x1 + (x2 - x1) // 2, y + 4]})
                line_data = []
        return multiline

    def line_to_img(self, line):
        font = self.fonts['font_11']['chars']
        _line_data = [bitarray([]) for _ in range(11)]
        for c in line:
            letter = font[c]
            for i in range(11):
                _line_data[i].extend(letter[i])
                _line_data[i].append(False)
        line_data = []
        for el in _line_data:
            if line_data or True in el:
                line_data.append(el)
        return line_data
