import os
from google.cloud import firestore
from datetime import datetime, timezone, timedelta

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

def save_career_path(user_id: str, target_job: str, path_data: dict):
    """Saves a generated career path to the user's profile."""
    if not db:
        print("Database client not available. Cannot save path.")
        return

    path_ref = db.collection('saved_paths').document() 
    full_path_data = {
        'userId': user_id,
        'target_job': target_job,
        'path_data': path_data, 
        'saved_at': datetime.now(timezone.utc) 
    }
    try:
        path_ref.set(full_path_data)
        print(f"Successfully saved path for user: {user_id}")
    except Exception as e:
        print(f"Error saving path for user {user_id}: {e}")

def get_saved_paths(user_id: str) -> list:
    """Retrieves all saved career paths for a given user."""
    if not db:
        print("Database client not available. Cannot retrieve paths.")
        return []

    paths_list = []
    try:
        docs = db.collection('saved_paths').where('userId', '==', user_id).stream()
        for doc in docs:
            path_data = doc.to_dict()
            path_data['path_id'] = doc.id
            paths_list.append(path_data)
        print(f"Found {len(paths_list)} paths for user {user_id}")
    except Exception as e:
        print(f"Error retrieving paths for user {user_id}: {e}")
    return paths_list

def delete_saved_path(user_id: str, path_id: str):
    """Deletes a specific saved path, verifying user ownership."""
    if not db:
        print("Database client not available. Cannot delete path.")
        raise Exception("Database client not available.")

    path_ref = db.collection('saved_paths').document(path_id)
    
    try:
        doc = path_ref.get()
        if not doc.exists:
            print(f"Path {path_id} not found. Cannot delete.")
            raise Exception("Path not found.")
        
        path_data = doc.to_dict()
        if path_data.get('userId') != user_id:
            print(f"User {user_id} does not own path {path_id}. Deletion forbidden.")
            raise Exception("User does not have permission to delete this path.")

        path_ref.delete()
        print(f"Successfully deleted path {path_id} for user {user_id}")
    
    except Exception as e:
        print(f"Error deleting path {path_id} for user {user_id}: {e}")
        raise e 

def get_cached_job_skills(job_title: str) -> dict | None:
    """
    Checks the cache for a job title's skills.
    Returns the data if found and not older than 30 days.
    """
    if not db:
        print("Database client not available. Skipping cache check.")
        return None

    try:
        doc_id = job_title.lower().replace(" ", "_")
        cache_ref = db.collection('job_skills_cache').document(doc_id)
        
        doc = cache_ref.get()
        if not doc.exists:
            print(f"CACHE MISS for job: {job_title}")
            return None

        data = doc.to_dict()
        cached_at = data.get('cached_at', datetime.now(timezone.utc))

        if datetime.now(timezone.utc) - cached_at > timedelta(days=30):
            print(f"CACHE STALE for job: {job_title}")
            return None

        print(f"CACHE HIT for job: {job_title}")
        return data.get('skills_data')

    except Exception as e:
        print(f"Error getting cached skills for {job_title}: {e}")
        return None


def cache_job_skills(job_title: str, skills_data: dict):
    """Saves a job's skill data to the Firestore cache."""
    if not db:
        print("Database client not available. Cannot save to cache.")
        return

    try:
        doc_id = job_title.lower().replace(" ", "_")
        cache_ref = db.collection('job_skills_cache').document(doc_id)
        
        cache_data = {
            'job_title': job_title,
            'skills_data': skills_data, 
            'cached_at': datetime.now(timezone.utc)
        }
        cache_ref.set(cache_data)
        print(f"CACHE SAVED for job: {job_title}")

    except Exception as e:
        print(f"Error saving skills to cache for {job_title}: {e}")