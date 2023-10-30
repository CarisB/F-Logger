from config_data import *
from Sensors import Sensors

from scipy.interpolate import interp1d


class FMLogger:
    logging: bool = False

    @staticmethod
    def add_data(data_points: list) -> str:
        """Creates and adds sensor data to data_points. Returns a status message string."""

        if FMLogger.logging:
            if not Sensors.fm.isOnline():
                return SENSOR_OFFLINE_MSG

            fm_value = Sensors.fm.get_currentValue()

            # Correcting the data reading
            calibration_curve = interp1d([0.5, 0.90, 1.30, 1.70, 2.10, 2.50],
                                         [0, 0.02 * 60, 0.04 * 60, 0.06 * 60, 0.08 * 60, 0.10 * 60], kind="cubic")

            adjusted_flow = 0

            try:
                adjusted_flow = calibration_curve(fm_value)
            except:
                if fm_value < 0.5:
                    adjusted_flow = 0
                elif fm_value > 2.5:
                    adjusted_flow = 0.10 * 60

            values = {
                'flowvolts': fm_value,
                'flow': float(adjusted_flow)
            }

            # Add data to data_points to be written
            data_points.append(
                {
                    "measurement": MEASUREMENT_LABEL,
                    "tags": {
                        "hostname": TAG_HOSTNAME,
                        "device": DEVICE_ID,
                        "place": TAG_PLACE,
                        "setup": TAG_SETUP
                    },
                    "fields": values
                })

            # Return FM info
            return f"Voltage: {fm_value} mV, Flow: {adjusted_flow} L/min"

        else:  # FMLogger.logging = False
            return LOGGER_DISABLED_MSG
