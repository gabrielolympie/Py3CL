# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose streamlit port
EXPOSE 8501

# Make sure the script is executable
RUN chmod +x launch_demo.sh

# Run launch_demo.sh when the container launches
ENTRYPOINT ["sh", "./launch_demo.sh"]