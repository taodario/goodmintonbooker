from datetime import datetime, time, timedelta
import time as time_module
from playwright.sync_api import sync_playwright, Playwright
from config import USERNAME, PASSWORD


def login(page):
    print("... logging in...")
    page.goto("https://recreation.utoronto.ca/home")
    page.click('#loginLinkBtn')  # clicks "Sign In"
    page.click(
        '#section-sign-in-first > div:nth-child(6) > div > button')  # clicks "Log in with UTOR ID"
    time_module.sleep(1)
    page.fill('#username', USERNAME)
    page.fill('#password', PASSWORD)
    time_module.sleep(2)
    page.click('#login-btn')
    time_module.sleep(5)
    print("ACTION: Please check phone and approve DUO Verification!")
    page.wait_for_selector('#trust-browser-button')
    print("DUO Verification has been approved!")
    time_module.sleep(3)
    page.click('#trust-browser-button')
    time_module.sleep(5)


def navigate_to_booking_page(page):
    print("... navigating to the booking page...")
    page.goto("https://recreation.utoronto.ca/booking")
    print("... clicking the S&R Badminton link...")
    page.click(
        "//div[@id='divBookingProducts-large']//a[contains(@class, 'inherit-link')]//*[contains(text(), 'S&R Badminton')]/..")


# recommended that desired_seconds is the 59th second. (1 second till the next min)
def wait_until_time(desired_hour, desired_minute, desired_second):
    desired_time = time(desired_hour, desired_minute, desired_second)
    desired_time_string = desired_time.strftime("%H:%M:%S")

    desired_datetime = datetime.combine(datetime.today(), desired_time)
    max_time = desired_datetime + timedelta(seconds=1)

    while True:
        now = datetime.now().time()
        if desired_time <= now < max_time.time():
            print("The desired time has been reached: " + desired_time.strftime(
                "%H:%M:%S"))
            return True
        # loop every 100 ms
        time_module.sleep(0.1)
        print(
            "... waiting until time is: " + desired_time_string + "... current time is " + now.strftime(
                "%H:%M:%S"))


def check_time_and_refresh(page, desired_hour, desired_minute, desired_second):
    wait_until_time(desired_hour, desired_minute, desired_second)
    print("refreshing the page now...")
    page.reload()


def click_date(page, desired_date):
    print("clicking date: " + desired_date + "...")
    date_selector = ".d-none [data-date-text='" + desired_date + "']"
    page.click(date_selector)


def select_court_and_time(page, timeString):
    selector_base = f"//*[contains(text(),'{timeString}')]"
    courts = ["Court 03-AC-Badminton", "Court 02-AC-Badminton",
              "Court 01-AC-Badminton"]
    for court in courts:
        print(f"on court page {court}")
        parent_element = page.locator("#tabBookingFacilities")
        parent_element.locator(f"//*[contains(text(),'{court}')]").click()
        time_element = page.locator(selector_base).locator("../..").locator(
            "button")
        print(f"Time element text: {time_element.text_content()}")
        if "Book Now" not in time_element.text_content():
            print("'Book now' not the current text in button")
            continue
        time_element.click()
        button_text = time_element.text_content()
        # TODO:
        print(f"The text of the button is: {button_text}")


def refresh_every_minute_until_two_minutes_away(page, hour, minute, second):
    """
    If the given time (hour, minute, second) is more than 2 minutes away from the current time,
    refresh every minute.

    :param page: page object
    :param hour: Desired hour (0-23)
    :param minute: Desired minute (0-59)
    :param second: Desired second (0-59)
    """
    desired_time = datetime.combine(datetime.today(), datetime.min.time()).replace(hour=hour, minute=minute, second=second)
    while True:
        now = datetime.now()
        time_difference = desired_time - now

        if time_difference.total_seconds() <= 120:
            print("The time is within 2 minutes. Stopping refresh.")
            break

        print("refreshed!")
        print(f"Current time: {now.strftime('%H:%M:%S')}. Refreshing in 1 minute...")
        print("refreshing...")
        page.reload()
        time_module.sleep(60)  # Wait for 1 minute


def run(playwright: Playwright):

    # booking date
    today = datetime.today()
    print(f"Thanks for using Badminton Booker. The day today is: {today}")
    month = input("Enter the MONTH of desired booking date (e.g., Jul): ")
    day = input("Enter the DAY of desired booking date (e.g., 17): ")
    year = input("Enter the YEAR of desired booking date (e.g., 2024): ")

    # time and date as it appears on the UofT Booking page
    desired_date = f"{month} {day}, {year}"
    desired_time = input(
        "Enter the time as it appears (e.g., '7 - 7:55 AM', '6 - 6:55 PM'): ")

    # time to perform the page reload
    refresh_hour = int(
        input("Enter the HOUR you want to refresh the page and hit book (1-12): "))
    refresh_minute = int(
        input("Enter the MINUTE you want to refresh the page and hit book (0-59): "))
    refresh_second = int(
        input("Enter the SECOND you want to refresh the page and hit book (0-59): "))
    am_or_pm = input(
        "Is the time you want to refresh the page and hit book AM or PM? ").lower()
    # Adjust refresh_hour for AM or PM (convert to 24h)
    if am_or_pm.lower() == "pm" and refresh_hour != 12:
        refresh_hour += 12
    elif am_or_pm.lower() == "am" and refresh_hour == 12:
        refresh_hour = 0

    print("firing up chromedriver!")
    chromium = playwright.chromium  # or "firefox" or "webkit".
    browser = chromium.launch(
        headless=True)  # TODO : make headless true for the real thing!
    page = browser.new_page()
    print("... logging in...")
    login(page)

    print("... logged in...")
    navigate_to_booking_page(page)

    # if the time is more than 5 minutes away, reload every minute
    refresh_every_minute_until_two_minutes_away(page, refresh_hour, refresh_minute, refresh_second)

    print("... navigated to booking page...")
    print(
        f"INFO: refreshing at {refresh_hour}:{refresh_minute}:{refresh_second}")
    check_time_and_refresh(page, refresh_hour, refresh_minute, refresh_second)

    print(f"... refreshed... clicking date {desired_date} now...")
    click_date(page, desired_date)

    print("clicked date... booking court at the desired hour now...")
    select_court_and_time(page, desired_time)

    print(
        "Attempt at booking completed. Please view logs above to see if booking was successful. Closing...")
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
