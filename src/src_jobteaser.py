# Projet Webscrapping
# Object : get job offers from JobTeaser using a dedicated class
# Author :
#       - Lacoste Victor (main)
#       - Barbier Joseph
#       - Judic Erwan
#       - Komla Djodji Adayeke

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
from datetime import datetime
from locale import setlocale, LC_TIME





class JobTeaser:
    def __init__(self, pages_to_visit=50):
        """
        Initialize a Chrome webdriver and set initial values
        """
        self.driver = webdriver.Chrome()
        self.url = "https://www.jobteaser.com/fr/job-offers?locale=fr&locale=en"
        self.job_links = []
        self.pages_visited = 0
        self.pages_to_visit = pages_to_visit
        self.titles = []
        self.companies = []
        self.contracts = []
        self.cities = []
        self.descriptions = []
        self.dates = [] 
    

    def accept_cookies(self):
        """
        Method to accept cookies on the website
        """
        cookies_button = self.driver.find_element(By.CSS_SELECTOR, "#didomi-notice-agree-button")
        cookies_button.click()

    def search_jobs(self, keyword):
        """
        Method to enter a keyword in the search bar
        """
        search_box = self.driver.find_element(By.CSS_SELECTOR, "#job-ads-keyword-search")
        search_box.send_keys(keyword)
        search_box.send_keys(Keys.RETURN)


    def wait_for_page_load(self):
        """
        Method to wait for the page to load
        """
        WebDriverWait(self.driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, "//li[@class ='Card_listItem__BHwSk']")))
        time.sleep(3)


    def get_job_links(self):
        """
        Method to get job offer links on the current page
        """
        jobs = self.driver.find_elements(By.XPATH, "//a[@class ='link_jds-Link__IVm1_ cardTitle_jds-CardTitle__link__joX8c']")
        self.job_links.extend([job.get_attribute("href") for job in jobs])


    def navigate_pages(self):
        """
        Method to navigate through pages of job listings while getting the links
        """
        while self.pages_visited < self.pages_to_visit:
            self.get_job_links()
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            self.driver.execute_script("window.scrollBy(0, -200);")
            time.sleep(1)
            next_buttons = self.driver.find_elements(By.XPATH, "//a[@class ='button_jds-Button__Cbo3A button_jds-Button--onlyIcon__s_xZR button_jds-Button--minor__ukW_c pagination_jds-Pagination__button__GgDAw']")
            if self.pages_visited < self.pages_to_visit - 1:
                if self.pages_visited == 0:
                    next_buttons[0].click()
                else:
                    next_buttons[1].click()
                self.driver.implicitly_wait(2)
            self.pages_visited += 1


    def close_browser(self):
        """
        Method to close the browser
        """
        self.driver.quit()


    def str_to_date(string):
        """
        Method to convert date string to a formatted date
        ('Publiée le 24 janvier 2024' ---> '2024/24/01')
        """
        setlocale(LC_TIME, 'fr_FR.UTF-8')
        date_string = string.replace("Publiée le ", "")
        date_object = datetime.strptime(date_string, "%d %B %Y")
        formatted_date = date_object.strftime("%Y/%d/%m")
        return formatted_date


    def separate_by_digit(self, contracts):
        """
        Method to separate contract information into types and
        durations ('Stage - 4 à 6 mois' ---> 'Stage' AND '4 à 6 mois')
        """
        contract_types = []
        contract_durations = []

        for string in contracts:
            index_digit = next((i for i, c in enumerate(string) if c.isdigit()), None)

            if index_digit is not None:
                contract_types.append(string[:index_digit - 1])
                contract_durations.append(string[index_digit:])
            else:
                contract_types.append(string)
                contract_durations.append("Undetermined")

        return contract_types, contract_durations


    def scrape_jobs(self):
        """
        Method to scrape job details from each job link
        """
        for job_link in self.job_links:
            try:
                self.driver = webdriver.Chrome()
                self.driver.get(job_link)
                time.sleep(3)
                self.accept_cookies()
                
                # extract job details
                title = self.driver.find_elements(By.XPATH, "//h1")[0].text
                company = self.driver.find_elements(By.XPATH, "//h4")[0].text
                contract = self.driver.find_elements(By.XPATH, "//p[@class ='jds-Text__qsGqo jds-Text--normal__pHwjn jds-Text--resetSpacing__8szyJ jds-Text--weight-normal__D3xbZ jo-JobAdContext__text__7FOJC']")[0].text
                city = self.driver.find_elements(By.XPATH, "//p[@class ='jds-Text__qsGqo jds-Text--normal__pHwjn jds-Text--resetSpacing__8szyJ jds-Text--weight-normal__D3xbZ jo-JobAdContext__text__7FOJC']")[1].text
                description = self.driver.find_elements(By.XPATH, "//section[@class ='jds-Text__qsGqo jds-Text--normal__pHwjn jds-RichText__Kel2q jo-Description__richText__dHFVq']")[0].text

                try:
                    date = self.driver.find_elements(By.XPATH, "//p[@class ='jds-Text__qsGqo jds-Text--normal__pHwjn jds-Text--grey__gYV39 jds-Text--resetSpacing__8szyJ jo-Heading--published__B0FnS']")[0].text
                    formatted_date = self.str_to_date(date)
                except:
                    formatted_date = 'Error'
                    
                # append details to lists
                self.titles.append(title)
                self.companies.append(company)
                self.contracts.append(contract)
                self.cities.append(city)
                self.descriptions.append(description)
                self.dates.append(formatted_date)

            except:
                # handle exceptions and append error values to lists
                self.titles.append('Error')
                self.companies.append('Error')
                self.contracts.append('Error')
                self.cities.append('Error')
                self.dates.append('Error')
                self.descriptions.append('Error')
                pass
            
            # ensure the browser is closed after each iteration
            self.driver.quit()