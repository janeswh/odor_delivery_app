import serial
import time
import pdb

# ser = serial.Serial('COM6', 9600, timeout=0, parity=serial.PARITY_EVEN, rtscts=1)
ser = serial.Serial("COM8", 9600)
print("Opening Serial Port")
time.sleep(2)
# two seconds for arduino to reset and port to open

s = "5"
r = "0"

print("Sending " + s)
ser.write(s.encode())  # default encoding UTF-8 for Arudino bytes

print("Echo back from Aduino")
pdb.set_trace()
r = ser.read()
print(r.decode())  # eliminate the 'b' bytes indicator default UTF-8
