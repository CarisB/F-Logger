from config_data import *
from Sensors import Sensors

import math


class ISELogger:
    logging: bool = False

    @staticmethod
    def add_data(data_points: list) -> str:
        """Creates and adds sensor data to data_points. Returns a status message string."""

        if ISELogger.logging:
            if not Sensors.mv.isOnline():
                return SENSOR_OFFLINE_MSG

            mv_value = Sensors.mv.get_currentRawValue()
            ppm = math.exp((mv_value - ISE_CALIBRATION_B) / -ISE_CALIBRATION_A)

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
                        "voltage": mv_value,
                        "ppm": ppm,
                        "calibration_a": ISE_CALIBRATION_A,
                        "calibration_b": ISE_CALIBRATION_B
                    }
                })

            # Return ISE info
            return f"Voltage: {mv_value} mV, PPM: {ppm} ppm"

        else:  # ISELogger.logging = False
            return LOGGER_DISABLED_MSG
