# Projet Webscrapping
# Object : get job offers from JobTeaser using a dedicated class
# Author :
#       - Lacoste Victor (main)
#       - Barbier Joseph
#       - Judic Erwan
#       - Komla Djodji Adayeke

from src.src_jobteaser import JobTeaser
import pandas as pd

keyword = 'data science'

scraper = JobTeaser(3)
scraper.driver.get(scraper.url)
scraper.accept_cookies()
scraper.search_jobs(keyword)
scraper.wait_for_page_load()
scraper.navigate_pages()
scraper.close_browser()
scraper.scrape_jobs()

contract_types, contract_durations = scraper.separate_by_digit(scraper.contracts)

data = {
    "Link": scraper.job_links,
    "Title": scraper.titles,
    "Company": scraper.companies,
    "Contract": contract_types,
    "Contract Duration": contract_durations,
    "City": scraper.cities,
    "Date": scraper.dates,
    "Description": scraper.descriptions
}

df = pd.DataFrame(data)
df['Site'] = 'Jobteaser'

# fill the Sector attribute with N/A because it was not possible to extract it from the website
df['Sector'] = 'N/A'

df['Keyword'] = keyword

# keep only those offers for which we have been able to extract all attributes
df = df[df['Title'] != 'Error']
df = df[df['Date'] != 'Error']

# save results to csv
#df.to_csv('www/jobteaser.csv', index=False)