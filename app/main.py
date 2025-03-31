from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from pymongo import MongoClient
from typing import Optional
from datetime import datetime
import os

# Cargar variables de entorno
INFLUX_URL = os.getenv("INFLUX_URL")
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN")
INFLUX_ORG = os.getenv("INFLUX_ORG")
INFLUX_BUCKET = os.getenv("INFLUX_BUCKET")
MONGO_URL = os.getenv("MONGO_URL")


# Inicializar InfluxDB
influx_client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
write_api = influx_client.write_api(write_options=SYNCHRONOUS)

# Inicializar MongoDB
mongo_client = MongoClient(MONGO_URL)
mongo_db = mongo_client["iot_db"]
mongo_collection = mongo_db["uplinks"]

# FastAPI
app = FastAPI(title="LSCR", description="API para recibir datos IoT y guardarlos en InfluxDB + MongoDB")

# 📘 Modelos Pydantic
class SensorData(BaseModel):
    devEUI: str
    deviceName: str
    applicationName: str
    type: str
    measurementValue: float
    timestamp: Optional[datetime] = None

class DataResponse(BaseModel):
    status: str
    message: str

# ✅ Endpoint POST
@app.post("/data", response_model=DataResponse)
def receive_data(data: SensorData):
    try:
        # Guardar en InfluxDB
        point = (
            Point("sensor_data")
            .tag("devEUI", data.devEUI)
            .tag("deviceName", data.deviceName)
            .tag("applicationName", data.applicationName)
            .tag("type", data.type)
            .field("measurementValue", data.measurementValue)
        )
        if data.timestamp:
            point = point.time(data.timestamp)

        write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=point)

        # Guardar en MongoDB
        mongo_doc = data.dict()
        if not mongo_doc.get("timestamp"):
            mongo_doc["timestamp"] = datetime.utcnow()
        mongo_collection.insert_one(mongo_doc)

        return DataResponse(
            status="success",
            message="Datos guardados en InfluxDB y MongoDB"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
