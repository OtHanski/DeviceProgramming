from FileHandler import ChooseFiles

def ReadData(filename):
    f = open(filename, "r")
    lines = f.readlines()
    # [delay, int, intdev]
    data = []
    
    delayind = filename.find("ms_")
    
    data.append(filename[delayind-4:delayind].strip())
    data.append(lines[1][9:].strip())
    data.append(lines[2][9:].strip())
    
    return data


def main():
    indir = "C:/Users/ottoh/Desktop/Oscilloscope"
    files = ChooseFiles(initdir = indir)
    folder = files[0][:files[0].rfind("/")]
    
    writestr = "#delay\t\tSigInt\t\tIntdev"
    for f in files:
        data = ReadData(f)
        writestr +="\n"+data[0]+"\t"+data[1]+"\t"+data[2]
    
    wr = open(folder+"/intstats.txt", "w")
    wr.write(writestr)
    
main()