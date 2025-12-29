from selenium.common import NoSuchElementException, WebDriverException
from selenium.webdriver import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
import time
import os
import random
import logging
import json
import sys

def scrape_county(county, driver):
    min_acres = 1 # CHANGE MIN AS NEEDED
    max_acres = -1
    max_acres_searched = -1
    exported_all = False
    splitting_listings = False

    # search for county/city
    searchbar_placeholder = driver.find_element(By.CLASS_NAME, 'search-bar-placeholder')
    searchbar_placeholder.click()
    human_delay(2, 3)
    searchbar_input = driver.find_element(By.CLASS_NAME, 'search-bar-input')
    searchbar_input.send_keys(county + " County, TX") # CHANGE STATE CODE AS NEEDED
    searchbar_input.send_keys(Keys.ENTER)
    logging.info(f"Searching listings for {county}")
    human_delay(6, 7)

    # inner loop iterates through acre filters
    while not exported_all:
        try:
            # find filter button
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'mdc-button'))
            )
            filter_button = driver.find_element(By.CLASS_NAME, 'mdc-button')
            filter_button.click()
            human_delay(4, 5)

            # enter minimum acres
            min_acreage_threshold_input = driver.find_element(By.CSS_SELECTOR, "input[placeholder='Min acres']")
            min_acreage_threshold_input.send_keys(Keys.BACKSPACE)
            min_acreage_threshold_input.send_keys(str(min_acres))
            min_acres_searched = min_acres
            human_delay(1, 1.8)

            # delete max acres in case
            max_acreage_threshold_input = driver.find_element(By.CSS_SELECTOR, "input[placeholder='Max acres']")
            max_acreage_threshold_input.send_keys(Keys.BACKSPACE)
            human_delay(1, 1.8)

            # get amount of listings without searching
            apply_filter_button = driver.find_element(By.CSS_SELECTOR, 'a[data-cy="applyFilters"]')
            apply_filter_button_text = apply_filter_button.text.strip()

            # if too many listings. must be < 1000
            if "999+" in apply_filter_button_text:
                logging.info(f"Too many listings for {county}. Splitting.")

                # calculate max acres and search it
                max_acres = min_acres + 1
                max_acreage_threshold_input = driver.find_element(By.CSS_SELECTOR, "input[placeholder='Max acres']")
                max_acreage_threshold_input.send_keys(Keys.BACKSPACE)
                human_delay(.5, 1.2)
                max_acreage_threshold_input.send_keys(str(max_acres))
                human_delay(1, 1.8)
                max_acreage_threshold_input.send_keys(Keys.ENTER)

                # for logging purposes
                min_acres_searched = min_acres
                max_acres_searched = max_acres

                # new minimum acre value, reset variables
                min_acres = max_acres
                max_acres = -1
                splitting_listings = True
            elif "Show 0 Listings" in apply_filter_button.text:
                logging.info(f"0 listings for {county}. Exiting county.")
                close_filters_button = driver.find_element(By.CSS_SELECTOR, '.button-close')
                close_filters_button.click()
                break
            else:
                # listings < 1000
                # search
                min_acreage_threshold_input.send_keys(Keys.ENTER)

                # reset variables
                max_acres_searched = -1
                splitting_listings = False
            human_delay(2, 3)

            # check for popup
            try:
                cancel_button = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//button[.//span[normalize-space()='Cancel']]"))
                )
                cancel_button.click()
                human_delay(2, 3)
            except:
                print("No popup")

            # get number of listings
            listing_count_element = driver.find_element(By.CSS_SELECTOR, "span[data-cy='resultsCount']")
            listing_count = listing_count_element.text

            # export listings
            export_button = driver.find_element(By.XPATH, "//crx-export-results-link[@class='export']")
            export_button.click()
            human_delay(2, 3)
            logging.info(f"Exported {listing_count} listings for {county}.")

            # changes log depending on if a max acre was entered or not
            if max_acres_searched == -1:
                logging.info(f"Min acres: {min_acres_searched}. Max:")
            else:
                logging.info(f"Min acres: {min_acres_searched}. Max: {max_acres_searched}")

            # if we're not currently splitting up the listings that means all were exported, update status and move to next county
            if not splitting_listings:
                exported_all = True
        except Exception as e:
            # if the scraping logic at any point has an error, log it and return False
            logging.error(e)
            return False

    return True

def human_delay(min_sec, max_sec):
    delay = random.uniform(min_sec, max_sec)
    time.sleep(delay)

