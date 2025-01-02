from fastapi import APIRouter, Request, HTTPException
from .utils import update_session_list, get_session_list ,get_chat_history  # Import the utility functions

router = APIRouter()

# POST endpoint to update the session-based list
@router.get("/update-list/")
async def update_list(request: Request, item: str):
    try:
        session = request.session
        # Update the session list
        if "user_list" not in session:
            session["user_list"] = []
        session["user_list"].append(item)
        return {"message": "Item added to list", "list": session["user_list"]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")

# GET endpoint to fetch the session-based list
@router.get("/get-list/")
async def get_list(request: Request):
    session = request.session
    user_list = session.get("user_list", [])
    return {"list": user_list}

@router.get("/get-chat_history/")
async def get_list(request: Request):
    session = request.session
    chat_his = get_chat_history(session)
    
    return chat_his