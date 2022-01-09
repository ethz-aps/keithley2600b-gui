## GUI for TDDB-Measurements with Keithley
This software is able to perfom IV-Measurements, Stressing with a constant current, TDDB Measurements with a constant voltage. Plotting the Output- and Transfer-Characterisitc is also possible. It is based on a python keihley driver (https://github.com/OE-FET/keithley2600)
The data is saved in a csv file. 

![1](https://user-images.githubusercontent.com/93489014/142616469-c5fddf25-d426-4ac1-bd5b-2808b3f80898.png)

### Hardware:
- Keithley’s Series 2600B System SMU instrument 

### Software Requirements:
- Python3 (ConfigObj,PyQt5, numpy)

### Use:
After adapting the IP Adress of the Keithley device in the config.ini file the software can be started with:

python gui.py
