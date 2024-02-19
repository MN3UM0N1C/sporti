from bs4 import BeautifulSoup
import json
import requests


class LeagueParser:
    def __init__(self, league):
        self.league = league
        self.url = f"https://www.besoccer.com/competition/table/{league}"
        self.parsed_page = BeautifulSoup(requests.get(self.url).text, 'html.parser')

    def leaderboard_parser(self):
        table_data = []
        headers = [th.text.strip() for th in self.parsed_page.select('tr.row-head th')]
        for row in self.parsed_page.select('tr.row-body'):
            team_data = {}
            cells = row.find_all(['td', 'th'])
            for header, cell in zip(headers, cells):
                if header == 'PTS' and cell.text.strip():
                    team_data[header] = cell.text.strip().replace("\n", " ")
                elif header in ['MP', 'W', 'D', 'L', 'GF', 'GA'] and cell.text.strip():
                    team_data[header] = cell.text.strip().split()[0].replace("\n", " ")
                elif header == 'GD' and cell.text.strip():  
                    team_data[header] = cell.text.strip().replace("\n", " ")
                else:
                    if cell.text.strip():
                        team_data[header] = cell.text.strip().replace("\n", " ")
            table_data.append(team_data)
        return table_data

    def leaderboard_table(self):
        data_list = []
        data_list.append(self.leaderboard_parser())
        return json.dumps(data_list).replace("\n", "")

    def html_table_to_json(self):
        player_data = []
        for row in self.parsed_page.select('tbody tr'):
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

    def league_highlights(self):
        data_list = []
        for table in self.parsed_page.find_all("table", class_="table"):
            data_list.append(self.html_table_to_json())
        names = ["goalscorers", "minutes per goal", "GOALS FROM THE PENALTY SPOT", "GOALS FROM THE PENALTY SPOT",
                 "BEST GOALKEEPER", "PENALTIES SAVED", "YELLOW CARDS", "RED CARDS", "ASSISTS", "MATCHES PLAYED"]
        return json.dumps(dict(zip(names, data_list)))


domestic_leagues = ["premier_league", "serie_a", "primera_division", "ligue_1", "bundesliga"]
international_competitions = ["champions_league", "europa_league"]

league_parser = LeagueParser("europa_league")
print(league_parser.leaderboard_table())

# for international in international_competitions:
#     league_parser = LeagueParser(international)
#     print(league_parser.league_highlights())