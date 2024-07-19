import pytest
from playwright.sync_api import sync_playwright


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


def test_page_title(page):
    page.goto("https://google.com")
    assert page.title() == "Google"


def test_navigation(page):
    page.goto("https://example.com")
    assert page.url == "https://example.com/"
    page.click("text=More information")
    assert "iana.org" in page.url
