# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the requirements file into the container
COPY requirements.txt ./

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Make port 8080 available to the world outside this container
EXPOSE 8080
ENV GRADIO_SERVER_NAME="0.0.0.0"

# Run the application
CMD ["python", "./demo/app.py"]