import requests
from dotenv import load_dotenv
import os
load_dotenv()
GITHUB_APIKEY = os.getenv("GITHUB_APIKEY")


def get_github(endpoint, apiKey=GITHUB_APIKEY, query_params={}, return_links=False):
    """
    Get data from github using query parameters and passing a custom apikey header
    """

    # Compose the endpoint url
    baseUrl = "https://api.github.com"
    url = f"{baseUrl}{endpoint}"

    # Create the headers
    headers = {
        "Authorization": f"Bearer {apiKey}"
    }
    # make the request and get the response using HTTP GET verb
    res = requests.get(url, params=query_params, headers=headers)

    print(f"Request data to {res.url} status_code:{res.status_code}")
    data = res.json()

    if res.status_code != 200:
        raise ValueError(f'Invalid github api call: {data["message"]}')
    if return_links:
        return data, res.links
    return data
