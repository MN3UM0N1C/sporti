import subprocess
import os
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

    def find_winner(self, team1, team2, league_name):
        if league_name not in self.league_id_mapping.values():
            print("Invalid league name.")
            return None
        
        file_name = f"{league_name.replace(' ', '_')}.xml"
        file_path = os.path.join("winner", "football", file_name)
        xml_data = self.load_xml_file(file_path)
        if not xml_data:
            print(f"No data available for {league_name}.")
            return None

        soup = BeautifulSoup(xml_data, "xml")

        team1_score = 0
        team2_score = 0
        
        for week in soup.find_all("week")[:4]:  # Iterate through the first 4 weeks
            matches = week.find_all("match")
            for match in matches:
                local_team = match.find("localteam").get("name")
                visitor_team = match.find("visitorteam").get("name")
                if (local_team == team1 and visitor_team == team2) or (local_team == team2 and visitor_team == team1):
                    local_score = int(match.find("localteam").get("score"))
                    visitor_score = int(match.find("visitorteam").get("score"))
                    if local_team == team1:
                        team1_score += local_score
                        team2_score += visitor_score
                    else:
                        team1_score += visitor_score
                        team2_score += local_score
        
        if team1_score > team2_score:
            return team1
        elif team2_score > team1_score:
            return team2
        else:
            return "It was a draw"

# Example usage:
analyzer = FootballMatchAnalyzer()
base_url = "https://www.goalserve.com/getfeed/401117231212497fb27a08db8de47c17/soccerfixtures"
output_dir = "winner/football"
analyzer.download_all_leagues(base_url, output_dir)
winner = analyzer.find_winner("Chelsea", "Luton Town", "Premier_League")
print("Winner:", winner)
