import requests
import subprocess

class FootballDataDownloader:
    def __init__(self, league_id_mapping):
        self.league_id_mapping = league_id_mapping
        self.base_url = "https://www.goalserve.com/getfeed/401117231212497fb27a08db8de47c17/getodds/soccer?cat=soccer_10&League="

    def download_file(self, league_id, output_file):
        try:
            url = f"{self.base_url}{league_id}"
            subprocess.run(['curl', '-o', f"data/{output_file}", url], check=True)
            print(f"File downloaded successfully: {output_file}")
        except subprocess.CalledProcessError as e:
            print(f"Error downloading file: {e}")

    def download_all_files(self):
        for league_id, league_name in self.league_id_mapping.items():
            self.download_file(league_id, f"{league_name}.xml")


if __name__ == "__main__":
    # Example usage:
    league_id_mapping = {
        '1204': 'Premier_League',
        '1399': 'La_Liga',
        '1229': 'Bundesliga',
        '1269': 'Serie_A',
        '1221': 'Ligue_1',
        '1440': 'MLS',
        '1368': 'Saudi_League',
        '1005': 'UEFA_Champions_League',
        '1007': 'UEFA_Europa_League',
    }

    football_downloader = FootballDataDownloader(league_id_mapping)
    football_downloader.download_all_files()
