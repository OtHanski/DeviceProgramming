import usbtmc #change to pyvisa
import time
import sys
import struct
import numpy
import _thread
import ROOT #get rid of
import usb
import usb.core
import urllib
import urllib.request

oldWaveform = ""
header = ""
scope_id = "USB::0x0aad::0x01d6::INSTR"


def restartScope():
	print("WARNING: Scope not responding properly, trying to restart", end='', flush=True)
	try:
		urllib.request.urlopen('http://10.42.43.231/api/relay/0?apikey=69DCEEFA18B4AF96')
	except:
		print('')
		print("ERROR: Could not reach smart plug. Stopping execution!")
		quit()
	else:
		urllib.request.urlopen('http://10.42.43.231/api/relay/0?apikey=69DCEEFA18B4AF96&value=0')
		for rep in range(5):
			time.sleep(0.5)
			print('.', end='', flush=True)
		urllib.request.urlopen('http://10.42.43.231/api/relay/0?apikey=69DCEEFA18B4AF96&value=1')
		for rep in range(55):
			time.sleep(0.5)
			print('.', end='', flush=True)
	print('')

def init(instr):
    ### Seems to work for the most part. Reuse this ###
    
	global header
	instr.write("*RST")

	if instr.ask("*IDN?") != 'Rohde&Schwarz,RTM3004,1335.8794k04/103028,01.550':
		instr.close()
		restartScope()
	print("Scope found. Initializing",end='', flush=True)

	instr.write("CHAN1:STAT ON")
	instr.write("CHAN1:COUP DC")
	instr.write("CHAN1:SCAL 20E-3")
	instr.write("CHAN1:OFFS -20E-3")
	instr.write("CHAN2:STAT ON")
	instr.write("CHAN2:COUP DC")
	instr.write("CHAN2:SCAL 200E-3")
	instr.write("CHAN2:OFFS -800E-3")
	instr.write("CHAN3:STAT ON")
	instr.write("CHAN3:COUP DC")
	instr.write("CHAN3:SCAL 0.5")
	instr.write("CHAN3:OFFS 1.5")
	instr.write("CHAN4:STAT ON")
	#instr.write("CHAN4:COUP DC") # 1MOhm for AxPET trigerring reflection (triggers on negative V)
	instr.write("CHAN4:SCAL 0.5")
	instr.write("CHAN4:OFFS 1.5")
	instr.write("TIM:SCAL 500E-9")
	instr.write("TIM:POS 1.5E-6")
	instr.write("ACQ:POIN 20000")
	instr.write("ACQ:INT SMHD")
	instr.write("TRIG:A:MODE NORM")
	instr.write("TRIG:A:SOUR EXT")
	instr.write("TRIG:A:LEV5 2.4")
	instr.write("TRIG:A:EDGE:SLOP POS")
	instr.write("FORM REAL")
	instr.write("FORM:BORD LSBF")

	for rep in range(12):
		time.sleep(0.5)
		print('.', end='', flush=True)
	print('', end='\n', flush=True)
	header=instr.ask("CHAN:DATA:HEAD?")
	getWaveforms(instr)
	return instr

def getNSamples(scope):
	sep1 = header.find(",");
	sep2 = header.find(",",sep1+1);
	sep3 = header.find(",",sep2+1);
	return int(header[sep2+1:sep3])

def decodeWaveforms(data):
	sep1 = header.find(",");
	sep2 = header.find(",",sep1+1);
	sep3 = header.find(",",sep2+1);
	t0 = numpy.float32(header[0:sep1])
	t1 = numpy.float32(header[sep1+1:sep2])
	n = int(header[sep2+1:sep3])
	dt=(t1-t0)/(n-1)
	decWaves = numpy.zeros((1+len(data),n),'f')
	decWaves[0] = [round((t0+i*dt)*1e10)/1e10 for i in range(n)]
	for ch in range(len(data)):
		# First character should be "#".
		pound = data[ch][0:1]
		if pound != b'#':
			print("ERROR: Unknown data format returned from scope!")
			quit()
		# Second character is number of following digits for length value.
		length_digits = int(data[ch][1:2])
		data_length = int(data[ch][2:length_digits+2])
		# from the given data length, and known header length, we get indices:
		data_begin = length_digits + 2  # 2 for the '#' and digit count
		data_end = data_begin + data_length
		data_entries = data_length // 4;
		if data_entries != n:
			print("ERROR: Data length not consistent with number of samples!")
			quit()
		decWaves[ch+1] = numpy.float32(struct.unpack('f'*data_entries,data[ch][data_begin:data_end]))
	return decWaves

