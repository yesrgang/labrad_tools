import numpy as np
import matplotlib as mpl
from matplotlib import pyplot as plt
import json
from datetime import datetime
import matplotlib.dates as mdates

T, R = np.loadtxt('PR503J2_R_T_Table.csv', delimiter=',', unpack=True, dtype=float)
start = 1400
stop = 1800
T = T[start:stop]
R = R[start:stop]
a5,a4,a3,a2,a1,a0 = np.polyfit(R,T,5)


def T(R):
	return a5*R**5 + a4*R**4 + a3*R**3 + a2*R**2 + a1*R + a0




with open("/home/brad/yesrdata/SrQ/table temp servo/monitor_8_places_air_temps.txt") as json_file:
	data = json.load(json_file)

time_format = '%m/%d/%y %H:%M:%S'
dates = data['date']
time = [datetime.strptime(i, time_format) for i in dates]
time1 = time[::8]
time2 = time[1::8]
time3 = time[2::8]
time4 = time[3::8]
time5 = time[4::8]
time6 = time[5::8]
time7 = time[6::8]
time8 = time[7::8]

last = min([len(time1),len(time2),len(time3),len(time4),len(time5),len(time6),len(time7),len(time8)])

time1 = time1[:last]
time2 = time2[:last]
time3 = time3[:last]
time4 = time4[:last]
time5 = time5[:last]
time6 = time6[:last]
time7 = time7[:last]
time8 = time8[:last]



temp = np.asarray(data['reading'])
temp = T(temp)
temp1 = temp[::8]
temp2 = temp[1::8]
temp3 = temp[2::8]
temp4 = temp[3::8]
temp5 = temp[4::8]
temp6 = temp[5::8]
temp7 = temp[6::8]
temp8 = temp[7::8]

temp1 = temp1[:last]
temp2 = temp2[:last]
temp3 = temp3[:last]
temp4 = temp4[:last]
temp5 = temp5[:last]
temp6 = temp6[:last]
temp7 = temp7[:last]
temp8 = temp8[:last]


avg_temp = (temp1 + temp2 + temp3 + temp4 + temp5 + temp6)/6.



ch = data['channel']
ch1 = ch[::8]
ch2 = ch[1::8]
ch3 = ch[2::8]
ch4 = ch[3::8]
ch5 = ch[4::8]
ch6 = ch[5::8]
ch7 = ch[6::8]
ch8 = ch[7::8]

'''
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
'''


plt.figure()
plt.plot_date(time1,temp1,'-',label='H1 launch')
plt.plot_date(time2,temp2,'-',label='H1 retro')
plt.plot_date(time3,temp3,'-',label='H2 launch')
plt.plot_date(time4,temp4,'-',label='H2 retro')
plt.plot_date(time5,temp5,'-',label='Bottom')
plt.plot_date(time6,temp6,'-',label='Top Mezz')
plt.plot_date(time7,temp7,'-',label='Air inside close')
plt.plot_date(time8,temp8,'-',label='Air inside far')
ax = plt.gca()
ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
plt.legend()
plt.xlabel('Time')
plt.ylabel('Temp (C)')
plt.title('Different locations around optical table')




plt.figure()
plt.plot_date(time1,temp1-np.mean(temp1),'-',label='H1 launch')
plt.plot_date(time2,temp2-np.mean(temp2),'-',label='H1 retro')
plt.plot_date(time3,temp3-np.mean(temp3),'-',label='H2 launch')
plt.plot_date(time4,temp4-np.mean(temp4),'-',label='H2 retro')
plt.plot_date(time5,temp5-np.mean(temp5),'-',label='Bottom')
plt.plot_date(time6,temp6-np.mean(temp6),'-',label='Top Mezz')
#plt.plot_date(time7,temp7-np.mean(temp7),'-',label='Air inside close')
#plt.plot_date(time8,temp8-np.mean(temp8),'-',label='Air inside far')


plt.plot_date(time1,avg_temp - np.mean(avg_temp),'--k',linewidth=3,label='Average')

ax = plt.gca()
ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
plt.legend()
plt.xlabel('Time')
plt.ylabel('Temp - mean(Temp) (C)')
plt.title('Different locations around optical table')



plt.figure()
plt.plot_date(time1, avg_temp,'-')
ax = plt.gca()
ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
plt.xlabel('Time')
plt.ylabel('Temp (C)')
plt.title('Average temp')




plt.show()
