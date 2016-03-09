import sys
import labrad

if __name__ == "__main__":
    string = str(sys.argv[1])
    cxn = labrad.connect()
    server = cxn.vagabond_receiver
    received_string = server.send_string(string)
    sys.stdout.write(str(received_string))
