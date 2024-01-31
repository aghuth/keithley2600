# Keithley 2600—series control via Python
The package enables simple control of the Keithley 2600 - series source meters via Python.
It allows setting the device up and performing simple measurements.

The source meter uses an internal TSP language for remote control. This package exposes commands, functions and 
variables that are used to control the source meter in TSP to Python.


## Installation
1. To be able to connect to the device, make sure a VISA driver is installed.
2. Create a Python virtual environment
3. Install package from GitHub with `pip install keithley2600@git+https://github.com/aghuth/keithley2600`
4. Install requirements from requirements.txt

There is another Keithley 2600 package on PyPI, which is a more functional and complicated alternative.

## Usage
The interface to the device is presented as the `Keithley2600` class.  
It is advised to use the interface with an IDE with line completion like PyCharm for quick feature discovery.  
1. Get the device address, connect and initialise interface:  
```connecting to device
import pyvisa
rm = pyvisa.ResourceManager()
devs = rm.list_resources()
dev = rm.open_resource(devs[0])
smu = Keithley2600(dev)
```
2. Write a script to make a measurement:
```preset measurement
smu.setup_for_IV_measurement(iLimit=1e-3, NPLC=3)
smu.output = True
i, v = smu.measure_iv()
smu.outut = False
```
3. For a custom setup, attributes can be set manually:
```custom setup
smu.limit_i = 1 # A
smu.range_v = 20 # V
smu.nplc = 10
if smu.level_v > 20:
    smu.level_v = 20
```




