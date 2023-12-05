#this file is for the reading and recording of the Purple Air sensor
#Kevin Cheng summer 2022
import serial
import time
from time import sleep
from timeit import default_timer as timer
from datetime import datetime,tzinfo
import zoneinfo
from dateutil import tz
from urllib import request
import pytz
import os



#initialize the file the data is being written to
directory = r'AirQuality_log'

day_timestring = datetime.strftime(datetime.now(),'%Y%m%d_%H%M%S')

file_today = directory + day_timestring + '.dat'

data_name = "PM1.0\tPM2.5\tPM10\tAQI"


#initialize the serial port for the sensor
ser = serial.Serial(port = '/dev/ttyUSB2', baudrate = 115200, timeout = 0.5)
    

while True:
    start = timer()#calculate the execution time 
    nowtime = datetime.strftime(datetime.now(),'%Y-%m-%d %H:%M:%S.%f')
    #byteData = read_all(ser)
    byteData = ser.read(400)#read from the serial port
    data = str(byteData,encoding = "utf-8",errors = "ignore")#decode the message
    substring = ","
    if substring in data:#determine if message is useful or not, useful ones contain commas
        data1 = data.split('\n')#split the data string with new lines
        try:
            data2 = data1[1].split(",")#try to split
        except IndexError:#if data1 doesn't have multiple indeces
            continue
        else:#if no index error
            try:
                dateString = data2[0]#use the timestamp from Purple Air
                dateString1 = dateString[0:19]#the exact timestamp excluding the last letter "z"
                date_format = "%Y/%m/%dT%H:%M:%S"#the format of the timestamp
                
                #create datetime object in local timezone
                try:
                    dt_utc = datetime.strptime(dateString1,date_format)#get the timestamp into a datetime object
                except ValueError:#a possible error
                    continue
                else:
                    #dt_utc = dt_utc.replace(tzinfo=pytz.UTC)
                #get local timezone
                    local_zone = tz.tzlocal()#get the local time zone
                #convert timezone of datetime from UTC to local
                    #dt_local = dt_utc.astimezone(local_zone)
                    dt_utc = dt_utc.isoformat()#isoformat the timestamp 
                    #local_time = dt_local.isoformat()
                    PM_1 = data2[4]#assign the values
                    PM_2 = data2[5]#PM2.5 here
                    PM_10 = data2[6]
                    AQI = data2[7]
                    #may skip one message every 20 minutes, may be due to the routine display of the configuration of the Purple Air sensor
            except IndexError:#if dataString doesn't have multiple indeces
                continue
            else:
                print(dt_utc,PM_1,PM_2,PM_10,AQI)
                
                if (os.path.isfile(file_today)):#if the file exists
    #          with open(file_today, 'a') as fileobject:
                    with open(file_today, 'a') as fileobject:
                        fileobject.write(nowtime+'\t')#write the time
                        fileobject.write(PM_1+"\t"+PM_2+"\t"+PM_10+"\t"+AQI)#write the data with a tab
                        fileobject.write('\n')#new line
                        fileobject.close()
                else:
                #with open(file_today, 'w') as fileobject:
                    with open(file_today, 'w') as fileobject:
                        fileobject.write(data_name+'\n')
                        fileobject.write(nowtime+'\t')
                        fileobject.write(PM_1+"\t"+PM_2+"\t"+PM_10+"\t"+AQI)#unclear what happened here ValueError: I/O operation on closed file.
                        fileobject.write('\n')
                        fileobject.close()
                        
                #open the url and assign the data with the formatting function
                url = "http://tronador.bldg60.wfu.edu/measurements/url_create?instrument_id=11&PM_1.0={0}&PM_2.5={1}&PM_10={2}&AQI={3}&at={4}&email=luthyka@wfu.edu&api_key=Qhfy2GVkJzSMNLDU4K-v".format(PM_1,PM_2,PM_10,AQI,dt_utc)
                try:#try to open the url to upload the data
                    request.urlopen(url)
                except OSError:#if cannot be opened properly
                    print("URL was not opened.")
                    continue
                else:#if no OSError
                    elapsed_time = timer() - start # in seconds
                    sleep(120-elapsed_time)
    else:
        continue