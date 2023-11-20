import pyvisa as visa

def POWERSENSORINIT(settings,instrdummy=None,argumentdummy=None):
    
    # Fetch visa address
    settings = POWERSENSORVISA(settings)
    VISAID = settings["POWERSENSORU8"]["VISAID"]
    
    # Set up device connection
    rm = visa.ResourceManager()
    POWERSENSOR = rm.open_resource(VISAID)
    
    return settings, POWERSENSOR

def POWERSENSORVISA(settings, instr = None, argument = None):
    # Find the USB address the Keysight U8 is plugged into.
    # Note, at the moment doesn't work for non-USB
    
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
                device.close()
                IDN = ""
            for IDCheck in settings["POWERSENSORU8"]["IDN"]:
                if IDCheck.upper() in IDN:
                    settings["POWERSENSORU8"]["VISAID"] = ResID
                    break
                device.close()
    
    # Close the device before finishing.
    device.close()
    
    return settings
    
def POWERSENSORGETPOWER(settings, POWERSENSOR, argument = None):
    # Fetch power from U8 and convert to watts (Courtesy of Philipp
    dbm = float(POWERSENSOR.query('FETCH?'))
    watt = 10**((dbm-30)/10)
    
    return watt