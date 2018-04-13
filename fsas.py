import string
import serial, sys, time
import numpy as np
import pickle
from datetime import datetime
import matplotlib.pyplot as plt
import os.path

debug_flag = False # becomes a bit more verbose
filename = None # set to the pickle file we want to load instead of capturing a new trace

GPIB_delay = 0.5 # delay in seconds after each serial command

# GPIB addressing table
address_talk = list('@' + string.ascii_uppercase) # '@ABCDEFGHIJKLMNOPQRSTUVWXYZ'
address_listen = list(''.join([chr(i) for i in range(32,63)]) ) # ' !"#$%&\'()*+,-./0123456789:;<=>'

# the addresses of my devices
control_index = 10 # Arduino GPIB-USB serial converter (Jacek Greniger GitHub)
fsas_index = 20    # Rohde-Schwarz Spectrum Analyzer 100Hz-2GHz
smcp_index = 1     # Rohde-Schwarz Signal Generator 5kHz-1.3GHz

# verify if an active serial port is present
serial_ports = ["/dev/ttyUSB%d"%i for i in xrange(4)]

serial_open_flag = False

# send a serial command followed by a LF CR "\r\n"
def write(cmd):
    string = cmd+"\r\n"
    s.write(string)
    if debug_flag:
        print string
    time.sleep(GPIB_delay)

# send a serial command followed by a LF CR "\r\n and listen for a reply"
def query(cmd):
    string = cmd+"\r\n"
    s.write(string)
    time.sleep(GPIB_delay)
    if s.inWaiting():
        tmp = s.readline()
    if debug_flag:
        print string, tmp
    
# obtain the talker or listener index from a specific address as specified in the GPIB addressing table
def set_listener_talker(listener, talker):
    listener_ = address_listen(listener)
    talker_ = address_talk(talker)
    string = "C_?%s%s" % (listener_, talker_)
    if debug_flag:
        print "Listens: %d <- Talks: %d -- CMD: %s" % (listener, talker, string)
    write(string)

def read_trace_data():
    TRACE_SIZE = 2190 # FSAS dumps 2190 bytes when asked for a trace complete with the header (the first 1802 bytes for 901 points (one int16 each))

    query('DTRACE:BLOCK:T_1?') # ask for a trace (1) dump

    # switch control interface to listen to commands and FSAS to talk
    set_listener_talker(control_index, fsas_index)

    print "---- NOW RECEIVING TRACE DUMP DATA FROM FSAS ----"

    buffer = ""
    while len(buffer) < TRACE_SIZE + 10: # we add some margin since we're adding control strings
        tmp = ""
        write("Y") # read a full buffer of data from the instrument
        time.sleep(GPIB_delay) # wait a bit for the data transmission to finish
        tmp += "XXX" # we add a marker to locate different dumps (~395 bytes each)
        while s.inWaiting()>0: # is any character present in the serial buffer
            tmp += s.read(1) # read one byte
        buffer += tmp

    # remove garbage from buffer and return
    return buffer.replace("XXXOK\r\nOK\r\nOK\r\n\xfe", "").replace("XXX\xfe", "")

print "---------------------------"
print "--- Rohde-Schwarz  FSAS ---"
print "---  Spectrum Analyzer  ---"
print "---   TRACE DUMP TOOL   ---"
print "---------------------------"
print "--- marco cogoni IS0KYB ---"
print "---------------------------"
print

if len(sys.argv) == 1: # no command line options
    print "Command line options:\n"
    print "-f tracedump.pickle\t -> load a saved tracedump from File and process it producing an out image and print FSAS data"
    print "-c\t\t\t -> use the GPIB bus to Capture a trace dump from the FSAS\n"
    exit()
elif len(sys.argv) == 2: # capture a new trace
    if sys.argv[1] == "-c":
        pass
