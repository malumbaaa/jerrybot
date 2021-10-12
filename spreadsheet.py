import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('TestProject-secret.json', scope)
client = gspread.authorize(creds)

sheet = client.open('TestSpreadsheet').sheet1


# mevl = sheet.get_all_records()
# print(mevl)


def insert_data(data):
    sheet.insert_row(data, 2)
