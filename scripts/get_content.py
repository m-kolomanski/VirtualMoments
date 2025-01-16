"""
This is a script for content preparation. It fetches all the screenshots from a Steam profile,
then crawls links to get the actual image links and metadata that can be used for display. 
Content is then saved to a JSON file.
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import requests as rq
import json
import yaml
from datetime import datetime
from utils import message

def fetchFullScreenshotProfile(url: str) -> str:
    """
    Fetches the full HTML content of a webpage by scrolling to the bottom.
    This function uses Selenium to open a webpage in headless mode, scrolls to the bottom
    to ensure all dynamic content is loaded, and then returns the full HTML source of the page.
    Parameters:
        url (str): The URL of the webpage to fetch.
    Returns:
        str: The full HTML content of the webpage.
    """
    message("\tSetting up selenium")
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--disable-gpu")  # Disable GPU (recommended for headless)
    chrome_options.add_argument("--no-sandbox")  # Required for some Linux environments
    chrome_options.add_argument("--disable-dev-shm-usage") 

    driver = webdriver.Chrome(options=chrome_options)

    driver.get(url)

    scroll_pause = 2
    last_height = driver.execute_script("return document.body.scrollHeight")

    message("\tScrolling")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause)

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    message("\tFetching source")
    page = driver.page_source
    driver.quit()

    return page

def extractScreenshotLinks(url: str = None, html_text: str = None) -> list[str]:
    """
    Extracts screenshot links from the provided HTML content or URL.
    This function searches for all anchor tags in the HTML content and filters
    out the links that contain "sharedfiles/filedetails" in their href attribute.
    Parameters:
        url (str, optional): The URL to fetch the HTML content from. Defaults to None.
        html_text (str, optional): The HTML content as a string. Defaults to None.
    Returns:
        list[str]: A list of screenshot links found in the HTML content.
    Raises:
        ValueError: If both `url` and `html_text` are None.
    """
    if all([url is None, html_text is None]):
        raise ValueError("Either url or html_text must be provided.")
    
    if html_text is None:
        html_text = rq.get(url).text

    soup = BeautifulSoup(html_text, "html.parser")
    a_tags = soup.find_all("a")
    hrefs = [a.get("href") for a in a_tags]
    ss_links = [h for h in hrefs if "sharedfiles/filedetails" in h]

    return ss_links

def parseSteamDate(date_string):
    """
    Formats weird Steam date strings into a nicer format.
    
    Example conversion: "25 Jan, 2021 @ 12:34pm" -> "25 January 2021"

    Parameters:
        date_string (str): The input date string, as fetched from steamcommunity
                           screenshot page.
    
    Returns:
        str: The formatted date string in the format "DD Month YYYY".
    """
    if "@" in date_string:
        date_string = date_string.split("@")[0]

    date_string = date_string.strip()

    input_date_format = "%b %d, %Y" if date_string[0].isalpha() else "%d %b, %Y"

    # if the year is missing, assume current year
    if "," not in date_string:
        current_year = datetime.now().year
        date_string = f"{date_string}, {current_year}"

    parsed_date = datetime.strptime(date_string, input_date_format)
    formatted_date = parsed_date.strftime("%d %B %Y")

    return formatted_date

def extractScreenshotMetadata(url: str = None, html_text: str = None) -> dict[str, str, str, str]:
    """
    Extracts metadata from a screenshot page.
    This function retrieves and parses the HTML content of a screenshot page to extract
    metadata such as the game name, screenshot title, image link, and date.
    The HTML content can be provided directly or fetched from a URL.
    Parameters:
        url (str, optional): The URL of the screenshot page. Defaults to None.
        html_text (str, optional): The HTML content of the screenshot page. Defaults to None.
    Returns:
        dict: A dictionary with the extracted metadata:
            - game (str): The name of the game.
            - title (str): The title of the screenshot.
            - link (str): The URL of the screenshot image.
            - date (str): The date the screenshot was taken.
    Raises:
        ValueError: If both `url` and `html_text` are None.
    """

    if all([url is None, html_text is None]):
        raise ValueError("Either url or html_text must be provided.")
    
    if html_text is None:
        html_text = rq.get(url).text

    soup = BeautifulSoup(html_text, "html.parser")
    img_link = soup.find("img", id="ActualMedia").get("src").split("?")[0]
    game = soup.select_one("div.screenshotAppName a").text
    title = soup.select_one("div.screenshotDescription")
    date = soup.select("div.detailsStatRight")[1].text

    if not title:
        title = ""
    else:
        title = title.text.replace('"', '')

    return {
        "game": game,
        "title": title,
        "link": img_link,
        "date": parseSteamDate(date) 
    }


if __name__ == "__main__":
    message("Finding steam profile...")
    with open("manifest.yaml", "r") as f:
        manifest = yaml.safe_load(f)

    page_url = manifest["content"]["steam_profile_url"]
    if "screenshots" not in page_url:
        page_url += "/screenshots/"

    message("Fetching full screenshot profile...")
    page = fetchFullScreenshotProfile(page_url)

    message("Extracting screenshot links...")
    ss_links = extractScreenshotLinks(html_text = page)

    message("Extracting image links...")
    content = [extractScreenshotMetadata(url = link) for link in ss_links]

    json.dump(content, open("content.json", "w"))
    message(f"Done, fetched {len(content)} screenshots.")