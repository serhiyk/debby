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
                font_chars[char] = map(bitarray, data)
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
                    logging.warn('Same %s %s', char, str(_trie['char']))
                _trie['char'] = char

    def parse_line(self, data, font):
        data = map(bitarray, map(list, zip(*data)))
        text = ''
        counter = 0
        char_data = []
        font_trie = self.fonts[font]['trie']
        _trie = font_trie
        for line in data:
            if True not in line:
                counter += 1
                if char_data:
                    if 'char' in _trie:
                        text += _trie['char']
                    else:
                        logging.warn('Unknown letter %s', str(char_data))
                char_data = []
                _trie = font_trie
                continue
            if counter > 3 and text:
                text += ' '
            counter = 0
            char_data.append(line)
            for k, v in _trie.items():
                if k == 'char':
                    continue
                if k.count(True) == line.count(True) and k in line:
                    _trie = v
                    break
            else:
                _trie = {}
        if text != '':
            return text
