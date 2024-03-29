from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
from openpyxl import Workbook
from PyQt5 import QtGui

from MonthGUI import *
from EditGUI import *
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
        self.setWindowIcon(QtGui.QIcon('teemo-classic.png'))
        # List that will hold the lines from unit.txt
        self.all_lines = []
        self.fill_unit_list()
        self.xl_folder_path = ''
        self.hide_error_boxes()
        self.button_listener()

    def button_listener(self):
        """Listens for button clicks."""
        # Calls functions when the designated pushButton is clicked
        self.ui.pushButton_2.clicked.connect(self.add_unit)
        self.ui.pushButton_5.clicked.connect(self.delete_unit)
        self.ui.pushButton_3.clicked.connect(self.update_all)
        self.ui.pushButton.clicked.connect(self.generate)
        self.ui.show_data.clicked.connect(self.show_data_page)
        self.ui.EditUnit.clicked.connect(self.edit_unit_info)
        self.ui.ExcelDocument.clicked.connect(self.generate_excel)

    def hide_error_boxes(self):
        """Hides the Text Edit used to display error messages."""
        self.ui.ErrorEdit.hide()
        self.ui.ErrorEdit.setReadOnly(True)

    def fill_unit_list(self):
        """Fills the scroll area with the units that are available
        from the data.txt file. Adds a checkbox for each unit.
        """
        unit_list = []
        try:
            with open('units.txt', 'r+', newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    unit_list.append(row)
                unit_list = sorted(unit_list, key=lambda k: k['name'])
                self.all_lines = unit_list
        except IOError:
            print("No units.txt file")

        layout = self.ui.scrollAreaWidgetContents.layout()
        # For every Line/Unit add a QCheckBox to the layout
        if layout is None or layout == '':
            layout = QVBoxLayout()
            # Set the scrollArea layout to the layout that contains the check boxes
            self.ui.scrollAreaWidgetContents.setLayout(layout)
        for i in range(len(unit_list)):
            layout.addWidget(QCheckBox(unit_list[i]['name']))
        layout.update()

    def add_unit(self):
        """Uses the info given by the user in the Text Edits to add
        a units information to the units.txt file.
        It will then call fill_unit_list() to add the new unit to
        the scroll area.
        """
        valid_info = False
        # Take the input from user and add the information to units.txt
        unit_name = self.ui.lineEdit.text()
        unit_url = self.ui.lineEdit_2.text()

        try:
            urllib.request.urlopen(unit_url)
        except ValueError:
            self.ui.URLErrorLabel.setText("Invalid URL! Check for https://")
        except URLError:
            self.ui.URLErrorLabel.setText("Invalid URL! Cannot be reached!")
        else:
            self.ui.URLErrorLabel.setText("")
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
                    rows = []
                    new_dict = {'name': unit_name, 'url': unit_url, 'date': date}
                    try:
                        with open('units.txt', 'r+', newline='') as csvfile:
                            reader = csv.DictReader(csvfile)
                            for row in reader:
                                rows.append(row)
                            rows.append(new_dict)
                    except IOError:
                        print("Units file does not exist")

                    with open('units.txt', 'w+', newline='') as csvfile:
                        fieldnames = ['name', 'url', 'date']
                        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                        writer.writeheader()
                        for i in range(len(rows)):
                            writer.writerow(rows[i])

                    # Maybe just add an append open and add to the end of file.

                # Opens and reads from the list in units.txt
                unit_list = []
                try:
                    with open('units.txt', 'r+', newline='') as csvfile:
                        reader = csv.DictReader(csvfile)
                        for row in reader:
                            unit_list.append(row)
                        self.all_lines = unit_list
                except IOError:
                    print("No units.txt file")

                layout = self.ui.scrollAreaWidgetContents.layout()
                if layout is None or layout == '':
                    self.fill_unit_list()
                else:
                    layout.addWidget(QCheckBox(unit_name))
                    layout.update()

    def delete_unit(self):
        """Deletes a unit from the units.txt file and
        removes its check box from the scroll area.
        """
        # Fill a list with QCheckBoxes. If a box is not checked add it to units.txt
        # This essential deletes the units that were checked.
        check_boxes = self.ui.scrollAreaWidgetContents.findChildren(QCheckBox)
        layout = self.ui.scrollAreaWidgetContents.layout()
        lines = []
        with open('units.txt', 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                lines.append(row)
        with open('units.txt', 'w') as f:
            fieldnames = ['name', 'url', 'date']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for i in range(len(lines)):
                if check_boxes[i].isChecked() is False:
                    writer.writerow(lines[i])
                else:
                    check_boxes[i].setChecked(False)
                    check_boxes[i].hide()
                    layout.update()

        unit_list = []
        try:
            with open('units.txt', 'r+', newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    unit_list.append(row)
                self.all_lines = unit_list
        except IOError:
            print("No units.txt file")

    def update_all(self):
        """Gathers and updates all the unit info for the units
        that can be found in the units.txt file.
        """
        self.ui.move(self.width + 500, self.height)
        # Start the selenium code and start scraping the listing html for information
        units = []
        for line in self.all_lines:
            units.append(line)
        self.get_info_for(units)
        print("Updates Complete")

    def generate(self):
        """Gathers data for any units that has it's check box checked.
        A data GUI is then created and shown to the user.
        """
        # Start the selenium code for the listing url for the checked listing
        check_boxes = self.ui.scrollAreaWidgetContents.findChildren(QCheckBox)
        units = []
        for i in range(len(check_boxes)):
            if check_boxes[i].isChecked() is True:
                units.append(self.all_lines[i])
                check_boxes[i].setChecked(False)
                # The only thing about the ppl is
                # that they be cray
        self.get_info_for(units)
        # Generate the data GUI to present the data gathered from the listings html
        for unit in units:
            data_win = MonthWin(unit['name'])
            data_win.show()
            data_win.activateWindow()

    def show_data_page(self):
        """Generates a data GUI window to show a user the stored
        information on a unit. Generates no new data.
        """
        self.ui.move(self.width + 500, self.height)
        check_boxes = self.ui.scrollAreaWidgetContents.findChildren(QCheckBox)
        for i in range(len(check_boxes)):
            if check_boxes[i].isChecked() is True:
                data_win = MonthWin(check_boxes[i].text())
                data_win.show()
                data_win.activateWindow()
                check_boxes[i].setChecked(False)

    def get_info_for(self, units):
        """Starts the webdriver process and sends the needed information
        to various helper functions. Moves the main window so it
        remains visible. Also clicks the inspect option of the context
        click.
        """
        self.ui.move(self.width + 500, self.height)
        # Creates a driver for chrome
        opts = Options()
        opts.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (HTML, like Gecko) "
                          "Chrome/75.0.3770.100 Safari/537.36")
        self.update_date(units)
        driver = webdriver.Chrome(chrome_options=opts)
        count = 0
        for unit in units:
            try:
                driver.get(unit['url'])  # Goes to the url listed for the unit
            except TypeError:
                print("Invalid url! Type")
            except WebDriverException:
                print("Invalid url! WebDriver")
            # Right clicks and left clicks to inspect web page elements
            if count == 0:
                time.sleep(1)
                actions = ActionChains(driver)
                actions.context_click().perform()
                time.sleep(0.5)
                pyautogui.click(150, 356)
                time.sleep(1)
            count += 1

            # Generally the functions find the data you are looking for
            # Check the file HelperFunctions to specifically see what they do
            month_list = get_month_info(driver)

            gen_data_file(month_list, unit['name'])
        # Closes chrome and everything it was using
        driver.quit()

    def edit_unit_info(self):
        check_boxes = self.ui.scrollAreaWidgetContents.findChildren(QCheckBox)
        for box in check_boxes:
            if box.isChecked():
                self.edit_win = EditWindow(box)
                self.edit_win.show()
                self.edit_win.activateWindow()
                self.edit_win.ui.Accept.clicked.connect(self.edit_name)

    def edit_name(self):
        self.edit_win.update_data()
        self.update_scroll_box()

    def update_scroll_box(self):
        name = self.edit_win.get_name()
        old_name = self.edit_win.old_unit_name
        check_boxes = self.ui.scrollAreaWidgetContents.findChildren(QCheckBox)
        for box in check_boxes:
            if box == self.edit_win.boxey:
                box.setText(name)
        self.edit_win.close()
        try:
            os.renames(old_name, name)
        except FileNotFoundError:
            print("May Not Have Changed Directory Name!\nPlease restart the program!")

        unit_list = []
        try:
            with open('units.txt', 'r+', newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    unit_list.append(row)
                self.all_lines = unit_list
        except IOError:
            print("No units.txt file")

    @staticmethod
    def update_date(units):
        current_date = str(datetime.date.today())
        remove = True
        for unit in units:
            with open('units.txt', 'r+', newline='') as inf, open('units_temp.txt', 'w', newline='') as outf:
                reader = csv.DictReader(inf.readlines())
                writer = csv.DictWriter(outf, fieldnames=['name', 'url', 'date'])
                writer.writeheader()
                for row in reader:
                    try:
                        if row['name'] == unit['name']:
                            row['date'] = current_date
                            writer.writerow(row)
                        else:
                            writer.writerow(row)
                    except TypeError:
                        print("Date could not update correctly")
                        remove = False
                writer.writerows(reader)
            if remove is True:
                os.remove('units.txt')
                os.rename('units_temp.txt', 'units.txt')

    def generate_excel(self):
        # Loop through check boxes to find out what units to view
        names = []
        check_boxes = self.ui.scrollAreaWidgetContents.findChildren(QCheckBox)
        for box in check_boxes:
            if box.isChecked():
                names.append(box.text())
        # Check for already created file and open if found
        for name in names:
            if self.has_xl_folder() is False:
                self.make_xl_folder()
        # Create if not found --Done
        # Populate with new data
            if self.has_xlsx_file(name):
                os.startfile(self.xl_folder_path + '/' + name + '.xlsx')
            else:
                self.make_xlsx_file(name)

            os.startfile(self.xl_folder_path + '/' + name + '.xlsx')

    def has_xlsx_file(self, name):
        return os.path.isfile(self.xl_folder_path + '/' + name + '.xlsx')

    def make_xlsx_file(self, name):
        wb = Workbook()
        ws0 = wb.active
        ws0.title = 'Annual Data'
        self.generate_month_sheets(name, wb)
        try:
            wb.save(self.xl_folder_path + '/' + name + '.xlsx')
        except PermissionError:
            print("File may already be in use.\nFile not saved!")

    def has_xl_folder(self):
        path_name = os.path.split(os.getcwd())
        path_name = os.path.split(path_name[0])
        path_name = os.path.split(path_name[0])
        self.xl_folder_path = path_name[0] + "/Desktop/RentalExcel"
        return os.path.isdir(self.xl_folder_path)

    def make_xl_folder(self):
        try:
            os.mkdir(self.xl_folder_path)
        except IOError:
            print("Could not create excel folder.\nQuiting program...")
            time.sleep(2)
            quit()

    @staticmethod
    def generate_month_sheets(name, wb):
        year = str(datetime.datetime.now().year)
        with open('./' + name + '/' + year + '.txt', 'r', newline='') as unit_file:
            reader = csv.DictReader(unit_file)
            for row in reader:
                title = row['month']
                if title != 'n/a':
                    wb.create_sheet(title=title)
