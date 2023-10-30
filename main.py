"""
- GUI Logging tool built for the F- Detector experiment in Building 904 @ CERN
- Developer: Christopher Baek
- Required modules: InfluxDB, Yoctopuce, SciPy

Sensors are stored as static variables in the Sensors class.
Each logger has its own static class that stores its respective logging state (HVLogger also has HVLogger.line).
The logger's add_data function adds the log data to data_points[] and returns a status string.
main() is run initially by tkinter.after(0, main), and then run recursively by itself with tkinter.after(POLLING_MS, main)
"""

# region Imports
from config_db import *
from config_data import *
from config_gui import *
from Sensors import Sensors
from ISELogger import ISELogger
from METEOLogger import METEOLogger
from FMLogger import FMLogger
from HVLogger import HVLogger

from influxdb import InfluxDBClient
import os
import webbrowser

import tkinter as tk
from tkinter import ttk
from tkinter import PhotoImage
from tkinter import filedialog
from tkinter import messagebox

import warnings
from urllib3.exceptions import InsecureRequestWarning
warnings.filterwarnings("ignore", category=InsecureRequestWarning)
# endregion


# region Init
# Open connection with database
client = InfluxDBClient(host=DB_HOST, port=DB_PORT, username=DB_USERNAME, password=DB_PASSWORD,
                        database=DB_DATABASE, ssl=True, verify_ssl=False)

hv_log_path = HV_LOG_DEFAULT_PATH  # Set the HV logfile path to the default

Sensors.init()  # Find and initialize sensors
# endregion


# region UI Functions
def toggle_ise_logger():
    if ISELogger.logging:
        ise_toggle_button['image'] = off_img
        ise_status_text.set(LOGGER_DISABLED_MSG)
        ISELogger.logging = False
    else:
        ise_toggle_button['image'] = on_img
        ise_status_text.set(WAITING_TO_WRITE_MSG)
        ISELogger.logging = True


def toggle_meteo_logger():
    if METEOLogger.logging:
        meteo_toggle_button['image'] = off_img
        meteo_status_text.set(LOGGER_DISABLED_MSG)
        METEOLogger.logging = False
    else:
        meteo_toggle_button['image'] = on_img
        meteo_status_text.set(WAITING_TO_WRITE_MSG)
        METEOLogger.logging = True


def toggle_fm_logger():
    if FMLogger.logging:
        fm_toggle_button['image'] = off_img
        fm_status_text.set(LOGGER_DISABLED_MSG)
        FMLogger.logging = False
    else:
        fm_toggle_button['image'] = on_img
        fm_status_text.set(WAITING_TO_WRITE_MSG)
        FMLogger.logging = True


def toggle_hv_logger():
    if HVLogger.logging:
        hv_toggle_button['image'] = off_img
        hv_status_text.set(LOGGER_DISABLED_MSG)
        HVLogger.logging = False
    else:
        hv_toggle_button['image'] = on_img
        hv_status_text.set(WAITING_TO_WRITE_MSG)
        HVLogger.logging = True


def browse_files():
    global hv_log_path

    filename = filedialog.askopenfilename(
        initialdir='/',
        title='Select a File',
        filetypes=(('.log files', '*.log'), ('All files', '*.*'))
    )
    hv_logfile_text.set(filename)


def set_hv_log_path():
    global hv_log_path

    hv_log_path = hv_logfile_text.get()
    tk.messagebox.showinfo(title='Success', message=f'HV logfile set to {hv_log_path}')


def open_grafana():
    webbrowser.open_new(GRAFANA_URL)
# endregion


# region GUI
# Main window
root = tk.Tk()
root.title(WINDOW_TITLE)
root.geometry(f'{WINDOW_WIDTH}x{WINDOW_HEIGHT}')

# Resources
current_path = os.path.dirname(os.path.abspath(__file__))  # The current directory of the script
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
toggle_frame.rowconfigure(index=3, weight=1)

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

# FM Toggle Frame
fm_toggle_label = tk.Label(master=toggle_frame, text='FM Logger',
                           anchor='w', font=TOGGLE_LABEL_FONT)
fm_toggle_label.grid(column=0, row=3,
                     sticky=tk.W, padx=5, pady=5)

fm_toggle_button = ttk.Button(master=toggle_frame, image=off_img, command=toggle_fm_logger)
fm_toggle_button.grid(column=1, row=3,
                      sticky=tk.W, padx=5, pady=5)

fm_status_text = tk.StringVar()
fm_status_label = ttk.Label(master=toggle_frame, textvariable=fm_status_text)
fm_status_label.grid(column=2, row=3,
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

# HV Logfile
hv_logfile_frame = ttk.Frame(master=root)
hv_logfile_frame.pack(pady=30)

hv_logfile_label = tk.Label(master=hv_logfile_frame, text='HV GECO Log File',
                            font='Helvetica 12 italic')
hv_logfile_label.pack(anchor='w')

hv_logfile_text = tk.StringVar()
hv_logfile_text.set(hv_log_path)
hv_logfile_entry = tk.Entry(master=hv_logfile_frame, textvariable=hv_logfile_text,
                            width=50, fg='#333', bg='#eee')
hv_logfile_entry.pack(side='left')

hv_logfile_browse_button = tk.Button(master=hv_logfile_frame, text='Browse Files...', command=browse_files)
hv_logfile_browse_button.pack(side='left')

hv_logfile_select_button = tk.Button(master=hv_logfile_frame, text='Select', command=set_hv_log_path)
hv_logfile_select_button.pack(side='left')

# DB Write Status
db_write_status_text = tk.StringVar()
db_write_status_label = tk.Label(master=root, textvariable=db_write_status_text,
                                 padx=50, pady=10)
db_write_status_label.pack(anchor='e')

# Link to Grafana
grafana_button = ttk.Button(master=root, text=GRAFANA_BUTTON_TEXT, command=open_grafana)
grafana_button.pack(pady=10)
# endregion


# region Main Logic
# Main loop (called back by tkinter.after() after POLLING_MS, set in the config_data module)
def main():
    data_points = []  # Resets data collection to write to database
    Sensors.check_sensors()  # Check the connection status of sensors, try to set if missing

    # Gets the last line of the selected HV logfile
    if HVLogger.logging:
        HVLogger.line = HVLogger.get_last_line(hv_log_path)

    # Add data points and set status text accordingly
    ise_status_text.set(
        ISELogger.add_data(data_points))
    meteo_status_text.set(
        METEOLogger.add_data(data_points))
    hv_status_text.set(
        HVLogger.add_data(data_points))
    fm_status_text.set(
        FMLogger.add_data(data_points))

    if data_points and client.write_points(data_points):  # Successful write
        db_write_status_text.set(WRITE_SUCCESS_TEXT)
        db_write_status_label['fg'] = WRITE_SUCCESS_COLOR
    else:  # Couldn't write to database
        db_write_status_text.set(WRITE_FAIL_TEXT)
        db_write_status_label['fg'] = WRITE_FAIL_COLOR

    # Waits for POLLING_MS milliseconds, then callback to repeat loop
    root.after(POLLING_MS, main)


# Run
root.after(0, main)
root.mainloop()
# endregion