def getWaveforms(instr):
	global oldWaveform
	while True:
		instr.write("CHAN1:DATA?")
		ch1 = instr.read_raw()
		instr.write("CHAN2:DATA?")
		ch2 = instr.read_raw()
		instr.write("CHAN3:DATA?")
		ch3 = instr.read_raw()
		instr.write("CHAN4:DATA?")
		ch4 = instr.read_raw()
		instr.write("CHAN1:DATA?")
		ch1_check = instr.read_raw()
		if (ch1 != oldWaveform) and (ch1 == ch1_check):
			oldWaveform = ch1
			return [ch1,ch2,ch3,ch4]

if len(sys.argv) < 2:
	print("ERROR: Need to give number of events as command line options!")
	quit()

nEvents = int(float(sys.argv[1]))

try:
	scope = init(usbtmc.Instrument(scope_id))
	nSamples = getNSamples(scope)
except usb.core.USBError:
	exc = sys.exc_info()[1]
	if exc.errno == 110:
		scope.close()
		print("stuff")
		restartScope()

		try:
			scope = init(usbtmc.Instrument(scope_id))
			nSamples = getNSamples(scope)
		except:
			raise ValueError("ERROR: Reset not successful, check scope and connection!")
	else:
		print("ERROR: Unknown USB Error. Stopping execution!")
		raise
except ValueError as err:
	if err.args == ('WrongIdent'):
		restartScope()
		try:
			scope = init(usbtmc.Instrument(scope_id))
			nSamples = getNSamples(scope)
		except:
			raise ValueError("ERROR: Reset not successful, check scope and connection!")
	else:
		print("ERROR: Unknown Error. Stopping execution!")
		raise
except:
	raise

f = ROOT.TFile("/home/positron/DAQ/scripts/scope.temp.root", "RECREATE","RTM3004 DAQ file",201)

graphList = [ [ROOT.TGraph(nSamples) for ch in range(4)] for n in range(nEvents) ]

placeholderString=""
for i in range(24008):
	placeholderString+=str('0')
saveStrings = [placeholderString for ch in range(4)]

startTime = time.time()

lock = False

def saveToFile(tempStrings,eventNum,sampleNum):
	currentEvent = tempStrings
	global lock
	global graphList
	global f
	decodedWaveforms = decodeWaveforms(currentEvent);
	timeAxis = decodedWaveforms[0];
	l = ROOT.TList()
	graphList[eventNum][0].SetName("waveform_ch1")
	graphList[eventNum][0].SetTitle("Waveform - Channel 1;time (rel. to trigger) [s];voltage [V]")
	graphList[eventNum][1].SetName("waveform_ch2")
	graphList[eventNum][1].SetTitle("Waveform - Channel 2;time (rel. to trigger) [s];voltage [V]")
	graphList[eventNum][2].SetName("waveform_ch3")
	graphList[eventNum][2].SetTitle("Waveform - Channel 3;time (rel. to trigger) [s];voltage [V]")
	graphList[eventNum][3].SetName("waveform_ch4")
	graphList[eventNum][3].SetTitle("Waveform - Channel 4;time (rel. to trigger) [s];voltage [V]")
	for samp in range(sampleNum):
		graphList[eventNum][0].SetPoint(samp, timeAxis[samp], decodedWaveforms[1][samp])
		graphList[eventNum][1].SetPoint(samp, timeAxis[samp], decodedWaveforms[2][samp])
		graphList[eventNum][2].SetPoint(samp, timeAxis[samp], decodedWaveforms[3][samp])
		graphList[eventNum][3].SetPoint(samp, timeAxis[samp], decodedWaveforms[4][samp])
	l.Add(graphList[eventNum][0])
	l.Add(graphList[eventNum][1])
	l.Add(graphList[eventNum][2])
	l.Add(graphList[eventNum][3])
	f.WriteObject(l,"Event #"+str(eventNum+1))
	lock = False
	return

for i in range(0,nEvents):
	print("Acquiring event #",str(i+1),"of",str(nEvents), end="\r", flush=True)
	try:
		saveStrings = getWaveforms(scope)
	except usb.core.USBError:
		exc = sys.exc_info()[1]
		if exc.errno == 110:
			print('')
			restartScope()
			try:
				scope = init(usbtmc.Instrument(scope_id))
				saveStrings = getWaveforms(scope)
			except:
				raise ValueError("ERROR: Reset not successful, check scope and connection!")
		else:
			print("ERROR: Unknown USB Error. Stopping execution!")
			raise
	while lock:
		time.sleep(0.0001)
	lock = True
	_thread.start_new_thread(saveToFile, (saveStrings,i,nSamples))

while lock:
	time.sleep(0.0001)

f.Close()

print("Acquisition of",str(nEvents),"events completed. Elapsed time:",round(time.time()-startTime),"seconds.")
sys.exit(0)

