# VirtualMoments
Personal page for sharing game screenshots scraped from Steam screenshot service

## Scraping
All images are hosted using Steam screenshot hosting service. There is no API for this service, so links to the content need to be scrapped. Selenium is used to scroll through a steam profile page to load all screenshots and links to image pages are obtained. Then from each image page, a direct link to the content is obtained and saved.

### Todo
- Python script scraping the links and metadata about personal screenshots and creating a manifest file, which is used for generating a web page
- Personal web page with Astro, using the manifest to generate folders and image displays
- Build process to deploy ready product to github pages
