from gspread_sensitive_info import authenticate_google_sheets
from gspread_sensitive_info import JSON_KEYFILE
from gspread_sensitive_info import SHEET_URL


def get_and_update_n(client, sheet_url):
    """Find the first 'n' in RECEIVED column, retrieve the code from CODE column, and update 'n' to 'y'."""
    
    sheet = client.open_by_url(sheet_url)
    worksheet = sheet.sheet1  

    # Get all values from RECEIVED column (y/n) and CODE column (codes)
    column_d = worksheet.col_values(4)  
    column_a = worksheet.col_values(1)  

    # Find the first 'n'
    for i, value in enumerate(column_d):
        if value.strip().lower() == "n":
            code = column_a[i]  # Get corresponding code
            cell_position = f"D{i+1}"  # Get the cell position (Google Sheets is 1-based)

            worksheet.update(cell_position, [["y"]]) # Update 'n' to 'y'

            print(f"✅ Found code: {code} (Updated row {i+1} from 'n' to 'y')")
            return code

    print("❌ No 'n' found in RECEIVED column")
    return None 

client = authenticate_google_sheets(JSON_KEYFILE)

next_code = get_and_update_n(client, SHEET_URL)