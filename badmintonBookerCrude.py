from datetime import datetime, time, timedelta
import time
from playwright.sync_api import sync_playwright, Playwright
from config import USERNAME, PASSWORD


def login(page):
    print("logging in...")
    page.goto("https://recreation.utoronto.ca/home")
    page.click('#loginLinkBtn')  # clicks "Sign In"
    page.click(
        '#section-sign-in-first > div:nth-child(6) > div > button')  # clicks "Log in with UTOR ID"
    time.sleep(1)
    page.fill('#username', USERNAME)
    page.fill('#password', PASSWORD)
    time.sleep(2)
    page.click('#login-btn')
    time.sleep(5)
    page.wait_for_selector('#trust-browser-button')
    time.sleep(3)
    page.click('#trust-browser-button')
    time.sleep(5)


def navigate_to_booking_page(page):
    print("navigating to the booking page...")
    page.goto("https://recreation.utoronto.ca/booking")
    print("clicking the S&R Badminton link...")
    page.click(
        "//div[@id='divBookingProducts-large']//a[contains(@class, 'inherit-link')]//*[contains(text(), 'S&R Badminton')]/..")


def wait_until_time(desired_hour, desired_minute, desired_seconds):
    desired_time = time(desired_hour, desired_minute, desired_seconds)
    desired_datetime = datetime.combine(datetime.today(), desired_time)
    max_time = desired_datetime + timedelta(seconds=1)

    while True:
        now = datetime.now().time()
        if desired_time <= now < max_time.time():
            print("The desired time has been reached: " + desired_time.strftime("%H:%M:%S"))
            return True
        # loop every 100 ms
        time.sleep(0.1)


def check_time_and_refresh(page, desired_time):

    # Assume desired_hour is already the correct 24-hour format
    target_time = dtime(hour=desired_hour, minute=0, second=0)

    while True:
        now = datetime.now()
        time_to_target = datetime.combine(now.date(), target_time) - now

        # If more than 3 minutes to target, reload every minute
        if time_to_target > timedelta(minutes=3):
            time.sleep(
                30)  # Wait until the start of the next minute
            print("refreshing the page...")
            page.reload()
        else:
            # When less than 3 minutes to target, break out of the loop
            break

    # Final reload just before the hour
    while True:
        now = datetime.now()
        previous_hour = (desired_hour - 1) % 24

        if dtime(previous_hour, 59, 59) <= now.time() < dtime(desired_hour,
                                                              0, 1):
            print("performing the last refresh...")
            page.reload()
            break
        print("the current time is: " + now.strftime('%Y-%m-%d %H:%M:%S'))
        time.sleep(0.1)  # Check every 100 milliseconds


def click_date(page, desired_date):
    print("clicking date: " + desired_date + "...")
    date_selector = ".d-none [data-date-text='" + desired_date + "']"
    page.click(date_selector)


def select_court_and_time(page, hour):
    selector_base = "//*[contains(text(),'" + hour + " - " + hour + ":55 PM" + "')]"
    courts = ["Court 01-AC-Badminton", "Court 02-AC-Badminton",
              "Court 03-AC-Badminton"]
    for court in courts:
        parent_element = page.locator("#tabBookingFacilities")
        parent_element.locator(f"//*[contains(text(),'{court}')]").click()
        time_element = page.locator(selector_base).locator("../..").locator(
            "button")
        time_element.click()
        button_text = time_element.text_content()
        print(f"The text of the button is: {button_text}")


def run(playwright: Playwright):

    DESIRED_DATE = "Jul 17, 2024"
    # should set it to be able to be AM and PM because of weekends
    DESIRED_HOUR = "8"  # the full string for xpath would be: 7 - 7:55 PM

    chromium = playwright.chromium  # or "firefox" or "webkit".
    browser = chromium.launch(
        headless=False)  # if headless is false, there will be a popup window
    page = browser.new_page()

    login(page)
    navigate_to_booking_page(page)
    check_time_and_refresh(page, int(DESIRED_HOUR))
    click_date(page, DESIRED_DATE)
    select_court_and_time(page, DESIRED_HOUR)

    browser.close()


with sync_playwright() as playwright:
    run(playwright)
