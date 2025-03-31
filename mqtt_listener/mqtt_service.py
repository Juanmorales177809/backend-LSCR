import paho.mqtt.client as mqtt
import json
import requests

print("Hola mundo exterior")
# Configura aquí la IP o dominio de tu servidor MQTT (el del ChirpStack Gateway Bridge)
MQTT_BROKER = "172.16.20.3"
MQTT_PORT = 1883  # por defecto, puede ser 8883 si usas TLS
MQTT_TOPIC = "application/+/device/+/event/up"
API_URL = "http://172.16.20.7:8000/data" 

# Si usas autenticación MQTT (ChirpStack puede tener usuario/contraseña)
MQTT_USERNAME = ""   
MQTT_PASSWORD = ""  

# Callback cuando se conecta al broker
def on_connect(client, userdata, flags, rc):
    print(f"Conectado al broker MQTT con codigo {rc}")
    client.subscribe(MQTT_TOPIC)
    print(f"Suscrito al topico: {MQTT_TOPIC}")

# Callback cuando se recibe un mensaje
def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        device_info = payload.get("deviceInfo", {})
        dev_name = device_info.get("deviceName", "N/A")
        dev_eui = device_info.get("devEui", "N/A")
        timestamp = payload.get("time", None)
        object_data = payload.get("object", {})
        messages = object_data.get("messages", [[]])[0]

        # recorrer todas las mediciones
        for m in messages:
            tipo = m.get("type")
            valor = m.get("measurementValue")
            valor = m.get("measurementValue")
            # Saltar si no es un número
            if not isinstance(valor, (int, float)):
                print("Valor no numérico, ignorado:", valor)
                continue

            ts = m.get("timestamp", timestamp)

            # construir y enviar JSON a FastAPI
            data = {
                "devEUI": dev_eui,
                "deviceName": dev_name,
                "applicationName": device_info.get("applicationName", "N/A"),
                "type": tipo,
                "measurementValue": valor,
                "timestamp": ts
            }

            response = requests.post(API_URL, json=data)
            print("Enviado a API:", response.status_code, response.json())

    except Exception as e:
        print(f"Error procesando mensaje: {e}")


# Crear cliente y configurar callbacks
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# Autenticación si aplica
# client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

# Conectar al broker
client.connect(MQTT_BROKER, MQTT_PORT, 60)

print("Escuchando mensajes MQTT...\n")
client.loop_forever()
