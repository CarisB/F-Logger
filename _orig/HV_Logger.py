from influxdb import InfluxDBClient
import time
import re
from datetime import datetime
import os

import warnings
from urllib3.exceptions import InsecureRequestWarning

warnings.filterwarnings("ignore", category=InsecureRequestWarning)

# Configurazione del client InfluxDB

client = InfluxDBClient(host='dbod-epdtmon.cern.ch', port=8081, username='rpcgif', password='RPCgas2021',
                        database='data', ssl=True, verify_ssl=False)

# Nome del file di dati
DATA_FILE = "C:\\Users\\rpcgif\\cernbox\\Documents\\CAENGECO2020.log"


def parse_data_line(line):
    match = re.match(r'\[(.*?)\]: \[HV\] bd \[(\d+)\] ch \[(\d+)\] par \[(.*?)\] val \[(.*?)\];', line)
    if match:
        timestamp_str, board, channel, parameter, value = match.groups()
        timestamp = datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%S")
        return {
            "measurement": "hv",
            "tags": {
                "place": "904",
                "module": "V1741A",
                "board": str(board),
                "channel": str(channel),
                "par": str(parameter)
            },
            "fields": {
                "value": float(value)
            }
        }
    return None


def main():
    while True:
        last_line = ""

        # Open log and seek only the last line (more performant than reading the whole file)
        with open(DATA_FILE, 'rb') as f:
            try:  # catch OSError in case of a one line file
                f.seek(-2, os.SEEK_END)
                while f.read(1) != b'\n':
                    f.seek(-2, os.SEEK_CUR)
            except OSError:
                f.seek(0)

            last_line = f.readline().decode()

        data_points = []
        data_point = parse_data_line(last_line)

        if data_point:
            data_points.append(data_point)

            res = client.write_points(data_points)

            print(res)
            print(data_points)

            # with open(DATA_FILE, "w") as f:
            # pass

        time.sleep(2)


if __name__ == "__main__":
    main()
