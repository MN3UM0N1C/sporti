import json
import requests
from bs4 import BeautifulSoup

class CricketStatsFormatter:
    def __init__(self, team):
        self.url1 = f"http://www.cricmetric.com/jscripts/leadersdata.py?show=Player&type=Standard&role=Batting&format=Test&category=Men&start=2023-01-01&end=2024-04-08&start_date=2023-01-01&amp;end_date=2024-04-08&&&&&playerteam={team}"
        self.url2 = f"http://www.cricmetric.com/jscripts/series_data.py?start=2023-01-01&end=2024-04-08&format=Test&start_date=2012-01-01&amp;end_date=2024-04-08&&&&&team={team}&"
        self.url3 = f"http://www.cricmetric.com/jscripts/fixture_data.py?start=2023-01-01&end=2024-04-08&rownum=false&sort=desc&start_date=2023-01-01&amp;end_date=2024-04-08&&&&&team={team}&"
        pass

    def prettify(self, ugly_json):
        # Parse the ugly JSON
        data = json.loads(ugly_json)

        # Extract columns and rows
        columns = [col['label'] for col in data['cols']]
        rows = []
        for row in data['rows']:
            formatted_row = {}
            for i, cell in enumerate(row['c']):
                # Check if 'v' key exists, otherwise use an empty string
                value = str(cell.get('v', ''))
                if "<a href" in value:
                    value = BeautifulSoup(value, 'html.parser').get_text()

                if 'f' in cell:
                    # If 'f' key exists, it contains HTML markup, so strip it
                    value = BeautifulSoup(cell['f'], 'html.parser').get_text()
                formatted_row[columns[i]] = value
            rows.append(formatted_row)

        # Create prettier JSON
        prettier_json = {
            'columns': columns,
            'rows': rows
        }
        return json.dumps(prettier_json, indent=4)

    def fetch_json_data(self, url):
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            print(f"Failed to fetch data from URL: {url}")
            return None

    def main(self):
        for url in [self.url1, self.url2, self.url3]:
            json_data = self.fetch_json_data(url)
            if json_data:
                prettified_json = self.prettify(json_data)
                print(prettified_json)
                print("\n")



# Create instance of the formatter
CricketStatsFormatter("Afghanistan").main()
