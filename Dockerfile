FROM python:3.12.10-slim

# Set working directory to /app
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

#set virtul environetal
RUN python -m venv /app/settings

ENV PATH="/app/settings/env/bin:$PATH"

# Install dependencies
RUN pip install --no-cache-dir --upgrade -r requirements.txt
RUN pip install --no-cache-dir faststream[rabbit]

# Copy application code
COPY . .

# Expose port 8000 for the application
EXPOSE 8000

# Run command to start the application

CMD ["uvicorn", "main:app", "--host", "0.0.0.0" , "--port", "8000"]