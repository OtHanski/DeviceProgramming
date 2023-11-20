import pyvisa as visa



def TRUEFORMVISA(settings):
    # Find the USB address the Trueform is plugged into.
    # Note, at the moment the program is written specifically for USB.
    
    rm = visa.ResourceManager()
    ResList=rm.list_resources()
    ID =""
    
    for ResID in ResList:
        if ResID[0:3] == "USB" and ResID[-5:] == "INSTR":
            # Try-except to catch connection errors
            try:
                device = rm.open_resource(ResID)
                # Ping the device for ID, check if it's the TRUEFORM
                IDN = device.query("*IDN?").strip()
                print(ID)
            except:
                IDN = ""
                device.close()
            for IDCheck in settings["TRUEFORM"]["IDN"]:
                if IDCheck.upper() in IDN.upper():
                    settings["TRUEFORM"]["VISAID"] = ResID
                    break
                device.close()
    
    device.close()
    
    return settings

# Define the direct SCPI communication functions
def TRUEFORMWRITESCPI(settings,instr,argument):
    TRUEFORM = instr["TRUEFORM"]
    SCPI_string = argument+'\r\n'
    TRUEFORM.write(SCPI_string)
    return settings
    
def TRUEFORMREADSCPI(settings,instr,argument):
    TRUEFORM = instr["TRUEFORM"]
    read_data = TRUEFORM.read()
    print(str(read_data))
    return settings

def TRUEFORMQUERYSCPI(settings,instr,argument):
    TRUEFORM = instr["TRUEFORM"]
    SCPI_string = argument+'\r\n'
    read_data = TRUEFORM.query(SCPI_string)
    print(read_data)
    return settings

def TRUEFORMDELAY(settings,instr,argument):
    # argument: delay
    delay = argument

    correct_arg = False
    try:
        float(delay)
        correct_arg = True
    except ValueError:
        print("Invalid command argument")
    
    if correct_arg:
        # build command
        SCPI_string = "TRIG:DEL "+delay
        TRUEFORMWRITESCPI(settings,instr,SCPI_string)
        settings["TRUEFORM"]["DEL"] = delay
    
    return settings
    

def TRUEFORMINIT(settings,instrdummy=None,argumentdummy=None):
    
    # Fetch visa address
    settings = TRUEFORMVISA(settings)
    VISAID = settings["TRUEFORM"]["VISAID"]
    
    # Set up device connection
    rm = visa.ResourceManager()
    TRUEFORM = {"TRUEFORM": rm.open_resource(VISAID)}
    
    TRUEFORM_SETTINGS = settings["TRUEFORM"]
    
    TRUEFORM_COMMANDS = ["SOUR1:FUNC "+TRUEFORM_SETTINGS["FUNC"], "SOUR1:FREQ "+TRUEFORM_SETTINGS["FREQ"], \
                         "SOUR1:FUNC:PULS:WIDT "+TRUEFORM_SETTINGS["WIDT"],  "BURST:NCYC "+TRUEFORM_SETTINGS["BURST:NCYC"],\
                         "BURST:STAT "+TRUEFORM_SETTINGS["BURST:STAT"], "TRIG:SOUR "+TRUEFORM_SETTINGS["TRIG:SOUR"], \
                         "TRIG:DEL "+TRUEFORM_SETTINGS["DELAY"], "OUTP1 ON", "SOUR1:VOLT "+TRUEFORM_SETTINGS["VOLT"],\
                         f"SOUR1:VOLT:OFFS {float(TRUEFORM_SETTINGS['VOLT'])/2}"]
    
    # Reset the device
    TRUEFORM["TRUEFORM"].write("*RST")
    
    # Write the settings to device
    for SCPI_string in TRUEFORM_COMMANDS:
        TRUEFORMWRITESCPI(settings,TRUEFORM,SCPI_string)
    
    # Set the device status to "ON", enabling measurement
    settings["TRUEFORM"]["STAT"] = "ON"
    
    return settings, TRUEFORM["TRUEFORM"]