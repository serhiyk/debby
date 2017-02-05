#!/usr/bin/python
import sys
from os import listdir
import json
import time
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import QObject, SIGNAL


class MainWindow(QtGui.QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.initUI()

    def initUI(self):
        # self.setFixedSize(320, 240)
        self.setWindowTitle('Debby')

        # layout = QtGui.QVBoxLayout()
        layout = QtGui.QGridLayout()
        button = QtGui.QPushButton("Add", self)
        self.connect(button, SIGNAL("clicked()"), self.add_button_handler)
        layout.addWidget(button, 0, 0, 1, 3)
        i = 1
        for f in listdir('../config'):
            if f.endswith('.json'):
                label = QtGui.QLabel(f[:-5], self)
                layout.addWidget(label, i, 0, 1, 1)
                button = QtGui.QPushButton('Run', self)
                self.connect(button, SIGNAL("clicked()"), lambda who=f: self.run_button_handler(who))
                layout.addWidget(button, i, 1, 1, 1)
                button = QtGui.QPushButton('Edit', self)
                self.connect(button, SIGNAL("clicked()"), lambda who=f: self.edit_button_handler(who))
                layout.addWidget(button, i, 2, 1, 1)
                i += 1
        self.setLayout(layout)
        self.show()

    def add_button_handler(self):
        global current_window
        current_window = AddWindow()
        self.close()

    def run_button_handler(self, args):
        print 'run:', args

    def edit_button_handler(self, args):
        global current_window
        current_window = EditWindow(args)
        self.close()


class AddWindow(QtGui.QWidget):
    def __init__(self):
        super(AddWindow, self).__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Debby')
        layout = QtGui.QGridLayout()
        label = QtGui.QLabel('Type', self)
        layout.addWidget(label, 0, 0)
        self.combo = QtGui.QComboBox(self)
        self.combo.addItem("warrior")
        layout.addWidget(self.combo, 0, 1)
        label = QtGui.QLabel('Name', self)
        layout.addWidget(label, 1, 0)
        self.edit = QtGui.QLineEdit(self)
        layout.addWidget(self.edit, 1, 1)
        button = QtGui.QPushButton("Cancel", self)
        self.connect(button, SIGNAL("clicked()"), self.cancel_button_handler)
        layout.addWidget(button, 2, 0)
        button = QtGui.QPushButton("Add", self)
        self.connect(button, SIGNAL("clicked()"), self.add_button_handler)
        layout.addWidget(button, 2, 1)
        self.setLayout(layout)
        self.show()

    def cancel_button_handler(self):
        global current_window
        current_window = MainWindow()
        self.close()

    def add_button_handler(self):
        config_name = str(self.edit.text())
        config_type = str(self.combo.currentText())
        data = {'type': config_type}
        if config_type == 'warrior':
            data['variables'] = {}
            data['general_skills'] = {'targetnext': 'f9', 'attack': 'f1', 'target': 'f2', 'pickup': 'f4'}
            data['hp_skills'] = []
            data['pre_skills'] = []
            data['post_skills'] = []
        with open('../config/' + config_name + '.json', 'w') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        global current_window
        current_window = MainWindow()
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
        current_window = MainWindow()
        self.close()

    def save_button_handler(self):
        global current_window
        current_window = MainWindow()
        self.close()

    def add_variable(self):
        pass

    def add_general_skill(self):
        pass

    def remove_general_skill(self, arg):
        arg.parent = None
        pass


class AddVariableWindow(QtGui.QWidget):
    def __init__(self, config_file):
        super(AddVariableWindow, self).__init__()
        self.config_file = config_file
        with open('../config/' + config_file) as data_file:
            self.config = json.load(data_file)
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Add variable')
        layout = QtGui.QGridLayout()
        label = QtGui.QLabel('Name', self)
        layout.addWidget(label, 0, 0)
        self.edit_name = QtGui.QLineEdit(self)
        layout.addWidget(self.name_edit, 0, 1)
        label = QtGui.QLabel('Value', self)
        layout.addWidget(label, 1, 0)
        self.edit_value = QtGui.QLineEdit(self)
        layout.addWidget(self.edit_value, 1, 1)
        button = QtGui.QPushButton("Back", self)
        self.connect(button, SIGNAL("clicked()"), self.go_back)
        layout.addWidget(button, 2, 0)
        button = QtGui.QPushButton("Add", self)
        self.connect(button, SIGNAL("clicked()"), self.save_config)
        layout.addWidget(button, 2, 1)
        self.setLayout(layout)
        self.show()

    def save_config(self):
        self.go_back()

    def go_back(self):
        global current_window
        current_window = EditWindow()
        self.close()


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    current_window = MainWindow()
    sys.exit(app.exec_())
