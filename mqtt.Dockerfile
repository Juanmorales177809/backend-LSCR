FROM python:3.10-slim

WORKDIR /app

COPY mqtt_listener/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY mqtt_listener/mqtt_service.py .
COPY mqtt_listener/prueba.py .
CMD ["python", "prueba.py"]
