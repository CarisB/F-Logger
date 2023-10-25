from influxdb import InfluxDBClient
from yoctopuce.yocto_genericsensor import *

# Constants
DB_HOST = "dbod-epdtmon.cern.ch"
DB_PORT = 8081
DB_USERNAME = "rpcgif"
DB_PASSWORD = "RPCgas2021"
DB_DATABASE = "data"
VOLTAGE_SENSOR_ID = "RXMVOLT2-1CA34F.genericSensor1"
MEASUREMENT_LABEL = "yoctopuce"
DEVICE_ID = "Yocto-milliVolt-Rx-BNC"
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
mv_sensor = YGenericSensor.FindGenericSensor(VOLTAGE_SENSOR_ID)

# Main Loop
while mv_sensor.isOnline():
    mv_value = mv_sensor.get_currentRawValue()

    print(f"Voltage: {mv_value} mV")

    data_points = [
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
        }
    ]

    res = client.write_points(data_points)
    print(res)

    YAPI.Sleep(2000)

# Exit code if a sensor isn't online
if not mv_sensor.isOnline(): print("Voltage sensor is offline.")
print("Exiting.")
YAPI.FreeAPI()