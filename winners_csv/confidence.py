import csv
from openai import OpenAI
import json

client = OpenAI(api_key="token")

def parse_csv_file(filename):
    data = []
    try:
        with open(filename, newline='', encoding='utf-8') as csvfile:
            csv_reader = csv.reader(csvfile)
            for row in csv_reader:
                # Assuming the structure is "fighter_1","fighter_2","prediction"
                if len(row) == 3:  # Ensure there are three elements in each row
                    data.append(tuple(row))
                else:
                    print(f"Ignoring malformed row: {row}")
    except Exception as e:
        print(f"Error occurred while parsing CSV file: {e}")
    return data

def analyze_sentiment(user_input):
    try:
        completion = client.chat.completions.create(model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a confidence analyzer, skilled in analyzing sport prediction and diagnosing confidence value of it, response should be in percentage, not any other discussion or string, one from this 5: 10%, 30%, 50%, 70%, 100%. percantage is your diagnosed accuracy confidence from inputted prediction string"},
            {"role": "user", "content": user_input}
        ])
        sentiment = completion.choices[0].message.content
        return sentiment
    except Exception as e:
        print(f"Error occurred while analyzing sentiment: {e}")

def extract_odds_values(prediction_string):
    try:
        completion = client.chat.completions.create(model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": """Please extract bookmaker odds values and fair odds values from the prediction string. and return them in json format only no strings, only ones that has market of Match Winners, json format should be static and fixed,    "Match Winner": {
        "Bookmaker Odds": {
            "Sheffield United": 2.10,
            "Draw": 3.30,
            "Fulham": 3.60
        },
        "Fair Odds": {
            "Sheffield United": 2.30,
            "Draw": 3.20,
            "Fulham": 3.10
        }
        this is example 
    },

            """},
            {"role": "user", "content": prediction_string}
        ])
        extracted_values = completion.choices[0].message.content
        return extracted_values
    except Exception as e:
        pass

def calculate_profitability(json_data):
    try:
        bookmaker_odds = json_data["Match Winner"]["Bookmaker Odds"]
        fair_odds = json_data["Match Winner"]["Fair Odds"]

        profitability = {}

        for outcome, numbers in bookmaker_odds.items():
            bookmaker_odds_value = bookmaker_odds[outcome]
            fair_odds_value = fair_odds[outcome]

            if bookmaker_odds_value != 0:
                profitability[outcome] = ((float("{:.2f}".format((bookmaker_odds_value))) - float("{:.2f}".format((fair_odds_value)))) / float("{:.2f}".format(((bookmaker_odds_value)))) * 100)
            else:
                profitability[outcome] = 0
        return profitability
    except Exception as e:
        pass

def main():
    data = []
    csv_filling = []
    try:
        for pred in parse_csv_file("prediction.csv")[1:]:
            try:
                sentiment = analyze_sentiment(f"Team 1: {pred[0]}, Team 2: {pred[1]}, Prediction: {pred[2]}")
                odds_values = extract_odds_values(pred[2])
                json_data = json.loads(odds_values)
                profitability = calculate_profitability(json_data)

                diff_home = profitability.get("home", 0)
                diff_away = profitability.get("away", 0)
                diff_draw = profitability.get("draw", 0)
                data = {
                    "fighter_1": pred[0],
                    "fighter_2": pred[1],
                    "diff_home": list(profitability.values())[0],
                    "diff_away": list(profitability.values())[2],
                    "diff_draw": list(profitability.values())[1]
                }
                csv_filling.append([pred[0], pred[1],sentiment,data])
                print(f"{pred[0]},{pred[1]},{sentiment},{data}")
            except:
                pass

    except Exception as e:
        pass

    try:
        with open("analyzed_prediction.csv", mode='w', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(["fighter_1", "fighter_2", "diff_home", "diff_away", "diff_draw"])
            for item in csv_filling:
                csv_writer.writerow([item[0],item[1],item[2],item[3]])

        print("Analysis completed. Data saved to 'analyzed_prediction.csv'.")
    except Exception as e:
        pass

if __name__ == '__main__':
    main()
