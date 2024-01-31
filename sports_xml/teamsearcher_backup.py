from bs4 import BeautifulSoup
import json
import requests
import subprocess
from datetime import datetime
import shutil
import time
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
        self.output_folder = "app/odds/football/"
        self.old_folder = os.path.join(self.output_folder, "old")

    def backup_existing_files(self):
        try:
            if not os.path.exists(self.old_folder):
                os.makedirs(self.old_folder)

            files = os.listdir(self.output_folder)
            xml_files = [f for f in files if f.endswith('.xml')]

            for xml_file in xml_files:
                shutil.move(os.path.join(self.output_folder, xml_file), os.path.join(self.old_folder, xml_file))
                print(f"Moved {xml_file} to old folder.")

        except Exception as e:
            print(f"Error backing up existing files: {e}")

    def download_file(self, league_id, output_file):
        try:
            url = f"{self.base_url}{league_id}"
            current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"{self.league_id_mapping[league_id]}_{current_time}.xml"
            subprocess.run(['curl', '-o', os.path.join(self.output_folder, filename), url], check=True)
            print(f"File downloaded successfully: {filename}")
        except subprocess.CalledProcessError as e:
            print(f"Error downloading file: {e}")
        time.sleep(5)

    def load_data(self, league_id):
        with open(os.path.join(self.output_folder, f"{self.league_id_mapping[league_id]}.xml"), 'r') as file:
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
        self.backup_existing_files()
        for league_id, league_name in self.league_id_mapping.items():
            self.download_file(league_id, f"{league_name}.xml")
            time.sleep(5)

class BasketballDataParser:
    def __init__(self):
        self.base_url = "http://www.goalserve.com/getfeed/401117231212497fb27a08db8de47c17/getodds/soccer?cat=basket_10&League="
        self.league_id_mapping = {"1046": 'nba', "1278": 'euro_league', "1291": 'euro_cup', "2691": 'ncaa'}
        self.output_folder = "app/odds/basketball/"
        self.old_folder = os.path.join(self.output_folder, "old")

    def backup_existing_files(self):
        try:
            if not os.path.exists(self.old_folder):
                os.makedirs(self.old_folder)

            files = os.listdir(self.output_folder)
            xml_files = [f for f in files if f.endswith('.xml')]

            for xml_file in xml_files:
                shutil.move(os.path.join(self.output_folder, xml_file), os.path.join(self.old_folder, xml_file))
                print(f"Moved {xml_file} to old folder.")

        except Exception as e:
            print(f"Error backing up existing files: {e}")

    def download_file(self, league_id, output_file):
        try:
            url = f"{self.base_url}{league_id}"
            current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"{self.league_id_mapping[league_id]}_{current_time}.xml"
            subprocess.run(['curl', '-o', os.path.join(self.output_folder, filename), url], check=True)
            print(f"File downloaded successfully: {filename}")
        except subprocess.CalledProcessError as e:
            print(f"Error downloading file: {e}")

    def load_data(self, league_id):
        try:
            with open(os.path.join(self.output_folder, f"{self.league_id_mapping[league_id]}.xml"), 'r') as file:
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
        self.backup_existing_files()
        for league_id, league_name in self.league_id_mapping.items():
            self.download_file(league_id, f"{league_name}.xml")
            time.sleep(5)


class TennisDataScraper:
    def __init__(self):
        self.base_url = "http://www.goalserve.com/getfeed/401117231212497fb27a08db8de47c17/getodds/soccer?cat=tennis_10"
        self.output_folder = "app/odds/tennis/"
        self.old_folder = os.path.join(self.output_folder, "old")

    def backup_existing_files(self):
        try:
            if not os.path.exists(self.old_folder):
                os.makedirs(self.old_folder)
            files = os.listdir(self.output_folder)
            xml_files = [f for f in files if f.endswith('.xml')]
            for xml_file in xml_files:
                shutil.move(os.path.join(self.output_folder, xml_file), os.path.join(self.old_folder, xml_file))
                print(f"Moved {xml_file} to old folder.")
        except Exception as e:
            print(f"Error backing up existing files: {e}")

    def download_file(self, output_file):
        try:
            self.backup_existing_files()
            url = self.base_url
            current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"tennis_{current_time}.xml"
            subprocess.run(['curl', '-o', os.path.join(self.output_folder, filename), url], check=True)
            print(f"File downloaded successfully: {filename}")
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

class MMADataParser:
    def __init__(self):
        self.base_url = "http://www.goalserve.com/getfeed/401117231212497fb27a08db8de47c17/getodds/soccer?cat=mma_10"
        self.output_folder = "app/odds/mma/"
    def backup_existing_files(self):
        try:
            if not os.path.exists(f"{self.output_folder}old"):
                os.makedirs(f"{self.output_folder}old")

            files = os.listdir(self.output_folder)
            xml_files = [f for f in files if f.endswith('.xml')]

            for xml_file in xml_files:
                shutil.move(f"{self.output_folder}{xml_file}", f"{self.output_folder}old/{xml_file}")
                print(f"Moved {xml_file} to old folder.")

        except Exception as e:
            print(f"Error backing up existing files: {e}")

    def download_file(self, output_file):
        try:
            self.backup_existing_files()
            url = self.base_url
            current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"mma_{current_time}.xml"
            subprocess.run(['curl', '-o', f"{self.output_folder}{filename}", url], check=True)
            print(f"File downloaded successfully: {filename}")
        except subprocess.CalledProcessError as e:
            print(f"Error downloading file: {e}")

    def load_data(self):
        try:
            with open(f'app/odds/mma/mma.xml', 'r') as file:
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
