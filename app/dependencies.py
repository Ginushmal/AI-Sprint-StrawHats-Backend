# dependencies.py
from dotenv import load_dotenv
import os
import requests

# Load environment variables
load_dotenv()

def get_session_secret_key():
    """Retrieve the session secret key from the environment."""
    return os.getenv("SESSION_SECRET_KEY")

def get_search_api_key():
    """Retrieve the search API key from the environment."""
    return os.getenv("SEARCH_API_KEY")

def perform_search(query: str):
    """Perform a search using the external search API."""
    url = "https://www.searchapi.io/api/v1/search"
    api_key = get_search_api_key()
    params = {
        "engine": "google_shopping",
        "q": query,
        "gl": "us",
        "hl": "en",
        "location": "California,United States",
        "api_key": api_key,
    }
    response = requests.get(url, params=params)
    response.raise_for_status()  # Raise an HTTPError for bad responses
    return response.json()["shopping_results"]


def perform_search_advanced(data: dict):
    """Print all key-value pairs from a JSON object."""
    for key, value in data.items():
        print(f"{key}: {value}")

    query = data.get("query")
    price_min = data.get("min_price")
    price_max = data.get("max_price")
    """Perform a search using the external search API."""
    url = "https://www.searchapi.io/api/v1/search"
    api_key = get_search_api_key()
    
    if price_max == price_min:
        price_max = None
        price_min = None
    
    params = {
        "engine": "google_shopping",
        "q": query,
        "gl": "us",
        "hl": "en",
        "price_min": price_min,
        "price_max": price_max,
        "location": "California,United States",
        "api_key": api_key,
    }
    response = requests.get(url, params=params)
    response.raise_for_status()  # Raise an HTTPError for bad responses
    # print("resssssssssss",response.json())
    return response.json()["shopping_results"]