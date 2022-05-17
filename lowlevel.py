import serial #for port opening
import sys #for exceptions
from ai import AI
# from collections import __main__
#

#configure the serial connections (the parameters differs on the device you are connecting to)

class Serializer: 
    def __init__(self, port, baudrate=115200, timeout=5): 
        self.port = serial.Serial(port = port, baudrate=baudrate, 
        timeout=timeout, writeTimeout=timeout)

    def open(self): 
        ''' Open the serial port.'''
        self.port.open()

    def close(self): 
        ''' Close the serial port.'''
        self.port.close() 

    def send(self, chosen_move):
        self.port.write(chosen_move)

    def recv(self):
        return self.port.readline() 

PORT = '/dev/ttyUSB0' #Esto puede necesitar cambiarse

def main():
    test_port = Serializer(port = PORT)
    try:
        test_port().open()
    except:
        print ("Could not open serial port: ", sys.exc_info()[0])
        sys.exit()

    while True:
        print(test_port.recv())

if __name__ == "__main__":
     main()
