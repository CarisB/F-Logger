from config_data import *
import os
import re
from datetime import datetime


class HVLogger:
    logging: bool = False
    line: str = ""

    @staticmethod
    def add_data(data_points: list) -> str:
        """Parses HV logfile data and adds it to data_points. Returns a status message string."""

        if HVLogger.logging:
            if not HVLogger.line:
                return f"Couldn't read HV log file."

            # Get values from last line of HV log file
            hv_data = HVLogger.parse_hv_data(HVLogger.line)

            # Add data to data_points to be written
            data_points.append(
                {
                    "measurement": "hv",
                    "tags": {
                        "place": TAG_PLACE,
                        "module": TAG_MODULE,
                        "board": str(hv_data['board']),
                        "channel": str(hv_data['channel']),
                        "par": str(hv_data['parameter'])
                    },
                    "fields": {
                        "value": float(hv_data['value'])
                    }
                }
            )

            # Returns HV info
            return f"Current: {hv_data['value']} μA"

        else:
            return LOGGER_DISABLED_MSG

    @staticmethod
    def get_last_line(file_path: str) -> str | None:
        """Opens a file and returns the last line as a string."""

        try:
            with open(file_path, 'rb') as f:
                try:  # catch OSError in case of a one line file
                    f.seek(-2, os.SEEK_END)
                    while f.read(1) != b'\n':
                        f.seek(-2, os.SEEK_CUR)
                except OSError:
                    f.seek(0)

                return f.readline().decode()
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
