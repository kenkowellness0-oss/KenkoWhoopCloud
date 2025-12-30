FROM python:3.10-slim

# Install dependencies
RUN apt-get update && apt-get install -y wget unzip gnupg --no-install-recommends

# Install Google Chrome stable
RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && apt-get install -y ./google-chrome-stable_current_amd64.deb \
    && rm google-chrome-stable_current_amd64.deb

# Fetch latest available Chromedriver version (matching stable support)
RUN LATEST_CHROMEDRIVER=$(wget -qO- https://chromedriver.storage.googleapis.com/LATEST_RELEASE) \
    && wget -q https://chromedriver.storage.googleapis.com/$LATEST_CHROMEDRIVER/chromedriver_linux64.zip \
    && unzip chromedriver_linux64.zip -d /usr/local/bin/ \
    && rm chromedriver_linux64.zip \
    && chmod +x /usr/local/bin/chromedriver

# Prevent Chrome sandbox issue inside containers
ENV CHROME_OPTS="--no-sandbox --disable-dev-shm-usage"

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

CMD ["python", "main.py"]
