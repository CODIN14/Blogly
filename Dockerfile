FROM python:3.11-slim

WORKDIR /app
COPY . .

# Upgrade pip and install dependencies with increased timeout
RUN pip install --upgrade pip --default-timeout=100 && \
    pip install -r requirements.txt --default-timeout=100

# Ensure gunicorn is installed
RUN pip install gunicorn --default-timeout=100

EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]