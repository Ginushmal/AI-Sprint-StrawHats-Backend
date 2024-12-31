import requests
from dotenv import load_dotenv
import os
from fastapi import FastAPI
from app.routes import router
from starlette.middleware.sessions import SessionMiddleware

load_dotenv()

app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key=os.getenv("SESSION_SECRET_KEY"))

# Include API routes
app.include_router(router)


@app.get("/")
def read_root():
    return {"Hello": "World"}

# @app.post("/search")
# def search(query: str):
#     url = "https://www.searchapi.io/api/v1/search"
#     API_KEY = os.getenv("SEARCH_API_KEY")
#     print(os.getenv("SEARCH_API_KEY"))
#     print(API_KEY)
#     params = {
#     "engine": "google_shopping",
#     "q": query,
#     "gl": "us",
#     "hl": "en",
#     "location": "California,United States",
#     "api_key": API_KEY
#     }
#     print(params)
#     response = requests.get(url, params = params)
#     print(response.text)
#     return response.json()["shopping_results"]


# testList = []
# @app.get("/testAdd")
# def testAdd(item : str):
#     testList.append("item")
#     return testList