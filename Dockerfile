FROM python:3.13-slim

WORKDIR /app

# Copy only the requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Make the script executable
RUN chmod +x deployment_finder.py

# Set the entrypoint to the CLI tool
ENTRYPOINT ["./deployment_finder.py"]
