from bs4 import BeautifulSoup
import json

class FootballDataParser:
    def __init__(self):
        self.league_id_mapping = {
            '1204': 'Premier_League',
            '1399': 'La_Liga',
            '1229': 'Bundesliga',
            '1269': 'Serie_A',
            '1221': 'Ligue_1',
            '1440': 'MLS',
            '1368': 'Saudi_League',
            '1005': 'UEFA_Champions_League',
            '1007': 'UEFA_Europa_League',
        }

    def load_data(self, league_id):
        with open(f'data/{self.league_id_mapping[league_id]}.xml', 'r') as file:
            xml_content = file.read()
            return BeautifulSoup(xml_content, 'xml')

    def search(self, league_id, match, casino=None):
        result = []
        soup = self.load_data(league_id)
        for k in soup.find_all("match", {"id": match}):
            if casino is not None:
                result = k.find_all('bookmaker', {'name': casino})
            else:
                result = k.find_all('bookmaker')
        return result

    def team(self, league_id, teams, casino=None):
        c = 0
        soup = self.load_data(league_id)
        matches = soup.find_all("match")
        for i in matches:
            bundle = [i.find("localteam").get("name"), i.find("visitorteam").get("name")]
            if teams[0] in bundle and teams[1] in bundle:
                print(matches[c].get("id"))
                return self.search(league_id, matches[c].get("id"), casino=casino)
            c += 1

    def koef(self, file):
        data = [(k.get('name'), k.get('value')) for i in file for k in i.find_all('odd')]
        return json.dumps(dict(data))

football_parser = FootballDataParser()
print(football_parser.koef(football_parser.team("1204", ["Everton", "Newcastle"], casino="10Bet")))
