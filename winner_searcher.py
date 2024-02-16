import os
import json
import subprocess
from bs4 import BeautifulSoup

class FootballMatchAnalyzer:
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

    def download_xml_file(self, url, file_path):
        try:
            # Create directories if they don't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            # Use subprocess to call curl command to download the XML file
            result = subprocess.run(["curl", "-s", "-o", file_path, url], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"XML file downloaded successfully: {file_path}")
                return True
            else:
                print(f"Error downloading XML file from {url}: {result.stderr}")
                return False
        except subprocess.CalledProcessError as e:
            print(f"Error downloading XML file from {url}: {e}")
            return False

    def download_all_leagues(self, base_url, output_dir):
        for league_id, league_name in self.league_id_mapping.items():
            url = f"{base_url}/leagueid/{league_id}"
            file_path = os.path.join(output_dir, f"{league_name.replace(' ', '_')}.xml")
            self.download_xml_file(url, file_path)

    def load_xml_file(self, file_path):
        try:
            with open(file_path, "r") as file:
                return file.read()
        except FileNotFoundError:
            print(f"File {file_path} not found.")
            return None

    def find_winner(self, team1, team2, league_name=None):
        match_results = []

        # If league_name is not provided, iterate through all downloaded files
        if league_name is None:
            for file_name in os.listdir("winner/football"):
                file_path = os.path.join("winner/football", file_name)
                if file_path.endswith(".xml"):
                    xml_data = self.load_xml_file(file_path)
                    if xml_data:
                        soup = BeautifulSoup(xml_data, "xml")
                        matches = self.extract_matches(soup, team1, team2, file_name)
                        if matches:
                            match_results.extend(matches)
        else:
            league_id = [k for k, v in self.league_id_mapping.items() if v == league_name.replace('_', ' ')][0]
            file_name = f"{league_name.replace('_', ' ')}.xml"
            file_path = os.path.join("winner/football", file_name)
            if os.path.exists(file_path):
                xml_data = self.load_xml_file(file_path)
                if xml_data:
                    soup = BeautifulSoup(xml_data, "xml")
                    match_results.extend(self.extract_matches(soup, team1, team2, file_name))

        return match_results

    def extract_matches(self, soup, team1, team2, league_name):
        match_results = []

        last_four_weeks = soup.find_all("week")[:4]

        for week in last_four_weeks:
            matches = week.find_all("match")
            for match in matches:
                local_team = match.find("localteam").get("name")
                visitor_team = match.find("visitorteam").get("name")
                local_score = match.find("localteam").get("score")
                visitor_score = match.find("visitorteam").get("score")

                if (local_team == team1 and visitor_team == team2) or (local_team == team2 and visitor_team == team1):
                    match_results.append({
                        "League": league_name.replace('.xml', ''),
                        "Local Team": local_team,
                        "Visitor Team": visitor_team,
                        "Local Score": local_score,
                        "Visitor Score": visitor_score,
                        "Winner": team1 if local_score > visitor_score else team2 if visitor_score > local_score else "Draw"
                    })

        return match_results


from datetime import datetime, timedelta

class BaketballMatchAnalyzer():
    def __init__(self):
        self.league_id_mapping = {"1046": 'nba', "1278": 'euro_league', "1291": 'euro_cup', "2691": 'ncaa'}

    def download_xml_file(self, url, file_path):
        try:
            # Create directories if they don't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            # Use subprocess to call curl command to download the XML file
            result = subprocess.run(["curl", "-s", "-o", file_path, url], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"XML file downloaded successfully: {file_path}")
                return True
            else:
                print(f"Error downloading XML file from {url}: {result.stderr}")
                return False
        except subprocess.CalledProcessError as e:
            print(f"Error downloading XML file from {url}: {e}")
            return False

    def download_all_leagues(self, base_url, output_dir):
        for league_id, league_name in self.league_id_mapping.items():
            url = f"{base_url}/{league_id}"
            file_path = os.path.join(output_dir, f"{league_name.replace(' ', '_')}.xml")
            self.download_xml_file(url, file_path)

    def load_xml_file(self, file_path):
        try:
            with open(file_path, "r") as file:
                return file.read()
        except FileNotFoundError:
            print(f"File {file_path} not found.")
            return None

    def find_winner(self, team1, team2, league_name=None):
        match_results = []

        # If league_name is not provided, iterate through all downloaded files
        if league_name is None:
            for file_name in os.listdir("winner/basketball"):
                file_path = os.path.join("winner/basketball", file_name)
                if file_path.endswith(".xml"):
                    xml_data = self.load_xml_file(file_path)
                    if xml_data:
                        soup = BeautifulSoup(xml_data, "xml")
                        matches = self.extract_matches(soup, team1, team2, file_name)
                        if matches:
                            match_results.extend(matches)
        else:
            league_id = [k for k, v in self.league_id_mapping.items() if v == league_name.replace('_', ' ')][0]
            file_name = f"{league_name.replace('_', ' ')}.xml"
            file_path = os.path.join("winner/basketball", file_name)
            if os.path.exists(file_path):
                xml_data = self.load_xml_file(file_path)
                if xml_data:
                    soup = BeautifulSoup(xml_data, "xml")
                    match_results.extend(self.extract_matches(soup, team1, team2, file_name))

        return match_results

    def extract_matches(self, soup, team1, team2, league_name):
        match_results = []
        today = datetime.today().date()

        for match in soup.find_all("match"):
            match_date_str = match.get("date")
            match_date = datetime.strptime(match_date_str, "%d.%m.%Y").date()
            if today - match_date <= timedelta(days=30): 
                local_team = match.find("localteam").get("name")
                visitor_team = match.find("awayteam").get("name")
                local_score = match.find("localteam").get("totalscore")
                visitor_score = match.find("awayteam").get("totalscore")
                if (local_team == team1 and visitor_team == team2) or (local_team == team2 and visitor_team == team1):
	                match_results.append({
	                    "League": league_name.replace('.xml', ''),
	                    "Local Team": local_team,
	                    "Visitor Team": visitor_team,
	                    "Local Score": local_score,
	                    "Visitor Score": visitor_score,
	                    "Winner": team1 if local_score > visitor_score else team2 if visitor_score > local_score else "Draw"
	                })

        return match_results
