from config_data import *
from Sensors import Sensors


class METEOLogger:
    TABLE_NAME = "yoctopuce"
    DEVICE_ID = "Yocto-Meteo-V2"
    TAG_PLACE = "904"
    TAG_SETUP = "ise"
    EXCEPTION_MSG = "Meteo Exception: could not return Meteo raw value."

    logging: bool = False

    @classmethod
    def add_data(cls, data_points: list) -> str:
        """Creates and adds sensor data to data_points. Returns a status message string."""

        if cls.logging:
            if Sensors.humidity is None or Sensors.temperature is None or Sensors.pressure is None:
                return SENSOR_OFFLINE_MSG

            try:
                humidity_value = Sensors.humidity.get_currentRawValue()
                temperature_value = Sensors.temperature.get_currentRawValue()
                pressure_value = Sensors.pressure.get_currentRawValue()

                if (
                        humidity_value == Sensors.humidity.CURRENTRAWVALUE_INVALID or
                        temperature_value == Sensors.temperature.CURRENTRAWVALUE_INVALID or
                        pressure_value == Sensors.pressure.CURRENTRAWVALUE_INVALID
                ):
                    return cls.EXCEPTION_MSG
            except:
                return cls.EXCEPTION_MSG

            # Add data to data_points to be written
            data_points.append(
                {
                    "measurement": cls.TABLE_NAME,
                    "tags": {
                        "device": cls.DEVICE_ID,
                        "place": cls.TAG_PLACE,
                        "setup": cls.TAG_SETUP
                    },
                    "fields": {
                        "humidity": humidity_value,
                        "temperature": temperature_value,
                        "pressure": pressure_value
                    }
                })

            # Return METEO info
            return f"Temperature: {temperature_value} / Humidity: {humidity_value} / Pressure: {pressure_value}"

        else:  # METEOLogger.logging = False
            return LOGGER_DISABLED_MSG
