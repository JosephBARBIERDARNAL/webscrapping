# Project : Webscraping
# Object : Create a dedicated class for Welcome to the Jungle jobs scraping
# Author :
#       - Erwan Judic (main)
#       - Komla Djodji Adayeke
#       - Lacoste Victor
#       - Barbier Joseph

# selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# other
import re
import time
from datetime import datetime
import pandas as pd






class JungleScraper:
    """
    The JungleScraper() class contains all main features needed to
    build a welcome to the jungle job scraper. It contains various methods
    for searching or scraping.
    """
    
    def __init__(self):
        """
        Initializes the Firefox webdriver
        """
        self.driver = webdriver.Firefox()
        print("JungleScraper initialized")


    def accept_cookies(self):
        """
        Clicks the accept cookies button
        """
        cookie_button = self.driver.find_element(By.CSS_SELECTOR, "#axeptio_btn_acceptAll")
        cookie_button.click()


    def search_offers(self, url, keyword, number_of_pages_to_browse):
        """
        Searches for job offers based on a keyword and
        collects URLs across multiple pages
        """
        
        # initialize the browser
        self.driver.get(url)

        # accept cookies with a wait time for the tab to appear
        self.driver.implicitly_wait(2)
        self.accept_cookies()

        # search for job offers using the keyword
        search_box = self.driver.find_element(By.CSS_SELECTOR, "#search-query-field")
        search_box.send_keys(keyword)
        search_box.send_keys(Keys.RETURN)

        # wait for the search results page to load
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//a[@class ='sc-6i2fyx-0 gIvJqh']"))
        )

        # retrieve the job offer URLs across all pages
        offer_links = []
        browsed_pages = 0
        first_iteration = True

        while browsed_pages < number_of_pages_to_browse:
            # retrieve job offer URLs on the current page
            offers = self.driver.find_elements(By.XPATH, "//a[@class ='sc-6i2fyx-0 gIvJqh']")
            offer_links.extend([offer.get_attribute("href") for offer in offers])

            # click on the next page button
            try:
                next_buttons = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, "sc-dChVcU.edvHKF"))
                )
                if first_iteration:
                    next_button = next_buttons[0]
                    first_iteration = False
                else:
                    next_button = next_buttons[1]

                next_button.click()
                
                # wait for the new page to load
                self.driver.implicitly_wait(2)
                browsed_pages += 1
            
            # stop the loop if the next button is not found
            except:
                break

        return offer_links


    def convert_date(self, date_string):
        """
        Converts a date string to 'year/month/day' format
        """
        date_obj = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%SZ")
        return date_obj.strftime("%Y/%m/%d")


    def extract_duration(self, value):
        """
        Extracts duration from a string enclosed in parentheses
        """
        # use a regular expression to extract the duration in parentheses
        match = re.search(r'\(([^)]+)\)', value)

        # if a match is found, return the duration, otherwise return None
        return match.group(1) if match else None


    def scrape_offer(self, url):
        """
        Scrapes details of a job offer from its URL
        """
        self.driver.get(url)
        
        # retrieve the offer information
        title_elements = self.driver.find_elements(By.XPATH, "//h1")
        title_elements2 = self.driver.find_elements(By.XPATH, "//h2")
        title = title_elements[0].text if title_elements else title_elements2[0].text

        elements = self.driver.find_elements(By.XPATH, "//div[@class ='sc-dQEtJz iIerXh']")
        salary_text = elements[2].text if elements else None
        salary = salary_text.replace("Salary:\n", "") if salary_text else None

        company_elements = self.driver.find_elements(By.CLASS_NAME, "sc-ERObt.kkLHbJ.wui-text")
        company = company_elements[0].text if company_elements else None

        contract_element = elements[0].text if elements else None
        contract_element = contract_element.replace("\n", "").strip()
        contract = contract_element if contract_element else None

        city_element = elements[1].text if elements else None
        city = city_element if city_element else None

        sector_elements = self.driver.find_elements(By.XPATH, "//div[@class ='sc-dQEtJz kiMwlt']")
        sector_text = sector_elements[0].text if sector_elements else None
        sector = sector_text if sector_text else None

        apply_url_elements = self.driver.find_elements(By.XPATH, "//a[@class ='sc-gvZAcH iNpPnN']")
        url = apply_url_elements[0].get_attribute("href") if apply_url_elements else None

        date_elements = self.driver.find_elements(By.XPATH, "//div[@class ='sc-bXCLTC dPVkkc']//time")
        date_str = date_elements[0].get_attribute("datetime") if date_elements else None
        converted_date = self.convert_date(date_str) if date_str else None

        description_elements = self.driver.find_elements(By.XPATH, "//div[@class ='sc-18ygef-1 ezamTS']")
        description_text = description_elements[0].text if description_elements else None
        description_text = description_text.replace("\n", "") if description_text else None

        # explicit wait before loading the next offer page
        time.sleep(1)

        return {
            "Title": title,
            "Salary": salary,
            "Company": company,
            "Contract": contract,
            "Location": city,
            "Sector": sector,
            "Url": url,
            "Date": converted_date,
            "Description": description_text
        }


    def close_driver(self):
        """
        Closes the webdriver
        """
        self.driver.quit()
