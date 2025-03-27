import json
import base64
import os
from io import BytesIO
from django.core.management.base import BaseCommand
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from sensors.models import DHTData, PumpData, SoilMoistureData, MotionData
import paho.mqtt.client as mqtt
from sensors.utils import send_telegram_message


# MQTT configuration
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPICS = {
    "sensor/dht11": "dht",
    "sensor/soil": "soil",
    "sensor/pir": "pir",
    "sensor/pump_status": "pump"
}

class Command(BaseCommand):
    help = 'Starts the MQTT subscriber to listen to sensor data and save to the database.'

    def handle(self, *args, **options):
        def on_connect(client, userdata, flags, rc):
            print("Connected to MQTT Broker____!")
            # for topic in MQTT_TOPICS.values():
            for topic in MQTT_TOPICS.keys():

                client.subscribe(topic)

        def on_message(client, userdata, msg):
            topic = msg.topic
            data = json.loads(msg.payload.decode())

            if topic == "sensor/dht11":
                print("in dht topic")
                DHTData.objects.create(temperature=data["temperature"], humidity=data["humidity"])
            elif topic == "sensor/soil":
                print("in soil")
                # Process soil moisture value to remove the '%' sign and convert to float
                soil_moisture_str = str(data["soil_moisture"])
                print("soil_str => ", soil_moisture_str)
                print("type of soil_str => ", type(soil_moisture_str))
                moisture_level = float(soil_moisture_str.replace('%', '').strip())
                print("in soil")
                SoilMoistureData.objects.create(moisture_level=moisture_level)
            elif topic == "sensor/pir":
                print("in pir")
                motion_detected=data["motion"]
                MotionData.objects.create(motion_detected=bool(data["motion"]))
                if motion_detected:
                    message = "🚨Alert... Motion detected in your farm! "
                    send_telegram_message(message)
                self.stdout.write(self.style.SUCCESS(f"Processed PIR sensor data: {data}"))         
            elif topic == "sensor/pump_status":
                print("in pump")
                # PumpData.objects.create(id=1,defaults={"pumpStatus": data["pumpStatus"]})
                PumpData.objects.create(pumpStatus=data["pumpStatus"])
                print("Pump data saved")

            print(f"Data saved from topic {topic}: {data}")

        # Initialize the MQTT client
        client = mqtt.Client()
        client.on_connect = on_connect
        client.on_message = on_message
        client.connect(MQTT_BROKER, MQTT_PORT, 60)

        # Start the MQTT client loop
        client.loop_forever()
