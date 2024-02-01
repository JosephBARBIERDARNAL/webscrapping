# Projet Webscrapping
# Object : get job offers from HelloWork using a dedicated class
# Author :
#       - Komla Djodji Adayeke (main)
#       - Lacoste Victor
#       - Judic Erwan
#       - Barbier Joseph

from src.src_hellowork import HelloWork 
import pandas as pd



# init and load page
scraper = HelloWork()
url = "https://www.hellowork.com/fr-fr/"
scraper.load_page(url)
scraper.accept_cookies()

# find jobs in data science
keywords = "data science"
scraper.search_for_jobs(keywords)

# get jobs and save them as a csv file
job_data = scraper.scrape_jobs(nb_pages=2)
job_data['Site'] = 'HelloWork'
job_data['Duration'] = 'N/A'
job_data['Sector'] = 'N/A'
job_data['Keyword'] = keywords
#job_data.to_csv('www/hellowork.csv', index=False)

# close browser 
scraper.close_browser()