elif len(sys.argv) == 3: # don't connect to the FSAS, just load an old tracedump from file
    if sys.argv[1] == "-f":
        filename = sys.argv[2]
        with open(filename, "rb") as fn:
            dump_data = pickle.load(fn)
            print "... loading file to process ...\n"

if not filename:
    for p in serial_ports:
        if os.path.exists(p):
            #s = serial.Serial(port=p, baudrate=115200, bytesize=8, parity='N', stopbits=1, timeout=None, xonxoff=0, rtscts=0)
            s = serial.Serial(port=p, baudrate=115200)
            time.sleep(3)
            if s.isOpen():
                serial_open_flag = True
                print "Active Serial Connection:", p
                break
    if not serial_open_flag:
        print "Serial connection not working!!!"
        exit()
        

gpib_buffer_file = "GPIB_tracedump.%s.pickle" % str(datetime.now()).split(".")[0].replace(" ", "_")


#########################################    
# Start writing on the serial interface #
#########################################
if not filename:
    print "Flushing the serial queue..."
    while s.inWaiting(): # flush the serial interface before beginning
        s.read(1)

    # start sending GPIB commands
    query("E0") # disable local serial echo
    query("R") # enable remote operations on the GPIB bus

    # switch FSAS to listen commands and control inteface to talk
    set_listener_talker(fsas_index, control_index)

    query("DF:C 1M") # set the center frequency on the FSAS
    
    buffer = read_trace_data() # read trace data from FSAS
    s.close()

    # Save binary buffer to disk
    with open(gpib_buffer_file, 'wb') as f:
        pickle.dump(buffer,f)
else:
    buffer = dump_data

# let's decode the uncorrected trace information:
# val = uint16 >> 4
raw_trace_data = np.right_shift(np.fromstring(buffer[:], dtype=np.uint16, count=901), 4)

# let's decode the header information: we don't need everything!

# this dictionary contains low level data types for each FSAS property at its byte offset
data_type_dict = {1802:'<B',1803:'<B',1804:'<B', 1805:'<i2', 1807:'<i2', 1809:'<i2', 1811:'<i2',1813:'<B',1814:'<B', 1815:'<i2', 1817:'<B', 1819:'<B', 1853:'<i2',
                 1896:'<i4', 1914:'<i4', 1920:'<i4', 1926:'<i4', 1930:'<i4'}

# each offset has its full description
data_descript_dict = {1802:'Mode (3: Freq. Analyzer, 4: Scalar Network Analyzer, 6:Communication Analyzer, 7: Receiver)',1803:'keys',1804:'keys', 1805:'Ref. Level (dB * 0.01)', 1807:'Ref. Level Offset (dB * 0.01)', 1809:'Lev. Tracking Gen. (dB * 0.01)', 1811:'Lev. Offset Tracking Gen. (dB * 0.01)',
                  1813:'RF Attenuator (dB)',1814:'Tracking Generator Attenuation (dB)', 1815:'Mixer Level (dB * 0.01)', 1817:"Range etc", 1819:"Units", 1853:'Averaging Samples',
                 1896:'Center Freq. (Hz)', 1914:'Start Freq. (Hz)', 1920:'Stop Freq. (Hz)', 1926:'Sweep Time (0.1 ms)', 1930:'RBW (Hz)'}

# each property has a concise name linked to the byte offset
data_name_dict = {'mode':1802,'keys1':1803,'keys2':1804, 'ref_level':1805, 'ref_level_offset':1807, 'level_tracking_gen':1809, 'level_offset_tracking_gen':1811,
                  'rf_att':1813,'tracking_gen_att':1814, 'mixer_level':1815, "range":1817, "units":1819, 'avg_samples':1853,
                 'ceter_freq':1896, 'start_freq':1914, 'stop_freq':1920, 'sweep_time':1926, 'rbw':1930}

data_values_dict = {}

