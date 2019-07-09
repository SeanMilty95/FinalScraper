from DataGUI import *


class MonthWin(QMainWindow):
    def __init__(self, name):
        super(MonthWin, self).__init__()
        # Load the GUI created in the designer program
        self.ui = uic.loadUi('Month.ui', self)
        self.title = "Available Month List"
        self.unit_name = name
        self.available_months = []
        self.input_data()
        self.button_listener()

    def input_data(self):
        self.ui.setWindowTitle(self.title)
        self.get_month_names()

        layout = QFormLayout()
        for name in self.available_months:
            if name != 'n/a':
                layout.addWidget(QCheckBox(name))
        self.ui.groupBox.setLayout(layout)

    def button_listener(self):
        self.ui.buttonBox.accepted.connect(self.show_month_data)
        self.ui.buttonBox.rejected.connect(self.ui.close)

    def get_month_names(self):
        year = str(datetime.datetime.now().year)
        with open('./' + self.unit_name + '/' + year + '.txt', 'r', newline='') as unit_file:
            reader = csv.DictReader(unit_file)
            for row in reader:
                self.available_months.append(row['month'])

    def show_month_data(self):
        month_list = []
        check_boxes = self.ui.groupBox.findChildren(QCheckBox)
        for i in range(len(check_boxes)):
            if check_boxes[i].isChecked():
                month_list.append(check_boxes[i].text())
                check_boxes[i].setCheckState(False)

        for month in month_list:
            data_win = DataWin(self.unit_name, month)
            data_win.show()
            data_win.activateWindow()
        self.ui.close()
