#!/usr/bin/env python3
import RPi.GPIO as GPIO
import tsys01
import ms5837
from kellerLD import KellerLD
import pickle
import time
import os
import math
import configparser
import sys

BURN = 33

samp_count = 1

NumSamples = 0

ps_test = "pgrep -a python"

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(BURN, GPIO.OUT)
GPIO.output(BURN, 0)

def str2bool(v):
    return v.lower() in ("yes", "true", "t", "1")

def abortMission(configLoc):

    abortConfig = configparser.ConfigParser()
    abortConfig.read(configLoc)
    abortConfig.set('Mission','Abort','1')
    with open(config,'wb') as abortFile:
        abortConfig.write(abortFile)

def kill_sampling(scriptNames):

    for script in scriptNames:
        os.system("sudo pkill -9 -f {}".format(script))

scriptNames = ["TempPres.py", "Minion_image.py","Minion_image_IF.py","OXYBASE_RS232.py","ACC_100Hz.py","Extended_Sampler.py","TempPres_IF.py","OXYBASE_RS232_IF.py","ACC_100Hz_IF.py","Iridium_gps.py","Iridium_data.py"]


if(any(x in os.popen(ps_test).read() for x in scriptNames)) == True:

    kill_sampling(scriptNames)

data_config = configparser.ConfigParser()
data_config.read('/home/pi/Documents/Minion_scripts/Data_config.ini')

configDir = data_config['Data_Dir']['Directory']
configLoc = '{}/Minion_config.ini'.format(configDir)
config = configparser.ConfigParser()
config.read(configLoc)
Abort = str2bool(config['Mission']['Abort'])
iniImg = str2bool(config['Sampling_scripts']['Image'])
iniP30 = str2bool(config['Sampling_scripts']['30Ba-Pres'])
iniP100 = str2bool(config['Sampling_scripts']['100Ba-Pres'])
iniTmp = str2bool(config['Sampling_scripts']['Temperature'])
iniO2  = str2bool(config['Sampling_scripts']['Oxybase'])
iniAcc = str2bool(config['Sampling_scripts']['ACC_100Hz'])

firstp = open("/home/pi/Documents/Minion_scripts/timesamp.pkl","rb")
samp_time = pickle.load(firstp)

for dataNum in os.listdir('{}/minion_data/FIN/'.format(configDir)):
    if dataNum.endswith('_TEMPPRES-FIN.txt'):
        samp_count = samp_count + 1

samp_time = "{}-{}".format(samp_count, samp_time)

Stime = float(config['Final_Samples']['hours'])
Srate = float(config['Final_Samples']['TempPres_sample_rate'])    

file_name = "{}/minion_data/FIN/{}_TEMPPRES-FIN.txt".format(configDir, samp_time)

Sf = 1/Srate

TotalSamples = Stime*60*60*Srate

######################

time.sleep(1)

file = open(file_name,"a+")

if iniP30 == True:

    Psensor = ms5837.MS5837_30BA() # Default I2C bus is 1 (Raspberry Pi 3)

    if not Psensor.init():
        print("Failed to initialize P30 sensor!")
        exit(1)

    # We have to read values from sensor to update pressure and temperature
    if Psensor.read():
        Pres_ini = Psensor.pressure()
    else:
        Pres_ini = "Broken"

    file.write("T+P MS5837_30BA P30 @ %s\r\n" % samp_time)
    file.write("Pressure(mbar),Temp(C) \r\n")

    print("Pressure 30: {} Bar").format(Pres_ini)


if iniP100 == True:

    Psensor = KellerLD()

    if not Psensor.init():
        print("Failed to initialize P100 sensor!")
        exit(1)
    # We have to read values from sensor to update pressure and temperature
    if Psensor.read():
        Pres_ini = Psensor.pressure()
    else:
        Pres_ini = "Broken"

    file.write("T+P KellerLD P100 @ %s\r\n" % samp_time)
    file.write("Pressure(mbar),Temp(C) \r\n")

    print("Pressure 100: {} Bar").format(Pres_ini)

if iniTmp == True:

    sensor_temp = tsys01.TSYS01()

    # We must initialize the sensor before reading it
    if not sensor_temp.init():
        print("Error initializing Temperature sensor")
        exit(1)

    file.write("and TempTSYS01")
    file.write("Pressure(mbar), Temp(C), TempTSYS01(C) \r\n")

file.close()

if __name__ == '__main__':

    if Pres_ini == "Broken":
        GPIO.output(Burn,1)
        abortMission(configLoc)
        os.system('sudo python /home/pi/Documents/Minion_scripts/Iridium_gps.py')

    if Abort == True:
        GPIO.output(Burn,1)

    if Pres_ini >= 1500:
        GPIO.output(BURN,1)

        if iniImg == True:
            os.system('sudo python /home/pi/Documents/Minion_scripts/Minion_image_IF.py &')

        if iniO2 == True:
            os.system('sudo python /home/pi/Documents/Minion_scripts/OXYBASE_RS232_IF.py &')

        if iniAcc == True:
            os.system('sudo python /home/pi/Documents/Minion_scripts/ACC_100Hz_IF.py &')

        # Spew readings
        while(NumSamples <= TotalSamples and Pres_ini >= 1500):

            file = open(file_name,"a")

            if Psensor.read():

                if iniTmp == True:

                    if not sensor_temp.read():
                        print("Error reading sensor")
                        iniTmp = False

                    print("Temperature_accurate: %0.2f C" % sensor_temp.temperature())

                    file.write("{},{},{}\n".format(Psensor.pressure(), Psensor.temperature(), sensor_temp.temperature()))

                else:

                    file.write("{},{}\n".format(Psensor.pressure(), Psensor.temperature()))

            else:
                print('Sensor ded')
                file.write('Sensor fail')
                abortMission(configLoc)
              
            Pres_ini = Psensor.pressure()
            
            print(Pres_ini)

            if Pres_ini >= MAX_Depth:
                file.write("Minion Exceeded Depth Maximum!")
                abortMission(configLoc)

            NumSamples = NumSamples + 1

            time.sleep(Sf)

        file.close()
        os.system('sudo python /home/pi/Documents/Minion_scripts/Iridium_gps.py')
        GPIO.output(data_rec, 0)

    else:

        os.system('sudo python /home/pi/Documents/Minion_scripts/Iridium_gps.py')
