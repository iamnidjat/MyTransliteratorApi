FROM python:3.11-slim 
# a lighter version of the Python image

WORKDIR /app
# setting the working directory inside the container

COPY requirements.txt .
# copying the file with the requirements to the /app directory.

RUN pip install --no-cache-dir --upgrade -r requirements.txt
# installing all Python dependencies listed in requirements.txt inside the container
# --no-cache-dir → prevents pip from storing cache files, reducing final image size
# --upgrade → ensures the latest compatible versions of packages are installed
# -r /code/requirements.txt → tells pip to read dependencies from that file path

COPY . .
# copying the entire project from your local machine into the container's /app directory

HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD curl -f http://localhost:8000/v1/health || exit 1
# Docker will periodically check if app is alive
# Every 30 seconds, Docker runs the check
# 5 seconds is the maximum time Docker waits for the check to finish, if request takes more than 5 seconds → FAIL
# 3 consecutive failures are allowed before marking unhealthy (to prevent false alarms)
# CMD curl -f http://localhost:8000/v1/health -> This is the actual test command
# curl -f = “fail on HTTP error status codes”
# If curl fails → exit with error code 1 (unhealthy); 0 means healthy
# If /health fails → container marked unhealthy

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
# starting the FastAPI application using Uvicorn when the container runs
# "app.main:app" → points to the FastAPI instance (app variable inside main.py in app folder)
# --host 0.0.0.0 → makes the app accessible from outside the container
# --port 8000 → runs the server on port 8000
# --reload → automatically reloads the server when code changes (should be removed in production for better performance)