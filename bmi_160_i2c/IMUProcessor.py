import time
import json
import numpy as np
import matplotlib.pyplot as plt
from bmi160 import BMI160
import paho.mqtt.client as mqtt

# MQTT settings
MQTT_BROKER_IP = "localhost"  # IP address of MQTT broker
MQTT_PORT = 1883  # Port for MQTT communication
MQTT_KEEPALIVE_INTERVAL = 60  # MQTT keep-alive interval (in seconds)
GYROSCOPE_TOPIC = "IMU/gyroscope"  # MQTT topic for gyroscope data
ACCELEROMETER_TOPIC = "IMU/accelerometer"  # MQTT topic for accelerometer data
SPEED_TOPIC = "IMU/speed"  # MQTT topic for speed data
ORIENTATION_TOPIC = "IMU/orientation"  # MQTT topic for orientation data

# BMI160 configuration
DEFAULT_BMI160_ADDRESS = 0x69
SENSITIVITY = 16384.0  # LSB/g for ±2g range (BMI160 default setting)
NORMALIZATION_FACTOR = 5000  # Adjust based on the range of your gyroscope values

# Constants
NOISE_THRESHOLD = 0.05  # Minimum acceleration (in g) to consider, filters out noise
DECAY_FACTOR = 0.5  # Factor to reduce velocity when stationary
GRAVITY_CONSTANT = 9.8  # Earth's gravitational acceleration in m/s²
MS_TO_KMPH = 3.6  # Conversion factor from m/s to km/h
STATIONARY_RESET_THRESHOLD = 0.7  # Threshold for detecting if device is stationary
STATIONARY_ITERATIONS_THRESHOLD = 20  # Number of iterations to consider the device stationary
UPSIDE_DOWN_THRESHOLD = -9.0  # Threshold for detecting if the device is upside down. approximate acceleration (in m/s²) along the z-axis
MAX_ORIENTATION_ANGLE = 90  # Maximum orientation angle (in degrees) for pitch or roll

# Sleep time between reading motion data
SLEEP_TIME = 0.1


