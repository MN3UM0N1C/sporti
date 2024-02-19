from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import requests
import time


dictionary = {}
url = "http://www.basketball-reference.com"
headers = {
            'User-Agent': UserAgent().random,
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": "https://www.google.com/",
            "DNT": "1",
            "X-Forwarded-For": "127.0.0.1",
            "Cookie": "asdasj ejjee"
        }
proxy_to_use = {"http": "http://customer-Football:FootballPassword_123@pr.oxylabs.io:7777"}
page_content = requests.get("http://www.basketball-reference.com", headers=headers, proxies=proxy_to_use).text
main_page = BeautifulSoup(page_content, "html.parser").find("div", id="all_elg_standings").find_all("a")
#main_page.append(BeautifulSoup(page_content, "html.parser").find("div", id="div_ecp_standings").find_all("a"))
print(main_page)
for i in main_page:
	dictionary[i.get("href").split("/")[3]] = i.get_text()
print(dictionary)

