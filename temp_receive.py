# SPDX-FileCopyrightText: 2018 Brent Rubell for Adafruit Industries
#
# SPDX-License-Identifier: MIT

#receiver code for raspberry pi for thermocouples on Raspberry pi
#Kevin Cheng, summer 2022

"""
Example for using the RFM69HCW Radio with Raspberry Pi.

Learn Guide: https://learn.adafruit.com/lora-and-lorawan-for-raspberry-pi
Author: Brent Rubell for Adafruit Industries
"""

# Import Python System Libraries
import time
# Import Blinka Libraries
import busio
from digitalio import DigitalInOut, Direction, Pull
import board
# Import the SSD1306 module.
import adafruit_ssd1306
# Import the RFM69 radio module.
import adafruit_rfm69
#import the DS3231 RTC module
#import adafruit_ds3231
import os
from datetime import datetime
import numpy as np
from urllib import request
import math


# Button A
btnA = DigitalInOut(board.D5)
btnA.direction = Direction.INPUT
btnA.pull = Pull.UP

# Button B
btnB = DigitalInOut(board.D6)
btnB.direction = Direction.INPUT
btnB.pull = Pull.UP

# Button C
btnC = DigitalInOut(board.D12)
btnC.direction = Direction.INPUT
btnC.pull = Pull.UP

# Create the I2C interface.
i2c = busio.I2C(board.SCL, board.SDA)

#DS3231 RTC initialization
#ds3231 = adafruit_ds3231.DS3231(i2c)   

# 128x32 OLED Display
reset_pin = DigitalInOut(board.D4)
display = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c, reset=reset_pin)
# Clear the display.
display.fill(0)
display.show()
width = display.width
height = display.height

# Configure Packet Radio
CS = DigitalInOut(board.CE1)
RESET = DigitalInOut(board.D25)
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
rfm69 = adafruit_rfm69.RFM69(spi, CS, RESET, 915.0)
prev_packet = None
# Optionally set an encryption key (16 byte AES key). MUST match both
# on the transmitter and receiver (or be set to None to disable/the default).
rfm69.encryption_key = b'\x01\x02\x03\x04\x05\x06\x07\x08\x01\x02\x03\x04\x05\x06\x07\x08'

#directory = r'\var\www\html\data\anemometer\WMPro1352_'
#directory = r'\home\pi\Documents\TempLogger\tempLog_'
directory = r'tempLog_'
#directory = r'/home/pi/Documents/TempLogger/tempLog_'

day_timestring = datetime.strftime(datetime.now(),'%Y%m%d_%H%M%S')#assign the day_timestring with the time from the raspberry pi
file_today = directory + day_timestring + '.dat'#naming the dat file being written
#line = ser.readline().decode('utf-8')
nowtime = datetime.strftime(datetime.now(),'%Y-%m-%d %H:%M:%S') #acquiring the time


while True:  #infinite loop
    packet = None
    # draw a box to clear the image
    display.fill(0)
    display.text('RasPi Radio', 35, 0, 1)
    
    
    # check for packet rx
    packet = rfm69.receive()
    if packet is None:
        display.show()
        display.text('- Waiting for PKT -', 15, 20, 1)
    
    else:
        display.fill(0)
        #print packet instead
        try:#matches with the UnicodeDecodeError
            packet_text = str(packet,encoding="utf-8",errors="replace")#decoding the byte information received into a string with specific encoding language and error exceptions
            #display.text('RX: ', 0, 0, 1)
            #display.text(packet_text, 25, 0, 1)
            print(packet_text+'\n')
            #display.text('RX: ', 0, 0, 1)
            #display.text(packet_text, 25, 0, 1)#may run into the buffer too small error, needs correction
            info = packet_text.split(",")
            
        except UnicodeDecodeError:  # excepting the UnicodeDecodeError
            continue
        
        else:# if doesn't run into an error
            try:
                dateString = info[1]
            except IndexError:#if runs into an index error
                print("Error ignored.")
                continue
            else:#if no index error
                try:
                    datetime = datetime.strptime(dateString, '%m/%d/%Y-%H:%M:%S')
                except ValueError:#data format may not match with the format above
                    continue
                else:
                    iso_date = datetime.isoformat()#use the timestamp from the transmitter and transfer into isoformat
                    cI = float(info[2])#internal temperature at index 2
                    c0 = float(info[3])#temperature of the first thermocouple 
                    c1 = float(info[4])
                    c2 = float(info[5])
                    check1 = math.isnan(cI)#check if it is not a number that would interfere with the URL
                    check2 = math.isnan(c0)
                    check3 = math.isnan(c1)
                    check4 = math.isnan(c2)
                    if check1 == True or check2 == True or check3 == True or check4 == True:#if either of the four temperatures is not a number, assign it with the value of zero
                        if check1 == True:
                            cI = 0.00
                        elif check2 == True:
                            c0 = 0.00
                        elif check3 == True:
                            c1 =0.00
                        elif check4 == True:
                            c2 = 0.00
                            
                        if (os.path.isfile(file_today)):#if the file exists
                #with open(file_today, 'a') as fileobject:
                            with open(file_today, 'a') as fileobject:#append the file
                                #fileobject.write(nowtime+', ')
                                fileobject.write(packet_text+'\n')
                                fileobject.close()
                    
                        else:
            #with open(file_today, 'w') as fileobject:
                            with open(file_today, 'w') as fileobject:
                                #fileobject.write(nowtime+',')
                                fileobject.write(packet_text+'\n')
                                fileobject.close()
                    else:#if the four temperatures are actual numbers, do the following
                        if (os.path.isfile(file_today)):#if the file exists
                #with open(file_today, 'a') as fileobject:
                            with open(file_today, 'a') as fileobject:#append the file
                                #fileobject.write(nowtime+', ')
                                fileobject.write(packet_text+'\n')
                                fileobject.close()
                    
                        else:
            #with open(file_today, 'w') as fileobject:
                            with open(file_today, 'w') as fileobject:
                                #fileobject.write(nowtime+',')
                                fileobject.write(packet_text+'\n')
                                fileobject.close()
                    
                    #create the url to upload
                    url = "http://tronador.bldg60.wfu.edu/measurements/url_create?instrument_id=7&0m_temp={0}&1m_temp={1}&2m_temp={2}&Int_temp1={3}&email=luthyka@wfu.edu&api_key=Qhfy2GVkJzSMNLDU4K-v&at{4}".format(c0,c1,c2,cI,iso_date)
                    try:
                        request.urlopen(url) #opens url silently
                    except OSError:
                        print("Error opening the URL.")
                    else:
                        display.show()
                        time.sleep(0.1)