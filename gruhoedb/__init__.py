from googleapiclient.discovery import build


def get_cells(api_key, spreadsheet_id):
    request = make_request(api_key, spreadsheet_id)
    response = request.execute()
    return response['values']


def make_request(api_key, spreadsheet_id):
    service = build('sheets', 'v4', developerKey=api_key)
    return service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range='Sheet1!A1:E')
