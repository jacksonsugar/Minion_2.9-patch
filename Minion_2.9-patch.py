import os
import time

ini_dir = os.getcwd()

# Remove old files
print('Removing old files...')
os.system('sudo rm -r /home/pi/Desktop/Minion_config.ini /home/pi/Documents/Minion_scripts/Minion_DeploymentHandler.py /home/pi/Documents/Minion_scripts/TempPres.py /home/pi/Documents/Minion_scripts/Recovery_Sampler.py /home/pi/Documents/Minion_scripts/Extended_Sampler.py')

os.system('sudo rm -r /home/pi/Documents/Minion_scripts/TempPres_IF.py')

time.sleep(1)
# Add new files
print('Replacing new files...')

os.system('sudo cp updates/Minion_config.ini /home/pi/Desktop/Minion_config.ini')

os.system('sudo cp updates/Minion_2.9_Systemtest.py updates/Minion_DeploymentHandler.py updates/Recovery_Sampler.py updates/Extended_Sampler.py updates/TempPres.py /home/pi/Documents/Minion_scripts/')

os.system('sudo mkdir /home/pi/Documents/drivers')
# Clone repos
os.chdir('/home/pi/Documents/drivers/')
os.system('git clone https://github.com/bluerobotics/tsys01-python.git')
os.system('git clone https://github.com/bluerobotics/ms5837-python.git')
os.system('git clone https://github.com/bluerobotics/KellerLD-python.git')
os.system('git clone https://github.com/adafruit/Adafruit_Python_ADXL345.git')
os.system('git clone https://github.com/adafruit/Adafruit_Python_ADS1x15.git')
# Install acc driver
os.chdir('Adafruit_Python_ADXL345/')
os.system('sudo python setup.py install')
os.chdir('..')
# Install adc driver
os.chdir('Adafruit_Python_ADS1x15/')
os.system('sudo python setup.py install')

os.system('sudo cp /home/pi/Documents/drivers/KellerLD-python/kellerLD.py /home/pi/Documents/Minion_scripts/')
os.system('sudo cp /home/pi/Documents/drivers/ms5837-python/ms5837.py /home/pi/Documents/Minion_scripts/')
os.system('sudo cp -r /home/pi/Documents/drivers/tsys01-python/tsys01 /home/pi/Documents/Minion_scripts/')
# Exit
os.chdir(ini_dir)