import sys
import os

# Ensure execution directory is in path
sys.path.append(os.path.join(os.getcwd(), 'execution'))

from gmaps_lead_pipeline import run_pipeline

CITIES = [
    # Batch 3: Tier 3 Cities & Towns in BC (Population > 5k)
    "Squamish", "Powell River", "Prince Rupert", "Terrace", "Parksville", 
    "Whistler", "Williams Lake", "Nelson", "Trail", "Dawson Creek", 
    "Quesnel", "Ladysmith", "Castlegar", "Sooke", "Duncan", 
    "Sidney", "Qualicum Beach", "Kitimat", "Revelstoke", "Summerland",
    "Salmon Arm", "Merritt", "Kimberley", "Fernie", "Osoyoos", 
    "Hope", "Kent", "Sechelt", "Gibsons", "Invermere"
]

SHEET_URL = "https://docs.google.com/spreadsheets/d/1iiQvatTj9t0aYqcRS8i5Brxd-FezGmRHOGq5PlI1Qks/edit?gid=0#gid=0"

def main():
    total_leads = 0
    
    for city in CITIES:
        print(f"\n\n>>> STARTING SCRAPE FOR: {city} <<<\n")
        query = f"Dentist in {city}, BC, Canada"
        
        try:
            # Run pipeline for this city
            # We use a limit of 40 per city to aim for ~400 total across 10 cities
            results = run_pipeline(
                search_query=query,
                max_results=40, 
                sheet_url=SHEET_URL,
                workers=5, # Slightly higher parallelism
                save_intermediate=True,
                skip_sheets=False
            )
            
            added = results.get("leads_added", 0)
            total_leads += added
            print(f">>> FINISHED {city}. Added {added} new leads. Total so far: {total_leads}")
            
        except Exception as e:
            print(f"!!! Error scraping {city}: {e}")
            
    print(f"\n\nALL CITIES COMPLETE. Total leads added: {total_leads}")

if __name__ == "__main__":
    main()
