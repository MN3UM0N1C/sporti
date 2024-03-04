

from bs4 import BeautifulSoup
import os
import json
import random
from datetime import datetime, timedelta

class BasketballMatchAnalyzer:
    def __init__(self, sport, unique=False, cache_file='cache.json', days=1000):
        self.days = days
        self.sport = sport
        self.xml_folder = f'app/odds/{sport}'
        self.matches = []
        self.unique = unique
        self.cache_file = cache_file

    def load_data(self):
        today = datetime.today().date()
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
                    match_date_str = match.get("formatted_date")
                    match_date = datetime.strptime(match_date_str, "%d.%m.%Y").date()
                    print(match_date) 
                    if today - match_date <= timedelta(days=int(self.days)):
                        print("tre") 
                        type_elements = match.find_all('type')
                        for type_element in type_elements:
                            try:
                                match_data = {
                                    "type_value": type_element['value'],
                                    "local_team": match.find('localteam')['name'],
                                    "away_team": match.find(versus_team)['name'],
                                    "odds_home": float(type_element.find('odd', {'name': 'Home'})['value']),
                                    "odds_away": float(type_element.find('odd', {'name': 'Away'})['value'])
                                }
                            except:
                                pass
                            self.matches.append(match_data)
                    else:
                        print("sasd")

    def is_cached(self, output):
        if not os.path.exists(self.cache_file):
            # If the file doesn't exist, create it
            with open(self.cache_file, 'w') as f:
                json.dump([], f)  # Write an empty JSON object to the file
            return False
        
        # Check if the file is not empty
        if os.stat(self.cache_file).st_size > 2:
            with open(self.cache_file, 'r') as f:
                cached_data = json.load(f)
                return output in cached_data
        else:
            return False  # Return False if file is empty

    def cache_output(self, output):
        if output == {}:
            pass
        else:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    cached_data = json.load(f)
            else:
                cached_data = []
            cached_data.append(output)
            with open(self.cache_file, 'w') as f:
                json.dump(cached_data, f)

    def random_from_cache(self):
        if os.path.exists(self.cache_file):
            if os.stat(self.cache_file).st_size > 2:
                with open(self.cache_file, 'r') as f:
                    cached_data = json.load(f)
                    return random.choice(cached_data)
            else:
                return False  # Return False if file is empty


    def analyze_matches(self):
        counter = 0
        output = {}
        types = set(match['type_value'] for match in self.matches)
        for type_value in types:
            type_matches = [match for match in self.matches if match['type_value'] == type_value]
            sorted_matches = sorted(type_matches, key=lambda x: x['odds_home'])
            small_odds = sorted_matches[:5]
            medium_odds = sorted_matches[len(sorted_matches) // 5:2 * (len(sorted_matches) // 5)]
            high_odds = sorted_matches[-5:]
            output[type_value] = {
                "small_odds": [
                    {
                        "local_team_name": small["local_team"],
                        "away_team_name": small["away_team"],
                        "odds": min(small["odds_home"], small["odds_away"])
                    } for small in small_odds
                ],
                "medium_odds": [
                    {
                        "local_team_name": medium["local_team"],
                        "away_team_name": medium["away_team"],
                        "odds": (medium["odds_home"] + medium["odds_away"]) / 2
                    } for medium in medium_odds[:5]  # Take only 3 medium matches
                ],
                "high_odds": [
                    {
                        "local_team_name": high["local_team"],
                        "away_team_name": high["away_team"],
                        "odds": max(high["odds_home"], high["odds_away"])
                    } for high in high_odds
                ]
            }

            if self.unique:
                if not self.is_cached(output):
                    self.cache_output(output)
                    return output  # If output is unique, break the loop
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
        if output == {}:
            print("try")
            return self.random_from_cache()
        return output

def main():
    unique = True
    analyzer = BasketballMatchAnalyzer("football", unique=unique, 15)
    analyzer.load_data()
    analysis_result = analyzer.analyze_matches()
    print(json.dumps(analysis_result, indent=4))

if __name__ == "__main__":
    main()