from .PROCESSING.statistics import get_stats as STATISTICS
from .PROCESSING.histogram import get_histogram as HISTOGRAM
from .RTM_CONTROLS import *
from .TRUEFORM_CONTROLS import *
from .LAKESHORE_CONTROLS import *
from .MAXIGAUGE_CONTROLS import *
from .POWERSENSORU8_CONTROLS import *
from .SYSTEM_COMMANDS import *
from .PROCESSING.FileHandler import *
from pytimedinput import timedInput
from datetime import datetime
import traceback

"""
Please only add multi-device functions here. Device-specific
functions should be programmed in their respective files.
"""

def INIT(settings,instr = {}):
    
    argument = None
    
    devices_initialized = False
    
    # All of the instruments are collected into the instr dictionary for quick access
    
    ### Oscilloscope ###
    if settings["RTM"]["STAT"] == "ON":
        settings, RTMinstr = RTMINIT(settings)
        instr["RTM3004"] = RTMinstr
        devices_initialized = True
    
    ### Signal generator ###
    if settings["TRUEFORM"]["STAT"] == "ON":
        settings,TRUEFORMinstr = TRUEFORMINIT(settings)
        instr["TRUEFORM"] = TRUEFORMinstr
        devices_initialized = True
    
    ### Temperature controller ###
    if settings["LAKESHORE"]["STAT"] == "ON":
        try:
            instr["LAKESHORE"]
        except KeyError:
            settings,LAKESHOREinstr = LAKESHOREINIT(settings)
            instr["LAKESHORE"] = LAKESHOREinstr
            devices_initialized = True
    
    ### Pressure gauge ###
    if settings["MAXIGAUGE"]["STAT"] == "ON":
        settings,MAXIGAUGEinstr = MAXIGAUGEINIT(settings)
        instr["MAXIGAUGE"] = MAXIGAUGEinstr
        devices_initialized = True
    
    ### Microwave power ###
    if settings["POWERSENSORU8"]["STAT"] == "ON":
        settings,POWERSENSORinstr = POWERSENSORINIT(settings)
        instr["POWERSENSORU8"] = POWERSENSORinstr
        devices_initialized = True
    
    if devices_initialized:
        print("Initializing",end='', flush=True)
        for rep in range(12):
            time.sleep(0.5)
            print('.', end='', flush=True)
        print('', end='\n', flush=True)
    else:
        print("No devices enabled")
    
    devicestr = "Devices connected:"
    for key in instr:
        devicestr += "\n├ "+key
    print("\n"+devicestr+"\n")
    
    return settings, instr


def GETMETADATA(settings,instr,data):
    
    # Measurement time
    dateVAR = date.today()
    timestring = dateVAR.strftime("%Y/%m/%d, %H:%M:%S")
    data["time"]["start time"] = timestring
    
    # Pressures
    if settings["MAXIGAUGE"]["STAT"] == "ON":
        data["metadata"]["pressures"] = MAXIGAUGEPRESSURES(settings, instr["MAXIGAUGE"])
    
    # Microwave power
    if settings["POWERSENSORU8"]["STAT"] == "ON":
        data["metadata"]["µwave power"] = POWERSENSORGETPOWER(settings, instr["POWERSENSORU8"])
    
    #Temperatures
    if settings["LAKESHORE"]["STAT"] == "ON":
        data["metadata"]["temperature"] = LAKESHORETEMP(settings, instr["LAKESHORE"])
    
    return data
    

# Main measurement routine
def WAVEFORMMEASURE(settings,instr,argument):
    try:
        nWaveforms = int(argument)
    except ValueError:
        print("Invalid argument")
        return settings
    
    rootfolder = settings["FILE"]["ROOTFOLDER"]
    measfolder = "/"+settings["FILE"]["MEASFOLDER"]
    
    # Set up measurement folder by date
    dateVAR = date.today()
    datestring = dateVAR.strftime("%Y-%m-%d")
    measfolder =  datestring + measfolder
    
    folder = rootfolder +"/"+ measfolder
    # Create folder
    CheckFolder(folder)
    
    # Initialise data dictionary
    data = INITDATA(settings,nWaveforms)
    
    for i in range(nWaveforms):
        # Build filepath according to settings, index by measurement number
        filename = settings["FILE"]["FILENAME"]+"_"+str(i+1).zfill(len(str(nWaveforms)))+".json"
        filepath = folder+"/"+filename
        # Get oscilloscope data
        data = RTMGETWAVEFORM(data,settings,instr)
        # Get metadata (temperature, start time, pressures etc)
        data = GETMETADATA(settings,instr,data)
        WriteJson(filepath,data)
        if (i+1)%10 == 0:
            print("Waveform number "+str(i+1)+" done")


