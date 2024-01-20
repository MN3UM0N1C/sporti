from bs4 import BeautifulSoup
import json
import requests
from fake_headers import Headers

headers = Headers()

class StakeScraper():
    def __init__(self):
        self.match_list_url = "http://stake.com/sports/soccer"
        self.headers =  {
        'Host': 'stake.com',
        'Cookie': '__cf_bm=yGpWaB5YG600.kWug3OUgofEs1mUTraafJD6Vymsy.c-1705586710-1-AWl1Iw5UeRTwaToYHkr79QttvTMuopKp5cl4xmFEDrM6k8LofIyykEJCmlFnFKzgjVxr1LSbtB1PGgCEy8q+FjA=; cf_clearance=7Ps3rULab_5cWXaZOKciWBBw73d0o7UIKaULk3N7ux0-1705586715-1-ARrqe/415gpxD9NzCjlFDJ9XYgYf4azGwV05Dkgx9MmoEi8wKiuveAYE0KIQpyEZfz8mrATU6B8wgfbeqoKc1Mw=; currency_currency=btc; currency_hideZeroBalances=false; currency_currencyView=crypto; currency_bankingCurrencies=[]; session_info=undefined; fiat_number_format=en; cookie_consent=false; leftSidebarView_v2=expanded; sidebarView=hidden; casinoSearch=["Monopoly","Crazy Time","Sweet Bonanza","Money Train","Reactoonz"]; sportsSearch=["Liverpool FC","Kansas City Chiefs","Los Angeles Lakers","FC Barcelona","FC Bayern Munich"]; sportMarketGroupMap={}; oddsFormat=decimal; locale=en; mp_e29e8d653fb046aa5a7d7b151ecf6f99_mixpanel=%7B%22distinct_id%22%3A%20%22%24device%3A18d1ce4032d2944-0be52ee14f4b428-47380724-1fa400-18d1ce4032d2945%22%2C%22%24device_id%22%3A%20%2218d1ce4032d2944-0be52ee14f4b428-47380724-1fa400-18d1ce4032d2945%22%2C%22%24initial_referrer%22%3A%20%22%24direct%22%2C%22%24initial_referring_domain%22%3A%20%22%24direct%22%7D; _ga=GA1.2.911911304.1705586729; _gid=GA1.2.721321414.1705586729; _ga_TWGX3QNXGG=GS1.1.1705586729.1.1.1705587283.0.0.0; intercom-id-cx1ywgf2=119d43e1-ce04-4ba2-a4dc-57540ff57805; intercom-session-cx1ywgf2=; intercom-device-id-cx1ywgf2=07c8e9cf-1831-47ca-a1bd-2034992de1dc',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Te': 'trailers'
        }


    def get_matches(self):
        links = []
        match_page = BeautifulSoup(requests.get(self.match_list_url, headers=self.headers, allow_redirects=True).text, 'html.parser')
        matches = match_page.find_all("a", class_="link variant-link size-md align-left svelte-14e5301")
        for match in matches:
            links.append(f'{self.match_list_url}{match.get("href")}')
        return links

    def parse_all_matches(self):
        results = []
        for link in self.get_matches():
            parser = BeautifulSoup(requests.get(link, headers=self.headers).text, "html.parser")
            results.append(self.html_to_json(parser.find("div", class_="groups svelte-1xk80tl")))
        return results


    def extract_odds_data(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        odds_data = {}

        # Find all elements with class 'outcome'
        outcome_elements = soup.find_all('button', {'class': 'outcome'})

        for outcome in outcome_elements:
            # Extract team/country name
            team_name = outcome.find('span', {'class': 'name'}).text.strip()

            # Extract odds value
            odds_value = outcome.find('span', {'class': 'weight-bold'}).text.strip()

            # Add team name and odds value to the dictionary
            odds_data[team_name] = float(odds_value)

        return odds_data

    def html_to_json(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        json_data = {}

        # Find all div elements with class 'secondary-accordion'
        accordion_elements = soup.find_all('div', {'class': 'secondary-accordion'})

        for index, accordion in enumerate(accordion_elements):
            # Extract the market name
            market_name = accordion.find('span', {'class': 'weight-semibold'}).text.strip()

            # Extract odds data using the previously defined function
            odds_data = self.extract_odds_data(str(accordion))

            # Add market name and odds data to the dictionary
            json_data[f'market_{index + 1}_{market_name}'] = odds_data

        return json.dumps(json_data, indent=2)



scraper = StakeScraper()
result_json = scraper.parse_all_matches()
print(result_json)






# link variant-link size-md align-left svelte-14e5301
# link variant-link size-md align-left svelte-14e5301
# link variant-link size-md align-left svelte-14e5301
