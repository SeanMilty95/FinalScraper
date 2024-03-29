import csv
import os
import datetime
import urllib.request
from urllib.error import URLError

from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon


class EditWindow(QMainWindow):
    def __init__(self, box):
        super(EditWindow, self).__init__()
        # Load .ui file created in the designer program
        self.ui = uic.loadUi('EditGUI.ui', self)
        self.ui.setWindowTitle(" Edit Unit Info")
        self.setWindowIcon(QIcon('teemo-classic.png'))
        self.old_unit_name = box.text()
        self.old_url = self.find_old_url()
        self.boxey = box
        self.new_name = ''
        self.new_url = ''
        self.name_changed = False
        self.input_data()
        # self.button_listener()

    def input_data(self):
        self.ui.OldName.setText(self.old_unit_name)
        self.ui.OldURL.setText(self.old_url)

    # def button_listener(self):
        # self.ui.Accept.clicked.connect(self.update_data)

    def update_data(self):
        self.new_name = self.ui.NewName.text()
        self.new_url = self.ui.NewURL.text()

        try:
            urllib.request.urlopen(self.new_url)
        except ValueError:
            self.ui.URLErrorLabel.setText("Invalid URL!")
        except URLError:
            self.ui.URLErrorLabel.setText("Invalid URL!")
        else:
            os.rename('./' + self.old_unit_name, './' + self.new_name)

            new_info = []
            date = str(datetime.date.today())
            with open('units.txt', 'r', newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    if row['name'] == self.old_unit_name:
                        new_info.append({'name': self.new_name, 'url': self.new_url, 'date': date})
                    else:
                        new_info.append(row)

            with open('units.txt', 'w', newline='') as csvfile:
                fieldnames = ['name', 'url', 'date']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for i in range(len(new_info)):
                    writer.writerow(new_info[i])

    def find_old_url(self):
        with open('units.txt', 'r', newline='') as unit_file:
            reader = csv.DictReader(unit_file)
            for row in reader:
                if row['name'] == self.old_unit_name:
                    return row['url']
        return 'hello'

    def get_name(self):
        return self.new_name
