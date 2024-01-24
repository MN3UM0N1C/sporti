from bs4 import BeautifulSoup
import json
import requests
from zenrows import ZenRowsClient

client = ZenRowsClient("c6301ed331b3e1626f37f9d806c6c5ea79c9642c")

class StakeScraper():
    def __init__(self):
        self.base_url = "http://stake.com"
        self.match_list_url = "http://stake.com/sports/soccer/"
        self.match_name = ""

    def get_matches(self):
        links = []
        match_page = BeautifulSoup(client.get(self.match_list_url).text, 'html.parser')
        matches = match_page.find_all("a", {"class":"link variant-link size-md align-left svelte-14e5301", "data-sveltekit-preload-data": "off"})
        for match in matches:
            links.append(f'{self.base_url}{match.get("href")}')
        return set(links)

    def parse_all_matches(self):
        results = []
        link_list = self.get_matches()
        for link in link_list:
            if "sports/soccer"in link:
                parser = BeautifulSoup(client.get(link).text, "html.parser")
                results.append(self.html_to_json(parser))
            else:
                continue
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

    def data_searcher(self, teams):
        with open('odds_data.json', 'r') as file:
            content = file.read()
        for element in json.loads(content):
            try:
                if teams[1] in list(element.values())[0].keys() and teams[0] in list(element.values())[0].keys():
                    return json.dumps(element)
                    break
            except IndexError:
                continue




scraper = StakeScraper()
#result_json = scraper.parse_all_matches()
# with open('odds_data.json', 'w') as file:
#     file.write(result_json)
print(scraper.data_searcher(["Republic of Korea", "Malaysia"]))

