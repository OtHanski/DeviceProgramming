from datetime import date
import pyvisa as visa
import numpy as np
import time
import struct
from .PROCESSING.FileHandler import WriteJson, CheckFolder



def RTMVISA(settings, instr = None, argument = None):
    # Find the USB address the RTM3004 is plugged into.
    # Note, at the moment the program is written specifically for USB.
    
    rm = visa.ResourceManager()
    ResList=rm.list_resources()
    ID = ""
    found = False
    
    for ResID in ResList:
        if ResID[0:3] == "USB" and ResID[-5:] == "INSTR":
            # Try-except to catch connection errors
            try:
                device = rm.open_resource(ResID)
                # Ping the device for ID, check if it's the RTM
                IDN = device.query("*IDN?").upper()
            except visa.errors.VisaIOError:
                IDN = ""
                device.close()
            for IDCheck in settings["RTM"]["IDN"]:
                if IDCheck.upper() in IDN:
                    settings["RTM"]["VISAID"] = ResID
                    break
                device.close()
    
    # Remember to close ya devices bois and gals
    device.close()
    
    return settings

# Define the direct SCPI communication functions
def RTMWRITESCPI(settings,instr,argument):
    RTM = instr["RTM3004"]
    SCPI_string = argument
    RTM.write(SCPI_string)
    return settings
    
def RTMREADSCPI(settings,instr,argument):
    RTM = instr["RTM3004"]
    read_data = RTM.read()
    print(str(read_data))
    return settings

def RTMQUERYSCPI(settings,instr,argument):
    RTM = instr["RTM3004"]
    SCPI_string = argument
    read_data = RTM.query(SCPI_string)
    print(read_data)
    return settings

# Direct setting commands
def RTMCHANSTAT(settings,instr,argument):
    # arguments: [channel, status]
    chan = argument[0]
    status = argument[1]
    
    allowed_chan = ("1","2","3","4")
    allowed_args = ("ON","OFF")
    if status in allowed_args and chan in allowed_chan:
        # build command
        SCPI_string = "CHAN"+str(chan)+":STAT "+status
        RTMWRITESCPI(settings,instr,SCPI_string)
        settings["RTM"]["CHAN_SETTINGS"]["CHAN"+chan]["STAT"] = status
    else:
        print("Invalid command argument")
        
    return settings
    
def RTMCHANOFFSET(settings,instr,argument):
    # arguments: [channel, offset]
    chan = argument[0]
    offset = argument[1]
    
    allowed_channels = ["1","2","3","4"]
    
    # Check whether arguments correct
    correct_arg = False
    try:
        float(offset)
        if chan in allowed_channels:
            correct_arg = True
    except ValueError:
        print("Invalid command argument")
    
    if correct_arg:
        # build command
        SCPI_string = "CHAN"+str(chan)+":OFFS "+offset
        RTMWRITESCPI(settings,instr,SCPI_string)
        settings["RTM"]["CHAN_SETTINGS"]["CHAN"+chan]["OFFS"] = offset
    
    return settings
        

def RTMCHANSCALE(settings,instr,argument):
    # arguments: [channel, scale]
    chan = argument[0]
    scale = argument[1]
    
    allowed_channels = ["1","2","3","4"]
       
    # Check whether arguments correct
    correct_arg = False
    try:
        float(scale)
        if chan in allowed_channels:
            correct_arg = True
    except ValueError:
        print("Invalid command argument")
    
    if correct_arg:
        # build command
        SCPI_string = "CHAN"+str(chan)+":SCAL "+scale
        RTMWRITESCPI(settings,instr,SCPI_string)
        settings["RTM"]["CHAN_SETTINGS"]["CHAN"+chan]["SCAL"] = scale
    
def RTMTIMEOFFSET(settings,instr,argument):
    # argument: offset
    offset = argument

    correct_arg = False
    try:
        float(offset)
        correct_arg = True
    except ValueError:
        print("Invalid command argument")

    if correct_arg:
        # build command
        SCPI_string = "TIM:POS "+offset
        RTMWRITESCPI(settings,instr,SCPI_string)
        settings["RTM"]["TIME_SETTINGS"]["POS"] = offset
    
    return settings

