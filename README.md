# KeepTradeCut-Scraper
A python program to scrape the keeptradecut website and upload data to a google sheet.

To run this on your own (with full google sheets compatability) you need a few things:
1. install the proper softwawre (Python, BeautifulSoup, etc.) -- you will be prompted to install any missing software when you run this program from the command line.
2. A google sheet key to upload the data to. In an example url: https://docs.google.com/spreadsheets/d/YOURKEYHERE/edit#gid=ignorethis
3. A google sheets API (this is free, and will make a free google account that will need edit access to your google sheet) -- link for more info: https://developers.google.com/sheets/api/quickstart/python
4. A json file with credentials, to authorize access to the google sheet. Info on how to set this up is online, and ChatGPT is quite good at this stuff if you have more questions and can't reach me.

Fill in your sheets key, credentials, give your api google account edit access, and it should be pretty plug-and-play--everything you need to edit is in the "main" method all the way at the bottom of the file.