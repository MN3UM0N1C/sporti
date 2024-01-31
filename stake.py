from bs4 import BeautifulSoup
import json
import requests
from zenrows import ZenRowsClient
import time
from fuzzywuzzy import fuzz
import re


client = ZenRowsClient("c6301ed331b3e1626f37f9d806c6c5ea79c9642c")

class StakeScraper():
    def __init__(self):
        self.base_url = "http://stake.com"
        self.match_list_url = "http://stake.com/sports/soccer/"
        self.match_name = ""
        self.user_input = ""
        self.league_id_mapping = {
        'https://stake.com/sports/soccer/england/premier-league': 'Premier League',
        'https://stake.com/sports/soccer/spain/la-liga': 'La Liga',
        'https://stake.com/sports/soccer/germany/bundesliga': 'Bundesliga',
        'https://stake.com/sports/soccer/italy/serie-a': 'Serie A',
        'https://stake.com/sports/soccer/france/ligue-1': 'Ligue 1',
        'https://stake.com/sports/soccer/international-clubs/uefa-champions-league': 'UEFA Champions League',
        'https://stake.com/sports/soccer/international-clubs/uefa-europa-league': 'UEFA Europa League',
        }
    def get_matches(self):
        links = []
        for league in list(self.league_id_mapping.keys()):
            match_page = BeautifulSoup(client.get(league, params={"js_render": True}).text, 'html.parser')
            matches = match_page.find_all("a", {"class":"link variant-link size-md align-left svelte-14e5301", "data-sveltekit-preload-data": "off"})
            for match in matches:
                if re.match(r"http://stake.com/sports/soccer/.+/.+/.+", f'{self.base_url}{match.get("href")}'):
                    links.append(f'{self.base_url}{match.get("href")}${self.league_id_mapping[league]}')
            time.sleep(4)
        return set(links)

    def parse_all_matches(self):
        results = []     
        link_dict = {key: value for pair in self.get_matches() for key, value in [pair.split('$')]}
        for link, league in link_dict.items():
            if "sports/soccer"in link:
                print(link)
                parser = BeautifulSoup(client.get(link, params={"js_render": True}).text, "html.parser")
                results.append({league : self.html_to_json(parser)})
            else:
                continue
        print(results)
        return json.dumps(results)

    def extract_odds_data(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        odds_data = {}
        outcome_elements = soup.find_all('button', {'class': 'outcome'})
        for outcome in outcome_elements:
            team_name = outcome.find('span', {'class': 'name'}).text.strip()
            odds_value = outcome.find('span', {'class': 'weight-bold'}).text.strip()
            odds_data[team_name] = float(odds_value)
        return odds_data

    def html_to_json(self, html):
        soup = html
        json_data = {}
        accordion_elements = soup.find_all('div', {'class': 'secondary-accordion'})
        for index, accordion in enumerate(accordion_elements):
            market_name = accordion.find('span', {'class': 'weight-semibold'}).text.strip()
            odds_data = self.extract_odds_data(str(accordion))
            json_data[f'market_{index + 1}_{market_name}'] = odds_data
        return json_data

    def data_searcher(self, teams, league):
        with open('odds_data.json', 'r') as file:
            content = file.read()
        best_match_score = 0
        best_match = None
        for element in json.loads(content):
            try:
                element_teams = list(list(list(element.values())[0].values())[0].keys())
                element_league = list(element.keys())[0]
                if league.lower() == element_league.lower():
                    for team in teams:
                        for element_team in element_teams:
                            match_score = fuzz.partial_ratio(team.lower(), element_team.lower())
                            if match_score > best_match_score:
                                best_match_score = match_score
                                best_match = element
                if best_match_score >= 90:  # Adjust the threshold as needed
                    return json.dumps(best_match)
            except IndexError:
                continue


class BasketballStakeScraper():
    def __init__(self):
        self.base_url = "http://stake.com"
        self.match_list_url = "http://stake.com/sports/soccer/"
        self.match_name = ""
        self.user_input = ""
        self.league_id_mapping = {
        'https://stake.com/sports/basketball/usa/nba': 'NBA',
        'https://stake.com/sports/basketball/usa/ncaa-regular': 'NCAA',
        'https://stake.com/sports/basketball/international/euroleague': 'Euroleague',
        'https://stake.com/sports/basketball/international/eurocup': 'Eurocup',
        }
    def get_matches(self):
        links = []
        matches = []
        for league in list(self.league_id_mapping.keys()):
            match_page = BeautifulSoup(client.get(league, params={"js_render": True}).text, 'html.parser')
            matches = match_page.find_all("a", {"class":"link variant-link size-md align-left svelte-14e5301", "data-sveltekit-preload-data": "off"})
            for match in matches:
                if re.match(r"http://stake.com/sports/basketball/.+/.+/.+", f'{self.base_url}{match.get("href")}'):
                    links.append(f'{self.base_url}{match.get("href")}${self.league_id_mapping[league]}')
            time.sleep(4)
        return set(links)

    def parse_all_matches(self):
        results = []    
        link_dict = {key: value for pair in self.get_matches() for key, value in [pair.split('$')]}
        for link, league in link_dict.items():
            if "sports/basketball/"in link:
                print(link)
                parser = BeautifulSoup(client.get(link, params={"js_render": True}).text, "html.parser")
                results.append({league : self.html_to_json(parser)})
            else:
                continue
        print(results)
        return json.dumps(results)

    def extract_odds_data(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        odds_data = {}
        outcome_elements = soup.find_all('button', {'class': 'outcome'})
        for outcome in outcome_elements:
            team_name = outcome.find('span', {'class': 'name'}).text.strip()
            odds_value = outcome.find('span', {'class': 'weight-bold'}).text.strip()
            odds_data[team_name] = float(odds_value)
        return odds_data

    def html_to_json(self, html):
        soup = html
        json_data = {}
        accordion_elements = soup.find_all('div', {'class': 'secondary-accordion'})
        for index, accordion in enumerate(accordion_elements):
            market_name = accordion.find('span', {'class': 'weight-semibold'}).text.strip()
            odds_data = self.extract_odds_data(str(accordion))
            json_data[f'market_{index + 1}_{market_name}'] = odds_data
        return json_data

    def data_searcher(self, teams, league):
        with open('basketball_odds_data.json', 'r') as file:
            content = file.read()
        best_match_score = 0
        best_match = None
        for element in json.loads(content):
            try:
                element_teams = list(list(list(element.values())[0].values())[0].keys())
                element_league = list(element.keys())[0]
                if league.lower() == element_league.lower():
                    for team in teams:
                        for element_team in element_teams:
                            match_score = fuzz.partial_ratio(team.lower(), element_team.lower())
                            if match_score > best_match_score:
                                best_match_score = match_score
                                best_match = element
                if best_match_score >= 90:  # Adjust the threshold as needed
                    return json.dumps(best_match)
            except IndexError:
                continue

class TennisScraper():
    def __init__(self):
        self.base_url = "http://stake.com"
        self.match_name = ""
        self.user_input = ""
        self.league_id_mapping = {
        'https://stake.com/sports/tennis/atp/atp-montpellier-france-men-singles': 'ATP France Men Single',
        'https://stake.com/sports/tennis/atp/atp-montpellier-france-men-double': 'ATP France Men double',
        'https://stake.com/sports/tennis/wta/wta-linz-austria-women-singles': 'WTA Austria Women Single',
        'https://stake.com/sports/tennis/wta/wta-hua-hin-thailand-women-singles': 'WTA Thailand Women Single',
        'https://stake.com/sports/tennis/wta/wta-hua-hin-thailand-women-double' : 'WTA Thailand Women Double',
        'https://stake.com/sports/tennis/wta/wta-linz-austria-women-doubles' : 'WTA Austria Women Double',
        }
    def get_matches(self):
        links = []
        matches = []
        for league in list(self.league_id_mapping.keys()):
            match_page = BeautifulSoup(client.get(league, params={"js_render": True}).text, 'html.parser')
            matches = match_page.find_all("a", {"class":"link variant-link size-md align-left svelte-14e5301", "data-sveltekit-preload-data": "off"})
            for match in matches:
                if re.match(r"http://stake.com/sports/tennis/.+/.+/.+", f'{self.base_url}{match.get("href")}'):
                    links.append(f'{self.base_url}{match.get("href")}${self.league_id_mapping[league]}')
            time.sleep(4)
        return set(links)

    def parse_all_matches(self):
        results = []    
        link_dict = {key: value for pair in self.get_matches() for key, value in [pair.split('$')]}
        for link, league in link_dict.items():
            if "sports/tennis/"in link:
                print(link)
                parser = BeautifulSoup(client.get(link, params={"js_render": True}).text, "html.parser")
                results.append({league : self.html_to_json(parser)})
            else:
                continue
        print(results)
        return json.dumps(results)

    def extract_odds_data(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        odds_data = {}
        outcome_elements = soup.find_all('button', {'class': 'outcome'})
        for outcome in outcome_elements:
            team_name = outcome.find('span', {'class': 'name'}).text.strip()
            if outcome.find('span', {'class': 'weight-bold'}) != None:
                odds_value = outcome.find('span', {'class': 'weight-bold'}).text.strip()
                odds_data[team_name] = float(odds_value)
        return odds_data

    def html_to_json(self, html):
        soup = html
        json_data = {}
        accordion_elements = soup.find_all('div', {'class': 'secondary-accordion'})
        for index, accordion in enumerate(accordion_elements):
            market_name = accordion.find('span', {'class': 'weight-semibold'}).text.strip()
            odds_data = self.extract_odds_data(str(accordion))
            json_data[f'market_{index + 1}_{market_name}'] = odds_data
        return json_data

    def data_searcher(self, teams, league):
        with open('tennis_odds_data.json', 'r') as file:
            content = file.read()
        best_match_score = 0
        best_match = None
        for element in json.loads(content):
            try:
                element_teams = list(list(list(element.values())[0].values())[0].keys())
                element_league = list(element.keys())[0]
                if league.lower() == element_league.lower():
                    for team in teams:
                        for element_team in element_teams:
                            match_score = fuzz.partial_ratio(team.lower(), element_team.lower())
                            if match_score > best_match_score:
                                best_match_score = match_score
                                best_match = element
                if best_match_score >= 90:  # Adjust the threshold as needed
                    return json.dumps(best_match)
            except IndexError:
                continue

class MMAScraper():
    def __init__(self):
        self.base_url = "http://stake.com"
        self.match_name = ""
        self.user_input = ""
        self.league_id_mapping = {'https://stake.com/sports/mma' : 'UFC'
        }
    def get_matches(self):
        links = []
        matches = []
        for league in list(self.league_id_mapping.keys()):
            match_page = BeautifulSoup(client.get(league, params={"js_render": True}).text, 'html.parser')
            matches = match_page.find_all("a", {"class":"link variant-link size-md align-left svelte-14e5301", "data-sveltekit-preload-data": "off"})
            for match in matches:
                if re.match(r"http://stake.com/sports/mma/.+/.+/.+", f'{self.base_url}{match.get("href")}'):
                    links.append(f'{self.base_url}{match.get("href")}${self.league_id_mapping[league]}')
            time.sleep(4)
        return set(links)

    def parse_all_matches(self):
        results = []    
        link_dict = {key: value for pair in self.get_matches() for key, value in [pair.split('$')]}
        print(link_dict)
        for link, league in link_dict.items():
            if "sports/mma/"in link:
                print(link)
                parser = BeautifulSoup(client.get(link, params={"js_render": True}).text, "html.parser")
                results.append({league : self.html_to_json(parser)})
            else:
                continue
        print(results)
        return json.dumps(results)

    def extract_odds_data(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        odds_data = {}
        outcome_elements = soup.find_all('button', {'class': 'outcome'})
        for outcome in outcome_elements:
            team_name = outcome.find('span', {'class': 'name'}).text.strip()
            if outcome.find('span', {'class': 'weight-bold'}) != None:
                odds_value = outcome.find('span', {'class': 'weight-bold'}).text.strip()
                odds_data[team_name] = float(odds_value)
        return odds_data

    def html_to_json(self, html):
        soup = html
        json_data = {}
        accordion_elements = soup.find_all('div', {'class': 'secondary-accordion'})
        for index, accordion in enumerate(accordion_elements):
            market_name = accordion.find('span', {'class': 'weight-semibold'}).text.strip()
            odds_data = self.extract_odds_data(str(accordion))
            json_data[f'market_{index + 1}_{market_name}'] = odds_data
        return json_data

    def data_searcher(self, teams, league):
        with open('mma_odds_data.json', 'r') as file:
            content = file.read()
        best_match_score = 0
        best_match = None
        for element in json.loads(content):
            try:
                element_teams = list(list(list(element.values())[0].values())[0].keys())
                element_league = list(element.keys())[0]
                if league.lower() == element_league.lower():
                    for team in teams:
                        for element_team in element_teams:
                            match_score = fuzz.partial_ratio(team.lower(), element_team.lower())
                            if match_score > best_match_score:
                                best_match_score = match_score
                                best_match = element
                if best_match_score >= 90:  # Adjust the threshold as needed
                    return json.dumps(best_match)
            except IndexError:
                continue


#scraper = StakeScraper()
# result_json = scraper.parse_all_matches()
# with open('odds_data.json', 'w') as file:
#     file.write(result_json)
#print(scraper.data_searcher(["luton town", "Brighton & Hove Albion "], "Premier League"))

# basketball_scraper = BasketballScraper()
# result_json = basketball_scraper.parse_all_matches()
# with open('basketball_odds_data.json', 'w') as file:
#     file.write(result_json)
# print(basketball_scraper.data_searcher(["Cazaux, Arthur", "Marterer, Maximilian"], "ATP France Men Single"))

# tennis_scraper = TennisScraper()
# result_json = tennis_scraper.parse_all_matches()
# with open('tennis_odds_data.json', 'w') as file:
#     file.write(result_json)
# print(tennis_scraper.data_searcher(["Cazaux, Arthur", "Marterer, Maximilian"], "ATP France Men Single"))

# mma_scraper = MMAScraper()
# result_json = mma_scraper.parse_all_matches()
# with open('mma_odds_data.json', 'w') as file:
#     file.write(result_json)
# print(mma_scraper.data_searcher(["Rodriguez, Pete", "Gorimbo, Themba"], "UFC"))