def RTMTIMESCALE(settings,instr,argument):
    # argument: scale
    scale = argument
    
    correct_arg = False
    try:
        float(scale)
        correct_arg = True
    except ValueError:
        print("Invalid command argument")    
    
    if correct_arg:
        # build command
        SCPI_string = "TIM:SCAL "+scale
        RTMWRITESCPI(settings,instr,SCPI_string)
        settings["RTM"]["TIME_SETTINGS"]["SCAL"] = scale
    else:
        print("Invalid command argument")
    
    return settings

def RTMDATAPOINTS(settings,instr,argument):
    # argument: n_points
    N = argument
    
    correct_arg = False
    try:
        int(N)
        correct_arg = True
    except ValueError:
        print("Invalid command argument")
        
    if correct_arg:
        # build command
        SCPI_string = "ACQ:POIN "+N
        RTMWRITESCPI(settings,instr,SCPI_string)
        settings["RTM"]["ACQUISITION_SETTINGS"]["POIN"] = N
    
    return settings

def RTMTRIGSOURCE(settings,instr,argument):
    # argument: source channel
    source = argument
    
    source_numbers = ("1","2","3","4")
    
    correct_arg = False
    if source in source_numbers:
        source = "CH"+source
        correct_arg = True
    else:
        print("Invalid command argument")
    
    if correct_arg:
        # build command
        SCPI_string = "TRIG:A:SOUR "+source
        RTMWRITESCPI(settings,instr,SCPI_string)
        settings["RTM"]["TRIG_SETTINGS"]["SOUR"] = source
    
    return settings

def RTMTRIGMODE(settings,instr,argument):
    # argument: trigger mode
    mode = argument
    
    allowed_modes = ["AUTO", "NORM"]
    correct_arg = False
    
    if mode in allowed_modes:
        correct_arg = True
    else:
        print("Invalid command argument")
    
    if correct_arg:
        # build command
        SCPI_string = "TRIG:A:MODE "+mode
        RTMWRITESCPI(settings,instr,SCPI_string)
        settings["RTM"]["TRIG_SETTINGS"]["MODE"] = mode
    
    return settings

def RTMTRIGLEVEL(settings,instr,argument):
    # argument: trigger level
    level = argument
    channel = settings["RTM"]["TRIG_SETTINGS"]["SOUR"]
    if channel[:2] == "CH":
        channel = channel[2]

    correct_arg = False
    try:
        float(level)
        correct_arg = True
    except ValueError:
        print("Invalid command argument")
    
    if correct_arg:
        # build command
        SCPI_string = "TRIG:A:LEV"+channel+" "+level
        RTMWRITESCPI(settings,instr,SCPI_string)
        settings["RTM"]["TRIG_SETTINGS"]["LEV"] = level
    
    return settings
    

