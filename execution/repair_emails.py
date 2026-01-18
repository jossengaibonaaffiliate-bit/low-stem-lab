
import gspread
import pandas as pd
import sys
import os
import logging
from google.oauth2.service_account import Credentials

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Ensure current directory is in path for imports
sys.path.append(os.getcwd())

from execution.extract_website_contacts import scrape_website_contacts

# Constants
SHEET_URL = "https://docs.google.com/spreadsheets/d/1iiQvatTj9t0aYqcRS8i5Brxd-FezGmRHOGq5PlI1Qks"
CREDENTIALS_FILE = "service_account.json"
SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def connect_to_sheet():
    """Connect to Google Sheet and return the worksheet."""
    try:
        creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPE)
        client = gspread.authorize(creds)
        sheet = client.open_by_url(SHEET_URL)
        # Assuming the data is in the first sheet/tab
        worksheet = sheet.get_worksheet(0)
        return worksheet
    except Exception as e:
        logger.error(f"Failed to connect to Google Sheet: {e}")
        return None

def repair_missing_emails():
    """Find rows without emails and try to find them using Deep Search."""
    worksheet = connect_to_sheet()
    if not worksheet:
        return

    logger.info("Fetching data from Google Sheet...")
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)
    
    # Identify rows with missing emails (empty string or None)
    # Adjust column name if your sheet uses 'Email' vs 'email'
    email_col = 'emails' 
    website_col = 'website'
    name_col = 'business_name'

    if email_col not in df.columns:
        logger.error(f"Column '{email_col}' not found in sheet columns: {df.columns}")
        return

    missing_mask = (df[email_col] == "") | (df[email_col].isnull())
    missing_indices = df[missing_mask].index
    
    total_missing = len(missing_indices)
    logger.info(f"Found {total_missing} rows with missing emails.")

    repaired_count = 0
    
    for idx in missing_indices:
        row = df.iloc[idx]
        website = row.get(website_col)
        name = row.get(name_col)
        
        # We need a website or at least a name to search
        if not website and not name:
            continue
            
        logger.info(f"[{repaired_count+1}/{total_missing}] Attempting repair for: {name} ({website})")
        
        # Use existing extraction logic (which attempts deep search & social search)
        # Use website if available, otherwise pass empty string to force search engine use
        target_url = website if website else "" 
        
        try:
            contact_data = scrape_website_contacts(target_url, name)
            found_emails = contact_data.get('emails', [])
            
            if found_emails:
                primary_email = found_emails[0]
                logger.info(f"  >>> SUCCESS: Found {primary_email}")
                
                # Update the DataFrame
                df.at[idx, email_col] = primary_email
                
                # Update the ACTUAL Google Sheet (row by row to be safe/incremental)
                # gspread rows are 1-indexed, header is row 1, so row index idx is idx+2
                cell_row = idx + 2
                
                # Find the column index for email (1-indexed)
                col_index = df.columns.get_loc(email_col) + 1
                
                worksheet.update_cell(cell_row, col_index, primary_email)
                repaired_count += 1
            else:
                logger.info("  >>> FAILED: No email found.")
                
        except Exception as e:
            logger.error(f"Error repairing row {idx}: {e}")
            continue

    logger.info(f"REPAIR COMPLETE. Repaired {repaired_count} leads.")

if __name__ == "__main__":
    repair_missing_emails()
