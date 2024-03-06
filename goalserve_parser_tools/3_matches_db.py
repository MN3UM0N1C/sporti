from bs4 import BeautifulSoup
import os
import json
import random
from datetime import datetime, timedelta
import re
import mysql.connector

class Odds_counter:
    def __init__(self, sport, unique=False, cache_file='cache.json', days=1000, sql_file="prediction.sql"):
        self.days = days
        self.sport = sport
        self.xml_folder = f'app/odds/{sport}'
        self.matches = []
        self.sql_file = sql_file
        self.unique = unique
        self.cache_file = cache_file
        self.db_connection = None

    def parse_sql_file(self):
        try:
            self.db_connection = mysql.connector.connect(
                host="localhost",
                user="kali",
                password="chatftw",
                database="chatftw_pred"
            )
            print("Connected to the database")

            matches = []
            cursor = self.db_connection.cursor()
            query = "SELECT fighter_1, fighter_2 FROM prediction WHERE id > %s"
            cursor.execute(query, (self.sport,))
            matches = cursor.fetchall()
            cursor.close()

            return matches

        except mysql.connector.Error as e:
            print("Error connecting to MySQL database:", e)
            return []

        finally:
            if self.db_connection:
                self.db_connection.close()
                print("Database connection closed.")


    def load_data(self):
        names = self.parse_sql_file()
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
                if self.sport == "mma" or self.sport == "basketball":
                    time_tag = "date"
                else:
                    time_tag = "formatted_date"
                for match in matches:
                    match_date_str = match.get(time_tag)
                    match_date = datetime.strptime(match_date_str, "%d.%m.%Y").date()
                    if today - match_date <= timedelta(days=int(self.days)):
                        type_elements = match.find_all('type')
                        localteam_name = match.find("localteam")["name"]
                        awayteam_name = match.find(versus_team)["name"]
                        for pair in names: 
                            if localteam_name == pair[0] or localteam_name == pair[1] and awayteam_name == pair[1] or  awayteam_name == pair[0]:
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
            home_sorted_matches = sorted(type_matches, key=lambda x: x['odds_away'])
            small_odds = sorted_matches[:5]
            medium_odds = sorted_matches[len(sorted_matches) // 5:2 * (len(sorted_matches) // 5)]
            high_odds = sorted_matches[-5:]
            seen_matches = set()  # To keep track of seen matches
            output[type_value] = {
                "small_odds": [
                    {
                        "local_team_name": small["local_team"],
                        "away_team_name": small["away_team"],
                        "odds": min(small["odds_home"], small["odds_away"])
                    } for small in small_odds if (small["local_team"], small["away_team"]) not in seen_matches and not seen_matches.add((small["local_team"], small["away_team"]))
                ],
                "medium_odds": [
                    {
                        "local_team_name": medium["local_team"],
                        "away_team_name": medium["away_team"],
                        "odds": "{:.2f}".format((medium["odds_home"] + medium["odds_away"]) / 2)
                    } for medium in medium_odds[:5] if (medium["local_team"], medium["away_team"]) not in seen_matches and not seen_matches.add((medium["local_team"], medium["away_team"]))
                ],
                "high_odds": [
                    {
                        "local_team_name": high["local_team"],
                        "away_team_name": high["away_team"],
                        "odds": max(high["odds_home"], high["odds_away"])
                    } for high in high_odds if (high["local_team"], high["away_team"]) not in seen_matches and not seen_matches.add((high["local_team"], high["away_team"]))
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
            return self.random_from_cache()

        return output



def main():
    unique = True
    analyzer = Odds_counter("football", unique=unique, days=90)
    analyzer.load_data()
    analysis_result = analyzer.analyze_matches()
    print(json.dumps(analysis_result, indent=4))

if __name__ == "__main__":
    main()