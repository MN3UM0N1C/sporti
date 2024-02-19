from bs4 import BeautifulSoup
import json
import requests
from fuzzywuzzy import process
from fake_useragent import UserAgent

class Parser:
    def __init__(self, user_input):
        self.user_input = user_input.lower()
        self.headers = {
            'User-Agent': UserAgent().random,
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": "https://www.google.com/",
            "DNT": "1",
            "X-Forwarded-For": "127.0.0.1",
        }
        self.initial_url = f'https://www.besoccer.com/ajax/autocomplete?q={self.user_input}'
        self.soup = BeautifulSoup(requests.get(self.initial_url, headers=self.headers).text, "html.parser")
        if len(self.soup.find_all("li")) >= 2:
            self.url = self.soup.find_all("li")[1].a['href']
            self.source = requests.get(self.url).text
        else:
            self.source = ""


###### Last 5 ######

    def get_match_result(self, match):
        class_attr = match["class"]
        if "win" in class_attr:
            return "W"
        elif "draw" in class_attr:
            return "D"
        elif "lose" in class_attr:
            return "L"
        else:
            return "Unknown"

    def last_five(self):
        if self.source != "":
            soup = BeautifulSoup(self.source, 'html.parser')
        else:
            return("not found")
        matches = []
        win_loss = {}
        for match in soup.select('.spree-box'):
            if match.find(class_='result').find_all("span")[0].find("b"):
                bold_index = 0
            else:
                bold_index = 1
            match_data = {
                'home_score': match.find(class_='result').get_text().replace("\n" ,"").replace(" ", "").split("-")[0],
                'away_score': match.find(class_='result').get_text().replace("\n" ,"").replace(" ", "").split("-")[1],
                'home_team': match.find_all(class_='shield')[0]['alt'],
                'away_team': match.find(class_='shield').find_next_sibling()['alt'],
                'date': match.find(class_='date').text.strip(),
                'result': self.get_match_result(match),
                "league" : match.find(class_='shield').find_next_sibling()['alt']
            }
            if bold_index == 0:
                match_data['home_team'] =  self.user_input
                match_data['away_team'] = match.find_all(class_='shield')[0]['alt']
            elif bold_index == 1:
                match_data['home_team'] =  match.find_all(class_='shield')[0]['alt']
                match_data['away_team'] = self.user_input
            bold_index = None
            matches.append(match_data)
        win_loss["Wins / Loss"] = self.get_results_string(matches) 
        return [matches, win_loss]

    def get_results_string(self, matches):
        results = ''.join(match['result'] for match in matches)
        return results

###### Last 5 ######

###### Stand Out ######

    def get_standout_players(self):
        standout_players_div = BeautifulSoup(self.source, 'html.parser').find("div", id="mod_featuredPlayers")
        standout_players = []

        if standout_players_div:
            # Check if there's a div with more statistics
            main_featured_player_div = standout_players_div.find("div", class_="team-squad panel-body br-bottom ph0")
            if main_featured_player_div:
                player_data = self.parse_main_featured_player(main_featured_player_div)
                player_data['featured'] = True
                standout_players.append(player_data)

            # Parse the rest of the players
            for player_link in standout_players_div.select('.pv10'):
                if "mainFeaturedPlayer" not in player_link.get("data-cy", ""):
                    player_data = {
                        'name': player_link.find(class_='person-name').text.strip(),
                        'number': player_link.find(class_='info-box').find('span', class_='number').text.strip(),
                        'position': player_link.find(class_='info-box').find('span', class_='bg-role').text.strip(),
                        'photo_url': player_link.find('img')['src'],
                        'featured': False
                    }
                    standout_players.append(player_data)

        return standout_players

    def parse_main_featured_player(self, player_div):
        player_data = {
            'name': player_div.find(class_='person-name').text.strip(),
            'number': player_div.find(class_='info-box').find('span', class_='number').text.strip(),
            'position': player_div.find(class_='info-box').find('span', class_='bg-role').text.strip(),
            'photo_url': player_div.find('img')['src']
        }
        return player_data

###### Stand Out ######

