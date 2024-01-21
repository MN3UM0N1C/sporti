from bs4 import BeautifulSoup
import json
import requests
import subprocess
from itertools import product


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
        try:
            with open(f'data/{self.league_id_mapping[league_id]}.xml', 'r') as file:
                xml_content = file.read()
                return BeautifulSoup(xml_content, 'xml')
        except FileNotFoundError:
            print(f"Error: File not found for league ID {league_id}. Make sure to download the file first.")

    def search(self, league_id, match, casino=None):
        result = []
        try:
            soup = self.load_data(league_id)
            for k in soup.find_all("match", {"id": match}):
                if casino is not None:
                    result = k.find_all('bookmaker', {'name': casino})
                else:
                    result = k.find_all('bookmaker')
            return result
        except AttributeError:
            print("Error: Data structure is not as expected. Check if the XML file has the correct structure.")

    def is_match(self, team_name, match_name):
        team_words = team_name.lower().split()
        match_words = match_name.lower().split()
        return any(word in match_words for word in team_words)        

    def team(self, league_id, teams, casino=None):
        soup = self.load_data(league_id)
        matches = soup.find_all("match")
        for match in matches:
            local_team = match.find("localteam").get("name")
            visitor_team = match.find("visitorteam").get("name")
            if self.is_match(teams[0], local_team) and self.is_match(teams[1], visitor_team):
                return self.search(league_id, match.get("id"), casino=casino)

    def koef(self, file):
        try:
            data = [(k.get('name'), k.get('value')) for i in file for k in i.find_all('odd')]
            return json.dumps(dict(data))
        except (TypeError, AttributeError):
            print("Coefficients not found.")

    def download_all_files(self):
        for league_id, league_name in self.league_id_mapping.items():
            self.download_file(league_id, f"{league_name}.xml")
    def parse_all_matches(self):
        all_matches_data = []
        for league_id, league_name in self.league_id_mapping.items():
            try:
                soup = self.load_data(league_id)
                matches = soup.find_all("match")
                for match in matches:
                    match_data = {
                        "league": league_name,
                        "match_id": match.get("id"),
                        "local_team": match.find("localteam").get("name"),
                        "visitor_team": match.find("visitorteam").get("name"),
                        "odds": []
                    }
                    for bookmaker in match.find_all('bookmaker'):
                        bookmaker_name = bookmaker.get('name')
                        odds = [(odd.get('name'), odd.get('value')) for odd in bookmaker.find_all('odd')]
                        match_data["odds"].append({"bookmaker": bookmaker_name, "odds": dict(odds)})
                    all_matches_data.append(match_data)
            except Exception as e:
                print(f"An error occurred while parsing matches for league {league_name}: {e}")
        return json.dumps(all_matches_data, indent=2)


