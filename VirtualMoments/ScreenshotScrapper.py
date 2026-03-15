from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import requests as rq
import yaml
from datetime import datetime, timedelta
import logging
import os
from dataclasses import dataclass

@dataclass
class Screenshot:
    page_link: str
    game: str
    title: str
    link: str
    date: str

class ScreenshotScrapper:
    """
    Scraps screenshot links and metadata from Steam profile.

    Arguments:
    ----------
        steam_user_name (str): Steam user name.
    """
    logger = logging.getLogger("ScreenshotScrapper")
    _request_delay: int = 5

    def __init__(self, steam_user_name: str):
        self.logger.info(f"Initializing ScreenshotScrapper for {steam_user_name}")
        self.profile_url = f"https://steamcommunity.com/id/{steam_user_name}/screenshots/"

        self.profile_page: str = None
        self.profile_links: list[str] = None
        self.content_structure: list[dict[str, str, str, str]] = []

    def generateContentStructure(self, output: str = None):
        """
        Fetches screenshot links from profile page and
        constructs the structure of the content with metadata.
        Parameters:
            output (str, optional): Output file to save the structure to in a YAML file.
        Returns:
            list[dict] A list of dictionaries with the extracted metadata:
            - game (str): The name of the game.
            - title (str): The title of the screenshot.
            - link (str): The URL of the screenshot image.
            - date (str): The date the screenshot was taken.
        """

        self.logger.info("Fetching full steam screenshot profile")
        self.fetchFullProfile()

        self.logger.info("Extracting screenshot links from the page")
        self.extractScreenshotLinks()

        n_links = len(self.profile_links)
        self.logger.info(f"Extracting metadata for {n_links} links")

        content_structure = []
        cached_links = []
        if os.path.exists(output):
            with open(output, "r") as f:
                content_structure = yaml.safe_load(f)
                cached_links = (l["page_link"] for l in content_structure)

        estimated_time = self._request_delay * n_links
        finish_time = datetime.now() + timedelta(seconds = estimated_time)
        self.logger.info(f"Estimated time: {estimated_time} seconds, finish at {finish_time.strftime('%H:%M:%S')}")

        for link in self.profile_links:
            if link in cached_links:
                self.logger.info(f"\tSkipping {link}, already cached")
                continue
            time.sleep(self._request_delay)
            try:
                content_structure.append(self.extractScreenshotMetadata(url = link))
            except Exception:
                self.logger.error(f"Failed fetching metadata for {link}")
                self.logger.error("Partial content is returned")
                break

        self.content_structure = content_structure

        if output is not None:
            with open(output, "w") as f:
                # TODO: this saves object names as names of entries in yaml, crashing the load
                yaml.dump(self.content_structure, f, default_flow_style = False)

        return self.content_structure
    
    def fetchFullProfile(self) -> str:
        """
        Fetches the full HTML content of a webpage by scrolling to the bottom.
        This function uses Selenium to open a webpage in headless mode, scrolls to the bottom
        to ensure all dynamic content is loaded, and then returns the full HTML source of the page.
        Returns:
            str: The full HTML content of the webpage.
        """
        self.logger.debug("\tSetting up selenium")
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in headless mode
        chrome_options.add_argument("--disable-gpu")  # Disable GPU (recommended for headless)
        chrome_options.add_argument("--no-sandbox")  # Required for some Linux environments
        chrome_options.add_argument("--disable-dev-shm-usage") 

        driver = webdriver.Chrome(options=chrome_options)

        driver.get(self.profile_url)

        scroll_pause = 2
        last_height = driver.execute_script("return document.body.scrollHeight")

        self.logger.debug("\tScrolling")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(scroll_pause)

            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        self.logger.debug("\tFetching source")
        page = driver.page_source
        driver.quit()

        self.profile_page = page
        return page
    
    def extractScreenshotLinks(self) -> list[str]:
        """
        Extracts screenshot links from the provided HTML content or URL.
        This function searches for all anchor tags in the HTML content and filters
        out the links that contain "sharedfiles/filedetails" in their href attribute.
        Returns:
            list[str]: A list of screenshot links found in the HTML content.
        Raises:
            ValueError: If both `url` and `html_text` are None.
        """
        if self.profile_page is None:
            raise ValueError("Page should not be empty - fetch profile page first.")

        soup = BeautifulSoup(self.profile_page, "html.parser")
        a_tags = soup.find_all("a")
        hrefs = [a.get("href") for a in a_tags]
        ss_links = [h for h in hrefs if "sharedfiles/filedetails" in h]

        self.profile_links = ss_links
        return ss_links
    
    def extractScreenshotMetadata(self, url: str = None) -> dict[str, str, str, str]:
        """
        Extracts metadata from a screenshot page.
        This function retrieves and parses the HTML content of a screenshot page to extract
        metadata such as the game name, screenshot title, image link, and date.
        The HTML content can be provided directly or fetched from a URL.
        Parameters:
            url (str, optional): The URL of the screenshot page. Defaults to None.
        Returns:
            dict: A dictionary with the extracted metadata:
                - game (str): The name of the game.
                - title (str): The title of the screenshot.
                - link (str): The URL of the screenshot image.
                - date (str): The date the screenshot was taken.
        Raises:
            ValueError: If both `url` and `html_text` are None.
        """
        if url is None:
            raise ValueError("Provide screenshot url.")
        
        self.logger.debug(f"\tFetching metadata for {url}")

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

        return Screenshot(
            page_link = url,
            game = game,
            title = title,
            link = img_link,
            date = self.parseSteamDate(date)
        )
    
    def parseSteamDate(self, date_string):
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
    
    def setRequestDelay(self, delay: int):
        """
        Sets request delay in seconds.
        Steam can block your IP of there are too many requests in short time.
        Having a delay between requests remedies that situation.
        Default delay is 5 seconds, but you can change it with this function.
        """
        self._request_delay = delay
