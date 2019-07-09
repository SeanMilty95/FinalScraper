import datetime
import csv

from PyQt5 import uic
from PyQt5.QtWidgets import *


class MonthWin(QMainWindow):
    def __init__(self, name):
        super(MonthWin, self).__init__()
        # Load the GUI created in the designer program
        self.ui = uic.loadUi('Month.ui', self)
        self.title = "Available Month List"
        self.unit_name = name
        self.available_months = []
        self.input_data()

    def input_data(self):
        self.ui.setWindowTitle(self.title)
        self.get_month_names()

        layout = QFormLayout()
        for name in self.available_months:
            layout.addWidget(QCheckBox(name))
        layout.update()

    def get_month_names(self):
        year = str(datetime.datetime.now().year)
        with open('./' + self.unit_name + '/' + year, 'r', newline='') as unit_file:
            reader = csv.DictReader(unit_file)
            for row in reader:
                self.available_months.append(row['month'])
