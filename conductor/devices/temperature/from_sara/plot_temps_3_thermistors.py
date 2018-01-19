import numpy as np
import matplotlib as mpl
from matplotlib import pyplot as plt
import json
from datetime import datetime


A= 3.9083e-3
B = -5.775e-7
R0 = 1000.


def T(R):
	return (-A + (A**2 - 4*B*(1-R/R0))**0.5)/(2*B)

print T(1095)

print T(1100)


with open("grounding_comparison_4.txt") as json_file:
	data = json.load(json_file)

time_format = '%a %b %d %H:%M:%S %Y'
dates = data['date']
time = [datetime.strptime(i, time_format) for i in dates]
time1 = time[::3]
time2 = time[1::3]
time3 = time[2::3]

temp = np.asarray(data['reading'])
temp = T(temp)
temp1 = temp[::3]
temp2 = temp[1::3]
temp3 = temp[2::3]

ch = data['channel']
ch1 = ch[::3]
ch2 = ch[1::3]
ch3 = ch[2::3]

f, (ax1, ax2, ax3) = plt.subplots(3, sharex=True)
f.subplots_adjust(hspace=0.5)
ax1.plot_date(time1, temp1,'-')
ax2.plot_date(time2, temp2,'-')
ax3.plot_date(time3, temp3,'-')
ax1.set_title('Connect shield at thermistor')
ax2.set_title('Connect shield at Keithley')
ax3.set_title('Crappy shielding around thermistor')
ax1.set_ylabel('Temp (C)')
ax2.set_ylabel('Temp (C)')
ax2.set_xlabel('Time')



plt.figure()
endpt = 700
plt.plot(time1[:endpt], temp1[:endpt]-np.mean(temp1[:endpt]),'-r',label='Connect shield at thermistor')
plt.plot(time2[:endpt],temp2[:endpt]-np.mean(temp2[:endpt]),'-b',label='Connect shield at Keithley')
plt.plot(time3[:endpt],temp3[:endpt]-np.mean(temp3[:endpt]),'-k',label='Thermistor not shielded')
plt.legend()
plt.xlabel('Time')
plt.ylabel('Temp - mean(Temp) (C)')
plt.title('On top of amplifier box, in the same insulated box')




plt.show()
