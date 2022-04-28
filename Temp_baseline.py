from keithley2600.keithley_driver import Keithley2600 as Kdr
import data

def svbd_baseline():
    #voltages, currents = (range(-2000,2010,10),range(-200,201))
    voltages,currents = Kdr.voltage_sweep_single_smu(smua, range(-200, 201), 1, 0.5, False,)
    with open("SteadyV_BD_Baseline.txt","w") as txt_file:
        for i in currents:
            txt_file.write(str(i)+"\n")

"""
Idea: Create a button in steadyv_bd which does baseline measurement saving to file as different lines starting
with -200V to 200V in 1V steps

"""