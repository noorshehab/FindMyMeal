from apify_client import ApifyClientAsync
from typing import Any,List,Dict
import os 
from dotenv import load_dotenv

load_dotenv()
APIFY_KEY=os.getenv("APIFY_KEY")



class ApifyService:
    def __init__(self):
       self.client=ApifyClientAsync(APIFY_KEY)
    async def get_restaurants(self,location:str,search_string:str)->List[Dict[str, Any]]:
        query={
        "searchStringsArray": [search_string],
            "locationQuery": location,
            "maxCrawledPlacesPerSearch": 10,
            "language": "en",
            "scrapeReviewsPersonalData": True,
            "scrapeImages": False, 
            "scrapeReviews": False,
        }
        print(f"DEBUG: Starting Apify actor for {search_string} in {location}...")

        run = await self.client.actor("compass/crawler-google-places").call(run_input=query,memory_mbytes=1024,
            timeout_secs=120)
        if not run:
            print("Error: Apify run failed to start.")
            return []

        results = []
        dataset_client = self.client.dataset(run["defaultDatasetId"])

        async for item in dataset_client.iterate_items():
            results.append(item)
            
        print(f"DEBUG: Fetched {len(results)} raw items from Apify.")
        return results

