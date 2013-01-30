# -*- coding: utf-8 -*-
import sys
import random
import time
import socket
import os
import csv
import glob
import signal

MTU=1300
#Camera_data_size = 0

    
def signal_handler(signal, frame):
    print 'shutting down sensor...'
    # if Camera_data_size > 0:
    #     print Camera_data_size
    sys.exit(0)

def usage():
    print "sensor.py <sensor_type> <server_ip> <server_port>\n\
    valid sensor_type: [temp, device, gps, camera]"
            

def sensor_send(message, ipaddr, port):
    '''
    send data 
    '''
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = (ipaddr, port)
    
    sentbytes=0
    while sentbytes < len(message):
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
    start_time = time.time()
    sensor_type= argv[0].lower()
    ip="localhost" 
    port=5000
    
    if argv[0] == "-h" or argv[0]=="--help":
        usage()
        sys.exit(0)
    if(len(argv)==3):
        ip=argv[1]
        port=int(argv[2])
    else:
        print "using defaults=> localhost and port:",port
    

    #choose deviceid?
    dev_id=sensor_type+"-"+str(random.randint(10000,99999))
    
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

    logFname = dev_id+'.log'
    logFile = open(logFname, 'wb')
    logWriter = csv.writer(logFile, delimiter='\t')
    
    j=0
    while (True):
        curr_time = round(time.time(),3)
        if (sensor_type =="temp"):
            val= round(random.normalvariate(mean_temp, 10),1)
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
            
            if (t>60):
                t=5
            
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

        else:
            print "argument:",argv[0],"not defined"
            files=glob.glob(logFname)
            for f in files:
                os.unlink(f)
            usage()
            break
            
        #pack the data into a dictionary    
        message={}
        message["ts"]=curr_time
        message["dev_id"]=(dev_id)
        message["data"]=(val)

        sensor_send(str(message), ip, port)
        #print timeout
        
        if(sensor_type!="camera"):
            #could have stored the dictionary (pickle it)
            logWriter.writerow([curr_time, val])
        else:
            val_len = len(str(val))
            logWriter.writerow([curr_time, val_len])
            if(val!="NO_MOTION"):
                #global Camera_data_size
                #Camera_data_size += val_len
                camFile = open(dev_id+'.data', 'ab')
                camFile.write(str(val))
        time.sleep(timeout)
        
if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    main(sys.argv[1:])