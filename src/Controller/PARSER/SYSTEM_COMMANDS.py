import sys
import time
from .PROCESSING.FileHandler import ReadJson, WriteJson, ChooseSingleFile

def WAIT(settings, instr, argument):
    # Argument: waittime
    try:
        waittime = float(argument)
    except ValueError:
        print("Invalid command argument")
        return settings
    
    print("Waiting "+argument+" seconds")
    time.sleep(waittime)
    
    return settings

def SETCOMMENT(settings,instr,argument):
    # Argument: comment string
    settings["COMMENT"] = argument
    
    return settings

def SYSEXIT(settings, instr, argument):
    # Argument: None
    if settings["RTM"]["STAT"] == "ON":
        try:
            instr["RTM3004"].close()
        except:
            print("Failure while closing RTM3004 VISA session")
    if settings["TRUEFORM"]["STAT"] == "ON":
        try:
            instr["TRUEFORM"].close()
        except:
            print("Failure while closing TRUEFORM VISA session")
    
    if settings["ERROR"] != "":
        print("System has encountered an error:\n"+settings["ERROR"])
        sys.exit("Quitting program")
    else:
        sys.exit("System has exited succesfully")


def SAVE_SETTINGS(settings,instr,argument):
    # Argument: settings name
    # Note, doesn't save comment value
    folder = "./SETTINGS/"
    filename = argument.upper()
    
    if filename == "DEFAULT":
        print("Not allowed to overwrite default settings from within program.\
               \nPlease make a backup and rewrite the default manually instead.")
        return settings
    else:
        # Erase comment line before writing
        writeset = settings
        writeset["COMMENT"] = ""
        WriteJson(folder+filename+".json",writeset)
        return settings

def LOAD_SETTINGS(settings,instr,argument):
    # Argument: settings name
    # Reinit done in parser.py exception
    folder = "./SETTINGS/"
    if argument != "":
        filename = folder+argument.upper()+".json"
    else:
        filename = ChooseSingleFile(initdir = folder)
    
    try:
        readsettings = ReadJson(filename)
        settings = readsettings
    except FileNotFoundError:
        print("No such settings file found.")
        return None
    
    return settings

def SHOW_SETTINGS(settings,instr,argument):
    # Argument: None
    printstring = ""
    
    def formatSETTINGS(printtree,tree,depth):
        if not isinstance(tree,dict):
            None
        else:
            for key in tree:
                if isinstance(tree[key],dict):
                    printtree += "\n    "+"│   "*depth+"├ "+ str(key)
                    printtree = formatSETTINGS(printtree,tree[key],depth+1)
                else:
                    printtree += "\n    "+"│   "*(depth)+"├ "+ str(key)
                    printtree += ": "+str(tree[key])
        return printtree
    
    printstring = formatSETTINGS(printstring,settings,0)+"\n"
    print(printstring)
    
    return settings
    
def SETMEASFILENAME(settings,instr,argument):
    filepath = argument
    
    measfolder = filepath[:filepath.rfind("/")]
    if filepath.rfind(".") != -1:
        filename = filepath[filepath.rfind("/")+1:filepath.rfind(".")]
    else:
        filename =  filepath[filepath.rfind("/")+1:]
    
    settings["FILE"]["FILENAME"] = filename
    settings["FILE"]["MEASFOLDER"] = measfolder
    
    return settings

def SETMEASUREMENT(settings,instr,argument):
    measurement = argument
    
    settings["FILE"]["MEASUREMENT"] = measurement
    return settings
    
def HELP(settings, instr, argument):
    # argument should be command in its full form: COM1:COM2:COM3
    command = argument.strip()
    
    # Fetch commandlist from file
    commandlist = ReadJson("./PARSER/commands.json")
    
    function = commandlist
    
    if command != "":
        # Use a similar method as with command parser to figure out the command in question
        keylist = command.split(":")
        
        for key in keylist:
            # Handle CHAN commands
            if key[:4] == "CHAN":
                key = "CHAN<n>"
            try:
                function = function[key]
            except KeyError:
                print("Invalid command name")
                return settings
        
        description = function["description"]
        args = function["arguments"]
        printdescription = "\n" + command+": "+ description + "\nArguments: " + args + "\n"
        print(printdescription)
    
    tree = function
    printtree = ""
    if not command == "":
        printtree += command + ":\n"
    else:
        printtree += "Full command tree:\n"
    
    # For fetching the 
    def formatHELP(printtree,tree,depth):
        if not isinstance(tree,dict):
            None
        else:
            for key in tree:
                if isinstance(tree[key],dict):
                    printtree += "    "+"│   "*depth+"├ "+ str(key)+"\n"
                    printtree = formatHELP(printtree,tree[key],depth+1)
        return printtree
    
    comparison = printtree
    printtree = formatHELP(printtree,function,0)
    if not comparison == printtree:
        print(printtree)
    
    return settings
    
    
    
    
    
    
    