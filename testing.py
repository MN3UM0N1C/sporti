import json
from fuzzywuzzy import fuzz

def data_searcher(teams, league):
    best_match = None
    best_match_score = 0
    with open('odds_data.json', 'r') as file:
        data = json.load(file)
    for element in data:
        try:
            element_league = list(element.keys())[0]
            if league.lower() == element_league.lower():
                element_teams = list(list(element.values())[0].values())[0].keys()
                total_score = 0
                for team in teams:
                    max_score = 0
                    for element_team in element_teams:
                        match_score = fuzz.partial_ratio(team.lower(), element_team.lower())
                        max_score = max(max_score, match_score)
                    total_score += max_score
                
                if total_score > best_match_score:
                    best_match_score = total_score
                    best_match = element
        except IndexError:
            continue
    return best_match

match = data_searcher(["", " west ham united"], "Premier League")
if match:
    print(match)
