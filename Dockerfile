# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set the working directory in the container
WORKDIR /app

# Install system dependencies needed by the project
# g++ is needed to compile the C++ shared library
# git is needed if you want to clone repositories inside the container build process
RUN apt-get update && apt-get install -y \
    build-essential \
    g++ \
    git \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Copy the current directory contents into the container at /app
COPY .

# Install any needed Python packages specified in requirements.txt
# Since we didn't explicitly create a requirements.txt, we'll install directly
# from the packages we know we need.
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    pydantic \
    google-cloud-translate

# Build the C++ shared library inside the Docker image
WORKDIR /app/Krishi-Veda-Module/vedic_engine/
RUN g++ -O3 -shared -fPIC anurupyena.cpp paravartya.cpp -o vedic_kernels.so

# Return to the app root directory
WORKDIR /app

# Expose the port that the application will run on
EXPOSE 8000

# Run the FastAPI application using Uvicorn
CMD exec uvicorn main:app --host 0.0.0.0 --port 8000
