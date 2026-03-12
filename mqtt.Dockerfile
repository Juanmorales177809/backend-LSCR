FROM python:3.10-slim

# Instala herramientas de red sin conflicto
RUN apt update && apt install -y \
    iputils-ping \
    net-tools \
    iproute2 \
    dnsutils \
    telnet \
    && apt clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY mqtt_listener/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY mqtt_listener/mqtt_service.py .
COPY mqtt_listener/prueba.py .

CMD ["python", "prueba.py"]

