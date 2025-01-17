import copy
import json
import math
from pydantic import BaseModel
from openai import OpenAI
client = OpenAI()
from .utils import get_chat_history, add_to_chat_history, rank_products
from fastapi import Request
from .dependencies import perform_search_advanced
import numpy as np

# Define the function with chat history memory
def openAI_chat_assistant(session: dict ,new_message: str,tools= None,response_format=None ,  temperature: float = 0, max_tokens: int = 1024 ) :
    # Initialize 
    prompt = [{"role": "system", "content": "You are a helpful shopping assistant. Answer in very short and simple sentences. Dont ask too many questions, and don't respond with un provided information."}]
    
    chat_history = get_chat_history(session)
    
    chat_history = add_to_chat_history(session=session,message={"role": "user", "content": new_message})
    
    prompt.extend(chat_history) if chat_history else prompt
    
    # print("Prompt: ", prompt)
    # print("Prompt type ", type(prompt))
    
    # Call the OpenAI API to generate a response
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=prompt,
        temperature=temperature,
        max_tokens=max_tokens,
        tools=tools,
        response_format = response_format
    )
    
    # Extract the assistant's response
    assistant_reply = completion.choices[0].message.content

    
    # Return the reply and updated chat history
    return completion


def order_the_best_5_search_results(session: dict ,best_five_results: str ,user_input: str):
    # Parse the input JSON string
    best_five_results_copy = json.loads(best_five_results)
    best_five_results_copy_2 = json.loads(best_five_results)
    best_five_results = json.loads(best_five_results)
    
    
    # Extract the search index from the parsed JSON
    # search_index = best_five_results.get("search_index", "Unknown Search Index")
    
    # get a copy of best_five_results
    # best_five_results_copy = best_five_results.copy()
    
    # Extract product details from the results
    product_attributes = []
    
    product_list_for_chat_history = []
    
    for product in best_five_results_copy.get("search_results", []):
        product.pop("product_link", None)
        product.pop("offers_link", None)
        product.pop("thumbnail", None)
        product.pop("price_normalized",None)
        product.pop("rating_normalized",None)
        product.pop("reviews_normalized",None)
        product.pop("rank",None)
        product.pop("position",None)
        product.pop("extracted_price",None)
        product.pop("extracted_original_price",None)
        product_attributes.append(
            # remove product_link , offers_link , thumbnail from the product attributes , other attributes could differ
            product
        )
    
    for product in best_five_results_copy_2.get("search_results", []):
        product.pop("offers_link", None)
        product.pop("price_normalized",None)
        product.pop("rating_normalized",None)
        product.pop("reviews_normalized",None)
        product.pop("position",None)
        product.pop("extracted_price",None)
        product.pop("extracted_original_price",None)
        
        # get the product id from product
        product_id = product.get('product_id')
        # if product id is NaN\
        if product_id is None or (isinstance(product_id, float) and math.isnan(product_id)):
            product['product_id'] = product.get('prds')
        
        print("Produccccccccccct : ", product)        
        
        product_list_for_chat_history.append(
            product
        )
        
    # print("Bet 5 result s",best_five_results.get("search_results", []))
    # Combine the search index and product attributes into a final JSON object
    result_json = {
        # "search_index": search_index,
        "products": product_attributes
    }
    
    # Convert the final JSON object to a string
    result_json_string = json.dumps(result_json, indent=4)
    
    # user_searched_item = get_search_history_item(search_index)
    
    users_quarry = user_input
    
    # print("User searched quarry: ", users_quarry)
    
    quarry = users_quarry + " These are the attributes of the item user searched for , according to that , rank the following top 5 search results to mach the users search criteria and to be the overall best product from the search results considering all the factors .'score' attribute in these are given according to our analytical hierarchy process from all the search results . keep your reasoning very short , and remember you are giving this reasoning directly to the user so use proper pronounce. 5 Search results : "+ result_json_string
    
    class OrderStructured(BaseModel):
        reasons_for_the_order: str
        product_ID_of_the_rank_1_search_result_according_to_you_should_not_be_NaN: str
        product_ID_of_the_rank_2_search_result_according_to_you_should_not_be_NaN: str
        product_ID_of_the_rank_3_search_result_according_to_you_should_not_be_NaN: str
        product_ID_of_the_rank_4_search_result_according_to_you_should_not_be_NaN: str
        product_ID_of_the_rank_5_search_result_according_to_you_should_not_be_NaN: str
        
    completion = client.beta.chat.completions.parse(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": quarry},
        ],
        response_format=OrderStructured,
    )
        
    
    json_gpt_ranking = completion.choices[0].message.content
    
    print("GPT rankings",json_gpt_ranking)
    
        # Parse the GPT response for the ranking information
    ranking_info = json.loads(json_gpt_ranking)
    
    # Map product IDs to their ranks
    product_rank_map = {
        ranking_info["product_ID_of_the_rank_1_search_result_according_to_you_should_not_be_NaN"]: 1,
        ranking_info["product_ID_of_the_rank_2_search_result_according_to_you_should_not_be_NaN"]: 2,
        ranking_info["product_ID_of_the_rank_3_search_result_according_to_you_should_not_be_NaN"]: 3,
        ranking_info["product_ID_of_the_rank_4_search_result_according_to_you_should_not_be_NaN"]: 4,
        ranking_info["product_ID_of_the_rank_5_search_result_according_to_you_should_not_be_NaN"]: 5,
    }
    
    print("Product rank map: ", product_rank_map)
    
    # Add rank and reasoning to each product in the result
    reasoning = ranking_info["reasons_for_the_order"]
    
    # best_five_results["chat_reply"] = reasoning
    
    # for results in best_five_results["search_results"]:
    #     # Use 'product_id' if available; fallback to 'prds' otherwise
    #     product_identifier = results.get("product_id") or results.get("prds")
    #     results["rank"] = product_rank_map.get(product_identifier, "Not Ranked")


    # # Convert the final result to a JSON string with ranks and reasoning
    # result_json_string_with_ranking = json.dumps(best_five_results, indent=4)
    
    # print("final result with ranking and reasoning: ", result_json_string_with_ranking)
    
    # add_to_chat_history(session=session,message={"role": "assistant", "content": result_json_string_with_ranking})
    
    print ("Product list for chat history : ", product_list_for_chat_history)
    
    for results in product_list_for_chat_history:
        # Use 'product_id' if available; fallback to 'prds' otherwise
        product_identifier = results.get("product_id") 
        results["GPT_rank"] = product_rank_map.get(product_identifier, "Not Ranked")
    
    
    print("Product list for chat history after ranking : ", product_list_for_chat_history)
    json_for_chat_history = {"search_results" : product_list_for_chat_history , "chat_reply" : reasoning}
    
    # convert the json object to a string
    result_json_string_with_ranking = json.dumps(json_for_chat_history, indent=4)
    
    
    return result_json_string_with_ranking


