import re
import PARSER.command_functions as command_functions
from .PROCESSING.FileHandler import ChooseSingleFile, ReadJson, ReadTXT
from math import *
from functools import partial


def EXECCOMMAND(settings, instr, command, argument):
    # If command is "null", skip processing
    if command == "NULL":
        return settings, instr
    
    # Fetch the function from the list of functions
    func = getattr(command_functions,command)
    
    # Handle special functions:
    if func == command_functions.LOAD_SETTINGS:
        print("Loading new settings: "+argument)
        temp_settings = func(settings,instr,argument)
        if not temp_settings == None:
            temp_settings, instr = command_functions.INIT(temp_settings,instr)
    elif command[:3] == "FOR":
        print("For loops are only available for scripts")
    elif command == "SCRIPT":
        RUNSCRIPT(argument)
    elif command == "RTMINIT":
        temp_settings, RTMinstr = func(settings)
        instr["RTM3004"] = RTMinstr
    elif command == "TRUEFORMINIT":
        temp_settings,TRUEFORMinstr = func(settings)
        instr["TRUEFORM"] = TRUEFORMinstr
    
    else:
        # If no special cases detected
        temp_settings = func(settings, instr, argument)
    
    # If the function returns a set of settings, overwrite current ones
    if temp_settings != None:
        settings = temp_settings
    
    return settings, instr

def PARSECOMMAND(settings, instr, user_in,commandlist):
    # Parses a single line command
    
    # Remove extra whitespaces, semicolons, uppercase everything for easier matching
    command = user_in.strip("\n\t ;").upper()
    
    # If it exists, find argument and remove it from command string
    argindex = user_in.find(" ")
    if argindex != -1:
        argument = user_in[argindex+1:]
        command = command[:argindex]
    else:
        argument = ""
    
    if command == "SCRIPT":
        RUNSCRIPT(settings, instr, argument)
        return "NULL", None
    
    # Fetch the function to call from the commandlist dictionary
    keylist = command.split(":")  
    function_call = commandlist
    
    for key in keylist:
        # If "CHAN" command, figure out the channel
        if key[:4] == "CHAN":
            chan = key[4]
            argument = [chan,argument]
            key = "CHAN<n>"
        try:
            function_call = function_call[key]
        except KeyError:
            print("Invalid function request")
            return "NULL", None
    function_call = function_call["function"]
    
    return function_call, argument


def RUNSCRIPT(settings, instr, argument):
    # Argument: filename
    filename = argument

    # Fetch commandlist from file
    commandlist = ReadJson("./PARSER/commands.json")
    
    if filename == "":
        filename = ChooseSingleFile("./Saved_Scripts")
        print("Running script: "+filename[filename.rfind("/")+1:filename.rfind(".")])
        
    if filename == "":
        print("No file selected")
        return None
    
    try: 
        script_string = ReadTXT(filename)
    except FileNotFoundError:
        print("No such script file found")
        return None
    
    # Parse the for loops in the script
    script_string = FORLOOP(script_string)
    
    commands = re.split(r";|\n",script_string)
    for com in commands:
        if len(com) > 0:
            print(com)
            command, argument = PARSECOMMAND(settings, instr, com.strip(), commandlist)
            EXECCOMMAND(settings, instr, command, argument)
            
            
def FORLOOP(script_string):
    # Define regex pattern for parsing for loops
    loop_pattern = re.compile("FOR[0-9]+\{[^\{\}]*\}",re.IGNORECASE)
    number_pattern = re.compile("[0-9]+")
    eval_pattern = re.compile("(?<!<)<[^<>]+>(?!>)")
    replacement_finished = False
    
    # Method for evaluating the value of a loop variable
    def loopvareval(matchobj, loopvariable):
        i = loopvariable
        evalstring = matchobj.group()
        evalstring = evalstring.strip("<>")
        # print(evalstring)
        value = eval(evalstring)
        try:
            value = str(value)
        except:
            print("Error evaluating loop variable")
            value = None
        return value
    
    # Method for stripping the topmost layer off a matched loop variable
    def striplayer(matchobj):
        stripstring = matchobj.group()
        stripstring = stripstring[1:-1]
        return stripstring
    
    while not replacement_finished:
        
        loop = loop_pattern.search(script_string)
        
        # If no matches are found, we're finished with replacing the for-blocks
        if loop == None:
            replacement_finished = True
            break
        else:
            loopstr = loop.group()
        
        # Fetch number of loops
        loopnumber = int(number_pattern.search(loopstr).group())
        
        # Remove the FOR<i>{ and }, init replacement string
        startind = 4+len(str(loopnumber))
        patternstr = loopstr[startind:-1]
        replstr = ""
        
        # Build the command script for opened for loops, substitute the loop numbers
        for i in range(loopnumber):
            # Substitute numbers into current loop iteration
            addstr = re.sub("(?<!<)<[^<>]+>(?!>)", partial(loopvareval, loopvariable = i), patternstr)
            # For loop iterators further down the tree, remove one iteration
            addstr = re.sub(r"<<[^<>]+>>", striplayer, addstr)
            # Add to full command string
            replstr += addstr
        
        #print(loop.expand())
        #print(replstr)
        # replace the parsed loop into the script
        #script_string = re.sub(loopstr,replstr,script_string)
        script_string = script_string.replace(loop.group(), replstr)
        print(script_string)
    
    print(script_string)
    return script_string
        