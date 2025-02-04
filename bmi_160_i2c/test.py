import time
import paho.mqtt.client as mqtt
import json
from bmi160 import BMI160

# Sleep time between reading motion data
SLEEP_TIME = 0.1

# MQTT settings
MQTT_BROKER_IP = "localhost"
MQTT_PORT = 1883
GYROSCOPE_TOPIC = "IMU/gyroscope"
ACCELEROMETER_TOPIC = "IMU/accelerometer"


def main():
    # Initialize the BMI160 sensor
    bmi160_sensor = BMI160(0x69) # Pass the i2c address of BMI160

    # Initialize MQTT client
    mqtt_client = mqtt.Client()
    mqtt_client.connect(MQTT_BROKER_IP, MQTT_PORT, 60)

    # Read motion data every SLEEP_TIME seconds
    while True:
        motion_data = bmi160_sensor.read_motion_data()

        if motion_data:
            # Print the motion data in a readable format
            print(
                f"Gyroscope - X: {motion_data['gx']}, Y: {motion_data['gy']}, Z: {motion_data['gz']}")
            print(
                f"Accelerometer - X: {motion_data['ax']}, Y: {motion_data['ay']}, Z: {motion_data['az']}")
            
            # Prepare gyroscope and accelerometer data for publishing
            gyroscope_data = {
                'gx': motion_data['gx'],
                'gy': motion_data['gy'],
                'gz': motion_data['gz']
            }
            accelerometer_data = {
                'ax': motion_data['ax'],
                'ay': motion_data['ay'],
                'az': motion_data['az']
            }

            # Publish gyroscope data to the GYROSCOPE_TOPIC
            mqtt_client.publish(GYROSCOPE_TOPIC, payload=json.dumps(gyroscope_data))

            # Publish accelerometer data to the ACCELEROMETER_TOPIC
            mqtt_client.publish(ACCELEROMETER_TOPIC, payload=json.dumps(accelerometer_data))
        else:
            print("Failed to read motion data.")

        # Sleep for before reading again
        time.sleep(SLEEP_TIME)


if __name__ == "__main__":
    main()