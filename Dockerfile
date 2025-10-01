FROM python:3.12.0-slim

RUN apt-get update && \
    apt-get install -y \
    dbus \
    bluez \
    libdbus-1-dev \
    libglib2.0-dev \
    && apt-get clean

WORKDIR /app

# Copy and install dependencies first
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]