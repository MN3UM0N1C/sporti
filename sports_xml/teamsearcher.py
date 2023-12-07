from bs4 import BeautifulSoup
import json

league_id = {
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

def search(id, match, casino=None):
	result =[]
	with open(f'data/{league_id[id]}.xml', 'r') as file:
		xml_content = file.read()
		soup = BeautifulSoup(xml_content, 'xml')
		for k in soup.find_all("match", {"id": match}):
			if casino != None:
				result = k.find_all('bookmaker', {'name': casino})
			else:
				result = k.find_all('bookmaker')
		return result

def team(id, teams casino=None):
	c = 0
	with open(f'data/{league_id[id]}.xml', 'r') as file:
		xml_content = file.read()
		soup = BeautifulSoup(xml_content, 'xml')
		matches = soup.find_all("match")
		for i in matches:
			bundle = [i.find("localteam").get("name"), i.find("visitorteam").get("name")]
			if teams[0] in bundle and teams[1] in bundle:
				print(matches[c].get("id"))
				return search(id, matches[c].get("id"), casino=casino)
			c+= 1

def koef(file):
    data = [(k.get('name'), k.get('value')) for i in file for k in i.find_all('odd')]
    return json.dumps(dict(data))


print(koef(team(["Everton", "Newcastle"], "1204", casino="10Bet")))
