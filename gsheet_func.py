from google.oauth2.service_account import Credentials
import gspread
from twilio_func import *
# Define the scopes and credentials
s = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
creds = Credentials.from_service_account_file("credentials.json", scopes=s)
client = gspread.authorize(creds)

# List accessible spreadsheets
spreadsheets = client.list_spreadsheet_files()
for spreadsheet in spreadsheets:
    print(spreadsheet)


# Access the spreadsheet and worksheet
sheet = client.open("Reminders").sheet1

# Get the first row and column values
row_values = sheet.row_values(1)
col_values = sheet.col_values(1)

# Determine filled rows and columns
row_filled = len(col_values)
col_filled = len(row_values)

# Function to save reminder date
def save_reminder_date(date):
    global row_filled  # Update row_filled after adding a row
    sheet.update_cell(row_filled + 1, 1, date)
    row_filled += 1
    print("Saved")
    return 0