# read in the values
print "------------------------------"
print "A few parameters from the FSAS"
print "------------------------------\n"
for off in data_type_dict:
    data_values_dict[off] = np.fromstring(buffer[off:], dtype=data_type_dict[off], count=1)
    print "byte offset:", off, "value:", data_values_dict[off][0],"\t\t", data_descript_dict[off]

    
############ Visualization
font = {'weight' : 'bold',
        'size'   : 15}

plt.rc('font', **font)

fig = plt.figure(figsize=(16,16))

start_freq, stop_freq = np.fromstring(buffer[1914:], dtype=data_type_dict[1914], count=1)/1e6, np.fromstring(buffer[1920:], dtype=data_type_dict[1920], count=1)/1e6
ref_level = np.fromstring(buffer[1805:], dtype=data_type_dict[1805], count=1)[0]/100.
ref_level_offset = np.fromstring(buffer[1807:], dtype=data_type_dict[1807], count=1)[0]/100.
rbw = np.fromstring(buffer[1930:], dtype=data_type_dict[1930], count=1)[0]/1e4
sweep_time = np.fromstring(buffer[1926:], dtype=data_type_dict[1926], count=1)[0]/1e4
rf_att = np.fromstring(buffer[1813:], dtype=data_type_dict[1813], count=1)[0]


range_ = data_values_dict[ data_name_dict['range'] ]
mask = int('00000111', 2)
if range_&mask == 0:
    range_range = 110.
elif range_&mask == 1:
    range_range = 100.
elif range_&mask == 2:
    range_range = 50.
elif range_&mask == 2:
    range_range = 50.
elif range_&mask == 3:
    range_range = 20.
elif range_&mask == 4:
    range_range = 10.
elif range_&mask == 5:
    range_range = 1.

mask = int('00001000', 2)
if range_&mask:
    range_scaling = "lin"
else:
    range_scaling = "log"

mask = int('00010000', 2)
if range_&mask:
    range_axis = "db"
else:
    range_axis = "percent" # not implemented yet

mask = int('00100000', 2)
if range_&mask:
    range_grid = "abs"
else:
    range_grid = "rel" # not implemented yet

mask = int('10000000', 2)
if range_&mask:
    range_freq = "lin"
else:
    range_freq = "log"

ax = fig.add_subplot(111)#, axisbg='blue')
ax.set_facecolor('blue')
fig.patch.set_facecolor('blue')

trace_data = (raw_trace_data-3938.)/3938.*(range_range)+ref_level+ref_level_offset # FIXME: the range should be decoded from the header data too!
plt.plot(np.linspace(start_freq, stop_freq, 901), trace_data[:], c='lightgreen')

plt.grid(color="w")
plt.xlabel("Freq. (MHz)", color="w", fontweight='bold')
plt.ylabel("Power (dBm)", color="w", fontweight='bold')
plt.ylim(-range_range+ref_level+ref_level_offset, ref_level+ref_level_offset)
plt.xlim(start_freq, stop_freq)
plt.xticks(np.linspace(start_freq, stop_freq, 11), color="w")
plt.yticks(np.linspace(-range_range+ref_level, ref_level, 12), color="w")
plt.title("ROHDE & SCHWARZ FSAS", color='w', fontsize=20)
rbw_text = "RBW: "+str(rbw)+" kHz"
rf_att_text = "RF Att: "+str(rf_att)+" dB"
sweep_text = "Sweep: "+str(sweep_time)+" s"
plt.text(0.8,1.08, rbw_text,
     horizontalalignment='left',
     verticalalignment='center', transform=ax.transAxes, color="w")
plt.text(0.8,1.06, rf_att_text,
     horizontalalignment='left',
     verticalalignment='center', transform=ax.transAxes, color="w")
plt.text(0.8,1.04, sweep_text,
     horizontalalignment='left',
     verticalalignment='center', transform=ax.transAxes, color="w")

fig.savefig(gpib_buffer_file[:-7] + ".png", frameon=True, facecolor='b', edgecolor='b',)