somple_top_search_results= {
  "results": [
    {
      "position": 1,
      "product_id": "11234567890123456789",
      "title": "ECOWISH Women's Casual V Neck Button Down Red Dress - Medium",
      "link": "https://www.amazon.com/dp/B089W7MXYZ",
      "product_link": "https://www.amazon.com/dp/B089W7MXYZ",
      "seller": "Amazon",
      "price": "$39.99",
      "extracted_price": 39.99,
      "rating": 4.5,
      "reviews": 1532,
      "delivery": "Free delivery for Prime members",
      "extensions": ["V Neck", "Short Sleeve", "Knee-Length"],
      "brand": "ECOWISH",
      "thumbnail": "https://example.com/images/red_dress1.jpg"
    },
    {
      "position": 2,
      "product_id": "22345678901234567890",
      "title": "ANRABESS Women's Summer Casual Sundress - Red, Medium",
      "link": "https://www.amazon.com/dp/B093J6ABCD",
      "product_link": "https://www.amazon.com/dp/B093J6ABCD",
      "seller": "Amazon",
      "price": "$29.99",
      "extracted_price": 29.99,
      "rating": 4.7,
      "reviews": 2280,
      "delivery": "Free delivery with $25 order",
      "extensions": ["Spaghetti Strap", "Flowy", "Lightweight"],
      "brand": "ANRABESS",
      "thumbnail": "https://example.com/images/red_dress2.jpg"
    },
    {
      "position": 3,
      "product_id": "33456789012345678901",
      "title": "MEROKEETY Women's Sleeveless Wrap Dress - Red, Medium",
      "link": "https://www.amazon.com/dp/B08KL7EFGH",
      "product_link": "https://www.amazon.com/dp/B08KL7EFGH",
      "seller": "Amazon",
      "price": "$47.99",
      "extracted_price": 47.99,
      "rating": 4.6,
      "reviews": 874,
      "delivery": "Free delivery for Prime members",
      "extensions": ["Wrap Style", "Adjustable Waist", "Knee-Length"],
      "brand": "MEROKEETY",
      "thumbnail": "https://example.com/images/red_dress3.jpg"
    },
    {
      "position": 4,
      "product_id": "44567890123456789012",
      "title": "PRETTYGARDEN Women's Casual T-Shirt Dress - Red, Medium",
      "link": "https://www.amazon.com/dp/B08KL7LMNO",
      "product_link": "https://www.amazon.com/dp/B08KL7LMNO",
      "seller": "Amazon",
      "price": "$34.99",
      "extracted_price": 34.99,
      "rating": 4.3,
      "reviews": 640,
      "delivery": "Free delivery with $25 order",
      "extensions": ["T-Shirt Style", "Soft Fabric", "Midi Length"],
      "brand": "PRETTYGARDEN",
      "thumbnail": "https://example.com/images/red_dress4.jpg"
    },
    {
      "position": 5,
      "product_id": "55678901234567890123",
      "title": "ZESICA Women's Summer Wrap Maxi Dress - Red, Medium",
      "link": "https://www.amazon.com/dp/B08KL7PQRS",
      "product_link": "https://www.amazon.com/dp/B08KL7PQRS",
      "seller": "Amazon",
      "price": "$45.99",
      "extracted_price": 45.99,
      "rating": 4.5,
      "reviews": 1325,
      "delivery": "Free delivery for Prime members",
      "extensions": ["Maxi Length", "Floral Design", "Bohemian Style"],
      "brand": "ZESICA",
      "thumbnail": "https://example.com/images/red_dress5.jpg"
    }
  ]
}



