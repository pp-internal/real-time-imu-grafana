from flask import Flask
from flask_cors import CORS
import time
import os
import threading
import pandas as pd
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import WriteOptions

# Flask application setup
app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'secret!'

# CSV file paths
PPG_DATA_FILE = 'ppg_data.csv'
FILTERED_PPG_DATA_FILE = 'filtered_ppg_signal_with_timestamps.csv'

# Read CSV data into DataFrames
df = pd.read_csv(PPG_DATA_FILE, skiprows=14, engine='python', skipfooter=5)
df_filtered = pd.read_csv(FILTERED_PPG_DATA_FILE, engine='python')

# Global variables to track current index positions in DataFrames
current_index_influx = 0
current_index_influx_filtered = 0

# InfluxDB configuration
INFLUXDB_URL = os.getenv("INFLUXDB_URL", "http://localhost:8086")
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN", "TOKEN")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG", "ORG")
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET", "BUCKET")

# Create InfluxDB client
client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)

write_options = WriteOptions(batch_size=1000, flush_interval=10000)
write_api = client.write_api(write_options=write_options)

# Write precision in nanoseconds (for higher resolution timing)
WRITE_PRECISION = WritePrecision.NS

stop_flag = threading.Event()

def send_metrics_to_influxdb():
    """
    Sends sensor metrics from the 'ppg_data.csv' file to InfluxDB.
    This function loops through the CSV rows, creating points for each metric and sending them in batches.
    """
    global current_index_influx

    while not stop_flag.is_set():
        try:
            # Get the current row of data from the DataFrame
            row = df.iloc[current_index_influx]

            # Create data points for each metric and assign appropriate tags and fields
            points = [
                Point("device1").tag("sensor", "ledc1_pd1").field("value", row["LEDC1_PD1"]).time(int(time.time_ns()), WRITE_PRECISION),
                Point("device1").tag("sensor", "ledc1_pd2").field("value", row["LEDC1_PD2"]).time(int(time.time_ns()), WRITE_PRECISION),
                Point("device1").tag("sensor", "ledc2_pd1").field("value", row["LEDC2_PD1"]).time(int(time.time_ns()), WRITE_PRECISION),
                Point("device1").tag("sensor", "ledc2_pd2").field("value", row["LEDC2_PD2"]).time(int(time.time_ns()), WRITE_PRECISION),
                Point("device1").tag("sensor", "accx").field("value", row["ACCX"]).time(int(time.time_ns()), WRITE_PRECISION),
                Point("device1").tag("sensor", "accy").field("value", row["ACCY"]).time(int(time.time_ns()), WRITE_PRECISION),
                Point("device1").tag("sensor", "accz").field("value", row["ACCZ"]).time(int(time.time_ns()), WRITE_PRECISION)
            ]

            # Write data to InfluxDB
            write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=points)

            # Update the index to point to the next row
            current_index_influx += 1
            if current_index_influx >= len(df):
                current_index_influx = 0

            # Wait for 10ms before sending the next batch of data
            time.sleep(0.01)
        except Exception as e:
            print(f"Exception in send_metrics_to_influxdb: {e}")
            break

def send_metrics_filtered_to_influxdb():
    """
    Sends filtered PPG metrics from the 'filtered_ppg_signal_with_timestamps.csv' file to InfluxDB.
    This function loops through the CSV rows, creating points for the filtered metrics and sending them in batches.
    """
    global current_index_influx_filtered

    while not stop_flag.is_set():
        try:
            # Get the current row of data from the filtered DataFrame
            row = df_filtered.iloc[current_index_influx_filtered]

            # Create data point for the filtered PPG signal
            point = Point("device1").tag("sensor_filtered", "filtered_ppg").field("value", row["Filtered_PPG"]).time(int(time.time_ns()), WRITE_PRECISION)

            # Write data to InfluxDB
            write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=[point])

            # Update the index to point to the next row
            current_index_influx_filtered += 1
            if current_index_influx_filtered >= len(df_filtered):
                current_index_influx_filtered = 0

            # Wait for 10ms before sending the next data point
            time.sleep(0.01)
        except Exception as e:
            print(f"Exception in send_metrics_filtered_to_influxdb: {e}")
            break

# Main
if __name__ == '__main__':
    try:
        # Start separate threads for each function to send data concurrently
        thread1 = threading.Thread(target=send_metrics_to_influxdb)
        thread2 = threading.Thread(target=send_metrics_filtered_to_influxdb)
        
        thread1.start()
        thread2.start()

        # Keep the main thread alive to capture keyboard interrupt
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting")
        stop_flag.set()
        thread1.join()
        thread2.join()
    finally:
        # Ensure the client is properly closed
        write_api.__del__()
        client.close()
        print("Closed InfluxDB client")
