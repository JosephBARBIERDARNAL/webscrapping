# Project : Webscraping
# Object : get job offers from Welcome to the Jungle using a dedicated class
# Author :
#       - Erwan Judic (main)
#       - Komla Djodji Adayeke
#       - Lacoste Victor
#       - Barbier Joseph

import pandas as pd
from src.src_welcometothejungle import JungleScraper


# init and load page
keywords = "data science"
nb_pages = 20
jungle_scraper = JungleScraper()
url = "https://www.welcometothejungle.com/fr"
links_offers = jungle_scraper.search_offers(url, keywords, nb_pages)

# get jobs 
data = []
for offer in links_offers:
    offer_info = jungle_scraper.scrape_offer(offer)
    data.append(offer_info)
df = pd.DataFrame(data)
print(f"Scrapping over: {len(df)} jobs found.")

# save data to csv
#df.to_csv("www/welcometothejungle.csv", index=False)
jungle_scraper.close_driver()