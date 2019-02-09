import logging
import time
import random
import _thread
import queue
import serial
from pymouse import PyMouse


class KB(object):
    def __init__(self):
        super(KB, self).__init__()
        self.q = queue.Queue()
        self.ser = serial.Serial()
        self.ser.baudrate = 57600
        self.ser.port = 'COM9'
        self.ser.timeout = 0.1
        self.ser.open()
        self.running = True
        _thread.start_new_thread(self._read_thread, ())
        self.mouse = PyMouse()

    def close(self):
        self.running = False
        self.ser.close()

    def _read_thread(self):
        data = b''
        while self.running:
            rx_byte = self.ser.read(1)
            if not rx_byte:
                continue
            if rx_byte == b'\x01':
                data = b''
            elif rx_byte == b'\x00':
                self.q.put(data)
            else:
                data += rx_byte

    def _send(self, data):
        with self.q.mutex:
            self.q.queue.clear()
        self.ser.write(b'\x01')
        self.ser.write(data)
        self.ser.write(b'\x00')
        try:
            self.q.get(timeout=10)
        except queue.Empty:
            logging.error('response timeout')

    def write(self, data):
        # self._send(b'w' + data)
        self._send(b'p' + data)
        time.sleep(random.uniform(0.05, 0.15))
        self._send(b'r' + data)
        time.sleep(random.uniform(0.02, 0.1))

    def click(self):
        self._send(b'Cl')

    def doubleclick(self):
        self.click()
        time.sleep(0.01)
        self.click()

    def mouse_pres_right(self):
        self._send(b'Pr')

    def mouse_release_right(self):
        self._send(b'Rr')

    def move(self, x, y):
        if x < 0:
            x += 0x10000
        if y < 0:
            y += 0x10000
        self._send(b'M%04X%04X' % (x, y))

    def move_to(self, position):
        n = 0
        while n < 5:
            n += 1
            cur_position = self.mouse.position()
            if cur_position == position:
                break
            x = position[0] - cur_position[0]
            y = position[1] - cur_position[1]
            self.move(x, y)

    def move_to_0(self):
        self.move(-1920, -1080)

    def rotate(self, x, y):
        self._send(b'Pr')
        self.move(x, y)
        self._send(b'Rr')

    def press(self, key):
        self._send(b'p' + key.encode('utf-8'))

    def release(self, key):
        self._send(b'r' + key.encode('utf-8'))

    def alt_tab(self):
        self.press(b'82')
        time.sleep(0.2)
        self.write(b'B3')
        time.sleep(0.2)
        self.release(b'82')
        time.sleep(3)

    def enter(self):
        self.write(b'B0')

    def f1(self):
        self.write(b'C2')

    def f2(self):
        self.write(b'C3')

    def f3(self):
        self.write(b'C4')

    def f4(self):
        self.write(b'C5')

    def f5(self):
        self.write(b'C6')

    def f6(self):
        self.write(b'C7')

    def f7(self):
        self.write(b'C8')

    def f8(self):
        self.write(b'C9')

    def f9(self):
        self.write(b'CA')

    def f10(self):
        self.write(b'CB')

    def f11(self):
        self.write(b'CC')

    def f12(self):
        self.write(b'CD')

    def write_str(self, data):
        for c in data:
            self.write(b'%02X' % ord(c))
