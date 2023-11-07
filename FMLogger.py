from config_data import *
from Sensors import Sensors

from scipy.interpolate import interp1d


class FMLogger:
    TABLE_NAME = "yoctopuce"
    DEVICE_ID = "Yocto-0-10V-Rx"
    TAG_HOSTNAME = "pcgasteam01"
    TAG_PLACE = "904"
    TAG_SETUP = "ise"
    EXCEPTION_MSG = "FM Exception: could not return current value."

    logging: bool = False

    @classmethod
    def add_data(cls, data_points: list) -> str:
        """Creates and adds sensor data to data_points. Returns a status message string."""

        if cls.logging:
            if not Sensors.fm.isOnline():
                return SENSOR_OFFLINE_MSG

            try:
                fm_value = Sensors.fm.get_currentValue()

                if fm_value == Sensors.fm.CURRENTRAWVALUE_INVALID:
                    return cls.EXCEPTION_MSG
            except:
                return cls.EXCEPTION_MSG

            # Correcting the data reading
            calibration_curve = interp1d([0.5, 0.90, 1.30, 1.70, 2.10, 2.50],
                                         [0, 0.02 * 60, 0.04 * 60, 0.06 * 60, 0.08 * 60, 0.10 * 60], kind="cubic")

            adjusted_flow = 0.0

            try:
                adjusted_flow = float(calibration_curve(fm_value))
            except:
                if fm_value < 0.5:
                    adjusted_flow = 0.0
                elif fm_value > 2.5:
                    adjusted_flow = 0.10 * 60

            values = {
                'flowvolts': fm_value,
                'flow': adjusted_flow
            }

            # Add data to data_points to be written
            data_points.append(
                {
                    "measurement": cls.TABLE_NAME,
                    "tags": {
                        "hostname": cls.TAG_HOSTNAME,
                        "device": cls.DEVICE_ID,
                        "place": cls.TAG_PLACE,
                        "setup": cls.TAG_SETUP
                    },
                    "fields": values
                })

            # Return FM info
            return f"Voltage: {fm_value} mV, Flow: {round(adjusted_flow, 3)} L/min"

        else:  # FMLogger.logging = False
            return LOGGER_DISABLED_MSG
