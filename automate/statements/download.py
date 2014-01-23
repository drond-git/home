#!/usr/bin/python

import time

from common import app

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
                # TODO(drond): Extract date from: u"Download PDF\n'January 13, 2014 Statement'"
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


def SigninAmex(browser):
    # Open the main page.
    browser.get('https://www.americanexpress.com/')
    assert 'American Express' in browser.title
    # Waiting for sign in to be performed (manually, for now).
    e = WebDriverWait(browser, 60).until(EC.presence_of_element_located((By.LINK_TEXT, "Log Out")))


def Click(browser, e):
    # Using e.click() raises exception, so this is what we do:
    ActionChains(browser).move_to_element(e).move_by_offset(1, 1).click().perform()

def _Sub(browser):
    browser.get('https://www.americanexpress.com/')
    # Sometimes they have popups that need to be dismissed. We do this here, for now.
    popup_close_buttons = browser.find_elements_by_xpath('//button[@title="Close"]')
    for b in popup_close_buttons:
        if b.is_displayed():
            b.click()
    # Navigate to the statements download page.
    time.sleep(0.3)
    browser.find_element_by_xpath('//*[@id="iNav_MyAccount"]').click()
    time.sleep(0.3)
    browser.find_element_by_xpath('//*[@id="menu_myacct_viewstmt"]').click()
    time.sleep(0.3)
    
def DownloadAmexOne(browser, account_identifier):
    """The account_identifier is the id of the link."""
    _Sub(browser)
    # Determine what statements we'll download.
    Click(browser, browser.find_element_by_xpath('//*[@id="expandTP"]'))  # Show dropdown.
    periods_list = browser.find_element_by_xpath('//ul[@class="periodSelectMenu"]')
    pl = periods_list.find_elements_by_xpath('li/a')
    download_these = []
    for i, item in enumerate(pl):
        text = item.text
        print "Checking item %r" % text
        if ('Statement' in text or 'Summary' in text or '\n' not in text):
            download_these.append((i, text))
    print "Will download: %r" % download_these
    Click(browser, browser.find_element_by_xpath('//*[@id="expandTP"]'))  # Hide dropdown.
    time.sleep(0.5)
    # We iterate over all periods we decided to download.
    for download_i, text in download_these:
        print "Preparing to download item %r %r" % (download_i, text)
        # Show dropdown.
        Click(browser, browser.find_element_by_xpath('//*[@id="expandTP"]'))
        print "sleeping 1"
        time.sleep(3)
        # Click on the option we want for this iteration.
        periods_list = browser.find_element_by_xpath('//ul[@class="periodSelectMenu"]')
        pl = periods_list.find_elements_by_xpath('li/a')
        item = pl[download_i]
        Click(browser, item)
        print "Clicked to select item %r" % item.text
        time.sleep(3.0)
        # TODO(drond): Verify that select options are set correctly. They are, by default, now.
        pass
        # Clicking to open the download dialog is not simple. Here's one way:
        print "Clicking to download item %r" % item.text
        e = browser.find_element_by_xpath('//a/span[text()="Download"]')
        Click(browser, e)
        print "Downloaded item %r" % item.text
        # Enable extended details in the statements (why not)!
        extra_details_checkbox = browser.find_element_by_xpath('//*[@id="downloadWithETD"]')
        if not extra_details_checkbox.is_selected():
            extra_details_checkbox.click()
            assert extra_details_checkbox.is_selected()
        # Start the download.
        e = browser.find_element_by_xpath('//*[@id="downloadContinueButton"]')
        Click(browser, e)


def DownloadAmexAll(browser):
    DownloadAmexOne(browser, "")



# "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --user-data-dir=/Users/vsh/Downloads/Selenium/chrome-profiles --profile-directory=Automation
chrome_options = Options()
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--user-data-dir=/Users/vsh/Downloads/Selenium/chrome-profiles")
chrome_options.add_argument("--profile-directory=Automation")

# Per https://sites.google.com/a/chromium.org/chromedriver/capabilities docs:
prefs = {
    "savefile.default_directory" : "/Users/vsh/Downloads/Selenium/chrome-downloads",
    "download.default_directory" : "/Users/vsh/Downloads/Selenium/chrome-downloads",
    "download.directory_upgrade" : 1,
    "download.prompt_for_download" : 1,
    }
prefs = {
    "savefile": { "default_directory" : "/Users/vsh/Downloads/Selenium/chrome-downloads"},
    "download": {
        "default_directory" : "/Users/vsh/Downloads/Selenium/chrome-downloads",
        "directory_upgrade" : 1,
        "prompt_for_download": 1,
        },
    }
chrome_options.add_experimental_option("prefs", prefs)

if False:
  browser = webdriver.Chrome(executable_path="/Users/vsh/Downloads/Selenium/chromedriver", chrome_options=chrome_options)

# Most likely plan:
#   - Edit profile's Preferences to set the downloads directory, so I don't have to maintain that
#     aspect manually.
#   - Proceed "one file downloaded at a time.
#   - List all files in download directory, kick off file download, then wait until there's one new file. In-progress download files have .crdownload extensions.
#   - Find a way to be sure the download ended successfully. See http://stackoverflow.com/questions/559096/check-whether-a-pdf-file-is-valid-python.
#   - Pass the one new file to a function that will move and rename it to represent the statement's period.


if False:
    SigninBoa(browser)
    DownloadBoaAll(browser)

if False:
    SigninAmex(browser)
    DownloadAmexAll(browser)

# Exit before we quit the browser -- leave it for debugging.
##exit(0)

##time.sleep(180.0)
##browser.quit()


## elem = browser.find_element_by_name('p')  # Find the search box
## elem.send_keys('seleniumhq' + Keys.RETURN)


ARGS = app.ARGS
ARGS.PARSER.add_argument('foo')


def main(argv):
  print "RUN MY MAIN with argv %r" % argv
  print 'ARG --foo = %r' % ARGS.foo


if __name__ == '__main__':
  app.run()
