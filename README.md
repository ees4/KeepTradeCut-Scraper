# KeepTradeCut-Scraper

# Export to csv (easiest option):
To do this:
1. Download ktc_to_csv.py
2. Edit the inputs in the main method to match your league settings (change the line: export_to_csv(players, format='1QB', tep=0) to match your format and tep level)
3. Type: python3 ktc_to_csv.py into your "terminal" from the same directory as ktc_to_csv.py is in.

# Export to a google sheet (more difficult):
To run this on your own (with full google sheets compatability) you need a few things:
1. install the proper softwawre (Python, BeautifulSoup, etc.) -- you will be prompted to install any missing software when you run this program from the command line.
2. A google sheet key to upload the data to. In an example url: https://docs.google.com/spreadsheets/d/YOURKEYHERE/edit#gid=ignorethis
3. A google sheets API (this is free, and will make a free google account that will need edit access to your google sheet) -- link for more info: https://developers.google.com/sheets/api/quickstart/python
4. A json file with credentials, to authorize access to the google sheet. Info on how to set this up is online, and ChatGPT is quite good at this stuff if you have more questions and can't reach me.
5. Now: fill in your sheets key, credentials, give your api google account edit access, and it should be pretty plug-and-play--everything you need to edit is in the "main" method all the way at the bottom of the file.

# Main file (for those who are curious):
This is the file I use to upload to the databank. It still contains a method to upload to individual leagues as well.

For any questions or issues, please dm kyle pitts' burner @pitts_burner on twitter (X), or u/325xi5mt on reddit.
