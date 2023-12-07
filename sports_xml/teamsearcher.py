from bs4 import BeautifulSoup
import json
import requests
import subprocess

class FootballDataParser:
    def __init__(self, league_id_mapping):
        self.league_id_mapping = league_id_mapping
        self.base_url = "https://www.goalserve.com/getfeed/401117231212497fb27a08db8de47c17/getodds/soccer?cat=soccer_10&League="

    def download_file(self, league_id, output_file):
        try:
            url = f"{self.base_url}{league_id}"
            subprocess.run(['curl', '-o', f"data/{output_file}", url], check=True)
            print(f"File downloaded successfully: {output_file}")
        except subprocess.CalledProcessError as e:
            print(f"Error downloading file: {e}")

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
                return self.search(league_id, matches[c].get("id"), casino=casino)
            c += 1

    def koef(self, file):
        data = [(k.get('name'), k.get('value')) for i in file for k in i.find_all('odd')]
        return json.dumps(dict(data))

    def download_all_files(self):
        for league_id, league_name in self.league_id_mapping.items():
            self.download_file(league_id, f"{league_name}.xml")


if __name__ == "__main__":
    # Example usage:
    league_id_mapping = {
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

    football_parser = FootballDataParser(league_id_mapping)
    football_parser.download_all_files()
    result = football_parser.koef(football_parser.team("1204", ["Everton", "Newcastle"], casino="10Bet"))
    print(result)
