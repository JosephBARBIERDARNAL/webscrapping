# Project : Webscraping
# Object : get job offers from Welcome to the Jungle using a dedicated class
# Author :
#       - Erwan Judic (main)
#       - Komla Djodji Adayeke
#       - Lacoste Victor
#       - Barbier Joseph

import pandas as pd
from src.src_welcometothejungle import JungleScraper
from src.get_duration import separate_by_digit


# init and load page
keywords = "data science"
nb_pages = 50
jungle_scraper = JungleScraper()
url = "https://www.welcometothejungle.com/fr"
links_offers = jungle_scraper.search_offers(url, keywords, nb_pages)

# get jobs 
data = []
for offer in links_offers:
    offer_info = jungle_scraper.scrape_offer(offer)
    data.append(offer_info)
df = pd.DataFrame(data)

contract, duration = separate_by_digit(df['Contract'])
df['Contract'] = contract
df['Duration'] = duration
df['Keyword'] = keywords
df['Site'] = 'Welcome to the Jungle'
df = df[df['Date'] != 'Error']
print(f"Scrapping over: {len(df)} jobs found.")

# save data to csv
df.to_csv("www/welcometothejungle.csv", index=False)
jungle_scraper.close_driver()