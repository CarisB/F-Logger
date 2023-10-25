from config_data import *
from yoctopuce.yocto_humidity import *
from yoctopuce.yocto_temperature import *
from yoctopuce.yocto_pressure import *


class METEOLogger:
    def __init__(self,
                 humidity_sensor: YHumidity,
                 temperature_sensor: YTemperature,
                 pressure_sensor: YPressure):
        self.logging = False
        self.humidity_sensor = humidity_sensor
        self.temperature_sensor = temperature_sensor
        self.pressure_sensor = pressure_sensor

    def add_meteo_data(self, data_points: list) -> str:
        """Creates and adds sensor data to data_points. Returns a status message string."""

        if (self.humidity_sensor is None
                or self.temperature_sensor is None
                or self.pressure_sensor is None):
            return SENSOR_OFFLINE_MSG

        if self.logging:
            humidity_value = self.humidity_sensor.get_currentRawValue()
            temperature_value = self.temperature_sensor.get_currentRawValue()
            pressure_value = self.pressure_sensor.get_currentRawValue()

            # Add data to data_points to be written
            data_points.append(
                {
                    "measurement": MEASUREMENT_LABEL,
                    "tags": {
                        "device": DEVICE_ID,
                        "place": TAG_PLACE,
                        "setup": TAG_SETUP
                    },
                    "fields": {
                        "humidity": humidity_value,
                        "temperature": temperature_value,
                        "pressure": pressure_value
                    }
                })

            # Return METEO info
            return f"Temperature: {temperature_value} / Humidity: {humidity_value} / Pressure: {pressure_value}"

        else:  # self.logging = False
            return LOGGER_DISABLED_MSG
