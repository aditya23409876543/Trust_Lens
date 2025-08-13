# main.py

# Import the necessary tools from the FastAPI library
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict

# Create an instance of the FastAPI class
# This 'app' is the main entry point for your API
app = FastAPI(
    title="Hackathon Feedback System",
    description="A simple API to submit and retrieve product feedback. This is the backend component.",
    version="1.0.0",
)

# --- CORS Middleware ---
# This is crucial for a hackathon! It allows your frontend (running on a different address)
# to communicate with this backend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)


# --- Data Models (Data Structure) ---
# Pydantic models define the structure of your data.
# FastAPI uses these for automatic validation and documentation.

class FeedbackSubmit(BaseModel):
    """Model for submitting a new piece of feedback."""
    product_id: int = Field(..., example=1, description="The ID of the product being reviewed.")
    rating: int = Field(..., ge=1, le=5, description="A rating from 1 (bad) to 5 (great).")
    comment: str = Field(..., min_length=5, example="This product was amazing!", description="The user's written comment.")

class FeedbackDisplay(BaseModel):
    """Model for displaying feedback after it's been stored."""
    feedback_id: int
    product_id: int
    rating: int
    comment: str

# --- In-Memory Database ---
# For a hackathon, a real database is too slow to set up.
# We'll use a simple Python dictionary as a temporary, in-memory "database".
# This makes your app super fast and easy to run anywhere.
# The key will be the feedback_id, and the value will be the feedback data.
fake_feedback_db: Dict[int, FeedbackDisplay] = {}
current_feedback_id = 0

# --- API Endpoints (The URLs) ---
# These are the URLs your application will respond to.

@app.get("/")
def read_root():
    """A simple root endpoint to confirm the API is running."""
    return {"message": "Feedback API is running! Go to /docs for interactive API documentation."}

@app.post("/feedback", response_model=FeedbackDisplay, status_code=201)
def submit_feedback(feedback: FeedbackSubmit):
    """
    Submit feedback for a product.
    This endpoint receives feedback data from the frontend, validates it, and stores it.
    """
    global current_feedback_id
    current_feedback_id += 1 # Increment the ID to ensure every feedback is unique

    # Create a new feedback record to store in our database
    new_feedback = FeedbackDisplay(
        feedback_id=current_feedback_id,
        product_id=feedback.product_id,
        rating=feedback.rating,
        comment=feedback.comment
    )

    # Save it to our fake database
    fake_feedback_db[new_feedback.feedback_id] = new_feedback

    # Return the created feedback to the frontend
    return new_feedback

@app.get("/products/{product_id}/feedback", response_model=List[FeedbackDisplay])
def get_feedback_for_product(product_id: int):
    """
    Get all feedback submitted for a specific product.
    This endpoint searches our "database" and returns all matching feedback.
    """
    # Use a list comprehension for a clean and efficient way to find all feedback
    # for the given product_id.
    product_reviews = [
        feedback for feedback in fake_feedback_db.values()
        if feedback.product_id == product_id
    ]

    # While not strictly necessary for a hackathon, returning an empty list
    # is often better than an error if nothing is found.
    # if not product_reviews:
    #     raise HTTPException(
    #         status_code=404,
    #         detail=f"No feedback found for product ID {product_id}"
    #     )

    return product_reviews

