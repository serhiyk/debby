import time
import serial


class KB(object):
    def __init__(self):
        super(KB, self).__init__()
        self.ser = serial.Serial()
        self.ser.baudrate = 57600
        self.ser.port = 'COM9'
        self.ser.open()

    def click(self):
        self.ser.write(chr(1))
        self.ser.write('c')
        self.ser.write(chr(0))

    def doubleclick(self):
        self.click()
        time.sleep(0.01)
        self.click()
        # self.ser.write(chr(1))
        # self.ser.write('d')
        # self.ser.write(chr(0))

    def move(self, x, y):
        if x < 0:
            x_s = -1
        else:
            x_s = 1
        x *= x_s
        if y < 0:
            y_s = -1
        else:
            y_s = 1
        y *= y_s
        while x > 0 or y > 0:
            if x > 100:
                _x = 100
            else:
                _x = x
            x -= _x
            _x *= x_s
            if _x < 0:
                _x += 256
            if y > 100:
                _y = 100
            else:
                _y = y
            y -= _y
            _y *= y_s
            if _y < 0:
                _y += 256
            self.ser.write(chr(1))
            self.ser.write('m')
            self.ser.write('{:02X}'.format(_x))
            self.ser.write('{:02X}'.format(_y))
            self.ser.write(chr(0))
            time.sleep(0.5)

    def move_to(self, coordinates):
        _x = coordinates[0] - self.current_x
        _y = coordinates[1] - self.current_y
        self.move(_x, _y)
        self.current_x = coordinates[0]
        self.current_y = coordinates[1]

    def move_to_0(self):
        self.move(-1920, -1080)
        self.current_x = 0
        self.current_y = 0

    def send(self, key):
        self.ser.write(chr(1))
        self.ser.write('w')
        self.ser.write(key)
        self.ser.write(chr(0))

    def press(self, key):
        self.ser.write(chr(1))
        self.ser.write('p')
        self.ser.write(key)
        self.ser.write(chr(0))

    def release(self, key):
        self.ser.write(chr(1))
        self.ser.write('r')
        self.ser.write(key)
        self.ser.write(chr(0))

    def write(self, data):
        for c in data:
            self.send('{:02X}'.format(ord(c)))

    def close(self):
        self.ser.close()

    def alt_tab(self):
        self.press('82')
        time.sleep(0.2)
        self.send('B3')
        time.sleep(0.2)
        self.release('82')
        time.sleep(3)

    def enter(self):
        self.send('B0')

    def f1(self):
        self.send('C2')

    def f2(self):
        self.send('C3')

    def f3(self):
        self.send('C4')

    def f4(self):
        self.send('C5')

    def f5(self):
        self.send('C6')

    def f6(self):
        self.send('C7')

    def f7(self):
        self.send('C8')

    def f8(self):
        self.send('C9')

    def f9(self):
        self.send('CA')

    def f10(self):
        self.send('CB')

    def f11(self):
        self.send('CC')

    def f12(self):
        self.send('CD')


if __name__ == '__main__':
    t = KB()
    t.move_to_0()
    t.move_to((500, 500))
    t.click()
    time.sleep(1)
    t.write('hello')
