import requests
from bs4 import BeautifulSoup, Comment
import json
from fake_useragent import UserAgent
import time
from unidecode import unidecode
from datetime import datetime
from fuzzywuzzy import process
import pprint




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
            "Cookie": "asdasj udv u %00ejjee"
        }
        # Get content from the initial search page
        self.content  = requests.get(f"http://www.basketball-reference.com/search/search.fcgi?&search={self.user_input}", headers=self.headers, proxies=self.proxy_to_use)
        self.url = f'https://www.transfermarkt.com/schnellsuche/ergebnis/schnellsuche?query={user_input}'
        self.data_list = []
        self.global_page = None
        self.international_team = False

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

    def divide_list(self, lst, num_divisions):
        divided_lists = [[] for _ in range(num_divisions)]

        for index, value in enumerate(lst):
            sublist_index = index % num_divisions
            divided_lists[sublist_index].append(float(value))

        return divided_lists

    def statistics(self):
        sublists = []
        data_tips = []
        titles = {}
        values = []
        info = BeautifulSoup(self.content.text, "html.parser")           
        player_page = BeautifulSoup(requests.get(f'http://www.basketball-reference.com{info.find("div", id="players").find("div", class_="search-item-name").find("a", href=True).get("href")}',headers=self.headers, proxies=self.proxy_to_use).text.replace("<!--", " "), "html.parser")
        #Get episodes
        statistics_div = player_page.find("div", class_="stats_pullout")
        episodes = statistics_div.find("div", attrs=False).find("div", attrs=False).find_all('p', recursive=False)
        episodes = [p.find('strong') for p in episodes]        
        for strong_tag in episodes:
            if strong_tag:
                titles[strong_tag.get_text()] = ""
        # Get episodes
        #Get data-tips
        for sections in statistics_div.find_all("div", class_=True):
            [values.append(p.get_text()) for p in sections.find_all("p")]
            for data_tip_elements in sections.find_all("span"):
                data_tips.append(data_tip_elements.get("data-tip"))
        #Get data-tips                
        for key in titles:
            titles[key] = data_tips
        # Get Values
        for lists in self.divide_list(values, len(titles)):
            sublists.append(list(zip(data_tips, lists)))
        #print(len(dict))
        titles.update(zip(titles.keys(), sublists))
        return json.dumps(titles)

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
        print(div_id)
        if allc:
            if self.international_team:
                table_div = self.global_page.find("div", {"id": div_id})
            else:
                table_div = self.global_page.find("div", {"id" :div_id})
        else:
            table_div = self.global_page.find("div", {"id": div_id})
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
        info = self.global_page
        per_game_id = "per_game"
        if teams:
            if self.international_team:
                self.global_page = BeautifulSoup(requests.get(f'{self.international_url.replace("teams", "schedules")}', headers=self.headers, proxies=self.proxy_to_use).text, "html.parser")
                for els in self.global_page.find_all("div", id=True):
                    if f"div_{self.closest_match_key}" in els.get("id"):
                        check = els.get("id")
                kombali.append(self.team_table_parser(check))
            else:
                self.global_page = BeautifulSoup(requests.get(f"http://www.basketball-reference.com{self.uri}{datetime.now().year}_games.html", headers=self.headers, proxies=self.proxy_to_use).text, "html.parser")
                for els in self.global_page.find_all("div", id="div_games"):
                    check = els.get("id")
                kombali.append(self.team_table_parser(check))
            if self.international_team:
                per_game_id = "div_player-stats-per_game"
            self.global_page = info
            for els in info.find_all("div", id=True):
                if per_game_id in els.get("id"):
                    check = els.get("id")
            kombali.append(self.team_table_parser(check))
        else:
            kombali.append(self.table_parser("div_last5"))
            #kombali.append(self.table_parser("div_last5"))
        return kombali

    # def find_closest_match(self, user_input, output, threshold=5):
    #         # Normalize the user input
    #         normalized_input = user_input.replace('+', ' ').lower()

    #         closest_match = None
    #         min_distance = float('inf')

    #         # Iterate through the output dictionary
    #         for key, value in output.items():
    #             # Normalize the value
    #             normalized_value = value.replace('+', ' ').lower()

    #             # Check for exact match
    #             if normalized_input == normalized_value:
    #                 return key

    #             # Calculate the Levenshtein distance for partial matches
    #             distance = self.levenshtein_distance(normalized_input, normalized_value)
    #             if distance < min_distance:
    #                 min_distance = distance
    #                 closest_match = key

    #         # Check if the closest match is within the acceptable threshold
    #         if min_distance <= threshold:
    #             return closest_match
    #         else:
    #             return None
    def find_closest_match(self, user_input, database_teams):
        # Create a list of tuples containing team names and their similarity scores
        matches = process.extract(user_input, database_teams, limit=len(database_teams))

        # Filter matches based on a threshold (adjust as needed)
        threshold = 70
        filtered_matches = [match for match in matches if match[1] >= threshold]

        if not filtered_matches:
            return None  # No close matches found

        # Return the team with the highest similarity score
        best_match = max(filtered_matches, key=lambda x: x[1])
        return best_match[0]

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
        names = ["Regular season", "Per Game"]
        profile = ""
        if teams:
            # Call find_closest_match with only user_input and output as arguments
            self.closest_match_key =  next((key for key, val in output.items() if val == self.find_closest_match(self.user_input, list(output.values()))), None)
            if self.closest_match_key:
                self.international_url = f"http://www.basketball-reference.com/international/teams/{self.closest_match_key}/{datetime.now().year}.html"
                self.global_page = BeautifulSoup(
                requests.get(self.international_url,
                    headers=self.headers, proxies=self.proxy_to_use).text.replace("<!--", " "), "html.parser")
                profile = ""#self.team_info(True)
                if self.global_page == None:
                    print("koka")
                    self.global_page = BeautifulSoup(requests.get(f"http://www.basketball-reference.com/international/teams/{self.closest_match_key}/2024.html", headers=self.headers, proxies=self.proxy_to_use).text.replace("<!--", " "), "html.parser")
                profile = ""#self.team_info(True) 
                self.international_team = True   
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
basketball_players= [
    "Payton Pritchard",
    "Sam Hauser",
    "Jaylen Brown",
    "Jayson Tatum",
    "Derrick White",
    "Jrue Holiday",
    "Al Horford",
    "Kristaps Porziņģis",
    "Luke Kornet",
    "Oshae Brissett",
    "aniel Hackett",
    "Devontae Cacok",
    "Gabriel Lundberg",
    "Isaïa Cordinier",
    "Jaleen Smith",
    "Jordan Mickey",
    "Marco Belinelli",
    "Ognjen Dobrić",
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
    # ... (add more players as needed)
]



if __name__ == "__main__":
    for hu in basketball_players:
        retry_count = 0
        while retry_count < 2:
            try:
                scraper = FootballerScraper(hu)
                results = scraper.names(False,True)
                if isinstance(results, list):
                    retry_count += 1
                    print(f"Retrying {hu} - Retry count: {retry_count}")
                    time.sleep(10)
                    continue
                else:
                    print(f"{results} \n {hu}")
            except Exception as e:
                retry_count += 1
                print(f"Retrying {hu} - Retry count: {retry_count}\n")
                time.sleep(10)
                continue
            break
        else:
            print(f"Not Found")    
