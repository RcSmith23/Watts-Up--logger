#! /usr/bin/env python

import sys, os
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import numpy as np
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
import matplotlib.pyplot as plt

class PlotForm(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.setWindowTitle('Watts Up Logger Plot Utility')
        self.final = []
        self.names = []

        self.create_menu()
        self.create_main_frame()
        self.create_status_bar()

    def save_plot(self):
        file_options = "PNG (*.png)|*.png"
        path = unicode(QFileDialog.getSaveFileName(self, 
            'Save file', 'image', file_options))
        if path:
            self.canvas.print_figure(path, dip=self.dpi)
            self.statusBar().showMessage("Saved to %s" % path, 2000)

    def on_pick(self, event):
        if isinstance(event.artist ,Line2D):
            thisline = event.artist
            msg = "You've selected: \n %s" % line_points
            QMessageBox.information(self, "Click!", msg)
	    print "Pick event called, line 2D"

    def draw_plot(self):
        self.figure.clf()
        self.ax = self.figure.add_subplot(111)
        self.canvas.mpl_connect('pick_event', self.on_pick)
        self.ax.grid(self.grid_cb.isChecked())
	lines = []
	for entry in self.final:
            line, = self.ax.plot(*entry, picker=True)
            lines.append(line)
        self.ax.hold(False)
	self.ax.set_title("Energy Data")
        self.ax.set_xlabel("Time (minutes)")
        self.ax.set_ylabel("Power (w)")
        self.ax2 = self.ax.twinx()
        clim = plt.get(self.ax, 'ylim')
        self.ax2.set_ylim(clim[0]*1000/120, clim[1]*1000/120)
        self.ax2.set_ylabel("Current (mA)")
 
        for i in range(0, len(lines)):
            lines[i].set_label(self.names[i])
        handles, labels = self.ax.get_legend_handles_labels()
        self.ax.legend(handles, labels)
        self.canvas.draw()

    def create_main_frame(self):
        self.main_frame = QWidget()

        self.dpi = 100
        self.figure = plt.figure(dpi=self.dpi)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setParent(self.main_frame)
       	self.toolbar = NavigationToolbar(self.canvas, self.main_frame)

        self.add_log_button = QPushButton("&Add Log")
        self.add_log_button.setFixedWidth(150)
        self.add_log_button.clicked.connect(self.add_log)
        self.clear_plot_button = QPushButton("&Clear Plot")
        self.clear_plot_button.setFixedWidth(150)
        self.clear_plot_button.clicked.connect(self.clear_plot)
        self.grid_cb = QCheckBox("Show &Grid")
        self.grid_cb.setChecked(False)
        self.connect(self.grid_cb, SIGNAL('stateChanged(int)'), self.draw_plot)

        hbox = QHBoxLayout()
        hbox.addWidget(self.add_log_button)
        hbox.addWidget(self.clear_plot_button)
        hbox.addWidget(self.grid_cb)

        vbox = QVBoxLayout()
        vbox.addWidget(self.canvas)
        vbox.addWidget(self.toolbar)
        vbox.addLayout(hbox)

        self.main_frame.setLayout(vbox)
        self.setCentralWidget(self.main_frame)

    def add_log(self):
        files = QFileDialog.getOpenFileNames(self.main_frame,
            "Select one or more files to open",)
        if files:
            data = []
            input_files = map(str, files)
            for f in input_files:
                read = unicode(f)
                temp = np.genfromtxt(read, usecols = (2, 3, 4, 5)).tolist()
                data.append(temp)
                self.names.append(os.path.basename(f))
            for item in data:
                t = []
                w = []
                for row in item:
                    t.append((row[0] / 60))
                    w.append(row[1])
                self.final.append([t, w])
            self.draw_plot()
        self.statusBar().showMessage("Added new logs to subplot")

    def clear_plot(self):
        if self.final:
            self.final = []
            self.figure.delaxes(self.ax)
            self.figure.delaxes(self.ax2)
            self.canvas.draw()

    def create_menu(self):
        self.file_menu = self.menuBar().addMenu("&File")
        save_file_action = self.create_action("&Save plot",
	    shortcut="Ctrl+S", slot=self.save_plot,
            tip="Save the plot")
        open_file_action = self.create_action("&Add log",
            shortcut="Ctrl+O", slot=self.add_log,
            tip="Add log to subplot")
        quit_action = self.create_action("&Quit", 
            shortcut="Ctrl+Q", tip="Close the app")

        self.add_actions(self.file_menu,
            (save_file_action, open_file_action, None, quit_action))

    def create_status_bar(self):
        self.status_text = QLabel("Logger Plot")
        self.statusBar().addWidget(self.status_text, 1)

    def add_actions(self, target, actions):
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)

    def create_action(self, text, slot=None, shortcut=None, 
                        icon=None, tip=None, checkable=False, 
                        signal="triggered()"):
        action = QAction(text, self)
        if icon is not None:
            action.setIcon(QIcon(":/%s.png" % icon))
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

def main():
    app = QApplication(sys.argv)
    form = PlotForm()
    form.show()
    app.exec_()

if __name__ == '__main__':
    main()
