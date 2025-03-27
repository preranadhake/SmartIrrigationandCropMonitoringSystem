import base64
import os
import json
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array, load_img
from django.shortcuts import render, get_object_or_404
from django.core.files.storage import default_storage
from django.http import JsonResponse
from .models import DiseasePrediction
import paho.mqtt.client as mqtt
from django.conf import settings
import threading
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect, get_object_or_404
from .models import DiseasePrediction

MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_PUBLISH_TOPIC = "camera/capture"
MQTT_PHOTO_TOPIC = "camera/photo"

model_path = os.path.join(os.path.dirname(__file__), 'best_model.keras')
model = load_model(model_path)
class_names = [
    'Apple___Apple_scab', 'Apple___Black_rot', 'Apple___Cedar_apple_rust', 'Apple___healthy', 'Blueberry___healthy',
    'Cherry___Powdery_mildew', 'Cherry___Healthy', 'Corn___Cercospora_leaf_spot_Gray_leaf_spot',
    'Corn___Common_rust', 'Corn___Northern_Leaf_Blight', 'Corn___healthy',
    'Grape___Black_rot', 'Grape___Esca_(Black_Measles)', 'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)', 'Grape___healthy',
    'Potato___Early_blight', 'Potato___Late_blight', 'Potato___healthy', 'Tomato___Bacterial_spot',
    'Tomato___Early_blight', 'Tomato___healthy', 'Tomato___Late_blight', 'Tomato___Leaf_Mold', 'Tomato___Septoria_leaf_spot',
    'Tomato___Spider_mites Two-spotted_spider_mite', 'Tomato___Target_Spot', 'Tulsi___Healthy',
]

disease_remedies = {
    'Apple___Apple_scab': {
        'remedies': 'Prune infected leaves and branches. Remove fallen leaves to reduce fungal spread. Improve air circulation by proper spacing.',
        'pesticides': 'Mancozeb, Captan, or Chlorothalonil.'
    },
    'Apple___Black_rot': {
        'remedies': 'Remove mummified fruits and cankers. Use resistant varieties and maintain orchard sanitation.',
        'pesticides': 'Thiophanate-methyl or Lime-sulfur sprays.'
    },
    'Apple___Cedar_apple_rust': {
        'remedies': 'Prune and destroy infected leaves and twigs. Avoid planting apple trees near cedar trees.',
        'pesticides': 'Fungicides containing Myclobutanil or Mancozeb.'
    },
    'Apple___healthy': {
        'remedies': 'No action needed. Continue regular maintenance and monitoring.',
        'pesticides': 'None.'
    },
    'Blueberry___healthy': {
        'remedies': 'Continue regular care with proper irrigation and pest monitoring.',
        'pesticides': 'None.'
    },
    'Cherry___Powdery_mildew': {
        'remedies': 'Prune infected branches to improve air circulation. Avoid overhead watering.',
        'pesticides': 'Sulfur-based fungicides or Potassium bicarbonate.'
    },
    'Cherry___Healthy': {
        'remedies': 'No action needed. Maintain regular care practices.',
        'pesticides': 'None.'
    },
    'Corn___Cercospora_leaf_spot_Gray_leaf_spot': {
        'remedies': 'Rotate crops to avoid overwintering pathogens. Use resistant hybrids.',
        'pesticides': 'Azoxystrobin or Propiconazole.'
    },
    'Corn___Common_rust': {
        'remedies': 'Use disease-resistant hybrids. Avoid excessive irrigation.',
        'pesticides': 'Mancozeb or Tebuconazole.'
    },
    'Corn___Northern_Leaf_Blight': {
        'remedies': 'Use resistant varieties and avoid dense planting. Destroy infected crop residue.',
        'pesticides': 'Azoxystrobin or Mancozeb.'
    },
    'Corn___healthy': {
        'remedies': 'No action needed. Regular monitoring and maintenance.',
        'pesticides': 'None.'
    },
    'Grape___Black_rot': {
        'remedies': 'Remove and destroy mummified berries and infected leaves. Maintain proper spacing for ventilation.',
        'pesticides': 'Mancozeb or Captan.'
    },
    'Grape___Esca_(Black_Measles)': {
        'remedies': 'Prune out infected wood and remove heavily infected vines. Maintain soil fertility.',
        'pesticides': 'Fungicides are generally not effective for this disease. Focus on cultural practices.'
    },
    'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)': {
        'remedies': 'Remove infected leaves and avoid excessive overhead irrigation.',
        'pesticides': 'Copper-based fungicides or Mancozeb.'
    },
    'Grape___healthy': {
        'remedies': 'No action needed. Regular monitoring is sufficient.',
        'pesticides': 'None.'
    },
    'Potato___Early_blight': {
        'remedies': 'Remove infected plant debris. Use certified disease-free seeds.',
        'pesticides': 'Mancozeb or Chlorothalonil.'
    },
    'Potato___Late_blight': {
        'remedies': 'Destroy infected plants and avoid overhead watering. Rotate crops annually.',
        'pesticides': 'Copper-based fungicides or Mancozeb.'
    },
    'Potato___healthy': {
        'remedies': 'No action needed. Continue regular care and monitoring.',
        'pesticides': 'None.'
    },
    'Tomato___Bacterial_spot': {
        'remedies': 'Remove infected leaves and practice crop rotation.',
        'pesticides': 'Copper-based fungicides or Streptomycin.'
    },
    'Tomato___Early_blight': {
        'remedies': 'Remove infected leaves and improve air circulation.',
        'pesticides': 'Chlorothalonil or Mancozeb.'
    },
    'Tomato___healthy': {
        'remedies': 'No action needed. Continue regular care and monitoring.',
        'pesticides': 'None.'
    },
    'Tomato___Late_blight': {
        'remedies': 'Remove infected plant parts and avoid overhead irrigation.',
        'pesticides': 'Metalaxyl or Mancozeb.'
    },
    'Tomato___Leaf_Mold': {
        'remedies': 'Prune infected leaves and improve air circulation.',
        'pesticides': 'Neem oil or Sulfur-based fungicides.'
    },
    'Tomato___Septoria_leaf_spot': {
        'remedies': 'Remove infected leaves and improve irrigation practices.',
        'pesticides': 'Copper-based fungicides.'
    },
    'Tomato___Spider_mites Two-spotted_spider_mite': {
        'remedies': 'Remove infested leaves and use insecticidal soap.',
        'pesticides': 'Acaricides like Spiromesifen or Abamectin.'
    },
    'Tomato___Target_Spot': {
        'remedies': 'Remove infected leaves and improve air circulation.',
        'pesticides': 'Mancozeb or Chlorothalonil.'
    },
    'Tulsi___Healthy': {
        'remedies': 'Regular watering and fertilization. Monitor for pest attacks.',
        'pesticides': 'None.'
    },
}

