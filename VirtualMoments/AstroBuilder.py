"""
This script is for building Astro project by parsing the manifest and preparing
files with pages / albums.
"""
import yaml
import os
from datetime import datetime

class AstroBuilder:
    """
    Orchestrates building the Astro project from a manifest and content data.

    Arguments:
    ----------
        web_dir (str): Path to the web/ directory containing templates and output pages.
        manifest (str): List or path to manifest.yaml defining albums and games.
        content (str): Path to the content file (YAML or JSON) with screenshot data.
    """
    def __init__(self, web_dir: str, manifest: str | list, content: str | list):
        self.web_dir = web_dir
        self.pages_dir = os.path.join(web_dir, "src", "pages")
        self.covers_dir = os.path.join(web_dir, "public", "cover")
        self.manifest = manifest
        self.content = content

        if isinstance(self.manifest, str):
            with open(self.manifest, "r") as f:
                self.manifest = yaml.safe_load(f)

        if isinstance(self.content, str):
            with open(self.content, "r") as f:
                self.content = yaml.safe_load(f)

        with open(os.path.join(self.pages_dir, "album_template.astro"), "r") as f:
            self.album_template = f.read()

        with open(os.path.join(self.pages_dir, "index_template.astro"), "r") as f:
            self.index_template = f.read()

    def build(self):
        """
        Builds all album pages and the index page, writing .astro files to the pages directory.
        """
        albums = [Album(a["name"], a["games"]) for a in self.manifest["albums"]]
        albums.append(Album("Other", []))

        for album in albums:
            album.default_covers_path = self.covers_dir

        for screenshot in self.content:
            matched = any(
                screenshot["game"] in album.games and (album.addScreenshot(screenshot) or True)
                for album in albums
            )
            if not matched:
                albums[-1].addScreenshot(screenshot)

        for album in albums:
            page = AlbumPage(self.album_template, album)
            page.buildAlbumPage(save = True, dir = self.pages_dir)

        index = IndexPage(self.index_template, albums)
        index.buildIndexPage(save = True, dir = self.pages_dir)

        return albums

class Album:
    default_covers_path = "web/public/cover"
    """
    A class to represent an album containing games and screenshots.

    Attributes:
    ----------
    name (str): The name of the album.
    games (list[str]): A list of games included in the album.
    screenshots (list[str], optional): A list of screenshots associated with the album (default is an empty list).

    Methods:
    -------
    addScreenshot(screenshot):
        Adds a screenshot to the album.
    buildAlbumContent():
        Builds and returns the HTML content for the album's screenshots.
    buildAlbumCover():
        Builds and returns the HTML content for the album's cover.
    buildPageName():
        Generates and returns a URL-friendly page name based on the album's name.
    """
    def __init__(self, name: str, games: list[str], screenshots: list[dict] = None):
        """
        Initialize a new instance of the class.
        Arguments:
        ----------
            name (str): The name of the instance.
            games (str): The games associated with the instance.
            screenshots (list[dict], optional): A list of screenshots. Defaults to an empty list if not provided.
        """
        self.name = name
        self.games = games
        self.screenshots = screenshots if screenshots is not None else []

    def addScreenshot(self, screenshot: dict):
        """
        Adds a screenshot to the list of screenshots.
        Arguments:
        ----------
            screenshot (dict): The screenshot object to be added to the list.
        """
        self.screenshots.append(screenshot)

    def buildAlbumContent(self) -> str:
        """
        Generates HTML content for an album of screenshots.
        This method iterates over the `self.screenshots` list, which contains dictionaries
        with keys "link", "title", and "date". For each screenshot, it creates an HTML
        string representing an Astro <Screenshot /> component with the corresponding attributes.

        Returns:
        ----------
            str: An HTML string for Astro <AlbumCover />.
        """
        screenshots_html = [
            f'<Screenshot src="{screenshot["link"]}" alt="{screenshot["title"]}" date="{screenshot["date"]}" />'
            for screenshot in self.screenshots
        ]
        return "".join(screenshots_html)
    
    def buildAlbumCover(self) -> str:
        """
        Generates an HTML string for the Astro <AlbumCover /> component, representing the
        album cover. 

        Returns:
        ----------
            str: An HTML string for Astro <AlbumCover />.
        """
        page_name = self.buildPageName()
        cover_exists = os.path.exists(f"{self.default_covers_path}/{page_name}.svg")
        return f'''
            <AlbumCover
                name="{self.name}"
                path="/VirtualMoments/{page_name}/" 
                { f'cover="{page_name}"' if cover_exists else "" }
            />
        '''

    def buildPageName(self) -> str:
        """
        Generates a formatted, html-friendly page name by replacing spaces with underscores,
        removing colons and apostrophes, and converting the string to lowercase.

        Returns:
        ----------
            str: The formatted page name.
        """

        return self.name.replace(' ', '_').replace(":", "").replace("'", "").lower()
    
