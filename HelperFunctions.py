from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
from decimal import Decimal
import time
import datetime
import csv
import pyautogui


def find_month(soup):
    """
    Finds the html code section that contains the month
    name and the year. returns the month name first and year second.
    """
    month_div = soup.find(class_='month')
    month_names = month_div.find_all('span')
    year = month_names[0].contents[1]
    month_name = month_names[0].find('span').contents[0]
    year = year.strip()
    return month_name, year


def get_available_days(days):
    """
    Looks through the calendar html and finds all references to
    the class name 'day-template--available-stay'.
    """
    available_days = [tuple]
    available_days.pop()

    for i in range(len(days)):
        av_stay = days[i].find(class_='day-template--available-stay')
        if av_stay is not None:
            day_num = days[i].find(class_='day-template__day').contents[0]
            day_rate = days[i].find(class_='day-template__rate')
            day_rate2 = None
            if day_rate is not None and len(day_rate.contents) > 0:
                day_rate2 = day_rate.contents[0]
            else:
                day_rate2 = None
            aval_rate = (day_num, day_rate2)
            available_days.append(aval_rate)

    return available_days


def get_booked_days(days):
    """
    Finds all references to the class name 'day-template--disabled'
    """
    booked_days = []

    for i in range(len(days)):
        booked = days[i].find(class_='day-template--disabled')
        if booked is not None:
            day_num = days[i].find(class_='day-template__day').contents[0]
            booked_days.append(day_num)
    return booked_days


def get_past_days(days):
    """
    Finds all references to the class name 'day-template--past'
    """
    past_days = []

    for i in range(len(days)):
        past = days[i].find(class_='day-template--past')
        if past is not None:
            day_num = days[i].find(class_='day-template__day').contents[0]
            past_days.append(day_num)
    return past_days


def get_avg_listed_rate(soup):
    """
    Finds and returns the given average rate from the listing page.
    """
    rate = soup.find(class_='rental-price__amount').contents[0]
    return rate


def next_calendar(driver):
    """
    Finds the next button for the calendar section and virtually clicks it.
    """
    rates_elem = None
    try:
        rates_elem = driver.find_element_by_class_name('rate-details')
    except NoSuchElementException:
        time.sleep(1)
        print("Rate-details element not found in the gathered HTML")
    if rates_elem is not None:
        actions = ActionChains(driver)
        actions.move_to_element(rates_elem)
        actions.perform()
    time.sleep(0.3)
    next_cal_elem = driver.find_element_by_class_name('cal-controls__button--next')
    ActionChains(driver).click(next_cal_elem).perform()


def get_soup(driver):
    """
    Grabs all the html from the vrbo listing webpage.
    """
    # elem = driver.find_element_by_xpath("//*")
    # source_code = elem.get_attribute("innerHTML")#used to be outer
    source_code = driver.execute_script("return document.body.innerHTML")
    soup = BeautifulSoup(source_code, 'html.parser')
    return soup


def calculate_avg(avail):
    """
    Calculates the average rate based on actual rental cost
    listed in the calendar.
    """
    int_list = []
    num_sum = 0
    avg = 0
    for day in avail:
        if day[1] is not None:
            num = day[1].strip('$')
            num = int(num)
            int_list.append(num)
    length = len(int_list)
    for i in range(length):
        num_sum += int_list[i]
    if length != 0:
        avg = num_sum / length
    return int(avg)


def have_calendar_prices(available_days):
    """
    Checks if the calendar actually lists daily prices.
    """
    has = False
    for days in available_days:
        if days[1] is not None:
            has = True
    return has


def Add_New_Unit():
    """
    Adds a new unit to the units list.
    """
    # Add new unit info to units.txt. Creates the file if it does not exist
    add_unit = input("Add new unit information yes or no? ")
    print()
    add_unit = add_unit.upper()
    if add_unit == 'YES' or add_unit == 'Y':
        unit_name = input("Enter unit name: ")
        unit_url = input("Enter the url for the listing: ")
        date = str(datetime.date.today())
        unit_info = unit_name + ' ' + unit_url + ' ' + date + '\n'
        url_file = open('units.txt', 'a+')
        url_file.write(unit_info)
        url_file.close()


def print_current_unit_options(unit_list):
    # print the values able to be chosen
    lines_list = []
    for line in unit_list:
        line = line.split()
        lines_list.append(line)
        print(line[0])
    print("all\n")
    return lines_list


def choose_unit(lines_list):
    url_target = ''
    # Ask what unit info you want to generate
    selected_unit = input("Select a unit from the above list to generate data.:")
    for line in lines_list:
        if selected_unit == line[0]:
            url_target = line[1]
    if selected_unit == "all":
        print("Updating all unit information.")
    elif url_target == '':
        print("Not a valid option")
    return url_target, selected_unit


