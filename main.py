import requests
from bs4 import BeautifulSoup
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from tqdm import tqdm
import sys,time,random
from datetime import date, datetime

"""
Scrapes all Superflex and 1QB values for all players in the live keeptradecut database.

Returns players where players is a list of player and pick dicts
"""
def scrape_ktc(scrape_redraft = False):
    # universal vars
    URL = "https://keeptradecut.com/dynasty-rankings?page={0}&filters=QB|WR|RB|TE|RDP&format={1}"
    all_elements = []
    players = []

    for format in [1,0]:
        if format == 1:
            # Find all elements with class "onePlayer"
            for page in tqdm(range(10), desc="Linking to keeptradecut.com's 1QB rankings...",unit="page"):
                page = requests.get(URL.format(page,format))
                soup = BeautifulSoup(page.content, "html.parser")
                player_elements = soup.find_all(class_="onePlayer")
                for player_element in player_elements:
                    all_elements.append(player_element)

            # Player information
            for player_element in all_elements:

                # Find elements within the player container
                player_name_element = player_element.find(class_="player-name")
                player_position_element = player_element.find(class_="position")
                player_value_element = player_element.find(class_="value")
                player_age_element = player_element.find(class_="position hidden-xs")

                # Extract player information
                player_name = player_name_element.get_text(strip=True)
                team_suffix = (player_name[-3:] if player_name[-3:] == 'RFA' else player_name[-4:] if player_name[-4] == 'R' else player_name[-2:] if player_name[-2:] == 'FA' else player_name[-3:] if player_name[-3:].isupper() else "")

                # Remove the team suffix
                player_name = player_name.replace(team_suffix, "").strip()
                player_position_rank = player_position_element.get_text(strip=True)
                player_value = player_value_element.get_text(strip=True)
                player_value = int(player_value)
                player_position = player_position_rank[:2]

                # Handle NoneType for player_age_element
                if player_age_element:
                    player_age_text = player_age_element.get_text(strip=True)
                    player_age = float(player_age_text[:4]) if player_age_text else 0
                else:
                    player_age = 0

                # Split team and rookie
                if team_suffix[0] == 'R':
                    player_team = team_suffix[1:]
                    player_rookie = "Yes"
                else:
                    player_team = team_suffix
                    player_rookie = "No"

                if player_position == "PI":
                    pick_info = {
                        "Player Name": player_name,
                        "KTC 1QB Position Rank": None,
                        "Position": player_position,
                        "Team": None,
                        "KTC 1QB Value": player_value,
                        "Age": None,
                        "Rookie": None,
                        "FantasyCalc 1QB Position Rank": None,
                        "FantasyCalc 1QB Value": 0,
                        "KTC SF Position Rank": None,
                        "KTC SF Value": 0,
                        "FantasyCalc SF Position Rank": None,
                        "FantasyCalc SF Value": 0,
                        "KTC 1QB Redraft Position Rank": None,
                        "KTC 1QB Redraft Value": 0,
                        "FantasyCalc 1QB Redraft Value": 0,
                        "FantasyCalc 1QB Position Rank": None,
                        "FantasyCalc 1QB Value": 0,
                        "KTC SF Redraft Position Rank": None,
                        "KTC SF Redraft Value": 0,
                        "FantasyCalc SF Redraft Value": 0
                    }
                    players.append(pick_info)

                else:
                    player_info = {
                        "Player Name": player_name,
                        "KTC 1QB Position Rank": player_position_rank,
                        "Position": player_position,
                        "Team": player_team,
                        "KTC 1QB Value": player_value,
                        "Age": player_age,
                        "Rookie": player_rookie,
                        "FantasyCalc 1QB Position Rank": None,
                        "FantasyCalc 1QB Value": 0,
                        "KTC SF Position Rank": None,
                        "KTC SF Value": 0,
                        "FantasyCalc SF Position Rank": None,
                        "FantasyCalc SF Value": 0,
                        "KTC 1QB Redraft Position Rank": None,
                        "KTC 1QB Redraft Value": 0,
                        "FantasyCalc 1QB Redraft Value": 0,
                        "FantasyCalc 1QB Position Rank": None,
                        "FantasyCalc 1QB Value": 0,
                        "KTC SF Redraft Position Rank": None,
                        "KTC SF Redraft Value": 0,
                        "FantasyCalc SF Redraft Value": 0
                    }
                    players.append(player_info)
        else:
            # Find all elements with class "onePlayer"
            for page in tqdm(range(10), desc="Linking to keeptradecut.com's Superflex rankings...",unit="page"):
                page = requests.get(URL.format(page,format))
                soup = BeautifulSoup(page.content, "html.parser")
                player_elements = soup.find_all(class_="onePlayer")
                for player_element in player_elements:
                    all_elements.append(player_element)

            for player_element in all_elements:

                # Find elements within the player container
                player_name_element = player_element.find(class_="player-name")
                player_position_element = player_element.find(class_="position")
                player_value_element = player_element.find(class_="value")
                player_age_element = player_element.find(class_="position hidden-xs")

                # Extract and print player information
                player_name = player_name_element.get_text(strip=True)
                team_suffix = (player_name[-3:] if player_name[-3:] == 'RFA' else player_name[-4:] if player_name[-4] == 'R' else player_name[-2:] if player_name[-2:] == 'FA' else player_name[-3:] if player_name[-3:].isupper() else "")

                # Remove the team suffix
                player_name = player_name.replace(team_suffix, "").strip()
                player_position_rank = player_position_element.get_text(strip=True)
                player_position = player_position_rank[:2]
                player_value = player_value_element.get_text(strip=True)
                player_value = int(player_value)

                if player_position == "PI":
                    for pick in players:
                        if pick["Player Name"] == player_name:
                            pick["KTC SF Value"] = player_value
                            break
                else:
                    for player in players:
                        if player["Player Name"] == player_name:
                            player["KTC SF Position Rank"] = player_position_rank
                            player["KTC SF Value"] = player_value
                            break

    players = add_redraft_values(players)

    return players


