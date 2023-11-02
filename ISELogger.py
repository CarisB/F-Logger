from config_data import *
from Sensors import Sensors

import math


class ISELogger:
    TABLE_NAME = "yoctopuce"
    DEVICE_ID = "Yocto-milliVolt-Rx-BNC"
    TAG_PLACE = "904"
    TAG_SETUP = "ise"
    ISE_CALIBRATION_A = 24.71
    ISE_CALIBRATION_B = 98.96

    logging: bool = False

    @classmethod
    def add_data(cls, data_points: list) -> str:
        """Creates and adds sensor data to data_points. Returns a status message string."""

        if cls.logging:
            if not Sensors.mv.isOnline():
                return SENSOR_OFFLINE_MSG

            mv_value = Sensors.mv.get_currentRawValue()
            ppm = math.exp((mv_value - cls.ISE_CALIBRATION_B) / -cls.ISE_CALIBRATION_A)

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
                        "voltage": mv_value,
                        "ppm": ppm,
                        "calibration_a": cls.ISE_CALIBRATION_A,
                        "calibration_b": cls.ISE_CALIBRATION_B
                    }
                })

            # Return ISE info
            return f"Voltage: {mv_value} mV, PPM: {round(ppm, 2)} ppm"

        else:  # ISELogger.logging = False
            return LOGGER_DISABLED_MSG
