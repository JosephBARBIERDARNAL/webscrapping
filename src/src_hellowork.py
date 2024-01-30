# Projet Webscrapping
# Object : Create a dedicated class for HelloWork jobs scraping
# Author :
#       - Komla Djodji Adayeke (main)
#       - Lacoste Victor
#       - Judic Erwan
#       - Barbier Joseph


# selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

# other
import pandas as pd
import time
import requests
from tqdm import tqdm
from bs4 import BeautifulSoup






class HelloWork:
    """
    The HelloWork() class contains all main features needed to
    build a HelloWork job scraper. It contains various methods
    for searching or scraping.
    """

    def __init__(self, sec_sleep: float = 1):
        """
        Initiate the Scraper.
        """
        self.driver = webdriver.Firefox()
        self.sec_sleep = sec_sleep

        
    def sleep(self, n: float = 1.0):
        """
        Pause scraper for a given amount of time
        """
        time.sleep(n * self.sec_sleep)

        
    def close_browser(self):
        """
        Close all browser tabs.
        """
        self.driver.quit()

        
    def load_page(self, url: str):
        """
        Loads a specified URL in the web driver.
        """
        self.driver.get(url)
        self.sleep(2)

        
    def accept_cookies(self):
        """
        Find and click on the "accept cookies" button.
        """
        continue_button_xpath = '//button[@id="hw-cc-notice-continue-without-accepting-btn"]'
        cookies_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, continue_button_xpath))
        )
        cookies_button.click()
        self.sleep(1)

        
    def search_for_jobs(self, keyword: str):
        """
        Search for jobs using a specified keyword.
        """
        search_input = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.NAME, "k"))
        )
        search_input.send_keys(keyword)
        self.sleep(1)
        search_input.send_keys(Keys.RETURN)
        self.sleep(2)

        
    def scroll(self, px: int):
        """
        Scroll down a specified number of pixels on the page.
        """
        self.driver.execute_script(f"window.scrollBy(0, {px});")
        self.sleep(1)

        
    def get_job_links(self) -> list:
        """
        Get all job links from the current page.
        """
        links = []
        css_expression = '.offer--content .offer--maininfo h3 a'
        job_links = WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, css_expression))
        )
        for job_link in job_links:
            links.append(job_link.get_attribute('href'))
        return links

    
    def get_job_details(self, url: str) -> dict:
        """
        Extract detailed information for a single job listing from a given URL.
        Uses requests and BeautifulSoup to parse the HTML content.
        """
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)

        html = response.text
        soup = BeautifulSoup(html, 'html.parser')

        # Job title
        job_title_span = soup.find('span', {'class': 'tw-block tw-typo-xl sm:tw-typo-3xl tw-mb-2', 'data-cy': 'jobTitle'})
        if job_title_span is not None:
            job_title = job_title_span.text.strip()
        else:
            job_title = None

        # Company name
        company_name_span = soup.find('span', {'class': 'tw-contents tw-typo-m tw-text-grey'})
        if company_name_span is not None:
            company_name = company_name_span.text.strip()
        else:
            company_name = None

        # Location and job type
        spans = soup.find_all('span', {'class': 'tw-inline-flex tw-typo-m tw-text-grey'})
        if len(spans) >= 2:
            job_type_span = spans[1].text.strip()
            location_span = spans[0].text.strip()
        else:
            job_type_span = None
            location_span = None

        # Salary
        salary_span = soup.find('li', {'class': 'tw-tag-attractive-s tw-readonly'})
        if salary_span is not None:
            salary = salary_span.text.strip().replace('\u202f', '')
        else:
            salary = None

        # Publication date
        date_span = soup.find('span', {'class': 'tw-block tw-typo-xs tw-text-grey tw-mt-3 tw-break-words'})
        if date_span is not None:
            date_text = date_span.text.strip().split(' ')
            date = date_text[2]
            ref = date_text[6].split('/')[0]
        else:
            date = None
            ref = None

        # Advertisement reference
        ref_span = soup.find('span', {'class': 'tw-block tw-typo-xs tw-text-grey tw-mt-3 tw-break-words'})
        if ref_span is not None:
            ref_text = ref_span.text.strip().split(' ')
            ref = ref_text[6].split('/')[0]
        else:
            ref = None

        # Find the <p> element by its class name
        paragraph_element = soup.find('p', class_='tw-typo-long-m')

        # Extract text from the <p> element
        paragraph_text = paragraph_element.get_text(strip=True)

        # Extract text from the <p> element
        if paragraph_element is not None:
            paragraph_text = paragraph_element.get_text(strip=True)
        else:
            paragraph_text = None

        return job_title, company_name,salary, location_span, paragraph_text, date, job_type_span, ref

        
    def scrape_jobs(self, nb_pages: int) -> pd.DataFrame:
        """
        Scrape job details from a specified number of pages using a given keyword.
        """
        
        # find the link for each job
        all_links = []
        for _ in range(nb_pages):
            all_links.extend(self.get_job_links())
            self.scroll(500) 
            
        # iterate over the links to get the job info
        job_data = []
        for url in tqdm(all_links):
            job_data.append(self.get_job_details(url))

        df = pd.DataFrame(job_data)
        df.columns = ['Title', 'Company', 'Salary', 'Location', 'Description', 'Date', 'Contract', 'Job ID']
        print(f"Scrapping over: {len(df)} jobs found.")
        return df