def file_output(Month_List, occupancy_rates, tot_rev, selected_unit):
    # Send acquired data to data file.
    data_file = open(selected_unit + '-data.txt', 'w+')
    data_file.write("Information gathered on " + str(datetime.date.today()) + '\n')
    count = 0
    days_unbooked = 0
    for month in Month_List:
        data_file.write(month[0] + ' ' + month[1] + '\n')
        data_file.write("Given Rate: " + month[2] + ' ' + "Calculated Rate: " + '$' + str(month[3]) + '\n')

        data_file.write("Available Days: ")
        days_unbooked += len(month[5])
        for i in range(len(month[5])):
            data_file.write(month[5][i][0] + ' ')
        data_file.write("\nBooked Days: ")
        for i in range(len(month[6])):
            data_file.write(month[6][i] + ' ')
        data_file.write("\nPast Days: ")
        for i in range(len(month[7])):
            data_file.write(month[7][i] + ' ')
        data_file.write("\nOccupancy Rate: " + occupancy_rates[count] + '%')
        data_file.write("\nEstimated Revenue: $" + month[8])
        count += 1
        data_file.write('\n')
        data_file.write('\n')

    data_file.write("\n\nEstmated Toatal Revenue: $" + tot_rev)
    data_file.write("\nDays Unbooked: " + str(days_unbooked))

    data_file.close()


def gen_data_file(Month_List, occupancy_rates, tot_rev, selected_unit):
    append = False

    # initialize lists
    new_avail_days = []
    new_booked_days = []
    new_revenue = []
    year = []
    month_name = []
    new_given = 0
    rating = 0

    # Do maths for updated values
    for month in Month_List:
        if new_given != month[2]:
            new_given = month[2]
        new_avail_days.append(month[5])
        new_booked_days.append(month[6])
        new_revenue.append(month[8])
        year.append(month[1])
        month_name.append(month[0])
        rating = month[9]

    # Holds the rows from the reader
    rows = []
    new_dict = []

    for i in range(4):
        new_dict.append(
            {'year': year[i], 'month': month_name[i], 'given_rate': new_given, 'available_days': new_avail_days[i],
             'booked_days': new_booked_days[i],
             'revenue': new_revenue[i], 'rating': rating})

    try:
        with open(selected_unit + 'Specs.txt', 'r+', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                rows.append(row)

    except IOError:
        print("Data File Does Not Exist")
        append = True

    if append is False:
        for i in range(len(rows)):
            for k in range(4):
                if rows[i]['year'] == year[k] and rows[i]['month'] == month_name[k]:
                    rows[i] = new_dict[k]
                elif i == len(rows):
                    rows.append(new_dict[k])
                else:
                    continue
    else:
        for i in range(4):
            rows.append(new_dict[i])

    with open(selected_unit + 'Specs.txt', 'w+', newline='') as csvfile:
        fieldnames = ['month', 'year', 'given_rate', 'available_days', 'booked_days', 'revenue', 'rating']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for i in range(len(rows)):
            writer.writerow(rows[i])


def Get_Month_Info(driver):
    # Get the info from 4 calendars
    Month_List = []
    given_rate = 0
    cal_prices = False
    for i in range(4):
        if i > 0:
            next_calendar(driver)
        soup = get_soup(driver)
        # print(soup)
        # rates = soup.find(id_="rates-availability") //not correct
        # print(rates)
        month_table = soup.find(class_='month-table')
        if month_table is None:
            reload_page()
            soup = get_soup(driver)
            month_table = soup.find(class_='month-table')
            # print(month_table)
        # print(month_table)
        days = month_table.find_all(class_='day')
        available_days = get_available_days(days)
        cal_prices = have_calendar_prices(available_days)
        month_name, year = find_month(soup)
        rating = find_rating(soup)
        booked_days = get_booked_days(days)
        past_days = get_past_days(days)
        if cal_prices:
            average_rate = calculate_avg(available_days)
        else:
            average_rate = 0
        if i == 0:
            given_rate = get_avg_listed_rate(soup)
        revenue = month_revenue(booked_days, cal_prices, average_rate, given_rate)
        packet = (month_name, year, given_rate, average_rate, cal_prices, available_days, booked_days,
                  past_days, revenue, rating)
        Month_List.append(packet)

    return Month_List


# may need to change and add to packet for Month_List
def calc_monthly_occupancy_rate(month_list):
    occupancy_rates = []
    for month in month_list:
        days_occupied = len(month[6])
        all_days = Union(month[5], month[6], month[7])
        total_days = len(all_days)
        occupancy_rate = Decimal((days_occupied / total_days) * 100)
        occupancy_rate = round(occupancy_rate, 1)
        occupancy_rates.append(str(occupancy_rate))
    return occupancy_rates


def Union(list1, list2, list3):
    # Adds only unique days to the list
    final_list = list(set().union(list1, list2, list3))
    return final_list


def month_revenue(booked, calced, avg, given):
    revenue = 0
    num_days = len(booked)
    if calced:
        revenue = num_days * avg
    else:
        given = given.strip('$')
        given = int(given)
        revenue = num_days * given
    return str(revenue)


def get_total_revenue(Month_List):
    total = 0
    for month in Month_List:
        total += int(month[8])
    return str(total)


def reload_page():
    #pyautogui.hotkey('f5')
    #time.sleep(2)
    pyautogui.scroll(-6000)
    time.sleep(2)

def find_rating(soup):
    rating_div = soup.find(class_="review-summary__header-ratings-average")
    contents = rating_div.contents
    contents2 = contents[0].split('/')
    rating = contents2[0]
    return rating
