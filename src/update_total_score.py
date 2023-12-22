import requests
import time, json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

class MatchStatistics:
    def __init__(self, home_team, away_team):
        self.home_team = home_team
        self.away_team = away_team
        if home_team in self.team_dict:
            self.querystring_match = {"team_id": self.team_dict[home_team]}
        elif away_team in self.team_dict:
            self.querystring_match = {"team_id": self.team_dict[away_team]}
        else:
            self.querystring_match = {}

    with open("team_dict.json", "r") as file:
        team_dict = json.load(file)

    url_endpoint = "https://sofascores.p.rapidapi.com/v1"
    url_match_suffix = "/teams/near-events"
    url_statistics_suffix = "/events/statistics"
    url_incidents_suffix = "/events/incidents"
    headers = {
        "X-RapidAPI-Key": "4262a4297emshdf95e4a21863915p1ec56bjsnbd1c62f6586a",
        "X-RapidAPI-Host": "sofascores.p.rapidapi.com"
    }

    total_goals = 0
    total_corners = 0
    total_yellow_cards = 0
    total_red_cards = 0

    def get_event_id(self):
        if len(self.querystring_match) == 0:
            Exception("No team is registered in team_dict")
        response = requests.get(self.url_endpoint + self.url_match_suffix, headers=self.headers, params=self.querystring_match)
        response = response.json()
        event_json = response['data']['previousEvent']
        event_id = int(event_json['id'])
        self.querystring_statistics = {"event_id": str(event_id)}

    def get_goals(self):
        if len(self.querystring_match) == 0:
            Exception("No team is registered in team_dict")
        response = requests.get(self.url_endpoint + self.url_match_suffix, headers=self.headers, params=self.querystring_match)
        response = response.json()
        event_json = response['data']['previousEvent']
        self.total_goals = int(event_json['homeScore']['current'] + event_json['awayScore']['current'])
        print("Total goals: " + str(self.total_goals))
    
    def get_adjusted_cards(self):
        response = requests.get(self.url_endpoint + self.url_incidents_suffix, headers=self.headers, params=self.querystring_statistics)
        response = response.json()
        self.total_yellow_cards = 0
        self.total_red_cards = 0
        if "data" in response:
            for incident in response["data"]:
                if incident["incidentType"] == "card":
                    if incident["incidentClass"] == "yellow":
                        self.total_yellow_cards += 1
                    else:
                        self.total_red_cards += 1
        print("Total yellow cards: " + str(self.total_yellow_cards))
        print("Total red cards: " + str(self.total_red_cards))


    def get_total_corners(self):
        response = requests.get(self.url_endpoint + self.url_statistics_suffix, headers=self.headers, params=self.querystring_statistics)
        response = response.json()

        # Extracting data from the response
        for group in response['data'][0]['groups']:
            if group['groupName'] == 'TVData':
                for stat in group['statisticsItems']:
                    if stat['name'] == 'Corner kicks':
                        self.total_corners = int(stat['home']) + int(stat['away'])
        print("Total corners: " + str(self.total_corners))
        
        
    def get_total_score(self):
        return self.total_goals * self.total_corners * (self.total_yellow_cards + 2 * self.total_red_cards)

def write_to_sheet(target_match, total_score):
    # Initialize the Sheets API
    SERVICE_ACCOUNT_FILE = '/Users/elanu/Documents/GCC/gcyr-408819-83b15ce5b8eb.json'
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    SPREADSHEET_ID = '1wseMtOZXNLL_fWxrTHhqApJluSYIPy8I9WVrSfMXzb0'
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('sheets', 'v4', credentials=creds)

    # Function to find a row based on a condition
    def find_row(sheet_service, sheet_id, target_value, column='B'):
        # Adjust range as necessary. Here it reads column B for all rows
        range_name = f'Foaie1!{column}1:{column}1000'
        result = sheet_service.spreadsheets().values().get(
            spreadsheetId=sheet_id, range=range_name).execute()
        values = result.get('values', [])

        for i, row in enumerate(values):
            if row and row[0] == target_value:
                return i + 1  # +1 because Sheets is 1-indexed, not 0-indexed
        return None

    # Function to update a specific cell
    def update_cell(sheet_service, sheet_id, row_number, value, column_index = 8):
        cell_name = f'Foaie1!{chr(65 + column_index)}{row_number}'
        body = {'values': [[value]]}
        result = sheet_service.spreadsheets().values().update(
            spreadsheetId=sheet_id, range=cell_name,
            valueInputOption='USER_ENTERED', body=body).execute()
        return result

    # Your target values
    target_in_column_B = target_match
    value_to_write = total_score

    # Find the row
    row_number = find_row(service, SPREADSHEET_ID, target_in_column_B)
    if row_number:
        # Update the cell
        result = update_cell(service, SPREADSHEET_ID, row_number, value_to_write)
        print(f"Updated cell: {result.get('updatedCells')} cells updated.")
    else:
        print("Target value not found in column B.")

def run_total_score(match):
    teams = match.split("-")
    home_team = teams[0].strip()
    away_team = teams[1].strip()
    obj = MatchStatistics(home_team, away_team)
    obj.get_event_id()
    while True:
        obj.get_goals()
        obj.get_total_corners()
        obj.get_adjusted_cards()
        write_to_sheet(match, obj.get_total_score())
        time.sleep(180)
if __name__ == '__main__':
    run_total_score(match = "alaves - real madrid")