def CONNECTIONTEST(settings,instr,argument= None):
    # Test whether connected devices can be reached
    
    # Oscilloscope test
    try:
        RTMQUERYSCPI(settings,instr,"*IDN?")
        print("RTM query successful")
    except Exception as exname:
        print("RTM connection test ran into the following error:\n"+traceback.format_exc())
    
    # Signal generator test
    try:
        TRUEFORMQUERYSCPI(settings,instr,"*IDN?")
        print("Signal generator query successful")
    except Exception as exname:
        print("Signal generator connection test ran into the following error:\n"+traceback.format_exc())
    
    # Pressure gauge test
    try:
        instr["MAXIGAUGE"].identify()
        print("Maxigauge pressuremeter query successful")
    except Exception as exname:
        print("Pressure gauge connection test ran into the following error:\n"+traceback.format_exc())
    
    # Temperature controller 
    try:
        print(repr(LAKESHORETEMP(settings, instr["LAKESHORE"], argument=None)))
        print("Lakeshore temperature controller query successful")
    except Exception as exname:
        print("Temperature controller connection test ran into the following error:\n"+traceback.format_exc())
    
    # Powersensor 
    try:
        print(repr(POWERSENSORGETPOWER(settings, instr["POWERSENSORU8"], argument = None)))
        print("Power sensor U8 controller query successful")
    except Exception as exname:
        print("Power sensor U8 connection test ran into the following error:\n"+traceback.format_exc())
    

def INITDATA(settings, nWaveforms):
    # Setup measurement dictionary
    data = {                                                                        \
            "metadata": {                                                           \
                "measurement": settings["FILE"]["MEASUREMENT"],                     \
                "comment": settings["COMMENT"],                                     \
                "N": nWaveforms,                                                    \
                "Trigger channel": settings["RTM"]["TRIG_SETTINGS"]["SOUR"],        \
                "STAT": [settings["RTM"]["CHAN_SETTINGS"]["CHAN1"]["STAT"],         \
                         settings["RTM"]["CHAN_SETTINGS"]["CHAN2"]["STAT"],         \
                         settings["RTM"]["CHAN_SETTINGS"]["CHAN3"]["STAT"],         \
                         settings["RTM"]["CHAN_SETTINGS"]["CHAN4"]["STAT"]],        \
                "header": [],                                                       \
                "filetype": "measurement",                                          \
                "pressures": [],                                                    \
                "µwave power": "",                                                  \
                "temperature": ""                                                   \
                        },                                                          \
            "time": {                                                               \
                "start time": "",                                                   \
                "unit": "s",                                                        \
                "data": []                                                          \
                    },                                                              \
            "Channels": {                                                           \
                    "CH1":  {                                                       \
                        "unit": "V",                                                \
                        "Voltage": []                                               \
                            },                                                      \
                    "CH2":  {                                                       \
                        "unit": "V",                                                \
                        "Voltage": []                                               \
                            },                                                      \
                    "CH3":  {                                                       \
                        "unit": "V",                                                \
                        "Voltage": []                                               \
                            },                                                      \
                    "CH4":  {                                                       \
                        "unit": "V",                                                \
                        "Voltage": []                                               \
                            }                                                       \
                        }                                                           \
            }
            
    return data

def DIAGNOSTICS(settings, instr, argument):
    # Argument = seconds between measurements
    if argument == "": argument = 10
    waittime = float(argument)
    MAXIGAUGE = instr["MAXIGAUGE"]
    LAKESHORE = instr["LAKESHORE"]
    
    rootfolder = settings["FILE"]["ROOTFOLDER"]
    measfolder = "/"+settings["FILE"]["MEASFOLDER"]
    
    # Set up measurement folder by date
    dateVAR = date.today()
    datestring = dateVAR.strftime("%Y-%m-%d")
    measfolder =  datestring + measfolder
    
    folder = rootfolder +"/"+ measfolder
    # Create folder
    CheckFolder(folder)
    
    n = 0
    filepath = folder+f"/DIAGNOSTIC{n}.dat"
    while os.path.exists(filepath):
        n+=1
        filepath = folder+f"/DIAGNOSTIC{n}.dat"
    
    with open(filepath,"w") as f:
        f.write("time\tpressures\ttemps\n")
    
    print(f"Measuring temperature and pressure, waittime {waittime} s\n Write \"q\" to end measurement") 
    
    while True:
        time = datetime.now().strftime("%H:%M:%S")
        pressures = MAXIGAUGEPRESSURES(settings, MAXIGAUGE, argument = [1,2,3,4])
        temps = LAKESHORETEMP(settings, LAKESHORE, argument=None)
        with open(filepath,"a") as f:
            f.write(f"{time}\t{pressures}\t{temps}\n")
        inp,timeout = timedInput("<<<",timeout = waittime)
        if inp == "q":
            break
        
    return settings