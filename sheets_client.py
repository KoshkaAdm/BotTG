import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
client = gspread.authorize(creds)

def create_user_sheet(user_id):
    sheet_name = f"UserSheet_{user_id}"
    sheet = client.create(sheet_name)
    sheet.share(None, perm_type="anyone", role="writer")
    worksheet = sheet.get_worksheet(0)
    worksheet.update([["Дата", "Тип", "Описание", "Сумма/Задача"]])
    return sheet.url

def append_expense(user_id, amount, category):
    sheet = client.open(f"UserSheet_{user_id}")
    worksheet = sheet.get_worksheet(0)
    worksheet.append_row([get_date(), "Расход", category, amount])

def append_task(user_id, task):
    sheet = client.open(f"UserSheet_{user_id}")
    worksheet = sheet.get_worksheet(0)
    worksheet.append_row([get_date(), "Задача", task, "-"])

def get_date():
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M")
