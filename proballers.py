import requests
import urllib3
from bs4 import BeautifulSoup, Comment
import json

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

basketball_players= [
        "Payton Pritchard",
        "Sam Hauser",
        "Jaylen Brown",
        "Jayson Tatum",
        "Derrick White",
        "Jrue Holiday",
        "Al Horford",
        "Kristaps Porzingis",
        "Luke Kornet",
        "Oshae Brissett",
        "Daniel Hackett",
        "Devontae Cacok",
        "Iffe Lunderberg",
        "Isaïa Cordinier",
        "Jaleen Smith",
        "Jordan Mickey",
        "Marco Belinelli",
        "Ognjen Dobric",
        "Rihards Lomazs",
        "Tornike Shengelia",
        "Gabe Olaseni",
        "Jordan Taylor",
        "Joshua Sharma",
        "Kareem Queeley",
        "Luke Nelson",
        "Matt Morgan",
        "Morayo Soluade",
        "Rokas Gustys",
        "Sam Dekker",
        "Tarik Phillip",
        'Kevin Durant',
        'lebron james',
        'Giannis Antetokounmpo',
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

# for player in basketball_players:
#     data = {'query': player,}
#     response = requests.post('https://www.proballers.com/search_player', headers=headers, data=data, verify=False)
#     try:
#         if response.json()[0]['urlProballers']:
#             print(f'{player} - {response.json()[0]["urlProballers"]}')
#         else:
#             print(f'{player} - Error')
#     except Exception as e:
#         pass

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
		self.user_input = user_input
		self.data = {'query': self.user_input} 
		try:
			if team:
				self.page_content = requests.get(requests.post('https://www.proballers.com/search_team', headers=self.headers, data=self.data, verify=False).json()[0]['team_url'], headers=self.headers)
			else:
				self.page_content = requests.get(requests.post('https://www.proballers.com/search_player', headers=self.headers, data=self.data, verify=False).json()[0]['urlProballers'], headers=self.headers)
		except IndexError:
			self.page_content = False

	def parse_html_table(self):
		if self.page_content:
			soup = BeautifulSoup(self.page_content.text, 'html.parser')
			data_list = []
			table_body = soup.find_all('tbody')[1]
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
			json_data = json.dumps(data_list)
			return json_data
		else:
			return "Not Found"

for i in basketball_players:	
	scraper = BasketballScraper("Boston Celtics", True)
	print(f'{scraper.parse_html_table()}\n{i}\n\n\n')
