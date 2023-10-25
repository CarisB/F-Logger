from config_db import *
from config_data import *
from config_gui import *

from influxdb import InfluxDBClient
from yoctopuce.yocto_genericsensor import *
from yoctopuce.yocto_humidity import *
from yoctopuce.yocto_pressure import *
from yoctopuce.yocto_temperature import *

import os
import re
from datetime import datetime
import webbrowser

import tkinter as tk
from tkinter import ttk
from tkinter import PhotoImage

import warnings
from urllib3.exceptions import InsecureRequestWarning
warnings.filterwarnings("ignore", category=InsecureRequestWarning)

# Logger toggles
logging_ise = True
logging_meteo = True
logging_hv = True

# Setup USB interface
errmsg = YRefParam()
if YAPI.RegisterHub("usb", errmsg) != YAPI.SUCCESS:
    sys.exit("Init Error: " + errmsg.value)

# Open connection with database
client = InfluxDBClient(host=DB_HOST, port=DB_PORT, username=DB_USERNAME, password=DB_PASSWORD,
                        database=DB_DATABASE, ssl=True, verify_ssl=False)

# Find sensors
mv_sensor = YGenericSensor.FindGenericSensor(VOLTAGE_SENSOR_ID)
humidity_sensor = YHumidity.FirstHumidity()
temperature_sensor = YTemperature.FirstTemperature()
pressure_sensor = YPressure.FirstPressure()


def main():
    data_points = []
    last_line = get_last_line(HV_LOG_FILE)

    add_ise_data(data_points)
    add_meteo_data(data_points)
    add_hv_data(data_points, last_line)

    if data_points and client.write_points(data_points):  # Successful write
        db_write_status_text.set(WRITE_SUCCESS_TEXT)
        db_write_status_label['fg'] = WRITE_SUCCESS_COLOR
    else:  # Couldn't write to database
        db_write_status_text.set(WRITE_FAIL_TEXT)
        db_write_status_label['fg'] = WRITE_FAIL_COLOR

    # Waits for POLLING_MS milliseconds, then callback to repeat loop
    root.after(POLLING_MS, main)


def add_ise_data(data_points: list):
    if not mv_sensor.isOnline():
        ise_toggle_label['fg'] = SENSOR_OFFLINE_COLOR
        ise_status_text.set("Sensor is offline.")
        return

    if logging_ise:
        mv_value = mv_sensor.get_currentRawValue()

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

        # Display ISE info
        ise_status_text.set(f"Voltage: {mv_value} mV")


def add_meteo_data(data_points: list):
    if (humidity_sensor is None
            or temperature_sensor is None
            or pressure_sensor is None):
        meteo_toggle_label['fg'] = SENSOR_OFFLINE_COLOR
        meteo_status_text.set("Sensor is offline.")
        return

    if logging_meteo:
        humidity_value = humidity_sensor.get_currentRawValue()
        temperature_value = temperature_sensor.get_currentRawValue()
        pressure_value = pressure_sensor.get_currentRawValue()

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
                    "humidity": humidity_value,
                    "temperature": temperature_value,
                    "pressure": pressure_value
                }
            })

        # Display METEO info
        meteo_status_text.set(
            f"Temperature: {temperature_value} / Humidity: {humidity_value} / Pressure: {pressure_value}")


def add_hv_data(data_points: list, last_line: str):
    if not last_line:
        hv_toggle_label['fg'] = SENSOR_OFFLINE_COLOR
        hv_status_text.set(f"Couldn't read {HV_LOG_FILE}.")
        return

    if logging_hv:
        # Get values from last line of HV log file
        hv_data = parse_hv_data(last_line)

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

        # Display HV info
        hv_status_text.set(f"Current: {hv_data['value']} μA")


def get_last_line(file):
    try:
        with open(file, 'rb') as f:
            try:  # catch OSError in case of a one line file
                f.seek(-2, os.SEEK_END)
                while f.read(1) != b'\n':
                    f.seek(-2, os.SEEK_CUR)
            except OSError:
                f.seek(0)

            return f.readline().decode()
    except FileNotFoundError:
        return None


def parse_hv_data(line: str):
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

    # No regex match was found
    return None


def toggle_ise():
    global logging_ise

    if logging_ise:
        ise_toggle_button['image'] = off_img
        logging_ise = False
    else:
        ise_toggle_button['image'] = on_img
        logging_ise = True


