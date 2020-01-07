#!/usr/bin/python3
# rotary volume and track knob
# This script is compatible with any I2S DAC e.g. from Hifiberry, Justboom, ES9023, PCM5102A
# Please combine with corresponding gpio button script, which handles the button functionality of the encoder
# RPi-Jukebox-RFID/misc/sampleconfigs/gpio-buttons.py.rotaryencoder.sample

# these files belong all together:
# RPi-Jukebox-RFID/scripts/rotary-encoder.py
# RPi-Jukebox-RFID/scripts/rotary_encoder_base.py
# RPi-Jukebox-RFID/misc/sampleconfigs/phoniebox-rotary-encoder.service.stretch-default.sample
# RPi-Jukebox-RFID/misc/sampleconfigs/gpio-buttons.py.rotaryencoder.sample
# See wiki for more info: https://github.com/MiczFlor/RPi-Jukebox-RFID/wiki

#
# circuit diagram for one of two possible encoders (volume), use GPIOs from code below for the tracks
# (capacitors are optionally)
# KY-040 is just one example, typically the pins are named A and B instead of Clock and Data
#
#       .---------------.                      .---------------.
#       |               |                      |               |
#       |        B / DT |------o---------------| GPIO 5        |
#       |               |      |               |               |
#       |       A / CLK |------)----o----------| GPIO 6        |
#       |               |      |    |          |               |
#       |           SW  |------)----)----------| GPIO 3        |
#       |               |      |    |          |               |
#       |           +   |------)----)----------| 3.3V          |
#       |               |      |    |          |               |
#       |           GND |------)----)----------| GND           |
#       |               |      |    |          |               |
#       '---------------'      |    |          '---------------'
#            KY-040            |    |              Raspberry
#                              |    |
#                             ---  ---
#                       100nF ---  --- 100nF
#                              |    |
#                              |    |
#                              |    |
#                             ===  ===
#                             GND  GND
#

import RPi.GPIO as GPIO
from rotary_encoder_base import RotaryEncoder as enc
import os, time, sys
from signal import pause
from subprocess import check_call
import logging

logger = logging.getLogger(__name__)


def rotaryChangeCWVol(steps):
    logger.debug('Call volume up')
    check_call("./scripts/playout_controls.sh -c=volumeup -v="+str(steps), shell=True)

def rotaryChangeCCWVol(steps):
    logger.debug('Call volume down')
    check_call("./scripts/playout_controls.sh -c=volumedown -v="+str(steps), shell=True)

def rotaryChangeCWTrack(steps):
    logger.debug('Call  playernext')
    check_call("./scripts/playout_controls.sh -c=playernext", shell=True)

def rotaryChangeCCWTrack(steps):
    logger.debug('Call  playerprev')
    check_call("./scripts/playout_controls.sh -c=playerprev", shell=True)

APinVol = 17
BPinVol = 22

APinTrack = 23
BPinTrack = 22

GPIO.setmode(GPIO.BCM)
useRotVol = True
useRotTrack  = False

if __name__ == "__main__":
    logger = logging.getLogger()
    logging.basicConfig(level='DEBUG')

    try:
        if useRotVol:
            logger.info('Starting Rotary Volume Encoder with BCM {},BCM {}'.format(APinVol,BPinVol))
            encVol = enc(APinVol, BPinVol, rotaryChangeCWVol, rotaryChangeCCWVol, 0.2)
            encVol.start()
        else:
            encVol = None
        if useRotTrack:
            logger.info('Starting Rotary Track Encoder with BCM {},BCM {}'.format(APinVol,BPinVol))
            encTrack = enc(APinTrack, BPinTrack, rotaryChangeCWTrack, rotaryChangeCCWTrack, 0.05)
            encTrack.start()
        else:
            encTrack = None
        logger.debug('Waiting for interactions')
        pause()
    except KeyboardInterrupt:
        if encVol is not None:
            logger.debug('Stop Rotary Volume Encoder')
            encVol.stop()
        if encTrack is not None:
            logger.debug('Stop Rotary Track Encoder')
            encTrack.stop()
    GPIO.cleanup()
    logger.info("\nExiting rotary encoder decoder\n")
    # exit the application
        #sys.exit(0)
