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

COPY .env .env
# copying local environment variables

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
# starting the FastAPI application using Uvicorn when the container runs
# "app.main:app" → points to the FastAPI instance (app variable inside main.py in app folder)
# --host 0.0.0.0 → makes the app accessible from outside the container
# --port 8000 → runs the server on port 8000
# --reload → automatically reloads the server when code changes