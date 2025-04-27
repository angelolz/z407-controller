FROM python:3.12-slim
RUN apt-get update && \
    apt-get install -y \
    dbus \
    bluez \
    libdbus-1-dev \
    libglib2.0-dev \
    && apt-get clean
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]