# AI Career Advisor

This web application provides personalized career advice by analyzing a user's resume using a generative AI model.

## Project Status
 ongoing

## Setup Instructions
Before running this application, you must configure your local environment by creating the necessary secret files.

### 1. Backend Setup

The backend requires a Google Cloud service account key and a Gemini API key.

1.  **Create `.env` file:**
    *   Navigate to the `backend/` directory.
    *   Create a copy of the example file: `cp .env.example .env`
    *   Open the new `.env` file and add your Google Gemini API key:
        ```
        GEMINI_API_KEY=YOUR_API_KEY_HERE
        ```

2.  **Create `serviceAccountKey.json`:**
    *   Go to your [Google Cloud Console](https://console.cloud.google.com/).
    *   Navigate to **IAM & Admin > Service Accounts**.
    *   Select your project and find the appropriate service account (or create a new one with the necessary permissions for Firebase and Firestore).
    *   Click on the service account, go to the **Keys** tab, and click **Add Key > Create new key**.
    *   Choose **JSON** as the key type and click **Create**. A JSON file will be downloaded.
    *   Rename this file to `serviceAccountKey.json` and place it inside the `backend/` directory.

    **IMPORTANT:** The `serviceAccountKey.json` file is highly sensitive. It is listed in `.gitignore` and must never be committed to version control.

### 2. Frontend Setup

The frontend requires your Firebase project configuration.

1.  **Create `.env` file:**
    *   Navigate to the `frontend/` directory.
    *   Create a copy of the example file: `cp .env.example .env`
    *   Open the new `.env` file and replace the placeholder values with your actual Firebase project credentials. You can find these in your Firebase project settings.

        ```
        # Firebase configuration
        VITE_FIREBASE_API_KEY="YOUR_API_KEY"
        VITE_FIREBASE_AUTH_DOMAIN="YOUR_PROJECT_ID.firebaseapp.com"
        # ... and so on for all variables
        ```
