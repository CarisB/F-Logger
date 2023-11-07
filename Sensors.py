from config import *

from yoctopuce.yocto_genericsensor import *
from yoctopuce.yocto_humidity import YHumidity
from yoctopuce.yocto_temperature import YTemperature
from yoctopuce.yocto_pressure import YPressure


class Sensors:
    mv: YGenericSensor
    fm: YGenericSensor
    humidity: YHumidity
    temperature: YTemperature
    pressure: YPressure

    @staticmethod
    def init():
        # Setup USB interface
        errmsg = YRefParam()
        if YAPI.RegisterHub("usb", errmsg) != YAPI.SUCCESS:
            sys.exit("Init Error: " + errmsg.value)

        Sensors.mv = YGenericSensor.FindGenericSensor(Config.VOLTAGE_SENSOR_ID)
        Sensors.fm = YGenericSensor.FindGenericSensor(Config.FLOWMETER_ID)
        Sensors.humidity = YHumidity.FirstHumidity()
        Sensors.temperature = YTemperature.FirstTemperature()
        Sensors.pressure = YPressure.FirstPressure()

    @staticmethod
    def check_sensors():
        if not Sensors.mv.isOnline():
            Sensors.mv = YGenericSensor.FindGenericSensor(Config.VOLTAGE_SENSOR_ID)
        if not Sensors.fm.isOnline():
            Sensors.fm = YGenericSensor.FindGenericSensor(Config.FLOWMETER_ID)
        if not Sensors.humidity:
            Sensors.humidity = YHumidity.FirstHumidity()
        if not Sensors.temperature:
            Sensors.temperature = YTemperature.FirstTemperature()
        if not Sensors.pressure:
            Sensors.pressure = YPressure.FirstPressure()
