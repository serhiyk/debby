#!/usr/bin/python
import sys
import os
import json
import time
import thread
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import SIGNAL
from warrior import Warrior
from support import Support


class Debby(QtGui.QWidget):
    def __init__(self):
        super(Debby, self).__init__()
        self.last_battle_time = None
        self.config = {}
        self.config_file = os.path.join(os.path.expanduser('~'), 'debby.json')
        if os.path.isfile(self.config_file):
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Debby')
        self.setStyleSheet("QLabel { font-size: 36pt; }")
        self.main_layout = QtGui.QVBoxLayout(self)
        self.config_list = QtGui.QComboBox(self)
        for f in os.listdir(os.path.join('..', 'config')):
            if f.endswith('.json'):
                self.config_list.addItem(f)
        cur_config = self.config.get('config')
        if cur_config:
            index = self.config_list.findText(cur_config)
            if index > 0:
                self.config_list.setCurrentIndex(index)
        self.connect(self.config_list, QtCore.SIGNAL('currentIndexChanged(const QString&)'), self.change_config)
        self.main_layout.addWidget(self.config_list)
        self.run_button = QtGui.QPushButton('Run', self)
        self.connect(self.run_button, SIGNAL('clicked()'), self.run_button_handler)
        self.main_layout.addWidget(self.run_button)
        self.hpbar = QtGui.QProgressBar(self)
        self.hpbar.setMinimum(0)
        self.hpbar.setMaximum(100)
        self.hpbar.setHidden(True)
        self.connect(self.hpbar, SIGNAL('update_hp_signal'), self.hpbar.setValue)
        self.main_layout.addWidget(self.hpbar)
        self.killed_counter_label = QtGui.QLabel(self)
        self.killed_counter_label.setHidden(True)
        self.connect(self.killed_counter_label, SIGNAL('update_killed_counter_signal'), self.killed_counter_label.setText)
        self.main_layout.addWidget(self.killed_counter_label)
        self.target_counter_label = QtGui.QLabel(self)
        self.target_counter_label.setHidden(True)
        self.connect(self.target_counter_label, SIGNAL('update_target_counter_signal'), self.target_counter_label.setText)
        self.main_layout.addWidget(self.target_counter_label)
        self.setLayout(self.main_layout)
        self.move(0, 100)
        self.show()

    def change_config(self):
        self.config['config'] = str(self.config_list.currentText())
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f)
        print self.config_list.currentText()

    def run_button_handler(self):
        def setter(obj, name, value):
            obj.__dict__[name] = value
            self.attr_watcher(name, value)
        deb_file = os.path.join('..', 'config', str(self.config_list.currentText()))
        with open(deb_file, 'r') as f:
            deb_data = json.load(f)
        deb = eval(deb_data['type'])
        deb.__setattr__ = setter
        self.deb = deb(deb_file)
        thread.start_new_thread(self.deb.run, ())
        thread.start_new_thread(self.timer_thread, ())
        self.run_button.setDisabled(True)
        self.run_button.setHidden(True)
        self.config_list.setDisabled(True)

    def attr_watcher(self, name, value):
        if name == 'hp':
            if self.hpbar.isHidden():
                self.hpbar.setVisible(True)
            self.hpbar.emit(SIGNAL('update_hp_signal'), value)
        elif name == 'target_counter':
            if self.target_counter_label.isHidden():
                self.target_counter_label.setVisible(True)
            if value > 0:
                self.last_battle_time = None
                self.target_counter_label.emit(SIGNAL('update_target_counter_signal'), '#{}'.format(value))
            else:
                self.last_battle_time = time.time()
        elif name == 'killed_counter':
            if self.killed_counter_label.isHidden():
                self.killed_counter_label.setVisible(True)
            self.killed_counter_label.emit(SIGNAL('update_killed_counter_signal'), 'Killed: {}'.format(value))

    def timer_thread(self):
        while True:
            if self.last_battle_time:
                m, s = divmod(int(time.time() - self.last_battle_time), 60)
                self.target_counter_label.emit(SIGNAL('update_target_counter_signal'), '{} : {:02}'.format(m, s))
            time.sleep(1)


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    current_window = Debby()
    sys.exit(app.exec_())
