#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>
 
// Replace with your network credentials
const char* ssid = "moto g52_3917";
const char* password = "asdfghjkl";
 
// MQTT Broker details
const char* mqtt_server = "192.168.89.250";
 
// Define MQTT topics
const char* tempHumTopic = "sensor/dht11";
const char* soilMoistureTopic = "sensor/soil";
const char* pirTopic = "sensor/pir";
const char* pumpStatusTopic = "sensor/pump_status";   // Topic to publish pump status
const char* pumpControlTopic = "pump/control";        // Topic to receive pump control commands
 
// Define DHT11 sensor parameters
#define DHTPIN 4          // DHT11 connected to GPIO4
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);
 
// Define other sensor pins
#define SOIL_MOISTURE_PIN 33  // Soil moisture analog pin
#define PIR_PIN 14            // PIR sensor connected to GPIO14
#define PUMP_PIN 12           // Relay connected to GPIO12 to control the pump
 
WiFiClient espClient;
PubSubClient client(espClient);
unsigned long lastMsg = 0;
const long interval = 2000;  // Publish interval in milliseconds
 
// Calibration values for soil moisture
int raw_min = 0;         // Reading from fully saturated soil
int raw_max = 4095;      // Reading from completely dry soil
 
// Thresholds for controlling the pump (adjust as needed)
const float soilMoistureThresholdLow = 20.0;  // Moisture below this value will turn the pump on
const float soilMoistureThresholdHigh = 40.0; // Moisture above this value will turn the pump off
 
bool manualPumpControl = false;  // Flag for manual control of the pump
bool pumpState = false;          // Current pump state (false = off, true = on)
 
// Function to connect to WiFi
void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);
 
  WiFi.begin(ssid, password);
 
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
 
  Serial.println();
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}
 
// Function to connect to the MQTT broker
void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    if (client.connect("ESP32Client")) {
      Serial.println("connected");
      client.subscribe(pumpControlTopic);  // Subscribe to pump control topic
      Serial.println("Subscribed to pump control topic");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}
 
// Function to control the pump
void controlPump(bool turnOn) {
//  if (pumpState != turnOn) {  // Only change the state if needed
//    delay(1000);
//    pumpState = turnOn;
//    digitalWrite(PUMP_PIN, turnOn ? HIGH : LOW);
//    delay(500);
// 
//    // Publish pump status as JSON payload
//    String pumpStatusPayload = "{\"pumpStatus\": \"" + String(turnOn ? "ON" : "OFF") + "\"}";
//    client.publish(pumpStatusTopic, pumpStatusPayload.c_str());
//    Serial.println("Pump " + String(turnOn ? "ON" : "OFF"));
//  }

  if (turnOn) {
    delay(1000);
    digitalWrite(PUMP_PIN, HIGH);  // Turn pump ON
    delay(500);
    // Publish pump status as JSON payload
    String pumpStatusPayload = "{\"pumpStatus\": \"" + String(turnOn ? "ON" : "OFF") + "\"}";
    client.publish(pumpStatusTopic, pumpStatusPayload.c_str());
    Serial.println("Pump ON");
  } else {
    delay(1000);
    digitalWrite(PUMP_PIN, LOW);   // Turn pump OFF
    delay(500);
    // Publish pump status as JSON payload
    String pumpStatusPayload = "{\"pumpStatus\": \"OFF\"}";
    client.publish(pumpStatusTopic, pumpStatusPayload.c_str());
    Serial.println("Pump OFF");
  }

}
 
// MQTT callback function
void callback(char* topic, byte* payload, unsigned int length) {
  String message = "";
  for (int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  Serial.print("Message received on topic: ");
  Serial.println(topic);
  Serial.print("Message: ");
  Serial.println(message);
 
  if (String(topic) == pumpControlTopic) {
         Serial.print("in main if  message");
    if (message == "{\"action\":\"on\"}") {
      Serial.print("in on message");
      manualPumpControl = true;  // Enable manual control
      controlPump(true);         // Turn pump ON
    } else if (message == "{\"action\":\"off\"}") {
      Serial.print("in pump off message");
      manualPumpControl = true;  // Enable manual control
      controlPump(false);        // Turn pump OFF
    }
  }
}
 
void setup() {
  Serial.begin(115200);
  setup_wifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
 
  dht.begin();
 
  pinMode(SOIL_MOISTURE_PIN, INPUT);
  pinMode(PIR_PIN, INPUT);
  pinMode(PUMP_PIN, OUTPUT);  // Set the pump control pin as output
 
  digitalWrite(PUMP_PIN, LOW);  // Ensure the pump is off initially
}
 
void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();
 
  unsigned long now = millis();
  if (now - lastMsg > interval) {
    lastMsg = now;
 
    // Read DHT11 data
    float temperature = dht.readTemperature();
    float humidity = dht.readHumidity();
 
    if (!isnan(temperature) && !isnan(humidity)) {
      String tempHumPayload = "{\"temperature\": " + String(temperature) + ", \"humidity\": " + String(humidity) + "}";
      client.publish(tempHumTopic, tempHumPayload.c_str());
      Serial.println("DHT11 Data Published: " + tempHumPayload);
    } else {
      Serial.println("Failed to read from DHT sensor!");
    }
 
    // Read and convert Soil Moisture data
    int raw_value = analogRead(SOIL_MOISTURE_PIN);
    Serial.print("Raw Soil Moisture Value: ");
    Serial.println(raw_value);
 
    float soilMoisturePercentage = 100.0 * (raw_max - raw_value) / (raw_max - raw_min);
    soilMoisturePercentage = constrain(soilMoisturePercentage, 0, 100);
 
    String soilMoisturePayload = "{\"soil_moisture\": \"" + String(soilMoisturePercentage) + "%\"}";
    client.publish(soilMoistureTopic, soilMoisturePayload.c_str());
    Serial.println("Soil Moisture Data Published: " + soilMoisturePayload);
 
    // Control the pump automatically based on soil moisture (if not in manual mode)
    if (!manualPumpControl) {
      if (soilMoisturePercentage < soilMoistureThresholdLow) {
        controlPump(true);  // Turn pump ON
      } else if (soilMoisturePercentage > soilMoistureThresholdHigh) {
        controlPump(false); // Turn pump OFF
      }
    }
 
    // Read PIR data
    int pirState = digitalRead(PIR_PIN);
    String pirPayload = "{\"motion\": " + String(pirState) + "}";
    client.publish(pirTopic, pirPayload.c_str());
    Serial.println("PIR Data Published: " + pirPayload);
    delay(1000);
  }
}
 
 