def login(driver):
    username = "kai971493@gmail.com"
    pw = "AngeloState1!"
    human_delay(4,5)
    login_or_signup_button = driver.find_element(By.XPATH, "//button[normalize-space(.//span[contains(@class, 'mdc-button__label')])='Sign Up or Log In']")
    login_or_signup_button.click()
    human_delay(2,3)
    login_tab_switch = driver.find_element(By.CLASS_NAME, "tab.switch")
    login_tab_switch.click()
    human_delay(1.8,2.5)
    username_input = driver.find_element(By.CSS_SELECTOR, "input[type='email']")
    username_input.send_keys(username)
    human_delay(2,3)
    password_input = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
    password_input.send_keys(pw)
    human_delay(1,2)
    login_button = driver.find_element(By.CSS_SELECTOR, "button[data-cy='button-login']")
    login_button.click()
    human_delay(4,5)
    logging.info("Logged in.")

def reuse_or_login(driver):
    driver.get("https://crexi.com")

    # load cookies if they exist
    if os.path.exists("../crexi_cookies.json"):
        with open("../crexi_cookies.json", "r") as f:
            cookies = json.load(f)
            for cookie in cookies:
                try:
                    driver.add_cookie(cookie)
                except:
                    pass

    driver.get("https://crexi.com/properties")
    human_delay(4,5)

    try:
        login_or_signup_button = driver.find_element(By.XPATH, "//button[normalize-space(.//span[contains(@class, 'mdc-button__label')])='Sign Up or Log In']")
        logging.info("Cookies failed. Still logged out. Logging in...")
        login(driver)
        with open("../crexi_cookies.json", "w") as f:
            json.dump(driver.get_cookies(), f)
    except NoSuchElementException:
        logging.info("Successfully applied saved cookies")

def clear_searchbar(driver):
    try:
        remove_prev_county_button = driver.find_element(By.XPATH,
                                                        "//button[@class='search-bar-pill-remove cui-button-reset']")
        remove_prev_county_button.click()
        human_delay(2, 3)
    except Exception as e:
        logging.info("Failed to clear searchbar.")
        logging.error(e)

def scrape_with_retries(driver, county):
    max_retries = 3
    retries = 0
    success = False

    while not success and retries < max_retries:
        try:
            success = scrape_county(county, driver)
        except Exception as e:
            logging.error(e)
            success = False

        if not success:
            retries += 1
            logging.info(f"{county} County failed. Retrying.")
            # reload the page
            driver.get("https://crexi.com/properties")
            human_delay(2, 3)
            clear_searchbar(driver)

    if retries == max_retries:
        logging.info("County failed after 3 retries.")

    clear_searchbar(driver)

    return success

def create_driver(download_dir):
    chrome_options = uc.ChromeOptions()

    prefs = {
        "download.default_directory": download_dir,          # Set download folder
        "download.prompt_for_download": False,               # No dialog popup
        "download.directory_upgrade": True,                  # Allow overwriting default folder
        "safebrowsing.enabled": True                         # Avoid safebrowsing block
    }
    chrome_options.add_experimental_option("prefs", prefs)
    chrome_options.add_argument('--ignore-ssl-errors=yes')
    chrome_options.add_argument('--ignore-certificate-errors')
    driver = uc.Chrome(options=chrome_options, use_subprocess=True)

    return driver

