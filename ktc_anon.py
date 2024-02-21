import requests
from bs4 import BeautifulSoup
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from tqdm import tqdm
import sys,time,random
from datetime import date

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
            # find all elements with class "onePlayer"
            for page in tqdm(range(10), desc="Linking to keeptradecut.com's 1QB rankings...",unit="page"):
                page = requests.get(URL.format(page,format))
                soup = BeautifulSoup(page.content, "html.parser")
                player_elements = soup.find_all(class_="onePlayer")
                for player_element in player_elements:
                    all_elements.append(player_element)

            # player information
            for player_element in all_elements:

                # find elements within the player container
                player_name_element = player_element.find(class_="player-name")
                player_position_element = player_element.find(class_="position")
                player_value_element = player_element.find(class_="value")
                player_age_element = player_element.find(class_="position hidden-xs")

                # extract player information
                player_name = player_name_element.get_text(strip=True)
                team_suffix = (player_name[-3:] if player_name[-3:] == 'RFA' else player_name[-4:] if player_name[-4] == 'R' else player_name[-2:] if player_name[-2:] == 'FA' else player_name[-3:] if player_name[-3:].isupper() else "")

                # remove the team suffix
                player_name = player_name.replace(team_suffix, "").strip()
                player_position_rank = player_position_element.get_text(strip=True)
                player_value = player_value_element.get_text(strip=True)
                player_value = int(player_value)
                player_position = player_position_rank[:2]

                # handle NoneType for player_age_element
                if player_age_element:
                    player_age_text = player_age_element.get_text(strip=True)
                    player_age = float(player_age_text[:4]) if player_age_text else 0
                else:
                    player_age = 0

                # split team and rookie
                if team_suffix[0] == 'R':
                    player_team = team_suffix[1:]
                    player_rookie = "Yes"
                else:
                    player_team = team_suffix
                    player_rookie = "No"

                if player_position == "PI":
                    pick_info = {
                        "Player Name": player_name,
                        "Position Rank": None,
                        "Position": player_position,
                        "Team": None,
                        "Value": player_value,
                        "Age": None,
                        "Rookie": None,
                        "SFPosition Rank": None,
                        "SFValue": 0,
                        "RdrftPosition Rank": None,
                        "RdrftValue": 0,
                        "SFRdrftPosition Rank": None,
                        "SFRdrftValue": 0
                    }
                    players.append(pick_info)

                else:
                    player_info = {
                        "Player Name": player_name,
                        "Position Rank": player_position_rank,
                        "Position": player_position,
                        "Team": player_team,
                        "Value": player_value,
                        "Age": player_age,
                        "Rookie": player_rookie,
                        "SFPosition Rank": None,
                        "SFValue": 0,
                        "RdrftPosition Rank": None,
                        "RdrftValue": 0,
                        "SFRdrftPosition Rank": None,
                        "SFRdrftValue": 0
                    }
                    players.append(player_info)
        else:
            # find all elements with class "onePlayer"
            for page in tqdm(range(10), desc="Linking to keeptradecut.com's Superflex rankings...",unit="page"):
                page = requests.get(URL.format(page,format))
                soup = BeautifulSoup(page.content, "html.parser")
                player_elements = soup.find_all(class_="onePlayer")
                for player_element in player_elements:
                    all_elements.append(player_element)

            for player_element in all_elements:

                # find elements within the player container
                player_name_element = player_element.find(class_="player-name")
                player_position_element = player_element.find(class_="position")
                player_value_element = player_element.find(class_="value")
                player_age_element = player_element.find(class_="position hidden-xs")

                # extract and print player information
                player_name = player_name_element.get_text(strip=True)
                team_suffix = (player_name[-3:] if player_name[-3:] == 'RFA' else player_name[-4:] if player_name[-4] == 'R' else player_name[-2:] if player_name[-2:] == 'FA' else player_name[-3:] if player_name[-3:].isupper() else "")

                # remove the team suffix
                player_name = player_name.replace(team_suffix, "").strip()
                player_position_rank = player_position_element.get_text(strip=True)
                player_position = player_position_rank[:2]
                player_value = player_value_element.get_text(strip=True)
                player_value = int(player_value)

                if player_position == "PI":
                    for pick in players:
                        if pick["Player Name"] == player_name:
                            pick["SFValue"] = player_value
                            break
                else:
                    for player in players:
                        if player["Player Name"] == player_name:
                            player["SFPosition Rank"] = player_position_rank
                            player["SFValue"] = player_value
                            break

    # add ktc redraft values for 'contender'/'rebuilder' evaluation
    if scrape_redraft:
        players = add_redraft_values(players)

    return players


