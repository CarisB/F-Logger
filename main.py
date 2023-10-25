"""
- GUI Logging tool built for the F- Detector experiment in Building 904 @ CERN
- Developer: Christopher Baek
- Required modules: InfluxDB, Yoctopuce
"""

from config_db import *
from config_data import *
from config_gui import *

from ISELogger import ISELogger
from METEOLogger import METEOLogger
from HVLogger import HVLogger

from influxdb import InfluxDBClient
from yoctopuce.yocto_genericsensor import *
from yoctopuce.yocto_humidity import YHumidity
from yoctopuce.yocto_temperature import YTemperature
from yoctopuce.yocto_pressure import YPressure

from pathlib import Path
import webbrowser

import tkinter as tk
from tkinter import ttk
from tkinter import PhotoImage

import warnings
from urllib3.exceptions import InsecureRequestWarning
warnings.filterwarnings("ignore", category=InsecureRequestWarning)

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

# Instantiate Logger objects
ise_logger = ISELogger(mv_sensor)
meteo_logger = METEOLogger(humidity_sensor, temperature_sensor, pressure_sensor)
hv_logger = HVLogger()


def main():
    data_points = []
    hv_logger.line = HVLogger.get_last_line(HV_LOG_FILE)

    # Add data points and set status text accordingly
    ise_status_text.set(
        ise_logger.add_ise_data(data_points))
    meteo_status_text.set(
        meteo_logger.add_meteo_data(data_points))
    hv_status_text.set(
        hv_logger.add_hv_data(data_points))

    if data_points and client.write_points(data_points):  # Successful write
        db_write_status_text.set(WRITE_SUCCESS_TEXT)
        db_write_status_label['fg'] = WRITE_SUCCESS_COLOR
    else:  # Couldn't write to database
        db_write_status_text.set(WRITE_FAIL_TEXT)
        db_write_status_label['fg'] = WRITE_FAIL_COLOR

    # Waits for POLLING_MS milliseconds, then callback to repeat loop
    root.after(POLLING_MS, main)


def toggle_ise_logger():
    if ise_logger.logging:
        ise_toggle_button['image'] = off_img
        ise_logger.logging = False
    else:
        ise_toggle_button['image'] = on_img
        ise_logger.logging = True


def toggle_meteo_logger():
    if meteo_logger.logging:
        meteo_toggle_button['image'] = off_img
        meteo_logger.logging = False
    else:
        meteo_toggle_button['image'] = on_img
        meteo_logger.logging = True


def toggle_hv_logger():
    if hv_logger.logging:
        hv_toggle_button['image'] = off_img
        hv_logger.logging = False
    else:
        hv_toggle_button['image'] = on_img
        hv_logger.logging = True


def open_grafana():
    webbrowser.open_new(GRAFANA_URL)


# Main window
root = tk.Tk()
root.title(WINDOW_TITLE)
root.geometry(f'{WINDOW_WIDTH}x{WINDOW_HEIGHT}')

# Resources
current_path = Path().absolute().__str__()
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

ise_toggle_button = ttk.Button(master=toggle_frame, image=off_img, command=toggle_ise_logger)
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

meteo_toggle_button = ttk.Button(master=toggle_frame, image=off_img, command=toggle_meteo_logger)
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

hv_toggle_button = ttk.Button(master=toggle_frame, image=off_img, command=toggle_hv_logger)
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
