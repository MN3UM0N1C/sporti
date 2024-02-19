import requests
import urllib3
from bs4 import BeautifulSoup, Comment
import json

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

nba_teams = [
    "Atlanta Hawks",
    "Boston Celtics",
    "Brooklyn Nets",
    "Charlotte Hornets",
    "Chicago Bulls",
    "Cleveland Cavaliers",
    "Dallas Mavericks",
    "Denver Nuggets",
    "Detroit Pistons",
    "Golden State Warriors",
    "Houston Rockets",
    "Indiana Pacers",
    "LA Clippers",
    "Los Angeles Lakers",
    "Memphis Grizzlies",
    "Miami Heat",
    "Milwaukee Bucks",
    "Minnesota Timberwolves",
    "New Orleans Pelicans",
    "New York Knicks",
    "Oklahoma City Thunder",
    "Orlando Magic",
    "Philadelphia 76ers",
    "Phoenix Suns",
    "Portland Trail Blazers",
    "Sacramento Kings",
    "San Antonio Spurs",
    "Toronto Raptors",
    "Utah Jazz",
    "Washington Wizards"
]


headers = {
	'Host': 'www.proballers.com',
	'Sec-Ch-Ua-Mobile': '?0',
	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.134 Safari/537.36',
	'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
	'Accept': '*/*',
	'X-Requested-With': 'XMLHttpRequest',
	'Sec-Ch-Ua-Platform': '""',
	'Origin': 'https://www.proballers.com',
	'Sec-Fetch-Site': 'same-origin',
	'Sec-Fetch-Mode': 'cors',
	'Sec-Fetch-Dest': 'empty',
	'Referer': 'https://www.proballers.com/',
	'Accept-Language': 'en-US,en;q=0.9',
	'Connection': 'close',
}

class BasketballScraper:
	def __init__(self, user_input, team=False):
		self.headers = {
		'Host': 'www.proballers.com',
		'Sec-Ch-Ua-Mobile': '?0',
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.134 Safari/537.36',
		'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
		'Accept': '*/*',
		'X-Requested-With': 'XMLHttpRequest',
		'Sec-Ch-Ua-Platform': '""',
		'Origin': 'https://www.proballers.com',
		'Sec-Fetch-Site': 'same-origin',
		'Sec-Fetch-Mode': 'cors',
		'Sec-Fetch-Dest': 'empty',
		'Referer': 'https://www.proballers.com/',
		'Accept-Language': 'en-US,en;q=0.9',
		'Connection': 'close',
		}
		if "los angeles clippers" in user_input or "Clippers" in user_input or "clippers" in user_input:
			self.user_input = "LA Clippers"
		else:
			self.user_input = user_input
		self.data = {'query': self.user_input} 
		try:
			if team:
				self.page_content = requests.get(requests.post('https://www.proballers.com/search_team', headers=self.headers, data=self.data, verify=False).json()[0]['team_url'], headers=self.headers)
			else:
				self.page_content = requests.get(requests.post('https://www.proballers.com/search_player', headers=self.headers, data=self.data, verify=False).json()[0]['urlProballers'], headers=self.headers)
		except IndexError:
			self.page_content = False

	def retain_unique_elements(self, input_list):
		seen = set()
		unique_elements = []
		for elem in input_list:
			# Convert element to its string representation
			elem_str = str(elem)
			if elem_str not in seen:
				seen.add(elem_str)
				unique_elements.append(elem)
		return json.dumps(unique_elements)

	def averages(self):
		if self.page_content:
			soup = BeautifulSoup(self.page_content.text, 'html.parser')
			return json.dumps({title.get_text(): stat.get_text() for title, stat in zip(soup.find_all("span", class_="identity__stats__title"), soup.find_all("span", class_="identity__stats__stat"))})

	def parse_html_table(self):
	    if self.page_content:
	        soup = BeautifulSoup(self.page_content.text, 'html.parser')
	        data_list = []
	        for table in soup.find_all('table'):
	            table_data = []
	            headers = []
	            thead = table.find('thead')
	            if thead:
	                header_row = thead.find('tr')
	                if header_row:
	                    headers = [header.text.strip().lower() for header in header_row.find_all(['th', 'td'])]
	            tbody = table.find('tbody')
	            if tbody:
	                rows = tbody.find_all('tr')
	                for row in rows:
	                    row_data = {}
	                    cells = row.find_all(['td', 'th'])
	                    for i, cell in enumerate(cells):
	                        if i < len(headers):
	                            header_text = headers[i]
	                            cell_text = cell.text.strip()
	                            link = cell.find('a')
	                            if link:
	                                link_text = link.get('href')
	                                row_data[header_text] = {'text': cell_text, 'link': link_text}
	                            else:
	                                row_data[header_text] = cell_text
	                    table_data.append(row_data)
	            data_list.append(table_data)
	        return json.dumps(data_list)

	def parse_euroleague(self):
		if self.page_content:
			soup = BeautifulSoup(self.page_content.text, 'html.parser')
			data_list = []
			soup2 = soup.find('div', {"aria-labelledby": True, "class" : True, "id" : True})
			table_body = soup2.find("tbody")
			rows = table_body.find_all('tr')
			num_columns = max(len(row.find_all(['td', 'th'])) for row in rows)
			for row in rows:
				row_data = {}
				cells = row.find_all(['td', 'th'])
				for i, cell in enumerate(cells):
					header_text = soup.find_all('thead')[0].find_all('th')[i].text.strip().lower()
					cell_text = cell.text.strip()
					link = cell.find('a')
					if link:
						link_text = link.get('href')
						row_data[header_text] = {'text': cell_text, 'link': link_text}
					else:
						row_data[header_text] = cell_text
				data_list.append(row_data)
			return self.retain_unique_elements(data_list)

	def parse_games_table(self):
		if self.page_content:
			soup = BeautifulSoup(requests.get(f'{self.page_content.url}/games').text, "html.parser")
			data_list = []
			for table in soup.find_all('table'):
				table_data = []
				headers = []
				thead = table.find('thead')
				if thead:
				    header_row = thead.find('tr')
				    if header_row:
				        headers = [header.text.strip().lower() for header in header_row.find_all(['th', 'td'])]
				tbody = table.find('tbody')
				if tbody:
				    rows = tbody.find_all('tr')
				    for row in rows:
				        row_data = {}
				        cells = row.find_all(['td', 'th'])
				        for i, cell in enumerate(cells):
				            if i < len(headers):
				                header_text = headers[i]
				                cell_text = cell.text.strip()
				                link = cell.find('a')
				                if link:
				                    link_text = link.get('href')
				                    row_data[header_text] = {'text': cell_text, 'link': link_text}
				                else:
				                    row_data[header_text] = cell_text
				        table_data.append(row_data)
				data_list.append(table_data)
				return json.dumps(data_list)

	def leaders(self):
		if self.page_content:
			soup = BeautifulSoup(requests.get(f'{self.page_content.url}games').text, "html.parser")
			data_list = []
			for leader in soup.find('div', class_='team-leaders__entry-container').find_all("li", {"class": "team-leaders__entry"}):
				data_list.append(leader.get_text().replace("\n", "").replace("  ", ""))
			return data_list
		else:
			return "Not Found"



for i in nba_teams:	
	scraper = BasketballScraper("la clippers", True)
	#print(scraper.parse_games_table())
	#print(scraper.parse_html_table())
	#print(scraper.averages())
	print(scraper.parse_euroleague())
	#print(scraper.leaders())


