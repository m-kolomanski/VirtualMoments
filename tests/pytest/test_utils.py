import sys
from pathlib import Path
from datetime import datetime
# Add the run directory to the path, othwerwise pytests
# fails to find the tested file.
script_path = Path(__file__).resolve().parent.parent.parent / "scripts"
sys.path.insert(0, str(script_path))

from utils import parseSteamDate

class TestParseSteamDate:
    def test_standardFormat(self):
        assert parseSteamDate("25 Jan, 2021 @ 12:34pm") == "25 January 2021"
        assert parseSteamDate("15 Sep, 2023") == "15 September 2023"
        assert parseSteamDate("10 May @ 7:05am") == f"10 May {datetime.now().strftime('%Y')}"

    def test_reverseFormat(self):
        assert parseSteamDate("Jan 25, 2021 @ 12:34pm") == "25 January 2021"
        assert parseSteamDate("Sep 15, 2023") == "15 September 2023"
        assert parseSteamDate("May 10 @ 7:05am") == f"10 May {datetime.now().strftime('%Y')}"