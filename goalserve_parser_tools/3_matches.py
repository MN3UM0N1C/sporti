from bs4 import BeautifulSoup
import os
import json


class BasketballMatchAnalyzer:
    def __init__(self, sport):
        self.sport = sport
        self.xml_folder = f'app/odds/{sport}'
        self.matches = []

    def load_data(self):
        for filename in os.listdir(self.xml_folder):
            if filename.endswith('.xml'):
                file_path = os.path.join(self.xml_folder, filename)
                with open(file_path, 'r') as file:
                    xml_data = file.read()
                soup = BeautifulSoup(xml_data, 'xml')
                matches = soup.find_all('match')
                if self.sport == "football":
                    versus_team = "visitorteam"
                else:
                    versus_team = "awayteam"
                for match in matches:
                    match_data = {
                        "type_value": match.find('type')['value'],
                        "local_team": match.find('localteam')['name'],
                        "away_team": match.find(versus_team)['name'],
                        "odds_home": float(match.find('odd', {'name': 'Home'})['value']),
                        "odds_away": float(match.find('odd', {'name': 'Away'})['value'])
                    }
                    self.matches.append(match_data)

    def analyze_matches(self):
        output = {}
        types = set(match['type_value'] for match in self.matches)
        for type_value in types:
            type_matches = [match for match in self.matches if match['type_value'] == type_value]
            sorted_matches = sorted(type_matches, key=lambda x: x['odds_home'])
            small_odds = sorted_matches[0]
            medium_odds = sorted_matches[len(sorted_matches) // 2]
            high_odds = sorted_matches[-1]
            output[type_value] = {
                "small_odds": {
                    "local_team_name": small_odds["local_team"],
                    "away_team_name": small_odds["away_team"],
                    "odds": min(small_odds["odds_home"], small_odds["odds_away"])
                },
                "medium_odds": {
                    "local_team_name": medium_odds["local_team"],
                    "away_team_name": medium_odds["away_team"],
                    "odds": (medium_odds["odds_home"] + medium_odds["odds_away"]) / 2
                },
                "high_odds": {
                    "local_team_name": high_odds["local_team"],
                    "away_team_name": high_odds["away_team"],
                    "odds": max(high_odds["odds_home"], high_odds["odds_away"])
                }
            }
        return output

def main():
    analyzer = BasketballMatchAnalyzer("mma")
    analyzer.load_data()
    analysis_result = analyzer.analyze_matches()
    print(json.dumps(analysis_result))

if __name__ == "__main__":
    main()


