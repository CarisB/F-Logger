class Config:
    HV_LOG_DEFAULT_PATH = "C:\\Users\\rpcgif\\cernbox\\Documents\\CAENGECO2020.log"
    GRAFANA_URL = "https://epdt-rd-monitoring.web.cern.ch/d/i_Rdg6C4z/904?orgId=1&from=now-7d&to=now&refresh=5m"

    POLLING_MS = 2000

    VOLTAGE_SENSOR_ID = "RXMVOLT2-1CA34F.genericSensor1"
    FLOWMETER_ID = "RX010V01-218513.genericSensor1"

    WINDOW_WIDTH = 800
    WINDOW_HEIGHT = 700

    WINDOW_TITLE = "F- Experiment Logger Tool"
    TITLE_LABEL = "F- Experiment Logger Tool"

    TITLE_FONT = 'Helvetica 36 bold'
    TOGGLE_LABEL_FONT = 'Helvetica 14 bold'

    SENSOR_OFFLINE_COLOR = '#b00'
    SENSOR_OFFLINE_MSG = "Sensor is offline."
    LOGGER_DISABLED_MSG = "Logger is disabled."
    WAITING_TO_WRITE_MSG = "Waiting..."

    WRITE_SUCCESS_TEXT = "Successfully written to database"
    WRITE_SUCCESS_COLOR = '#0a0'
    WRITE_FAIL_TEXT = "ERROR: Failed to write to database"
    WRITE_FAIL_COLOR = '#b00'

    GRAFANA_BUTTON_TEXT = "Open Grafana Dashboard"
