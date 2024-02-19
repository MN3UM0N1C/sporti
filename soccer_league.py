from bs4 import BeautifulSoup
import json
import requests

class SoccerScraper:
    def __init__(self):
        self.domestic_leagues = ["premier_league", "serie_a", "primera_division", "ligue_1", "bundesliga"]
        self.international_competitions = ["champions_league", "europa_league"]

    def leaderboard_parser(self, html):
        soup = html
        table_data = []
        headers = [th.text.strip() for th in soup.select('tr.row-head th')]
        for row in soup.select('tr.row-body'):
            team_data = {}
            cells = row.find_all(['td', 'th'])
            for header, cell in zip(headers, cells):
                if header == 'PTS':
                    team_data[header] = cell.text.strip().replace("\n", " ")
                elif header in ['MP', 'W', 'D', 'L', 'GF', 'GA']:
                    team_data[header] = cell.text.strip().split()[0].replace("\n", " ")
                elif header == 'GD':
                    team_data[header] = cell.text.strip().replace("\n", " ")
                else:
                    team_data[header] = cell.text.strip().replace("\n", " ")
            table_data.append(team_data)
        return table_data

    def html_table_to_json(self, html):
        soup = html
        player_data = []
        for row in soup.select('tbody tr'):
            player = {}
            ld_json_script = row.find('script', {'type': 'application/ld+json'})
            if ld_json_script:
                ld_json_data = json.loads(ld_json_script.string)
                player['name'] = ld_json_data.get('name', '')
                player['team'] = ld_json_data.get('worksFor', '')
            cells = row.find_all(['td', 'th'])
            for cell in cells:
                class_list = cell.get('class', [])
                if 'num' in class_list:
                    matches_text = cell.find('span', class_='va-m').text.strip().split()[0]
                    matches = int(''.join(c for c in matches_text if c.isdigit()))
                    goals_text = cell.find('span', class_='va-m').text.strip().split()[0]
                    goals = int(''.join(c for c in goals_text if c.isdigit()))
                    goal_average_text = cell.find('span', class_='extra-num').text.strip('()').replace('%', '')
                    goal_average = float(goal_average_text)
                    player['statistics'] = {
                        'matches': matches,
                        'goals': goals,
                        'goal_average': goal_average
                    }
            player_data.append(player)
        return player_data

    def format_output(self, data_list):
        formatted_output = ""
        for data in data_list:
            for team_data in data:
                formatted_output += f"{team_data.get('', '').strip()} | pts: {team_data.get('PTS', '')} | games played: {team_data.get('MP', '')} | w: {team_data.get('W', '')} | d: {team_data.get('D', '')} | l: {team_data.get('L', '')} | goalsfor: {team_data.get('GF', '')} | goals against: {team_data.get('GA', '')} | goals difference: {team_data.get('GD', '')} |\n"
        return formatted_output.strip()
        
    def league_highlights(self, league):
        data_list = []
        url = f"https://www.besoccer.com/competition/rankings/{league}"
        parsed_page = BeautifulSoup(requests.get(url).text, 'html.parser')
        for table in parsed_page.find_all("table", class_="table"):
            data_list.append(self.html_table_to_json(table))
        names = ["goalscorers", "minutes per goal", "GOALS FROM THE PENALTY SPOT", "GOALS FROM THE PENALTY SPOT",
                 "BEST GOALKEEPER", "PENALTIES SAVED", "YELLOW CARDS", "RED CARDS", "ASSISTS", "MATCHES PLAYED"]
        return json.dumps(dict(zip(names, data_list)))

    def leaderboard_table(self, league):
        data_list = []
        url = f"https://www.besoccer.com/competition/table/{league}"
        parsed_page = BeautifulSoup(requests.get(url).text, 'html.parser')
        data_list.append(self.leaderboard_parser(parsed_page.find("table", class_="table")))
        return json.dumps(data_list).replace("\n", "")

    def scrape_data(self):
        for league in self.domestic_leagues:
            print(self.format_output(self.league_highlights(league)))
            print(self.format_output(self.leaderboard_table(league)))

        for international in self.international_competitions:
            print(self.league_highlights(international))

# Create an instance of the SoccerScraper class
scraper = SoccerScraper()
# Call the method to scrape data
scraper.scrape_data()