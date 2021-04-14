import os
import time

ini_dir = os.getcwd()

# Remove old files
print('Removing old files...')
os.system('sudo rm -r /home/pi/Desktop/Minion_config.ini /home/pi/Documents/Minion_scripts/Iridium_gps.py /home/pi/Documents/Minion_scripts/minsat.py /home/pi/Documents/Minion_scripts/Minion_DeploymentHandler.py /home/pi/Documents/Minion_scripts/TempPres.py /home/pi/Documents/Minion_scripts/Recovery_Sampler.py /home/pi/Documents/Minion_scripts/Extended_Sampler.py')

os.system('sudo rm -r /home/pi/Documents/Minion_scripts/TempPres_IF.py')

#os.system('sudo rm -r /home/pi/Documents/Minion_scripts/Minion_2.9_Systemtest.py')

time.sleep(1)
# Add new files
print('Replacing new files...')

os.system('sudo cp updates/Minion_config.ini /home/pi/Desktop/Minion_config.ini')

os.system('sudo cp updates/Recovery_Sampler_Burn.py updates/Iridium_gps.py updates/minsat.py updates/Minion_2.9_Systemtest.py updates/Minion_DeploymentHandler.py updates/Recovery_Sampler.py updates/Extended_Sampler.py updates/TempPres.py /home/pi/Documents/Minion_scripts/')

os.system('sudo mkdir /home/pi/Documents/drivers')
# Clone repos
os.chdir('/home/pi/Documents/drivers/')
os.system('git clone https://github.com/bluerobotics/tsys01-python.git')
os.system('git clone https://github.com/bluerobotics/ms5837-python.git')
os.system('git clone https://github.com/bluerobotics/KellerLD-python.git')
os.system('git clone https://github.com/pimoroni/adxl345-python.git')
os.system('git clone https://github.com/adafruit/Adafruit_Python_ADS1x15.git')
# Install adc driver
os.chdir('Adafruit_Python_ADS1x15/')
os.system('sudo python setup.py install')

os.system('sudo cp /home/pi/Documents/drivers/adxl345-python/adxl345.py /home/pi/Documents/Minion_scripts/')
os.system('sudo cp /home/pi/Documents/drivers/KellerLD-python/kellerLD.py /home/pi/Documents/Minion_scripts/')
os.system('sudo cp /home/pi/Documents/drivers/ms5837-python/ms5837.py /home/pi/Documents/Minion_scripts/')
os.system('sudo cp -r /home/pi/Documents/drivers/tsys01-python/tsys01 /home/pi/Documents/Minion_scripts/')
# Exit
os.chdir(ini_dir)

# Configure the last 3 digits of IP 192.168.0.XXX

IP_addr = input('What local IP extension would you like to use? 192.168.0.')

if len(str(IP_addr)) > 3 or len(str(IP_addr)) < 1 or IP_addr <= 1 or IP_addr >= 255:
    IP_fail = 1
    while IP_fail == 1: 
        IP_addr = input('Illigal IP address: 192.168.0.%s! Please try again: ' % IP_addr)
        if len(str(IP_addr)) > 3 or len(str(IP_addr)) < 1 or IP_addr <= 1 or IP_addr >= 255:
            pass
        else:
            IP_fail = 0
            print("Local IP address = 192.168.0.%s" % IP_addr)
else:
    print("Minion_Hub IP address = 192.168.0.%s" % IP_addr)

# Add IP address to config file
with open('/home/pi/Desktop/Minion_config.ini', 'r') as file :
    Minion_conf = file.read()

# Replace the directory
Minion_conf = Minion_conf.replace('XXX', '{}'.format(IP_addr))

# Write the file out again
with open('/home/pi/Desktop/Minion_config.ini', 'w') as file:
    file.write(Minion_conf)