from bs4 import BeautifulSoup
import os
import json
import random
from datetime import datetime, timedelta
import re
import mysql.connector
import copy

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
            query = "SELECT fighter_1, fighter_2, prediction_team FROM prediction WHERE id > %s"
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
                        type_elements = []
                        for types in match.find_all('type'):
                            if types["value"] == "Home/Away":
                                type_elements.append(types)
                        localteam_name = match.find("localteam")["name"]
                        awayteam_name = match.find(versus_team)["name"]
                        for type_element in type_elements:
                            for pair in names:  
                                if localteam_name == pair[0] or localteam_name == pair[1] and awayteam_name == pair[1] or  awayteam_name == pair[0]:
                                    if pair[2] == "team1":
                                        predicted_team = localteam_name
                                    else:
                                        predicted_team = awayteam_name
                                    match_data = {
                                        "type_value": type_element['value'],
                                        "local_team": match.find('localteam')['name'],
                                        "away_team": match.find(versus_team)['name'],
                                        "odds_home": float(type_element.find('odd', {'name': 'Home'})['value']),
                                        "odds_away": float(type_element.find('odd', {'name': 'Away'})['value']),
                                        "date" : match_date_str,
                                        "prediction_team" : predicted_team
                                    }
                                    self.matches.append(match_data)
        seen = set()
        uniq_list_of_dicts = []
        for d in self.matches:
            # Convert each dictionary to a hashable type (e.g., tuple of sorted items) to check for uniqueness
            hashable_d = tuple(sorted(d.items()))
            if hashable_d not in seen:
                uniq_list_of_dicts.append(d)
                seen.add(hashable_d)
        self.matches = uniq_list_of_dicts

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
        good_out = {}
        counter = 0
        output = {}
        types = set(match['type_value'] for match in self.matches)
        for type_value in types:
            type_matches = [match for match in self.matches if match['type_value'] == type_value]

            # Sort home_type_matches based on 'odds_home'
            home_sorted_matches = sorted(type_matches, key=lambda x: x['odds_home'])                

            # Determine the length of each part
            part_length = len(home_sorted_matches) // 3

            # Ensure the length of home_sorted_matches is divisible by 3
            if len(home_sorted_matches) % 3 != 0:
                home_sorted_matches.pop()

            # Split home_sorted_matches into three parts based on length
            home_small_odds = home_sorted_matches[:part_length]
            home_medium_odds = home_sorted_matches[part_length:2*part_length]
            home_high_odds = home_sorted_matches[2*part_length:]

            # Sort away_type_matches based on 'odds_away'
            away_sorted_matches = sorted(type_matches, key=lambda x: x['odds_away'])

            # Determine the length of each part for away_sorted_matches
            part_length = len(away_sorted_matches) // 3

            # Ensure the length of away_sorted_matches is divisible by 3
            if len(away_sorted_matches) % 3 != 0:
                away_sorted_matches.pop()


            # Split away_sorted_matches into three parts based on length
            away_small_odds = away_sorted_matches[:part_length]
            away_medium_odds = away_sorted_matches[part_length:2*part_length]
            away_high_odds = away_sorted_matches[2*part_length:]

            seen_matches = set()  # To keep track of seen matches 
            output[type_value] = {
                "small_odds": [
                    {
                        "local_team_name": small_home["local_team"] if small_home["prediction_team"] == small_home["local_team"] else small_away["local_team"],
                        "away_team_name": small_home["away_team"] if small_home["prediction_team"] == small_home["local_team"] else small_away["away_team"],
                        "odds": {"predicted_odd" : small_home["odds_home"] if small_home["prediction_team"] == small_home["local_team"] else small_away["odds_away"], "home_odds": small_home["odds_home"], "away_odds": small_away["odds_away"]},
                        "winner" : small_home["prediction_team"] if small_home["prediction_team"] == small_home["local_team"] else small_away["prediction_team"],
                        "date": small_home["date"] if small_home["prediction_team"] == small_home["local_team"] else small_away["date"]
                    } for small_home, small_away in zip(home_small_odds, away_small_odds)
                    if (small_home["local_team"], small_home["away_team"]) not in seen_matches and not seen_matches.add((small_home["local_team"], small_home["away_team"]))
                ],
                "medium_odds": [
                    {
                        "local_team_name": medium_home["local_team"] if medium_home["prediction_team"] == medium_home["local_team"] else medium_away["local_team"],
                        "away_team_name": medium_home["away_team"] if medium_home["prediction_team"] == medium_home["local_team"] else medium_away["away_team"],
                        "odds": {"predicted_odd" : medium_home["odds_home"] if medium_home["prediction_team"] == medium_home["local_team"] else medium_away["odds_away"], "home_odds": medium_home["odds_home"], "away_odds": medium_away["odds_away"]},
                        "winner" : medium_home["prediction_team"] if medium_home["prediction_team"] == medium_home["local_team"] else medium_away["prediction_team"],
                        "date": medium_home["date"] if medium_home["prediction_team"] == medium_home["local_team"] else medium_away["date"]
                    } for medium_home, medium_away in zip(home_medium_odds, away_medium_odds)
                    if (medium_home["local_team"], medium_home["away_team"]) not in seen_matches and not seen_matches.add((medium_home["local_team"], medium_home["away_team"]))
                ],
                "high_odds": [
                    {
                        "local_team_name": high_home["local_team"] if high_home["prediction_team"] == high_home["local_team"] else high_away["local_team"],
                        "away_team_name": high_home["away_team"] if high_home["prediction_team"] == high_home["local_team"] else high_away["away_team"],
                        "odds": {"predicted_odd" : high_home["odds_home"] if high_home["prediction_team"] == high_home["local_team"] else high_away["odds_away"], "home_odds": high_home["odds_home"], "away_odds": high_away["odds_away"]},
                        "winner" : high_home["prediction_team"] if high_home["prediction_team"] == high_home["local_team"] else high_away["prediction_team"],
                        "date": high_home["date"] if high_home["prediction_team"] == high_home["local_team"] else high_away["date"]
                    } for high_home, high_away in zip(home_high_odds, away_high_odds)
                    if (high_home["local_team"], high_home["away_team"]) not in seen_matches and not seen_matches.add((high_home["local_team"], high_home["away_team"]))
                ]}
            output["Home/Away"]["small_odds"] = output["Home/Away"]["small_odds"][:12]
            output["Home/Away"]["medium_odds"] = output["Home/Away"]["medium_odds"][:12]
            output["Home/Away"]["high_odds"] = output["Home/Away"]["high_odds"][:12]

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
  # Cache the output if not unique

        if output == {}:
            return self.random_from_cache()

        return output



def main():
    good_out = {}
    unique = False
    analyzer = Odds_counter("football", unique=unique, days=90)
    analyzer.load_data()
    analysis_result = analyzer.analyze_matches()
    print(json.dumps(analysis_result, indent=4)) 



if __name__ == "__main__":
    main()