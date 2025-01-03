from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI,Body ,Request
from starlette.middleware.sessions import SessionMiddleware
from app.dependencies import get_session_secret_key, perform_search, perform_search_advanced
from app.routes import router
from app.inventory_detection import detect_inventory
# from app.mock_camera import MockCamera
from app.camera import CameraHandler, LaptopCamera
from .chatAgentFuncs import talk_to_gpt

changed_items = []

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Replace with the frontend's URL
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all HTTP headers
)

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

@app.post("/talk_to_bot")
def talk_to_bot(message: str, request: Request):
    top_5_search_results = talk_to_gpt(user_input=message, request=request)
    return top_5_search_results

@app.post("/clear-session")
async def clear_session(request: Request):
    request.session.clear()  # Clears all session data
    return {"message": "Session data cleared successfully."}

@app.post("/echo")
def echo(message: str):
    return {"message": message}

@app.post("/check-inventory")
def check_inventory(request: Request):
    previous_inventory = [{'Item': 'banana', 'Count': 2}, {'Item': 'apple', 'Count': 1}]
    # mock_camera = MockCamera()
    # image_path = mock_camera.get_img_path()
    camera = LaptopCamera()
    image_path = CameraHandler(camera).get_img_path()
    print(image_path)
    inventory_df, results = detect_inventory(image_path)
    current_inventory = inventory_df.to_dict('records')

    # Remove 'Confidence' column from current inventory
    for item in current_inventory:
        del item['Confidence']

    # Check if the current inventory matches the previous inventory
    if current_inventory == previous_inventory:
        return {"message": "Inventory has not changed.", "status": 0, "bot_output": []}
    else:
        # Inventory has changed
        changed_inventory = []
        for prev in previous_inventory:
            if prev['Item'] not in changed_items:
                for current in current_inventory:
                    if prev['Item'] == current['Item']:
                        if prev['Count'] > current['Count']:
                            changed_inventory.append({'Item': prev['Item'], 'Count': prev['Count'] - current['Count']})
                            changed_items.append(prev['Item'])
                        break
                else:
                    changed_inventory.append({'Item': prev['Item'], 'Count': prev['Count']})
                    changed_items.append(prev['Item'])
        if not changed_inventory:
            return {"message": "Inventory has not changed.", "status": 0, "bot_output": []}
        else:
            most_wanted_item = max(changed_inventory, key=lambda x: x['Count'])
            message = f"I want to buy {most_wanted_item['Item']}."
            top_5_search_results = talk_to_gpt(user_input=message, request=request)
            return {"message": f"Running low on {most_wanted_item['Item']}.", "status": 1, "bot_output": top_5_search_results}

@app.post("/check_fridge")
def check_fridge(request: Request):
    top_5_search_results = talk_to_gpt(user_input="I want banana", request=request)
    # status if changed = 0
    status = 1
    return {"status":status,"message":"Running low on bananas", "bot_output":top_5_search_results}