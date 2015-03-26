""" 
This class defines a double exponential to fit its parameters
"""
import numpy as np
from fitcurve import CurveFit

def heaviside(array_in):
    array_out = np.zeros(len(array_in))
    for i in range(len(array_in)):
        if array_in[i] < 0.0:
            array_out[i] = 0.0
        elif array_in[i] > 0.0:
            array_out[i] = 1.0
        elif array_in[i] == 0.0:
            array_out[i] = 0.5
    return array_out

class FitDoubleExponential(CurveFit):
    def __init__(self, parent):
        self.parent = parent
        self.curveName = 'Double Exponential'
        self.parameterNames = ['A', 'C', 't0', 'tau1', 'tau2']
        self.parameterValues = [100.0, 1.0, 20.0, 20.0, 2.0]
        self.parameterFit = [True, True, True, True, True]

    def fitFunc(self, x, p):
        evolution = p[0]*heaviside(x-p[2])*(np.exp(-(x-p[2])/p[3]) - np.exp(-(x-p[2])/p[4])) + p[1]
        return evolution

if __name__ == '__main__':
    import matplotlib.pyplot as plt
    x = np.linspace(0, 160, 100)
    dxp = FitDoubleExponential(0.)
    plt.plot(x, dxp.fitFunc(x, dxp.parameterValues))
    plt.show()
