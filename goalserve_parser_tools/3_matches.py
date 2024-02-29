

from bs4 import BeautifulSoup
import os
import json

class BasketballMatchAnalyzer:
    def __init__(self, sport, unique=False, cache_file='cache.json'):
        self.sport = sport
        self.xml_folder = f'app/odds/{sport}'
        self.matches = []
        self.unique = unique
        self.cache_file = cache_file

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

    def is_cached(self, output):
        if not os.path.exists(self.cache_file):
            return False
        with open(self.cache_file, 'r') as f:
            cached_data = json.load(f)
            return output in cached_data

    def cache_output(self, output):
        if os.path.exists(self.cache_file):
            with open(self.cache_file, 'r') as f:
                cached_data = json.load(f)
        else:
            cached_data = []
        cached_data.append(output)
        with open(self.cache_file, 'w') as f:
            json.dump(cached_data, f)

    def analyze_matches(self):
        counter = 0
        output = {}
        types = set(match['type_value'] for match in self.matches)
        for type_value in types:
            type_matches = [match for match in self.matches if match['type_value'] == type_value]
            sorted_matches = sorted(type_matches, key=lambda x: x['odds_home'])
            sorted_matches_away = sorted(type_matches, key=lambda x: x['odds_away'])
            for match in sorted_matches:
                small_odds = sorted_matches[counter]
                medium_odds = sorted_matches[len(sorted_matches) // 2]
                high_odds = sorted_matches[-(counter+1)]
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


                if self.unique:
                    if not self.is_cached(output):
                        break  # If output is unique, break the loop
                    else:
                        counter += 1 
                        output = {}  # Clear the output if not unique
            if self.unique:
                if not self.is_cached(output):
                    self.cache_output(output)  # Cache the output if unique
                else:
                    continue  # If not unique, continue to the next type value
            else:
                self.cache_output(output)  # Cache the output if not unique
        return output

def main():
    unique = True
    analyzer = BasketballMatchAnalyzer("basketball", unique=unique)
    analyzer.load_data()
    analysis_result = analyzer.analyze_matches()
    print(json.dumps(analysis_result, indent=4))

if __name__ == "__main__":
    main()