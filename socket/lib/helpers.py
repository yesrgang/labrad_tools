import os
import subprocess

def get_network_devices():
    all_addresses = ['192.168.1.{}'.format(i) for i in range(128)]
    all_addresses_str = ''.join([' ' + addr for addr in all_addresses])
    result = None
    available_addresses = []
    for address in all_addresses:
        result = subprocess.call('fping -q -t10 -c1 {}'.format(address) + ' > /dev/null 2>&1', shell=True)
        if not result:
            available_addresses.append(address)
    return available_addresses

if __name__ == '__main__':
    print get_network_devices()

