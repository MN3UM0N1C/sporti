from bs4 import BeautifulSoup
import json
import requests

class NBA():
    def __init__(self, user_input):
        self.user_input = user_input
        self.user_input_url = user_input.replace(" ", "-")
        self.past_game_url = f"https://www.covers.com/sport/basketball/nba/teams/main/{self.user_input_url}"
        self.statistics_url = f"https://www.covers.com/sport/basketball/nba/teams/main/{self.user_input_url}/stats"
        self.injuries_url = f'https://www.covers.com/sport/basketball/nba/teams/main/{self.user_input_url}/injuries'

    def nba_request(self, url):
        page = requests.get(url).text
        soup = BeautifulSoup(page, 'html.parser')
        return soup

    def parser(self):
        page = self.nba_request(self.past_game_url)
        table = page.find("table", {"class" : True})
        record_block =  page.find('div', class_='record-block')
        # Create a dictionary to store the data
        win_loss = {
            "Win / Loss": record_block.find('div', class_='record-value').text}
        header_row = table.find('thead').find_all('tr')[1]
        keys = [th.text.strip() for th in header_row.find_all('th')]
        # Initializing list to hold parsed data
        data = []
        data.append(win_loss)
        # Parsing table rows
        for row in table.find('tbody').find_all('tr'):
            cells = row.find_all('td')
            if len(cells) == len(keys):
                row_data = {}
                for i in range(len(keys)):
                    row_data[keys[i]] = cells[i].text.strip().replace("\n", "").replace("  ", "")
                data.append(row_data)
        return json.dumps(data)

    def statistics_parser(self):
        # Extracting header row to get keys
        table = self.nba_request(self.statistics_url).find("table", {"class" : True})
        header_row = table.find('thead').find_all('tr')[0]
        keys = [th.text.strip() for th in header_row.find_all('th')]
        # Initializing list to hold parsed data
        data = []
        # Parsing table rows
        for row in table.find('tbody').find_all('tr'):
            cells = row.find_all('td')
            if len(cells) == len(keys):
                row_data = {}
                for i in range(len(keys)):
                    row_data[keys[i]] = cells[i].text.strip().replace("\n", "").replace("  ", "")
                data.append(row_data)
        return json.dumps(data)

    def injuries(self):
        soup = self.nba_request(self.injuries_url).find("div", {"class" : "covers-CoversMatchups-responsiveTableContainer"})
        # Find all rows in the table body
        rows = soup.find('tbody').find_all('tr')[::2]  # Select every second row starting from the first row

        # Initialize an empty list to store player information
        players_info = []

        # Loop through each row
        for row in rows:
            # Extract player name
            player_name = row.find('a').get_text(strip=True)
            
            # Extract player position (assuming it's always in the second <td> tag)
            player_position = row.find_all('td')[1].get_text()
            
            # Extract player status
            player_status = row.find_all('td')[2].get_text()
            
            # Append player information to the list
            players_info.append({
                'player_name': player_name.replace("\n", "").replace(" ", ""),
                'player_position': player_position.replace("\n", "").replace(" ", ""),
                'player_status': player_status
            })
        return players_info

    def team_stats(self):
        # Extracting header row to get keys
        table = self.nba_request(self.statistics_url).find("table", {"class" : "covers-CoversResults-Table"})
        header_row = table.find('thead').find_all('tr')[0]
        keys = [th.text.strip() for th in header_row.find_all('th')]
        # Initializing list to hold parsed data
        data = []
        # Parsing table rows
        for row in table.find('tbody').find_all('tr'):
            cells = row.find_all('td')
            if len(cells) == len(keys):
                row_data = {}
                for i in range(len(keys)):
                    row_data[keys[i]] = cells[i].text.strip().replace("\n", "").replace("  ", "")
                data.append(row_data)
        return json.dumps(data)



# Converting data to JSON
scraper = NBA("denver-nuggets")
print(scraper.team_stats())
print(scraper.statistics_parser())
print(scraper.injuries())
print(scraper.parser())


