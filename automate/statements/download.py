#!/usr/bin/python

import time

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0


def SigninBoa(browser):
    # Open the main page.
    browser.get('http://www.bankofamerica.com')
    assert 'Bank of America' in browser.title
    # If this is the first session ever, give 60 seconds to log in, then logout with the user ID saved.
    e = WebDriverWait(browser, 60).until(EC.presence_of_element_located((By.ID, "multiID")))
    # Help sign-in by navigating to the page that only requires password input.
    sign_in = browser.find_element_by_link_text("Sign In")
    sign_in.click()
    password_input = WebDriverWait(browser, 60).until(EC.presence_of_element_located((By.NAME, "password")))
    password_input.click()
    # Waiting for sign in to be performed (manually, for now).
    e = WebDriverWait(browser, 60).until(EC.presence_of_element_located((By.LINK_TEXT, "Sign Off")))


def DownloadBoaOne(browser, account_identifier):
    """The account_identifier is the id of the link."""
    browser.get("https://secure.bankofamerica.com/myaccounts")
    # Click <a> id="MyAccess Checking - 7770"
    browser.find_element_by_id(account_identifier).click()
    # Click <a> name="Statements & Documents"
    browser.find_element_by_name("Statements & Documents").click()
    # Wait for the tab to become visible.
    WebDriverWait(browser, 60).until(EC.visibility_of_element_located((By.ID, "FilterDocumentsForm")))
    time.sleep(1.0)  # The click may be happening too soon without this.
    # Find the table with all the statements, which we will iterate.
    t = browser.find_element_by_xpath('//table[@id="documentInboxModuleStatementTable"]')
    trs = t.find_elements_by_xpath('//tbody/tr[@class="odd" or @class="even"]')
    for tr in trs:  
        print tr.text
        s = tr.find_element_by_xpath('td/a')
        s.click()  # Opens the context menu.
        time.sleep(0.5)
        links = browser.find_elements_by_partial_link_text("Download PDF\n")
        for l in links:
            if l.is_displayed():
                print l.text
                ##l.click()
                ActionChains(browser).move_to_element_with_offset(l, 5, 5).click().perform()
                # TODO(vsh): Extract date from: u"Download PDF\n'January 13, 2014 Statement'"
                ##statement_date = l.text
                break
        # Now scroll down so the next statement is visible.
        browser.execute_script("window.scrollBy(0, %d);" % tr.size['height'])
        time.sleep(0.5)


def DownloadBoaAll(browser):
    # Until it's possible to control where files are downloaded, we have to do
    # one account only -- files for different accounts (given the same statement
    # date) will have the same name.
    DownloadBoaOne(browser, "MyAccess Checking - 7770")
    DownloadBoaOne(browser, "Amway Platinum Plus Visa - 9229")
    DownloadBoaOne(browser, "AAA East Central Platinum Plus Visa - 7257")


# "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --user-data-dir=/Users/vsh/Downloads/Selenium/chrome-profiles --profile-directory=Automation
chrome_options = Options()
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--user-data-dir=/Users/vsh/Downloads/Selenium/chrome-profiles")
chrome_options.add_argument("--profile-directory=Automation")

browser = webdriver.Chrome(
    executable_path="/Users/vsh/Downloads/Selenium/chromedriver",
    chrome_options=chrome_options)

SigninBoa(browser)
DownloadBoaAll(browser)

# Exit before we quit the browser -- leave it for debugging.
exit(0)

time.sleep(180.0)
browser.quit()


## elem = browser.find_element_by_name('p')  # Find the search box
## elem.send_keys('seleniumhq' + Keys.RETURN)
