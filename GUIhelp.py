from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from DataGUI import *

from HelperFunctions import *


class Window(QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        # Load .ui file created in the designer program
        self.ui = uic.loadUi('GUI.ui', self)
        self.ui.setWindowTitle("VRBO Web Scraper")
        # Gets the dimensions of the screen
        self.width = GetSystemMetrics(0) / 3.5
        self.height = GetSystemMetrics(1) / 3
        self.ui.move(self.width, self.height)
        # List that will hold the lines from unit.txt
        self.all_lines = []
        self.fill_unit_list()
        self.hide_error_boxes()
        self.button_listener()

    def button_listener(self):
        """Listens for button clicks."""
        # Calls functions when the designated pushButton is clicked
        self.ui.pushButton_2.clicked.connect(self.addUnit)
        self.ui.pushButton_5.clicked.connect(self.deleteUnit)
        self.ui.pushButton_3.clicked.connect(self.updateAll)
        self.ui.pushButton.clicked.connect(self.generate)
        self.ui.show_data.clicked.connect(self.show_data_page)

    def hide_error_boxes(self):
        """Hides the Text Edit used to display error messages."""
        self.ui.ErrorEdit.hide()
        self.ui.ErrorEdit.setReadOnly(True)

    def fill_unit_list(self):
        """Fills the scroll area with the units that are available
        from the data.txt file. Adds a checkbox for each unit.
        """
        # Opens and reads from the list in units.txt
        in_file = open('units.txt', 'r')
        unit_list = in_file.readlines()
        self.all_lines = unit_list
        in_file.close()

        layout = self.ui.scrollAreaWidgetContents.layout()
        # For every Line/Unit add a QCheckBox to the layout
        if layout is None or layout == '':
            layout = QVBoxLayout()
            # Set the scrollArea layout to the layout that contains the check boxes
            self.ui.scrollAreaWidgetContents.setLayout(layout)
        for i in range(len(unit_list)):
            line = unit_list[i].split(' ')
            layout.addWidget(QCheckBox(line[0]))
        layout.update()

    def addUnit(self):
        """Uses the info given by the user in the Text Edits to add
        a units information to the units.txt file.
        It will then call fill_unit_list() to add the new unit to
        the scroll area.
        """
        valid_info = False
        # Take the input from user and add the information to units.txt
        unit_name = self.ui.lineEdit.text()
        unit_url = self.ui.lineEdit_2.text()

        if unit_name == '' or unit_url == '':
            self.ui.ErrorEdit.show()
            self.ui.ErrorEdit.setText('Please fill out the unit information in the spaces provided.')
        else:
            self.ui.ErrorEdit.clear()
            self.ui.ErrorEdit.hide()
            valid_info = True
        if valid_info:
            if unit_name is not None and unit_url is not None:  # If a field is empty do not add to file
                self.ui.lineEdit.clear()
                self.ui.lineEdit_2.clear()
                date = str(datetime.date.today())
                unit_info = unit_name + ' ' + unit_url + ' ' + date + '\n'
                url_file = open('units.txt', 'a+')
                url_file.write(unit_info)
                url_file.close()

            # Opens and reads from the list in units.txt
            in_file = open('units.txt', 'r')
            unit_list = in_file.readlines()
            self.all_lines = unit_list
            in_file.close()

            layout = self.ui.scrollAreaWidgetContents.layout()
            if layout is None or layout == '':
                self.fill_unit_list()
            else:
                layout.addWidget(QCheckBox(unit_name))
                layout.update()

    def deleteUnit(self):
        """Deletes a unit from the units.txt file and
        removes its check box from the scroll area.
        """
        # Fill a list with QCheckBoxes. If a box is not checked add it to units.txt
        # This essential deletes the units that were checked.
        checkBoxes = self.ui.scrollAreaWidgetContents.findChildren(QCheckBox)
        lines = []
        layout = self.ui.scrollAreaWidgetContents.layout()
        with open('units.txt', 'r') as f:
            lines = f.readlines()
        with open('units.txt', 'w') as f:
            for i in range(len(lines)):
                # split_line = lines[i].split(' ')
                if checkBoxes[i].isChecked() is False:
                    f.write(lines[i])
                else:
                    checkBoxes[i].setChecked(False)
                    checkBoxes[i].hide()
                    layout.update()

    def updateAll(self):
        """Gathers and updates all the unit info for the units
        that can be found in the units.txt file.
        """
        # Start the selenium code and start scraping the listing html for information
        units = []
        for line in self.all_lines:
            line = line.split(' ')
            units.append(line)
        self.get_info_for(units)
        print("Updates Complete")

    def generate(self):
        """Gathers data for any units that has it's check box checked.
        A data GUI is then created and shown to the user.
        """
        # Start the selenium code for the listing url for the checked listing
        checkBoxes = self.ui.scrollAreaWidgetContents.findChildren(QCheckBox)
        units = []
        for i in range(len(checkBoxes)):
            if checkBoxes[i].isChecked() is True:
                units.append(self.all_lines[i].split(' '))
                checkBoxes[i].setChecked(False)
        self.get_info_for(units)
        # Generate the data GUI to present the data gathered from the listings html
        for unit in units:
            data_win = DataWin(unit[0])
            data_win.show()
            data_win.activateWindow()

    def show_data_page(self):
        """Generates a data GUI window to show a user the stored
        information on a unit. Generates no new data.
        """
        checkBoxes = self.ui.scrollAreaWidgetContents.findChildren(QCheckBox)
        units = []
        for i in range(len(checkBoxes)):
            if checkBoxes[i].isChecked() is True:
                units.append(self.all_lines[i].split(' '))
                checkBoxes[i].setChecked(False)
        for unit in units:
            data_win = DataWin(unit[0])
            data_win.show()
            data_win.activateWindow()

    def get_info_for(self, units):
        """Starts the webdriver process and sends the needed information
        to various helper functions. Moves the main window so it
        remains visible. Also clicks the inspect option of the context
        click.
        """
        # Creates a driver for chrome
        opts = Options()
        opts.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/75.0.3770.100 Safari/537.36")
        #opts.add_argument("--disable-infobars")
        #driver = webdriver.Chrome(executable_path=r'chromedriver.exe')
        driver = webdriver.Chrome(chrome_options=opts)
        for unit in units:
            driver.get(unit[1])  # Goes to the url listed for the unit
            self.ui.move(self.width + 500, self.height)
            # Right clicks and left clicks to inspect web page elements
            time.sleep(1)
            actions = ActionChains(driver)
            actions.context_click().perform()
            pyautogui.click(150, 356)
            time.sleep(1)

            # Generally the functions find the data you are looking for
            # Check the file HelperFunctions to specifically see what they do
            Month_List = Get_Month_Info(driver)

            occupancy_rates = calc_monthly_occupancy_rate(Month_List)

            tot_rev = get_total_revenue(Month_List)

            gen_data_file(Month_List, occupancy_rates, tot_rev, unit[0])
        # Closes chrome and everything it was using
        driver.quit()
