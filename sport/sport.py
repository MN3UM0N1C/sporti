import requests
from bs4 import BeautifulSoup, Comment
import json
from fake_useragent import UserAgent
import time


class FootballerScraper:
    def __init__(self, user_input):
        self.user_input = user_input.replace(" ", "+")
        self.proxy_to_use = {"http": "http://customer-Football:FootballPassword_123@pr.oxylabs.io:7777"}
        self.headers = {
            'User-Agent': UserAgent().random,
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": "https://www.google.com/",
            "DNT": "1",
            "X-Forwarded-For" : "127.0.0.1",
            "Cookie" : "aaaaaaaaaaaaa"
        }
        self.content = requests.get(f"http://fbref.com/en/search/search.fcgi?random=0&search={self.user_input}&amp;i=clubs", headers=self.headers, proxies = self.proxy_to_use)
        self.url = f'https://www.transfermarkt.com/schnellsuche/ergebnis/schnellsuche?query={user_input}'
        self.data_list = []
        self.data_dict = {}

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
        try:
            rewards_list = []
            rewards_dict = {"rewards" : ""}
            soup = BeautifulSoup((self.content.text), 'html.parser')
            for j in soup.find_all("li", {"class" : "important poptip"}):
                rewards_list.append(j.get_text())
            rewards_dict["rewards"] = rewards_list
            return json.dumps(rewards_dict)
        except:
            return f"Request failed with status code: {page.status_code}"

    def footballer_info(self, url):
        div_block = []
        classname = "info-table info-table--right-space min-height-audio"
        page = requests.get(url, headers=self.headers, proxies=self.proxy_to_use)
        info = BeautifulSoup(page.text, 'html.parser')
        try:
            div_block = info.find("div", class_=classname).find_all("span")
        except AttributeError:
            try:
                div_block = info.find("div", class_=("info-table info-table--right-space")).find_all("span")
            except:
                return "footbaler not found"
        for i in div_block:
            self.data_list.append(i.text)
        return json.dumps(self.dictifier(self.data_list))

    def search(self):
        response = requests.get(self.url, headers=self.headers, proxies=self.proxy_to_use)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            td_elements = soup.find_all('td', class_="hauptlink")
            try:
                fb_url = "https://www.transfermarkt.com" + td_elements[0].find("a").get("href")
                return self.footballer_info(fb_url)
            except IndexError:
                return "Footballer not found"
        else:
            return f"Request failed with status code: {response.status_code}"

    def statistics(self):
        statistics = {"MP": "", "min": "", "goals":"","assists": ""}
        nums = []
        classname = "tm-player-performance__stats-list-item-value svelte-xwa5ea"
        page = BeautifulSoup((self.content.text), 'html.parser')
        info = BeautifulSoup(page.text, 'html.parser')
        try:
            for stats in info.find('div', {'class': 'p1'}).find_all("p"):
                nums.append(stats.get_text())
            for key in statistics:
                statistics[key] = nums.pop(0)  
            return json.dumps(statistics)  
        except AttributeError:
            for i in div_block:
                self.data_list.append(i.text)
            return self.dictifier(self.data_list)

    def table_parser(self, div_id, allc=False):
        info = BeautifulSoup(self.content.text, 'html.parser')
        date_id = "year_id"
        if allc == True:
            date_id = "date"
            info = BeautifulSoup(requests.get(f'http://fbref.com{info.find("div", class_="filter").find("a", href=True).get("href")}' ,headers=self.headers, proxies = self.proxy_to_use).text, "html.parser")
        table_div = info.find("div", {"id": div_id})
        try:
            date_elements = [element.text for element in table_div.find_all("th", {"class" : "left", "data-stat" : date_id})]
        except AttributeError:
            date_elements = []
        th_elements = [element.text for element in table_div.find_all("th", class_="poptip")]
        td_elements = [element.text for element in table_div.find_all("td")]
        th_elements.pop(0)
        chunked = [td_elements[i:i + len(th_elements)] for i in range(0, len(td_elements), len(th_elements))]
        result = {date: dict(zip(th_elements, data)) for date, data in zip(date_elements, chunked)}    
        return result

    def team_table_parser(self, div_id, allc=False):
        info = BeautifulSoup(self.content.text, 'html.parser')
        if allc == True:
            page = requests.get(f'http://fbref.com/{teams_page.find("div", class_="filter").find("a", href=True).get("href")}' ,headers=self.headers, proxies = self.proxy_to_use).text.replace("<!--", " ")
            table_div = BeautifulSoup(page, "html.parser").find("div", {"id": div_id})
        else:
            table_div = teams_page.find("div", {"id": div_id})
        date_elements = [element.text for element in table_div.find_all("th", {"scope" : "row"})]
        th_elements = [element.text for element in table_div.find_all("th", {"class" : "poptip"})]
        td_elements = [element.text for element in table_div.find_all("td")]
        th_elements.pop(0)
        chunked = [td_elements[i:i + len(th_elements)] for i in range(0, len(td_elements), len(th_elements))]
        result = {date: dict(zip(th_elements, data)) for date, data in zip(date_elements, chunked)} 
        return result

    def team_info(self):
        self.data_list = []
        team_dict = {}
        info = info = BeautifulSoup(self.content.text, 'html.parser')
        teams_page = BeautifulSoup(requests.get(f'http://fbref.com/{info.find("div", class_="search-item-name").find("a", href=True).get("href")}' ,headers=self.headers, proxies = self.proxy_to_use).text, "lxml")
        for uk in teams_page.find("div", {"data-template" : "Partials/Teams/Summary"}).get_text().split("\n"):
            self.data_list.append(uk)
        team_dict["Team Info"] = self.data_list
        return json.dumps(team_dict)
        self.data_list = []



    def parse_all(self, teams=False):
        if self.data_list != []:
            self.data_list = []
        info = BeautifulSoup((self.content.text), 'html.parser')
        if teams == True:
            for t in teams_page.find_all(class_="table_container tabbed current"):
                self.data_list.append(self.team_table_parser(t.get("id")))
            return self.data_list
        else:
            for t in info.find_all(class_="table_container tabbed current"):
                self.data_list.append(self.table_parser(t.get("id")))         
            return self.data_list


    def parse_little(self, teams=False):
        kombali = []
        if teams:
            kombali.append(self.team_table_parser("div_matchlogs_for"))
            kombali.append(self.team_table_parser("all_stats_player_summary", True))
        else:
            kombali.append(self.table_parser("div_stats_standard_dom_lg"))
            kombali.append(self.table_parser("div_last_5_matchlogs", True))
        return kombali

    def names(self, teams=False, not_all=False):
        global teams_page
        info = BeautifulSoup(self.content.text, 'html.parser')
        names = []
        if teams:
            teams_page = BeautifulSoup(requests.get(f'http://fbref.com{info.find("div", id="clubs").find("div", class_="search-item-name").find("a", href=True).get("href")}' ,headers=self.headers, proxies = self.proxy_to_use).text.replace("<!--", " "), "html.parser")
            print(requests.get(f'http://fbref.com{info.find("div", class_="search-item-name").find("a", href=True).get("href")}' ,headers=self.headers, proxies = self.proxy_to_use).url)
            names_list = teams_page.find('div', id="inpage_nav").find_all("li")
        else:
            names_list = info.find('div', id="inpage_nav").find_all("li")
        for k in names_list:
            names.append(k.text)
        del names[-2:]
        if not_all:
            return json.dumps(dict(zip(names, self.parse_little(teams))))
        return json.dumps(dict(zip(names, self.parse_all(teams))))
        names = []


if __name__ == "__main__":
    user_input = "napoli"
    scraper = FootballerScraper(user_input)
    print(scraper.names(True, True))
    #print(scraper.team_info())
