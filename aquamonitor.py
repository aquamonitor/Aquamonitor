#!/usr/bin/python

import sys, time, smtplib, httplib, urllib, logging, RPi.GPIO as GPIO, os.path, os, traceback, signal, pygame
from subprocess import call, Popen, PIPE
from email.mime.text import MIMEText
from datetime import datetime, timedelta

Alarms={"WATER_LEAK_DETECTOR_1":0,"WATER_LEAK_DETECTOR_2":0,"FLOATSW_HIGH_WL":0,"FLOATSW_LOW_WL":0,"FLOATSW_LOW_AWC_WL":0}        # Alarm flags dictionary
#Alarms_messages=
Pins={"WATER_LEAK_DETECTOR_1":23,"WATER_LEAK_DETECTOR_2":24,"FLOATSW_HIGH_WL":13,"FLOATSW_LOW_WL":19,"FLOATSW_LOW_AWC_WL":22,
      "WATER_VALVE":10,"LED_PIN_R":4,"LED_PIN_G":17,"LED_PIN_B":27,"AWC_PUMP_OUT":9,"AWC_PUMP_IN":11}                             # GPIO Pins mapping
Colors={"RED":0xFF0000,"GREEN":0x00FF00,"YELLOW":0xFFFF00,"PURPLE":0xFF00FF,"BLUE":0x00FFFF,"DEEPBLUE":0x0000FF,"WHITE":0xFFFFFF} # Color table
MAIL_TO = ''                                          # Your destination email for alerts
MAIL_FROM = ''                                        # The source address for emails (can be non existent)
MAIL_SUBJECT = 'ALERT AQUARIUM'                       # The subject
SMTP_AUTH_USERNAME = ''                               # The SMTP server authentication username
SMTP_AUTH_PASSWD = ''                                 # The SMTP server authentication passwd
SMTP_SERVER = ""                                      # The SMTP server address
SMTP_PORT = 25                                        # The SMTP server port
PUSHOVER_TOKEN = ""                                   # your Pushover APP toker
PUSHOVER_USER = ""                                    # your Pushover USER token
TEST_FLAG = 0                                         # if in debug mode, set flag to 1 and no mail or pushover will be sent
LOOP_WAIT_TIMER = 5                                   # defines how many seconds interval between polling
VERSION = 1.5                                         # Code version number
logger = None                                         # empty variable for the logger handler to make it global
p_R = None
p_G = None
p_B = None

def Audio_alarm():
    if TEST_FLAG == 0:
        pygame.mixer.init()
        pygame.mixer.music.load("/usr/local/python/Aquamonitor/alarm.mp3")
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy() == True:
            continue
        
def Setup():
    global logger
    global p_R
    global p_G
    global p_B
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(Pins["FLOATSW_HIGH_WL"], GPIO.IN, pull_up_down=GPIO.PUD_UP, initial = GPIO.HIGH)
    GPIO.setup(Pins["FLOATSW_LOW_WL"], GPIO.IN, pull_up_down=GPIO.PUD_UP, initial = GPIO.HIGH)
    GPIO.setup(Pins["FLOATSW_LOW_AWC_WL"], GPIO.IN, pull_up_down=GPIO.PUD_UP, initial = GPIO.HIGH)    
    GPIO.setup(Pins["WATER_LEAK_DETECTOR_1"], GPIO.IN)
    GPIO.setup(Pins["WATER_LEAK_DETECTOR_2"], GPIO.IN)
    GPIO.setup(Pins["WATER_VALVE"], GPIO.OUT)
    GPIO.setup(Pins["AWC_PUMP_IN"], GPIO.OUT)
    GPIO.setup(Pins["AWC_PUMP_OUT"], GPIO.OUT)
    GPIO.setup(Pins["LED_PIN_R"], GPIO.OUT, initial = GPIO.HIGH) #high = leds off
    GPIO.setup(Pins["LED_PIN_G"], GPIO.OUT, initial = GPIO.HIGH)
    GPIO.setup(Pins["LED_PIN_B"], GPIO.OUT, initial = GPIO.HIGH)
    p_R = GPIO.PWM(Pins["LED_PIN_R"], 2000)
    p_G = GPIO.PWM(Pins["LED_PIN_G"], 2000)
    p_B = GPIO.PWM(Pins["LED_PIN_B"], 2000)
    p_R.start(0)
    p_G.start(0)
    p_B.start(0)
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler('/var/log/aquamonitor.log')
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(message)s',"%Y-%m-%d %H:%M:%S")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    if not sys.stdout.isatty():                                 # if we are not running from console, redirect the stdout & err to files
        sys.stdout = open('/var/log/aquamonitor_stdout.log', 'a')
        sys.stderr = open('/var/log/aquamonitor_stderr.log','a')
        
