
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
import os
from datetime import datetime

CREDENTIALS_FILE = "service_account.json"
SHEET_URL = "https://docs.google.com/spreadsheets/d/1iiQvatTj9t0aYqcRS8i5Brxd-FezGmRHOGq5PlI1Qks"
SCOPE = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

def export_to_csv():
    creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPE)
    client = gspread.authorize(creds)
    sheet = client.open_by_url(SHEET_URL)
    worksheet = sheet.get_worksheet(0)
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)
    
    timestamp = datetime.now().strftime("%Y-%m-%d")
    output_dir = f"scrape/{timestamp}"
    os.makedirs(output_dir, exist_ok=True)
    
    filename = f"{output_dir}/dentists_bc_full_export.csv"
    df.to_csv(filename, index=False)
    print(f"Exported {len(df)} leads to {filename}")

if __name__ == "__main__":
    export_to_csv()
