#!/usr/bin/env python2.7

import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

class MonitorForm(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.setWindowTitle("EDB Machine Monitor")

        self.create_menu()
        self.create_main_frame()
        self.create_status_bar()

    def create_main_frame(self):
        self.main_frame = QWidget()

        self.setCentralWidget(self.main_frame)


    def create_menu(self):
        self.file_menu = self.menuBar().addMenu("&File")
        quit_action = self.create_action("&Quit", shortcut="Ctrl+q",
                tip="Close the app")
        self.add_actions(self.file_menu, (quit_action))

    def create_action(self, text, slot=None, shortcut=None,
            icon=None, tip=None, checkable=False, signal="triggered()"):
        action = QAction(text, self)
        if icon is not None:
            action.setIcon(QIcon(":%s.png" % icon))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            self.connect(action, SIGNAL(signal), slot)
        if checkable:
            action.setCheckable(True)
        return action

    def add_actions(self, target, actions):
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)

    def create_status_bar(self):
        self.status_text = QLabel("EDB Machines")
        self.statusbar().addWidget(self.status_text, 1)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    screen = MonitorForm()
    screen.show()
    sys.exit(app.exec_())
