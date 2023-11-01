import google.auth
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Аутентификация приложения и получение токена доступа
credentials = service_account.Credentials.from_service_account_file(
    'path/to/credentials.json',
    scopes=['https://www.googleapis.com/auth/spreadsheets']
)
service = build('sheets', 'v4', credentials=credentials)

# Имя таблицы и листа, в который нужно добавить данные
spreadsheet_id = 'your-spreadsheet-id'
sheet_name = 'Sheet1'

# Данные, которые нужно добавить в таблицу
data = [['value1', 'value2'], ['value3', 'value4']]

# Диапазон ячеек, в которые нужно добавить данные
range_name = f'{sheet_name}!A1:B2'

# Запрос на добавление данных в таблицу
request = service.spreadsheets().values().update(
    spreadsheetId=spreadsheet_id,
    range=range_name,
    valueInputOption='USER_ENTERED',
    body={'values': data}
)
response = request.execute()

print(f'{response.get("updatedCells")} cells updated.')
