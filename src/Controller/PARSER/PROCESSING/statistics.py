import numpy as np
from .FileHandler import ReadJson, WriteJson, ChooseFiles
from .IntegrationLimits import GetLimits

def initstats():
    # Initialise statistics dictionary
    stats = { \
    "metadata": {
             "measurement": "", \
             "N": "0",  \
             "filetype": "statistics"
             },  \
    "time": {"data": [],"unit": "s"}, \
    "Channels": {  \
                "CH1":{"avg":[], "stderr":[], "unit": "V"}, \
                "CH2":{"avg":[], "stderr":[], "unit": "V"}, \
                "CH3":{"avg":[], "stderr":[], "unit": "V"}, \
                "CH4":{"avg":[], "stderr":[], "unit": "V"}  \
                } \
    }
    return stats
    
def sortfiles(files):
    # Use dictionary to figure out which file is part of which measurement
    sorted = {}
    for file in files:
        # Read from metadata which measurement series each file is a part of
        measurement = ReadJson(file)["metadata"]["measurement"]
        # Try adding file to corresponding measurement key, create key if not existing
        try:
            sorted[measurement].append(file)
        except KeyError:
            sorted[measurement] = [file]
    
    return sorted

    
def averaging(filelist,stats):
    # Due to vast amount of data, can't really be done by passing the data directly
    # Additionally, we can't keep the data in memory for processing, so will need to
    # read the datafiles multiple times for the processing.

    
    # Initialise averaging
    data = ReadJson(filelist[0])
    len_data = len(data["time"]["data"])
    stats["time"]["data"] = data["time"]["data"]
    for Channel in stats["Channels"]:
        stats["Channels"][Channel]["avg"] = np.zeros(len_data).tolist()
        stats["Channels"][Channel]["stderr"] = np.zeros(len_data).tolist()
    N = 0
    
    # On first pass we average
    for file in filelist:
        data = ReadJson(file)
        for Channel in data["Channels"]:
            Voltage = data["Channels"][Channel]["Voltage"]
            if len(Voltage) > 0:
                # First we sum all of the datapoints
                for index in range(len(Voltage)):
                    stats["Channels"][Channel]["avg"][index] += Voltage[index]
            else:
                stats["Channels"][Channel]["avg"] = []
                stats["Channels"][Channel]["stderr"] = []
        N += 1
    
    # Save number of measurements
    stats["metadata"]["N"] = str(N)
    
    # Then divide to get the average and set the units
    for Channel in stats["Channels"]:
        if stats["Channels"][Channel]["avg"] != []:
            for index in range(len_data):
                stats["Channels"][Channel]["avg"][index] /= N
    
    
    ### NOTE, THE STUFF BELOW MIGHT HAVE A BUG(s), DON'T REMEMBER IF FIXED => CHECK ###
    
    # On second pass we calculate deviation.
    for file in filelist:
        data = ReadJson(file)
        for Channel in data["Channels"]:
            if stats["Channels"][Channel]["avg"] != []:
                Voltage = data["Channels"][Channel]["Voltage"]
                # Sum squared deviation from mean
                for index in range(len(Voltage)):
                    stats["Channels"][Channel]["stderr"][index] += (stats["Channels"][Channel]["avg"][index]-Voltage[index])**2
    
    # Then divide by N and take sqrt to get standard deviation
    for Channel in stats["Channels"]:
        if stats["Channels"][Channel]["avg"] != []:
            for index in range(len_data):
                stats["Channels"][Channel]["stderr"][index] = (stats["Channels"][Channel]["stderr"][index])**(1/2)/N
    
    return stats
    
    
def Integrate(intLimits, offset, SigChan, meas_files, stats):
    
    time = np.array(stats["time"]["data"])
    avgVoltages = np.array(stats["Channels"][SigChan]["avg"])
    n_points = len(time)
    
    # Find list of indices where time is within our integration limits
    int_indices = [i for i in range(len(time)) \
                    if time[i] >= intLimits[0] and time[i] <= intLimits[1]]
    
    # Limit integral to within the integration limtis
    time = time[int_indices]
    avgVoltages = avgVoltages[int_indices]
    n_points = len(time)
    
    # Apply offset
    for i in range(n_points):
        avgVoltages[i] -= offset
    
    # Calculate integral
    avgIntegral = np.trapz(avgVoltages, time)
    stats["Channels"][SigChan]["Integral"] = avgIntegral
    stats["Channels"][SigChan]["IntegralError"] = 0
    
    # To get statistics of integral, we need to again read through the files
    Voltages = np.zeros(1)
    N = 0
    
    for file in meas_files:
        N+=1
        data = ReadJson(file)
        # Fetch the voltages matching our timewindow
        Voltages = np.array(data["Channels"][SigChan]["Voltage"])[int_indices]
        
        for i in range(n_points):
            Voltages[i] -= offset
        
        # Integral using trapezoidal approximation
        integral = np.trapz(Voltages, time)
        # Sum squared deviation from mean
        stats["Channels"][SigChan]["IntegralError"] += (integral-avgIntegral)**2
    
    # Then divide by N and take sqrt to get standard deviation
    for Channel in stats["Channels"]:
        stats["Channels"][SigChan]["IntegralError"] = (stats["Channels"][SigChan]["IntegralError"])**(1/2)/N
    
    return stats
    
    
def AskSignalChannel():
    # Ask user which channel data is expected to have the signal
    User_in = input("Please enter the number of the channel holding\nthe signal data, or enter \"quit\" to quit: ")
    if User_in.strip() == "quit":
        return User_in
    try:
        Chan = "CH"+str(int(User_in))
        return Chan
    except ValueError:
        print("Invalid input, please enter an integer number.\n")
        
    
def get_stats(settings,instr,arg):
    # This is the "main" routine
    
    # First initialise our statistics dictionary,
    stats = initstats()
    
    # Next let's fetch our files. Files are sorted by "measurement" metadata into a dictionary
    files = ChooseFiles(settings["FILE"]["ROOTFOLDER"])
    if len(files) == 0:
        print("No files selected, canceling STATISTICS")
        return None
    files_sorted = sortfiles(files)
    
    # Define the datafolder to save processed files in
    for measurement in files_sorted:
        foldername = files_sorted[measurement][0]
        break
    # Fetch the folder used for the chosen files, put the processed files in a subfolder
    foldername = foldername[:foldername.rfind("/")]+"/processed/"
    
    # Ask user for the signal channel for integration
    SigChan = AskSignalChannel()
    if SigChan == "quit":
        sys.exit("EXIT")
    
    # Controls whether integration limits are asked for each measurement
    unset_Limits = True
    while True:
        User_in = input("Use the same integration limits for all measurements? y/n/quit:\n")
        if User_in == "y":
            ask_Limits = False
            break
        elif User_in == "n":
            ask_Limits = True
            break
        elif User_in.strip() == "quit":
            sys.exit("EXIT")
        else:
            print("Invalid input. Please enter a valid input (y/n/quit)")

    # In each loop we process and save the data for one measurement set
    for measurement in files_sorted:
        stats["measurement"] = measurement
        stats = averaging(files_sorted[measurement],stats)
        # The saved stats files are named after the measurements
        filepath = foldername+measurement+".json"
        
        if ask_Limits or unset_Limits:
            Waveform = np.array([stats["time"]["data"],stats["Channels"][SigChan]["avg"]])
            intLimits, offset = GetLimits(Waveform)
            unset_limits = False
        stats = Integrate(intLimits, offset, SigChan, files_sorted[measurement], stats)
        
        WriteJson(filepath,stats)
    
    return settings
    