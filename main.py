import requests
from dotenv import load_dotenv
import os
from fastapi import FastAPI

load_dotenv()

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/search")
def search(query: str):
    url = "https://www.searchapi.io/api/v1/search"
    API_KEY = os.getenv("SEARCH_API_KEY")
    print(API_KEY)
    params = {
    "engine": "google_shopping",
    "q": query,
    "gl": "us",
    "hl": "en",
    "location": "California,United States",
    "api_key": API_KEY
    }
    print(params)
    response = requests.get(url, params = params)
    print(response.text)
    return response.json()["shopping_results"]