def run_scraper():
    # download path, CHANGE AS NEEDED
    download_dir = r"C:\Users\sandr\Desktop\testrun2"  # directory for local machine
    os.makedirs(download_dir, exist_ok=True)

    log_file = os.path.join(download_dir, "export_log.txt")

    logging.basicConfig(
        filename=log_file,
        filemode='a',
        format='%(asctime)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    # hardcoded counties
    counties = [
        "Appling", "Atkinson", "Bacon", "Baker", "Baldwin", "Banks", "Barrow",
        "Bartow", "Ben Hill", "Berrien", "Bibb", "Bleckley", "Brantley", "Brooks",
        "Bryan", "Bulloch", "Burke", "Butts", "Calhoun", "Camden", "Candler",
        "Carroll", "Catoosa", "Charlton", "Chatham", "Chattahoochee", "Chattooga",
        "Cherokee", "Clarke", "Clay", "Clayton", "Clinch", "Cobb", "Coffee",
        "Colquitt", "Columbia", "Cook", "Coweta", "Crawford", "Crisp", "Dade",
        "Dawson", "Decatur", "DeKalb", "Dodge", "Dooly", "Dougherty", "Douglas",
        "Early", "Echols", "Effingham", "Elbert", "Emanuel", "Evans", "Fannin",
        "Fayette", "Floyd", "Forsyth", "Franklin", "Fulton", "Gilmer", "Glascock",
        "Glynn", "Gordon", "Grady", "Greene", "Gwinnett", "Habersham", "Hall",
        "Hancock", "Haralson", "Harris", "Hart", "Heard", "Henry", "Houston",
        "Irwin", "Jackson", "Jasper", "Jeff Davis", "Jefferson", "Jenkins",
        "Johnson", "Jones", "Lamar", "Lanier", "Laurens", "Lee", "Liberty",
        "Lincoln", "Long", "Lowndes", "Lumpkin", "Macon", "Madison", "Marion",
        "McDuffie", "McIntosh", "Meriwether", "Miller", "Mitchell", "Monroe",
        "Montgomery", "Morgan", "Murray", "Muscogee", "Newton", "Oconee",
        "Oglethorpe", "Paulding", "Peach", "Pickens", "Pierce", "Pike", "Polk",
        "Pulaski", "Putnam", "Quitman", "Rabun", "Randolph", "Richmond",
        "Rockdale", "Schley", "Screven", "Seminole", "Spalding", "Stephens",
        "Stewart", "Sumter", "Talbot", "Taliaferro", "Tattnall", "Taylor",
        "Telfair", "Terrell", "Thomas", "Tift", "Toombs", "Towns", "Treutlen",
        "Troup", "Turner", "Twiggs", "Union", "Upson", "Walker", "Walton",
        "Ware", "Warren", "Washington", "Wayne", "Webster", "Wheeler", "White",
        "Whitfield", "Wilcox", "Wilkes", "Wilkinson", "Worth"
    ]

    # SCRAPING STARTS HERE

    driver = create_driver(download_dir)

    reuse_or_login(driver)

    # outer loop iterates through counties
    for county in counties:
        try:
            scrape_with_retries(driver, county)

        except WebDriverException as e:
            logging.error(f"WebDriverException while scraping county: {county}. Error: {e}")
            driver.quit()
            logging.info("Restarting driver...")
            driver = create_driver()
            reuse_or_login(driver)
            human_delay(3, 5)
            scrape_with_retries(driver, county)

        except Exception as e:
            logging.error(f"Unexpected error: {e}")

    logging.info("Finished all counties.")
    driver.quit()

run_scraper()

# if __name__ == "__main__":
#
#     # download path, CHANGE AS NEEDED
#     download_dir = r"C:\Users\sandr\Desktop\testrun2" # directory for local machine
#     os.makedirs(download_dir, exist_ok=True)
#
#     log_file = os.path.join(download_dir, "export_log.txt")
#
#     logging.basicConfig(
#         filename=log_file,
#         filemode='a',
#         format='%(asctime)s - %(levelname)s - %(message)s',
#         level=logging.INFO
#     )
#
#     # hardcoded counties
#     counties = [
#        "Baylor", "Bee", "Bell", "Bexar", "Blanco", "Borden", "Bosque", "Bowie",
#        "Brazoria", "Brazos", "Brewster", "Briscoe", "Brooks", "Brown", "Burleson", "Burnet", "Caldwell",
#        "Calhoun", "Callahan", "Cameron", "Camp", "Carson", "Cass", "Castro", "Chambers", "Cherokee",
#     "Childress", "Clay", "Cochran", "Coke", "Coleman", "Collin", "Collingsworth", "Colorado", "Comal",
#        "Comanche", "Concho", "Cooke", "Coryell", "Cottle", "Crane", "Crockett", "Crosby", "Culberson",
#        "Dallam", "Dallas", "Dawson", "Deaf Smith", "Delta", "Denton", "DeWitt", "Dickens", "Dimmit",
#        "Donley", "Duval", "Eastland", "Ector", "Edwards", "Ellis", "El Paso", "Erath", "Falls", "Fannin",
#        "Fayette", "Fisher", "Floyd", "Foard", "Fort Bend", "Franklin", "Freestone", "Frio", "Gaines",
#        "Galveston", "Garza", "Gillespie", "Glasscock", "Goliad", "Gonzales", "Gray", "Grayson", "Gregg",
#        "Grimes", "Guadalupe", "Hale", "Hall", "Hamilton", "Hansford", "Hardeman", "Hardin"
#     ]
#
#     # SCRAPING STARTS HERE
#
#     driver = create_driver(download_dir)
#
#     reuse_or_login(driver)
#
#     # outer loop iterates through counties
#     for county in counties:
#         try:
#             scrape_with_retries(driver, county)
#
#         except WebDriverException as e:
#             logging.error(f"WebDriverException while scraping county: {county}. Error: {e}")
#             driver.quit()
#             logging.info("Restarting driver...")
#             driver = create_driver()
#             reuse_or_login(driver)
#             human_delay(3, 5)
#             scrape_with_retries(driver, county)
#
#         except Exception as e:
#             logging.error(f"Unexpected error: {e}")
#
#     logging.info("Finished all counties.")
#     driver.quit()