"""
This script is for building Astro project by parsing the manifest and preparing
files with pages / albums.
"""

import json
import yaml

with open("manifest.yaml", "r") as f:
    manifest = yaml.safe_load(f)

with open("content.json", "r") as f:
    content = json.load(f)

with open("web/src/pages/album_template.astro", "r") as f:
    album_template = f.read()

album_covers = []
games_with_albums = []

for album in manifest['albums']:
    album_content = []
    for game in content.keys():
        if game in album['games']:
            album_content += content[game]
            games_with_albums.append(game)

    screenshots_html = [f'<Screenshot src="{screenshot["link"]}" alt="{screenshot["title"]}" />' for screenshot in album_content]

    album_html = album_template.replace("<!-- SCREENSHOTS -->", "\n".join(screenshots_html))

    page_name = album['name'].replace(' ', '_').replace(":", "").replace("'", "").lower()

    album_cover_html = f'<Album name="{album["name"]}" path="/VirtualMoments/{page_name}/" />'
    album_covers.append(album_cover_html)

    print(page_name)

    with open(f"web/src/pages/{page_name}.astro", "w") as f:
        f.write(album_html)

with open("web/src/pages/index_template.astro", "r") as f:
    index_html = f.read()

index_html = index_html.replace("<!-- ALBUMS -->", "\n".join(album_covers))
with open("web/src/pages/index.astro", "w") as f:
    f.write(index_html)
