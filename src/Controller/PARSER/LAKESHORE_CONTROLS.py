from .lakeshore.model_335 import *

"""
Note, due to the device being a pain in the ass, we use a different library for
controlling the lakeshore rather than the usual pyvisa. The drivers are included
in the "lakeshore" folder, see docs there for extra info.
"""

def LAKESHOREINIT(settings,instrdummy=None,argumentdummy=None):
    
    LAKESHORE = Model335(57600)
    
    sensor_settingsA = Model335InputSensorSettings(Model335InputSensorType.DIODE, True, False,
                                              Model335InputSensorUnits.KELVIN,
                                              Model335DiodeRange.TWO_POINT_FIVE_VOLTS)
    
    sensor_settingsB = Model335InputSensorSettings(Model335InputSensorType.DIODE, True, False,
                                              Model335InputSensorUnits.KELVIN,
                                              Model335DiodeRange.TWO_POINT_FIVE_VOLTS)
    
    # Apply these settings to input A of the instrument
    LAKESHORE.set_input_sensor("A", sensor_settingsA)
    #LAKESHORE.set_input_sensor("B", sensor_settingsB)
    #
    ## Set diode excitation current on channel A to 10uA
    LAKESHORE.set_diode_excitation_current("A", Model335DiodeCurrent.TEN_MICROAMPS)
    #LAKESHORE.set_diode_excitation_current("B", Model335DiodeCurrent.TEN_MICROAMPS)
    
    ### Setpoints for temperature, disabled until I have time to properly test the temperature control side.
    #LAKESHORE.set_heater_setup_one(Model335HeaterResistance.HEATER_50_OHM, 1.0, Model335HeaterOutputDisplay.POWER)
    #set_point = 280
    #LAKESHORE.set_control_setpoint(1, set_point)
    #LAKESHORE.set_control_setpoint(2, set_point)
    
    # Turn on the heater by setting range
    #LAKESHORE.set_heater_range(1, Model335HeaterRange.HIGH)
    
    return settings, LAKESHORE


def LAKESHORETEMPANDHEAT(settings, LAKESHORE, argument):
    
    # Collect instrument data
    heater_output_1 = LAKESHORE.get_heater_output(1)
    heater_output_2 = LAKESHORE.get_heater_output(2)
    temperature_reading = LAKESHORE.get_all_kelvin_reading()
    print(temperature_reading)
    
    return temperature_reading

def LAKESHORETEMP(settings, LAKESHORE, argument=None):
    
    # Collect instrument data
    temperature_reading = LAKESHORE.get_all_kelvin_reading()
    
    return temperature_reading