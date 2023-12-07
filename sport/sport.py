import requests
from bs4 import BeautifulSoup
import json

user_input = "lionel messi"
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'}
url = f'https://www.transfermarkt.com/schnellsuche/ergebnis/schnellsuche?query={user_input}'  
response = requests.get(url, headers=headers)
data_list = []

def dictifier(data):
    player_info = {}
    current_key = None
    for item in data_list:
        if ':' in item:
            current_key = item.replace(':', '').strip()
            player_info[current_key] = None  # Initialize the key with None
        elif current_key is not None:
            # Remove unnecessary characters and whitespace
            value = item.replace('\n', '').strip()
            # Skip empty values
            if value:
                player_info[current_key] = value
    return player_info

def rewards(url):
    rewards_page = requests.get(url, headers=headers)
    reward_parsed = BeautifulSoup(rewards_page.text, 'html.parser')
    



def footballer_info(url):
    classname = "info-table info-table--right-space min-height-audio"
    page = requests.get(url, headers=headers)
    info = BeautifulSoup(page.text, 'html.parser')
    try:
        div_block = info.find("div", class_="info-table info-table--right-space min-height-audio").find_all("span")
    except AttributeError:
        div_block = info.find("div", class_="info-table info-table--right-space").find_all("span")
    for i in div_block:
        data_list.append(i.text)
    return dictifier(data_list) 


def search():
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        td_elements = soup.find_all('td', class_="hauptlink")
        try:
            fb_url = "https://www.transfermarkt.com" + td_elements[0].find("a").get("href")
            return footballer_info(fb_url)
        except IndexError:
            return "Footballer not found" 
    else:
        return f"Request failed with status code: {response.status_code}"

print(search())



