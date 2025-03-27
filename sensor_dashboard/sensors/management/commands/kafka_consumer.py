
import json
from kafka import KafkaConsumer
import base64
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from sensors.models import DHTData, PumpData, SoilMoistureData, MotionData
from sensors.utils import send_telegram_message

class Command(BaseCommand):
    help = 'Run Kafka consumer to process sensor data'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting Kafka consumer...'))

        # Configure the Kafka consumer
        consumer = KafkaConsumer(
            'sensor-data',
            bootstrap_servers=['192.168.202.116:9092'],
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        )

        # Consume messages
        for message in consumer:
            data = message.value
            sensor_type = data.get('sensor_type')

            if sensor_type == 'soil_moisture':
                SoilMoistureData.objects.create(moisture_level=data.get('value'))
                self.stdout.write(self.style.SUCCESS(f"Processed soil moisture data: {data}"))
            elif sensor_type == 'temp_humidity':
                DHTData.objects.create(
                    temperature=data.get('temperature'),
                    humidity=data.get('humidity')
                )
                self.stdout.write(self.style.SUCCESS(f"Processed temperature & humidity data: {data}"))
            elif sensor_type == 'pir':
                motion_detected=data.get('motion_detected')
                MotionData.objects.create(motion_detected=motion_detected)
                if motion_detected:
                    message = "🚨 Motion detected! Check your surroundings."
                    send_telegram_message(message)
                self.stdout.write(self.style.SUCCESS(f"Processed PIR sensor data: {data}"))

            elif sensor_type == 'camera':
            # Handle image data from the camera
                 image_data = data.get('image')
                 if image_data:
                    save_camera_image(image_data)
            else:
                self.stdout.write(self.style.WARNING(f"Unknown sensor type: {sensor_type}"))

def save_camera_image(encoded_image):
    """
    Decodes a base64-encoded image and saves it.
    """
    from sensors.models import CameraImageData  # Import the model

    # Decode base64 image
    try:
        image_binary = base64.b64decode(encoded_image)
        # Save the image
        image_instance = CameraImageData()
        image_instance.image.save('camera_image.jpg', ContentFile(image_binary))
        image_instance.save()
        print("Saved camera image successfully.")
    except Exception as e:
        print(f"Failed to save camera image: {e}")
