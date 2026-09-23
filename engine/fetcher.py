#Reusable HTTP fetcher responsible for sending requests
#Handling timeouts and request errors.
import requests

class Fetcher:

    def __init__(self, headers=None, timeout=30):
        self.headers = headers or {}
        self.timeout = timeout

    def get(self, url):

        try:

            response = requests.get(
                url,
                headers=self.headers,
                timeout=self.timeout
            )

            response.raise_for_status()

            return response

        except requests.exceptions.Timeout:

            print(f"Request timed out: {url}")

            return None

        except requests.exceptions.RequestException as e:

            print(f"Request failed: {url}")
            print(f"Error: {e}")

            return None