import time
import traceback
from PARSER.parser import PARSECOMMAND, EXECCOMMAND
from PARSER.PROCESSING import FileHandler as FH
from PARSER.command_functions import SYSEXIT, INIT
from sys import exit


def main_Controller():
    # Main controller routine set inside a loop. 
    
    # Initializing the system settings
    try:
        print("Initializing default settings")
        commandlist = FH.ReadJson("./PARSER/commands.json")
        settings = FH.ReadJson("./SETTINGS/DEFAULT.json")
        settings, instr = INIT(settings)
    except Exception as initexname:
        print("Program ran into the following error during initialization:\n"+traceback.format_exc())
        exit("Exiting program")
    
    # Start controller loop
    print("Controller online, you may enter your commands:")
    while True:
        try:
            # Ask the user for input
            User_in = input(">>>")
            # Parse the input
            command, argument = PARSECOMMAND(settings, instr, User_in,commandlist)
            # Execute parsed command
            if not [command, argument] == [None, None]:
                settings, instr = EXECCOMMAND(settings,instr,command,argument)
        except Exception as exname:
            print("Program ran into the following error:\n"+traceback.format_exc())
            Exception_input = input("To shut down program, enter \"quit\", otherwise press Enter to proceed.")
            if Exception_input.lower() == "quit":
                SYSEXIT(settings,instr,"")
            


if __name__ == "__main__":
    main_Controller()