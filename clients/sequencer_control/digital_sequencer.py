from PyQt4 import QtGui, QtCore, Qt
from PyQt4.QtCore import pyqtSignal 
from client_tools import SuperSpinBox
from connection import connection
from twisted.internet.defer import inlineCallbacks
import numpy as np
import json
import matplotlib
matplotlib.use('Qt4Agg')
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import digital_channel_control as dcc

sbwidth = 65
sbheight = 15
pbheight = 20
acheight = 50
nlwidth = 200
ncwidth = 130
drheight = 20
pps = 1001

max_columns = 100
colors = ['#ff0000', '#ff7700', '#00ff00', '#0000ff', '#8a2be2', '#c77df3']
