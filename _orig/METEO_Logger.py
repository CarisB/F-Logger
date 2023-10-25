from influxdb import InfluxDBClient
from yoctopuce.yocto_humidity import *
from yoctopuce.yocto_pressure import *
from yoctopuce.yocto_temperature import *

# Constants
DB_HOST = "dbod-epdtmon.cern.ch"
DB_PORT = 8081
DB_USERNAME = "rpcgif"
DB_PASSWORD = "RPCgas2021"
DB_DATABASE = "data"

MEASUREMENT_LABEL = "yoctopuce"
DEVICE_ID = "Yocto-Meteo-V2"
TAG_PLACE = "904"
TAG_SETUP = "ise"

# Setup USB interface
errmsg = YRefParam()
if YAPI.RegisterHub("usb", errmsg) != YAPI.SUCCESS:
    sys.exit("Init Error: " + errmsg.value)

# Open connection with database
client = InfluxDBClient(host=DB_HOST, port=DB_PORT, username=DB_USERNAME, password=DB_PASSWORD,
                        database=DB_DATABASE, ssl=True, verify_ssl=False)

# Find sensors
humidity_sensor = YHumidity.FirstHumidity()
temperature_sensor = YTemperature.FirstTemperature()
pressure_sensor = YPressure.FirstPressure()

# Main Loop
while humidity_sensor.isOnline() and temperature_sensor.isOnline() and pressure_sensor.isOnline():
    humidity_value = humidity_sensor.get_currentRawValue()
    temperature_value = temperature_sensor.get_currentRawValue()
    pressure_value = pressure_sensor.get_currentRawValue()

    print(f"Temperature: {temperature_value} / Humidity: {humidity_value} / Pressure: {pressure_value}")

    data_points = [
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
        }
    ]

    res = client.write_points(data_points)
    print(res)

    YAPI.Sleep(2000)

# Exit code if a sensor isn't online
if not humidity_sensor.isOnline(): print("Humidity sensor is offline.")
if not temperature_sensor.isOnline(): print("Temperature sensor is offline.")
if not pressure_sensor.isOnline(): print("Pressure sensor is offline.")
print("Exiting.")
YAPI.FreeAPI()