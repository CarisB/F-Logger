"""
- GUI Logging tool built for the F- Detector experiment in Building 904 @ CERN
- Developer: Christopher Baek
- Required modules: Pydantic-Settings, InfluxDB, Yoctopuce, SciPy

Sensors are stored as static variables in the Sensors class.
Each logger has its own static class that stores its respective logging state (HVLogger also has HVLogger.line).
The logger's add_data function adds the log data to data_points[] and returns a status string.
main() is first run by root.after(0, main), and then run recursively by itself with root.after(POLLING_MS, main)
"""

from config_data import *
from config_gui import *
from Sensors import Sensors
from ISELogger import ISELogger
from METEOLogger import METEOLogger
from FMLogger import FMLogger
from HVLogger import HVLogger
from GUI import GUI

from pydantic_settings import BaseSettings
from influxdb import InfluxDBClient

from datetime import datetime
import warnings
from urllib3.exceptions import InsecureRequestWarning
warnings.filterwarnings("ignore", category=InsecureRequestWarning)


class Settings(BaseSettings):  # Database settings (stored in local .env file)
    DB_HOST: str
    DB_PORT: int
    DB_USERNAME: str
    DB_PASSWORD: str
    DB_DATABASE: str
    DB_SSL: bool
    DB_VERIFYSSL: bool

    class Config:
        env_file = '.env'


# Open connection with database
config = Settings()
client = InfluxDBClient(host=config.DB_HOST,
                        port=config.DB_PORT,
                        username=config.DB_USERNAME,
                        password=config.DB_PASSWORD,
                        database=config.DB_DATABASE,
                        ssl=config.DB_SSL,
                        verify_ssl=config.DB_VERIFYSSL)
Sensors.init()  # Find and initialize sensors
GUI.init()  # Initialize GUI


# Main loop (called back by tkinter.after() after POLLING_MS, set in the config_data module)
def main():
    data_points = []  # Resets data collection to write to database
    Sensors.check_sensors()  # Check the connection status of sensors, try to set if missing

    # Gets the last line of the selected HV logfile
    if HVLogger.logging:
        HVLogger.line = HVLogger.get_last_line(GUI.hv_log_path)

    # Add data points and set status text accordingly
    GUI.ise_status_text.set(
        ISELogger.add_data(data_points))
    GUI.meteo_status_text.set(
        METEOLogger.add_data(data_points))
    GUI.fm_status_text.set(
        FMLogger.add_data(data_points))
    GUI.hv_status_text.set(
        HVLogger.add_data(data_points))

    # Timestamp
    current_time = datetime.now()
    timestamp = datetime.fromtimestamp(current_time.timestamp())
    timestamp_str = timestamp.strftime("[%H:%M:%S]: ")

    if data_points and client.write_points(data_points):  # Successful write
        GUI.db_write_status_text.set(timestamp_str + WRITE_SUCCESS_TEXT)
        GUI.db_write_status_label['fg'] = WRITE_SUCCESS_COLOR
    else:  # Couldn't write to database
        GUI.db_write_status_text.set(timestamp_str + WRITE_FAIL_TEXT)
        GUI.db_write_status_label['fg'] = WRITE_FAIL_COLOR

    # Waits for POLLING_MS milliseconds, then callback to repeat loop
    GUI.root.after(POLLING_MS, main)


# Run
GUI.root.after(0, main)
GUI.root.mainloop()