class MMAMatchAnalyzer():
    def __init__(self):
        self.league_id_mapping = {"1046": 'nba', "1278": 'euro_league', "1291": 'euro_cup', "2691": 'ncaa'}

    def download_xml_file(self, url, file_path):
        try:
            # Create directories if they don't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            # Use subprocess to call curl command to download the XML file
            result = subprocess.run(["curl", "-s", "-o", file_path, url], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"XML file downloaded successfully: {file_path}")
                return True
            else:
                print(f"Error downloading XML file from {url}: {result.stderr}")
                return False
        except subprocess.CalledProcessError as e:
            print(f"Error downloading XML file from {url}: {e}")
            return False

    def download_all_leagues(self, base_url, output_dir):
            self.download_xml_file(base_url, f'{output_dir}/mma.xml')

    def load_xml_file(self, file_path):
        try:
            with open(file_path, "r") as file:
                return file.read()
        except FileNotFoundError:
            print(f"File {file_path} not found.")
            return None

    def find_winner(self, team1, team2, league_name=None):
        match_results = []

        # If league_name is not provided, iterate through all downloaded files
        if league_name is None:
            for file_name in os.listdir("winner/mma"):
                file_path = os.path.join("winner/mma", file_name)
                if file_path.endswith(".xml"):
                    xml_data = self.load_xml_file(file_path)
                    if xml_data:
                        soup = BeautifulSoup(xml_data, "xml")
                        matches = self.extract_matches(soup, team1, team2, file_name)
                        if matches:
                            match_results.extend(matches)
        else:
            league_id = [k for k, v in self.league_id_mapping.items() if v == league_name.replace('_', ' ')][0]
            file_name = f"{league_name.replace('_', ' ')}.xml"
            file_path = os.path.join("winner/mma", file_name)
            if os.path.exists(file_path):
                xml_data = self.load_xml_file(file_path)
                if xml_data:
                    soup = BeautifulSoup(xml_data, "xml")
                    match_results.extend(self.extract_matches(soup, team1, team2, file_name))

        return match_results

    def extract_matches(self, soup, team1, team2, league_name):
        match_results = []
        today = datetime.today().date()

        for match in soup.find_all("match"):
            match_date_str = match.get("date")
            match_date = datetime.strptime(match_date_str, "%d.%m.%Y").date()
            if today - match_date <= timedelta(days=60): 
                local_team = match.find("localteam").get("name")
                visitor_team = match.find("awayteam").get("name")
                local_score = match.find("localteam").get("winner")
                visitor_score = match.find("awayteam").get("winner")
                if (local_team == team1 and visitor_team == team2) or (local_team == team2 and visitor_team == team1):
                    match_results.append({
                        "League": league_name.replace('.xml', ''),
                        "Local Team": local_team,
                        "Visitor Team": visitor_team,
                        "Local Winner": local_score,
                        "Visitor Winner": visitor_score,
                        "Winner": team1 if local_score > visitor_score else team2 if visitor_score > local_score else "Draw"
                    })

        return match_results

# Example usage:
analyzer = BaketballMatchAnalyzer()
base_url = "https://www.goalserve.com/getfeed/401117231212497fb27a08db8de47c17/mma/live"
output_dir = "winner/mma"
analyzer.download_all_leagues(base_url, output_dir)
matches = analyzer.find_winner("Timmy Cuamba", "Bolaji Oki")
for match in matches:
    print(json.dumps(match, indent=4))

# Example usage:
analyzer = BaketballMatchAnalyzer()
base_url = "https://www.goalserve.com/getfeed/401117231212497fb27a08db8de47c17/bsktbl"
output_dir = "winner/basketball"
# analyzer.download_all_leagues(base_url, output_dir)
matches = analyzer.find_winner("Oklahoma City Thunder", "San Antonio Spurs")
for match in matches:
    print(json.dumps(match, indent=4))

analyzer = FootballMatchAnalyzer()
base_url = "https://www.goalserve.com/getfeed/401117231212497fb27a08db8de47c17/bsktbl"
output_dir = "winner/football"
# analyzer.download_all_leagues(base_url, output_dir)
matches = analyzer.find_winner()
for match in matches:
    print(json.dumps(match, indent=4))
