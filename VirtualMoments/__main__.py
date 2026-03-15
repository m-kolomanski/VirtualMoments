import argparse
import logging
from .ScreenshotScrapper import ScreenshotScrapper
from .AstroBuilder import AstroBuilder

parser = argparse.ArgumentParser(description="Scrape Steam screenshots for a given user.")
parser.add_argument("username", help="Steam username to scrape screenshots from")
parser.add_argument("-o", "--output", default="content.yaml", help="Output YAML file (default: content.yaml)")
parser.add_argument("-d", "--delay", type=int, default=5, help="Delay between requests in seconds (default: 5)")
parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose (debug) logging")
args = parser.parse_args()

logging.basicConfig(level=logging.INFO)
if args.verbose:
    logging.getLogger("ScreenshotScrapper").setLevel(logging.DEBUG)

scrapper = ScreenshotScrapper(args.username)
scrapper.setRequestDelay(args.delay)
content = scrapper.generateContentStructure(output = args.output)

astro_builder = AstroBuilder("web", "manifest.yaml", content)
astro_builder.build()