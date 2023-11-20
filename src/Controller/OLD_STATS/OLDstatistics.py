import numpy as np
import integrals as inte
from FileHandler import ChooseFiles
from IntegrationLimits import GetLimits

def ReadData(filename):
    f = open(filename, "r")
    lines = f.readlines()
    data = [[],[]]
    for i in range(2,len(lines)):
        data[1].append(float(lines[i].split()[1]))
        data[0].append(float(lines[i].split()[0]))
    return data

def WriteData(filepath,results):
    f = open(filepath,"w")
    t = results[0]
    V = results[1]
    Vdev = results[2]
    Int = results[3]
    Intdev = results[4]
    
    writestr = "#t [s]\t\tV [V]\t\tVdev [V]\n#SigInt: "+str(Int)+"\n#Intdev: "+str(Intdev)
    for i in range(len(t)):
        writestr += "\n"+str(t[i])+"\t"+str(V[i])+"\t"+str(Vdev[i])
    
    f.write(writestr)

def averaging(files):
    results = [[],[],[],0,0]
    
    # avg
    N = 0
    for fil in files:
        data = ReadData(fil)
        if N == 0:
            results[0] = data[0]
            results[1] = data[1]
        else:
            for i in range(len(data[0])):
                results[1][i] += data[1][i]
        N+=1
    
    for i in range(len(results[1])):
        results[1][i] /= N
    
    # dev
    N = 0
    for fil in files:
        data = ReadData(fil)
        if N == 0:
            results[2] = data[1]
            for i in range(len(data[0])):
                results[2][i] = (results[1][i]-data[1][i])**2
        else:
            for i in range(len(data[0])):
                results[2][i] += (results[1][i]-data[1][i])**2
        N+=1
        
    for i in range(len(results[2])):
        results[2][i] = (results[2][i]/N)**(1/2)
    
    return results

def integrate(results,files, intLimits, offset):
    
    # Find list of indices where time is within our integration limits
    int_indices = [i for i in range(len(results[0])) \
                    if results[0][i] >= intLimits[0] and results[0][i] <= intLimits[1]]
    
    time = results[0][int_indices[0]:int_indices[-1]]
    avgVolt = results[1][int_indices[0]:int_indices[-1]]
    for i in range(len(avgVolt)):
        avgVolt[i] -= offset
    
    # int
    results[3] = np.trapz(avgVolt,time)
    
    # intdev
    N = 0
    for fil in files:
        data = ReadData(fil)
        Volt = data[1][int_indices[0]:int_indices[-1]]
        for i in range(len(Volt)):
            Volt[i] -= offset
            
        gral = np.trapz(Volt,time)
        results[4] += (results[3]-gral)**2
        N += 1
    
    results[4] = (results[4]/N)**(1/2)
    
    
    return results
    
    
def main():
    indir = "C:/Users/ottoh/Desktop/Oscilloscope"
    files = ChooseFiles(initdir = indir)
    filedef = []
    
    for file in files:
        filedefEnd = file.rfind("_")
        if file[-4:] == ".dat" and not file[:filedefEnd] in filedef and not file[:3]=="OUT":
            filedef.append(file[:filedefEnd])
    
    fetchLimits = True
    
    for meas in filedef:
        files_temp = []
        for f in files:
            if f[:len(meas)] == meas:
                files_temp.append(f)
        # [[t],[avgV],[Vdev],int,intdev]
        results = averaging(files_temp)
        if fetchLimits:
            intLimits, offset = GetLimits(np.array([results[0],results[1]]))
            print("Integration limits: "+str(intLimits)+"\noffset: "+str(offset))
        fetchLimits = False
        
        results = integrate(results,files_temp,intLimits,offset)
        
        foldername = files[0][:files[0].rfind("/")]+"/processed/"
        filepath = foldername+files_temp[0][files_temp[0].rfind("/")+1:-4]+"stats.txt"
        
        print("Done with "+meas)
        WriteData(filepath,results)
    

if __name__ == "__main__":
    main()