# def search (attri : str):
#     # print("searching for : ",attri)
#     # global somple_top_search_results
#     # # convert somple_top_search_results to json string
    
#     # convert the json string attri to json dict object
#     attri_json = json.loads(attri)
    
#     all_searcch_result = perform_search_advanced(attri_json)
    
#     first_5_search_results = rank_products(all_searcch_result)[:5]
    
#     somple_top_search_results = {"search_results": first_5_search_results}
    
#     string_reult = json.dumps(somple_top_search_results)
#     return string_reult

# Replace NaN with null or another value (e.g., 0)
def replace_nan(obj):
    if isinstance(obj, dict):
        return {k: replace_nan(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [replace_nan(item) for item in obj]
    elif isinstance(obj, float) and np.isnan(obj):
        return None  # Replace NaN with null for JSON
    else:
        return obj

def talk_to_gpt(user_input : str ,request: Request):
    
    session = request.session # get the session object    
    
    # print("User input: ", user_input)
    
    chat_history = get_chat_history(session)
    
    tools = [
        {
            "type": "function",
            "function": {
        "name": "search_item",
        "description": "Search for an item to buy from an online store based on various criteria.if the user has provided them. if user has only provided a few continue with only what they have given.Do not ask him to give more details continually if he has not provided them.",
        "strict": True,
        "parameters": {
        "type": "object",
        "required": [
            "query",
            "item",
            "category",
            "store",
            "brand",
            "min_price",
            "max_price",
            "min_rating",
            "features",
            "keywords",
            "material",
            "color",
            "size_dimension",
            "size_scale"
        ],
        "properties": {
            "query": {
            "type": "string",
            "description": "summarized shorten version of the users exact search request (this should be suitable to search in a online shopping website)"
            },
            "item": {
            "type": "string",
            "description": "The name of the item being searched. Must have a value."
            },
            "category": {
            "type": "string",
            "description": "The category of the item"
            },
            "store": {
            "type": "string",
            "description": "The online store to search in, select 'Not Specified' if user haven't mention a specific store",
            "enum": [
                "Not Specified",
                "Amazon",
                "eBay",
                "Walmart",
                "Target",
                "Best Buy",
                "Etsy",
                "Home Depot",
                "Costco",
                "Wayfair",
                "Chewy",
                "Macy's",
                "Newegg",
                "Kohl's",
                "Nordstrom",
                "Overstock"
            ]
            },
            "brand": {
            "type": "string",
            "description": "The brand of the item, leave null if not specified"
            },
            "min_price": {
            "type": "number",
            "description": "Minimum price of the item, leave null if not specified"
            },
            "max_price": {
            "type": "number",
            "description": "Maximum price of the item, leave null if not specified"
            },
            "min_rating": {
            "type": "number",
            "description": "Minimum rating of the item (1 to 5), leave null if not specified"
            },
            "features": {
            "type": "array",
            "description": "List of features the item should have",
            "items": {
                "type": "string",
                "description": "Feature of the item"
            }
            },
            "keywords": {
            "type": "array",
            "description": "List of keywords related to the search",
            "items": {
                "type": "string",
                "description": "Keyword for the search"
            }
            },
            "material": {
            "type": "string",
            "description": "Material of the item"
            },
            "color": {
            "type": "string",
            "description": "Color of the item"
            },
            "size_dimension": {
            "type": "integer",
            "description": "Size of the item, provide a value in this only if the size is in inches or cm or any other unit is provided."
            },
            "size_scale": {
            "type": "string",
            "description": "Relative size, e.g., small, medium, or large.",
            "enum": [
                "Not Specified",
                "xxs",
                "xs",
                "s",
                "m",
                "l",
                "xl",
                "xxl"
            ]
            }
        },
        "additionalProperties": False
        }
    }

        }
    ]

    response = openAI_chat_assistant(session=session,new_message=user_input,tools=tools)
    response_msg = response.choices[0].message.content
    function_response_msg = None
    
    print("Response message........: ", response_msg)

    # if there is a function call, extract the function call information
    response_func = None
    if (response.choices[0].message.tool_calls):
        response_func = response.choices[0].message.tool_calls[0].function.name
        
        
        # write a switch case to call the function with the arguments
        if response_func == "search_item":
            arguments = response.choices[0].message.tool_calls[0].function.arguments
            # print("Passing arguments to search_item function: ",arguments )
            # argument is a string in json format, so we need to parse it
            function_response_msg = search_item(session=session,attributes_json=arguments, user_input=user_input)
            function_response_msg = json.loads(function_response_msg)
            function_response_msg = replace_nan(function_response_msg)
            
    return_msg = ""
    

        
    if function_response_msg:
        return_msg = function_response_msg
        search_results = function_response_msg.get("search_results")
        
        # get a copy of search results so the original search results are not modified
        search_results_copy = copy.deepcopy(search_results)
        
        product_list_for_chat_history = []
        
        for product in search_results_copy:
            product.pop("product_link", None)
            product.pop("thumbnail",None)
            product.pop("product_id",None)
            product.pop("prds",None)

            product_list_for_chat_history.append(
                product
            )
        
        
        
        # convert the search results to a string
        search_results_str = json.dumps(product_list_for_chat_history, indent=4)
        # search_results_str = "fake search results string"
        print("type of the search_results_str : ", type(search_results_str))
        # print("Type of a string to compare : ", type("fake search results string"))
        add_to_chat_history(session=session,message={"role": "assistant", "content": f"Here is the top 5 items for your search : {search_results_str}" })
    elif response_msg:
        # create a json object with the chat reply key
        return_msg = {"chat_reply": response_msg}
    
    
    print("Chat reply: ", return_msg["chat_reply"])
      
    chat_history= add_to_chat_history(session=session,message={"role": "assistant", "content": f"{return_msg["chat_reply"]}"})

    #   show_user(return_msg)
    # print("show user msg :" , return_msg)
    print("Chat Historyyyyyy..: ",get_chat_history(session))
    return_msg = json.dumps(return_msg)     
    return return_msg

# search_id = 0
def search_item(session: dict ,attributes_json: str , user_input : str): 
    # global search_id
    # search_id += 1
    arguments = json.loads(attributes_json)
    
    all_searcch_result = perform_search_advanced(arguments)
    
    first_5_search_results = rank_products(all_searcch_result)[:5]
    
    somple_top_search_results = {"search_results": first_5_search_results}
    
    string_reult = json.dumps(somple_top_search_results)

    result_with_reasons = order_the_best_5_search_results(session=session,best_five_results=string_reult,user_input=user_input)
    
    return result_with_reasons