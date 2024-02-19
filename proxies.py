from pprint import pprint
import requests
from fake_useragent import UserAgent
from sport import FootballerScraper
import time
# Structure payload.

proxy_to_use = {"http": "http://customer-Football:FootballPassword_123@pr.oxylabs.io:7777"}
headers = {
    'User-Agent': UserAgent().random,
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": "https://www.google.com/",
    "DNT": "1",
    "X-Forwarded-For" : "127.0.0.1",
    "Cookie" : "asdasj ejjee"
}

print(requests.get(f"http://fbref.com/en/search/search.fcgi?random=013&search=cristiano+ronaldo", headers=headers, proxies = proxy_to_use).text)