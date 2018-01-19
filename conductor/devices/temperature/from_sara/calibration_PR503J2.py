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


def r2t(R):
	return a5*R**5 + a4*R**4 + a3*R**3 + a2*R**2 + a1*R + a0

print a0, a1, a2, a3, a4, a5

print r2t(55e3)
print r2t(50e3)

fig = plt.figure()
plt.plot(R, T, 'bo')
y = r2t(R)
plt.plot(R, y, 'r')
#plt.show()