###### Injuries ######

    def get_injuries_and_suspensions(self):
        if self.source != "":
            injuries_div = BeautifulSoup(self.source, 'html.parser').find("div", id="mod_injuriesResume")
        else:
            return("not found")
        injuries = []

        if injuries_div:
            injuries_list = injuries_div.find("ul", class_="item-list")
            if injuries_list:
                for injury_li in injuries_list.find_all("li"):
                    player_box = injury_li.find("div", class_="player-box")
                    if player_box:
                        player_img_src = player_box.find("img")["src"]
                    else:
                        player_img_src = None

                    main_text = injury_li.find("a", class_="main-text").text.strip()

                    desc_boxes = injury_li.find_all("div", class_="desc-boxes")
                    if len(desc_boxes) == 2:
                        injury_reason = desc_boxes[0].text.strip()
                        recovery_info = desc_boxes[1].text.strip()
                    elif len(desc_boxes) == 1:
                        injury_reason = desc_boxes[0].text.strip()
                        recovery_info = None
                    else:
                        injury_reason = None
                        recovery_info = None
                    injury_info_list = injury_reason.split("\n")                        
                    injuries.append({
                        'player_name': main_text,
                        'player_img_src': player_img_src,
                        'injury_or_suspension_reason': injury_info_list[1],
                        'recovery_info': injury_info_list[2]
                    })

        return injuries

###### Injuries ######

###### Season ######

    def get_season_info(self):
        season_div = BeautifulSoup(self.source, 'html.parser').find("div", id="mod_season")
        season_info = {}

        if season_div:
            panel_title = season_div.find("div", class_="panel-title").text.strip()
            panel_subtitle = season_div.find("div", class_="panel-subtitle").text.strip()
            season_info['title'] = panel_title
            season_info['subtitle'] = panel_subtitle

            item_columns = season_div.find_all("div", class_="item-col")
            if item_columns:
                for column in item_columns:
                    main_line = column.find("div", class_="main-line").text.strip()
                    other_lines = column.find_all("div", class_="other-line")
                    if other_lines:
                        label = other_lines[-1].text.strip()
                        value = main_line
                        if label == "Cards / match":
                            value = value.replace("\n", "").replace(" ", "").replace("/", "/")
                        season_info[label] = [value]
                        for line in other_lines[:-1]:
                            value = line.text.strip()
                            season_info[label].append(value)

        return season_info

###### Season ######

###### League ######

    def get_league_info(self):
        if self.source != "":
            matchday_div = BeautifulSoup(self.source, 'html.parser').find("div", id="mod_leaguePerfomance").find("div", "panel-body")
        else:
            return("not found")
        matchday_info = []
        if matchday_div:
            table = matchday_div.find("table", class_="table")
            if table:
                rows = table.find_all("tr", class_="row-body")
                for row in rows:
                    matchday_data = {}
                    cells = row.find_all("td")
                    matchday_data['Standing'] = cells[0].text.strip()
                    matchday_data['Team'] = cells[2].text.strip()
                    matchday_data['PTS'] = cells[3].text.strip()
                    matchday_data['MP'] = cells[4].text.strip()
                    matchday_data['W'] = cells[5].text.strip()
                    matchday_data['D'] = cells[6].text.strip()
                    matchday_data['L'] = cells[7].text.strip()
                    matchday_data['GF'] = cells[8].text.strip()
                    matchday_data['GA'] = cells[9].text.strip()
                    matchday_data['GD'] = cells[10].text.strip()
                    matchday_info.append(matchday_data)

        return matchday_info

###### League ######


teams = [
    "borussia dortmund",
    "Las Palmas",
    "Valencia",
    "Barcelona",
    "Granada CF",
    "Real Madrid",
    "Girona",
    "Sevilla",
    "Atl. Madrid",
    "Real Sociedad",
    "Osasuna",
    "Almeria",
    "Ath Bilbao",
    "Getafe",
    "Celta Vigo",
    "Mallorca",
    "Rayo Vallecano",
    "Alaves",
    "Villarreal",
    "Cadiz CF",
    "Betis"
]

if __name__ == "__main__":
    for search in teams:
        parser = Parser(search)
        # print(json.dumps(parser.last_five(), indent=4))
        # print(json.dumps(parser.get_standout_players(), indent=4))
        # print(json.dumps(parser.get_injuries_and_suspensions(), indent=4))
        print(json.dumps(parser.get_season_info(), indent=4))
        # print(json.dumps(parser.get_league_info(), indent=4))