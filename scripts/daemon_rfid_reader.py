#!/usr/bin/env python2

import subprocess
import os, time
import logging
from Reader import Reader

# create and configure main logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
# create console handler with a higher log level
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)#DEBUG)
# create formatter and add it to the handler
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
# add the handler to the logger
logger.addHandler(handler)
reader = Reader()

# get absolute path of this script
dir_path = os.path.dirname(os.path.realpath(__file__))

# vars for ensuring delay between same-card-swipes
same_id_delay = 0
previous_id = ""
previous_time = time.time()
logger.info('Dir_path: {}'.format( dir_path))

logger.info('Ready to read a card')
while True:
        # reading the card id
        # NOTE: it's been reported that KKMOON Reader might need the following line altered.
        # Instead of:
        # cardid = reader.reader.readCard()
        # change the line to:
        #cardid = reader.readCard()
        # See here for (German ;) details:
        # https://github.com/MiczFlor/RPi-Jukebox-RFID/issues/551
        cardid = reader.reader.readCard()
        try:
            # start the player script and pass on the cardid
            if cardid != None:
                dt = time.time()-previous_time
                if (cardid != previous_id or dt>= same_id_delay):
                    logger.info('cardid: {}'.format(cardid))
                    subprocess.call([dir_path + '/rfid_trigger_play.sh --cardid=' + cardid], shell=True)
                    previous_id = cardid
                    previous_time = time.time()
                else:
                    logger.info('ignoring card {cardid}, {dt} < {same_id_delay}'.format(
                                cardid=cardid,
                                dt=dt,
                                same_id_delay=same_id_delay))
            else:
                logger.debug('no valid card id found: {}'.format(cardid))

        except OSError as e:
            logger.exception("Execution failed: {}".format(e))
