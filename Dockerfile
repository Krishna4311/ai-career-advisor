# --- Stage 1: Build the Frontend ---
FROM node:18-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# --- Stage 2: Build the Backend ---
FROM python:3.12-slim AS backend-builder
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- Stage 3: The Final Image ---
FROM python:3.12-slim
WORKDIR /app

# Copy installed Python dependencies from the backend-builder
COPY --from=backend-builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages

# Copy the backend application code
COPY backend/ .

# Copy the built frontend from the frontend-builder
COPY --from=frontend-builder /app/frontend/dist ./dist

# Expose the port the app runs on
EXPOSE 8080

# Command to run the application for production
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
