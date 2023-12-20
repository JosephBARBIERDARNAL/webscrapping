# selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# other
import pandas as pd
import time

# constants
sec_sleep = 0.5




def scroll_to_bottom(sec_sleep=sec_sleep):
    time.sleep(sec_sleep*10)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".jobs-search-results-list")))
    div_element = driver.find_element(By.CSS_SELECTOR, ".jobs-search-results-list")
    driver.execute_script("arguments[0].scrollIntoView(true);", div_element)
    driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;", div_element)

    
def load_page(driver, url, try_quitting_first=True):
    driver.get(url)
    time.sleep(sec_sleep*2.5)


def accept_cookies(driver):
    cookies_xpath = '//*[@id="artdeco-global-alert-container"]/div/section/div/div[2]/button[1]'
    cookies_button = driver.find_element(By.XPATH, cookies_xpath)
    cookies_button.click()
    time.sleep(sec_sleep)
    
    
def login(driver, email, password):
    
    # enter mail
    login_name_xpath = '//*[@id="session_key"]'
    email_field = driver.find_element(By.XPATH, login_name_xpath)
    email_field.send_keys(email)
    time.sleep(sec_sleep)
    
    # enter password
    login_password_xpath = '//*[@id="session_password"]'
    password_field = driver.find_element(By.XPATH, login_password_xpath)
    password_field.send_keys(password)
    time.sleep(sec_sleep)
    
    # click on sign in
    signin_button_xpath = '//*[@id="main-content"]/section[1]/div/div/form/div[2]/button'
    button_signin = driver.find_element(By.XPATH, signin_button_xpath)
    button_signin.click()
    time.sleep(sec_sleep)
    

def press_enter_and_scroll():
    # press "enter"
    search_field.send_keys(Keys.ENTER)
    time.sleep(sec_sleep)
    
    # scroll down in order to ensure all jobs are loaded
    scroll_to_bottom()
    
    
def close_message():
    message_xpath = "(//button[contains(@class, 'msg-overlay-bubble-header__control--new-convo-btn')])[last()]"
    message_close = driver.find_element(By.XPATH, message_xpath)
    message_close.click()
    time.sleep(sec_sleep)
    
    
def enter_keywords(keywords):
    input_keyword_xpath = "(//*[contains(@id, 'jobs-search-box-keyword-id-ember')])[last()]"
    search_field = driver.find_element(By.XPATH, input_keyword_xpath)
    search_field.clear()
    search_field.send_keys(keywords)
    time.sleep(sec_sleep)
    
    
def enter_location(location):
    location_keyword_xpath = "(//*[contains(@id, 'jobs-search-box-location-id-ember')])[last()]"
    search_field = driver.find_element(By.XPATH, location_keyword_xpath)
    search_field.clear()
    search_field.send_keys(location)
    time.sleep(sec_sleep)
    
    
def get_job_details(driver):
    # Find all job card elements
    job_cards = driver.find_elements(By.CLASS_NAME, 'job-card-container')

    # Initialize lists to store job details
    job_ids = []
    job_titles = []
    companies = []
    locations = []
    descriptions = []
    posted_dates = []

    # Iterate over job card elements to extract details
    for card in job_cards:
        job_id = card.get_attribute('data-job-id')
        title_element = card.find_element(By.CSS_SELECTOR, '.job-card-container__link.job-card-list__title')
        company_element = card.find_element(By.CSS_SELECTOR, '.job-card-container__primary-description')
        location_element = card.find_element(By.CSS_SELECTOR, '.job-card-container__metadata-wrapper li')
        date_element = card.find_element(By.XPATH, "//span[@class='tvm__text tvm__text--neutral']/span")

        if job_id:
            job_ids.append(job_id)
            job_titles.append(title_element.text if title_element else 'N/A')
            companies.append(company_element.text if company_element else 'N/A')
            locations.append(location_element.text if location_element else 'N/A')
            descriptions.append(card.text if card else 'N/A')
            posted_dates.append(date_element.text if date_element else 'N/A')

    # Create a DataFrame
    job_data = pd.DataFrame({
        'Job ID': job_ids,
        'Title': job_titles,
        'Company': companies,
        'Location': locations,
        'Description': descriptions,
        'Date': posted_dates,
    })

    return job_data