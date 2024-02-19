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

keys = []
values = []

def search(id, match, casino):
	with open(f'data/{league_id[id]}.xml', 'r') as file:
		xml_content = file.read()
		soup = BeautifulSoup(xml_content, 'xml')
		for k in soup.find_all("match", {"id": match}):
			if casino != None:
				result = k.find_all('bookmaker', {'name': casino})
			else:
				result = k.find_all('bookmaker')
		return result
def koef(file):	
	for i in file:
		keys.append(i.find('odd').get('name'))
		values.append(i.find('odd').get('value'))
	return json.dumps(dict(zip(keys, values)))


print(koef(search("1399", "5127703", casino="bwin")))
