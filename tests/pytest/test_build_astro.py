import sys
from pathlib import Path
# Add the run directory to the path, othwerwise pytests
# fails to find the tested file.
script_path = Path(__file__).resolve().parent.parent.parent / "scripts"
sys.path.insert(0, str(script_path))

import pytest
from datetime import datetime
from build_astro import Album, IndexPage, AlbumPage

@pytest.fixture
def album():
    return Album(
            name = "Test album", 
            games = ["Game 1", "Game 2"],
            screenshots = [
                {"game": "Game 1", "title": "Test title 1", "link": "https://test-link1.com", "date": "21 January 2024"},
                {"game": "Game 2", "title": "Test title 2", "link": "https://test-link2.com", "date": "25 January 2025"}
            ]
        )

class TestAlbum:
    def test_createAlbum(self):
        album = Album("Test album", ["Game 1", "Game 2"])

        assert album.name == "Test album"
        assert album.games == ["Game 1", "Game 2"]
        assert album.screenshots == []

    def test_addScreenshot(self, album):
        screenshot = {
            "game": "Game 1",
            "title": "Test title",
            "link": "https://test-link.com",
            "date": "21 January 2024"
        }

        album.addScreenshot(screenshot)

        assert len(album.screenshots) == 3
        assert album.screenshots[2] == screenshot

    def test_buildAlbumContent(self, album):
        album_content = album.buildAlbumContent()

        assert type(album_content) == str
        assert '<Screenshot src="https://test-link1.com" alt="Test title 1" date="21 January 2024" />' in album_content
        assert '<Screenshot src="https://test-link2.com" alt="Test title 2" date="25 January 2025" />' in album_content

    def test_buildAlbumCover(self, album):
        album_cover = album.buildAlbumCover()

        assert '<AlbumCover' in album_cover
        assert 'name="Test album"' in album_cover 
        assert 'path="/VirtualMoments/test_album/"' in album_cover
        assert '/>' in album_cover

    def test_buildPageName(self, album):
        page_name1 = album.buildPageName()
        assert page_name1 == "test_album"

        album2 = Album("ThiS is A'n: Album", [])
        page_name2 = album2.buildPageName()
        assert page_name2 == "this_is_an_album"

class TestIndexPage:
    @pytest.fixture
    def index_page(self, album):
        template = """
            <html>
                <body>
                    <!-- ALBUMS -->
                    <!-- FOOTER -->
                </body>
            </html>
        """
        return IndexPage(template, [album])

    def test_buildIndexPage(self, index_page):
        index_html = index_page.buildIndexPage()

        assert type(index_html) == str

        assert '<html>' in index_html
        assert '<body>' in index_html
        assert '</html>' in index_html
        assert '<AlbumCover' in index_html
        assert f'<Footer date="{datetime.now().strftime("%d %B %Y")}" />' in index_html

    def test_buildIndexPage_save(self, index_page, tmp_path):
        index_page.buildIndexPage(save=True, dir=tmp_path)

        index_file = tmp_path / "index.astro"
        assert index_file.exists()

        with open(index_file, "r", encoding="utf-8") as f:
            index_html = f.read()

        assert '<html>' in index_html
        assert '<body>' in index_html
        assert '</html>' in index_html
        assert '<AlbumCover' in index_html
        assert f'<Footer date="{datetime.now().strftime("%d %B %Y")}" />' in index_html

class TestAlbumPage:
    @pytest.fixture
    def album_page(self, album):
        template = """
            <html>
                <body>
                    <!-- SCREENSHOTS -->
                </body>
            </html>
        """
        return AlbumPage(template, album)
    
    @pytest.fixture
    def expected_html(self):
        return '<Screenshot src="https://test-link1.com" alt="Test title 1" date="21 January 2024" />'

    def test_buildAlbumPage(self, album_page, expected_html):
        album_html = album_page.buildAlbumPage()

        assert type(album_html) == str
        assert '<Screenshot src="https://test-link1.com" alt="Test title 1" date="21 January 2024" />' in album_html
        assert '<Screenshot src="https://test-link2.com" alt="Test title 2" date="25 January 2025" />' in album_html

    def test_buildAlbumPage_save(self, album_page, tmp_path):
        album_page.buildAlbumPage(save=True, dir=tmp_path)

        album_file = tmp_path / "test_album.astro"
        assert album_file.exists()

        with open(album_file, "r", encoding="utf-8") as f:
            album_html = f.read()

        assert '<Screenshot src="https://test-link1.com" alt="Test title 1" date="21 January 2024" />' in album_html
        assert '<Screenshot src="https://test-link2.com" alt="Test title 2" date="25 January 2025" />' in album_html