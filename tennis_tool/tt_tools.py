from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem
from bs4 import BeautifulSoup
import time
import requests
import warnings
import json

warnings.filterwarnings("ignore")


class TennisScraper:
    def __init__(self, user_input):
        self.user_input = user_input
        self.proxy_to_use = {
            "http": "http://customer-Football:FootballPassword_123@pr.oxylabs.io:7777"
        }
        self.headers = {
            'Host': 'ultimatetennisstatistics.com',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest',
            'Sec-Ch-Ua-Mobile': '?0',
            'User-Agent': UserAgent(software_names=SoftwareName.CHROME.value, operating_systems=OperatingSystem.WINDOWS.value, limit=1).get_random_user_agent(),
            'Sec-Ch-Ua-Platform': '""',
            'Referer': 'https://ultimatetennisstatistics.com/',
        }

    def get_player_id(self):
        params = {'term': self.user_input}
        try:
            response = requests.get(
                'https://ultimatetennisstatistics.com/autocompletePlayer',
                params=params,
                headers=self.headers,
                proxies=self.proxy_to_use,
                verify=False
            )
            if response.status_code == 200:
                return response.json()[0]['id']
            else:
                return f"Error: Received status code {response.status_code}"
        except requests.RequestException as e:
            return f"Request failed: {e}"
    
    def player_info(self):
        id = self.get_player_id()

        player_url = f'https://ultimatetennisstatistics.com/playerProfileTab?playerId={id}&tab=profile'
        try:
            response = requests.get(
                player_url,
                headers=self.headers,
                proxies=self.proxy_to_use,
                verify=False
            )

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                data = {}

                for row in soup.find_all('tr'):
                    header, value = self.get_row_data(row)
                    if header and value:
                        data[header] = value

                return data
            else:
                return f"Error: Received status code {response.status_code}"
        except requests.RequestException as e:
            return f"Request failed: {e}"

    def html_table_to_json(self, html_data):
        soup = html_data
        
        result = {}
        
        # Extract serve data
        serve_table = soup.find_all('div', class_='col-lg-3')[0].find('table')
        result['serve'] = self.extract_table_data(serve_table)
        
        # Extract return data
        return_table = soup.find_all('div', class_='col-lg-3')[1].find('table')
        result['return'] = self.extract_table_data(return_table)
        
        # Extract total data
        total_table = soup.find_all('div', class_='col-lg-3')[2].find('table')
        result['total'] = self.extract_table_data(total_table)
        
        return json.dumps(result, indent=2)

    def extract_table_data(self, table):
        data = {}
        rows = table.find_all('tr')
        
        for row in rows:
            columns = row.find_all(['th', 'td'])
            if columns:
                key = columns[0].text.strip()
                value = [col.text.strip() for col in columns[1:]]
                data[key] = value[0] if len(value) == 1 else value
        
        return data

    def statistics(self):
        id = self.get_player_id()
        matches_url = f"https://ultimatetennisstatistics.com/playerStatsTab?playerId={id}"
        statistics_parser = BeautifulSoup(requests.get(matches_url, headers=self.headers,proxies=self.proxy_to_use,verify=False).text, 'html.parser')
        try:
            if "No statistics available" in statistics_parser.get_text():
                return "Not Found"
            else:
                return self.html_table_to_json(statistics_parser.find("div", {"class":"row text-nowrap"}))
        except:
            return "Not Found"

    def get_matches(self):
        id = self.get_player_id()
        matches_url = f'https://ultimatetennisstatistics.com/matchesTable?playerId={id}&current=1&rowCount=15&sort%5Bdate%5D=desc&searchPhrase=&season=&fromDate=&toDate=&level=&bestOf=&surface=&indoor=&speed=&round=&result=&opponent=&tournamentId=&tournamentEventId=&outcome=&score=&countryId=&bigWin=false&_=1704742609214'
        
        try:
            response = requests.get(
                matches_url,
                headers=self.headers,
                proxies=self.proxy_to_use,
                verify=False
            )

            if response.status_code == 200:
                data = response.json()
                matches_data = []

                if 'rows' in data:
                    for match in data['rows']:
                        date = match.get('date', 'N/A')
                        tournament = match.get('tournament', 'N/A')
                        round_played = match.get('round', 'N/A')
                        winner_name = match['winner']['name'] if 'winner' in match else 'N/A'
                        loser_name = match['loser']['name'] if 'loser' in match else 'N/A'
                        score = match.get('score', 'N/A')
                
                        matches_data.append({
                            'date': match.get('date', 'N/A'),
                            'tournament': match.get('tournament', 'N/A'),
                            'round_played': match.get('round', 'N/A'),
                            'winner_name': match['winner']['name'] if 'winner' in match else 'N/A',
                            'loser_name': match['loser']['name'] if 'loser' in match else 'N/A',
                            'score': match.get('score', 'N/A'),
                        })
                
                return ' | '.join(str(match) for match in matches_data)
            else:
                return f"Error: Received status code {response.status_code}"
        except requests.RequestException as e:
            return f"Request failed: {e}"


    def get_row_data(self, row):
        header = row.find('th').get_text(strip=True) if row.find('th') else None
        value_cell = row.find('td')
        value = ''

        if value_cell:
            for child in value_cell.find_all():
                child.unwrap()
            value = value_cell.get_text(strip=True)

        return header, value

