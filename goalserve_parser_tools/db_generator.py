# from goalserve_odds_parser import Searcher
# import os
# from bs4 import BeautifulSoup

# class MatchParser:
# 	def __init__(self, root_folder):
# 	    self.root_folder = root_folder

# 	def find_xml_files(self):
# 		xml_files = []
# 		for root, dirs, files in os.walk(self.root_folder):
# 			for file in files:
# 				if "old" not in root:
# 					if file.endswith(".xml"):
# 						xml_files.append(os.path.join(root, file))
# 		return xml_files

# 	def parse_matches(self, xml_file):
# 		with open(xml_file, 'r') as f:
# 			xml_data = f.read()
# 		soup = BeautifulSoup(xml_data, 'xml')
# 		matches_data = []
# 		sport = soup.find("scores")["sport"]
# 		if sport == "soccer":
# 			sport = "football"
# 		league = xml_file.split("/")[-1].split(".")[0]
# 		for match in soup.find_all('match'):
# 			localteam_name = match.localteam['name']
# 			if match.awayteam != None:
# 				awayteam_name = match.awayteam['name']
# 			else:
# 				awayteam_name = match.visitorteam['name']
# 			if sport == "football" or sport == "basketball":
# 				searcher = Searcher(sport, localteam_name, awayteam_name, league=league)
# 			else: 
# 				searcher = Searcher(sport, localteam_name, awayteam_name)
# 			try:
# 				date = match["formatted_date"]
# 			except:
# 				date = match['date']
# 			matches_data.append([localteam_name, awayteam_name, date, searcher.search()])
# 		return matches_data

# 	def process_xml_files(self):
# 	    xml_files = self.find_xml_files()
# 	    all_matches = []

# 	    for xml_file in xml_files:
# 	        matches = self.parse_matches(xml_file)
# 	        all_matches.extend(matches)

# 	    return all_matches


# if __name__ == "__main__":
#     root_folder = "app/odds/"
#     parser = MatchParser(root_folder)
#     all_matches = parser.process_xml_files()

#     for match in all_matches:
#         print(match)



# from goalserve_odds_parser import Searcher
# import os
# from bs4 import BeautifulSoup
# import pymongo
# import json

# class MatchParser:
#     def __init__(self, root_folder):
#         self.root_folder = root_folder
#         self.client = pymongo.MongoClient("mongodb://localhost:27017/")
#         self.db = self.client["mydatabase"]
#         self.collection = self.db["matches"]

#     def find_xml_files(self):
#         xml_files = []
#         for root, dirs, files in os.walk(self.root_folder):
#             for file in files:
#                 if "old" not in root:
#                     if file.endswith(".xml"):
#                         xml_files.append(os.path.join(root, file))
#         return xml_files

#     def parse_matches(self, xml_file):
#         with open(xml_file, 'r') as f:
#             xml_data = f.read()
#         soup = BeautifulSoup(xml_data, 'xml')
#         matches_data = []
#         sport = soup.find("scores")["sport"]
#         if sport == "soccer":
#             sport = "football"
#         league = xml_file.split("/")[-1].split(".")[0]
#         for match in soup.find_all('match'):
#             localteam_name = match.localteam['name']
#             if match.awayteam != None:
#                 awayteam_name = match.awayteam['name']
#             else:
#                 awayteam_name = match.visitorteam['name']
#             if sport == "football" or sport == "basketball":
#                 searcher = Searcher(sport, localteam_name, awayteam_name, league=league)
#             else: 
#                 searcher = Searcher(sport, localteam_name, awayteam_name)
#             try:
#                 date = match["formatted_date"]
#             except:
#                 date = match['date']
#             matches_data.append([localteam_name, awayteam_name, date, searcher.search()])
#         return matches_data

#     def process_xml_files(self):
#         xml_files = self.find_xml_files()
#         all_matches = []

#         for xml_file in xml_files:
#             matches = self.parse_matches(xml_file)
#             all_matches.extend(matches)

#         return all_matches

#     def save_matches_to_mongodb(self):
#         all_matches = self.process_xml_files()

#         for match in all_matches:
#             team1, team2, date, json_data = match
            
#             # Convert JSON data string to dictionary
#             match_data_dict = json.loads(json_data)
            
#             # Insert into MongoDB collection
#             match_document = {
#                 "team1": team1,
#                 "team2": team2,
#                 "date": date,
#                 "data": match_data_dict
#             }
#             self.collection.insert_one(match_document)

#         print("Matches data inserted into MongoDB collection.")


# if __name__ == "__main__":
#     root_folder = "app/odds/"
#     parser = MatchParser(root_folder)
#     parser.save_matches_to_mongodb()



from goalserve_odds_parser import Searcher
import os
from bs4 import BeautifulSoup
import pymongo
import json

class MatchParser:
    def __init__(self, root_folder, connection_string):
        self.root_folder = root_folder
        self.client = pymongo.MongoClient(connection_string)
        self.db = self.client["mydatabase"]
        self.collection = self.db["matches"]

    def find_xml_files(self):
        xml_files = []
        for root, dirs, files in os.walk(self.root_folder):
            for file in files:
                if "old" not in root:
                    if file.endswith(".xml"):
                        xml_files.append(os.path.join(root, file))
        return xml_files

    def parse_matches(self, xml_file):
        with open(xml_file, 'r') as f:
            xml_data = f.read()
        soup = BeautifulSoup(xml_data, 'xml')
        matches_data = []
        sport = soup.find("scores")["sport"]
        if sport == "soccer":
            sport = "football"
        league = xml_file.split("/")[-1].split(".")[0]
        for match in soup.find_all('match'):
            localteam_name = match.localteam['name']
            if match.awayteam != None:
                awayteam_name = match.awayteam['name']
            else:
                awayteam_name = match.visitorteam['name']
            if sport == "football" or sport == "basketball":
                searcher = Searcher(sport, localteam_name, awayteam_name, league=league)
            else: 
                searcher = Searcher(sport, localteam_name, awayteam_name)
            try:
                date = match["formatted_date"]
            except:
                date = match['date']
            matches_data.append([localteam_name, awayteam_name, date, league, sport ,searcher.search()])
        return matches_data

    def process_xml_files(self):
        xml_files = self.find_xml_files()
        all_matches = []

        for xml_file in xml_files:
            matches = self.parse_matches(xml_file)
            all_matches.extend(matches)

        return all_matches

    def save_matches_to_mongodb(self):
        all_matches = self.process_xml_files()
        for match in all_matches:
            team1, team2, date, league, sport, json_data = match
            print(league)
            
            # Convert JSON data string to dictionary
            match_data_dict = json.loads(json_data)
            
            # Insert into MongoDB collection
            match_document = {
                "team1": team1,
                "team2": team2,
                "date": date,
                "league" : league,
                "data": match_data_dict,
            }
            self.db[sport].insert_one(match_document)

        print("Matches data inserted into MongoDB collection.")
        self.client.close()


if __name__ == "__main__":
    root_folder = "app/odds/"
    # Replace 'your_connection_string' with the actual connection string from MongoDB Atlas
    connection_string = "mongodb+srv://matches_20:chatftw.matches@cluster0.cbhrt8b.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    parser = MatchParser(root_folder, connection_string)
    parser.save_matches_to_mongodb()
