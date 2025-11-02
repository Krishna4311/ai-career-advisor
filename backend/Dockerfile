FROM python:3.12-slim
WORKDIR /app

# 1. Correctly copy ONLY the backend's requirements file
COPY backend/requirements.txt .
# 2. Install them
RUN pip install --no-cache-dir -r requirements.txt

# 3. Correctly copy ONLY the backend's source code
COPY backend/ .

EXPOSE 8080

# 4. Run the FastAPI application
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]