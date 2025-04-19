FROM python:3.9-slim

# Set working directory to /app
WORKDIR /app

# Copy requirements file
COPY requirements.txt .
#set virtul environetal
RUN python -m venv /app/env

ENV PATH="/app/env/bin:$PATH"

# Обновляем pip
RUN pip install --upgrade pip

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port 8000 for the application
EXPOSE 8000

# Run command to start the application

CMD ["uvicorn", "bridge.main:app", "--host", "--port", "8000"]