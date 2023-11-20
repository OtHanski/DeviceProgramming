from .pfeiffer.PfeifferVacuumVISA import *

"""
For the Pfeiffer vacuum gauge we use an open-source library originally written for serial
connection, but I converted it to pyvisa. I may at a later point clean the code and make it
more similar to the other devices, but no time now.
Otto H
"""

def MAXIGAUGEINIT(settings,instrdummy=None,argumentdummy=None):
    
    MAXIGAUGE = MaxiGauge(settings)
    
    return settings, MAXIGAUGE


def MAXIGAUGEPRESSURES(settings, MAXIGAUGE, argument = [1,2,3,4]):
    # Argument: list of gauges 1-6 (integer) to measure, for example [1,2,4,6]
    
    # Collect instrument data
    pressurelist = []
    for gauge in argument:
        pres = MAXIGAUGE.pressure(gauge)
        p = pres.pressure
        pressurelist.append(["gauge "+str(gauge),float(p)])
    
    return pressurelist

def MAXIGAUGETEST(settings, instr, argument = None):
    # Test maxigauge reading
    # arg = n
    maxi = instr["MAXIGAUGE"]
    pressures = MAXIGAUGEPRESSURES(settings, maxi, [1,2,3,4])
    print("Pressure reading: "+repr(pressures))
    
    if argument:
        for i in range(argument):
            print(repr(maxi.read()))
    
    return settings