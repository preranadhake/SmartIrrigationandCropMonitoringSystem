The **Smart Irrigation & Crop Monitoring System** is an IoT-powered precision farming solution that automates irrigation, monitors real-time environmental conditions, and predicts crop diseases using Machine Learning. It ensures efficient water usage, disease detection, suggest remedies and pesticideson it and improved crop health—all in one system!
**The system includes:**
Soil Sensor – Monitors soil moisture & automates irrigation
DHT11 Sensor – Measures temperature & humidity
PIR Sensor – Detects motion for security alerts
Crop Disease Prediction – Identifies diseases & suggests remedies
Camera Integration – Capture or upload images for analysis
Real-time Dashboard – Visualize data with interactive charts

**Tech Stack**
Backend: Django | MQTT | SQLite
IoT Sensors: DHT11 | Soil Moisture Sensor | PIR Sensor 
Frontend: HTML | CSS | Bootstrap | javaScript | Chart.js 
Machine Learning: TensorFlow/Keras (For disease prediction)
Communication: ESP32 | Arduino | MQTT Protocol | raspberry pi

**How It Works?**
1️⃣ Sensors collect real-time data → Soil Moisture | Temperature | Humidity | Motion
2️⃣ Pump automatically switches ON/OFF based on soil moisture threshold
3️⃣ Data is sent to Django backend via MQTT protocol
4️⃣ Real-time visualization of sensor data using interactive charts
5️⃣ Disease detection model processes captured image usimg camera & suggests remedies and pesticides
6️⃣ Users can monitor & control the system remotely via the web dashboard

One can check without having the sensor is that project is working or not : Use the mqtt_code/mqtt_publisher.py file.
