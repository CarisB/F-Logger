from config import *
from ISELogger import ISELogger
from METEOLogger import METEOLogger
from FMLogger import FMLogger
from HVLogger import HVLogger

import os
import webbrowser

import tkinter as tk
from tkinter import ttk
from tkinter import PhotoImage
from tkinter import filedialog
from tkinter import messagebox


class GUI:
    root: tk.Tk

    on_img: PhotoImage
    off_img: PhotoImage

    title_label: ttk.Label
    toggle_all_frame: ttk.Frame
    enable_all_button: ttk.Button
    disable_all_button: ttk.Button

    toggle_frame: ttk.Frame
    ise_toggle_label: tk.Label
    ise_toggle_button: ttk.Button
    ise_status_text: tk.StringVar
    ise_status_label: tk.Label
    ise_calibration_frame: ttk.Frame
    ise_calibration_label: tk.Label
    ise_calibration_formula_label: tk.Label
    ise_calibration_a_var: tk.DoubleVar
    ise_calibration_a_label: tk.Label
    ise_calibration_a_entry: tk.Entry
    ise_calibration_b_label: tk.Label
    ise_calibration_b_var: tk.DoubleVar
    ise_calibration_b_entry: tk.Entry
    ise_calibration_set_button: tk.Button
    ise_calibration_reset_button: tk.Button
    meteo_toggle_label: tk.Label
    meteo_toggle_button: ttk.Button
    meteo_status_text: tk.StringVar
    meteo_status_label: tk.Label
    fm_toggle_label: tk.Label
    fm_toggle_button: ttk.Button
    fm_status_text: tk.StringVar
    fm_status_label: tk.Label
    hv_toggle_label: tk.Label
    hv_toggle_button: ttk.Button
    hv_status_text: tk.StringVar
    hv_status_label: tk.Label

    hv_logfile_frame: ttk.Frame
    hv_logfile_label: tk.Label
    hv_logfile_text: tk.StringVar
    hv_logfile_entry: tk.Entry
    hv_logfile_browse_button: tk.Button
    hv_logfile_select_button: tk.Button

    db_write_status_text: tk.StringVar
    db_write_status_label: tk.Label
    grafana_button: ttk.Button

    @classmethod
    def init(cls):
        cls.root = tk.Tk()
        cls.root.title(Config.WINDOW_TITLE)
        cls.root.geometry(f'{Config.WINDOW_WIDTH}x{Config.WINDOW_HEIGHT}')

        # Resources
        current_path = os.path.dirname(os.path.abspath(__file__))  # The current directory of the script
        cls.on_img = PhotoImage(file=current_path + '/resources/on.png')
        cls.off_img = PhotoImage(file=current_path + '/resources/off.png')

        # Title
        cls.title_label = ttk.Label(
            master=cls.root, text=Config.TITLE_LABEL, font=Config.TITLE_FONT)
        cls.title_label.pack(pady=(20,0))

        # Enable All / Disable All
        cls.toggle_all_frame = ttk.Frame(master=cls.root)
        cls.toggle_all_frame.pack(anchor='w', padx=30, pady=20)

        cls.enable_all_button = ttk.Button(master=cls.toggle_all_frame,
                                           command=lambda: GUI.set_all(True),
                                           text='Enable All')
        cls.enable_all_button.pack(side='left')

        cls.disable_all_button = ttk.Button(master=cls.toggle_all_frame,
                                            command=lambda: GUI.set_all(False),
                                            text='Disable All')
        cls.disable_all_button.pack(side='left', padx=20)

        # ISE Calibration Frame
        inner_padding_x = 10
        inner_padding_y = 10

        cls.ise_calibration_frame = ttk.Frame(borderwidth=2, relief='ridge')
        cls.ise_calibration_frame.pack(anchor='w', padx=30, pady=(0, 20))

        cls.ise_calibration_label = tk.Label(master=cls.ise_calibration_frame,
                                             text='ISE (mV-to-PPM) calibration constants')
        cls.ise_calibration_label.pack(padx=inner_padding_x, pady=(inner_padding_y, 0))

        cls.ise_calibration_formula_label = tk.Label(master=cls.ise_calibration_frame,
                                                     text='PPM = e ^ ( (mV - B) / -A )')
        cls.ise_calibration_formula_label.pack()

        cls.ise_calibration_a_label = tk.Label(master=cls.ise_calibration_frame,
                                               text='A=')
        cls.ise_calibration_a_label.pack(side='left', padx=(inner_padding_x, 0), pady=(0, inner_padding_y))
        cls.ise_calibration_a_var = tk.DoubleVar()
        cls.ise_calibration_a_var.set(Config.ise_calibration_a)
        cls.ise_calibration_a_entry = tk.Entry(master=cls.ise_calibration_frame, textvariable=cls.ise_calibration_a_var,
                                               width=5, fg='#333', bg='#eee')
        cls.ise_calibration_a_entry.pack(side='left', pady=(0, inner_padding_y))

        cls.ise_calibration_b_label = tk.Label(master=cls.ise_calibration_frame,
                                               text='B=')
        cls.ise_calibration_b_label.pack(side='left', pady=(0, inner_padding_y))
        cls.ise_calibration_b_var = tk.DoubleVar()
        cls.ise_calibration_b_var.set(Config.ise_calibration_b)
        cls.ise_calibration_b_entry = tk.Entry(master=cls.ise_calibration_frame, textvariable=cls.ise_calibration_b_var,
                                               width=5, fg='#333', bg='#eee')
        cls.ise_calibration_b_entry.pack(side='left', pady=(0, inner_padding_y))

        cls.ise_calibration_set_button = tk.Button(master=cls.ise_calibration_frame,
                                                   command=cls.set_calibration,
                                                   text='Set')
        cls.ise_calibration_set_button.pack(side='left', pady=(0, inner_padding_y))
        cls.ise_calibration_reset_button = tk.Button(master=cls.ise_calibration_frame,
                                                     command=cls.reset_calibration,
                                                     text='Reset')
        cls.ise_calibration_reset_button.pack(side='left', padx=(0, inner_padding_x), pady=(0, inner_padding_y))

        # Main Toggle Frame
        cls.toggle_frame = ttk.Frame(master=cls.root)
        cls.toggle_frame.pack(anchor='w', padx=30)
        cls.toggle_frame.columnconfigure(index=0, weight=1)
        cls.toggle_frame.columnconfigure(index=1, weight=1)
        cls.toggle_frame.columnconfigure(index=2, weight=10)
        cls.toggle_frame.rowconfigure(index=0, weight=1)
        cls.toggle_frame.rowconfigure(index=1, weight=1)
        cls.toggle_frame.rowconfigure(index=2, weight=1)
        cls.toggle_frame.rowconfigure(index=3, weight=1)

        # ISE Toggle Frame
        cls.ise_toggle_label = tk.Label(master=cls.toggle_frame, text='ISE Logger',
                                        anchor='w', font=Config.TOGGLE_LABEL_FONT)
        cls.ise_toggle_label.grid(column=0, row=0,
                                  sticky=tk.W, padx=5, pady=5)

        cls.ise_toggle_button = ttk.Button(master=cls.toggle_frame,
                                           command=cls.toggle_ise_logger,
                                           image=cls.off_img)
        cls.ise_toggle_button.grid(column=1, row=0,
                                   sticky=tk.W, padx=5, pady=5)

        cls.ise_status_text = tk.StringVar()
        cls.ise_status_label = tk.Label(master=cls.toggle_frame, textvariable=cls.ise_status_text)
        cls.ise_status_label.grid(column=2, row=0,
                                  sticky=tk.W, padx=50, pady=5)

        # METEO Toggle Frame
        cls.meteo_toggle_label = tk.Label(master=cls.toggle_frame, text='METEO Logger',
                                          anchor='w', font=Config.TOGGLE_LABEL_FONT)
        cls.meteo_toggle_label.grid(column=0, row=1,
                                    sticky=tk.W, padx=5, pady=5)

        cls.meteo_toggle_button = ttk.Button(master=cls.toggle_frame,
                                             command=cls.toggle_meteo_logger,
                                             image=cls.off_img)
        cls.meteo_toggle_button.grid(column=1, row=1,
                                     sticky=tk.W, padx=5, pady=5)

        cls.meteo_status_text = tk.StringVar()
        cls.meteo_status_label = tk.Label(master=cls.toggle_frame, textvariable=cls.meteo_status_text)
        cls.meteo_status_label.grid(column=2, row=1,
                                    sticky=tk.W, padx=50, pady=5)

        # FM Toggle Frame
        cls.fm_toggle_label = tk.Label(master=cls.toggle_frame, text='FM Logger',
                                       anchor='w', font=Config.TOGGLE_LABEL_FONT)
        cls.fm_toggle_label.grid(column=0, row=2,
                                 sticky=tk.W, padx=5, pady=5)

        cls.fm_toggle_button = ttk.Button(master=cls.toggle_frame,
                                          command=cls.toggle_fm_logger,
                                          image=cls.off_img)
        cls.fm_toggle_button.grid(column=1, row=2,
                                  sticky=tk.W, padx=5, pady=5)

        cls.fm_status_text = tk.StringVar()
        cls.fm_status_label = tk.Label(master=cls.toggle_frame, textvariable=cls.fm_status_text)
        cls.fm_status_label.grid(column=2, row=2,
                                 sticky=tk.W, padx=50, pady=5)

        # HV Toggle Frame
        cls.hv_toggle_label = tk.Label(master=cls.toggle_frame, text='HV Logger',
                                       anchor='w', font=Config.TOGGLE_LABEL_FONT)
        cls.hv_toggle_label.grid(column=0, row=3,
                                 sticky=tk.W, padx=5, pady=5)

        cls.hv_toggle_button = ttk.Button(master=cls.toggle_frame,
                                          command=cls.toggle_hv_logger,
                                          image=cls.off_img)
        cls.hv_toggle_button.grid(column=1, row=3,
                                  sticky=tk.W, padx=5, pady=5)

        cls.hv_status_text = tk.StringVar()
        cls.hv_status_label = tk.Label(master=cls.toggle_frame, textvariable=cls.hv_status_text)
        cls.hv_status_label.grid(column=2, row=3,
                                 sticky=tk.W, padx=50, pady=5)

        # HV Logfile
        cls.hv_logfile_frame = ttk.Frame(master=cls.root)
        cls.hv_logfile_frame.pack(pady=20)

        cls.hv_logfile_label = tk.Label(master=cls.hv_logfile_frame, text='HV GECO Log File',
                                        font='Helvetica 12 italic')
        cls.hv_logfile_label.pack(anchor='w')

        cls.hv_logfile_text = tk.StringVar()
        cls.hv_logfile_text.set(HVLogger.hv_log_path)
        cls.hv_logfile_entry = tk.Entry(master=cls.hv_logfile_frame, textvariable=cls.hv_logfile_text,
                                        width=50, fg='#333', bg='#eee')
        cls.hv_logfile_entry.pack(side='left')

        cls.hv_logfile_browse_button = tk.Button(master=cls.hv_logfile_frame,
                                                 command=cls.browse_files,
                                                 text='Browse Files...')
        cls.hv_logfile_browse_button.pack(side='left')

        cls.hv_logfile_select_button = tk.Button(master=cls.hv_logfile_frame,
                                                 command=cls.set_hv_log_path,
                                                 text='Select')
        cls.hv_logfile_select_button.pack(side='left')

        # DB Write Status
        cls.db_write_status_text = tk.StringVar()
        cls.db_write_status_label = tk.Label(master=cls.root, textvariable=cls.db_write_status_text,
                                             padx=50, pady=10)
        cls.db_write_status_label.pack(anchor='e')

        # Link to Grafana
        cls.grafana_button = ttk.Button(master=cls.root,
                                        command=cls.open_grafana,
                                        text=Config.GRAFANA_BUTTON_TEXT)
        cls.grafana_button.pack(pady=10)

    @classmethod
    def toggle_ise_logger(cls):
        if ISELogger.logging: cls.set_ise_logger(False)
        else: cls.set_ise_logger(True)

    @classmethod
    def toggle_meteo_logger(cls):
        if METEOLogger.logging: cls.set_meteo_logger(False)
        else: cls.set_meteo_logger(True)

    @classmethod
    def toggle_fm_logger(cls):
        if FMLogger.logging: cls.set_fm_logger(False)
        else: cls.set_fm_logger(True)

    @classmethod
    def toggle_hv_logger(cls):
        if HVLogger.logging: cls.set_hv_logger(False)
        else: cls.set_hv_logger(True)

    @classmethod
    def set_all(cls, on: bool):
        cls.set_ise_logger(on)
        cls.set_meteo_logger(on)
        cls.set_fm_logger(on)
        cls.set_hv_logger(on)

    @classmethod
    def set_ise_logger(cls, on: bool):
        if on:
            cls.ise_toggle_button['image'] = cls.on_img
            cls.ise_status_text.set(Config.WAITING_TO_WRITE_MSG)
            ISELogger.logging = True
        else:
            cls.ise_toggle_button['image'] = cls.off_img
            cls.ise_status_text.set(Config.LOGGER_DISABLED_MSG)
            ISELogger.logging = False

    @classmethod
    def set_meteo_logger(cls, on: bool):
        if on:
            cls.meteo_toggle_button['image'] = cls.on_img
            cls.meteo_status_text.set(Config.WAITING_TO_WRITE_MSG)
            METEOLogger.logging = True
        else:
            cls.meteo_toggle_button['image'] = cls.off_img
            cls.meteo_status_text.set(Config.LOGGER_DISABLED_MSG)
            METEOLogger.logging = False

    @classmethod
    def set_fm_logger(cls, on: bool):
        if on:
            cls.fm_toggle_button['image'] = cls.on_img
            cls.fm_status_text.set(Config.WAITING_TO_WRITE_MSG)
            FMLogger.logging = True
        else:
            cls.fm_toggle_button['image'] = cls.off_img
            cls.fm_status_text.set(Config.LOGGER_DISABLED_MSG)
            FMLogger.logging = False

    @classmethod
    def set_hv_logger(cls, on: bool):
        if on:
            cls.hv_toggle_button['image'] = cls.on_img
            cls.hv_status_text.set(Config.WAITING_TO_WRITE_MSG)
            HVLogger.logging = True
        else:
            cls.hv_toggle_button['image'] = cls.off_img
            cls.hv_status_text.set(Config.LOGGER_DISABLED_MSG)
            HVLogger.logging = False

    @classmethod
    def set_calibration(cls):
        try:
            Config.set_ise_calibration(cls.ise_calibration_a_var.get(), cls.ise_calibration_b_var.get())
            Config.write_new_default_calibration()
            tk.messagebox.showinfo(title='Success',
                                   message=f'Calibration saved:\n'
                                           f'A={Config.ise_calibration_a}, B={Config.ise_calibration_b}')
        except tk.TclError:
            tk.messagebox.showinfo(title='ERROR', message='Please input a valid number.')

    @classmethod
    def reset_calibration(cls):
        cls.ise_calibration_a_var.set(Config.ise_calibration_a)
        cls.ise_calibration_b_var.set(Config.ise_calibration_b)
        tk.messagebox.showinfo(title='Success',
                               message=f'Calibration reset to:\n'
                                       f'A={Config.ise_calibration_a}, B={Config.ise_calibration_b}')

    @classmethod
    def browse_files(cls):
        filename = filedialog.askopenfilename(
            initialdir='/',
            title='Select a File',
            filetypes=(('.log files', '*.log'), ('All files', '*.*')))

        if filename != "":  # If file dialog wasn't cancelled
            cls.hv_logfile_text.set(filename)

    @classmethod
    def set_hv_log_path(cls):
        HVLogger.hv_log_path = cls.hv_logfile_text.get()
        tk.messagebox.showinfo(title='Success', message=f'HV logfile set to {HVLogger.hv_log_path}')

    @staticmethod
    def open_grafana():
        webbrowser.open_new(Config.GRAFANA_URL)
