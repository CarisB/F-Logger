from config_data import *

from yoctopuce.yocto_genericsensor import *
from yoctopuce.yocto_humidity import YHumidity
from yoctopuce.yocto_temperature import YTemperature
from yoctopuce.yocto_pressure import YPressure


class Sensors:
    def __init__(self):
        # Setup USB interface
        errmsg = YRefParam()
        if YAPI.RegisterHub("usb", errmsg) != YAPI.SUCCESS:
            sys.exit("Init Error: " + errmsg.value)

        self.mv: YGenericSensor = YGenericSensor.FindGenericSensor(VOLTAGE_SENSOR_ID)
        self.humidity: YHumidity = YHumidity.FirstHumidity()
        self.temperature: YTemperature = YTemperature.FirstTemperature()
        self.pressure: YPressure = YPressure.FirstPressure()

    def check_sensors(self):
        if not self.mv.isOnline():
            self.mv = YGenericSensor.FindGenericSensor(VOLTAGE_SENSOR_ID)
        if not self.humidity.isOnline():
            self.humidity = YHumidity.FirstHumidity()
        if not self.temperature.isOnline():
            self.temperature = YTemperature.FirstTemperature()
        if not self.pressure.isOnline():
            self.pressure = YPressure.FirstPressure()