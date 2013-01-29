# -*- coding: utf-8 -*-
import sys
import random
import time
import socket
import os
import csv
import signal

MTU=1300
    
def sensor_send(message, args):
def signal_handler(signal, frame):
    print 'shutting down sensor...'
    sys.exit(0)
def usage():
    print "sensor.py <sensor_type> <ip> <port>\n\
    valid sensor_type: [temp, device, gps, camera]"
            

    '''
    send data 
    '''
    ip=args[1]
    port=int(args[2])
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = (ip, port)
    
    sentbytes=0
    while sentbytes < len(message):
        temp = sock.sendto(message[sentbytes:(sentbytes+MTU)], server_address)
        sentbytes += temp
    
    if (sentbytes>MTU):
        print round(time.time(),3), len(message), ip, port
    if (sentbytes<MTU):
        print message, len(message), ip, port
    
    
def main(argv):
    '''
    very simple sensor generator
    '''
    start_time = time.time()
    if argv[0] == "-h" or argv[0]=="--help":
        usage()
        sys.exit(0)
    
    #choose deviceid?
    dev_id=argv[0]+"-"+str(random.randint(10000,99999))
    
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

    j=0
    maxt=mint=1.0
    while (True):
        if (argv[0]=="temp"):
            val= round(random.normalvariate(mean_temp, 10),1)
            timeout= 1.0
            
        elif (argv[0]=="device"):
            val=random.choice(["OFF","ON"])
            timeout= float(random.uniform(0.1,5))
            
        elif (argv[0]=="gps"):
            dist= paths[j][2]
            units= 1#float(1000.0/3600.0)
            speed=random.uniform(30.0*units, 100.0*units)
            t = float(dist/speed)
            val = [paths[j][0], paths[j][1]]
            
            if (t>5):
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

            
        elif (argv[0]=="camera"):
            #did we detect motion?
            if (motion):
                #yes there was motion
                #sends lots of data, often
                fps=15
                #bit rate is between 100 kbps to 1 Mbps
                bitrate= int(random.uniform(100000, 1000000))
                #generating random bytes to simulate MPEG2 video payload
                #in MPEG2 all frames are equal sized
                val= os.urandom(bitrate/8/fps)
                timeout=float(1/fps)
                #period of motion is random
                motion_time=float(random.uniform(1,5))
                if(time.time()-vid_stime>motion_time):
                    motion=0
            else:
                #no motion, no data, sleep random time
                val=0
                motion=random.choice([0,1])
                timeout=float(random.uniform(1,10))
                vid_stime=time.time()+timeout
        else:
            print argv[0],"not defined"
            usage()
            break
            
        #pack the data into a dictionary    
        message={}
        message["ts"]=round(time.time(),3)
        message["dev_id"]=(dev_id)
        message["data"]=(val)
        sensor_send(str(message), argv)
        time.sleep(timeout)
        
if __name__ == "__main__":
  main(sys.argv[1:])    signal.signal(signal.SIGINT, signal_handler)
    main(sys.argv[1:])