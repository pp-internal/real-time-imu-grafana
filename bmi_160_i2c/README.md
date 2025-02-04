## BMI160

This folder contains the code to interface the BMI160 with Raspberry Pi

### Dependencies

Install the `BMI160-i2c` package using below command
`python3 -m pip install BMI160-i2c`

### Connecting the BMI160 to Raspberry Pi

Make the connection as follows

| BMI160 Pins | Raspberry Pi Pins |
|-------------|-------------------|
| VIN         | 3.3V (Pin 1)      |
| GND         | GND (Pin 6)       |
| SDA         | I2C SDA (Pin 3)   |
| SCL         | I2C SCL (Pin 5)   |


### Enabling I2C on Raspberry Pi

1. **Open Raspberry Pi Configuration Tool:**
   - Run the following command in the terminal to open the Raspberry Pi configuration tool:
     ```bash
     sudo raspi-config
     ```

2. **Navigate to `Interface` Options:**
   - In the configuration menu, use the arrow keys to select `Interfaces` tab .

3. **Enable I2C:**
   - Select `I2C`, and click `OK` to enable I2C. Confirm with `Yes` if prompted.

4. **Reboot the Raspberry Pi:**
   - After enabling I2C, reboot the Raspberry Pi to apply the changes:
     ```bash
     sudo reboot
     ```

5. **Install I2C Tools (Optional, for testing):**
   - You can install `i2c-tools` to check if the I2C devices are connected properly:
     ```bash
     sudo apt-get install i2c-tools
     ```
   - After installation, run the following command to check connected I2C devices:
     ```bash
     sudo i2cdetect -y 1
     ```
     
### Address of BMI160
- Address of BMI160 can be either `0x68` or `0x69`
- We're using the `0x69` for our sensor
- If the I2C address of the BMI160 is not known we can find it using `i2cdetect` command
```
$ i2cdetect -y 1
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00:                         -- -- -- -- -- -- -- -- 
10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
40: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
60: -- -- -- -- -- -- -- -- -- 69 -- -- -- -- -- -- 
70: -- -- -- -- -- -- -- --                         
```
- In our case address is 0x69

### Run the `IMUProcessor.py`
- `IMUProcessor.py` This script interfaces with the BMI160 sensor to capture accelerometer and gyroscope data,
   processes motion information (speed, orientation), and publishes it via MQTT.


```
$ cd bmi_160_i2c
$ python IMUProcessor.py
BMI160 sensor initialized successfully at address 0x69 on bus 1.
Starting IMU Sensor...
```