def toggle_meteo():
    global logging_meteo

    if logging_meteo:
        meteo_toggle_button['image'] = off_img
        logging_meteo = False
    else:
        meteo_toggle_button['image'] = on_img
        logging_meteo = True


def toggle_hv():
    global logging_hv

    if logging_hv:
        hv_toggle_button['image'] = off_img
        logging_hv = False
    else:
        hv_toggle_button['image'] = on_img
        logging_hv = True


def open_grafana():
    webbrowser.open_new(GRAFANA_URL)


# Main window
root = tk.Tk()
root.title(WINDOW_TITLE)
root.geometry(f'{WINDOW_WIDTH}x{WINDOW_HEIGHT}')

# Resources
current_path = os.path.dirname(os.path.abspath(__file__))
on_img = PhotoImage(file=current_path + '/resources/on.png')
off_img = PhotoImage(file=current_path + '/resources/off.png')

# Title
title_label = ttk.Label(
    master=root, text=TITLE_LABEL, font=TITLE_FONT)
title_label.pack(pady=20)

# Main Toggle Frame
toggle_frame = ttk.Frame(master=root)
toggle_frame.pack(anchor='w', padx=30)
toggle_frame.columnconfigure(index=0, weight=1)
toggle_frame.columnconfigure(index=1, weight=1)
toggle_frame.columnconfigure(index=2, weight=10)
toggle_frame.rowconfigure(index=0, weight=1)
toggle_frame.rowconfigure(index=1, weight=1)
toggle_frame.rowconfigure(index=2, weight=1)

# ISE Toggle Frame
ise_toggle_label = tk.Label(master=toggle_frame, text='ISE Logger',
                            anchor='w', font=TOGGLE_LABEL_FONT)
ise_toggle_label.grid(column=0, row=0,
                      sticky=tk.W, padx=5, pady=5)

ise_toggle_button = ttk.Button(master=toggle_frame, image=on_img, command=toggle_ise)
ise_toggle_button.grid(column=1, row=0,
                       sticky=tk.W, padx=5, pady=5)

ise_status_text = tk.StringVar()
ise_status_label = ttk.Label(master=toggle_frame, textvariable=ise_status_text)
ise_status_label.grid(column=2, row=0,
                      sticky=tk.W, padx=50, pady=5)

# METEO Toggle Frame
meteo_toggle_label = tk.Label(master=toggle_frame, text='METEO Logger',
                              anchor='w', font=TOGGLE_LABEL_FONT)
meteo_toggle_label.grid(column=0, row=1,
                        sticky=tk.W, padx=5, pady=5)

meteo_toggle_button = ttk.Button(master=toggle_frame, image=on_img, command=toggle_meteo)
meteo_toggle_button.grid(column=1, row=1,
                         sticky=tk.W, padx=5, pady=5)

meteo_status_text = tk.StringVar()
meteo_status_label = ttk.Label(master=toggle_frame, textvariable=meteo_status_text)
meteo_status_label.grid(column=2, row=1,
                        sticky=tk.W, padx=50, pady=5)

# HV Toggle Frame
hv_toggle_label = tk.Label(master=toggle_frame, text='HV Logger',
                           anchor='w', font=TOGGLE_LABEL_FONT)
hv_toggle_label.grid(column=0, row=2,
                     sticky=tk.W, padx=5, pady=5)

hv_toggle_button = ttk.Button(master=toggle_frame, image=on_img, command=toggle_hv)
hv_toggle_button.grid(column=1, row=2,
                      sticky=tk.W, padx=5, pady=5)

hv_status_text = tk.StringVar()
hv_status_label = ttk.Label(master=toggle_frame, textvariable=hv_status_text)
hv_status_label.grid(column=2, row=2,
                     sticky=tk.W, padx=50, pady=5)

db_write_status_text = tk.StringVar()
db_write_status_label = tk.Label(master=root, textvariable=db_write_status_text,
                                 padx=50, pady=50)
db_write_status_label.pack(anchor='e')

# Link to Grafana
grafana_button = ttk.Button(master=root, text='Open Link to Grafana', command=open_grafana)
grafana_button.pack(pady=30)

# Run
root.after(0, main)
root.mainloop()
