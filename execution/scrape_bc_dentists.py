import sys
import os

# Ensure execution directory is in path
sys.path.append(os.path.join(os.getcwd(), 'execution'))

from gmaps_lead_pipeline import run_pipeline

KEYWORDS = [
    "Dentist", "Dental Clinic", "Orthodontist", "Oral Surgeon", 
    "Dental Hygiene Clinic", "Pediatric Dentist", "Cosmetic Dentistry", "Denture Clinic"
]

CITIES = [
    # --- METRO VANCOUVER ---
    "Vancouver", "Surrey", "Burnaby", "Richmond", "Coquitlam", "Langley", "Delta", "North Vancouver", 
    "Maple Ridge", "New Westminster", "Port Coquitlam", "West Vancouver", "Port Moody", "Whiterock", 
    "Pitt Meadows", "Tsawwassen", "Ladner", "Fort Langley", "Aldergrove",
    # --- VANCOUVER ISLAND ---
    "Victoria", "Nanaimo", "Saanich", "Duncan", "Comox", "Courtenay", "Campbell River", "Langford", 
    "Colwood", "Oak Bay", "Esquimalt", "Sooke", "Parksville", "Qualicum Beach", "Port Alberni", 
    # --- FRASER VALLEY / INTERIOR / NORTH ---
    "Abbotsford", "Chilliwack", "Mission", "Kelowna", "Kamloops", "Vernon", "Penticton", "Prince George"
    # (Truncated for efficiency, but will search major hubs for all keywords first)
]

SHEET_URL = "https://docs.google.com/spreadsheets/d/1iiQvatTj9t0aYqcRS8i5Brxd-FezGmRHOGq5PlI1Qks/edit?gid=0#gid=0"

def main():
    total_leads_added = 0
    
    for keyword in KEYWORDS:
        print(f"\n\n#### STARTING NEW BATCH FOR KEYWORD: {keyword.upper()} ####")
        for city in CITIES:
            print(f"\n>>> SCRAPING: {keyword} in {city} <<<")
            query = f"{keyword} in {city}, BC, Canada"
            
            try:
                results = run_pipeline(
                    search_query=query,
                    max_results=100, 
                    sheet_url=SHEET_URL,
                    workers=25, 
                    save_intermediate=True,
                    skip_sheets=False
                )
                
                added = results.get("leads_added", 0)
                total_leads_added += added
                print(f">>> FINISHED {city}. Added {added} new leads. Total this session: {total_leads_added}")
                
            except Exception as e:
                print(f"!!! Error scraping {keyword} in {city}: {e}")
                
    print(f"\n\nMISSION COMPLETE. Total new leads added to sheet: {total_leads_added}")

if __name__ == "__main__":
    main()
