#!/usr/bin/python

import sys, time, RPi.GPIO as GPIO, os, logging, pigpio
from time import gmtime, strftime
AWC_PUMP_OUT=9
AWC_PUMP_IN=11

if not len(sys.argv) > 1:
   print "You must provide one numerical argument to this function (duration in seconds). Exiting."
   sys.exit()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler('/var/log/awc.log')
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(message)s',"%Y-%m-%d %H:%M:%S")
handler.setFormatter(formatter)
logger.addHandler(handler)
GPIO.setmode(GPIO.BCM)
GPIO.setup(AWC_PUMP_IN, GPIO.OUT)
GPIO.setup(AWC_PUMP_OUT, GPIO.OUT)
    
def AWC(duration):
    logger.info("Starting a micro AWC")
    logger.info("Flushing")
    GPIO.output(AWC_PUMP_OUT, True)
    time.sleep(duration)
    GPIO.output(AWC_PUMP_OUT, False)
    logger.info("Filling")
    GPIO.output(AWC_PUMP_IN, True)
    time.sleep(duration)
    GPIO.output(AWC_PUMP_IN, False)
    logger.info("End of micro AWC")

if sys.argv[1].isdigit():
    try:
      logger.info("Executing a micro AWC for " + sys.argv[1] + " seconds")
      logger.handlers[0].flush()
      AWC(int(sys.argv[1]))
      sys.exit()
    except KeyboardInterrupt:                                 # cleanup in case we changed our minds and canceled the refill with CTRL+C
      GPIO.output(AWC_PUMP_OUT, False)
      GPIO.output(AWC_PUMP_IN, False)
      sys.exit()
    else:
      print("Value is neither close or a time expressed in seconds")
