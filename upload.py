from optparse import OptionParser
import serial
import xmodem
import os, sys, time
import logging
import pyprind

da_path = './da.bin'

logging.basicConfig()
parser = OptionParser(usage="python %prog [options]")
parser.add_option("-c", dest="com_port", help="COM port, can be COM1, COM2, ..., COMx")
parser.add_option("-d", action="store_true", dest="debug")
parser.add_option("-f", dest="bin_path", help="path of the bin file to be uploaded")
parser.add_option("-t", dest="target", help="target to be flashed (cm4 | ldr | n9).")
(opt, args) = parser.parse_args()

if opt.target != 'cm4' and opt.target != 'n9' and opt.target != 'ldr':
    print >> sys.stderr, "\nError: Invalid parameter!! Please specify the target to be flashed.\n"
    parser.print_help()
    sys.exit(-1)
    pass

debug = opt.debug

if not opt.bin_path or not opt.com_port:
    print >> sys.stderr, "\nError: Invalid parameter!! Please specify the COM port and the bin file.\n"
    parser.print_help()
    sys.exit(-1)

if not os.path.exists(opt.bin_path):
    print >> sys.stderr, "\nError: Bin file [ %s ] not found !!!\n" % (opt.bin_path)
    parser.print_help()
    sys.exit(-1)

#s = serial.Serial(opt.com_port, 115200)
#s.rts = 0;
s = serial.Serial()

def resetIntoBootloader():

    s.baudrate = 115200
    s.port = opt.com_port
    s.timeout = 1
    #s.rts = 0;
    s.open()

    #init Com port to orginal state
    s.setRTS(False)
    s.setDTR(False)
    time.sleep(0.05)

    #Discharge RTS
    s.setRTS(True)
    time.sleep(0.05)

    #Pull down only DTR
    s.setDTR(True)
    #time.sleep(0.01)
    s.setRTS(False)
    pass


#print >> sys.stderr, "Please push the Reset button"


error_count = 0
c_count = 0
retry = 0
start_time = time.time()
resetIntoBootloader()
while 1:
    c = s.read()
    if debug:
        print >> sys.stderr, "Read: "+c.encode('hex')
        pass
    if c == "C":
        c_count  = c_count +1
    if c!=0 and c!="C":
        error_count = error_count +1
    if c_count>1:
        print >> sys.stderr, "Start uploading the download agent"
        break
        pass
    if error_count>3:
        print "Error - Not reading the start flag"
        retry  = retry +1
        error_count = 0
        c_count = 0
        start_time = time.time()
        s.close()
        resetIntoBootloader()
    if time.time() - start_time > 3.0:
        print "Error - Timeout"
        retry  = retry +1
        error_count = 0
        c_count = 0
        start_time = time.time()
        s.close()
        resetIntoBootloader()
        pass
    if retry>3:
        print "Exiting"
        exit()
        pass


statinfo = os.stat(da_path)
bar = pyprind.ProgBar(statinfo.st_size/128+1)

def getc(size, timeout=1):
    return s.read(size)

def putc(data, timeout=1):
    bar.update()
    return s.write(data)

def putc_user(data, timeout=1):
    bar_user.update()
    return s.write(data)

def pgupdate(read, total):
    print "\r%d/%d bytes (%2.f%%) ..." % (read, total, read*100/total)

m = xmodem.XMODEM(getc, putc)

stream = open(da_path, 'rb')
m.send(stream)
s.baudrate = 115200*2

print >> sys.stderr, "DA uploaded, start uploading the user bin"
time.sleep(1)
if opt.target == 'ldr':
    s.write("1\r")
    pass
if opt.target == 'n9':
    s.write("3\r")
    pass
if opt.target == 'cm4':
    s.write("2\r")
    pass
s.flush()
s.flushInput()

flag = 1
while flag:
    c = s.read()
    if c =='C':
        flag = 0
        pass
    pass
s.flush()
s.flushInput()

statinfo_bin = os.stat(opt.bin_path)
bar_user = pyprind.ProgBar(statinfo_bin.st_size/128+2)
stream = open(opt.bin_path, 'rb')
m = xmodem.XMODEM(getc, putc_user)
m.send(stream)

print >> sys.stderr, "Bin file uploaded. The board reboots now."
time.sleep(1)
s.write("C\r")
s.flush()
s.flushInput()
