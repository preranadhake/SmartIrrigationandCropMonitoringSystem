import json
import paho.mqtt.client as mqtt
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages

from sensor_dashboard import settings
from .models import DHTData, PumpData, SoilMoistureData, MotionData
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from .serializers import MotionDataSerializer
from sensors.utils import send_telegram_message

MQTT_BROKER = "localhost"  
MQTT_PORT = 1883
MQTT_PUMP_TOPIC = "pump/control"  

mqtt_client = mqtt.Client()
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
mqtt_client.loop_start()  


def get_latest_sensor_data(request):
    one_hour_ago = timezone.now() - timedelta(hours=1)
    dht_data = DHTData.objects.filter(timestamp__gte=one_hour_ago).order_by('timestamp')
    soil_data = SoilMoistureData.objects.filter(timestamp__gte=one_hour_ago).order_by('timestamp')
    motion_data = MotionData.objects.filter(timestamp__gte=one_hour_ago).order_by('timestamp')
    pump_data = PumpData.objects.last()
    pump_status = pump_data.pumpStatus if pump_data else 'OFF'

    response_data = {
        'temperature': [data.temperature for data in dht_data],
        'humidity': [data.humidity for data in dht_data],
        'soil_moisture': [data.moisture_level for data in soil_data],
        'motion': [1 if data.motion_detected else 0 for data in motion_data],
        'timestamps': [data.timestamp.strftime("%H:%M:%S") for data in dht_data],
        'pump_status': pump_status
    }
    return JsonResponse(response_data)


def get_data_for_dashboard(request):
    dht_data = DHTData.objects.last()
    temp = dht_data.temperature if dht_data else None
    humid = dht_data.humidity if dht_data else None
    soil_data = SoilMoistureData.objects.last()
    soil_moisture = soil_data.moisture_level if soil_data else None
    latest_motion_data = MotionData.objects.last()
    motion_detected = latest_motion_data.motion_detected if latest_motion_data else False
    pump_data = PumpData.objects.last()
    pump_status = pump_data.pumpStatus if pump_data else 'OFF'

    response_data = {
        'temperature': temp,
        'humidity': humid,
        'soil_moisture': soil_moisture,
        'motion': motion_detected,
        'pump_status': pump_status
    }
    return JsonResponse(response_data)


@login_required
def chart(request):
    return render(request, 'sensors/charts.html')


@login_required
def dashboard(request):
    return render(request, 'sensors/dashboard.html')


def get_pump_status(request):
    pump_data = PumpData.objects.last()
    pump_status = pump_data.pumpStatus if pump_data else 'OFF'
    return JsonResponse({'pump_status': pump_status})


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')


def user_logout(request):
    logout(request)
    return redirect('login')


def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        if password != password2:
            messages.error(request, 'Passwords do not match.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
        else:
            User.objects.create_user(username=username, password=password)
            messages.success(request, 'Registration successful. Please log in.')
            return redirect('login')
    return render(request, 'register.html')


@login_required
def pump_control(request):
    """
    Render the pump control page and handle pump on/off commands using MQTT.
    """
    if request.method == 'POST':
        action = request.POST.get('action')  
        if action in ['on', 'off']:
            try:
                mqtt_client.publish(MQTT_PUMP_TOPIC, json.dumps({'action': action}))
                # return render(request, 'pump_control.html')
                return JsonResponse({'status': 'success', 'action': action})
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': str(e)})
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid action'})

    return render(request, 'pump_control.html')


def handle_motion_event(motion_detected):
    MotionData.objects.create(
        motion_detected=motion_detected,
        timestamp=timezone.now()
    )


def motion_data_view(request):
    motion_data_records = MotionData.objects.all().order_by('-timestamp')
    return render(request, 'motion_data.html', {'motion_data_records': motion_data_records})
