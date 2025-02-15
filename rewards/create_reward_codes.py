import random
import string
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
from gspread_sensitive_info import JSON_KEYFILE
from gspread_sensitive_info import SHEET_URL

def generate_codes(n=100, length=4):
    """Generate a list of n unique alphanumeric codes of given length."""
    codes = set()
    while len(codes) < n:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
        codes.add(code)
    return list(codes)



def write_to_google_sheets(sheet_url, json_keyfile, codes):
    """Write the generated codes to a Google Sheet."""
    
    # Authenticate with Google Sheets
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(json_keyfile, scope)
    client = gspread.authorize(creds)
    
    # Open the Google Sheet by URL
    sheet = client.open_by_url(sheet_url)
    worksheet = sheet.sheet1  # Use the first worksheet

    # Convert the list to a Pandas DataFrame
    df = pd.DataFrame({"Codes": codes})

    # Write data to the sheet (overwrite existing data)
    worksheet.update([df.columns.values.tolist()] + df.values.tolist())

    print("✅ Codes successfully written to Google Sheets!")


codes = generate_codes()
write_to_google_sheets(SHEET_URL, JSON_KEYFILE, codes)