captured_photo_path = "D:/python/sm/raspi_photos"

def mqtt_subscribe_photo():
    """
    Subscribe to MQTT topic and save incoming photo.
    """
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
            client.subscribe(MQTT_PHOTO_TOPIC)
        else:
            print(f"Failed to connect to MQTT Broker. Return code: {rc}")

    def on_message(client, userdata, msg):
        global captured_photo_path
        data = json.loads(msg.payload.decode())
        image_data = data.get("image")
        print("image_data==>", image_data)
        if image_data:
            image_bytes = base64.b64decode(image_data)
            captured_photo_path = os.path.join(settings.MEDIA_ROOT, 'photos', 'captured_photo.jpg')
            os.makedirs(os.path.dirname(captured_photo_path), exist_ok=True)
            with open(captured_photo_path, "wb") as f:
                f.write(image_bytes)
            print(f"Captured photo saved at {captured_photo_path}")
    
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()

threading.Thread(target=mqtt_subscribe_photo, daemon=True).start()

def predict_disease(image_path):
    """
    Predict the disease based on the uploaded or captured image.
    """
    print("in predict disease function")
    image = load_img(image_path, target_size=(128, 128))
    print("after load image")
    image = img_to_array(image)
    image = np.expand_dims(image, axis=0) / 255.0
    prediction = model.predict(image)
    max_probability = np.max(prediction)
    predicted_class = np.argmax(prediction, axis=1)
    print("predicted Class==>", predicted_class)

    disease_name = class_names[predicted_class[0]]
    remedies = disease_remedies.get(disease_name, {'remedies': 'No information available.', 'pesticides': 'No information available.'})
    return disease_name, max_probability, remedies

def upload_and_predict(request):
    """
    Handle manual upload and prediction.
    """
    predictions = DiseasePrediction.objects.order_by('-timestamp')[:5]

    if request.method == 'POST' and request.FILES['image']:
        image = request.FILES['image']
        image_path = default_storage.save(os.path.join('tmp', image.name), image)
        full_image_path = os.path.join(settings.MEDIA_ROOT, image_path)
        print("image Path ==>", image_path)
        image_url = default_storage.url(full_image_path)
        print("image_url==> ", image_url)
        
        try:
            prediction, probability, remedies = predict_disease(full_image_path)
            confidence_message = None
            if probability < 0.8:
                confidence_message = "Prediction may not be accurate."

            prediction_record = DiseasePrediction.objects.create(
                image_name=image.name,
                predicted_disease=prediction,
                remedy=remedies['remedies'],
                pesticides=remedies['pesticides']
            )

            return render(request, 'prediction/result.html', {
                'prediction': prediction,
                'probability': probability,
                'remedies': remedies,
                'image_url': image_url,
                'record_id': prediction_record.id,
                'confidence_message': confidence_message
            })


        except Exception as e:
            print("in exception")
            return render(request, 'prediction/result.html', {'error': str(e)})

    return render(request, 'prediction/upload.html', {'predictions': predictions})

@csrf_exempt
def capture_and_predict(request):
    """
    Trigger photo capture and predict the disease once the photo is captured.
    """
    global captured_photo_path
    if request.method == 'POST':
        
        try:
            print("in try  if request.method POST", request.method)
            mqtt_client = mqtt.Client()
            mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
            mqtt_client.publish(MQTT_PUBLISH_TOPIC, json.dumps({"action": "capture_photo"}))
            mqtt_client.disconnect()
            return JsonResponse({"status": "success", "message": "Capture event triggered. Wait for the photo to be captured."})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})

    if captured_photo_path and os.path.exists(captured_photo_path):
        try:
            prediction, probability, remedies = predict_disease(captured_photo_path)
            prediction_record = DiseasePrediction.objects.create(
                image_name="captured_photo.jpg",
                predicted_disease=prediction,
                remedy=remedies['remedies'],
                pesticides=remedies['pesticides']
            )

            return render(request, 'prediction/result.html', {
                'prediction': prediction,
                'probability': probability,
                'remedies': remedies,
                'image_url': f'/media/photos/captured_photo.jpg',
                'record_id': prediction_record.id
            })
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})
    
    return render(request, 'prediction/upload.html')

def prediction_detail(request, prediction_id):
    prediction = get_object_or_404(DiseasePrediction, id=prediction_id)
    return render(request, 'prediction/prediction_detail.html', {'prediction': prediction})
