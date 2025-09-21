import os
from google.cloud import firestore
from datetime import datetime, timezone

# --- Firestore Client Initialization ---
try:
    db = firestore.Client()
    print("Firestore client initialized successfully.")
except Exception as e:
    print(f"Error initializing Firestore client: {e}")
    db = None

# --- Database Functions ---

def save_user_skills(user_id: str, skills: list):
    """Saves or updates a user's skills in the Firestore database."""
    if not db:
        print("Database client not available. Cannot save skills.")
        return
    
    user_ref = db.collection('users').document(user_id)
    user_data = {
        'userId': user_id,
        'skills': skills,
        'last_updated': datetime.now(timezone.utc)
    }
    try:
        user_ref.set(user_data)
        print(f"Successfully saved skills for user: {user_id}")
    except Exception as e:
        print(f"Error saving skills for user {user_id}: {e}")

# --- NEW V2 FUNCTION ---
def save_feedback(suggestion_id: str, job_title: str, user_id: str, rating: str):
    """
    Saves user feedback for a specific job suggestion.

    Args:
        suggestion_id: The unique ID of the suggestion.
        job_title: The job title that was suggested.
        user_id: The unique identifier for the user.
        rating: The user's rating (e.g., 'helpful' or 'not_helpful').
    """
    if not db:
        print("Database client not available. Cannot save feedback.")
        return
        
    # We'll use the suggestion_id as the document ID for simplicity
    feedback_ref = db.collection('feedback').document(suggestion_id)
    feedback_data = {
        'suggestion_id': suggestion_id,
        'job_title': job_title,
        'user_id': user_id,
        'rating': rating,
        'timestamp': datetime.now(timezone.utc)
    }
    try:
        feedback_ref.set(feedback_data)
        print(f"Successfully saved feedback for suggestion: {suggestion_id}")
    except Exception as e:
        print(f"Error saving feedback for suggestion {suggestion_id}: {e}")
