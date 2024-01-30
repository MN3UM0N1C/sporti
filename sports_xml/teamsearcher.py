from bs4 import BeautifulSoup
import json
import requests
import subprocess
import time
from datetime import datetime
import os

class FootballDataParser:
    def __init__(self):
        self.base_url = "https://www.goalserve.com/getfeed/401117231212497fb27a08db8de47c17/getodds/soccer?cat=soccer_10&League="
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

    def download_file(self, league_id, output_file):
        try:
            # Backup previous download
            self.backup_previous_download(league_id)

            # Download new content
            url = f"{self.base_url}{league_id}"
            subprocess.run(['curl', '-o', f"app/odds/football/{output_file}", url], check=True)
            print(f"File downloaded successfully: {output_file}")
        except subprocess.CalledProcessError as e:
            print(f"Error downloading file: {e}")
        time.sleep(5)

    def backup_previous_download(self, league_id):
        try:
            # Delete any previously renamed .old files
            self.clean_up_backup_files(league_id)

            # Search for existing .xml file
            files = os.listdir("app/odds/football/")
            xml_files = [file for file in files if file.startswith(self.league_id_mapping[league_id]) and file.endswith(".xml")]

            # Rename the .xml file to .old if it exists
            if xml_files:
                os.rename(f"app/odds/football/{xml_files[0]}", f"app/odds/football/{xml_files[0]}.old")
                print(f"Previous download backed up as: {xml_files[0]}.old")
        except FileNotFoundError:
            pass  # No previous file to backup, ignore

    def clean_up_backup_files(self, league_id):
        try:
            files = os.listdir("app/odds/football/")
            old_files = [file for file in files if file.startswith(self.league_id_mapping[league_id]) and file.endswith(".old")]

            # Delete any previously renamed .old files
            for file in old_files:
                os.remove(f"app/odds/football/{file}")
                print(f"Removed previous backup file: {file}")
        except FileNotFoundError:
            pass

    def load_data(self, league_id):
        with open(f'app/odds/football/{self.league_id_mapping[league_id]}.xml', 'r') as file:
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

            # Check for both team orders
            if (self.is_match(teams[0], local_team) and self.is_match(teams[1], visitor_team)) or \
            (self.is_match(teams[0], visitor_team) and self.is_match(teams[1], local_team)):
                return self.search(league_id, match.get("id"), casino=casino)
                
    def koef(self, file):        
        data = [(k.get('name'), k.get('value')) for i in file for k in i.find_all('odd')]
        return json.dumps(dict(data))

    def download_all_files(self):
        for league_id, league_name in self.league_id_mapping.items():
            try:
                current_datetime = datetime.now().strftime("%Y%m%d%H%M%S")
                output_file = f"{league_name}_{current_datetime}.xml"
                self.download_file(league_id, output_file)
            except Exception as e:
                print(f"Error downloading files for {league_name}: {e}")

class BasketballDataParser:
    def __init__(self):
        self.base_url = "http://www.goalserve.com/getfeed/401117231212497fb27a08db8de47c17/getodds/soccer?cat=basket_10&League="
        self.league_id_mapping = {"1046": 'nba', "1278": 'euro_league', "1291": 'euro_cup', "2691": 'ncaa'}

    def download_file(self, league_id, output_file):
        try:
            # Backup previous download
            self.backup_previous_download(league_id)

            # Download new content
            url = f"{self.base_url}{league_id}"
            subprocess.run(['curl', '-o', f"app/odds/basketball/{output_file}", url], check=True)
            print(f"File downloaded successfully: {output_file}")
        except subprocess.CalledProcessError as e:
            print(f"Error downloading file: {e}")

    def backup_previous_download(self, league_id):
        try:
            # Delete any previously renamed .old files
            self.clean_up_backup_files(league_id)

            # Search for existing .xml file
            files = os.listdir("app/odds/basketball/")
            xml_files = [file for file in files if file.startswith(self.league_id_mapping[league_id]) and file.endswith(".xml")]

            # Rename the .xml file to .old if it exists
            if xml_files:
                os.rename(f"app/odds/basketball/{xml_files[0]}", f"app/odds/basketball/{xml_files[0]}.old")
                print(f"Previous download backed up as: {xml_files[0]}.old")
        except FileNotFoundError:
            pass  # No previous file to backup, ignore

    def clean_up_backup_files(self, league_id):
        try:
            files = os.listdir("app/odds/basketball/")
            old_files = [file for file in files if file.startswith(self.league_id_mapping[league_id]) and file.endswith(".old")]

            # Delete any previously renamed .old files
            for file in old_files:
                os.remove(f"app/odds/basketball/{file}")
                print(f"Removed previous backup file: {file}")
        except FileNotFoundError:
            pass

    def load_data(self, league_id):
        try:
            with open(f'app/odds/basketball/{self.league_id_mapping[league_id]}.xml', 'r') as file:
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
            try:
                current_datetime = datetime.now().strftime("%Y%m%d%H%M%S")
                output_file = f"{league_name}_{current_datetime}.xml"
                self.download_file(league_id, output_file)
                time.sleep(5)
            except Exception as e:
                print(f"Error downloading files for {league_name}: {e}")



