from twisted.internet.defer import Deferred
from twisted.internet.reactor import callLater

def sleep(secs):
    d = Deferred()
    callLater(secs, d.callback, None)
    return d

def get_instruction_set(address, register, data):
    ins = [58, address, len(data)+1, register] + data
    ins_sum = sum(ins[1:])
    ins_sum_bin = bin(ins_sum)[2:].zfill(8)
    lowest_byte = ins_sum_bin[-8:]
    checksum = int('0b'+str(lowest_byte), 0)
    ins.append(checksum)
    return [chr(i) for i in ins]
