import requests
import subprocess

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

url = f"https://www.goalserve.com/getfeed/401117231212497fb27a08db8de47c17/getodds/soccer?cat=soccer_10&League="

def download_file(url, output_file):
    try:
        subprocess.run(['curl', '-o', "data/" + output_file, url], check=True)
        print(f"File downloaded successfully: {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error downloading file: {e}")

for i,b in league_id.items():
	download_file(url + i, f'{b}.xml')



