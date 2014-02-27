#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import random
import time
import socket
import os
import csv
import glob
import signal
import wave, struct

MTU=1300
#Camera_data_size = 0
sensor_dir="./sensor_log/"
    
def signal_handler(signal, frame):
    print 'shutting down sensor...'
    # if Camera_data_size > 0:
    #     print Camera_data_size
    sys.exit(0)

def usage():
    print "sensor.py <sensor_type> <server_ip> <server_port> <id>\n\
    valid sensor_type: [temp, device, gps, camera]"
            

def sensor_send(message, ipaddr, port):
    '''
    send data 
    '''
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = (ipaddr, port)
    
    sentbytes=0
    while sentbytes < len(message):
        #we could fragment the data??
        #temp = sock.sendto(message[sentbytes:(sentbytes+MTU)], server_address)
        temp = sock.sendto(message[sentbytes:len(message)], server_address)
        sentbytes += temp
    
    # if (sentbytes>MTU):
    #     print round(time.time(),3), len(message), ip, port
    # if (sentbytes<MTU):
    #     print message, len(message), ip, port
    
    
def main(argv):
    '''
    very simple sensor generator
    '''
    if len(argv) < 4 or argv[0] == "-h" or argv[0]=="--help":
        usage()
        sys.exit(0)

    start_time = time.time()
    sensor_type= argv[0].lower()
    ip=argv[1]
    port=int(argv[2])
    dev_id = sensor_type+"_"+argv[3]
    
    #print " localhost and port:",port
    
    #choose deviceid?
    
    
    #randomly choose a mean temperature
    mean_temp=random.uniform(-30, 50)
    #randomly choose if we initially detect motion or not
    motion=random.choice([0,1])
    vid_stime= start_time
    
    # start with the first co-ordinate on the map
    paths = []
    iRow = 0
    with open('path.txt', 'rb') as gpsfile:
        p = csv.reader(gpsfile, delimiter='\t')
        for row in p:
            r = [float(row[0]), float(row[1]), float(row[2])]
            paths.append(r)
            iRow +=1
    fwdDir = True

    # ambient sound sensor
    # 48 kHz
    # 16 bit
    # Stereo
    waveData = []
    # number of samples per second
    splPerSec = 100 #1/splPerSec = packetization ts
    # initializing variables
    splPerTs = 1
    asdWrapLimit = 1
    
    if (sensor_type =="asd"):
        waveFile = wave.open('ct1.wav', 'rb')
        params = waveFile.getparams()
        # params:  (2, 2, 48000, 2880000, 'NONE', 'not compressed')
        rate = float(params[2])
        frames = waveFile.getnframes()
        # number of frames aggregated in each timestamp
        splPerTs = rate/splPerSec
        asdWrapLimit = int(params[3]/splPerTs)
        for i in range(0,asdWrapLimit):
            # infact they are two frames for each instance
            # data = str(struct.unpack("<hh", waveFile.readframes(1)))
            data = waveFile.readframes(int(splPerTs))
            waveData.append(data)
            # print "data: ",len(data)
            # data is a tuple of left and right channels
            # values for the channel are supposed to be 2s complementary 
            
    try:
        os.makedirs(sensor_dir)
    except OSError:
        print "Directory " + sensor_dir + " already exists"

    logFname = sensor_dir+dev_id+'.log'
    logFile = open(logFname, 'wb')
    logWriter = csv.writer(logFile, delimiter='\t')
    
    j=0
    seq_no=0
    while (True):
        curr_time = round(time.time(),5)
        if (sensor_type =="temp"):
            val= str(round(random.normalvariate(mean_temp, 10),1))+" C"
            timeout= 1.0
            
        elif (sensor_type =="device"):
            val=random.choice(["OFF","ON"])
            timeout= float(random.uniform(0.1,5))
            
        elif (sensor_type =="gps"):
            dist= paths[j][2]
            units= float(1000.0/3600.0)
            speed=random.uniform(30.0*units, 100.0*units)
            t = float(dist/speed)
            val = [paths[j][0], paths[j][1]]
            
            #we limit t to 60s
            if (t>60):
                t=60
            
            if(fwdDir):
                j +=1
                if(j+1==iRow):
                    fwdDir=False
            else:
                j -=1
                if(j==0):
                    fwdDir=True
            
            timeout = t

            
        elif (sensor_type =="camera"):
            #did we detect motion?
            if (motion):
                #yes there was motion
                #sends lots of data, often
                fps=15
                #bit rate is between 50 kbps to 200 kbps
                bitrate= int(random.uniform(50000, 200000))
                #generating random bytes to simulate MPEG2 video payload
                #in MPEG2 all frames are equal sized
                val= os.urandom(bitrate/8/fps)
                timeout=float(1.0/fps)
                #period of motion is random
                motion_time=float(random.uniform(1,5))
                if(time.time()-vid_stime>motion_time):
                    motion=0
            else:
                #no motion, no data, sleep random time
                val="NO_MOTION"
                motion=random.choice([0,1])
                timeout=float(random.uniform(1,10))
                vid_stime=time.time()+timeout

        elif (sensor_type == "asd"): 
            val = waveData[j%asdWrapLimit]
            j +=1
            # print "val: ",curr_time, (val)
            timeout=float(1.0/splPerSec)
            
        else:
            print "argument:",argv[0],"not defined"
            files=glob.glob(logFname)
            for f in files:
                os.unlink(f)
            usage()
            break
            
        #pack the data into a dictionary    
        message={}
        seq_no+=1
        #adding seq_no wrap-around
        if (seq_no > 32000):
            seq_no = 0
        message["dev_id"]=str(dev_id)
        message["ts"]=str(curr_time)
        message["seq_no"]=str(seq_no)
        message["data_size"]=str(len(str(val)))
        message["sensor_data"]=str(val)

        sensor_send(str(message), ip, port)
        #print timeout
        
        if(sensor_type!="camera"):
            #could have stored the dictionary (pickle it)
            logWriter.writerow([curr_time, seq_no, val])
        else:
            # print len(str(message))
            logWriter.writerow([curr_time, seq_no, message["data_size"]])
            if(val!="NO_MOTION"):
                #global Camera_data_size
                #Camera_data_size += val_len
                camFile = open(sensor_dir+dev_id+'.data', 'ab')
                camFile.write(str(val))
                camFile.close
        time.sleep(timeout)
        
if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    main(sys.argv[1:])
