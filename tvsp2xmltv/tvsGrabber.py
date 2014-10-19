#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime

import requests

from . import model
from . import defaults
from . import logger
from . import pictureLoader


class TvsGrabber(object):
    def __init__(self):
        self.headers = {
            'Connection': 'close',
            'User-Agent': 'Nexus 5; Android 4.4.4; de_DE'
        }
        self.channel_list = []
        self.grab_days = 1
        self.pictures = False
        self.xmltv_doc = model.XmltvRoot()


    def _get_channel(self, date, tvsp_id):
        #broadcast/list/K1/2014-10-18
        url = "http://tvs3.cellular.de/broadcast/list/{0}/{1}".format(tvsp_id, date)
        r = requests.get(url, headers=self.headers)
        r.encoding = 'utf-8'
        if r.status_code == requests.codes.ok:
            logger.log(r.url, logger.DEBUG)
            return r.json()
        else:
            logger.log('{0} returned status code {1}'.format(r.url, r.status_code), logger.WARNING)

    def start_grab(self):

        # single channels
        for chan_id in self.channel_list:
            tvsp_id = defaults.get_channel_key(chan_id)
            if tvsp_id:
                chan = model.Channel(chan_id, tvsp_id)
                self.xmltv_doc.append_element(chan)

        # combination channels
        for chan_id in self.channel_list:
            if defaults.combination_channels.has_key(chan_id):
                name = ';'.join(str(x) for x in defaults.combination_channels[chan_id])
                chan = model.Channel(chan_id, name)
                self.xmltv_doc.append_element(chan)

        # single channels
        for chan_id in self.channel_list:
            tvsp_id = defaults.get_channel_key(chan_id)

            date = datetime.date.today()
            if not defaults.grab_today:
                date = date + datetime.timedelta(days=1)

            # combination channel
            if not tvsp_id:
                if chan_id in defaults.combination_channels:
                    tvsp_id = defaults.combination_channels[chan_id]
                else:
                    logger.log("Channel {0} not in channel map.".format(chan_id), logger.WARNING)
                    continue

            for i in range(self.grab_days):
                day = date + datetime.timedelta(days=i)
                self.__grab_day(day, tvsp_id, chan_id)

        pictureLoader.cleanup_images()

    def add_channel(self, channel):
        if isinstance(channel, str):
            self.channel_list.append(channel)
        elif isinstance(channel, list):
            self.channel_list += channel

    def save(self):
        self.xmltv_doc.write_xml(defaults.destination_file)

    def __grab_day(self, date, tvsp_id, channel_id):
        retry = 0
        data = self._get_channel(date, tvsp_id)
        for s in data:
        # Im Falle eines Fehlers beim grabben
            try:
                prog = model.Programme(s, channel_id, self.pictures)
                self.xmltv_doc.append_element(prog)
            except Exception as e:
                logger.log("Failed to fetch Channel " + tvsp_id + " at " + date, logger.WARNING)
                logger.log(e, logger.WARNING)
                if defaults.debug:
                    raise
