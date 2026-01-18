
import gspread
from google.oauth2.service_account import Credentials

CREDENTIALS_FILE = "service_account.json"
SHEET_URL = "https://docs.google.com/spreadsheets/d/1iiQvatTj9t0aYqcRS8i5Brxd-FezGmRHOGq5PlI1Qks"
SCOPE = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

def count_leads():
    creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPE)
    client = gspread.authorize(creds)
    sheet = client.open_by_url(SHEET_URL)
    worksheet = sheet.get_worksheet(0)
    records = worksheet.get_all_records()
    print(f"Total leads in sheet: {len(records)}")
    
    # Count leads with emails
    with_email = [r for r in records if r.get('emails')]
    print(f"Leads with emails: {len(with_email)}")
    
    # Check for duplicates by lead_id
    ids = [r.get('lead_id') for r in records]
    unique_ids = set(ids)
    print(f"Unique leads by ID: {len(unique_ids)}")

if __name__ == "__main__":
    count_leads()
