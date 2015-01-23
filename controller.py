#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import sys, os
import MySQLdb as mdb

class MonitorForm(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.setWindowTitle("EDB Machine Monitor")

        self.create_menu()
        self.create_status_bar()
        self.machines = MachinesForm(self)
        self.setCentralWidget(self.machines)

    def create_menu(self):
        self.file_menu = self.menuBar().addMenu("&File")
        quit_action = self.create_action("&Quit", shortcut="Ctrl+q",
                tip="Close the app", slot=self.quit_program)
        self.add_actions(self.file_menu, [quit_action])

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
        self.statusBar().addWidget(self.status_text, 1)

    def quit_program(self):
        QCoreApplication.instance().quit()

class MachinesForm(QWidget):
    def __init__(self, parent):
        super(MachinesForm, self).__init__(parent)
        self.layout = QHBoxLayout(self)
        self.machines = QStandardItemModel()
        self.get_machines()
        self.machines.itemChanged.connect(self.item_changed)
        self.m_list = QListView()
        self.m_list.setModel(self.machines)
        self.layout.addWidget(self.m_list)
        self.selected = QStandardItemModel()
        self.s_list = QListView()
        self.s_list.setModel(self.selected)
        self.layout.addWidget(self.s_list)

    def get_machines(self):
        db_host = os.getenv("DB_HOST")
        db_user = os.getenv("DB_USERNAME")
        db_pass = os.getenv("DB_PASS")
        db_name = os.getenv("DB_NAME")
 
        try:
            con = mdb.connect(db_host, db_user, db_pass, db_name)
            cur = con.cursor()
            cur.execute("SELECT * FROM machines")
            rows = cur.fetchall()
        except mdb.Error, e:
            pass
        finally:
            if con:
                con.close()
        
        for r in rows:
            item = QStandardItem(r[1])
            item.setCheckState(Qt.Unchecked)
            item.setCheckable(True)
            self.machines.appendRow(item)

    def get_tests(self):
        db_host = os.getenv("DB_HOST")
        db_user = os.getenv("DB_USERNAME")
        db_pass = os.getenv("DB_PASS")
        db_name = os.getenv("DB_NAME")
 
        try:
            con = mdb.connect(db_host, db_user, db_pass, db_name)
            cur = con.cursor()
            # cur.execute("SELECT * FROM machines")
            # Need query to select all combinations
            rows = cur.fetchall()
        except mdb.Error, e:
            pass
        finally:
            if con:
                con.close()


    def item_changed(self, item):
        # First, find all checked machines.
        # Then find all tests available on both
        pass       

def main():
    app = QApplication(sys.argv)
    screen = MonitorForm()
    screen.show()
    sys.exit(app.exec_())

# The CLI for parsing and launching GUI
def start():
    # Parse CL args here first
    main()

if __name__ == '__main__':
    start()
