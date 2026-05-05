import requests
from urllib3.util import Retry
from requests.adapters import HTTPAdapter

class OpenF1Client:
    def __init__(self, base_url="https://api.openf1.org/v1"):
        self.base_url = base_url
        self.session = requests.Session()
        
        # Implementation of Exponential Backoff
        retries = Retry(
            total=5,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        self.session.mount('https://', HTTPAdapter(max_retries=retries))

    def fetch_data(self, endpoint, params=None):
        response = self.session.get(f"{self.base_url}/{endpoint}", params=params)
        response.raise_for_status()
        return response.json()