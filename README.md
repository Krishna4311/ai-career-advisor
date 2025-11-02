
# Career Craft: AI Career Advisor

## Live Application: https://pcsr-v2.web.app

Career Craft is an intelligent, full-stack web application that acts as a personalized career advisor. It uses Google's Gemini AI to analyze a user's skills against their career goals, providing personalized job suggestions and actionable, step-by-step career roadmaps.

The application's primary goal is to empower users with a clear, personalized plan to navigate from their current position to their desired career.

## Core Features

  * **AI Job Suggestions:** Users can upload a resume (PDF/DOCX) to receive a tailored list of recommended jobs, complete with match scores and AI-parsed skills.
  * **Dynamic Career Path Generation:** Users receive a detailed, step-by-step plan for a target job, including milestones, new skills to learn, and recommended actions.
  * **Skill Gap Analysis:** Manually input skills and a target job to see which skills are matching and which are missing.
  * **Personalized Dashboard:** Securely save generated career paths to a user profile to review them later, and delete them when no longer needed.

-----

## Technical Architecture

This project uses a decoupled, full-stack architecture hosted entirely on the Google Cloud Platform.

  * **Frontend:** A **React (Vite)** single-page application. It is responsible for all UI rendering and user interaction.
  * **Backend:** A **FastAPI (Python)** asynchronous API server. It handles all business logic, authentication, and communication with the AI and database.
  * **AI Model:** **Google Gemini Flash** is used via its Python SDK to perform all generative tasks (parsing, suggesting, and planning).
  * **Database:** **Google Firestore** (NoSQL) is used to store user data, saved career paths, and cache AI responses.
  * **Hosting & Proxy:** **Firebase Hosting** serves the static React application. Its **rewrite rules** are used as a proxy, securely forwarding all API calls (e.g., `/api/**`) to the backend service.
  * **Backend Infrastructure:** **Google Cloud Run** hosts the containerized FastAPI backend, allowing it to scale independently.
  * **Authentication:** **Firebase Authentication** handles user sign-up, login (including Google OAuth), and secure token verification.

-----

## Application Workflows

Below are the text-based flows for the application's core features. All API requests are securely proxied through Firebase Hosting to the Cloud Run backend.

### Workflow 1: Job Suggestion (from Resume)

This flow is triggered when a user uploads their resume.

```
[User (Browser)]
    |
    1. Uploads "resume.pdf" to the React frontend.
    |
    v
[Frontend (Firebase Hosting)]
    |
    2. Attaches the Firebase Auth token to the request.
    3. Sends a POST request to the relative path: "/api/suggest-jobs".
    |
    v
[Backend (Cloud Run - FastAPI)]
    |
    4. Receives request, verifies Auth token, and parses the "resume.pdf" into text.
    5. Sends the text to the Gemini AI with a prompt to extract skills and suggest jobs.
    |
    v
[Google AI (Gemini)]
    |
    6. Analyzes the text and returns a structured JSON object:
       { "parsed_skills": [...], "suggestions": [...] }
    |
    v
[Backend (Cloud Run - FastAPI)]
    |
    7. Saves the "parsed_skills" to the user's profile in Firestore.
    8. Returns the JSON with job suggestions to the frontend.
    |
    v
[Frontend (Firebase Hosting)]
    |
    9. Renders the list of suggested jobs and parsed skills for the user.
```

### Workflow 2: Career Path Generation

This flow is triggered when a user fills out the "Career Path" form.

```
[User (Browser)]
    |
    1. Enters "Current Skills" and a "Target Job" into the form.
    2. Clicks "Generate Career Path".
    |
    v
[Frontend (Firebase Hosting)]
    |
    3. Attaches the Firebase Auth token to the request.
    4. Sends a POST request with the JSON payload to "/api/generate-path".
    |
    v
[Backend (Cloud Run - FastAPI)]
    |
    5. Receives request and verifies the Auth token.
    6. Sends the skills and job title to the Gemini AI with a prompt to generate a plan.
    |
    v
[Google AI (Gemini)]
    |
    7. Analyzes the request and returns a structured JSON object:
       { "milestones": [...], "next_skills": [...], "recommended_actions": [...] }
    |
    v
[Backend (Cloud Run - FastAPI)]
    |
    8. Returns the JSON path data to the frontend.
    |
    v
[Frontend (Firebase Hosting)]
    |
    9. Renders the complete, step-by-step career path for the user.
```

### Workflow 3: Saving and Viewing a Path

This flow covers both saving a new path and retrieving all saved paths.

**A) Saving a Path:**

```
[User (Browser)]
    |
    1. Clicks "Save this Path" after a path is generated.
    |
    v
[Frontend (Firebase Hosting)]
    |
    2. Attaches the Auth token.
    3. Sends a POST request with the path data to "/api/save-path".
    |
    v
[Backend (Cloud Run - FastAPI)]
    |
    4. Receives request and verifies the Auth token.
    5. Creates a new document in the "saved_paths" collection in Firestore, associating it with the user's ID.
    6. Returns a "200 OK" success message.
```

**B) Viewing Saved Paths:**

```
[User (Browser)]
    |
    1. Clicks the "Saved Paths" button in the navigation bar.
    |
    v
[Frontend (Firebase Hosting)]
    |
    2. Attaches the Auth token.
    3. Sends a GET request to "/api/my-paths".
    |
    v
[Backend (Cloud Run - FastAPI)]
    |
    4. Receives request and verifies the Auth token.
    5. Queries the "saved_paths" collection in Firestore for all documents where "userId" matches the user's ID.
    6. Returns a JSON list of all found paths.
    |
    v
[Frontend (Firebase Hosting)]
    |
    7. Renders the list of saved paths in the sidebar.
```
