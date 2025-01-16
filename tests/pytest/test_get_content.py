import sys
from pathlib import Path
# Add the run directory to the path, othwerwise pytests
# fails to find the tested file.
script_path = Path(__file__).resolve().parent.parent.parent / "scripts"
sys.path.insert(0, str(script_path))

import pytest
from datetime import datetime
from get_content import extractScreenshotLinks, extractScreenshotMetadata, parseSteamDate

class TestExtractScreenshotLinks:
    def test_parseSimplePage(self):
        page_html = """
            <html>
                <body>
                    <a href="https://testlink1.com/sharedfiles/filedetails">Test link 1</a>
                    <a href="https://testlink1.com/sharedfetails">Test link</a>
                    <a href="https://testlink1.com/">Test link</a>
                    <a href="https://testlink2.com/sharedfiles/filedetails">Test link 2</a>
                    <a href="https://brokenlink.com">Test link X</a>
                </body>
            </html>
        """

        links = extractScreenshotLinks(html_text = page_html)
        assert type(links) == list
        assert len(links) == 2
        assert links[0] == "https://testlink1.com/sharedfiles/filedetails"
        assert links[1] == "https://testlink2.com/sharedfiles/filedetails"

    def test_throwErrorIfNoArgumentss(self):
        with pytest.raises(ValueError):
            extractScreenshotLinks()

class TestExtractScreenshotMetadata:
    def test_parseSimplePage(self):
        page_html = """
            <html>
                <body>
                    <img id="ActualMedia" src = "https://fake-link-to-test.com/someimage?somequery=stripthis" />
                    <div class = "screenshotAppName">
                        <a>Test game</a>
                    </div>
                    <div class = "screenshotDescription">Test title</div>
                    <div class = "detailsStatRight">Some other stat</div>
                    <div class = "detailsStatRight">21 Jan, 2024 @ 10:10pm</div>
                    <div class = "detailsStatRight">Some next stat</div>
                </body>
            </html>
        """
        metadata = extractScreenshotMetadata(html_text = page_html)
        assert type(metadata) == dict
        assert metadata["game"] == "Test game"
        assert metadata["title"] == "Test title"
        assert metadata["link"] == "https://fake-link-to-test.com/someimage"
        assert metadata["date"] == "21 January 2024"

    def test_throwErrorIfNoArguments(self):
        with pytest.raises(ValueError):
            extractScreenshotMetadata()

class TestParseSteamDate:
    def test_standardFormat(self):
        assert parseSteamDate("25 Jan, 2021 @ 12:34pm") == "25 January 2021"
        assert parseSteamDate("15 Sep, 2023") == "15 September 2023"
        assert parseSteamDate("10 May @ 7:05am") == f"10 May {datetime.now().strftime('%Y')}"

    def test_reverseFormat(self):
        assert parseSteamDate("Jan 25, 2021 @ 12:34pm") == "25 January 2021"
        assert parseSteamDate("Sep 15, 2023") == "15 September 2023"
        assert parseSteamDate("May 10 @ 7:05am") == f"10 May {datetime.now().strftime('%Y')}"