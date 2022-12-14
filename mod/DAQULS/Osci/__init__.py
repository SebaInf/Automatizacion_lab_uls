import pyvisa as visa
import time
from ROOT import TNtuple,TFile,TObject,TH1D

ip_direction = "TCPIP::10.3.84.21::INSTR"
inst = visa.ResourceManager().open_resource(ip_direction)
print(inst.query('*IDN?').strip())

def osc_w(command):
	inst.write(command)
	time.sleep(0.2)
	
	
def load_waveform(chidx, points_request):
    inst.write(f':WAV:SOUR CHAN{chidx}')
    time.sleep(0.2)
    inst.write(':WAV:MODE RAW')
    time.sleep(0.2)
    inst.write(f':WAV:POIN {points_request}')
    time.sleep(0.2)
    inst.write(':WAV:FORM BYTE')
    time.sleep(0.2)

    preample = inst.query(':WAV:PRE?').split(',')
    points = int(preample[2])
    xinc = float(preample[4])
    xorg = float(preample[5])
    xref = float(preample[6])
    yinc = float(preample[7])
    yorg = float(preample[8])
    yref = float(preample[9])

    #print(f'loading CH{chidx} {points}pts')
    data_bin = inst.query_binary_values('WAV:DATA?', datatype='B', container=bytes)
    t = [(float(i) - xref)*xinc + xorg for i in range(points)]
    v = [(float(byte_data) - yref)*yinc for byte_data in data_bin]
    #print("{0} {1} {2}".format(yinc, yorg, yref) )
    
    return t,v
    
    
def get_data(channel="1" ,numero_tri=1, point_number=100000, fname="datafile.root"):

	chlist=[int(x) for x in channel.split(",")]
	#print(chlist)
	s=len(chlist)
	#print(s)

	#inst.write(':Run')
	#time.sleep(1)
		
	inst.query('*OPC?')
	load_data = {}
	
	fout=TFile(fname,"recreate")
	
	if s==1:
		tupla=TNtuple("oscdata","osciloscope data","evn:t:v0" )
	elif s==2:
		tupla=TNtuple("oscdata","osciloscope data","evn:t:v0:v1" )
	elif s==3:
		tupla=TNtuple("oscdata","osciloscope data","evn:t:v0:v1:v2" )
	else :
		tupla=TNtuple("oscdata","osciloscope data","evn:t:v0:v1:v2:v3" )
		
	
	
	if numero_tri != "NULL":
		temp1=numero_tri
		temp2=1
		i=temp2
	elif run_time != "NULL":
		temp1=run_time
		temp2=time.time()
		i=temp2
	else:
		temp2=1
		temp1=temp2
		i=temp2
	
	
	while temp2<=temp1:
	
		inst.write(':SINGLE')
		time.sleep(0.2)
		for chidx in chlist:
			t, v = load_waveform(chidx,point_number)
			if 'time' not in load_data.keys():
				load_data['time'] = t
			load_data[f'CH{chidx}'] = v
		
			
		#temp3=temp2*10-temp1
		#i=(math.trunc(temp3))/10

		
		
		if s==1:
			for t0, v0 in zip(t,load_data[f'CH{1}']):
				print(v0)
				tupla.Fill(i,t0,v0)
		elif s==2:
			for t0, v0,v1 in zip(t,load_data[f'CH{1}'],load_data[f'CH{2}']):
				tupla.Fill(i,t0,v0,v1)
		elif s==3:
			for t0, v0,v1,v2 in zip(t,load_data[f'CH{1}'],load_data[f'CH{2}'],load_data[f'CH{3}']):
				tupla.Fill(i,t0,v0,v1,v2)
		else :
			for t0, v0,v1,v2,v3 in zip(t,load_data[f'CH{1}'],load_data[f'CH{2}'],load_data[f'CH{3}'],load_data[f'CH{4}']):
				tupla.Fill(i,t0,v0,v1,v2)
		#inst.write(':Run')
		#time.sleep(0.2)
			
		if numero_tri != "NULL":
			temp2=temp2+1
		
		elif run_time != "NULL":
			temp2=time.time()
		else:
			temp2=temp2+1
					
		i+=1
			
	fout.Write("",TObject.kOverwrite)
	fout.Close()



def get_data_csv(channel="1",numero_tri=1, poin_numer=100000):

	inst.write(':Run')
	time.sleep(1)
	
	inst.query('*OPC?')
	load_data = {}
	
	ntrig=1

	for i in range(ntrig):
	
		inst.write(':STOP')
		time.sleep(0.2)
		for chidx in chlist:
			t, v = load_waveform(chidx,poin_num)
			if 'time' not in load_data.keys():
				load_data['time'] = t
			load_data[f'CH{chidx}'] = v
	inst.write(':Run')
	time.sleep(0.2)
		#for t0, v0 in zip(t,v):
			#tupla.Fill(i,t0,v0)
	
	#fout.Write("",TObject.kOverwrite)
	#fout.Close()
	i = 2 #columna que queremos obtener
	columna = [fila[i] for fila in load_data]
	with open("fil_nam", 'w', newline='') as f:
		writer = csv.writer(f, delimiter=',')
		writer.writerow(load_data.keys())
		writer.writerows(zip(*load_data.values()))
		

	