def get_wta():
    url = "https://tennisapi1.p.rapidapi.com/api/tennis/rankings/wta"

    headers = {
        "X-RapidAPI-Key": "744abc8a30msh83cdcbcce129559p1c2752jsn420d7c779154",
        "X-RapidAPI-Host": "tennisapi1.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers)

    players = response.json()['rankings']
    wta_standings = ''
    for player in players:
        rank = player.get("ranking", "")
        row_name = player.get("rowName", "")
        points = player.get("points", "")

        wta_standings += f"Rank: {rank}, Row Name: {row_name}, Points: {points} | "

    return wta_standings

def get_atp():
    url = "https://tennisapi1.p.rapidapi.com/api/tennis/rankings/atp"

    headers = {
        "X-RapidAPI-Key": "744abc8a30msh83cdcbcce129559p1c2752jsn420d7c779154",
        "X-RapidAPI-Host": "tennisapi1.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers)

    players = response.json()['rankings']
    atp_standings = ''
    for player in players:
        rank = player.get("ranking", "")
        row_name = player.get("rowName", "")
        points = player.get("points", "")

        atp_standings += f"Rank: {rank}, Row Name: {row_name}, Points: {points} | "

    return atp_standings
tennis_players = [
    "Matteo Berrettini",
    "Diego Schwartzman",
    "Ashleigh Barty",
    "Naomi Osaka",
    "Simona Halep",
    "Sofia Kenin",
    "Serena Williams",
    "Ashleigh Barty",
    "Novak Djokovic",
    "Rafael Nadal",
    "Roger Federer",
    "Dominic Thiem",
    "Daniil Medvedev",
    "Stefanos Tsitsipas",
    "Alexander Zverev",
    "Andrey Rublev",

]

# if __name__ == "__main__":
#     for hu in tennis_players:
#         retry_count = 0
#         while retry_count < 2:
#             try:
#                 scraper = TennisScraper(hu)
#                 results = scraper.player_info()
#                 print(f"{results} \n {scraper.get_matches()} \n\n{hu}")
#             except Exception as e:
#                 retry_count += 1
#                 print(f"Retrying {hu} - Retry count: {retry_count}\n")
#                 time.sleep(10)
#                 continue
#             break
#         else:
#             print(f"Not Found")    
if __name__ == '__main__':
    for i in tennis_players:
        scraper = TennisScraper(i)
        print(i)
        
        try:
            player_info_result = scraper.player_info()
            if isinstance(player_info_result, str):
                print(player_info_result)  # Error message
            else:
                print(player_info_result)
                
            statistics_result = scraper.statistics()
            if statistics_result == "Not Found":
                print("No statistics available for this player.")
            elif isinstance(statistics_result, str):
                print(statistics_result)  # Error message
            else:
                print(statistics_result)
                
            matches_result = scraper.get_matches()
            if matches_result == "Not Found":
                print("No matches found for this player.")
            elif isinstance(matches_result, str):
                print(matches_result)  # Error message
            else:
                print(matches_result)
                
        except Exception as e:
            print(f"An error occurred: {e}")

        # Print ATP and WTA rankings
        print(get_atp())
        print(get_wta())
