# AUTHOR: CONG WANG
# DATE: 2017/3/12

from BuildCaptureClass import BuildCaptureClass
from BuildCaptureMake import bcMake
from BuildCaptureFilter import bcFilter
from BuildCaptureDeal import bcDeal
from common import removeDir
from FileDetect import FsMonitor
import os, sys, getopt
import threading
import signal

# STEP.1: INIT THE OBJECT
print ""
print "------------Start Phase------------"

shell = "/bin/bash"
opts, args = getopt.getopt(sys.argv[1:], "s:")
for op, value in opts:
    if op == "-s":
        shell = value

input_folder = os.getcwd()
output_folder = os.path.join(input_folder, "..", "BCOUTPUT")
bcc = BuildCaptureClass(input_folder, output_folder, shell)

if os.path.exists(output_folder):
    removeDir(output_folder)
os.mkdir(output_folder)

# DEBUG
print "The current directory is: " + bcc.input_folder
print "The output is stored in: " + bcc.output_folder


class Counter(threading.Thread):
    def __init__(self, lock, threadName):
        super(Counter, self).__init__(name=threadName)
        self.lock = lock

    def run(self):
        FsMonitor(bcc.input_folder)


lock = threading.Lock()
counter = Counter(lock, "thread-fsmonitor")
counter.start()

# STEP.2: EXECUTE 'MAKE' IN BASH AND SAVE THE OUTPUT AS 'ALL'
print ""
print "------------Make Phase------------"

make_status = bcMake(bcc)
if make_status == -1:
    print "[TYPE.1]Error in 'make'"
    sys.exit()
elif make_status == -2:
    print "[TYPE.2]Error in 'make clean'"
    sys.exit()
elif make_status == -3:
    print "[TYPE.3]Error in 'write all'"

# DEBUG
print "The output of 'make' is stored in: " + bcc.all_file
print ("This file contains %d lines" % (bcc.line_in_all))

# STEP.3: FILTER ALL THE OUTPUT AND SAVE THE OUTPUT AS 'OUTPUT'
print ""
print "------------Filter Phase------------"

filter_status = bcFilter(bcc)
if filter_status == -1:
    print "[TYPE.4]Error in 'write output'"

# DEBUG
print "The output of 'filter' is stored in: " + bcc.output_file
print ("This file contains %d lines" % (bcc.line_in_output))

# STEP.4: DEAL THE LINES IN 'OUTPUT'
print ""
print "------------Deal Phase------------"

deal_status = bcDeal(bcc)
os.kill(os.getpid(), signal.SIGTERM)
