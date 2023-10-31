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
                # Reading the logfile, starting from the last line such that
                # the entire logfile doesn't have to be stored in memory
                try:  # catch OSError in case of a one line file
                    # Logfile format is:
                    '''
                    [2023-10-30T16:28:57]: [HV] bd [0] ch [0] par [IMonH] val [0.34]; 
                    
                    '''
                    # (Note the space after the line and the line-break)

                    f.seek(-2, os.SEEK_END)  # Move cursor to end of last line, before the ending space

                    while f.read(1) != b'\n':  # Move cursor forward one; if not line-break, keep going back
                        f.seek(-2, os.SEEK_CUR)

                    # Line-break was detected, so cursor is now at start of line we want to read

                except OSError:  # File is one line, so just place cursor at beginning
                    f.seek(0)

                result = f.readline().decode()  # Reads the line

                if cls.CURRENT_PARAMETER in result:  # If the line is a current (I) reading, store it
                    cls.last_current_line = result

                return result

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
