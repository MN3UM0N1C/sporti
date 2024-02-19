import requests
from bs4 import BeautifulSoup, Comment
import json
from fake_useragent import UserAgent
import time
from unidecode import unidecode


class FootballerScraper:
	def __init__(self, user_input, team=False):
		self.user_input = ''.join(char for char in unidecode(user_input.replace("-", " ")) if char.isalpha() or char.isspace()).replace(" ", "+")
		self.proxy_to_use = {"http": "http://customer-Football:FootballPassword_123@pr.oxylabs.io:7777"}
		self.headers = {
			'User-Agent': UserAgent().random,
			"Accept-Language": "en-US,en;q=0.5",
			"Referer": "https://www.google.com/",
			"DNT": "1",
			"X-Forwarded-For": "127.0.0.1",
		}
		self.team = team
		self.user_input = user_input

	def player_last_matches(self):
		initial_url = f'https://www.besoccer.com/ajax/autocomplete?q={self.user_input}'
		response = requests.get(initial_url, headers=self.headers)
		soup = BeautifulSoup(response.text, "html.parser")
		matches = []
		first_player_url = soup.find_all("li")[1].a['href']
		tables = BeautifulSoup(requests.get(first_player_url.replace("player/", "player/matches/"), headers=self.headers).text, 'html.parser').find_all("tbody")[:10]
		# tables = table.find_all('tbody')[:10]  # Limit to the first 10 tables
		print(tables)
		for table in tables:
		    rows = table.find_all('tr', class_='row-body')[:10]  # Limit to the first 10 rows
		    for row in rows:
		        match = {}
		        columns = row.find_all('td')
		        for i, column in enumerate(columns):
		            header = table.find_all('th')[i].text.strip().lower().replace("\n", "")  # Get column header text
		            match[header] = column.text.strip().replace("\n", "")
		        matches.append(match)
		return json.dumps(matches)

	def team_last_matches(self):
		initial_url = f'https://www.besoccer.com/ajax/autocomplete?q={self.user_input}'
		response = requests.get(initial_url, headers=self.headers)
		soup = BeautifulSoup(response.text, "html.parser")
		matches = []
		first_player_url = soup.find_all("li")[1].a['href']
		panel_divs = BeautifulSoup(requests.get(first_player_url.replace("team/", "team/matches/"), headers=self.headers).text, 'html.parser').find_all('div', class_='panel')
		for panel_div in panel_divs[2:6]:
			match = {}
			title_div = panel_div.find('div', class_='panel-title')
			match['month'] = title_div.text.strip() if title_div else None
			match_divs = panel_div.find_all('a', class_='match-link')
			for match_div in match_divs:
			    match_info_div = match_div.find('div', class_='info-head')
			    match['status'] = match_info_div.find('span', class_='tag').text.strip() if match_info_div and match_info_div.find('span', class_='tag') else None
			    match['tournament'] = match_info_div.find('div', class_='middle-info').text.strip() if match_info_div and match_info_div.find('div', class_='middle-info') else None
			    team_info_divs = match_div.find_all('div', class_='team-info')
			    for i, team_info_div in enumerate(team_info_divs):
			        team_name = team_info_div.find('div', class_='name').text.strip() if team_info_div.find('div', class_='name') else None
			        team_logo_src = team_info_div.find('img', class_='team-shield')['src'] if team_info_div.find('img', class_='team-shield') else None
			        team_score = team_info_div.find('span', class_=f'r{i+1}').text.strip() if team_info_div.find('span', class_=f'r{i+1}') else None
			        match[f'team{i+1}_name'] = team_name
			        match[f'team{i+1}_logo'] = team_logo_src
			        match[f'team{i+1}_score'] = team_score
			    match['date'] = match_div.find('div', class_='date-transform').text.strip() if match_div.find('div', class_='date-transform') else None
			    matches.append(match)
		return json.dumps(matches)

	def search(self):
		if self.team:
			initial_url = f'https://www.besoccer.com/ajax/autocomplete?q={self.user_input}'
			response = requests.get(initial_url, headers=self.headers)
			soup = BeautifulSoup(response.text, "html.parser")
			first_team_url = soup.find_all("li")[1].a['href']

			if first_team_url:
				response = requests.get(first_team_url, headers=self.headers)
				soup = BeautifulSoup(response.text, "html.parser")
				streak_resume_div = soup.find("div", id="mod_streakResume")
				featured_players_div = soup.find("div", id="mod_featuredPlayers")
				injuries_div = soup.find("div", id="mod_injuriesResume")
				season_div = soup.find("div", id="mod_season")

				injuries_data = []
				streak_resume_data = {}
				featured_players_data = {}
				season_data = {}

				if streak_resume_div:
					spree_boxes = streak_resume_div.find_all("a", class_="spree-box")

					for spree_box in spree_boxes:
						team_name = spree_box.find("img", class_="shield")["alt"]
						result = spree_box.find("div", class_="result").text.strip()
						date = spree_box.find("div", class_="date").text.strip()
						
						home_goals, away_goals = result.split("-")
						
						match_url = spree_box["href"]
						streak_resume_data[match_url] = {
							"Team Name": team_name,
							"Home Goals": home_goals,
							"Away Goals": away_goals,
							"Date": date
	   					}

				if featured_players_div:
					def has_data_cy_featuredPlayer(tag):
						return tag.name == "a" and "data-cy" in tag.attrs and tag["data-cy"] == "featuredPlayer"

					featured_player_links = featured_players_div.find_all(has_data_cy_featuredPlayer)

					for player_link in featured_player_links:
						player_name = player_link.find("div", class_="person-name").text.strip()
						player_number = player_link.find("span", class_="number").text.strip()
						player_position = player_link.find("span", class_="bg-role").text.strip()

						# Check if the rating and rating_change elements exist
						rating_element = player_link.find("div", class_="row jc-ce").find("div")
						rating_change_element = player_link.find("div", class_="row jc-ce").find("div", class_="rating-text")

						player_rating = rating_element.text.strip() if rating_element else "N/A"
						rating_change = rating_change_element.text.strip() if rating_change_element else "N/A"

						featured_players_data[player_name] = {
							"Number": player_number,
							"Position": player_position,
							"Rating": player_rating,
							"Rating Change": rating_change
						}
				
				if injuries_div:
					injury_items = injuries_div.find_all("li")

					for item in injury_items:
						player_name = item.find("a", class_="main-text").text.strip()
						injury_description = item.find("div", class_="color-red").text.strip()
						injury_status = item.find("div", class_="color-grey2").text.strip()

						injury_info = {
							"Player Name": player_name,
							"Injury Description": injury_description,
							"Injury Status": injury_status
						}

						injuries_data.append(injury_info)

				if season_div:
					season_title = season_div.find("div", class_="panel-title").text.strip()
					season_subtitle = season_div.find("div", class_="panel-subtitle").text.strip()

					item_columns = season_div.find_all("div", class_="item-col")

					for column in item_columns:
						icon_class = column.find("div", class_="img-ico").get("class")[-1]
						main_line = column.find("div", class_="main-line").text.strip()
						other_lines = column.find_all("div", class_="other-line")

						season_data[icon_class] = {
							"Main Line": main_line,
							"Other Lines": [line.text.strip() for line in other_lines]
						}

					season_data["Season Title"] = season_title
					season_data["Season Subtitle"] = season_subtitle

					matches = soup.find_all('a', class_=lambda x: x and 'spree-box' in x)

					result_mapping = {
						'lose': 'L',
						'win': 'W',
						'draw': 'D'
					}

					form_string = ''.join(result_mapping.get(match['class'][-1], '') for match in matches)

				return f'Last 5 match form: {streak_resume_data} | Injuries: {injuries_data} | featured players: {featured_players_data} | Season info: {season_data} | Form: {form_string}'

		else:
			initial_url = f'https://www.besoccer.com/ajax/autocomplete?q={self.user_input}'
			response = requests.get(initial_url, headers=self.headers)
			soup = BeautifulSoup(response.text, "html.parser")
			first_player_url = soup.find_all("li")[1].a['href']

			if first_player_url:
				response = requests.get(first_player_url, headers=self.headers)
				soup = BeautifulSoup(response.text, "html.parser")
				stats_dict = {}
				personal_data = []
				career_data = {}
				player_info = ''
				birth_details = ''

				panel_head = soup.find("div", class_="panel-head ta-c jc-ce")
				full_name = panel_head.find("div", class_="panel-subtitle").text.strip()

				birth_details_div = soup.find("div", class_="panel-body ta-c mh10")
				if birth_details_div:
					birth_details = birth_details_div.find("p", class_="color-grey2").text.strip()
				else:
					birth_details = "Birth details not found"

				personal_data_section = soup.find('div', class_='table-head', text='Personal data')
				if personal_data_section:
					personal_data_table = personal_data_section.find_next('div', class_='table-body')
						
					personal_data_rows = personal_data_table.find_all('div', class_='table-row pr10')
					for row in personal_data_rows:
						data_label = row.find('div').text
						data_values = row.find_all('div')
						data_value = data_values[1].text.strip() if len(data_values) > 1 else ""
						personal_data.append(f"{data_label}: {data_value}")
				
				table_rows = soup.find_all('div', class_='table-row pr10')
				start_flag = False
				
				career_data = {}

				for row in table_rows:
					label = row.find('div').text.strip()
					if label == "Country of birth":
						country_of_birth = row.find('div', class_='image-row').text.strip()
						career_data[label] = country_of_birth
					elif label == "Preferred foot":
						preferred_foot = row.find_all('div')[1].text.strip()
						career_data[label] = preferred_foot
					elif label == "Continent of birth":
						continent_of_birth = row.find_all('div')[1].text.strip()
						career_data[label] = continent_of_birth
					elif label == "Region of birth":
						region_of_birth = row.find_all('div')[1].text.strip()
						career_data[label] = region_of_birth
					elif label == "Status":
						status = row.find_all('div')[1].text.strip()
						career_data[label] = status
					elif label == "Current club":
						current_club = row.find('a').text.strip()
						career_data[label] = current_club
					elif label == "Current competition":
						current_competition = row.find('a').text.strip()
						career_data[label] = current_competition
					elif label == "Previous club":
						previous_club = row.find('a').text.strip()
						career_data[label] = previous_club
					elif label == "Previous competition":
						previous_competition = row.find('a').text.strip()
						career_data[label] = previous_competition
					elif label == "Historic team":
						historic_team = row.find('a').text.strip()
						career_data[label] = historic_team
					elif label == "Historical competition":
						historical_competition = row.find('a').text.strip()
						career_data[label] = historical_competition
					elif label == "Most common shirt number":
						shirt_number = row.find_all('div')[1].text.strip()
						career_data[label] = shirt_number
					elif label == "Other shirt numbers":
						other_shirt_numbers = row.find_all('div')[1].text.strip()
						career_data[label] = other_shirt_numbers
					elif label == "Lower categories":
						lower_categories = row.find_all('div')[1].text.strip()
						career_data[label] = lower_categories				
								
				stat_divs = soup.find_all('div', class_='stat')

				for stat in stat_divs:
					big_row = stat.find('div', class_='big-row').text.strip()
					small_row = stat.find('div', class_='small-row').text.strip()
					stats_dict[small_row] = big_row
								
				player_info = f'{full_name} - {birth_details} | {" ".join(personal_data)} | {json.dumps(career_data)} | {json.dumps(stats_dict)}'

				competition_divs = soup.find_all("div", class_="scroll-box cheese-content br-right")
				compet_data = []

				for competition_div in competition_divs:
					script_tag = competition_div.find("script", type="application/ld+json")
					if script_tag:
						data = json.loads(script_tag.string)
						name = data.get("name", "")
						sport = data.get("sport", "")
						image = data.get("image", "")
						url = data.get("url", "")

						percentage_elem = competition_div.find("div", class_="percentage")
						percentage = percentage_elem.text if percentage_elem else ""

						victory_elem = competition_div.find("div", class_="color-grey2 victory")
						victory = victory_elem.text if victory_elem else ""

						wins_elem = competition_div.find("div", class_="tag-name c1")
						wins = wins_elem.text if wins_elem else ""

						draws_elem = competition_div.find("div", class_="tag-name c2")
						draws = draws_elem.text if draws_elem else ""

						losses_elem = competition_div.find("div", class_="tag-name c3")
						losses = losses_elem.text if losses_elem else ""

						compet_data.append({
							"Name": name,
							"Sport": sport,
							"Image": image,
							"URL": url,
							"Percentage": percentage,
							"Victory": victory,
							"Wins": wins,
							"Draws": draws,
							"Losses": losses
						})

				player_performance_panel = soup.find("div", class_="panel player-performance")
				player_performance_data = {}

				if player_performance_panel:
					table = player_performance_panel.find("table", class_="table")

					if table:
						rows = table.find_all("tr", class_="row-body")

						for row in rows:
							columns = row.find_all("td")

							if len(columns) >= 4:
								period = columns[0].text.strip()
								matches_played = int(columns[1].text.strip())
								
								goals_span = columns[2].find("span")
								goals = int(goals_span.text.strip()) if goals_span else None
								
								goals_per_90_span = columns[3].find("span")
								goals_per_90 = float(goals_per_90_span.text.strip()) if goals_per_90_span else None

								player_performance_data[period] = {
									"Matches Played": matches_played,
									"Goals": goals,
									"Goals per 90": goals_per_90
								}

				return player_info + ' | Competition data: ' + str(compet_data) + ' | Performance data: ' + json.dumps(player_performance_data)
		
if __name__ == "__main__":
	scraper = FootballerScraper('real madrid', True)
	print(scraper.team_last_matches())
#print(scraper.search())
