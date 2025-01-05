'''
This is a script for manifest preparation. It fetches all the screenshots from a Steam profile,
then crawls links to get the actual image links that can be used for display.

TODO:
- add logs
- add error handling
- add manifest creation
- add fetching screenshot metadata (game, title etc)
- add optimizations:
  - load previous manifest and check if number of images to fetch changes
- add ability to control fetched links with a config file (eg exclude specific games or screenshots)
'''
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import requests as rq

page_url = "https://steamcommunity.com/id/radvvan/screenshots/"

print("Setting up selenium")
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode
chrome_options.add_argument("--disable-gpu")  # Disable GPU (recommended for headless)
chrome_options.add_argument("--no-sandbox")  # Required for some Linux environments
chrome_options.add_argument("--disable-dev-shm-usage") 

driver = webdriver.Chrome(options=chrome_options)

driver.get(page_url)

scroll_pause = 2
last_height = driver.execute_script("return document.body.scrollHeight")

print("Scrolling")
while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(scroll_pause)

    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

print("Fetching source")
page = driver.page_source
driver.quit()

soup = BeautifulSoup(page, 'html.parser')
a_tags = soup.find_all("a")
hrefs = [a.get("href") for a in a_tags]
ss_links = [h for h in hrefs if "sharedfiles/filedetails" in h]

content_links = []

print("Fetching image links")
for h in ss_links:
    page = rq.get(h).text
    soup = BeautifulSoup(page, 'html.parser')
    img_link = soup.find("img", id="ActualMedia")
    content_links.append(img_link.get("src").split("?")[0])

print(f'Done, images fetched: {len(content_links)}')