"""
Scrapes all redraft values for all players in the live keeptradecut database.

Returns players where players is a list of player and pick dicts
"""
def add_redraft_values(players):
    # universal vars
    URL = "https://keeptradecut.com/fantasy-rankings?page={0}&filters=QB|WR|RB|TE&format={1}"
    all_elements = []

    for format in [1,2]:
        if format == 1:
            # Find all elements with class "onePlayer"
            for page in tqdm(range(10), desc="Linking to keeptradecut.com's Redraft 1QB rankings...",unit="page"):
                page = requests.get(URL.format(page,format))
                soup = BeautifulSoup(page.content, "html.parser")
                player_elements = soup.find_all(class_="onePlayer")
                for player_element in player_elements:
                    all_elements.append(player_element)

            for player_element in all_elements:

                # Find elements within the player container
                player_name_element = player_element.find(class_="player-name")
                player_position_element = player_element.find(class_="position")
                player_value_element = player_element.find(class_="value")

                # Extract and print player information
                player_name = player_name_element.get_text(strip=True)
                team_suffix = (player_name[-3:] if player_name[-3:] == 'RFA' else player_name[-4:] if player_name[-4] == 'R' else player_name[-2:] if player_name[-2:] == 'FA' else player_name[-3:] if player_name[-3:].isupper() else "")

                # Remove the team suffix
                player_name = player_name.replace(team_suffix, "").strip()
                player_position_rank = player_position_element.get_text(strip=True)
                player_value = player_value_element.get_text(strip=True)
                player_value = int(player_value)

                for player in players:
                    if player["Player Name"] == player_name:
                        player["KTC 1QB Redraft Position Rank"] = player_position_rank
                        player["KTC 1QB Redraft Value"] = player_value
                        break

        else:
            # Find all elements with class "onePlayer"
            for page in tqdm(range(10), desc="Linking to keeptradecut.com's Redraft Superflex rankings...",unit="page"):
                page = requests.get(URL.format(page,format))
                soup = BeautifulSoup(page.content, "html.parser")
                player_elements = soup.find_all(class_="onePlayer")
                for player_element in player_elements:
                    all_elements.append(player_element)

            for player_element in all_elements:

                # Find elements within the player container
                player_name_element = player_element.find(class_="player-name")
                player_position_element = player_element.find(class_="position")
                player_value_element = player_element.find(class_="value")

                # Extract and print player information
                player_name = player_name_element.get_text(strip=True)
                team_suffix = (player_name[-3:] if player_name[-3:] == 'RFA' else player_name[-4:] if player_name[-4] == 'R' else player_name[-2:] if player_name[-2:] == 'FA' else player_name[-3:] if player_name[-3:].isupper() else "")

                # Remove the team suffix
                player_name = player_name.replace(team_suffix, "").strip()
                player_position_rank = player_position_element.get_text(strip=True)
                player_value = player_value_element.get_text(strip=True)
                player_value = int(player_value)

                for player in players:
                    if player["Player Name"] == player_name:
                        player["KTC SF Redraft Position Rank"] = player_position_rank
                        player["KTC SF Redraft Value"] = player_value
                        break

    return players


