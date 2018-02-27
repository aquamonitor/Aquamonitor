#!/usr/bin/python

import sys, time, httplib, urllib, urllib2, logging, RPi.GPIO as GPIO, os.path, os, traceback, signal, pygame, syslog
from subprocess import call, Popen, PIPE
from datetime import datetime, timedelta

Alarms={"WATER_LEAK_DETECTOR_1":0,"WATER_LEAK_DETECTOR_2":0,"FLOATSW_HIGH_WL":0,"FLOATSW_LOW_WL":0}    # Alarm flags dictionary
Pins={"WATER_LEAK_DETECTOR_1":24,"WATER_LEAK_DETECTOR_2":23,"FLOATSW_HIGH_WL":26,"FLOATSW_LOW_WL":19}  # GPIO Pins mapping
PUSHOVER_TOKEN = "[YOUR APP ID]"                      # your Pushover APP toker
PUSHOVER_USER = "[YOUR TOKEN]"                        # your Pushover USER token
LOOP_WAIT_TIMER = 16                                  # defines how many seconds interval between polling
VERSION = 1.8                                         # Code version number
CAM_URL = "http://123.200.100.99:9091"                # Camera URL
REPEAT_TIMER = 10

def Audio_alarm():
    try:
         pygame.mixer.init()
         pygame.mixer.music.load("/usr/local/python/Aquamonitor/alarm.mp3")
         pygame.mixer.music.play()
         while pygame.mixer.music.get_busy() == True:
             continue
    except:
         Alert("Cannot play alarm wave file.")
         Pass

