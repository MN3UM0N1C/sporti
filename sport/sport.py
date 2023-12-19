import requests
from bs4 import BeautifulSoup
import json
from fake_useragent import UserAgent
import time


class FootballerScraper:
    def __init__(self, user_input):
        self.user_input = user_input
        self.proxy_list = []
        self.proxy_to_use = {"http": "http://customer-Football:FootballPassword_123@pr.oxylabs.io:7777"}
        self.headers = {
            'User-Agent': UserAgent().random,
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": "https://www.google.com/",
            "DNT": "1",
            "X-Forwarded-For" : "127.0.0.1",
            "Cookie" : "aaaaaaaaaaaaa"


        }
        self.content = requests.get(f"http://fbref.com/en/search/search.fcgi?random=0&search={self.user_input}", headers=self.headers, proxies = self.proxy_to_use).text
        self.url = f'https://www.transfermarkt.com/schnellsuche/ergebnis/schnellsuche?query={user_input}'
        self.target = "https://www.whoscored.com/"
        self.data_list = []
        self.data_dict = {}

        self.auth = requests.auth.HTTPProxyAuth("customer-Football", "FootballPassword_123")

    def request_2(self, url):
        try:
            return requests.get(url, headers=self.headers)
        except AttributeError:
            return requests.get(url, headers=self.headers, proxies=self.proxy_to_use)




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
            page = requests.get(f"https://fbref.com/en/search/search.fcgi?hint=neymar&search={self.user_input}", headers=self.headers, proxies=self.proxy_to_use)
            soup = BeautifulSoup(page.text, 'html.parser')
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
        return self.dictifier(self.data_list)

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
        page = requests.get(f"https://fbref.com/en/search/search.fcgi?hint=neymar&search={self.user_input}", headers=self.headers, proxies=self.proxy_to_use)
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

    def table_parser(self, div_id):
        info = BeautifulSoup(self.content, 'html.parser')
        table_div = info.find("div", {"id": div_id})
        date_elements = [element.text for element in table_div.find_all("th", {"class" : "left", "data-stat" : "year_id"})]
        th_elements = [element.text for element in table_div.find_all("th", class_="poptip")]
        td_elements = [element.text for element in table_div.find_all("td")]
        th_elements.pop(0)
        chunked = [td_elements[i:i + len(th_elements)] for i in range(0, len(td_elements), len(th_elements))]
        result = {date: dict(zip(th_elements, data)) for date, data in zip(date_elements, chunked)}    
        return json.dumps(result)

    def parse_all(self):
        print(self.proxy_to_use)
        info = BeautifulSoup((self.content), 'html.parser')
        #print(requests.get(f"http://api.ipify.org/", headers=self.headers, proxies={'http': 'http://customer-Football:FootballPassword_123@pr.oxylabs.io:7777'}).text)
        for t in info.find_all(class_="table_container tabbed current"):
            self.data_list.append(self.table_parser(t.get("id")))
        return self.data_list

    def names(self):
        names = []
        content = requests.get(f"https://fbref.com/en/search/search.fcgi?&search={self.user_input}", headers=self.headers, proxies=self.proxy_to_use)
        info = BeautifulSoup(content.text, 'html.parser')
        for k in info.find("div", {"id" : "inpage_nav"}).find_all("li"):
            names.append(k.text)
        del names[-2:]
        return json.dumps(dict(zip(names, self.parse_all())))
        names = []
        self.refresh_proxy()

    def whoscored_player(self):
        counter = 0
        url = f"https://www.whoscored.com/Search/?t={self.user_input}"
        info = BeautifulSoup(self.request_2(url).text, 'html.parser')
        rows = BeautifulSoup(self.request_2(self.target + info.find("a", class_="iconize iconize-icon-left").get('href')).text, 'html.parser')
        for elements in rows.find_all("div", class_="divtable-row row12-lg row12-m row12-s row12-xs alt"):
            div_texts = [div.text for div in elements]
            counter += 1 
            self.data_dict[counter] = list(set([s.replace("\n", "").replace("\r", "") for s in div_texts]))
        print(self.data_dict)
        #print(self.data_list)


        









if __name__ == "__main__":
    user_input = "cristiano+ronaldo"
    scraper = FootballerScraper(user_input)
    #print(scraper.search())
    #print(scraper.search())
    #print(scraper.rewards())
    #print(scraper.statistics()
    print(scraper.parse_all())
    print(scraper.whoscored_player())