"""
Scrapes all values for all players in the live keeptradecut database.

Returns players where players is a list of player and pick dicts
"""
def scrape_fantasy_calc(players):
    # universal vars
    URL = "https://api.fantasycalc.com/values/current?isDynasty=true&numQbs={0}&numTeams=12&ppr=1&includeAdp=false"

    for numQBs in [1,2]:
        if numQBs == 1:
            # pull fantasycalc player values json
            print("Linking to fantasycalc.com's 1QB rankings...")
            json = requests.get(URL.format(numQBs)).json()
            for fc_player in json:
                player_name = fc_player['player']['name']
                player_position_rank = fc_player['player']['position'] + str(fc_player['positionRank'])
                player_value = fc_player['value']
                player_redraft_value = fc_player['redraftValue']
                for player in players:
                    if player["Player Name"] == player_name:
                        player["FantasyCalc 1QB Position Rank"] = player_position_rank
                        player["FantasyCalc 1QB Value"] = player_value
                        player["FantasyCalc 1QB Redraft Value"] = player_redraft_value
                        break

        else:
            # pull fantasycalc player values json
            print("Linking to fantasycalc.com's Superflex rankings...")
            json = requests.get(URL.format(numQBs)).json()
            for fc_player in json:
                player_name = fc_player['player']['name']
                player_position_rank = fc_player['player']['position'] + str(fc_player['positionRank'])
                player_value = fc_player['value']
                player_redraft_value = fc_player['redraftValue']
                for player in players:
                    if player["Player Name"] == player_name:
                        player["FantasyCalc SF Position Rank"] = player_position_rank
                        player["FantasyCalc SF Value"] = player_value
                        player["FantasyCalc SF Redraft Value"] = player_redraft_value
                        break

    return players


"""
Given a scraped player value list, uploads those values to the appropriate sheet
using the appropriate league settings.
"""
def upload_to_league(players, gc, key, format='1QB', tep=0):
    # modify data for the league's settings
    if format == '1QB':
        header = [f"Updated {date.today().strftime('%m/%d/%y')} at {datetime.now().strftime('%I:%M%p').lower()}", "Position Rank", "Position", "Team", "Value", "Age", "Rookie", "KTC SF Position Rank", "KTC SF Value", "FantasyCalc Values ->", "FantasyCalc Position Rank", "FantasyCalc Value", "FantasyCalc SF Position Rank", "FantasyCalc SF Value", "Redraft Values ->", "KTC Redraft Position Rank", "KTC Redraft Value", "FantasyCalc Redraft Value"]
        # add player data to the rows database
        rows_data = [[
            player["Player Name"],
            player["KTC 1QB Position Rank"],
            player["Position"],
            player["Team"],
            player["KTC 1QB Value"], #4
            player["Age"],
            player["Rookie"],
            player["KTC SF Position Rank"],
            player["KTC SF Value"], #10
            "", # empty column for spacing
            player["FantasyCalc 1QB Position Rank"],
            player["FantasyCalc 1QB Value"], #8
            player["FantasyCalc SF Position Rank"],
            player["FantasyCalc SF Value"], #12
            "", # empty column for spacing
            player["KTC 1QB Redraft Position Rank"],
            player["KTC 1QB Redraft Value"], #14
            player["FantasyCalc 1QB Redraft Value"] #15
        ] for player in players]
        # add the header row
        rows_data.insert(0,header)

    elif format == 'SF':
        header = [f"Updated {date.today().strftime('%m/%d/%y')} at {datetime.now().strftime('%I:%M%p').lower()}", "Position Rank", "Position", "Team", "Value", "Age", "Rookie", "KTC 1QB Position Rank", "KTC 1QB Value", "FantasyCalc Values ->", "FantasyCalc Position Rank", "FantasyCalc Value",  "FantasyCalc 1QB Position Rank", "FantasyCalc 1QB Value", "Redraft Values ->", "KTC Redraft Position Rank", "KTC Redraft Value", "FantasyCalc Redraft Value"]
        # add player data to the rows database
        rows_data = [[
            player["Player Name"],
            player["KTC SF Position Rank"],
            player["Position"],
            player["Team"],
            player["KTC SF Value"], #4
            player["Age"],
            player["Rookie"],
            player["KTC 1QB Position Rank"],
            player["KTC 1QB Value"], #10
            "", # empty column for spacing
            player["FantasyCalc SF Position Rank"],
            player["FantasyCalc SF Value"], #8
            player["FantasyCalc 1QB Position Rank"],
            player["FantasyCalc 1QB Value"], #12
            "", # empty column for spacing
            player["KTC SF Redraft Position Rank"],
            player["KTC SF Redraft Value"], #14
            player["FantasyCalc SF Redraft Value"] #15
        ] for player in players]
        # add the header row
        rows_data.insert(0,header)

    else:
        sys.exit(f"Error: invalid format -- {format}")

    # adjust player values by TEP setting, make them unique, and clean up zeroes
    rows_data = tep_adjust(rows_data, tep)
    rows_data = make_unique(rows_data)
    rows_data = clean_up(rows_data)

    # open the spreadsheet, clear the first tab, append new data
    print(f"Connecting to {key[1]} google sheet...")
    spreadsheet = gc.open_by_key(key[0])
    worksheet = spreadsheet.get_worksheet(0)
    worksheet.clear()
    worksheet.append_rows(rows_data)
    print(f"Data upload to {key[1]} on {date.today().strftime('%B %d, %Y')} successful.")


