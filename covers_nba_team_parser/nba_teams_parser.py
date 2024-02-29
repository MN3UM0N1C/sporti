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
        record_block =  page.find('div', class_='record-block')
        data = []
        # Create a dictionary to store the data
        win_loss = {
            "Win / Loss": record_block.find('div', class_='record-value').text}
        data.append(win_loss)
        return json.dumps(data)

    def statistics_parser(self):
        player_statistics = {}
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
        player_statistics["Player statistics"] = data
        return json.dumps(player_statistics)

    def last_10(self):
        player_statistics = {}
        # Extracting header row to get keys
        table = self.nba_request(self.statistics_url).find_all("div", {"class" : "covers-CoversTeamPage-lastN"})
        for blocks in table:
            if "Last 10" in str(blocks):
                table = blocks.find("table")
        # Find the table body
        table_body = table.find('tbody')
        player_statistics = []
        # Loop through each row in the table body
        for row in table_body.find_all('tr'):
            # Extract data from each cell in the row
            cells = row.find_all('td')
            player_data = {
                "Date": cells[0].get_text().split("\n")[2],
                "VS": cells[0].get_text().split("\n")[6].replace("@", "").replace(" ", ""),
                "Scores": cells[0].get_text().split("\n")[10]
            }
            player_statistics.append(player_data)
        result = {"Last 10 Matches" : player_statistics}
        return json.dumps(result)

    def injuries(self):
        injuries_statistics = {}
        soup = self.nba_request(self.injuries_url).find("div", {"class" : "covers-CoversMatchups-responsiveTableContainer"})
        # Find all rows in the table body
        rows = soup.find('tbody').find_all('tr')[::2]  # Select every second row starting from the first row

        # Initialize an empty list to store player information
        players_info = []

        # Loop through each row
        for row in rows:
            # Extract player name
            if row.find('a') != None:
                player_name = row.find('a').get_text(strip=True)
            else:
                return "No injuries"
            
            # Extract player position (assuming it's always in the second <td> tag)
            player_position = row.find_all('td')[1].get_text()
            
            # Extract player status
            player_status = row.find_all('td')[2].get_text()
            
            # Append player information to the list
            players_info.append({
                'player_name': player_name.replace("\n", "").replace(" ", "").replace("\\n", "").replace("\\r", ""),
                'player_position': player_position.replace("\n", "").replace(" ", "").replace("\\n", "").replace("\\r", ""),
                'player_status': player_status.replace("\n", "").replace(" ", "").replace("\r", "")
            })
        injuries_statistics["Injuries statistics"] = players_info
        return json.dumps(players_info)

    def team_stats(self):
        team_stats = {}
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
        team_stats["Team statistics"] = data
        return json.dumps(team_stats)

    def team_offensive_stats(self):
        offensive = {}
        divs = self.nba_request(self.statistics_url).find_all("div", {"class" : "covers-CoversMatchups-responsiveTableContainer"})
        for blocks in divs:
            if "Offense" in str(blocks):
                table = blocks
                break
        # Find all table rows in the table body
        rows = table.find('tbody').find_all('tr')
        # Initialize an empty list to store the data
        data = []
        # Loop through each row
        for row in rows:
            # Extract the cells in the row
            cells = row.find_all('td')
            # Extract the text content from each cell
            row_data = [cell.get_text(strip=True) for cell in cells]
            # Append the row data to the list
            data.append(row_data)
        # Convert the list of data to a dictionary
        result = {}
        for row in data:
            result[row[0]] = {
                "Season Stats": row[1],
                "Rank": row[2]}

        offensive["offensive statistics"] = result
        return json.dumps(offensive)

    def team_defensive_stats(self):
        defensive = {}
        divs = self.nba_request(self.statistics_url).find_all("div", {"class" : "covers-CoversMatchups-responsiveTableContainer"})
        for blocks in divs:
            if "Defense" in str(blocks):
                table = blocks
                break
        # Find all table rows in the table body
        rows = table.find('tbody').find_all('tr')
        # Initialize an empty list to store the data
        data = []
        # Loop through each row
        for row in rows:
            # Extract the cells in the row
            cells = row.find_all('td')
            # Extract the text content from each cell
            row_data = [cell.get_text(strip=True) for cell in cells]
            # Append the row data to the list
            data.append(row_data)
        # Convert the list of data to a dictionary
        result = {}
        for row in data:
            result[row[0]] = {
                "Season Stats": row[1],
                "Rank": row[2]
            }
        defensive["defensive statistics"] = result
        return json.dumps(defensive)

    def team_leader_stats(self):
        team_leader = {}
        divs = self.nba_request(self.statistics_url).find_all("div", {"class" : "covers-CoversMatchups-responsiveTableContainer"})
        for blocks in divs:
            if "Team Leaders" in str(blocks):
                table = blocks
                break
        # Find all table rows in the table body
        rows = table.find('tbody').find_all('tr')
        # Initialize an empty list to store the data
        data = []
        # Loop through each row
        for row in rows:
            # Extract the cells in the row
            cells = row.find_all('td')
            # Extract the text content from each cell
            row_data = [cell.get_text(strip=True) for cell in cells]
            # Append the row data to the list
            data.append(row_data)
        # Convert the list of data to a dictionary
        result = {}
        for row in data:
            result[row[0]] = {
                "Player Name": row[1],
                row[0] : row[2]
            }
        team_leader["team leader statistics"] = result
        return json.dumps(team_leader)


nba_teams = [
    "atlanta-hawks",
    "boston-celtics",
    "brooklyn-nets",
    "charlotte-hornets",
    "chicago-bulls",
    "cleveland-cavaliers",
    "dallas-mavericks",
    "denver-nuggets",
    "detroit-pistons",
    "golden-state-warriors",
    "houston-rockets",
    "indiana-pacers",
    "los-angeles-clippers",
    "los-angeles-lakers",
    "memphis-grizzlies",
    "miami-heat",
    "milwaukee-bucks",
    "minnesota-timberwolves",
    "new-orleans-pelicans",
    "new-york-knicks",
    "oklahoma-city-thunder",
    "orlando-magic",
    "philadelphia-76ers",
    "phoenix-suns",
    "portland-trail-blazers",
    "sacramento-kings",
    "san-antonio-spurs",
    "toronto-raptors",
    "utah-jazz",
    "washington-wizards"
]

class all_in_one():
    def __init__(self, team_name):
        self.team = team_name
        pass 
    def search(self):
        scraper = NBA(self.team)
        return [scraper.injuries(), scraper.statistics_parser(),scraper.injuries(),scraper.team_stats(),scraper.team_offensive_stats(),scraper.team_defensive_stats(),scraper.team_leader_stats(), scraper.parser()]

if __name__ == "__main__":
    for team in nba_teams:
        searcher = all_in_one(team)
        print(searcher.search())