def Setup():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(Pins["FLOATSW_HIGH_WL"], GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(Pins["FLOATSW_LOW_WL"], GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(Pins["WATER_LEAK_DETECTOR_1"], GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(Pins["WATER_LEAK_DETECTOR_2"], GPIO.IN, pull_up_down=GPIO.PUD_UP)
    if not sys.stdout.isatty():                                 # if we are not running from console, redirect the stdout & err to files
        sys.stdout = open('/var/log/aquamonitor_stdout.log', 'a')
        sys.stderr = open('/var/log/aquamonitor_stderr.log','a')

def Time():
    return time.strftime("%D %H:%M:%S: ")

def Send_pushover(pushover_content):
    try:
        conn = httplib.HTTPSConnection("api.pushover.net:443")
        conn.request("POST", "/1/messages.json",
                    urllib.urlencode({
                    "token": PUSHOVER_TOKEN,
                    "user": PUSHOVER_USER,
                    "message": pushover_content,
                    }),
                    { "Content-type": "application/x-www-form-urlencoded" }
                    )
        conn.getresponse()
    except:
        print(Time() + "could not send pushover alert, passing")
        pass

def Refilling():
    try:
        response = urllib2.urlopen("http://192.168.0.150/set.cmd?user=admin+pass=12345678+cmd=getpower", timeout = 10)
        time.sleep(5)
        content = response.read()
        i = content[10]
        if int(i) == 1:
            return True
        else:
            return False
    except urllib2.URLError as e:
        print(Time() + "could not check IP power plug state, passing: " + str(e))
        Send_alert("Cannot communicate with valve: " + str(e), syslog.LOG_ERR)
        pass

def Close_RODI():
   try:
       urllib2.urlopen("http://192.168.0.150/set.cmd?user=admin+pass=12345678+cmd=setpower+p61=0", timeout = 15)
       time.sleep(5)
   except urllib2.URLError as e:
       Send_alert("Cannot communicate with valve: " + type(e), syslog.LOG_ERR)

def Send_alert(message, level):
    syslog.syslog(level,message)
    Send_pushover(message)
    print(Time() + message)

def Repeat_alert(probe, message, timer):
    global Alarms
    if datetime.now() > Alarms[probe] + timedelta(minutes=timer):
        Send_alert(message,syslog.LOG_WARNING)
        Alarms[probe] = datetime.now()                                        # reset alarm timestamp to reset the counter for next iteration

def Alert(message, probe):                                                    # In any event of an alert, inform through log, mail & pushover
    global Alarms
    Alarms[probe] = datetime.now()                                            # set a timestamp for recurring alarm cooldown and alert
    if probe == "WATER_LEAK_DETECTOR_1" or probe == "WATER_LEAK_DETECTOR_2":
        Send_alert(message,syslog.LOG_EMERG)
    elif probe == "FLOATSW_HIGH_WL":
        Send_alert(message,syslog.LOG_ERR)
    elif probe == "FLOATSW_LOW_WL":
        Send_alert(message,syslog.LOG_NOTICE)

def Monitor_probe(probe, mesg):
    global Alarms
    if GPIO.input(Pins[probe]) == 0 and Alarms[probe] == 0:                   # An alert is detected, for the first time on this probe: alarm + actions
        Alert(mesg, probe)                                                    # Send the initial Alert
        if probe == "WATER_LEAK_DETECTOR_1" or probe == "WATER_LEAK_DETECTOR_2":
           Audio_alarm()
           if Refilling() == True:
                Alert(mesg + " RO/DI valve was opened, closing it.", probe)
                Close_RODI()
           else:
                Alert(mesg, probe)
        if probe == "FLOATSW_LOW_WL" and Refilling() == False:
            proc = Popen(['python', '/usr/local/python/Aquamonitor/rodi.py', str(600)])
            Alert("Refilling for 600 seconds", probe)                     # by refilling
        if probe == "FLOATSW_HIGH_WL":                                    # or by stopping the current refill, if need be
            if Refilling() == False:
                Alert(mesg, probe)
            else:
                Close_RODI()
                Alert(mesg + " stopping the current refill. ", probe)
    elif GPIO.input(Pins[probe]) == 0 and Alarms[probe] !=0:              # if alarms continues, we already took actions, so just inform every X minutes
         Repeat_alert(probe, "Repeated: " + mesg, REPEAT_TIMER)
    elif GPIO.input(Pins[probe]) == 1 and Alarms[probe] !=0:              # If we have no longer an alert on the pin but have a not yet cleared alarm
         Alert(mesg + " stopped", probe)                                  # tell all is back to normal
         Alarms[probe] = 0                                                # clear the alarm flag

class GracefulKiller:
    kill_now = False
    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)
    def exit_gracefully(self,signum, frame):
        self.kill_now = True

if sys.argv[1] == "start":
    Setup()
    killer = GracefulKiller()
    Send_alert("Starting Aquamonitor v" + str(VERSION) + " continuous monitoring.",syslog.LOG_NOTICE) # Tell the user we (re)started
    while True:                                                                            # Good old infinite loop, what would we be without them?
        Monitor_probe("WATER_LEAK_DETECTOR_1","Water leak near RO/DI " + str(CAM_URL))     # Monitor the various probes and react accordingly
        Monitor_probe("WATER_LEAK_DETECTOR_2","Water leak under the tank " + str(CAM_URL))
        Monitor_probe("FLOATSW_LOW_WL","Low water level in the sump " + str(CAM_URL))
        Monitor_probe("FLOATSW_HIGH_WL","High water level in the sump " + str(CAM_URL))
        time.sleep(LOOP_WAIT_TIMER)                                                        # Execute loop only every minute to lower CPU footprint
        if killer.kill_now:
            Send_alert("Caught a SIGINT or SIGTERM, exiting cleanly",syslog.LOG_NOTICE)
            Close_RODI()
            GPIO.cleanup()
            sys.exit(3)
else:
    print(Time() + "Too few argument provided or start not mentionned")
    sys.exit(2)

# Exit code
# 0 : Normal exit
# 1 : Keyboard CTRL+C exit
# 2 : Incorrect argument provided
# 3 : Sigterm or Sigint
