#!/usr/bin/python

import sys, signal, time, RPi.GPIO as GPIO, os, logging, fcntl, subprocess, syslog, urllib2
from time import gmtime, strftime

FLOATSW_HIGH_WL = 26                                  # high water level float switch
VALVE_CHGSTATE_TIMER = 15                             # Electro valve needs roughly 20 seconds to switch from open to close and vice versa

def Setup():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(FLOATSW_HIGH_WL, GPIO.IN, pull_up_down=GPIO.PUD_UP)      #, initial = GPIO.HIGH)
    if not sys.stdout.isatty():
        sys.stderr = open('/var/log/rodi_stderr.log', 'a')
        sys.stdout = open('/var/log/rodi_stdout.log', 'a')

def Alert(message,level):
    syslog.syslog(level, message)
    print(Time()+message)

def Time():
     return time.strftime("%D %H:%M:%S: ")

def Close_valve():
    Alert("Closing the RO/DI valve", syslog.LOG_NOTICE)
    try:
        urllib2.urlopen("http://192.168.0.150/set.cmd?user=admin+pass=12345678+cmd=setpower+p61=0", timeout = 10)
        time.sleep(5)
    except urllib2.URLError as e:
        Send_alert("Cannot communicate with valve: " + type(e), syslog.LOG_ERR)

def Refilling():
    try:
        response = urllib2.urlopen("http://192.168.0.150/set.cmd?user=admin+pass=12345678+cmd=getpower", timeout = 10)
        content = response.read()
        time.sleep(2)
        i = content[10]
        if int(i) == 1:
            return True
        else:
            return False
    except urllib2.URLError as e:
        Send_alert("Cannot communicate with valve: " + type(e), syslog.LOG_ERR)

def Open_valve():
    if Refilling() == True:
        Alert("RO/DI Valve already opened",syslog.LOG_WARNING)
        sys.exit(5)
    else:
        Alert("Opening the RO/DI valve",syslog.LOG_NOTICE)
        try:
            urllib2.urlopen("http://192.168.0.150/set.cmd?user=admin+pass=12345678+cmd=setpower+p61=1", timeout = 10)
            time.sleep(5)
        except urllib2.URLError as e:
            Send_alert("Cannot communicate with valve: " + type(e), syslog.LOG_ERR)
        time.sleep(VALVE_CHGSTATE_TIMER)

class GracefulKiller:
     kill_now = False
     def __init__(self):
         signal.signal(signal.SIGINT, self.exit_gracefully)
         signal.signal(signal.SIGTERM, self.exit_gracefully)
     def exit_gracefully(self,signum, frame):
         self.kill_now = True

if not len(sys.argv) > 1:
    print(Time() + "You must provide one numerical argument to this function (duration in seconds). Exiting.")
    sys.exit(1)

if sys.argv[1] != "close" and sys.argv[1] != "stop" and not sys.argv[1].isdigit():
    print(Time() + "Value is neither 'close', 'stop' or a refill duration expressed in seconds")
    sys.exit(1)

i = 0
killer = GracefulKiller()
Setup()

if sys.argv[1] == "close" or  sys.argv[1] == "stop":
    Close_valve()
    sys.exit(0)

cnt = str.count(subprocess.check_output(["ps", "aux"]), "rodi.py")
if cnt > 1:
    Alert("Warning, we were called while other instance(s) of Rodi was already in Memory ("+str(cnt)+")",syslog.LOG_ERR)
    sys.exit(1)

if str.count(subprocess.check_output(["ps", "aux"]), "aquamonitor") < 1:
    Alert("Warning, we were called but Aquamonitor is not running, this could be dangerous, exiting.",syslog.LOG_CRIT)
    sys.exit(1)


if sys.argv[1].isdigit():
   if sys.argv[1] > 1000:
       Alert("Duration of refill set to more than 1000 seconds (" + str(i) + ") most likely a daily refill",syslog.LOG_NOTICE)
   if GPIO.input(FLOATSW_HIGH_WL) == 0:
       Alert("Water level in sump already high, refilling would be dangerous, exiting", syslog.LOG_ERR)
       if Refilling() == True:
           Alert("Also, RO/DI Valve already opened while high water in the sump, closing.", syslog.LOG_ERR)
           Close_valve()
       sys.exit(3)
   else:
       try:
           Alert("Not already refilling, sump water level normal, proceeding.", syslog.LOG_INFO)
           Alert("Refilling for " + sys.argv[1] + " seconds", syslog.LOG_INFO)
           Open_valve()
           while i < int(sys.argv[1]):
               time.sleep(1)
               i=i+1
               if i % 200 == 0:
                  if Refilling() == False:
                      Alert("Valve was closed while we were refilling. Exiting.",syslog.LOG_ERR)
                      sys.exit(1)
               if i % 30 == 0:
                   if GPIO.input(FLOATSW_HIGH_WL) == 0:
                       Alert("Water level in sump is now high, stopping the refill",syslog.LOG_WARNING)
                       Close_valve()
                       sys.exit(2)
               if killer.kill_now:
                   Alert("Caught a Sigterm, Sigkill or CTRL+C, exiting.",syslog.LOG_NOTICE)
                   Close_valve()
                   sys.exit(3)
           Close_valve()
           Alert("Refill done, exiting.",syslog.LOG_NOTICE)
           sys.exit(0)
       except RuntimeError as e:
           Alert("Caught a Runtime exception, exiting. Err No {0} / {1}".format(e.errno, e.strerror), syslog.LOG_ERR)
           Close_valve()
           sys.exit(4)
       except IOError as e:
           Alert("Caught an I/O exception, exiting. Err No {0} / {1}".format(e.errno, e.strerror), syslog.LOG_ERR)
           Close_valve()
           sys.exit(6)
else:
    sys.exit(7)

# Exit code :
# 7 : A non numerical argv[1] was given
# 6 : Caught an I/O exception
# 5 : already refilling
# 4 : Caught a runtime exception
# 3 : water is high either at start or during the refill
# 2 : a sigkill, sigterm or keyboard CTRL+C signal was received
# 1 : incorrect parameter received
# 0 : all went fine
