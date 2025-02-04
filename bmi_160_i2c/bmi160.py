from BMI160_i2c import Driver

DEFAULT_I2C_BUS_ID = 1  # Default I2C bus
DEFAULT_BMI160_ADDRESS = 0x69  # Default I2C address


class BMI160:
    """
    A wrapper class for interfacing with the BMI160 sensor over I2C.

    Parameters:
    i2c_address (int): The I2C address of the sensor. Defaults to 0x69.
    bus_id (int): The I2C bus ID. Defaults to 1.

    Raises:
    IOError: If the sensor connection fails due to I2C communication issues.
    FileNotFoundError: If the specified I2C bus ID is invalid or not available.
    """

    def __init__(self,
                 i2c_address: int = DEFAULT_BMI160_ADDRESS,
                 bus_id: int = DEFAULT_I2C_BUS_ID):
        self.i2c_address = i2c_address
        self.bus_id = bus_id
        self.sensor = None

        try:
            # Try to initialize the sensor with the given address and bus
            self.sensor = Driver(self.i2c_address, bus=self.bus_id)
            print(
                f"BMI160 sensor initialized successfully at address {hex(self.i2c_address)} on bus {self.bus_id}."
            )
        except FileNotFoundError as e:
            # Handle invalid bus ID error
            print(f"Invalid I2C bus {self.bus_id}. Check if the bus exists.")
            raise FileNotFoundError(f"I2C bus error: {e}")
        except OSError as e:
            # Handle general I2C communication error
            print(
                f"Failed to initialize the BMI160 sensor at address {hex(self.i2c_address)} on bus {self.bus_id}."
            )
            raise IOError(f"I2C communication error: {e}")

    def read_motion_data(self):
        """
        Reads motion data from the BMI160 sensor, including gyroscope and accelerometer values.
        
        Returns:
        dict: A dictionary containing gyroscope and accelerometer data with
              keys 'gx', 'gy', 'gz', 'ax', 'ay', and 'az'.
        If an error occurs, returns None.
        
        Raises:
        IOError: If there is an issue reading data from the sensor.
        """
        try:
            # Fetch motion data (gyroscope and accelerometer)
            data = self.sensor.getMotion6()

            # Return the data in a structured way
            motion_data = {
                'gx': data[0],  # Gyroscope X
                'gy': data[1],  # Gyroscope Y
                'gz': data[2],  # Gyroscope Z
                'ax': data[3],  # Accelerometer X
                'ay': data[4],  # Accelerometer Y
                'az': data[5]  # Accelerometer Z
            }
            return motion_data
        except Exception as e:
            # Handle any exceptions during reading
            print(f"Error reading motion data: {e}")
            return None
