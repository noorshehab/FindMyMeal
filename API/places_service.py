import httpx
from typing import List,Dict,Any


class PlacesService:
    def __init__(self,api_key:str):
        self.api_key=api_key

    #async def search()