"""
Given a scraped player value list, uploads those values to the appropriate tabs of a comprehensive
sheet storing all values for all league setting combinations.
"""
def upload_to_databank(players, gc, key):
    # open the spreadsheet, clear the first tab, append new data
    print(f"Connecting to {key[1]} google sheet...")
    spreadsheet = gc.open_by_key(key[0])
    for sheet in [[1,'1QB',0],[2,'1QB',1],[3,'1QB',2],[4,'1QB',3],[5,'SF',0],[6,'SF',1],[7,'SF',2],[8,'SF',3]]:
        index = sheet[0]
        format = sheet[1]
        tep = sheet[2]
        per_sheet(players, spreadsheet, index, format, tep)

    print(f"Data upload to {key[1]} on {date.today().strftime('%B %d, %Y')} successful.")


"""
Given a scraped player value list, uploads those values to the appropriate tabs of a comprehensive
sheet storing all values for all league setting combinations.
"""
def per_sheet(players, spreadsheet, index, format, tep):
    # modify data for the league's settings
    if format == '1QB':
        header = [f"Updated {date.today().strftime('%m/%d/%y')} at {datetime.now().strftime('%I:%M%p').lower()}", "Position Rank", "Position", "Team", "Value", "Age", "Rookie", "KTC SF Position Rank", "KTC SF Value", "FantasyCalc Values ->", "FantasyCalc Position Rank", "FantasyCalc Value", "FantasyCalc SF Position Rank", "FantasyCalc SF Value", "Redraft Values ->", "KTC Redraft Position Rank", "KTC Redraft Value", "FantasyCalc Redraft Value"]
        # add player data to the rows database
        rows_data = [[
            player["Player Name"],
            player["KTC 1QB Position Rank"],
            player["Position"],
            player["Team"],
            player["KTC 1QB Value"], #4
            player["Age"],
            player["Rookie"],
            player["KTC SF Position Rank"],
            player["KTC SF Value"], #10
            "", # empty column for spacing
            player["FantasyCalc 1QB Position Rank"],
            player["FantasyCalc 1QB Value"], #8
            player["FantasyCalc SF Position Rank"],
            player["FantasyCalc SF Value"], #12
            "", # empty column for spacing
            player["KTC 1QB Redraft Position Rank"],
            player["KTC 1QB Redraft Value"], #14
            player["FantasyCalc 1QB Redraft Value"] #15
        ] for player in players]
        # add the header row
        rows_data.insert(0,header)

    elif format == 'SF':
        header = [f"Updated {date.today().strftime('%m/%d/%y')} at {datetime.now().strftime('%I:%M%p').lower()}", "Position Rank", "Position", "Team", "Value", "Age", "Rookie", "KTC 1QB Position Rank", "KTC 1QB Value", "FantasyCalc Values ->", "FantasyCalc Position Rank", "FantasyCalc Value",  "FantasyCalc 1QB Position Rank", "FantasyCalc 1QB Value", "Redraft Values ->", "KTC Redraft Position Rank", "KTC Redraft Value", "FantasyCalc Redraft Value"]
        # add player data to the rows database
        rows_data = [[
            player["Player Name"],
            player["KTC SF Position Rank"],
            player["Position"],
            player["Team"],
            player["KTC SF Value"], #4
            player["Age"],
            player["Rookie"],
            player["KTC 1QB Position Rank"],
            player["KTC 1QB Value"], #8
            "", # empty column for spacing
            player["FantasyCalc SF Position Rank"],
            player["FantasyCalc SF Value"], #11
            player["FantasyCalc 1QB Position Rank"],
            player["FantasyCalc 1QB Value"], #13
            "", # empty column for spacing
            player["KTC SF Redraft Position Rank"],
            player["KTC SF Redraft Value"], #16
            player["FantasyCalc SF Redraft Value"] #17
        ] for player in players]
        # add the header row
        rows_data.insert(0,header)

    else:
        sys.exit(f"Error: invalid format -- {format}")

    # adjust player values by TEP setting, make them unique, and clean up zeroes
    rows_data = tep_adjust(rows_data, tep)
    rows_data = make_unique(rows_data)
    rows_data = clean_up(rows_data)

    # open the spreadsheet, clear the first tab, append new data
    worksheet = spreadsheet.get_worksheet(index)
    worksheet.clear()
    worksheet.append_rows(rows_data)


