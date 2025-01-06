'''
This is a script for manifest preparation. It fetches all the screenshots from a Steam profile,
then crawls links to get the actual image links that can be used for display.

TODO:
- add error handling
- add optimizations:
  - load previous manifest and check if number of images to fetch changes
- add ability to control fetched links with a config file (eg exclude specific games or screenshots)
'''
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import requests as rq
import json

def message(msg):
    print(f"[{time.ctime()}] {msg}")

page_url = "https://steamcommunity.com/id/radvvan/screenshots/"

message("Setting up selenium")
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode
chrome_options.add_argument("--disable-gpu")  # Disable GPU (recommended for headless)
chrome_options.add_argument("--no-sandbox")  # Required for some Linux environments
chrome_options.add_argument("--disable-dev-shm-usage") 

driver = webdriver.Chrome(options=chrome_options)

driver.get(page_url)

scroll_pause = 2
last_height = driver.execute_script("return document.body.scrollHeight")

message("Scrolling")
while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(scroll_pause)

    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

message("Fetching source")
page = driver.page_source
driver.quit()

soup = BeautifulSoup(page, 'html.parser')
a_tags = soup.find_all("a")
hrefs = [a.get("href") for a in a_tags]
ss_links = [h for h in hrefs if "sharedfiles/filedetails" in h]

message("Fetching image links")
content = {}
ss_count = 0

for h in ss_links:
    page = rq.get(h).text
    soup = BeautifulSoup(page, 'html.parser')
    img_link = soup.find("img", id="ActualMedia").get("src").split("?")[0]
    game = soup.select_one("div.screenshotAppName a").text
    title = soup.select_one("div.screenshotDescription")

    if not title:
        title = ""
    else:
        title = title.text

    if game not in content.keys():
        content[game] = []

    content[game].append({
        "title": title,
        "link": img_link
    })
    
    ss_count += 1

json.dump(content, open("content.json", "w"), indent=4)
message(f'Done, fetched {ss_count} screenshots from {len(content)} games.')