class IMUSensorManager:
    """
    Class for managing and reading data from the BMI160 sensor,
    processing motion data, and publishing it over MQTT.
    """

    def __init__(self, i2c_address, mqtt_broker, mqtt_port):
        # Initialize BMI160 sensor and MQTT client
        self.sensor = BMI160(i2c_address)
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.connect(mqtt_broker, mqtt_port,
                                 MQTT_KEEPALIVE_INTERVAL)

        # MQTT Topics or sending different data
        self.gyroscope_topic = GYROSCOPE_TOPIC
        self.accelerometer_topic = ACCELEROMETER_TOPIC
        self.speed_topic = SPEED_TOPIC
        self.orientation_topic = ORIENTATION_TOPIC

        # Speed calculation constants
        self.sensitivity = SENSITIVITY
        self.noise_threshold = NOISE_THRESHOLD
        self.decay_factor = DECAY_FACTOR
        self.stationary_reset_threshold = STATIONARY_RESET_THRESHOLD

        # Initial velocity and time tracking
        self.velocity = np.array([0.0, 0.0, 0.0])
        self.last_time = time.time()
        self.stationary_count = 0

    def read_and_publish(self):
        """
        Reads motion data from the BMI160 sensor and publishes it over MQTT.
        """
        motion_data = self.sensor.read_motion_data()  # Read motion data
        if motion_data:
            # Pass data to methods for processing and publishing
            self.gyroscope_accelerometer(motion_data)
            self.detect_speed(motion_data)
            self.detect_orientation(motion_data)

    def gyroscope_accelerometer(self, motion_data):
        """
        Publishes gyroscope and accelerometer data to MQTT.
        """
        if motion_data:
            # Prepare gyroscope data for MQTT
            gyroscope_data = {
                'gx': motion_data['gx'],
                'gy': motion_data['gy'],
                'gz': motion_data['gz']
            }
            # Prepare accelerometer data for MQTT
            accelerometer_data = {
                'ax': motion_data['ax'],
                'ay': motion_data['ay'],
                'az': motion_data['az']
            }

            # Publish data to respective MQTT topics
            self.mqtt_client.publish(self.gyroscope_topic,
                                     payload=json.dumps(gyroscope_data))
            self.mqtt_client.publish(self.accelerometer_topic,
                                     payload=json.dumps(accelerometer_data))

    def detect_speed(self, motion_data):
        """
        Detects speed based on accelerometer data and publishes it.
        """
        # Get accelerometer data and normalize it
        accel = np.array([
            motion_data['ax'], motion_data['ay'], motion_data['az']
        ]) / self.sensitivity * GRAVITY_CONSTANT
        # Remove noise
        accel = np.where(np.abs(accel) < self.noise_threshold, 0, accel)

        # Calculate velocity change based on time
        current_time = time.time()
        dt = current_time - self.last_time
        self.last_time = current_time

        # Delta velocity and updating velocity
        delta_velocity = accel * dt
        difference = delta_velocity - self.velocity
        self.velocity += difference

        # Detect if the device is stationary, and apply decay factor if necessary
        i_vel = np.linalg.norm(
            accel) - GRAVITY_CONSTANT  # Instantaneous velocity
        if i_vel < self.stationary_reset_threshold:
            self.stationary_count += 1
            if self.stationary_count > STATIONARY_ITERATIONS_THRESHOLD:
                self.velocity *= self.decay_factor
        else:
            self.stationary_count = 0

        # Calculate speed in m/s and convert to km/h
        speed = max(0, np.linalg.norm(self.velocity) - 1)
        speed_kmph = speed * MS_TO_KMPH

        # Publish speed data to MQTT
        speed_data = {
            'speed_ms': round(speed, 2),
            'speed_kmph': round(speed_kmph, 2)
        }
        self.mqtt_client.publish(self.speed_topic,
                                 payload=json.dumps(speed_data))

    def detect_orientation(self, motion_data):
        """
        Detects device orientation (pitch, roll, and upside down) and publishes it.
        """
        # Get accelerometer data for orientation calculations
        accel_x, accel_y, accel_z = motion_data['ax'], motion_data[
            'ay'], motion_data['az']

        # Calculate pitch and roll using accelerometer data
        pitch = np.degrees(
            np.arctan2(-accel_x, np.sqrt(accel_y**2 + accel_z**2)))
        roll = np.degrees(np.arctan2(accel_y, accel_z))

        # Check if the device is upside down based on the z-axis acceleration
        is_upside_down = MAX_ORIENTATION_ANGLE if accel_z < UPSIDE_DOWN_THRESHOLD else 0

        # Prepare orientation data for publishing
        direction_data = {
            "forward": 0.0,
            "backward": 0.0,
            "left": 0.0,
            "right": 0.0,
            "upside_down": is_upside_down
        }

        # Update orientation based on pitch and roll values
        if not is_upside_down:
            if pitch > 1:
                direction_data["forward"] = float(
                    round(min(pitch, MAX_ORIENTATION_ANGLE), 2))
            elif pitch < -1:
                direction_data["backward"] = float(
                    round(min(abs(pitch), MAX_ORIENTATION_ANGLE), 2))

            if roll > 1:
                direction_data["right"] = float(
                    round(min(roll, MAX_ORIENTATION_ANGLE), 2))
            elif roll < -1:
                direction_data["left"] = float(
                    round(min(abs(roll), MAX_ORIENTATION_ANGLE), 2))

        # Publish orientation data to MQTT
        self.mqtt_client.publish(self.orientation_topic,
                                 payload=json.dumps(direction_data))

    def live_plot_directions(self):
        """
        Live plot for displaying direction intensities (forward, backward, left, right).
        """
        plt.ion()  # Enable interactive plotting
        fig, ax = plt.subplots()
        bars = ax.bar(["Forward", "Backward", "Left", "Right"], [0, 0, 0, 0],
                      color=["blue", "red", "green", "orange"])
        ax.set_ylim(0, 10)
        ax.set_ylabel("Intensity")
        ax.set_title("Direction Intensities")

        try:
            while True:
                data = self.sensor.read_motion_data()  # Read motion data
                gyro_data = {
                    "gx": data["gx"],
                    "gy": data["gy"],
                    "gz": data["gz"]
                }

                # Calculate direction intensities based on gyroscope data
                intensities = self.calculate_direction_intensities(gyro_data)

                # Update bar heights in the plot based on intensities
                for i, direction in enumerate(
                    ["forward", "backward", "left", "right"]):
                    bars[i].set_height(intensities[direction])

                plt.pause(0.1)  # Pause for a short interval to update the plot
        except KeyboardInterrupt:
            plt.ioff()
            plt.show()

    @staticmethod
    def calculate_direction_intensities(gyro_data):
        """
        Calculate intensity of motion in each direction based on gyroscope data.
        """
        gx, gy = gyro_data["gx"], gyro_data["gy"]

        # Calculate intensities for each direction (forward, backward, left, right)
        backward_intensity = max(0, gx) / NORMALIZATION_FACTOR
        forward_intensity = max(0, -gx) / NORMALIZATION_FACTOR
        left_intensity = max(0, gy) / NORMALIZATION_FACTOR
        right_intensity = max(0, -gy) / NORMALIZATION_FACTOR

        return {
            "forward": round(forward_intensity, 2),
            "backward": round(backward_intensity, 2),
            "left": round(left_intensity, 2),
            "right": round(right_intensity, 2),
        }


if __name__ == "__main__":
    # Create IMUSensorManager object and start reading motion data
    imu_manager = IMUSensorManager(DEFAULT_BMI160_ADDRESS, MQTT_BROKER_IP,
                                   MQTT_PORT)

    print("Starting IMU Sensor...")

    try:
        while True:
            imu_manager.read_and_publish()  # Read and publish motion data
            time.sleep(SLEEP_TIME)  # Wait for the next reading
    except KeyboardInterrupt:
        print("IMU Sensor stopped.")  # Stop on keyboard interrupt
