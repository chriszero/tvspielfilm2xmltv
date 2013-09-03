#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime
import json

import requests

from . import model
from . import defaults
from . import logger
from . import pictureLoader


class TvsGrabber(object):
    def __init__(self):
        self.headers = {
            'Connection': 'Keep-Alive',
            'User-Agent': None
        }
        self.channel_list = []
        self.grab_days = 1
        self.pictures = False
        self.xmltv_doc = model.XmltvRoot()


    def _get_update(self):
        """liefert Infos mit Sender, Senderlogos

        """

        url = "http://tvsapi.cellmp.de/getUpdate.php"
        r = requests.get(url, headers=self.headers)
        r.encoding = 'utf-8'
        logger.log(r.url, logger.DEBUG)
        return json.JSONDecoder(strict=False).decode(r.text)


    def _get_detail(self, prog_id):
        """Holt die Sendungsdetails für die id ab

        """
        logger.log("_get_detail({0})".format(prog_id), logger.DEBUG)
        payload = {'id': prog_id}
        url = "http://tvsapi.cellmp.de/getDetails.php"
        r = requests.get(url, params=payload, headers=self.headers)
        r.encoding = 'utf-8'
        logger.log(r.url, logger.DEBUG)
        return json.JSONDecoder(strict=False).decode(r.text)


    def _get_category(self, date, sender=[]):
        """Holt verfügbare Sendungen

        date: das Datum für welche wir die Daten wollen
        sender: Eine Liste mit Sender ID's als string
        wird der Parameter weggelassen werden alle verfügbaren Sender Daten abgeholt

        """
        logger.log("_get_category({0}, {1})".format(date, sender), logger.DEBUG)
        # Build channel array for request
        sender_len = len(sender)
        channel = '['
        for i in range(sender_len):
            channel = channel + '"' + sender[i] + '"'
            if i < sender_len - 1:
                channel = channel + ','

        channel = channel + ']'

        logger.log('Grabbing Channel "' + channel + '" for date ' + date.isoformat())

        payload = {'name': 'day', 'channel': channel, 'date': date.isoformat()}
        url = "http://tvsapi.cellmp.de/getCategory_1_3.php"
        try:
            r = requests.get(url, params=payload, headers=self.headers)
        #print(r.url)
        except requests.exceptions.RequestException:
            logger.log("Failed to request", logger.MESSAGE)
            return []
        r.encoding = 'utf-8'
        logger.log("Grabbing channel {0}".format(r.url), logger.DEBUG)
        try:
            return json.JSONDecoder(strict=False).decode(r.text)
        except TypeError:
            logger.log("Failed to decode json", logger.DEBUG)
            return []

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
                tvsp_id = defaults.combination_channels[chan_id]

            for i in range(self.grab_days):
                day = date + datetime.timedelta(days=i)
                self.__grab_day(day, tvsp_id, chan_id)

        #print("Finished")
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
        if isinstance(tvsp_id, str):
            tvsp_id = [tvsp_id]
        data = self._get_category(date, [] + tvsp_id)
        for s in data:
        # Im Falle eines Fehlers beim grabben
                try:
                    progData = self._get_detail(s['sendungs_id'])
                    logger.log("__grab_day:progData\n {0}".format(progData), logger.DEBUG)
                    prog = model.Programme(progData, channel_id, self.pictures)
                    self.xmltv_doc.append_element(prog)
                except Exception as e:
                    logger.log("Failed to fetch Details for " + s['sendungs_id'] + " on Channel " + tvsp_id, logger.MESSAGE)
                    logger.log("Pausing for 30 seconds.", logger.MESSAGE)
                    from time import sleep
                    sleep(30)
                    if defaults.debug:
                        raise
