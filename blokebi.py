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
            match_data = {
                'home_team': match.find(class_='shield')['alt'],
                'away_team': match.find(class_='shield').find_next_sibling()['alt'],
                'home_score': int(match.find(class_='result').find('span').text.strip()),
                'away_score': int(match.find(class_='result').find('b').text.strip()),
                'date': match.find(class_='date').text.strip(),
                'result': self.get_match_result(match)
            }
            matches.append(match_data)
        win_loss["Wins / Loss"] = self.get_results_string(matches) 
        return [matches, win_loss]

    def get_results_string(self, matches):
        results = ''.join(match['result'] for match in matches)
        return results

###### Last 5 ######

###### Stand Out ######

    def get_standout_players(self):
        if self.source != "":
            standout_players_div = BeautifulSoup(self.source, 'html.parser').find("div", id="mod_featuredPlayers")
        else:
            return("not found")
        standout_players = []

        if standout_players_div:
            players_links = standout_players_div.select('.pv10')
            if players_links:
                # Extract photo URL for all players
                photo_urls = [player_link.find('img')['src'] for player_link in players_links]
                
                # Find the player with the highest stats
                max_stat_player_index = self.find_max_stat_player_index(players_links)

                for i, player_link in enumerate(players_links):
                    main_line = player_link.find(class_='main-line')
                    player_data = {
                        'name': player_link.find(class_='person-name').text.strip(),
                        'number': player_link.find(class_='info-box').find('span', class_='number').text.strip(),
                        'position': player_link.find(class_='info-box').find('span', class_='bg-role').text.strip(),
                        'elo': player_link.find(class_='row jc-ce').find('div').text.strip() if player_link.find(class_='row jc-ce') else None,
                        'photo_url': photo_urls[i],
                        'is_first_place': i == max_stat_player_index
                    }
                    if main_line:
                        player_data['main_line'] = main_line.text.strip()
                    else:
                        player_data['main_line'] = None

                    standout_players.append(player_data)

        return standout_players

    def find_max_stat_player_index(self, players_links):
        max_stat_player_index = 0
        max_stat = float(players_links[0].find(class_='main-line').text.strip()) if players_links[0].find(class_='main-line') else float('-inf')

        for i, player_link in enumerate(players_links):
            main_line = player_link.find(class_='main-line')
            if main_line:
                stat = float(main_line.text.strip())
                if stat > max_stat:
                    max_stat = stat
                    max_stat_player_index = i

        return max_stat_player_index

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

                    injuries.append({
                        'player_name': main_text,
                        'player_img_src': player_img_src,
                        'injury_reason': injury_reason.replace("\n", " | "),
                        'recovery_info': recovery_info
                    })

        return injuries

###### Injuries ######

###### Season ######

    def get_season_info(self):
        if self.source != "":
            season_div = BeautifulSoup(self.source, 'html.parser').find("div", id="mod_season")
        else:
            return("not found")
        season_info = {}

        if season_div:
            panel_title = season_div.find("div", class_="panel-title").text.strip()
            panel_subtitle = season_div.find("div", class_="panel-subtitle").text.strip()
            season_info['title'] = panel_title
            season_info['subtitle'] = panel_subtitle

            item_columns = season_div.find_all("div", class_="item-col")
            if item_columns:
                for column in item_columns:
                    main_line = column.find("div", class_="main-line").text.strip().replace(" ", "").replace("\n", "")
                    other_lines = column.find_all("div", class_="other-line")
                    if other_lines:
                        other_line_texts = [line.text.strip() for line in other_lines]
                    else:
                        other_line_texts = []

                    season_info[main_line] = other_line_texts

        return season_info

###### Season ######

###### Matchday ######

    def get_matchday_info(self):
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
                    matchday_data['Matchday'] = cells[0].text.strip()
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

###### Matchday ######


teams = [
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
        print(json.dumps(parser.last_five(), indent=4))
        print(json.dumps(parser.get_standout_players(), indent=4))
        print(json.dumps(parser.get_injuries_and_suspensions(), indent=4))
        print(json.dumps(parser.get_season_info(), indent=4))
        print(json.dumps(parser.get_matchday_info(), indent=4))
