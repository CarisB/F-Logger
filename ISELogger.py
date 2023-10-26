from config_data import *
from yoctopuce.yocto_genericsensor import YGenericSensor


class ISELogger:
    def __init__(self, mv_sensor: YGenericSensor):
        self.logging = False
        self.mv_sensor = mv_sensor

    def add_ise_data(self, data_points: list) -> str:
        """Creates and adds sensor data to data_points. Returns a status message string."""

        if self.logging:
            if not self.mv_sensor.isOnline():
                return SENSOR_OFFLINE_MSG

            mv_value = self.mv_sensor.get_currentRawValue()

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

        else:  # self.logging = False
            return LOGGER_DISABLED_MSG
