"""
This file is for logging data from the weather station to the raspberry pi
"""

#ranges of data
"""
solar radiation: 0-1750
precipitation: 0-400
strike: 0-65,535
strike distance: 0-40
wind speed: 0-30
air temperature: -50-60
vapor pressure: 0-47
air pressure: 1-120
orientation: -90-90
humidity sensor temperature: -40-50


"""
#libraries for the communication
import os
import sys
import serial
from datetime import datetime
import numpy as np
from time import sleep,localtime,strftime
from timeit import default_timer as timer
from urllib import request
import re
from math import e

#initializing the serial port 
ser = serial.Serial(port = '/dev/ttyUSB0', baudrate = 9600, timeout = 5)

#initialize the name of the file being written to 
directory = r'Weather_log'

day_timestring = datetime.strftime(datetime.now(),'%Y%m%d_%H%M%S')

file_today = directory + day_timestring + '.dat'

data_name = "Time\tSolar\tPrecipitation\tStrikes\tStrikeDistance\tNorthWindSpeed\tEastWindSpeed\tGustWindSpeed\tAirTemperature\tVaporPressure\tAtmosphericPressure\txOrientation\tyOrientation\tnullValue\thumiditySensortemperature\t"

#initialize the command outside of the loop
command = "0R4!"
command += '\r'#add a return
command1 = bytes(command,"ascii")#encoding the command into bytes


while True:#infinite loop
    start = timer()
    nowtime = datetime.strftime(datetime.now(),'%Y-%m-%d %H:%M:%S.%f')
    iso_date = datetime.now().replace(microsecond=0).isoformat()
    ser.close()#make sure the serial port is closed
    try: #matches with the serial port error
        ser.open()#open the serial port#encoding the command into bytes
    except serial.serialutil.SerialException:#exception for the serial port error
        ser.close()
        continue
    else:
        ser.write(command1)#write to the serial
        sleep(0.5)
        message1 = ser.readline().decode("ascii")#read from the serial port
        message2 = ser.readline().decode("ascii")
        message3 = str(ser.readline().decode("ascii"))
        print(message2)
        print(iso_date)
        message4 = re.split(r'\t+', message3)   
        print(message4)
        try: #matches with the index error 
            message5 = (str(message4[1])).split("]")#split the string with the bracket
        except IndexError:
            continue
        else:
            message6 = message5[0].split(" ")#contains solar, precipitation,strikes, strikeDistance,NorthWindSpeed,EastWindSpeed,gustWindSpeed,airTemperature,vaporPressure,atmosphericPressure,xOrientation,yOrientation,nullValue,humiditySensorTemperature
            print(message6)
            temperature = float(message6[7])#8th at message6
            airPressure = float(message6[9])#10th at message6
            vaporPressure = float(message6[8])
            eastWind = message6[5]#6th at message6
            northWind = message6[4]#5th at message6
            sat_pressure = 0.61078*(e**(17.27*temperature/(temperature+237.3)))
            RH = vaporPressure/sat_pressure*100
            print(RH)
           
            if (os.path.isfile(file_today)):
    #          with open(file_today, 'a') as fileobject:
                with open(file_today, 'a') as fileobject:
                    fileobject.write(nowtime+'\t')
                    fileobject.write(" ".join(str(x+'\t') for x in message6)+'\t')
                    fileobject.write('\n')
                    fileobject.close()
            else:
                #with open(file_today, 'w') as fileobject:
                with open(file_today, 'w') as fileobject:
                    fileobject.write(data_name+'\n')
                    fileobject.write(nowtime+'\t')
                    fileobject.write(" ".join(str(x+'\t') for x in message6)+'\t')#unclear what happened here ValueError: I/O operation on closed file.
                    fileobject.write('\n')
                    fileobject.close()
        #print(message2+message3)#skip message1, read the rest
        
        #create the link to the CHORDS website
            url = "http://tronador.bldg60.wfu.edu/measurements/url_create?instrument_id=1&A41temp={0}&A41rh={1}&A41pres={2}&A41ews={3}&A41nws={4}&at{5}&email=luthyka@wfu.edu&api_key=Qhfy2GVkJzSMNLDU4K-v".format(temperature,RH,airPressure,eastWind,northWind,iso_date)
            try:
                request.urlopen(url) #opens url silently
            except OSError:
                print("URL was not opened.")
                continue
            else:
                elapsed_time = timer() - start # in seconds
                sleep(60-elapsed_time)