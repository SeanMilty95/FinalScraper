import time
import csv
import os
import datetime
from decimal import Decimal

from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
import pyautogui


def find_month(soup):
    """Finds the html code section that contains the month name and the
    year. Returns the month name first and year second.
    """
    month_div = soup.find(class_='month')
    month_names = month_div.find_all('span')
    year = month_names[0].contents[1]
    month_name = month_names[0].find('span').contents[0]
    year = year.strip()
    return month_name, year


def get_available_days(days):
    """Looks through the calendar html and finds all references to
    the class name 'day-template--available-stay'.
    """
    available_days = [tuple]
    available_days.pop()

    for i in range(len(days)):
        av_stay = days[i].find(class_='day-template--available-stay')
        if av_stay is not None:
            day_num = days[i].find(class_='day-template__day').contents[0]
            day_rate = days[i].find(class_='day-template__rate')
            if day_rate is not None and len(day_rate.contents) > 0:
                day_rate2 = day_rate.contents[0]
            else:
                day_rate2 = None
            aval_rate = (day_num, day_rate2)
            available_days.append(aval_rate)

    return available_days


def get_booked_days(days):
    """Finds all references to the class name 'day-template--disabled'"""
    booked_days = []

    for i in range(len(days)):
        booked = days[i].find(class_='day-template--disabled')
        if booked is not None:
            day_num = days[i].find(class_='day-template__day').contents[0]
            booked_days.append(day_num)
    return booked_days


def get_past_days(days):
    """Finds all references to the class name 'day-template--past'"""
    past_days = []

    for i in range(len(days)):
        past = days[i].find(class_='day-template--past')
        if past is not None:
            day_num = days[i].find(class_='day-template__day').contents[0]
            past_days.append(day_num)
    return past_days


def get_avg_listed_rate(soup):
    """Finds and returns the given average rate from the listing page."""
    rate = soup.find(class_='rental-price__amount').contents[0]
    return rate


def next_calendar(driver):
    """Finds the next button for the calendar section and virtually clicks it."""
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
    """Grabs all the html from the vrbo listing webpage."""
    # elem = driver.find_element_by_xpath("//*")
    # source_code = elem.get_attribute("innerHTML")#used to be outer
    source_code = driver.execute_script("return document.body.innerHTML")
    soup = BeautifulSoup(source_code, 'html.parser')
    return soup


def calculate_avg(avail):
    """Calculates the average rate based on actual rental cost
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
    """Checks if the calendar actually lists daily prices."""
    has = False
    for days in available_days:
        if days[1] is not None:
            has = True
    return has


def print_current_unit_options(unit_list):
    """Prints the units that are stored in the units.txt file
    generated earlier in the code. These values are stored in
    the global list unit_list. Returns a list of the individual
    lines which contain the information for a unit.
    """
    # print the values able to be chosen
    lines_list = []
    for line in unit_list:
        line = line.split()
        lines_list.append(line)
        print(line[0])
    print("all\n")
    return lines_list


def gen_data_file(month_list, selected_unit):
    """Creates or appends a file to hold the data for an individual unit.
    A list is created for each piece of information because it is
    gathered for four different months.
    The information is stored in the file using a csv dictionary format.
    """
    append = False

    # initialize lists
    new_avail_days = []
    new_booked_days = []
    new_revenue = []
    year = []
    month_name = []
    new_given = 0
    rating = 0
    occupancy = []

    # Do maths for updated values
    for month in month_list:
        if new_given != month[2]:
            new_given = month[2]
        new_avail_days.append(month[5])
        new_booked_days.append(month[6])
        new_revenue.append(month[8])
        year.append(month[1])
        month_name.append(month[0])
        rating = month[9]
        occupancy.append(month[10])

    # Holds the rows from the reader
    rows = []
    new_dict = []

    for i in range(4):
        new_dict.append(
            {'year': year[i], 'month': month_name[i], 'given_rate': new_given, 'available_days': new_avail_days[i],
             'booked_days': new_booked_days[i],
             'revenue': new_revenue[i], 'rating': rating, 'occupancy': occupancy[i]})

    current_year = str(datetime.datetime.now().year)
    if os.path.exists('./' + selected_unit) is False and os.path.isdir('./' + selected_unit) is False:
        try:
            os.mkdir('./' + selected_unit)
        except OSError:
            print("Cannot create directory!")
    try:
        with open('./' + selected_unit + '/' + current_year + '.txt', 'r+', newline='') as csvfile:
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

    with open('./' + selected_unit + '/' + current_year + '.txt', 'w+', newline='') as csvfile:
        fieldnames = ['month', 'year', 'given_rate', 'available_days', 'booked_days', 'revenue', 'rating', 'occupancy']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for i in range(len(rows)):
            writer.writerow(rows[i])


def get_month_info(driver):
    """Gathers data from the sites html and returns a list holding
    the data.
    The variable month_list holds a list of months and each month
    has its own 'packet' of data.
    """
    # Get the info from 4 calendars
    month_list = []
    given_rate = 0
    for i in range(4):
        if i > 0:
            next_calendar(driver)
        soup = get_soup(driver)
        month_table = soup.find(class_='month-table')
        if month_table is None:
            reload_page()
            soup = get_soup(driver)
            month_table = soup.find(class_='month-table')
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
        revenue = month_revenue(booked_days, cal_prices,
                                average_rate, given_rate)
        occupancy = calc_monthly_occupancy_rate(available_days,
                                                booked_days,
                                                past_days)
        packet = (month_name, year, given_rate, average_rate,
                  cal_prices, available_days, booked_days,
                  past_days, revenue, rating, occupancy)
        month_list.append(packet)

    return month_list


# may need to change and add to packet for Month_List
def calc_monthly_occupancy_rate(av_days, book_days, past):
    """Calculates the occupancy rate for a month"""
    days_occupied = len(book_days)
    all_days = union(av_days, book_days, past)
    total_days = len(all_days)
    occupancy_rate = Decimal((days_occupied / total_days) * 100)
    occupancy_rate = round(occupancy_rate, 1)
    occupancy_rate = (str(occupancy_rate))
    return occupancy_rate


def union(list1, list2, list3):
    """Finds and returns the unique days from the various lists
    of days with the goal of finding the total days in a month.
    """
    # Adds only unique days to the list
    final_list = list(set().union(list1, list2, list3))
    return final_list


def month_revenue(booked, calced, avg, given):
    """Calculates the revenue generated in a month."""
    num_days = len(booked)
    if calced:
        revenue = num_days * avg
    else:
        given = given.strip('$')
        given = int(given)
        revenue = num_days * given
    return str(revenue)


def get_total_revenue(month_list):
    """Calculates the total revenue for the months stored in
    the given parameter.
    """
    total = 0
    for month in month_list:
        total += int(month[8])
    return str(total)


def reload_page():
    """Reloads the page and scroll to the listings calendar."""
    pyautogui.hotkey('f5')
    time.sleep(2)
    pyautogui.scroll(-6000)
    time.sleep(2)


def find_rating(soup):
    """Finds and returns the average rating of a unit."""
    rating_div = soup.find(class_="review-summary__header-ratings-average")
    contents = rating_div.contents
    contents2 = contents[0].split('/')
    rating = contents2[0]
    return rating
