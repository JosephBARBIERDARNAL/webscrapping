# selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# other
import pandas as pd
import time




class Scraper:
    """
    The Scraper() class contains all main features needed to
    build a linkedin job scraper. It contains various methods
    for login, cookies, searching or scraping.
    """

    
    def __init__(self, sec_sleep: float=0.5):
        """
        Initiate the Scraper.
        """
        self.driver = webdriver.Firefox()
        self.sec_sleep = sec_sleep
        
        
    def close_browser(self):
        """
        Close all browser tabs
        """
        self.driver.quit()

        
    def scroll_to_bottom(self):
        """
        Scroll to the bottom of the job page.
        It first find job list object and then scroll to the bottom of the page.
        """
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".jobs-search-results-list")))
        div_element = self.driver.find_element(By.CSS_SELECTOR, ".jobs-search-results-list")
        self.driver.execute_script("arguments[0].scrollIntoView(true);", div_element)
        self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;", div_element)
        time.sleep(self.sec_sleep)

        
    def load_page(self, url: str, try_quitting_first: bool=True):
        """
        Takes a url and open the associated page,
        with the possibility of first quitting current
        web driver for a "restart".
        """
        if try_quitting_first:
            self.close_browser()
        self.driver.get(url)
        time.sleep(self.sec_sleep)

        
    def accept_cookies(self):
        """
        Find "accept cookies" and click on it.
        """
        cookies_xpath = '//*[@id="artdeco-global-alert-container"]/div/section/div/div[2]/button[1]'
        cookies_button = self.driver.find_element(By.XPATH, cookies_xpath)
        cookies_button.click()
        time.sleep(self.sec_sleep)

        
    def login(self, email: str, password: str):
        """
        Take email and password, enter them and click on "sign in".
        """
        email_field = self.driver.find_element(By.XPATH, '//*[@id="session_key"]')
        email_field.send_keys(email)
        time.sleep(self.sec_sleep)
        
        password_field = self.driver.find_element(By.XPATH, '//*[@id="session_password"]')
        password_field.send_keys(password)
        time.sleep(self.sec_sleep)

        button_signin = self.driver.find_element(By.XPATH, '//*[@id="main-content"]/section[1]/div/div/form/div[2]/button')
        button_signin.click()
        time.sleep(self.sec_sleep)

        
    def press_enter_and_scroll(self):
        """
        After keywords filled, searching for related jobs and scrolling
        to the bottom of the page in order to be sure every job is displayed.
        """
        search_field = self.driver.find_element(By.XPATH, "(//*[contains(@id, 'jobs-search-box-location-id-ember')])[last()]")
        search_field.send_keys(Keys.ENTER)
        time.sleep(self.sec_sleep)
        self.scroll_to_bottom()

        
    def close_message(self):
        """
        Close message box.
        """
        message_close = self.driver.find_element(By.XPATH, "(//button[contains(@class, 'msg-overlay-bubble-header__control--new-convo-btn')])[last()]")
        message_close.click()
        time.sleep(self.sec_sleep)

        
    def enter_keywords(self, keywords: str):
        """
        Write keywords in the job search bar.
        """
        search_field = self.driver.find_element(By.XPATH, "(//*[contains(@id, 'jobs-search-box-keyword-id-ember')])[last()]")
        search_field.clear()
        search_field.send_keys(keywords)
        time.sleep(self.sec_sleep)

        
    def enter_location(self, location: str):
        """
        Write location wanted in the location search bar.
        """
        search_field = self.driver.find_element(By.XPATH, "(//*[contains(@id, 'jobs-search-box-location-id-ember')])[last()]")
        search_field.clear()
        search_field.send_keys(location)
        time.sleep(self.sec_sleep)

        
    def get_job_details(self):
        """
        For a given job page, get all infos displayed, store them
        into a pandas dataframe and return it.
        """
            
        # find all job card elements
        job_cards = self.driver.find_elements(By.CLASS_NAME, 'job-card-container')
    
        # initialize lists to store job details
        job_ids = []
        job_titles = []
        companies = []
        locations = []
        descriptions = []
        posted_dates = []
    
        # extract details from `job_cards`
        for card in job_cards:
            job_id = card.get_attribute('data-job-id')
            title_element = card.find_element(By.CSS_SELECTOR, '.job-card-container__link.job-card-list__title')
            company_element = card.find_element(By.CSS_SELECTOR, '.job-card-container__primary-description')
            location_element = card.find_element(By.CSS_SELECTOR, '.job-card-container__metadata-wrapper li')
            date_element = card.find_element(By.XPATH, "//span[@class='tvm__text tvm__text--neutral']/span")
            
            # add elements to lists if found
            if job_id:
                try:
                    job_ids.append(job_id)
                    job_titles.append(title_element.text if title_element else 'N/A')
                    companies.append(company_element.text if company_element else 'N/A')
                    locations.append(location_element.text if location_element else 'N/A')
                    descriptions.append(card.text if card else 'N/A')
                    posted_dates.append(date_element.text if date_element else 'N/A')
                except:
                    pass
    
        # output the results
        job_data = pd.DataFrame({
            'Job ID': job_ids,
            'Title': job_titles,
            'Company': companies,
            'Location': locations,
            'Description': descriptions,
            'Date': posted_dates,
        })
        return job_data

    
    def scrap_jobs(self, max_page: int=100, verbose: bool=False):
        """
        Starting from the first job page, iterate until max page is attained
        and get all job infos per page using previous `get_job_details()` method.
        All jobs are put into a pandas dataframe.
        The dataframe is then save in the `root/data/` directory as a csv.
        """
        
        # get job infos from first page
        job_df = self.get_job_details()
        
        # start with next page
        page = 2
        
        while (True and page < max_page):
        
            # go to next page
            next_page_xpath = f'//button[@aria-label="Page {page}"]'
            try:
                next_page_button = self.driver.find_element(By.XPATH, next_page_xpath)
                next_page_button.click()
                page += 1
            
            # next page not found, stop scrapping and return `job_df`
            except:
                print("Last page, scrapping over")
                return job_df
    
            # wait and scroll down
            self.scroll_to_bottom()
    
            # get job infos and add them to current `job_df`
            new_job_df = self.get_job_details()
            job_df = pd.concat([new_job_df, job_df])
            
            # print verbosity
            if verbose:
                    print(f"Page {page} scrapped.")
                    print(f"Jobs founded: {len(new_job_df)}")
            
            # save df at each iteration for safety
            job_df = job_df.reset_index(drop=True)
            job_df.to_csv('../data/job_df.csv', index=False)