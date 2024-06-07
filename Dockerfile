# Use the official Azure Functions Python base image
FROM mcr.microsoft.com/azure-functions/python:4-python3.10

# Set the working directory in the container
WORKDIR /home/site/wwwroot

# Copy the requirements file into the container
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose the port Azure Functions runs on
EXPOSE 80

# Command to run the Azure Functions host
CMD ["python", "-m", "azure_functions_worker"]
