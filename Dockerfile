FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libnss3 libx11-xcb1 libxcomposite1 libxdamage1 libxext6 libxfixes3 \
    libxrandr2 libasound2 libatk1.0-0 libatk-bridge2.0-0 libcups2 \
    libdrm2 libgbm1 libgtk-3-0 libpango-1.0-0 libcairo2 libxshmfence1 \
    ca-certificates fonts-liberation curl && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    playwright install --with-deps chromium

COPY app ./app
COPY web ./web
COPY scripts ./scripts
COPY local_config.example.yaml ./

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
