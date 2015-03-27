import labrad
cxn = labrad.connect()
n = cxn.node_yesr12
n.stop('yesr12 Red Master DDS')
n.restart('yesr12 Serial Server')
n.start('Red Master DDS')
