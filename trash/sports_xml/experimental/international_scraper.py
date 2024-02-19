from bs4 import BeautifulSoup


url = "https://www.basketball-reference.com"
headers = {
            'User-Agent': UserAgent().random,
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": "https://www.google.com/",
            "DNT": "1",
            "X-Forwarded-For": "127.0.0.1",
            "Cookie": "asdasj ejjee"
        }
proxy_to_use = {"http": "http://customer-Football:FootballPassword_123@pr.oxylabs.io:7777"}
info = BeautifulSoup(requests.get(url, headers=headers, proxies=proxy_to_use)).find("table", {"id", "elg_standings"}).find_all("a", href_=True).get("href")


