from config_data import *
import os
import re
from datetime import datetime


class HVLogger:
    CURRENT_PARAMETER = "IMonH"
    VOLTAGE_PARAMETER = "VMonH"

    logging: bool = False
    line: str = ""  # The logfile line being processed
    last_current_line: str = ""  # The last known current (I) reading from the log

    @classmethod
    def add_data(cls, data_points: list) -> str:
        """Parses HV logfile data and adds it to data_points. Returns a status message string."""

        if cls.logging:
            if not cls.line:
                return f"Couldn't read HV log file."

            # Get values from last line of HV log file
            data = cls.parse_hv_data(cls.line)

            # Add data to data_points to be written
            cls.append_data(data_points, data)

            # We want to log the current (I) reading every cycle,
            # but we don't need the voltage reading all the time
            # If the line is a voltage reading, log the last known current again
            if cls.line is not cls.last_current_line:
                data = cls.parse_hv_data(cls.last_current_line)
                cls.append_data(data_points, data)

            # Returns HV info
            return f"Current: {data['value']} μA"

        else:
            return LOGGER_DISABLED_MSG

    @staticmethod
    def append_data(data_points: list, data: dict):
        if not data_points or not data:
            return

        data_points.append(
            {
                "measurement": "hv",
                "tags": {
                    "place": TAG_PLACE,
                    "module": TAG_MODULE,
                    "board": str(data['board']),
                    "channel": str(data['channel']),
                    "par": str(data['parameter'])
                },
                "fields": {
                    "value": float(data['value'])
                }
            }
        )

    @classmethod
    def get_last_line(cls, file_path: str) -> str | None:
        """Opens a file and returns the last line as a string."""

        try:
            with open(file_path, 'rb') as f:
                res = ""
                try:  # catch OSError in case of a one line file
                    f.seek(-2, os.SEEK_END)
                    while f.read(1) != b'\n':
                        f.seek(-2, os.SEEK_CUR)
                    res = f.readline().decode()
                    if cls.CURRENT_PARAMETER in res:
                        cls.last_current_line = res
                except OSError:
                    f.seek(0)

                return res
        except FileNotFoundError:  # Couldn't find log
            return None

    @staticmethod
    def parse_hv_data(line: str) -> dict | None:
        """Parses a string using RegEx and returns a Dictionary with the fields."""

        match = re.match(r'\[(.*?)\]: \[HV\] bd \[(\d+)\] ch \[(\d+)\] par \[(.*?)\] val \[(.*?)\];', line)

        if match:
            timestamp_str, board, channel, parameter, value = match.groups()
            timestamp = datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%S")

            return {
                'timestamp': timestamp,
                'board': board,
                'channel': channel,
                'parameter': parameter,
                'value': value
            }

        # No RegEx match was found
        return None
