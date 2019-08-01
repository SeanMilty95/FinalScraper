from DataGUI import *


class MonthWin(QMainWindow):
    def __init__(self, name):
        super(MonthWin, self).__init__()
        # Load the GUI created in the designer program
        self.ui = uic.loadUi('Month.ui', self)
        self.title = "Available Month List"
        self.setWindowIcon(QIcon('teemo-classic.png'))
        self.unit_name = name
        self.is_annual = False
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
        self.ui.buttonBox.accepted.connect(self.which_data)
        self.ui.buttonBox.rejected.connect(self.ui.close)
        self.ui.AnnualData.clicked.connect(self.set_annual)

    def get_month_names(self):
        year = str(datetime.datetime.now().year)
        with open('./' + self.unit_name + '/' + year + '.txt', 'r', newline='') as unit_file:
            reader = csv.DictReader(unit_file)
            for row in reader:
                self.available_months.append(row['month'])

    def which_data(self):
        if self.is_annual:
            self.show_annual_data()
        else:
            self.show_month_data()

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

    def show_annual_data(self):
        self.ui.ErrorLabel.setText("Annual Data not yet available")
        self.ui.ErrorLabel.show()

    def set_annual(self):
        if self.is_annual:
            self.is_annual = False
            self.set_checkable()
        else:
            self.is_annual = True
            self.set_uncheckable()

    def set_uncheckable(self):
        months = self.ui.groupBox.findChildren(QCheckBox)
        for month in months:
            month.setChecked(False)
            month.setCheckable(False)

    def set_checkable(self):
        self.ui.ErrorLabel.hide()
        months = self.ui.groupBox.findChildren(QCheckBox)
        for month in months:
            month.setCheckable(True)
