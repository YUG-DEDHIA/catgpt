import os
import openai
import requests
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Add CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for simplicity
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API keys and endpoints
openai.api_key = os.getenv("OPENAI_API_KEY")
CAT_API_KEY = os.getenv("CAT_API_KEY")
CAT_API_BASE_URL = "https://api.thecatapi.com/v1"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the input model for chat queries
class Query(BaseModel):
    user_input: str

from difflib import get_close_matches

def get_breed_id(breed_name):
    """
    Fetch breed ID for the given breed name. If no exact match is found,
    suggest the closest match using approximate string matching.
    If still no match is found, fetch a random fact and return an appropriate message.
    """
    headers = {"x-api-key": CAT_API_KEY}
    response = requests.get(f"{CAT_API_BASE_URL}/breeds", headers=headers)
    
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch breeds from Cat API")
    
    breeds = response.json()
    breed_names = [breed["name"] for breed in breeds]
    
    # Exact match
    for breed in breeds:
        if breed_name.lower() == breed["name"].lower():
            return breed["id"]
    
    # Handle spelling errors with approximate matching
    closest_matches = get_close_matches(breed_name, breed_names, n=1, cutoff=0.6)
    if closest_matches:
        matched_breed_name = closest_matches[0]
        for breed in breeds:
            if matched_breed_name == breed["name"]:
                return breed["id"]
    
    # Fetch a random fact if no breed matches
    fact_response = requests.get(f"{CAT_API_BASE_URL}/facts", headers=headers, params={"limit": 1})
    if fact_response.status_code != 200:
        raise HTTPException(status_code=fact_response.status_code, detail="Failed to fetch random cat facts from Cat API")
    
    fact_data = fact_response.json()
    

    # Log and raise an error with the fact
    logger.info(f"Random cat fact: {fact_data}")
    raise HTTPException(
        status_code=404,
        detail=f"Breed '{breed_name}' does not exist. Here's a random fact about cats: {fact_data[0]['text']}",
    )


# Function to fetch cat images
def fetch_cats(breed_id=None, limit=1):
    headers = {"x-api-key": CAT_API_KEY}
    params = {"limit": limit, "order": "RAND"}
    if breed_id:
        params["breed_ids"] = breed_id
    
    response = requests.get(f"{CAT_API_BASE_URL}/images/search", headers=headers, params=params)
    
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch images from Cat API")
    
    return response.json()

import json  # Importing json for safe parsing

def process_user_input_with_openai(user_input):
    try:
        # Using the chat endpoint with the gpt-4o-mini model
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {
                    "role": "user",
                    "content": f"Extract the following details from the user input: 1) Breed of the cat (if mentioned), 2) Number of images requested (default is 1 if not specified). Respond in JSON format with 'breed' and 'limit'.\n\nUser input: {user_input}",
                },
            ],
            max_tokens=50,
            temperature=0.2,
        )
        # Parse the response from OpenAI
        raw_result = response.choices[0].message["content"].strip()
        logger.info(f"Raw OpenAI response: {raw_result}")

        # Clean and parse the response
        if raw_result.startswith("```json"):
            raw_result = raw_result.replace("```json", "").replace("```", "").strip()
        
        result = json.loads(raw_result)  # Safely parse JSON
        logger.info(f"Parsed OpenAI response: {result}")
        return result
    except json.JSONDecodeError as e:
        logger.error(f"JSON decoding error: {e}")
        raise HTTPException(status_code=500, detail="Failed to parse JSON response from OpenAI")
    except Exception as e:
        logger.error(f"Error in OpenAI processing: {e}")
        raise HTTPException(status_code=500, detail="Failed to process input with OpenAI")

# Chat API endpoint
@app.post("/chat")
async def chat_with_openai(query: Query):
    try:
        # Process the user input with OpenAI
        user_input = query.user_input
        parsed_data = process_user_input_with_openai(user_input)

        # Extract breed and limit from the parsed data
        breed_name = parsed_data.get("breed")
        limit = parsed_data.get("limit", 1)

        breed_id = None
        if breed_name:
            breed_id = get_breed_id(breed_name)

        # Fetch cat images
        cats = fetch_cats(breed_id=breed_id, limit=limit)
        logger.info(f"Fetched {len(cats)} cat images")
        cat_urls = [cat["url"] for cat in cats if "url" in cat]

        # Log the parsed values and response
        logger.info(f"User input: {user_input}, Breed name: {breed_name}, Limit: {limit}")
        logger.info(f"Cat URLs: {cat_urls}")

        # Return the response
        return {"response": cat_urls}

    except Exception as e:
        logger.error(f"Error in chat_with_openai: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/facts")
async def get_cat_facts():
    try:
        # Request a random cat fact from OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {
                    "role": "user",
                    "content": "Generate a random cat fact.",
                },
            ],
            max_tokens=1000,
            temperature=0.8,
        )
        # Parse the OpenAI response
        raw_result = response.choices[0].message["content"].strip()
        logger.info(f"Raw OpenAI response: {raw_result}")

        if raw_result.startswith("```json"):
            raw_result = raw_result.replace("```json", "").replace("```", "").strip()
        
        try:
            result = json.loads(raw_result)
        except json.JSONDecodeError:
            return {"fact": raw_result}

        return result

    except Exception as e:
        logger.error(f"Error in get_cat_facts: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate cat fact")
