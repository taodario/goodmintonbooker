import pytest
from playwright.sync_api import sync_playwright
import time as time_module


def take_screenshot(page):
    timestamp = int(
        time_module.time() * 1000)  # current time in milliseconds
    filename = f"../screenshots/screenshot_{timestamp}.png"
    page.screenshot(path=filename)
    print(f"Saved screenshot to {filename}")


@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        yield browser
        browser.close()


@pytest.fixture(scope="session")
def context(browser):
    context = browser.new_context()
    yield context
    context.close()


@pytest.fixture(scope="function")
def page(context):
    page = context.new_page()
    yield page
    page.close()


def test_take_screenshot(page):
    page.goto("https://google.com")
    take_screenshot(page)


if __name__ == "__main__":
    pytest.main()
