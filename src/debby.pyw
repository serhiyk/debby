#!/usr/bin/python
import sys
import os
import json
import thread
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import SIGNAL
from warrior import Warrior
from support import Support


class Debby(QtGui.QWidget):
    def __init__(self):
        super(Debby, self).__init__()
        self.config = {}
        self.config_file = os.path.join(os.path.expanduser('~'), 'debby.json')
        if os.path.isfile(self.config_file):
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Debby')
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
        self.hpbar = QtGui.QProgressBar()
        self.hpbar.setMinimum(0)
        self.hpbar.setMaximum(100)
        self.hpbar.setHidden(True)
        self.connect(self.hpbar, SIGNAL('update_hp_signal'), self.hpbar.setValue)
        self.main_layout.addWidget(self.hpbar)
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
        self.run_button.setDisabled(True)
        self.run_button.setHidden(True)
        self.config_list.setDisabled(True)

    def attr_watcher(self, name, value):
        if name == 'hp':
            if self.hpbar.isHidden():
                self.hpbar.setVisible(True)
            self.hpbar.emit(SIGNAL('update_hp_signal'), value)

    def edit_button_handler(self, args):
        global current_window
        current_window = EditWindow(args)
        self.close()


class EditWindow(QtGui.QWidget):
    def __init__(self, config_file):
        super(EditWindow, self).__init__()
        self.config_file = config_file
        with open('../config/' + config_file) as data_file:
            self.config = json.load(data_file)
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Debby')
        self.layout = QtGui.QVBoxLayout()
        self.init_variables()
        self.init_general_skills()
        layout = QtGui.QHBoxLayout()
        button = QtGui.QPushButton("Cancel", self)
        self.connect(button, SIGNAL("clicked()"), self.cancel_button_handler)
        layout.addWidget(button)
        button = QtGui.QPushButton("Save", self)
        self.connect(button, SIGNAL("clicked()"), self.save_button_handler)
        layout.addWidget(button)
        self.layout.addLayout(layout)
        self.setLayout(self.layout)
        self.show()

    def init_variables(self):
        group = QtGui.QGroupBox("Variables", self)
        layout = QtGui.QGridLayout(group)
        label = QtGui.QLabel('Name', self)
        layout.addWidget(label, 0, 0)
        label = QtGui.QLabel('Value', self)
        layout.addWidget(label, 0, 1)
        button = QtGui.QPushButton("Add", self)
        self.connect(button, SIGNAL("clicked()"), self.add_variable)
        layout.addWidget(button, 1, 0)
        self.layout.addWidget(group)

    def init_general_skills(self):
        group = QtGui.QGroupBox("General skills", self)
        layout = QtGui.QGridLayout(group)
        label = QtGui.QLabel('Name', self)
        layout.addWidget(label, 0, 0)
        label = QtGui.QLabel('Function', self)
        layout.addWidget(label, 0, 1)
        i = 1
        for skill, func in self.config['general_skills'].iteritems():
            label = QtGui.QLabel(skill, self)
            layout.addWidget(label, i, 0)
            label = QtGui.QLabel(func, self)
            layout.addWidget(label, i, 1)
            button = QtGui.QPushButton('Remove', self)
            self.connect(button, SIGNAL("clicked()"), lambda arg=button: self.remove_general_skill(arg))
            layout.addWidget(button, i, 2)
            i += 1
        button = QtGui.QPushButton("Add", self)
        self.connect(button, SIGNAL("clicked()"), self.add_general_skill)
        layout.addWidget(button, i, 0)
        self.layout.addWidget(group)

    def cancel_button_handler(self):
        global current_window
        current_window = Debby()
        self.close()

    def save_button_handler(self):
        global current_window
        current_window = Debby()
        self.close()

    def add_variable(self):
        pass

    def add_general_skill(self):
        pass

    def remove_general_skill(self, arg):
        arg.parent = None
        pass


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    current_window = Debby()
    sys.exit(app.exec_())