def Map(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def Set_led_color(col):                      # For example : col = 0x112233                                 
    R_val = (col & 0x110000) >> 16
    G_val = (col & 0x001100) >> 8
    B_val = (col & 0x000011) >> 0
    R_val = Map(R_val, 0, 255, 0, 100)
    G_val = Map(G_val, 0, 255, 0, 100)
    B_val = Map(B_val, 0, 255, 0, 100)
    p_R.ChangeDutyCycle(R_val)
    p_G.ChangeDutyCycle(G_val)
    p_B.ChangeDutyCycle(B_val)

def Stop_led():
    p_R.stop()
    p_G.stop()
    p_B.stop()
     
def Send_email(mail_content):
    smtpserver = smtplib.SMTP(SMTP_SERVER,SMTP_PORT)
    smtpserver.ehlo()
    smtpserver.starttls()
    smtpserver.ehlo
    smtpserver.login(SMTP_AUTH_USERNAME, SMTP_AUTH_PASSWD)
    header = 'To:' + MAIL_TO + '\n' + 'From: ' + MAIL_FROM + '\n' + 'Subject:'+ MAIL_SUBJECT + '\n'
    msg = header + '\n' + mail_content + '\n\n'
    smtpserver.sendmail(SMTP_AUTH_USERNAME, MAIL_TO, msg)
    smtpserver.close()

def Send_pushover(pushover_content):
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

def Refilling():
    if GPIO.input(Pins["WATER_VALVE"]) == True:
        return True
    else:
        return False
                
def Close_RODI():
    if TEST_FLAG == 0:
        GPIO.output(WATER_VALVE, False) 
        time.sleep(25)
      
def Send_alert(message):
    logger.info(message)                                                # log the event
    if TEST_FLAG == 0:
        Send_email(message)
        Send_pushover(message)        
    else:
        print(message)
        
def Alert_cooldown(probe, timer):
    if '{:%H:%M}'.format(Alarms[probe] + timedelta(minutes=timer)) == '{:%H:%M}'.format(datetime.now()):
        Alarms[probe] = datetime.now()                                  # reset alarm timestamp to reset the counter for next iteration
        return True                                                     # time has come to resend an alarm
    else:
        return False

def Alert(message, probe):                                              # In any event of an alert, inform through log, mail & pushover
    if probe == None:                                                   # If there is no probe declared 
        Send_alert(message)                                             # Just send it, and do not repeat
    else:                                                               # Otherwise, its an alarm and not a stopped alarm
        if Alarms[probe] == 0:                                          # if the alarm has not been seen recently, set a timestamp and alert
            Alarms[probe] = datetime.now()                              # set a timestamp for recurring alarm cooldown
            Send_alert(message)                                         # and alert
        elif Alert_cooldown(probe, 2):                                  # and if we are not in test/debug mode, send the alerts through mail & pushover
            Send_alert("Repeated: " + message)

def Monitor_probe(probe, mesg):
    if GPIO.input(Pins[probe]) == 0 and Alarms[probe] == 0:             # An alert is detected, for the first time on this probe
        Alert(mesg, probe)                                              # Send the initial Alert
        if probe == "WATER_LEAK_DETECTOR_1" or "WATER_LEAK_DETECTOR_2": 
            Audio_alarm()
            if Refilling() == True:
                Close_RODI()
        if probe == "FLOATSW_LOW_WL":                                   # if it is a low or high water alarm, we take corrective actions
            if Refilling() == False:
                Alert("Refilling for " + str(500) + " seconds",probe)   # by refilling            
                if TEST_FLAG == 0:
                    proc = Popen(['python', '/usr/local/python/Aquamonitor/rodi.py', str(500)])
        if probe == "FLOATSW_HIGH_WL":
            Audio_alarm()
            if Refilling() == True:                                     # or by stopping the current refill, if need be
                Alert("High water level in the sump, stopping the current refill.", probe)
                Close_RODI()
        if probe == "FLOATSW_LOW_AWC_WL":
            Alert("The AWC water reserve is nearly empty.", probe)
    if GPIO.input(Pins[probe]) == 1 and Alarms[probe] != 0:             # If we have no longer an alert on the pin but had an alarm previously 
        Alert(mesg + " stopped", probe)                                 # tell all is back to normal
        Alarms[probe] = 0                                               # clear the alarm flag
      
class GracefulKiller:
    kill_now = False
    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)
    def exit_gracefully(self,signum, frame):
        self.kill_now = True

if len(sys.argv) <2:
    print("Too few argument provided")
    sys.exit(2)
else:
    if sys.argv[1] != "status" and sys.argv[1] != "start":
        print("Incorrect argument provided, must be either start or status")
        sys.exit(2)
    
if sys.argv[1] == "start":
        Setup()
        killer = GracefulKiller()
        Alert("Starting Aquamonitor v" + str(VERSION) + " continuous monitoring.", None) # Tell the user we (re)started
        while True:                                                                     # Good old infinite loop, what would we be without them?
            if any(x != 0 for x in Alarms.itervalues()):
                Set_led_color(Colors["RED"])
            elif Refilling() == True:
                Set_led_color(Colors["BLUE"])
            elif GPIO.input(Pins["AWC_PUMP_IN"]) or GPIO.input(Pins["AWC_PUMP_OUT"]):
                Set_led_color(Colors["YELLOW"])
            else:
                Set_led_color(Colors["GREEN"])

            Monitor_probe("WATER_LEAK_DETECTOR_1","Water leak near RO/DI")     # Monitor the various probes and react accordingly if something happens
            Monitor_probe("WATER_LEAK_DETECTOR_2","Water leak under the tank")
            Monitor_probe("FLOATSW_LOW_WL","Low water level in the sump")
            Monitor_probe("FLOATSW_HIGH_WL","High water level in the sump")
            Monitor_probe("FLOATSW_LOW_AWC_WL","Low water in the AWC reserve") 
            time.sleep(LOOP_WAIT_TIMER)                                        # Execute loop only every minute to lower CPU footprint
            if killer.kill_now:
                Alert("Caught a SIGINT or SIGTERM, exiting cleanly", None)
                logger.info("Terminating Aquamonitor")
                Close_RODI()
                GPIO.cleanup()
                Stop_led()
                sys.exit(3)

# Exit code
# 0 : Normal exit
# 1 : Keyboard CTRL+C exit
# 2 : Incorrect arguement provided
# 3 : Sigterm or Sigint
# 4 : Crash