"""
Given a preliminary set of player rows, adjusts the tight end values for any TEP
setting.

Returns an adjusted, re-sorted set of player rows
"""
def tep_adjust(rows_data, tep):
    # sort the original values to make sure rows_data is ordered
    header = rows_data[0]
    rows_data = sorted(rows_data[1:], key=lambda x: x[4], reverse = True)
    rows_data.insert(0,header)

    # base case
    if tep == 0:
        return rows_data

    # adjust constants based on TEP 'level'
    s = 0.2
    if tep == 1:
        t_mult = 1.1
        r = 250
    elif tep == 2:
        t_mult = 1.2
        r = 350
    elif tep == 3:
        t_mult = 1.3
        r = 450
    else:
        sys.exit(f"Error: invalid TEP value -- {tep}")

    # adjust all value columns for TEP
    values = [4, 8, 11, 13, 16, 17]

    # adjust all tight end values based on TEP level
    for value in tqdm(values, desc="Updating TEP for each value column...", unit="column"):
        rank = 0
        header = rows_data[0]
        rows_data = sorted(rows_data[1:], key=lambda x: x[value], reverse = True)
        rows_data.insert(0,header)
        max_player_val = rows_data[1][value]

        for player in rows_data[1:]:
            if player[2] == "TE":
                t = t_mult * player[value]
                n = rank / (len(rows_data) - 25) * r + s * r
                player[value] = min(max_player_val - 1, round(t + n,2))
            rank += 1

    # re-sort the adjusted values for the sheet
    header = rows_data[0]
    rows_data = sorted(rows_data[1:], key=lambda x: x[4], reverse = True)
    rows_data.insert(0,header)

    return rows_data


"""
Given a set of player rows, adjusts all the values to ensure they are unique.

Returns an adjusted, but not re-sorted, set of player rows
"""
def make_unique(rows_data):
    # make all value columns unique
    values = [4, 8, 11, 13, 16, 17]

    # adjust all values
    for value in values:
        #initialize empty set of seen values
        seen_values = set()
        for player in rows_data:
            current_value = player[value]
            while current_value in seen_values:
                # if the current value is a duplicate, subtract 0.01
                current_value -= 0.01
            # update the set of seen values
            seen_values.add(current_value)
            # update the new, unique player value
            player[value] = current_value

    return rows_data


"""
Given a set of player rows, adjusts all the values to ensure there are no unnecessary zeros.

Returns an adjusted, but not re-sorted, set of player rows
"""
def clean_up(rows_data):
    # make all value columns unique
    values = [4, 8, 11, 13, 16, 17]

    # adjust all values
    for value in values:
        for player in rows_data:
            if isinstance(player[value], (int, float)) and player[value] <= 0:
                player[value] = None

    return rows_data


"""
Main method
"""
if __name__ == "__main__":
    # league sheet api keys
    your_league_key = ['ANONYMIZED', "Your Dynasty League"]
    raw_data_sheet_key = ['ANONYMIZED', "Raw Data Sheet"]

    # pull all player and pick values
    players = scrape_ktc(scrape_redraft=True)
    players = scrape_fantasy_calc(players)

    # set up google sheets credentials
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    credentials = ServiceAccountCredentials.from_json_keyfile_name('YOUR_FILEPATH/credentials.json', scope)
    gc = gspread.authorize(credentials)

    # upload appropriate values/pick values to each sheet
    upload_to_league(players, gc, your_league_key, format='SF', tep=1)
    upload_to_databank(players, gc, raw_data_sheet_key)