class TennisDataScraper:
    def __init__(self):
        self.base_url = "http://www.goalserve.com/getfeed/401117231212497fb27a08db8de47c17/getodds/soccer?cat=tennis_10"

    def download_file(self, output_file):
        try:
            # Backup previous download
            self.backup_previous_download()

            # Download new content
            url = self.base_url
            subprocess.run(['curl', '-o', f"data/tennis/{output_file}", url], check=True)
            print(f"File downloaded successfully: {output_file}")
        except subprocess.CalledProcessError as e:
            print(f"Error downloading file: {e}")

    def backup_previous_download(self):
        try:
            # Delete any previously renamed .old files
            self.clean_up_backup_files()

            # Search for existing .xml file
            files = os.listdir("data/tennis/")
            xml_files = [file for file in files if file.endswith(".xml")]

            # Rename the .xml file to .old if it exists
            if xml_files:
                os.rename(f"data/tennis/{xml_files[0]}", f"data/tennis/{xml_files[0]}.old")
                print(f"Previous download backed up as: {xml_files[0]}.old")
        except FileNotFoundError:
            pass  # No previous file to backup, ignore

    def clean_up_backup_files(self):
        try:
            files = os.listdir("data/tennis/")
            old_files = [file for file in files if file.endswith(".old")]

            # Delete any previously renamed .old files
            for file in old_files:
                os.remove(f"data/tennis/{file}")
                print(f"Removed previous backup file: {file}")
        except FileNotFoundError:
            pass

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
        try:
            current_datetime = datetime.now().strftime("%Y%m%d%H%M%S")
            output_file = f"tennis_{current_datetime}.xml"
            self.download_file(output_file)
        except Exception as e:
            print(f"Error downloading files: {e}")

class MMADataParser:
    def __init__(self):
        self.base_url = "http://www.goalserve.com/getfeed/401117231212497fb27a08db8de47c17/getodds/soccer?cat=mma_10"

    def download_file(self, output_file):
        try:
            # Backup previous download
            self.backup_previous_download()

            # Download new content
            url = self.base_url
            subprocess.run(['curl', '-o', f"app/odds/mma/{output_file}", url], check=True)
            print(f"File downloaded successfully: {output_file}")
        except subprocess.CalledProcessError as e:
            print(f"Error downloading file: {e}")

    def backup_previous_download(self):
        try:
            # Delete any previously renamed .old files
            self.clean_up_backup_files()

            # Search for existing .xml file
            files = os.listdir("app/odds/mma/")
            xml_files = [file for file in files if file.endswith(".xml")]

            # Rename the .xml file to .old if it exists
            if xml_files:
                os.rename(f"app/odds/mma/{xml_files[0]}", f"app/odds/mma/{xml_files[0]}.old")
                print(f"Previous download backed up as: {xml_files[0]}.old")
        except FileNotFoundError:
            pass  # No previous file to backup, ignore

    def clean_up_backup_files(self):
        try:
            files = os.listdir("app/odds/mma/")
            old_files = [file for file in files if file.endswith(".old")]

            # Delete any previously renamed .old files
            for file in old_files:
                os.remove(f"app/odds/mma/{file}")
                print(f"Removed previous backup file: {file}")
        except FileNotFoundError:
            pass

    def load_data(self, file_path):
        try:
            with open(file_path, 'r') as file:
                xml_content = file.read()
                return BeautifulSoup(xml_content, 'xml')
        except FileNotFoundError:
            print(f"Error: File not found at {file_path}. Make sure to download the file first.")

    def search(self, file_path, match, casino=None):
        try:
            soup = self.load_data(file_path)
            result = []
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
        file_path = 'app/odds/mma/mma.xml'
        soup = self.load_data(file_path)
        matches = soup.find_all("match")
        for match in matches:
            local_team = match.find("localteam")
            away_team = match.find("awayteam")
            if self.is_match(teams[0], local_team.get("name")) and self.is_match(teams[1], away_team.get("name")):
                return self.search(file_path, match.get("id"), casino=casino)

    def koef(self, file_path):
        try:
            soup = self.load_data(file_path)
            data = [(k.get('name'), k.get('value')) for i in soup for k in i.find_all('odd')]
            return json.dumps(dict(data))
        except (TypeError, AttributeError):
            print("Coefficients not found.")

    def download_all_files(self):
        try:
            current_datetime = datetime.now().strftime("%Y%m%d%H%M%S")
            output_file = f"mma_{current_datetime}.xml"
            self.download_file(output_file)
        except Exception as e:
            print(f"Error downloading files: {e}")


if __name__ == "__main__":
    mma_parser = MMADataParser()
    basketball_parser = BasketballDataParser()
    football_parser = FootballDataParser()
    mma_parser.download_all_files()
    basketball_parser.download_all_files()
    football_parser.download_all_files()
