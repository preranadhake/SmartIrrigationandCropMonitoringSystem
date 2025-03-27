import paho.mqtt.client as mqtt
import json
import random
import time


# MQTT broker details
BROKER = 'broker.emqx.io'  # Replace with your broker's address
PORT = 1883                # Default MQTT port, update if different
TOPICS = {
    # "temperature": "sensor/temperature",
    # "humidity": "sensor/humidity",
    # "soil_moisture": "sensor/soil_moisture",
    # "motion": "sensor/motion",
    # "pump_status": "sensor/pump_status"



    "sensor/dht11": "dht",
    "sensor/soil": "soil",
    "sensor/pir": "pir",
    "sensor/pump_status": "pump"
}


# Initialize MQTT client
client = mqtt.Client()


# Connect to the broker
def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print(f"Failed to connect, return code {rc}")
    client.on_connect = on_connect
    client.connect(BROKER, PORT)


# Publish data to specified topic
def publish(topic, payload):
    client.publish(topic, json.dumps(payload))
    print(f"Published to {topic}: {payload}")


# Generate and publish random dummy data
def generate_dummy_data():
    while True:
        # Generate random values for each sensor
        temperature = round(random.uniform(15.0, 30.0), 2)  # Temperature in °C
        humidity = round(random.uniform(30.0, 80.0), 2)     # Humidity in %
        # dht11 = {'temperature': temperature, 'humidity': humidity}
        soil_moisture = round(random.uniform(300, 800))     # Soil moisture level
        motion_detected = random.choice([True, False])      # Motion detected (boolean)
        pump_status = random.choice(["ON", "OFF"])          # Pump status (ON/OFF)
        # pump_status = "ON"  


        # Publish data
        # publish(TOPICS["temperature"], {"temperature": temperature})
        # publish(TOPICS["humidity"], {"humidity": humidity})
        publish(TOPICS["sensor/dht11"], {'temperature': temperature, 'humidity': humidity})
        publish(TOPICS["sensor/soil"], {"soil_moisture": soil_moisture})
        publish(TOPICS["sensor/pir"], {"motion": motion_detected})
        publish(TOPICS["sensor/pump_status"], {"pumpStatus": pump_status})


        # Wait before publishing next set of data
        time.sleep(5)  # Adjust as needed


# Main function
def run():
    connect_mqtt()
    client.loop_start()
    try:
        generate_dummy_data()
    except KeyboardInterrupt:
        print("Publishing stopped.")
    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    run()