class BasketballDataParser:
    def __init__(self, league_id_mapping):
        self.league_id_mapping = league_id_mapping
        self.base_url = "http://www.goalserve.com/getfeed/401117231212497fb27a08db8de47c17/getodds/soccer?cat=basket_10&League="

    def download_file(self, league_id, output_file):
        try:
            url = f"{self.base_url}{league_id}"
            subprocess.run(['curl', '-o', f"data/basketball/{output_file}", url], check=True)
            print(f"File downloaded successfully: {output_file}")
        except subprocess.CalledProcessError as e:
            print(f"Error downloading file: {e}")

    def load_data(self, league_id):
        try:
            with open(f'data/basketball/{self.league_id_mapping[league_id]}.xml', 'r') as file:
                xml_content = file.read()
                return BeautifulSoup(xml_content, 'xml')
        except FileNotFoundError:
            print(f"Error: File not found for league ID {league_id}. Make sure to download the file first.")

    def search(self, league_id, match, casino=None):
        result = []
        try:
            soup = self.load_data(league_id)
            for k in soup.find_all("match", {"id": match}):
                if casino is not None:
                    result = k.find_all('bookmaker', {'name': casino})
                else:
                    result = k.find_all('bookmaker')
            return result
        except AttributeError:
            print("Error: Data structure is not as expected. Check if the XML file has the correct structure.")
    def is_match(self, team_name, match_name):
        team_words = team_name.lower().split()
        match_words = match_name.lower().split()
        return any(word in match_words for word in team_words)        


    def team(self, league_id, teams, casino=None):
        soup = self.load_data(league_id)
        matches = soup.find_all("match")
        for match in matches:
            local_team = match.find("localteam").get("name")
            visitor_team = match.find("awayteam").get("name")
            if self.is_match(teams[0], local_team) and self.is_match(teams[1], visitor_team):
                return self.search(league_id, match.get("id"), casino=casino)


    def koef(self, file):
        try:
            data = [(k.get('name'), k.get('value')) for i in file for k in i.find_all('odd')]
            return json.dumps(dict(data))
        except (TypeError, AttributeError):
            print("Coefficients not found.")

    def download_all_files(self):
        for league_id, league_name in self.league_id_mapping.items():
            self.download_file(league_id, f"{league_name}.xml")
    def parse_all_matches(self):
        all_matches_data = []
        for league_id, league_name in self.league_id_mapping.items():
            try:
                soup = self.load_data(league_id)
                matches = soup.find_all("match")
                for match in matches:
                    match_data = {
                        "league": league_name,
                        "match_id": match.get("id"),
                        "local_team": match.find("localteam").get("name"),
                        "visitor_team": match.find("awayteam").get("name"),
                        "odds": []
                    }
                    for bookmaker in match.find_all('bookmaker'):
                        bookmaker_name = bookmaker.get('name')
                        odds = [(odd.get('name'), odd.get('value')) for odd in bookmaker.find_all('odd')]
                        match_data["odds"].append({"bookmaker": bookmaker_name, "odds": dict(odds)})
                    all_matches_data.append(match_data)
            except Exception as e:
                print(f"An error occurred while parsing matches for league {league_name}: {e}")
        return json.dumps(all_matches_data, indent=2)

class TennisDataScraper:
    def __init__(self):
        self.base_url = "http://www.goalserve.com/getfeed/401117231212497fb27a08db8de47c17/getodds/soccer?cat=tennis_10"
    def download_file(self, output_file):
        try:
            url = self.base_url
            subprocess.run(['curl', '-o', f"data/tennis/{output_file}", url], check=True)
            print(f"File downloaded successfully: {output_file}")
        except subprocess.CalledProcessError as e:
            print(f"Error downloading file: {e}")

    def load_data(self):
        try:
            with open(f'data/tennis/tennis.xml', 'r') as file:
                xml_content = file.read()
                return BeautifulSoup(xml_content, 'xml')
        except FileNotFoundError:
            print(f"Error: File not found for league ID . Make sure to download the file first.")

    def search(self, match, casino=None):
        result = []
        try:
            soup = self.load_data()
            for k in soup.find_all("match", {"id": match}):
                if casino is not None:
                    result = k.find_all('bookmaker', {'name': casino})
                else:
                    result = k.find_all('bookmaker')
            return result
        except AttributeError:
            print("Error: Data structure is not as expected. Check if the XML file has the correct structure.")

    def is_match(self, team_name, match_name):
        team_words = team_name.lower().split()
        match_words = match_name.lower().split()
        return any(word in match_words for word in team_words)        

    def team(self, teams, casino=None):
        soup = self.load_data()
        matches = soup.find_all("match")
        for match in matches:
            local_team = match.find_all("player")
            if self.is_match(teams[0], local_team[0].get("name")) and self.is_match(teams[1], local_team[1].get("name")):
                return self.search(match.get("id"), casino=casino)

    def koef(self, file):
        try:
            data = [(k.get('name'), k.get('value')) for i in file for k in i.find_all('odd')]
            return json.dumps(dict(data))
        except (TypeError, AttributeError):

            print("Coefficients not found.")

    def download_all_files(self):
        self.download_file("tennis.xml")

    def parse_all_matches(self):
        all_matches_data = []
        try:
            soup = self.load_data()
            matches = soup.find_all("match")
            for match in matches:
                match_data = {
                    "match_id": match.get("id"),
                    "players": [player.get("name") for player in match.find_all("player")],
                    "odds": []
                }
                for bookmaker in match.find_all('bookmaker'):
                    bookmaker_name = bookmaker.get('name')
                    odds = [(odd.get('name'), odd.get('value')) for odd in bookmaker.find_all('odd')]
                    match_data["odds"].append({"bookmaker": bookmaker_name, "odds": dict(odds)})
                all_matches_data.append(match_data)
        except Exception as e:
            print(f"An error occurred while parsing tennis matches: {e}")
        return json.dumps(all_matches_data, indent=2)

