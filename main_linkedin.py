# Projet Webscrapping
# Object : get job offers from LinkedIn using a dedicated class
# Author :
#       - Barbier Joseph (main)
#       - Lacoste Victor
#       - Judic Erwan
#       - Komla Djodji Adayeke

from src.src_linkedin import LinkedIn
import pandas as pd



# HOW TO GET CREDENTIALS
# 1 - Create a text file named credentials.txt in the root folder
# 2 - Write your LinkedIn email in the first line
# 3 - Write your LinkedIn password in the second line
# 4 - Save the file

# open text file
with open('credentials.txt', 'r') as file:
    credentials  = file.read()

    # split mail and password
    credentials = credentials.split('\n')
    mail = credentials[0]
    password = credentials[1]



# init, load page and login
scraper = LinkedIn()
scraper.load_page("https://www.linkedin.com/")
scraper.sleep(5)
scraper.accept_cookies()
scraper.login(mail, password)

# open recommended jobs page
scraper.load_page("https://www.linkedin.com/jobs/collections/recommended/")
scraper.sleep(5)
scraper.close_message()

# get jobs from all locations
us_jobs = scraper.get_all_jobs(location='United States')
southasia_jobs = scraper.get_all_jobs(location='South Asia')
eastasia_jobs = scraper.get_all_jobs(location='East Asia')
europe_jobs = scraper.get_all_jobs(location='European Economic Area')

# close browser after scraping
scraper.close_browser()

# concat all job dataframes and save to csv
linkedin_jobs = pd.concat([us_jobs, southasia_jobs, eastasia_jobs, europe_jobs])
linkedin_jobs['Site'] = 'LinkedIn'
linkedin_jobs['Contract'] = 'N/A'
linkedin_jobs['Salary'] = 'N/A'
linkedin_jobs['Sector'] = 'N/A'
linkedin_jobs.to_csv('www/linkedin.csv', index=False)