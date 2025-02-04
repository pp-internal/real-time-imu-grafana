import paho.mqtt.client as mqtt
import json
import sys

# Default MQTT settings (can be overridden by command-line arguments)
MQTT_BROKER_IP = "192.168.199.51"  # Default IP (if not provided as an argument)
MQTT_PORT = 1883  # Default port (if not provided as an argument)
GYROSCOPE_TOPIC = "IMU/gyroscope"
ACCELEROMETER_TOPIC = "IMU/accelerometer"


# Define callback for incoming messages
def on_message(client, userdata, msg):
    data = json.loads(msg.payload)
    print(f"Topic: {msg.topic}, Data: {data}")


# Parse command-line arguments
if len(sys.argv) >= 2:
    MQTT_BROKER_IP = sys.argv[1]
if len(sys.argv) >= 3:
    MQTT_PORT = int(sys.argv[2])

# Initialize MQTT client
mqtt_client = mqtt.Client()
mqtt_client.on_message = on_message

# Connect to the MQTT broker
mqtt_client.connect(MQTT_BROKER_IP, MQTT_PORT, 60)

# Subscribe to the topics
mqtt_client.subscribe(GYROSCOPE_TOPIC)
mqtt_client.subscribe(ACCELEROMETER_TOPIC)

# Start the loop to process incoming messages
mqtt_client.loop_forever()
