import csv
import datetime
import ast

from PyQt5 import uic
from PyQt5.QtPrintSupport import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtCore import QUrl
from win32api import GetSystemMetrics


class DataWin(QMainWindow):
    def __init__(self, unit_name, month):
        super(DataWin, self).__init__()
        # Load the GUI created in the designer program
        self.ui = uic.loadUi('Data_Page.ui', self)
        self.title = "Listing Data"
        self.month_to_see = month
        self.listing = unit_name
        self.url_string = ''
        self.revenue = 0
        self.annual_revenue = 0
        self.given_rate = 0
        self.booked_num = 0
        self.occupancy_rate = 0
        self.rating = 0
        self.expenseCount = 0
        self.width = GetSystemMetrics(0) / 3.5
        self.height = GetSystemMetrics(1) / 20
        self.input_data()
        self.buttons()

    def input_data(self):
        """Open the data file that contains the csv objects read from
        there and populate the data GUI.
        """
        current_year = str(datetime.datetime.now().year)
        self.ui.move(self.width - 350, self.height)
        # Add Listing name to data file
        self.ui.setWindowTitle(self.listing + ' Data Page')
        self.ui.Unit_Name.setText(self.listing + ' Data')
        self.ui.ErrorEdit.setReadOnly(True)
        self.ui.ErrorEdit.hide()
        self.ui.ExpenseError.setReadOnly(True)
        self.ui.ExpenseError.hide()

        # Gather data from file
        try:
            with open('./' + self.listing + '/' + current_year + '.txt', 'r', newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    self.annual_revenue += int(row['revenue'])
                    if row['month'] == self.month_to_see:
                        self.revenue = int(row['revenue'])
                        self.occupancy_rate = row['occupancy']
                        self.booked_num = len(ast.literal_eval(row['booked_days']))
                    self.given_rate = row['given_rate']
                    self.rating = row['rating']
                    self.ui.month_name.setText(row['month'].upper())
                    self.ui.NetMonth.setText(row['month'].upper())
        except IOError:
            self.ui.ErrorEdit.show()
            self.ui.ErrorEdit.setText("No data file found for this"
                                      "unit. Generate data from the"
                                      "main menu.")

        # Populate data page with the gathered data
        self.ui.Gross.setReadOnly(True)
        self.ui.Given.setReadOnly(True)
        self.ui.Occupancy.setReadOnly(True)
        self.ui.Rating.setReadOnly(True)
        self.ui.Net.setReadOnly(True)

        self.ui.Gross.setText('$ ' + str(self.revenue))
        self.ui.AnnualRevenue.setText('$ ' + str(self.annual_revenue*3))
        self.ui.Given.setText(str(self.given_rate))
        self.ui.Occupancy.setText(str(self.occupancy_rate))
        self.ui.Rating.setText(str(self.rating) + '/5')

        # Open units.txt for hyperlink
        with open('units.txt', 'r', newline='') as unit_file:
            reader = csv.DictReader(unit_file)
            for row in reader:
                if row['name'] == self.listing:
                    self.ui.HyperLink.setText('<a href=' + row['url'] + '>' + self.listing + '</a>')
                    self.ui.HyperLink.setOpenExternalLinks(True)
                    self.url_string = row['url']

        try:
            with open('./' + self.listing + '/' + 'Notes.txt', 'r', newline='') as sumfile:
                summary_notes = sumfile.read()
        except IOError:
            summary_notes = 'Summary Notes: '
        self.ui.SumNotes.setPlainText(summary_notes)

        # Add any previous expenses if they exist
        count1 = 0
        add = True
        # Open the expenses file
        try:
            with open('./' + self.listing + '/' + 'expenses.txt', 'r', newline='') as expfile:
                expenses = expfile.readlines()
        except IOError:
            self.ui.ExpenseError.show()
            self.ui.ExpenseError.setText("No Expense File Found. No Expenses Added")
            add = False

        if add:
            strings1 = []
            new_exp = []
            # Populates a list with a list of strings that
            # will go into the line edit text fields
            for expense in expenses:
                self.add_expense()  # Adds the HorizWidget with the 3 line edits
                new_exp.append(expense.strip('\n'))
                for i in range(len(new_exp)):
                    lines = new_exp[i].split(',')
                strings1.append(lines)
            # Fills the line edit text fields with the values
            # stored in the list named 'strings'
            widgets = self.ui.Expenses.findChildren(QWidget, 'HorzWidget')
            self.ui.ExpenseError.hide()
            for widget in widgets:
                edits = widget.findChildren(QLineEdit)
                count1 += 1
                count2 = 0
                for edit in edits:
                    edit.setText(strings1[count1 - 1][count2])
                    count2 += 1

    def buttons(self):
        """The following code will call the function in parenthesis
        when the designated button is clicked.
        """
        self.ui.pushButton.clicked.connect(self.add_expense)
        self.ui.pushButton_2.clicked.connect(self.calc_net)
        self.ui.pushButton_3.clicked.connect(self.save_pdf)
        self.ui.save_exp.clicked.connect(self.save_expenses)
        self.ui.SaveNotes.clicked.connect(self.save_notes)

        self.HyperLink.linkActivated.connect(self.link)

    def add_expense(self):
        """Add 3 lineEdits to the Exspenses QWidget.
        Has form layout(may need to delete in designer and add via python)
        if need to create via python dont forget to add placeholder text.
        """
        self.ui.ExpenseError.setText("Don't Forget to save any new expenses!")
        self.ui.ErrorEdit.hide()
        to_many = self.to_many()
        if to_many is False:
            # Grab layout if available
            layout = self.ui.Expenses.layout()

            # Initialize a horizontal box layout to hold line edits
            h_layout = QHBoxLayout()
            h_layout.setSpacing(5)
            h_layout.setObjectName('Expense')
            # Initialize a QWidget to hold the layout
            widget_box = QWidget()
            widget_box.setObjectName('HorzWidget')
            widget_box.setMinimumHeight(50)
            widget_box.setMaximumHeight(50)
            widget_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

            # Create Line Edits
            text = QLineEdit()
            text.setMaximumWidth(150)
            text2 = QLineEdit()
            text2.setMaximumWidth(150)
            text2.setObjectName('expTot')
            text3 = QLineEdit()
            text.setPlaceholderText('Expense Name')
            text2.setPlaceholderText('Total')
            text3.setPlaceholderText('Notes')

            # Add Line Edits to the horizontal box layout
            h_layout.addWidget(text)
            h_layout.addWidget(text2)
            h_layout.addWidget(text3)

            # Add Horizontal box layout to the Qwidget
            widget_box.setLayout(h_layout)

            if layout is None:
                # If no layout exists for the QFrame 'Expenses' create vertical layout
                # and add widget
                v_box = QVBoxLayout()
                v_box.setSpacing(5)
                v_box.addWidget(widget_box)
                # Set Frame layout to the vertical layout just created
                self.ui.Expenses.setLayout(v_box)

            else:
                # If layout exists add Qwidget with horizontal layout and update
                # frame layout.
                layout.addWidget(widget_box)
                layout.update()
            self.update_count()

    def calc_net(self):
        """Loop through the lineEdits with integer values and find
        the sum.
        Subtract that sum from the Gross income value found elsewhere.
        Set lineEdit text for net income.
        """
        month_expense = 0
        net_income_month = float(self.ui.Gross.text().strip('$'))  # Grab the gross income for the listing
        # net_income_annual = float(self.ui.AnnualGross.text().strip('$'))
        values = []
        # Grab all the Line Edit children from the QFrame 'Expenses'
        edits = self.ui.Expenses.findChildren(QLineEdit, 'expTot')
        # Add all non blank values to a list if integer values
        for edit in edits:
            if edit.text() is not None and edit.text() != '':
                new_val = edit.text().strip('$')
                values.append(float(new_val))
        # Subtract each value from the gross profit
        for value in values:
            net_income_month -= value
            month_expense += value
        # Set the Line Edit text equal to the net income
        self.ui.Net.setText('$ ' + str(net_income_month))
        if net_income_month == float(self.ui.Gross.text().strip('$')):
            self.ui.ErrorEdit.show()
            self.ui.ErrorEdit.setText("No Expenses used in calculations!")
        year_expense = month_expense * 12
        self.ui.AnnualNet.setText(str(year_expense))

    def save_expenses(self):
        """Saves the expenses created by the user for future reference
        stored in a text file named 'listing'expenses.txt.
        """
        self.ui.ExpenseError.setText("Expenses Saved!")
        expenses = self.ui.Expenses.findChildren(QWidget, 'HorzWidget')
        with open('./' + self.listing + '/' + 'expenses.txt', 'w+', newline='') as expfile:
            for expense in expenses:
                edits = expense.findChildren(QLineEdit)
                expfile.write(edits[0].text() + ',' + edits[1].text() + ',' + edits[2].text() + '\n')

    def save_pdf(self):
        """Take a screenshot of the data GUI
        Send to the QPrinter or QPainter and set value as pdf
        check favorited links for possible examples.
        """
        self.ui.ExpenseError.hide()
        self.ui.ErrorEdit.hide()
        
        printer = QPrinter(QPrinter.HighResolution)
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setResolution(100)

        printer.setOutputFileName('./' + self.listing + '/' + '.pdf')
        self.render(printer)

    def to_many(self):
        """Checks the amount of children called 'HorzWidget' from
        the 'Expenses' widget.
        Returns true if the number is 12 and false if less than 12.
        """

        num_widgets = self.ui.Expenses.findChildren(QWidget, 'HorzWidget')
        if len(num_widgets) == 12:
            return True
        else:
            return False

    def save_notes(self):
        with open('./' + self.listing + '/' + 'Notes.txt', 'w+', newline='') as sumfile:
            sumfile.write(self.ui.SumNotes.toPlainText())

    def update_count(self):
        """Gets the counter of expense horzwidgets and updates the
        counter label.
        """

        self.expenseCount += 1
        self.ui.Counter.setText(str(self.expenseCount) + ' / 12')

    def link(self):
        QDesktopServices.openUrl(QUrl(self.url_string))