# Main measurement routine, OLD VERSION, DO NOT USE
def RTMMEASURE(settings,instr,argument):
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
    
    # Setup measurement dictionary
    data = {                                                                        \
            "metadata": {                                                           \
                "measurement": settings["FILE"]["MEASUREMENT"],                     \
                "N": nWaveforms,                                                    \
                "Trigger channel": settings["RTM"]["TRIG_SETTINGS"]["SOUR"],        \
                "STAT": [settings["RTM"]["CHAN_SETTINGS"]["CHAN1"]["STAT"],         \
                         settings["RTM"]["CHAN_SETTINGS"]["CHAN2"]["STAT"],         \
                         settings["RTM"]["CHAN_SETTINGS"]["CHAN3"]["STAT"],         \
                         settings["RTM"]["CHAN_SETTINGS"]["CHAN4"]["STAT"]],        \
                "header": [],                                                       \
                "filetype": "measurement"                                           \
                        },                                                          \
            "time": {                                                               \
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
    
    for i in range(nWaveforms):
        # Build filepath according to settings, index by measurement number
        filename = settings["FILE"]["FILENAME"]+"_"+str(i+1).zfill(len(str(nWaveforms)))+".json"
        filepath = folder+"/"+filename
        data = RTMGETWAVEFORM(data,settings,instr)
        WriteJson(filepath,data)
        if (i+1)%10 == 0:
            print("Waveform number "+str(i+1)+" done")


def RTMGETHEADER(Channel,data,instr):
    # Fetches the data file header from RTM3004  
    header = []
    RTM = instr["RTM3004"]
    # [t_start, t_stop, n_samples, values per interval]
    headerstring = RTM.query("CHAN:DATA"+str(Channel)+":HEAD?")
    
    # Parse numerical values from the string format header
    sep1 = headerstring.find(",");
    sep2 = headerstring.find(",",sep1+1);
    sep3 = headerstring.find(",",sep2+1);
    header = [float(headerstring[0:sep1]), float(headerstring[sep1+1:sep2]), \
              int(headerstring[sep2+1:sep3]), int(headerstring[sep3+1:])]
              
    # If header is empty, there's a problem reading data from the test channel
    if header[0]==0 and header[1]==0 and header [2]==0 and header[3]==0:
        print("No reference signal detected.")
        ########################################
        #### REWRITE THIS PART, GLOBAL EXIT ####
        ########################################
        Waiter = input("Please connect a signal or enter \"q\" to quit.")
        if Waiter == "q":
            sys.exit()
        else:
            print("Retrying", flush=True)
            for rep in range(10):
                time.sleep(0.5)
                print('.', end='', flush=True)
            print('', end='\n', flush=True)
            FetchHeader()
    
    # Write header to metadata
    data["metadata"]["header"] = header
    
    return data,header

# Data decoder for RTM oscilloscope
def RTMDECODEWAVEFORMS(rawdata,header):
    # By default, data is read in binary packed format, this function decodes that into human-readable data.
    # [t_start, t_stop, n_samples, values per interval]
    t_start, t_stop, nSamples = header[0], header[1], header[2]
    dt=(t_stop-t_start)/(nSamples-1)
    
    # Initializing data array
    decWaves = np.zeros((1+len(rawdata),nSamples),'f')
    decWaves[0] = [round((t_start+i*dt)*1e10)/1e10 for i in range(nSamples)]
    
    for ch in range(len(rawdata)):
        # First character should be "#".
        pound = rawdata[ch][0:1]
        if pound != b'#':
            print("ERROR: Unknown data format returned from scope!")
            quit()
            
        # Second character is number of following digits for data string length value.
        length_digits = int(rawdata[ch][1:2])
        data_length = int(rawdata[ch][2:length_digits+2])
        
        # from the given data length, and known header length, we get indices:
        data_begin = length_digits + 2  # 2 for the '#' and digit count
        data_end = data_begin + data_length
        data_entries = data_length // 4;
        
        # Check that data length matches up
        #if data_entries != nSamples:
        #    print("ERROR: Data length not consistent with number of samples!")
        #    quit()
        # Unpack the data
        decoded = np.float32(struct.unpack('f'*data_entries,rawdata[ch][data_begin:data_end]))
        decWaves[ch+1] = decoded.tolist()
    return decWaves.tolist()
    
def RTMGETWAVEFORM(data,settings,instr):
    
    RTM = instr["RTM3004"]    
    
    # As comparison channel, choose first online channel
    Chanstat = data["metadata"]["STAT"]
    for index in range(len(Chanstat)):
        if Chanstat[index] == "ON":
            ComparisonChannel = index+1
    
    oldPoints = 0
    while True:
        # header: [t_start, t_stop, n_samples, values per interval]
        data, header = RTMGETHEADER(ComparisonChannel,data,instr)
        nPoints = header[2]
        if nPoints == oldPoints:
            break
        else:
            oldPoints = nPoints
    
    # Get comparison waveform
    Comp_Waveform = data["Channels"]["CH"+str(ComparisonChannel)]["Voltage"]

    while True:
        # Initialize data array
        tempdata=[]
        # Datakey tells which channels were recorded
        datakey=[]
        
        # Read all (active) data channels
        if Chanstat[0] == "ON":
            RTM.write("CHAN1:DATA?")
            ch1 = RTM.read_raw()
            tempdata.append(ch1)
            datakey.append("CH1")
        if Chanstat[1] == "ON":
            RTM.write("CHAN2:DATA?")
            ch2 = RTM.read_raw()
            tempdata.append(ch2)
            datakey.append("CH2")
        if Chanstat[2] == "ON":
            RTM.write("CHAN3:DATA?")
            ch3 = RTM.read_raw()
            tempdata.append(ch3)
            datakey.append("CH3")
        if Chanstat[3] == "ON":
            RTM.write("CHAN4:DATA?")
            ch4 = RTM.read_raw()
            tempdata.append(ch4)
            datakey.append("CH4") 
        
        # Read the comparison data
        RTM.write("CHAN"+str(ComparisonChannel)+":DATA?")
        ch_check = RTM.read_raw()
        
        # Check that data has changed from last measurement (Comp_Waveform) 
        # and that oscilloscope didn't refresh mid-measurement (ch_check)
        if (tempdata[ComparisonChannel-1] != Comp_Waveform) and (tempdata[ComparisonChannel-1] == ch_check):
            data, header = RTMGETHEADER(ComparisonChannel,data,instr)
            # Decode the read data
            tempdata = RTMDECODEWAVEFORMS(tempdata,header)
            Correct_length = True
            for column in tempdata:
                if len(column) != nPoints:
                    Correct_length = False
            
            if Correct_length:
                # Write the measured data to the data file
                data["time"]["data"] = tempdata[0]
                for index in range(len(datakey)):
                    data["Channels"][datakey[index]]["Voltage"] = tempdata[index+1]
                    
                return data
    
def RTMINIT(settings,instrdummy=None,argumentdummy=None):
    
    # Fetch visa address
    settings = RTMVISA(settings)
    VISAID = settings["RTM"]["VISAID"]
    
    # Set up device connection
    rm = visa.ResourceManager()
    RTM = {"RTM3004": rm.open_resource(VISAID)}
    
    RTM_SETTINGS = settings["RTM"]
    
    # Reset the device
    RTM["RTM3004"].write("*RST")
    
    # Set initial channel settings
    for chan in RTM_SETTINGS["CHAN_SETTINGS"]:
        for parameter in RTM_SETTINGS["CHAN_SETTINGS"][chan]:
            SCPI_string = chan +":"+ parameter+" " + RTM_SETTINGS["CHAN_SETTINGS"][chan][parameter]
            RTMWRITESCPI(settings,RTM,SCPI_string)
    
    # Set initial time settings
    for parameter in RTM_SETTINGS["TIME_SETTINGS"]:
        SCPI_string = "TIM:" + parameter + " " + RTM_SETTINGS["TIME_SETTINGS"][parameter]
        RTMWRITESCPI(settings,RTM,SCPI_string)
    
    # Set trigger settings
    for parameter in RTM_SETTINGS["TRIG_SETTINGS"]:
        SCPI_string = "TRIG:A:" + parameter + " " + RTM_SETTINGS["TRIG_SETTINGS"][parameter]
        RTMWRITESCPI(settings,RTM,SCPI_string)
    
    # Set data acquisition settings 
    for parameter in RTM_SETTINGS["ACQUISITION_SETTINGS"]:
        SCPI_string = "ACQ:" + parameter + " " + RTM_SETTINGS["ACQUISITION_SETTINGS"][parameter]
        RTMWRITESCPI(settings,RTM,SCPI_string)
        
    # Set format settings. Avoid touching, the decoder has been programmed for these.
    for parameter in RTM_SETTINGS["FORMAT_SETTINGS"]:
        SCPI_string = parameter + " " + RTM_SETTINGS["FORMAT_SETTINGS"][parameter]
        RTMWRITESCPI(settings,RTM,SCPI_string)

    # Set the device status to "ON", enabling measurement
    settings["RTM"]["STAT"] = "ON"
    
    return settings, RTM["RTM3004"]
    
    
    
    
    
    
    
    