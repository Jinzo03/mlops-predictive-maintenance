# 1. Use an official lightweight Python runtime as a parent image
FROM python:3.10-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Copy the requirements file into the container
COPY requirements.txt .

# 4. Install the specified dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of the application code into the container
COPY serve_model.py .

# 6. Expose the port that FastAPI runs on
EXPOSE 8000

# 7. Run the FastAPI server using Uvicorn when the container starts
CMD ["uvicorn", "serve_model:app", "--host", "0.0.0.0", "--port", "8000"]