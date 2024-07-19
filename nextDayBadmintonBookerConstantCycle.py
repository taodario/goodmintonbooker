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


def click_date(page, desired_date):
    print("clicking date: " + desired_date + "...")
    date_selector = ".d-none [data-date-text='" + desired_date + "']"
    page.click(date_selector)


def check_element_exists(page, selector):
    # Locate the element using the selector
    element = page.locator(selector)

    # Check if the element exists by counting the number of matched elements
    if element.count() > 0:
        print("Element exists")
        return True
    else:
        print("Element does not exist")
        return False


def click_court(page, court):
    parent_element = page.locator("#tabBookingFacilities")
    parent_element.locator(f"//*[contains(text(),'{court}')]").click()
    print(f"clicked on court: {court}")


def check_element_exists_by_locator(locator):
    # Check if the element exists by counting the number of matching elements
    count = locator.count()
    return count > 0  # Return True if element exists, otherwise False


def click_time(page, timeString):
    selector_base = f"//*[contains(text(),'{timeString}')]"

    if not check_element_exists_by_locator(page.locator(selector_base).locator(
            "../..").locator("button")):
        print("button not yet enabled for time " + timeString)
        return

    time_element = page.locator(selector_base).locator("../..").locator(
        "button")
    print(f"the time element text: {time_element.text_content()}")

    # if the button doesn't have "Book Now" it will cause a Playwright issue. Skip.
    if "Book Now" not in time_element.text_content():
        print(
            f"'Book now' not the current text in button. Skipping the time {timeString}")
        return

    time_element.click()
    print(f"clicked button for time {timeString}")
    button_text = time_element.text_content()
    print(f"The text of the button is: {button_text}")
    if "Booking" in button_text:
        print("Sleeping for 10s...")
        time_module.sleep(10)  # wait 100ms

        # Commenting out screenshot code because it's not tested.
        # # take a screenshot
        # # Construct a unique filename using the current timestamp
        # timestamp = int(time_module.time() * 1000)  # Current time in milliseconds
        # filename = f"screenshot_{timestamp}.png"
        #
        # # Take a screenshot and save it with the unique filename
        # page.screenshot(path=filename)
        # print(f"Saved screenshot to {filename}")

        # Sleep for a short time to ensure unique timestamps
        time_module.sleep(1)

    if check_element_exists(page, ".recaptcha-checkbox-border"):
        print("there is a recaptcha dialog! Re-navigating to booking page...")
        navigate_to_booking_page(page)


def constant_loop_for_booking(page, dates_to_consider, times_to_consider):
    courts = ["Court 03-AC-Badminton", "Court 02-AC-Badminton",
              "Court 01-AC-Badminton"]

    while True:
        for date in dates_to_consider:
            # click the date
            print(f"clicking date {date}")
            click_date(page, date)

            for court in courts:
                print(f"looking at court and clicking {court}")
                click_court(page, court)
                print(f"on court page for {court}")
                time_module.sleep(2)

                for timeString in times_to_consider:
                    print(f"looking at time {timeString}")
                    click_time(page, timeString)

            time_module.sleep(2)

        print("Loop completed, sleeping for 10 seconds...")
        time_module.sleep(10)  # Wait for 10 seconds before the next iteration
        print("reloading page...")
        page.reload()


def run(playwright: Playwright):

    # booking date
    today = datetime.today()
    print(f"Thanks for using Badminton Booker. The day today is: {today}")

    print("firing up chromedriver!")
    chromium = playwright.chromium  # or "firefox" or "webkit".
    browser = chromium.launch(
        headless=False)
    page = browser.new_page()
    print("... logging in...")
    login(page)

    print("... logged in...")
    navigate_to_booking_page(page)

    print("... navigated to booking page...")

    dates_to_consider = ["Jul 20, 2024"]
    times_to_consider = ["10 - 10:55 AM", "11 - 11:55 AM", "12 - 12:55 PM",
                         "1 - 1:55 PM", "2 - 2:55 PM", "3 - 3:55 PM",
                         "4 - 4:55 PM"]
    constant_loop_for_booking(page, dates_to_consider, times_to_consider)

    print(
        "Attempt at booking completed. Please view logs above to see if booking was successful. Closing...")
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
