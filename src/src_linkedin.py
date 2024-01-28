# selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# other
from datetime import datetime, timedelta
import pandas as pd
import time



    


class LinkedIn:
    """
    The LinkedIn() class contains all main features needed to
    build a linkedin job scraper. It contains various methods
    for login, cookies, searching or scraping.
    """

    
    def __init__(self, sec_sleep: float=1):
        """
        Initiate the Scraper.
        """
        self.driver = webdriver.Firefox()
        self.sec_sleep = sec_sleep
       
    
    def sleep(self, n: float=1.0):
        """
        Pause scraper for a given amount of time
        """
        time.sleep(self.sec_sleep)
        
        
    def close_browser(self):
        """
        Close all browser tabs.
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
        
    
    def scroll(self, px: int=200):
        """
        Scroll a little bit down on the job page.
        It first finds the job list object and then scrolls down a little bit.
        """
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".jobs-search-results-list")))
        div_element = self.driver.find_element(By.CSS_SELECTOR, ".jobs-search-results-list")
        self.driver.execute_script("arguments[0].scrollIntoView(true);", div_element)
        self.driver.execute_script(f"arguments[0].scrollTop += {px};", div_element)
        time.sleep(self.sec_sleep)

        
    def load_page(self, url: str, try_quitting_first: bool=False):
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

        
    def press_enter(self):
        """
        After keywords filled, searching for related jobs and scrolling
        to the bottom of the page in order to be sure every job is displayed.
        """
        search_field = self.driver.find_element(By.XPATH, "(//*[contains(@id, 'jobs-search-box-location-id-ember')])[last()]")
        search_field.send_keys(Keys.ENTER)
        time.sleep(self.sec_sleep)

        
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
        
    
    def change_date_format(self, date_str: str) -> str:
        """
        Change date format from Linkedin such as 
        '2 weeks ago' or '3 hours ago' to %Y/%m/%d.
        """
        
        # special case when there is "reposted" in the time since posted text
        if date_str.startswith("Reposted"):
            date_str = date_str.replace("Reposted ", "")
    
        # splitting the input string and change format
        number_str, unit, _ = date_str.split()
        number = int(number_str)
        unit = unit.rstrip('s') # plural case

        # mapping units to timedelta arguments
        unit_to_timedelta = {
            "day": timedelta(days=number),
            "week": timedelta(weeks=number),
            "month": timedelta(days=30 * number),
            "year": timedelta(days=365 * number),
            "hour": timedelta(hours=number),
            "minute": timedelta(minutes=number),
            "second": timedelta(seconds=number)
        }

        # compute differences
        delta = unit_to_timedelta.get(unit)
        if not delta:
            raise ValueError(f"Unsupported time unit: {unit}")

        past_date = (datetime.now() - delta).strftime("%Y/%m/%d")
        return past_date

        
    def get_job_details(self) -> pd.DataFrame:
        """
        For a given job page, get all infos displayed per job, store them
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
            try:
                job_id = card.get_attribute('data-job-id')
                title_element = card.find_element(By.CSS_SELECTOR, '.job-card-container__link.job-card-list__title')
                company_element = card.find_element(By.CSS_SELECTOR, '.job-card-container__primary-description')
                location_element = card.find_element(By.CSS_SELECTOR, '.job-card-container__metadata-wrapper li')
                date_element = card.find_element(By.XPATH, "//span[contains(., 'ago')]")

                # add elements to lists if found
                if job_id:
                    try:
                        job_ids.append(job_id)
                        job_titles.append(title_element.text if title_element else 'N/A')
                        companies.append(company_element.text if company_element else 'N/A')
                        locations.append(location_element.text if location_element else 'N/A')
                        descriptions.append(card.text if card else 'N/A')
                        posted_dates.append(date_element.text if date_element else 'N/A')
                        self.sleep(0.5)
                    except:
                        pass

            # we skip jobs that lead to stale exception
            except:
                pass
    
        
        # ensure all dates are valid and change their format
        if len(posted_dates)!=len(job_ids):
            posted_dates.append(posted_dates[-1])
        posted_dates_corrected = [self.change_date_format(date) for date in posted_dates]
        
        # output the results
        job_data = pd.DataFrame({
            'Job ID': job_ids,
            'Title': job_titles,
            'Company': companies,
            'Location': locations,
            'Description': descriptions,
            'Date': posted_dates_corrected
        })
        return job_data

    
    def scrap_jobs(self, file_name: str, max_page: int=100, verbose: bool=False) -> pd.DataFrame:
        """
        Starting from the first job page, iterate until max page is attained
        and get all job infos per page using previous `get_job_details()` method.
        All jobs are put into a pandas dataframe.
        The dataframe is then save in the `root/www/` directory as a csv.
        """
        
        # get job infos from first page
        job_df = self.get_job_details()
        
        # start with next page
        page = 2
        
        while page < max_page:
        
            # go to next page
            next_page_xpath = f'//button[@aria-label="Page {page}"]'
            try:
                next_page_button = self.driver.find_element(By.XPATH, next_page_xpath)
                next_page_button.click()
                page += 1
            
            # stop scrapping and return `job_df`
            except Exception as e:
                print(f"Scrapping over: {len(job_df)} jobs found.")
                return job_df
    
            # scroll down in order to display and load more jobs
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
            job_df.to_csv(f'www/{file_name}.csv', index=False)
            
        print(f"Scrapping over: {len(job_df)} jobs found.")
        return job_df
    
    
    def get_all_jobs(self, location: str, keywords: str='data science') -> pd.DataFrame:
        """
        Use most other methods to get all available jobs
        for the current search (location and keywords).
        Returns the dataframe containing all jobs for the
        selected location and keywords.
        """
        
        # enter user input
        self.enter_keywords(keywords)
        self.enter_location(location)
        self.press_enter()
        
        # waiting for jobs to load
        self.sleep(5)

        # file name used to saved the dataframe
        file_name = f"linkedin_{keywords.replace(' ', '_')}_{location.replace(' ', '_')}"
        
        # scrap all jobs and return it in main file
        jobs_df = self.scrap_jobs(file_name=file_name)
        return jobs_df