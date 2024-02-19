import requests
from bs4 import BeautifulSoup, Comment
import json
from fake_useragent import UserAgent
import time
from unidecode import unidecode
from datetime import datetime


broken_list = []

class FootballerScraper:
    def __init__(self, user_input):
        self.leagues = {}
        # Clean and prepare the user input for search
        self.user_input = ''.join(char for char in unidecode(user_input.replace("-", " ")) if char.isalpha() or char.isspace()).replace(" ", "+")
        self.proxy_to_use = {"http": "http://customer-Football:FootballPassword_123@pr.oxylabs.io:7777"}
        self.uri = None
        self.headers = {
            'User-Agent': UserAgent().random,
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": "https://www.google.com/",
            "DNT": "1",
            "X-Forwarded-For": "127.0.0.1",
            "Cookie": "asdasj ejjee"
        }
        # Get content from the initial search page
        self.content  = requests.get(f"http://www.basketball-reference.com/search/search.fcgi?&search={self.user_input}", headers=self.headers, proxies=self.proxy_to_use)
        self.url = f'https://www.transfermarkt.com/schnellsuche/ergebnis/schnellsuche?query={user_input}'
        self.data_list = []
        self.global_page = None

    def dictifier(self, data):
        player_info = {}
        current_key = None
        for item in data:
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

    def rewards(self):
        rewards_list = []
        rewards_dict = {"rewards": ""}
        soup = BeautifulSoup((self.content.text), 'html.parser')
        self.global_page = BeautifulSoup(
                    requests.get(
                        f'http://www.basketball-reference.com{soup.find("div", id="players").find("div", class_="search-item-name").find("a", href=True).get("href")}',
                        headers=self.headers, proxies=self.proxy_to_use).text.replace("<!--", " "), "html.parser")
        for j in self.global_page.find("ul", {"id": "bling"}).find_all("li", class_=True):
            rewards_list.append(j.get_text())
        rewards_dict["rewards"] = rewards_list
        return json.dumps(rewards_dict)

    def footballer_info(self, url):
        classname = "info-table info-table--right-space min-height-audio"
        page = requests.get(url, headers=self.headers, proxies=self.proxy_to_use)
        info = BeautifulSoup(page.text, 'html.parser')
        div_block = info.find("div", class_=classname).find_all("span")
        for i in div_block:
            self.data_list.append(i.text)
        return json.dumps(self.dictifier(self.data_list))

    def search(self):
        response = requests.get(self.url, headers=self.headers, proxies=self.proxy_to_use)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            td_elements = soup.find_all('td', class_="hauptlink")
            fb_url = "https://www.transfermarkt.com" + td_elements[0].find("a").get("href")
            return self.footballer_info(fb_url)
        else:
            return f"Request failed with status code: {response.status_code}"

    def dict_parser(self, div):
        page_content = requests.get("http://www.basketball-reference.com", headers=self.headers, proxies=self.proxy_to_use).text
        main_page = BeautifulSoup(page_content, "html.parser").find("div", {"id": div}).find_all("a")
        for i in main_page:
            self.leagues[i.get("href").split("/")[3]] = ''.join(char for char in unidecode(i.get_text().replace("-", " ")) if char.isalpha() or char.isspace()).replace(" ", "+")
        if div == "div_ecp_standings":
            return self.leagues 
        else:          
            return self.dict_parser("div_ecp_standings")

    def table_parser(self, div_id, allc=False):
        href_value = None
        info = BeautifulSoup(self.content.text, 'html.parser')
        date_id = "date"
        if info.find('div', id="inpage_nav") is None:
            info = self.global_page
            if allc:
                for links in info.find_all("a", {"href": True}):
                    if "all_comps" in str(links.get("href")):
                        href_value = links.get("href")
                        break
                table_div = BeautifulSoup(requests.get(f'http://www.basketball-reference.com{href_value}', headers=self.headers,
                                                       proxies=self.proxy_to_use).text.replace("<!--", " "), "html.parser")
            else:
                table_div = info.find("div", {"id": div_id})
                if table_div == None:
                    table_div = info.find("div", {"id":"switcher_per_game-playoffs_per_game"})
        else:
            if allc:
                for links in info.find_all("a", {"href": True}):
                    if "all_comps" in str(links.get("href")):
                        href_value = links.get("href")
                        break
                table_div = BeautifulSoup(requests.get(f'http://www.basketball-reference.com{href_value}', headers=self.headers,
                                                       proxies=self.proxy_to_use).text.replace("<!--", " "), "html.parser")
            else:
                table_div = info.find("div", {"id": div_id})
                if table_div == None:
                    table_div = info.find("div", class_="switcher_content")
        date_elements = [element.text for element in
                         table_div.find_all("th", {"class": "left", "data-stat": date_id})]
        if date_elements == []:
            date_elements = [element.text for element in table_div.find_all("th", {"class": "left", "data-stat": "season"})]
        th_elements = [element.text for element in table_div.find_all("th", class_="poptip")]
        td_elements = [element.text for element in table_div.find_all("td")]
        th_elements.pop(0)
        chunked = [td_elements[i:i + len(th_elements)] for i in range(0, len(td_elements), len(th_elements))]
        result = {date: dict(zip(th_elements, data)) for date, data in zip(date_elements, chunked)}
        return result

    def team_table_parser(self, div_id, allc=False):
        info = self.global_page
        if allc:
            href_value = info.find_all("div", class_="filter")[0].find("a", {"href": True}).get("href")
            table_div = BeautifulSoup(
                requests.get(f'http://www.basketball-reference.com{href_value}', headers=self.headers,
                             proxies=self.proxy_to_use).text.replace("<!--", " "), "html.parser").find(
                "div", {"id": div_id})
        else:
            table_div = info.find("div", {"id": div_id})
        date_elements = [element.text for element in table_div.find_all("th", {"scope": "row"})]
        th_elements = [element.text for element in table_div.find_all("th", {"class": "poptip"})]
        td_elements = [element.text for element in table_div.find_all("td")]
        th_elements.pop(0)
        chunked = [td_elements[i:i + len(th_elements)] for i in range(0, len(td_elements), len(th_elements))]
        result = {date: dict(zip(th_elements, data)) for date, data in zip(date_elements, chunked)}
        return result

    def team_info(self, international=False):
        self.data_list = []
        team_dict = {}
        second= []
        info = BeautifulSoup(self.content.text, 'html.parser')
        if international:
            teams_page = self.global_page
            return ''.join(teams_page.find("div", {"data-template" :"Partials/Teams/Summary"}).find_all(text=True, recursive=True)).replace("\n", "")
        else:
            teams_page = BeautifulSoup(
                requests.get(
                    f'http://www.basketball-reference.com{info.find("div", id="teams").find("div", class_="search-item-name").find("a", href=True).get("href")}',
                    headers=self.headers, proxies=self.proxy_to_use).text.replace("<!--", " "), "html.parser")
        for uk in teams_page.find("div", {"id": "meta"}).find("div", class_=False).find_all("strong"):
            self.data_list.append(uk.get_text().replace("\n", "").replace(":", ""))
        for tk in teams_page.find("div", {"id": "meta"}).find("div", class_=False).find_all("p"):
            second.append(''.join(tk.find_all(text=True, recursive=False)).replace("\n", ""))
       #print(self.data_list, second)
        return json.dumps(dict(zip(self.data_list, second)))

    def player_info(self):
        self.data_list = []
        team_dict = {}
        second= []
        info = BeautifulSoup(self.content.text, 'html.parser')
        teams_page = BeautifulSoup(
            requests.get(
                f'http://www.basketball-reference.com{info.find("div", id="players").find("div", class_="search-item-name").find("a", href=True).get("href")}',
                headers=self.headers, proxies=self.proxy_to_use).text.replace("<!--", " "), "html.parser")
        for uk in teams_page.find("div", {"id": "meta"}).find("div", class_=False).find_all("strong"):
            self.data_list.append(uk.get_text().replace("\n", "").replace(":", ""))
        for tk in teams_page.find("div", {"id": "meta"}).find("div", class_=False).find_all("p"):
            second.append(''.join(tk.find_all(text=True, recursive=False)).replace("\n", ""))
        return json.dumps(dict(zip(self.data_list, second)))

    def parse_all(self, teams=False):
        info = BeautifulSoup((self.content.text), 'html.parser')
        if info.find('div', id="inpage_nav") is None:
            info = self.global_page
        if self.data_list != []:
            self.data_list = []
        if teams:
            for t in self.global_page.find_all(class_="table_container tabbed current"):
                self.data_list.append(self.team_table_parser(t.get("id")))
            return self.data_list
        else:
            for t in info.find_all(class_="table_container tabbed current"):
                self.data_list.append(self.table_parser(t.get("id")))
            return self.data_list

    def parse_little(self, teams=False):
        kombali = []
        check = None
        if teams:
            #print(self.global_page.find_all("div", id=True))
            for els in self.global_page.find_all("div", id=True):
                if "per_game" in els.get("id") or ("ELG" in els.get("id") or "ECP" in els.get("id")):
                    check = els.get("id")
            #print(check)
            kombali.append(self.team_table_parser(check))
        else:
            kombali.append(self.table_parser("div_last5"))
            #kombali.append(self.table_parser("div_last5"))
        return kombali

    def find_closest_match(self, user_input, output):
        normalized_input = user_input.replace('+', ' ').lower()

        closest_match = None
        min_distance = float('inf')

        # Iterate through the output dictionary
        for key, value in output.items():
            # Normalize the value
            normalized_value = value.replace('+', ' ').lower()

            # Check for exact match
            if normalized_input == normalized_value:
                return key

            # Calculate the Levenshtein distance for partial matches
            distance = self.levenshtein_distance(normalized_input, normalized_value)
            if distance < min_distance:
                min_distance = distance
                closest_match = key

        return closest_match

    def levenshtein_distance(self, s1, s2):
        if len(s1) < len(s2):
            return self.levenshtein_distance(s2, s1)

        # Initialize matrix of zeros
        distance_matrix = [[0 for _ in range(len(s2) + 1)] for _ in range(len(s1) + 1)]

        # Populate the matrix
        for i in range(1, len(s1) + 1):
            distance_matrix[i][0] = i
        for j in range(1, len(s2) + 1):
            distance_matrix[0][j] = j

        for i in range(1, len(s1) + 1):
            for j in range(1, len(s2) + 1):
                cost = 0 if s1[i - 1] == s2[j - 1] else 1
                distance_matrix[i][j] = min(distance_matrix[i - 1][j] + 1,
                                            distance_matrix[i][j - 1] + 1,
                                            distance_matrix[i - 1][j - 1] + cost)

        return distance_matrix[len(s1)][len(s2)]

    def names(self, teams=False, not_all=False):
        global teams_page
        info = BeautifulSoup(self.content.text, 'html.parser')
        names = []
        output = self.dict_parser("div_elg_standings")
        
        names = ["Per game"]
        profile = ""
        if teams:
            # Call find_closest_match with only user_input and output as arguments
            closest_match_key = self.find_closest_match(self.user_input, output)
            if closest_match_key:
                self.global_page = BeautifulSoup(
                requests.get(f"http://www.basketball-reference.com/international/teams/{closest_match_key}/{datetime.now().year}.html",
                    headers=self.headers, proxies=self.proxy_to_use).text.replace("<!--", " "), "html.parser")
                profile = self.team_info(True)
                if self.global_page == None:
                    self.global_page = BeautifulSoup(requests.get(f"http://www.basketball-reference.com/international/teams/{closest_match_key}/2024.html", headers=self.headers, proxies=self.proxy_to_use).text.replace("<!--", " "), "html.parser")
                profile = self.team_info(True)    
            else:    
                self.uri = info.find("div", id="teams").find("div", class_="search-item-name").find("a", href=True).get("href")
                self.global_page = BeautifulSoup(
                    requests.get(f"http://www.basketball-reference.com{self.uri}{datetime.now().year}.html",
                        headers=self.headers, proxies=self.proxy_to_use).text.replace("<!--", " "), "html.parser")
        else:
            if info.find('div', id="LAL_sh") is None:
                self.global_page = BeautifulSoup(
                    requests.get(
                        f'http://www.basketball-reference.com{info.find("div", id="players").find("div", class_="search-item-name").find("a", href=True).get("href")}',
                        headers=self.headers, proxies=self.proxy_to_use).text.replace("<!--", " "), "html.parser")
                if self.global_page is None:
                    return "Not Found"
                names_list = self.global_page.find('div', id="inpage_nav").find_all("li")
            else:
                names_list = info.find('div', id="inpage_nav").find_all("li")
                broken_list.append(self.user_input)
            for k in names_list:
                names.append(
                    k.text)
        if not_all:
            return json.dumps({"Live information": dict(zip(names, self.parse_little(teams))), "Profile": (profile.replace('\\n', ""))})
        return json.dumps(dict(zip(names, self.parse_all(teams))))

basketball_teams = [
    #NBA Teams
    "Boston Celtics",
    "Golden State Warriors",
    "Milwaukee Bucks",
    "Los Angeles Clippers",
    "Toronto Raptors",

    #EuroLeague Teams (current season)
    "Anadolu Efes Istanbul",
    "Olympiacos Piraeus",
    "ASVEL Lyon-Villeurbanne",
    "ALBA Berlin",
    "Real Madrid",

    # EuroCup Teams (current season)
    "Virtus Segafredo Bologna",
    "Valencia Basket",
    "Lietkabelis Panevezys",
    "Galatasaray Nef",
    "Unicaja Malaga",
]


if __name__ == "__main__":
    scraper = FootballerScraper('Anadolu Efes Istanbul')
    results = scraper.names(True,True)
    print(results)