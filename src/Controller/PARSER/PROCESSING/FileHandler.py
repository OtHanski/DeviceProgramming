import os
import json
import tkinter as tk
from tkinter import filedialog

def ChooseFolder(initdir = ".."):
    # Initialise tkinter window
    root = tk.Tk()
    root.withdraw()
    
    # Prompt to choose the files to process.
    datafolder = filedialog.askdirectory(initialdir = initdir)
    
    return datafolder

def ChooseFiles(initdir = ".."):
    # Initialise tkinter window
    root = tk.Tk()
    root.withdraw()
    
    # Prompt to choose the files to process.
    files = filedialog.askopenfilenames(initialdir = initdir)
    
    # Return filenames as simple list
    return files

def ChooseSingleFile(initdir = ".."):
    # Initialise tkinter window
    root = tk.Tk()
    root.withdraw()
    
    # Prompt to choose the files to process.
    file = filedialog.askopenfilename(initialdir = initdir)
    
    # Return filenames as simple list
    return file

def CheckFolder(folderpath):
    # Check whether folder exists, create it if not
    if not os.path.exists(folderpath):
        os.makedirs(folderpath)
        print("Folder created: " + folderpath)

def WriteJson(filepath, dict):
    # Writes a dictionary to a json file
    folderpath = filepath[:filepath.rfind("/")]
    CheckFolder(folderpath)
    
    with open(filepath, "w") as json_file:  
        json.dump(dict, json_file, indent = 4, sort_keys = True)
    
    return None

def ReadJson(filepath):
    # Reads a json file, returns the dictionary form of the file
    with open(filepath, "r") as json_file:
        dict = json.load(json_file)
    
    return dict

def ReadTXT(filepath):
    # Reads a txt into a string
    f = open(filepath,"r")
    string = f.read()
    return string
    
def ConvertDAT(settings,instr,arg):

    files = ChooseFiles(settings["FILE"]["ROOTFOLDER"])
    convfolder = files[0][:files[0].rfind("/")]+"/converted"
    CheckFolder(convfolder)
    
    for filename in files:
        convfile = convfolder+filename[filename.rfind("/"):-5]+".dat"
        data = ReadJson(filename)
        filetype = data["metadata"]["filetype"]
        
        time = data["time"]["data"]
        
        datakey = ["time"]
        writedata = [time]
        writestr = "#"
        
        if filetype == "measurement":
            for chan in data["Channels"]:
                Voltage = data["Channels"][chan]["Voltage"]
                if len(Voltage) != 0:
                    datakey.append(chan)
                    writedata.append(Voltage)
            for key in datakey:
                writestr += key+"\t"
            
        if filetype == "statistics":
            Integral = None
            IntError = None
            for chan in data["Channels"]:
                Voltage = data["Channels"][chan]["avg"]
                if len(Voltage) != 0:
                    datakey.append(chan)
                    writedata.append(Voltage)
                try:
                    Integral = data["Channels"][chan]["Integral"]
                    IntError = data["Channels"][chan]["Intdev"]
                except KeyError:
                    None
            for key in datakey:
                writestr += key+"\t"
            writestr += "\n# Integral: "+str(Integral)+"\n#Integral Error: "+str(IntError)
        
        for i in range(len(time)):
            writestr += "\n"
            for j in range(len(datakey)):
                writestr += str(writedata[j][i])+"\t"
        
        f = open(convfile, "w")
        f.write(writestr)
        f.close()