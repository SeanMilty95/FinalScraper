import csv

from PyQt5 import uic
from PyQt5.QtPrintSupport import *
from PyQt5.QtWidgets import *
from win32api import GetSystemMetrics


class DataWin(QMainWindow):
    def __init__(self, unit_name):
        super(DataWin, self).__init__()
        # Load the GUI created in the designer program
        self.ui = uic.loadUi('Data_Page.ui', self)
        self.title = "Listing Data"
        self.listing = unit_name
        self.revenue = 0
        self.given_rate = 0
        self.booked_num = 0
        self.rating = 0
        self.expenseCount = 0
        self.width = GetSystemMetrics(0) / 3.5
        self.height = GetSystemMetrics(1) / 20
        self.inputData()
        self.Buttons()

    def inputData(self):
        """Open the data file that contains the csv objects read from
        there and populate the data GUI.
        """
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
            with open(self.listing + 'Specs.txt', 'r', newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    try:
                        self.revenue += int(row['revenue'])
                        self.booked_num += int(len(row['booked_days']))
                    except ValueError:
                        print("Not A Number")
                    self.given_rate = row['given_rate']
                    self.rating = row['rating']
        except IOError:
            self.ui.ErrorEdit.show()
            self.ui.ErrorEdit.setText("No data file found for this"
                                      "unit. Generate data from the"
                                      "main menu.")

        # Populate data page with the gathered data
        self.ui.Gross.setReadOnly(True)
        self.ui.Given.setReadOnly(True)
        self.ui.Booked.setReadOnly(True)
        self.ui.Rating.setReadOnly(True)
        self.ui.Net.setReadOnly(True)

        self.ui.Gross.setText(str(self.revenue))
        self.ui.Given.setText(str(self.given_rate))
        self.ui.Booked.setText(str(self.booked_num))
        self.ui.Rating.setText(str(self.rating + '/5'))

        # Add any previous expenses if they exist
        count1 = 0
        count2 = 0
        add = True
        # Open the expenses file
        try:
            with open(self.listing + 'expenses.txt', 'r', newline='') as expfile:
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
                self.AddExpense()  # Adds the HorizWidget with the 3 line edits
                new_exp.append(expense.strip('\n'))
                for i in range(len(new_exp)):
                    lines = new_exp[i].split(',')
                strings1.append(lines)
            # Fills the line edit text fields with the values
            # stored in the list named 'strings'
            widgets = self.ui.Expenses.findChildren(QWidget, 'HorzWidget')
            for widget in widgets:
                edits = widget.findChildren(QLineEdit)
                count1 += 1
                count2 = 0
                for edit in edits:
                    edit.setText(strings1[count1 - 1][count2])
                    count2 += 1

    def Buttons(self):
        """The following code will call the function in parenthesis
        when the designated button is clicked.
        """
        self.ui.pushButton.clicked.connect(self.AddExpense)
        self.ui.pushButton_2.clicked.connect(self.calc_net)
        self.ui.pushButton_3.clicked.connect(self.Save_PDF)
        self.ui.save_exp.clicked.connect(self.save_expenses)

    def AddExpense(self):
        """Add 3 lineEdits to the Exspenses QWidget.
        Has form layout(may need to delete in designer and add via python)
        if need to create via python dont forget to add placeholder text.
        """

        to_many = self.To_Many()
        if to_many is False:
            # Grab layout if available
            layout = self.ui.Expenses.layout()

            # Initialize a horizontal box layout to hold line edits
            HLayout = QHBoxLayout()
            HLayout.setSpacing(5)
            HLayout.setObjectName('Expense')
            # Initialize a QWidget to hold the layout
            WidgetBox = QWidget()
            WidgetBox.setObjectName('HorzWidget')
            WidgetBox.setMinimumHeight(50)
            WidgetBox.setMaximumHeight(50)
            WidgetBox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

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
            HLayout.addWidget(text)
            HLayout.addWidget(text2)
            HLayout.addWidget(text3)

            # Add Horizontal box layout to the Qwidget
            WidgetBox.setLayout(HLayout)

            if layout is None:
                # If no layout exists for the QFrame 'Expenses' create vertical layout
                # and add widget
                VBox = QVBoxLayout()
                VBox.setSpacing(5)
                VBox.addWidget(WidgetBox)
                # Set Frame layout to the vertical layout just created
                self.ui.Expenses.setLayout(VBox)

            else:
                # If layout exists add Qwidget with horizontal layout and update
                # frame layout.
                layout.addWidget(WidgetBox)
                layout.update()
            self.updateCount()

    def calc_net(self):
        """Loop through the lineEdits with integer values and find
        the sum.
        Subtract that sum from the Gross income value found elsewhere.
        Set lineEdit text for net income.
        """

        net_income = float(self.ui.Gross.text())  # Grab the gross income for the listing
        values = []
        # Grab all the Line Edit children from the QFrame 'Expenses'
        edits = self.ui.Expenses.findChildren(QLineEdit, 'expTot')
        # Add all non blank values to a list if integer values
        for edit in edits:
            if edit.text() is not None and edit.text() != '':
                values.append(float(edit.text()))
        # Subtract each value from the gross profit
        for value in values:
            net_income -= value
        # Set the Line Edit text equal to the net income
        self.ui.Net.setText(str(net_income))

    def save_expenses(self):
        """Saves the expenses created by the user for future reference
        stored in a text file named 'listing'expenses.txt.
        """
        expenses = self.ui.Expenses.findChildren(QWidget, 'HorzWidget')
        with open(self.listing + 'expenses.txt', 'w+', newline='') as expfile:
            for expense in expenses:
                edits = expense.findChildren(QLineEdit)
                expfile.write(edits[0].text() + ',' + edits[1].text() + ',' + edits[2].text() + '\n')

    def Save_PDF(self):
        """Take a screenshot of the data GUI
        Send to the QPrinter or QPainter and set value as pdf
        check favorited links for possible examples.
        """

        printer = QPrinter(QPrinter.HighResolution)
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setResolution(100)

        printer.setOutputFileName(self.listing + '.pdf')
        self.render(printer)

    def To_Many(self):
        """Checks the amount of children called 'HorzWidget' from
        the 'Expenses' widget.
        Returns true if the number is 12 and false if less than 12.
        """

        num_widgets = self.ui.Expenses.findChildren(QWidget, 'HorzWidget')
        if len(num_widgets) == 12:
            return True
        else:
            return False

    def updateCount(self):
        """Gets the counter of expense horzwidgets and updates the
        counter label.
        """

        self.expenseCount += 1
        self.ui.Counter.setText(str(self.expenseCount) + ' / 12')

