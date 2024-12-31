from fastapi import FastAPI,Body
from starlette.middleware.sessions import SessionMiddleware
from app.dependencies import get_session_secret_key, perform_search, perform_search_advanced
from app.routes import router

app = FastAPI()

# Add session middleware with secret key
app.add_middleware(SessionMiddleware, secret_key=get_session_secret_key())

# Include API routes
app.include_router(router)


@app.get("/")
def read_root():
    return {"Backend": "Healthy"}


@app.post("/search")
def search(query: str):
    return perform_search(query)

@app.post("/search-advanced")
def process_json(data: dict = Body(...)):
    return perform_search_advanced(data)