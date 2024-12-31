from typing import List

def update_session_list(session: dict, item: str):
    """Update the list stored in the session."""
    if "list" not in session:
        session["list"] = []  # Initialize if not present
    session["list"].append(item)
    return session["list"]

def get_session_list(session: dict) -> List[str]:
    """Retrieve the list stored in the session."""
    return session.get("list", [])



def add_to_chat_history(session: dict ,message: str):
    if "chat_history" not in session:
        session["chat_history"] = []  # Initialize if not present
    session["chat_history"].append(message)
    # only keep the last 5 messages in the chat history
    session["chat_history"] = session["chat_history"][-5:]
    
    return session["chat_history"] 

def get_chat_history(session: dict):
    if "chat_history" not in session:
        session["chat_history"] = []  # Initialize if not present
    
    return session["chat_history"]


def add_to_search_history(session: dict ,search_index: int, search_item: str):
    if "search_history" not in session:
        session["search_history"] = {}  # Initialize if not present
    session["search_history"][search_index] = search_item
    return session["search_history"]

def get_search_history_item(search_index: int):
    global search_history
    return search_history[search_index]

def get_search_history():
    global search_history
    return search_history

def delete_search_history_item(search_index: int):
    global search_history
    del search_history[search_index]
    return search_history

def clear_search_history():
    global search_history
    search_history.clear()
    return search_history