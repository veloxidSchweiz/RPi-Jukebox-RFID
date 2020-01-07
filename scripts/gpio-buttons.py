#!/usr/bin/python3
from gpiozero import Button
from signal import pause
from subprocess import check_call
from time import sleep
import logging
logger = logging.getLogger(__name__)

# This script will block any I2S DAC e.g. from Hifiberry, Justboom, ES9023, PCM5102A
# due to the assignment of GPIO 19 and 21 to a buttons

# 2018-10-31
# Added the function on holding volume + - buttons to change the volume in 0.3s interval
#
# 2018-10-15
# this script has the `pull_up=True` for all pins. See the following link for additional info:
# https://github.com/MiczFlor/RPi-Jukebox-RFID/issues/259#issuecomment-430007446
#
# 2017-12-12
# This script was copied from the following RPi forum post:
# https://forum-raspberrypi.de/forum/thread/13144-projekt-jukebox4kids-jukebox-fuer-kinder/?postID=312257#post312257
# I have not yet had the time to test is, so I placed it in the misc folder.
# If anybody has ideas or tests or experience regarding this solution, please create pull requests or contact me.

jukebox4kidsPath = "/home/pi/RPi-Jukebox-RFID"

def def_shutdown():
    logger.debug('Call Shutdown')
    check_call(jukebox4kidsPath+"/scripts/playout_controls.sh -c=shutdown", shell=True)

def def_butVolU():
    logger.debug('Call volumeup')
    check_call(jukebox4kidsPath+"/scripts/playout_controls.sh -c=volumeup", shell=True)

def def_butVolD():
    logger.debug('Call volumedown')
    check_call(jukebox4kidsPath+"/scripts/playout_controls.sh -c=volumedown", shell=True)

def def_butVol0():
    logger.debug('Call mute')
    check_call(jukebox4kidsPath+"/scripts/playout_controls.sh -c=mute", shell=True)

def def_butNext():
  for x in range(0, 19):
    if butNext.is_pressed == True :
      sleep(0.1)
    else:
      logger.debug('Call playernext')
      check_call(jukebox4kidsPath+"/scripts/playout_controls.sh -c=playernext", shell=True)
      break

def def_contrastup():
    if butPrev.is_pressed == True :
        logger.debug('Touch o4p_overview.temp')
        check_call("/usr/bin/touch /tmp/o4p_overview.temp", shell=True)
    else:
        logger.debug('Call contrast up')
        check_call("/usr/bin/python3 /home/pi/oled_phoniebox/scripts/contrast/contrast_up.py", shell=True)

def def_contrastdown():
    if butNext.is_pressed == True :
        logger.debug('Touch o4p_overview.temp')
        check_call("/usr/bin/touch /tmp/o4p_overview.temp", shell=True)
    else:
        logger.debug('Call contrast down')
        check_call("/usr/bin/python3 /home/pi/oled_phoniebox/scripts/contrast/contrast_down.py", shell=True)

def def_butPrev():
    for x in range(0, 19):
        if butPrev.is_pressed == True :
            sleep(0.1)
        else:
            logger.debug('Call playerprev')
            check_call(jukebox4kidsPath+"/scripts/playout_controls.sh -c=playerprev", shell=True)
            break

def def_butHalt():
    logger.debug('Call playerpause')
    check_call(jukebox4kidsPath+"/scripts/playout_controls.sh -c=playerpause", shell=True)

#shut = Button(3, hold_time=2)
butVol0 = Button(13,pull_up=True)
butVolU = Button(16,pull_up=True,hold_time=0.3,hold_repeat=True)
butVolD = Button(19,pull_up=True,hold_time=0.3,hold_repeat=True)
butNext = Button(26,pull_up=True,hold_time=2.0,hold_repeat=False)
butPrev = Button(20,pull_up=True,hold_time=2.0,hold_repeat=False)
butHalt = Button(21,pull_up=True)

#shut.when_held = def_shutdown
butVol0.when_pressed = def_butVol0
butVolU.when_pressed = def_butVolU
#When the Volume Up button was held for more than 0.3 seconds every 0.3 seconds he will call a ra$
butVolU.when_held = def_butVolU
butVolD.when_pressed = def_butVolD
#When the Volume Down button was held for more than 0.3 seconds every 0.3 seconds he will lower t$
butVolD.when_held = def_butVolD
butNext.when_pressed = def_butNext
butNext.when_held = def_contrastup
butPrev.when_pressed = def_butPrev
butPrev.when_held = def_contrastdown
butHalt.when_pressed = def_butHalt

pause()
