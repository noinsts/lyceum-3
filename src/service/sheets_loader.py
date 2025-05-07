import sqlite3
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Авторизація
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("../creds/credentials.json", scope)
client = gspread.authorize(creds)

# Відкриття Google Таблиці
sheet = client.open("lyceum-3").worksheet("schedule")

# З'єднання з SQLite
conn = sqlite3.connect("../../db/database.db")
cursor = conn.cursor()

# Витягування даних
cursor.execute("SELECT * FROM schedule")
rows = cursor.fetchall()

# Очистити старі дані в Google Таблиці
sheet.clear()

column_names = ['id', 'day_of_week', 'lesson_number', 'time_period', 'class', 'subject', 'teacher']
sheet.append_row(column_names)

# Додати нові дані
sheet.append_rows(rows)
