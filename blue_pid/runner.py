import time
import labrad
from pid import PID

T = 2

cxn = labrad.connect()
tlb = cxn.yesr20_tlb_6700
dmm = cxn._34980a

pid = PID(
    sampling_interval=T,
    overall_gain=1,
    prop_gain=-5e-2,
    int_gain=5e-2,
    min_max=(69, 72),
    )


if __name__ == '__main__':
    dmm.select_device_by_name('srq monitor')
    pi = tlb.piezo_voltage()
    pid.offset = pi
    while 1:
        v = dmm.measure_channel('Blue Spec. Err.')
        tick = pid.tick(v)
        print v, tick-pi
        pi = tick
        tlb.piezo_voltage(tick)
        time.sleep(T)

