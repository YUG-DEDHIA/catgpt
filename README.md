# Cat GPT

This is a FastAPI-based application that identifies cat breeds, fetches cat images, and provides random facts about cats. It integrates with OpenAI's GPT API for natural language understanding and The Cat API for cat breed data, images, and facts.

---

## Features

- **Cat Breed Identification**: Detects the breed of a cat based on user input.
- **Random Cat Facts**: Provides a random fact about cats if the specified breed is not found.
- **Cat Images**: Fetches one or more cat images, optionally filtered by breed.
- **Natural Language Processing**: Uses OpenAI to parse user input for breed names and image limits.
- **Error Handling**: Handles misspelled breed names and API errors gracefully.

---

## Endpoints

### `/chat` (POST)
Processes user input, identifies the requested cat breed, and fetches cat images or facts.

**Request Body**:
```json
{
    "user_input": "Show me pictures of Bengal cats."
}
```

---

## Prerequisites

- Python 3.8 or higher
- OpenAI API Key
- The Cat API Key

---

## Installation

Clone the repository:
```sh
git clone https://github.com/YUG-DEDHIA/catgpt.git
cd catgpt
```

Install dependencies:
```sh
cd backend
pip install -r requirements.txt
```

Set up environment variables:

Create a `.env` file in the project root with the following keys:
```
OPENAI_API_KEY=your_openai_api_key
CAT_API_KEY=your_cat_api_key
```

---

## Usage

Start the server:
```sh
uvicorn main:app --reload
```

Access the API at [http://127.0.0.1:8000](http://127.0.0.1:8000).

---

## How It Works

### User Input Parsing
Input is sent to OpenAI's GPT API, which extracts the cat breed and the number of images requested.

### Cat Breed Validation
- The breed is validated against The Cat API's breed list.
- If no match is found, approximate matching suggests the closest breed name.
- If no match is possible, a random cat fact is fetched.

### Image Fetching
The Cat API is queried to fetch images based on the identified breed and user-specified limit.

### Response Generation
The API responds with the fetched images or a random fact if the breed is invalid.

---

## API Integration

### OpenAI GPT
Used to parse natural language input and extract structured data.

### The Cat API
Endpoints:
- `/breeds`: Fetch cat breeds.
- `/images/search`: Fetch cat images.
- `/facts`: Fetch random cat facts.

---

## Error Handling

- If The Cat API or OpenAI fails, the API responds with appropriate HTTP error codes and messages.
- If no breed is found, a random fact about cats is returned.
