import pyvisa as visa

rm = visa.ResourceManager()
ls = rm.list_resources()

def testID(ID, save = False):
    try:
        instr = rm.open_resource(ID)
        instr.query("*IDN?")
        ans = instr.query("\x05")
        print(ans)
        if not save:
            instr.close()
            return None
        else:
            return instr
    except Exception as ex:
        print(repr(ex))
        instr.close()
        return None
    
