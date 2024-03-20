from bs4 import BeautifulSoup
import os
import json
import random
from datetime import datetime, timedelta
import re
import mysql.connector
import copy
import redis

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

            if self.sport.lower() == 'basketball':
                leagues = ['nba', 'ncaa']
            elif self.sport.lower() == 'football':
                leagues = ['uefa_europa_league', 'bundesliga', 'premier_league', 'la_liga', 'ligue_1', 'saudi_league', 'serie_a', 'uefa_champions_league']
            elif self.sport.lower() == 'mma':
                leagues = ['mma']
            else:
                leagues = ['tennis']

            num_placeholders = len(leagues)
            query = "SELECT fighter_1, fighter_2, prediction_team FROM prediction WHERE event_name IN ({})".format(', '.join(['%s'] * num_placeholders))
            cursor.execute(query, leagues)
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
                                        "odds_home": type_element.find('odd', {'name': 'Home'})['value'] if type_element.find('odd', {"name" : "Home"}) != None else "None", 
                                        "odds_away": type_element.find('odd', {'name': 'Away'})['value'],
                                        "date" : match_date_str,
                                        "prediction_team" : predicted_team
                                    }
                                    self.matches.append(match_data)
        unique_list = []
        seen = set()
        for d in self.matches:
            try:
                identifier = (d["local_team"], d["away_team"], d["date"])
            except:
                identifier = (d["local_team_name"], d["away_team_name"], d["date"])
            if identifier not in seen:
                seen.add(identifier)
                unique_list.append(d)
        self.matches = unique_list

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
            home_sorted_matches = sorted(type_matches, key=lambda x: float(x['odds_home']))           

            # Determine the length of each part
            part_length = len(home_sorted_matches) // 3

            # Ensure the length of home_sorted_matches is divisible by 3
            if len(home_sorted_matches) % 3 != 0:
                home_sorted_matches.pop()

            # Split home_sorted_matches into three parts based on length
            home_small_odds = home_sorted_matches[:part_length]
            home_medium_odds = home_sorted_matches[part_length:2*part_length]
            home_high_odds = home_sorted_matches[2*part_length:]
            home_high_odds.reverse()

            # Sort away_type_matches based on 'odds_away'
            away_sorted_matches = sorted(type_matches, key=lambda x: float(x['odds_away']))

            # Determine the length of each part for away_sorted_matches
            part_length = len(away_sorted_matches) // 3

            # Ensure the length of away_sorted_matches is divisible by 3
            if len(away_sorted_matches) % 3 != 0:
                away_sorted_matches.pop()


            # Split away_sorted_matches into three parts based on length
            away_small_odds = away_sorted_matches[:part_length]
            away_medium_odds = away_sorted_matches[part_length:2*part_length]
            away_high_odds = away_sorted_matches[2*part_length:]
            print(home_high_odds)
            seen_matches = set()  # To keep track of seen matches 
            output[type_value] = {
                "small_odds": [
                    {
                        "local_team_name": small_home["local_team"],# if small_home["prediction_team"] == small_home["local_team"] else small_away["local_team"],
                        "away_team_name": small_home["away_team"], #if small_home["prediction_team"] == small_home["local_team"] else small_away["away_team"],
                        "odds": {"predicted_odd" : small_home["odds_away"] if small_home["prediction_team"] == small_away["local_team"] else small_home["odds_home"], "home_odds": small_home["odds_home"], "away_odds": small_home["odds_away"]},
                        "winner" : small_home["local_team"] if small_home["prediction_team"] == small_home["local_team"] else small_home["away_team"],
                        "date": small_home["date"], #if small_home["prediction_team"] == small_home["local_team"] else sma["date"],
                        "sport" : self.sport
                    } for small_home, small_away in zip(home_small_odds, away_small_odds)
                    if (small_home["local_team"], small_home["away_team"]) not in seen_matches and not seen_matches.add((small_home["local_team"], small_home["away_team"]))
                ],
                "medium_odds": [
                    {
                        "local_team_name": medium_home["local_team"],# if medium_home["prediction_team"] == medium_home["local_team"] else medium_away["local_team"],
                        "away_team_name": medium_home["away_team"],# if medium_home["prediction_team"] == medium_home["local_team"] else medium_away["away_team"],
                        "odds": {"predicted_odd" : medium_home["odds_away"] if medium_home["prediction_team"] == medium_home["local_team"] else medium_home["odds_home"], "home_odds": medium_home["odds_home"], "away_odds": medium_home["odds_away"]},
                        "winner" : medium_home["local_team"] if medium_home["prediction_team"] == medium_home["local_team"] else medium_home["away_team"],
                        "date": medium_home["date"],# if medium_home["prediction_team"] == medium_home["local_team"] else medium_away["date"],
                        "sport" : self.sport
                    } for medium_home, medium_away in zip(home_medium_odds, away_medium_odds)
                    if (medium_home["local_team"], medium_home["away_team"]) not in seen_matches and not seen_matches.add((medium_home["local_team"], medium_home["away_team"]))
                ],
                "high_odds": [
                    {
                        "local_team_name": high_home["local_team"],# if high_home["prediction_team"] == high_home["local_team"] else high_away["local_team"],
                        "away_team_name": high_home["away_team"], #if high_home["prediction_team"] == high_home["local_team"] else high_away["away_team"],
                        "odds": {"predicted_odd" : high_home["odds_home"] if high_home["prediction_team"] == high_home["local_team"] else high_home["odds_away"], "home_odds": high_home["odds_home"], "away_odds": high_home["odds_away"]},
                        "winner" : high_home["local_team"] if high_home["prediction_team"] == high_home["local_team"] else high_home["away_team"],
                        "date": high_home["date"],# if high_home["prediction_team"] == high_home["local_team"] else high_away["date"],
                        "sport" : self.sport
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

class Combiner:
    def __init__(self, days, unique):
        self.unique = False
        self.sports = ["football", "basketball", "mma"]
        self.days = days
        self.combined = None
        # self.redis_client = redis.Redis(host='localhost', port=6379, db=0)

    def combine(self):
        combined = {}
        cache_key = 'combine_bet_result'

        # cached_result = self.redis_client.get(cache_key)
        # if cached_result:
        #     return json.loads(cached_result)
            
        for sport in self.sports:
            analyzer = Odds_counter(sport, unique=self.unique, days=self.days)
            analyzer.load_data()
            result = analyzer.analyze_matches()
            for t in range(4):
                try:
                    if sport == "football":
                        for market, values in result.items():
                            if market in combined:
                                combined[market]["small_odds"].append(values["small_odds"][t])
                                combined[market]["medium_odds"].append(values["medium_odds"][t])
                                combined[market]["high_odds"].append(values["high_odds"][t])
                                break
                            else:
                                combined[market] = {"small_odds" : [values["small_odds"][t]], "medium_odds" : [values["medium_odds"][t]], "high_odds" : [values["high_odds"][t]]}
                                break
                    if sport == "basketball":
                        for market, values in result.items():
                            if market in combined:
                                combined[market]["small_odds"].append(values["small_odds"][t])
                                combined[market]["medium_odds"].append(values["medium_odds"][t])
                                combined[market]["high_odds"].append(values["high_odds"][t])
                                break
                            else:
                                combined[market] = {"small_odds" : [values["small_odds"][t]], "medium_odds" : [values["medium_odds"][t]], "high_odds" : [values["high_odds"][t]]}
                                break
                    if sport == "mma":
                        try:
                            for market, values in result.items():
                                if market in combined:
                                    combined[market]["small_odds"].append(values["small_odds"][t])
                                    combined[market]["medium_odds"].append(values["medium_odds"][t])
                                    combined[market]["high_odds"].append(values["high_odds"][t])
                                    break
                                else:
                                    combined[market] = {"small_odds" : [values["small_odds"][t]], "medium_odds" : [values["medium_odds"][t]], "high_odds" : [values["high_odds"][t]]}
                                    break
                        except:
                            pass
                except:
                    pass

        # self.redis_client.set(cache_key, json.dumps(combined), ex=10)

        self.combined = combined
        return combined

    def convert_to_dummy_bets(self, difficulty):
        dummy_bets = []
        one_interval = []
        # Group the small_odds by their sports
        sports_dict = {}
        try:
            for item in self.combined["Home/Away"][difficulty]:
                if item['sport'] not in sports_dict:
                    sports_dict[item['sport']] = []
                sports_dict[item['sport']].append(item)
        except:
            pass

        # Iterate over each sport and process the small_odds
        for sport, odds_list in sports_dict.items():
            # Initialize variables for each bet
            total_odds = 1.0
            matches = []

            # Iterate over each match in odds_list
            for odd_item in odds_list:
                # Extract relevant information
                team1 = odd_item['local_team_name']
                team2 = odd_item['away_team_name']
                winner_team = odd_item['winner']
                winner_odds = odd_item['odds']

                # Calculate total odds for the bet
                total_odds *= float(winner_odds['predicted_odd'])

                # Construct match data
                match = {
                    'team1': team1,
                    'team2': team2,
                    'winner': {
                        'team': winner_team,
                        'odds': winner_odds,
                    }
                }

                # Append match to matches list
                matches.append(match)

            # Calculate bet and payout
            bet = 100
            payout = bet * total_odds

            # Construct the bet object
            bet_object = {
                'total_odds': "{:.2f}".format(total_odds),
                'bet': str(bet),
                'payout': "{:.2f}".format(payout),
                'matches': matches
            }

            # Append bet object to dummy_bets list
            dummy_bets.append(bet_object)
        return dummy_bets

    def express_bet(self):
        cache_key = 'express_bet_result'

        # cached_result = self.redis_client.get(cache_key)
        # if cached_result:
        #     return json.loads(cached_result)
        
        final_express = {}
        for difficulty in ["small_odds", "medium_odds", "high_odds"]:
            final_express[difficulty] = self.convert_to_dummy_bets(difficulty)

        # self.redis_client.set(cache_key, json.dumps(final_express), ex=3600)

        return final_express

    def transform_odds_data(self, odds_data):
        difficulty_mapping = {
            'small_odds': 'Small - Low risk',
            'medium_odds': 'Medium - Medium risk',
            'high_odds': 'High - High risk'
        }

        transformed_data = []

        for difficulty_key, bets in odds_data.items():
            for bet in bets:
                transformed_bet = {
                    'difficulty': difficulty_mapping[difficulty_key],
                    'data': {
                        'total_odds': bet['total_odds'],
                        'bet': bet['bet'],
                        'payout': bet['payout'],
                        'matches': bet['matches']
                    }
                }
                transformed_data.append(transformed_bet)

        return transformed_data

def main():
    unique = False
    good_out = {}
    combiner = Combiner(90, unique)
    # combiner.combine()
    print(json.dumps(combiner.combine(), indent=4))
    print(json.dumps(combiner.express_bet(), indent=4))

if __name__ == "__main__":
    main()