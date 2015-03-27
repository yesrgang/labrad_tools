import labrad
cxn = labrad.connect()
n = cxn.node_yesr12
n.stop('yesr12_red_master_dds')
n.restart('yesr12_serial_server')
n.start('red_master_dds')
