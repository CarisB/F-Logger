from config_data import *
from Sensors import Sensors


class ISELogger:
    logging: bool = False

    @staticmethod
    def add_ise_data(data_points: list) -> str:
        """Creates and adds sensor data to data_points. Returns a status message string."""

        if ISELogger.logging:
            if not Sensors.mv.isOnline():
                return SENSOR_OFFLINE_MSG

            mv_value = Sensors.mv.get_currentRawValue()

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
                        "voltage": mv_value
                    }
                })

            # Return ISE info
            return f"Voltage: {mv_value} mV"

        else:  # ISELogger.logging = False
            return LOGGER_DISABLED_MSG