class IndexPage:
    """
    A class used to build an index page for a web application.

    Attributes:
    ----------
    default_page_dir (str): The default directory where the index page will be saved.
    template (str): The HTML template for the index page.
    albums (list[Album]): A list of Album objects to be included in the index page.

    Methods:
    ----------
    buildIndexPage(save=False, dir=None)
        Builds the index page by replacing placeholders in the template with album covers and a footer.
        If save is True, saves the generated HTML to a file in the specified directory or the default directory.
        If save is False, returns the generated HTML as a string.
    """
    default_page_dir = "web/src/pages"

    def __init__(self, template: str, albums: list[Album]):
        """
        Initializes the instance with a template and a list of albums.
        Arguments:
        ----------
            template (str): The template string to be used.
            albums (list[Album]): A list of Album objects.
        """
        self.template = template
        self.albums = albums

    def buildIndexPage(self, save: bool = False, dir: str = None) -> str:
        """
        Builds the index page for the album collection.
        This method generates the HTML content for the index page by replacing
        placeholders in the template with the album covers and the current date
        in the footer. The generated HTML can either be saved to a file or returned
        as a string.

        Arguments:
        ----------
            save (bool): If True, the generated HTML will be saved to a file.
                         If False, the generated HTML will be returned as a string.
                         Default is False.
            dir (str, optional): The directory where the index page will be saved.
                                 If not provided, the default directory will be used.

        Returns:
        ----------
            str: The generated HTML content of the index page if `save` is False.
        """
        index_html = self.template.replace(
            "<!-- ALBUMS -->",
            "".join([album.buildAlbumCover() for album in self.albums])
        )

        index_html = index_html.replace(
            "<!-- FOOTER -->",
            f'<Footer date="{datetime.now().strftime("%d %B %Y")}" />'
        )

        if save:
            if dir is None: dir = self.default_page_dir

            with open(f"{dir}/index.astro", "w", encoding="utf-8") as f:
                f.write(index_html)
        else:
            return index_html

class AlbumPage:
    """
    A class used to represent an Album Page.

    Attributes:
    ----------
    default_page_dir (str): The default directory where the album page will be saved.
    template (str): The HTML template for the album page.
    album (Album): An instance of the Album class containing album data.

    Methods:
    ----------
    buildAlbumPage(save=False, dir=None):
        Builds the album page HTML. If save is True, saves the HTML to a file in the specified directory.
    """
    default_page_dir = "web/src/pages"

    def __init__(self, template: str, album: Album):
        """
        Initializes the BuildAstro class with the given template and album.
        Arguments:
        ----------
            template (str): The template string to be used.
            album (Album): An instance of the Album class.
        """
        self.template = template
        self.album = album

    def buildAlbumPage(self, save: bool = False, dir: str = None):
        """
        Builds the HTML content for an album page.
        This method generates the HTML content for the album page by replacing
        placeholders in the template with the album content HTML. The generated
        HTML text can either be saved to a file or returned as a string.

        Arguments:
        ----------
            save (bool): If True, the generated HTML content will be saved to a file. Defaults to False.
            dir (str, optional): The directory where the file should be saved.
                                 If None, the default directory will be used. Defaults to None.

        Returns:
        ----------
            str: The generated HTML content if `save` is False.
        """
        album_html = self.template.replace("<!-- SCREENSHOTS -->", self.album.buildAlbumContent())

        if save:
            if dir is None: dir = self.default_page_dir

            with open(f"{dir}/{self.album.buildPageName()}.astro", "w", encoding="utf-8") as f:
                f.write(album_html)
        else:
            return album_html