class MMADataParser:
    def __init__(self):
        self.base_url = "http://www.goalserve.com/getfeed/401117231212497fb27a08db8de47c17/getodds/soccer?cat=mma_10"
    def download_file(self, output_file):
        try:
            url = self.base_url
            subprocess.run(['curl', '-o', f"data/mma/{output_file}", url], check=True)
            print(f"File downloaded successfully: {output_file}")
        except subprocess.CalledProcessError as e:
            print(f"Error downloading file: {e}")

    def load_data(self):
        try:
            with open(f'data/mma/mma.xml', 'r') as file:
                xml_content = file.read()
                return BeautifulSoup(xml_content, 'xml')
        except FileNotFoundError:
            print(f"Error: File not found for league ID . Make sure to download the file first.")

    def search(self, match, casino=None):
        result = []
        try:
            soup = self.load_data()
            for k in soup.find_all("match", {"id": match}):
                if casino is not None:
                    result = k.find_all('bookmaker', {'name': casino})
                else:
                    result = k.find_all('bookmaker')
            return result
        except AttributeError:
            print("Error: Data structure is not as expected. Check if the XML file has the correct structure.")

    def is_match(self, team_name, match_name):
        team_words = team_name.lower().split()
        match_words = match_name.lower().split()
        return any(word in match_words for word in team_words)        

    def team(self, teams, casino=None):
        soup = self.load_data()
        matches = soup.find_all("match")
        for match in matches:
            local_team = match.find("localteam")
            away_team = match.find("awayteam")
            if self.is_match(teams[0], local_team.get("name")) and self.is_match(teams[1], away_team.get("name")):
                return self.search(match.get("id"), casino=casino)

    def koef(self, file):
        try:
            data = [(k.get('name'), k.get('value')) for i in file for k in i.find_all('odd')]
            return json.dumps(dict(data))
        except (TypeError, AttributeError):

            print("Coefficients not found.")

    def download_all_files(self):
        self.download_file("mma.xml")

    def parse_all_matches(self):
        all_matches_data = []
        try:
            soup = self.load_data()
            matches = soup.find_all("match")
            for match in matches:
                match_data = {
                    "match_id": match.get("id"),
                    "local_team": match.find("localteam").get("name"),
                    "away_team": match.find("awayteam").get("name"),
                    "odds": []
                }
                for bookmaker in match.find_all('bookmaker'):
                    bookmaker_name = bookmaker.get('name')
                    odds = [(odd.get('name'), odd.get('value')) for odd in bookmaker.find_all('odd')]
                    match_data["odds"].append({"bookmaker": bookmaker_name, "odds": dict(odds)})
                all_matches_data.append(match_data)
        except Exception as e:
            print(f"An error occurred while parsing MMA matches: {e}")
        return json.dumps(all_matches_data, indent=2)




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
    baskeball_id_mapping = {"1046": 'NBA', "1278": 'Euroleague', "1291": 'Eurocup', "2691": 'NCAA'}
    football_parser = FootballDataParser(league_id_mapping)
    basketball_parser = BasketballDataParser(baskeball_id_mapping)
    tennis_parser = TennisDataScraper()
    mma_parser = MMADataParser()    
    #tennis_parser.download_all_files()
    try:
        result = mma_parser.parse_all_matches()
        #result = football_parser.koef(football_parser.team("1007", ['Bayer Leverkusen', 'Molde'], casino="bwin"))
        #result = basketball_parser.koef(basketball_parser.team("1291", ["Cedevita Olimpija", "Venezia"], casino="Marathon"))
        #result = tennis_parser.koef(tennis_parser.team(["F. Auger-Aliassime", "D. Thiem"], casino="bwin"))
        #result = mma_parser.koef(mma_parser.team(["Sam Patterson", "Yohan Lainesse"], casino="bwin"))
        print(result)
    except Exception as e:     
        print(f"An error occurred: {e}")