"""
Given a scraped player value list, uploads those values to the appropriate sheet
using the appropriate league settings.
"""
def upload_to_league(players, gc, key, format='1QB', tep=0):
    # modify data for the league's settings
    if format == '1QB':
        header = ["Player Name", "Position Rank", "Position", "Team", "Value", "Age", "Rookie", "SFPosition Rank", "SFValue", "RdrftPosition Rank", "RdrftValue"]
        # add player data to the rows database
        rows_data = [[
            player["Player Name"],
            player["Position Rank"],
            player["Position"],
            player["Team"],
            player["Value"],
            player["Age"],
            player["Rookie"],
            player["SFPosition Rank"],
            player["SFValue"],
            player["RdrftPosition Rank"],
            player["RdrftValue"]
        ] for player in players]
        # add the header row
        rows_data.insert(0,header)

    elif format == 'SF':
        header = ["Player Name", "Position Rank", "Position", "Team", "Value", "Age", "Rookie", "1QBPosition Rank", "1QBValue", "RdrftPosition Rank", "RdrftValue"]
        # add player data to the rows database
        rows_data = [[
            player["Player Name"],
            player["SFPosition Rank"],
            player["Position"],
            player["Team"],
            player["SFValue"],
            player["Age"],
            player["Rookie"],
            player["Position Rank"],
            player["Value"],
            player["SFRdrftPosition Rank"],
            player["SFRdrftValue"]
        ] for player in players]
        # add the header row
        rows_data.insert(0,header)

    else:
        sys.exit(f"Error: invalid format -- {format}")

    # adjust player values by TEP setting
    rows_data = tep_adjust(rows_data, tep)

    # make player values unique for indexing and searchability
    rows_data = make_unique(rows_data)

    # open the spreadsheet, clear the first tab, append new data
    print(f"Connecting to {key[1]} google sheet...")
    spreadsheet = gc.open_by_key(key[0])
    worksheet = spreadsheet.get_worksheet(0)
    worksheet.clear()
    worksheet.append_rows(rows_data)
    print(f"Data upload to {key[1]} on {date.today().strftime('%B %d, %Y')} successful.")


"""
Scrapes all values for all players in the live keeptradecut database.

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
                        player["RdrftPosition Rank"] = player_position_rank
                        player["RdrftValue"] = player_value
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
                        player["SFRdrftPosition Rank"] = player_position_rank
                        player["SFRdrftValue"] = player_value
                        break

    return players


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

    # adjust SF, 1QB, and optionally redraft values
    values = [4, 8, 10] if rows_data[1][10] > 1 else [4, 8]

    # adjust all tight end values based on TEP level
    for value in values:
        rank = 0
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
    # make SF, 1QB, and optionally redraft values unique
    values = [4, 8, 10] if rows_data[1][10] > 1 else [4, 8]

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
Main method
"""
if __name__ == "__main__":
    # league sheet api keys
    your_league_key = ['replace this with your google sheets key', "Nickname for Your Home League (for example)"]
    # your_other_league_key = ['replace this', "Your other league (again, example)"]

    # optionally, also pull redraft values for players in database
    update_redraft = False
    if "redraft" in sys.argv:
        update_redraft = True

    # optionally, also update google sheet ktc database
    update_database = False
    if "database" in sys.argv:
        update_database = True

    # pull all player and pick values
    players = scrape_ktc(scrape_redraft=update_redraft)

    # set up google sheets credentials
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    credentials = ServiceAccountCredentials.from_json_keyfile_name('YOUR_FILEPATH/credentials.json', scope)
    gc = gspread.authorize(credentials)

    # upload appropriate values/pick values to each sheet
    upload_to_league(players, gc, your_league_key, format='1QB', tep=0)
    # upload_to_league(players, gc, your_other_league_key, format='SF', tep=1)
