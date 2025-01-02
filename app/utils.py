import json
from typing import List
import numpy as np
import pandas as pd
from scipy.stats import rankdata
import zlib
import base64

def update_session_list(session: dict, item: str):
    """Update the list stored in the session."""
    if "list" not in session:
        session["list"] = []  # Initialize if not present
    session["list"].append(item)
    return session["list"]

def get_session_list(session: dict) -> List[str]:
    """Retrieve the list stored in the session."""
    return session.get("list", [])



def add_to_chat_history(session: dict, message: dict):
    # Check if "chat_history" exists in the session
    if "chat_history" not in session:
        # Initialize as an empty encoded list
        encoded_chat_history = base64.b64encode(zlib.compress(json.dumps([]).encode())).decode()
        session["chat_history"] = encoded_chat_history
    
    # Decompress and decode the existing chat history
    chat_his_decoded = json.loads(
        zlib.decompress(base64.b64decode(session["chat_history"].encode())).decode()
    )
    
    # Append the new message
    chat_his_decoded.append(message)
    
    chat_his_decoded = chat_his_decoded[-5:]  # Keep only the last 5 messages
    
    # Compress and encode the updated chat history
    chat_his_encoded = base64.b64encode(zlib.compress(json.dumps(chat_his_decoded).encode())).decode()
    session["chat_history"] = chat_his_encoded
    
    return chat_his_decoded

def get_chat_history(session: dict):
    # Check if "chat_history" exists in the session
    if "chat_history" not in session:
        # Initialize as an empty encoded list
        encoded_chat_history = base64.b64encode(zlib.compress(json.dumps([]).encode())).decode()
        session["chat_history"] = encoded_chat_history
    
    # Decode and decompress the chat history
    chat_his_decoded = json.loads(
        zlib.decompress(base64.b64decode(session["chat_history"].encode())).decode()
    )
    
    return chat_his_decoded

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

def rank_products(products):
    """
    Ranks a list of products based on a pairwise comparison matrix.

    Parameters:
        products (list of dict): A list of products where each product is represented
                                 as a dictionary with keys 'price', 'rating', and 'reviews'.

    Returns:
        pd.DataFrame: A DataFrame with normalized scores, ranks, and other details for each product.
    """
    # Step 1: Define Pairwise Comparison Matrix
    # Define pairwise comparisons based on relative importance
    # e.g., "Price is more important than Rating and Reviews"
    pairwise_matrix = np.array([
        [1, 3, 5],  # Price compared with (Price, Rating, Reviews)
        [1/3, 1, 2],  # Rating compared with (Price, Rating, Reviews)
        [1/5, 1/2, 1]  # Reviews compared with (Price, Rating, Reviews)
    ])

    # Step 2: Calculate normalized weights
    def calculate_weights(matrix):
        # Sum each column
        col_sum = matrix.sum(axis=0)

        # Normalize the matrix by dividing each element by the column sum
        normalized_matrix = matrix / col_sum

        # Calculate the weights (average of rows)
        weights = normalized_matrix.mean(axis=1)
        return weights

    weights = calculate_weights(pairwise_matrix)

    # Map weights to parameters
    parameters = ["extracted_price", "rating", "reviews"]
    weights_dict = dict(zip(parameters, weights))

    # Step 3: Normalize the data for products
    # Convert product data to a DataFrame
    data = pd.DataFrame(products)

    # Fill missing values with 0
    data["rating"] = data["rating"].fillna(0)
    data["reviews"] = data["reviews"].fillna(0)

    # Normalize each parameter (lower price is better, higher rating/reviews are better)
    data["price_normalized"] = 1 / data["extracted_price"]  # Inverse since lower price is better
    data["rating_normalized"] = data["rating"] / data["rating"].max()
    data["reviews_normalized"] = data["reviews"] / data["reviews"].max()

    # Step 4: Compute final scores for each product
    data["score"] = (
        weights_dict["extracted_price"] * data["price_normalized"] +
        weights_dict["rating"] * data["rating_normalized"] +
        weights_dict["reviews"] * data["reviews_normalized"]
    )

    # Step 5: Rank products
    data["rank"] = rankdata(-data["score"], method="min")  # Negative for descending order

    # Return the DataFrame sorted by rank
    return data.sort_values("rank").to_dict(orient="records")
