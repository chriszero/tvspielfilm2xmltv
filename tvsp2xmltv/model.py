#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime
import os
from xml.etree.ElementTree import Element, ElementTree, SubElement, Comment, TreeBuilder

import pytz

from . import defaults
from . import pictureLoader


# Create Timezone according to our source
tz_ger = pytz.timezone('Europe/Berlin')


class Programme(object):
    def __init__(self, json, channel_id=None, loadPictures=False):

        self.loadPictures = loadPictures
        self.channel_id = channel_id
        self.json = json

        self.programme_id = self.__get_value('id')
        self.broadcaster_id = self.__get_value('broadcasterId')
        self.broadcaster_name = self.__get_value('broadcasterName')
        self.starttime = self.__get_value('timestart')
        self.endtime = self.__get_value('timeend')
        self.year = self.__get_value('year')
        self.programme_length = self.__get_value('lengthNetAndGross')
        self.title_de = self.__get_value('title')
        self.title_orig = self.__get_value('originalTitle')
        self.country = self.__get_value('country')
        self.genre = self.__get_value('genre')
        self.text = self.__get_value('text')

        self.review = self.__get_value('conclusion')
        self.director = self.__get_value('director')
        self.actors = self.__get_value('actors')

        self.anchorman = self.__get_value('anchorman')
        self.studio_guests = self.__get_value('studio_guests')

        self.subline = self.__get_value('subline')
        self.episode_title = self.__get_value('episodeTitle')
        self.season_number = self.__get_value('seasonNumber')
        self.epsiode_number = self.__get_value('episodeNumber')
        self.sart_id = self.__get_value('sart_id')  # SendungsArt  SE, RE, ... ?

        #self.wiederhol_hinweis = self.__get_value('repeatHint') # Wiederholungshinweis

        self.sz_neu = self.__get_value('isNew')
        self.sz_hdtv = self.__get_value('isHDTV')
        self.is_live = self.__get_value('isLive')
        self.rating = self.__get_value('fsk')
        self.tip_of_the_day = self.__get_value('isTipOfTheDay')
        self.star_rating = self.__get_value('thumbId')

        self.images = self.__get_value('images')

    def __get_value(self, key):
        if key in self.json:
            return self.json[key]
        else:
            return None

    def to_string(self):
        print(self.episode_title)
        print(self.title_de)

    def get_absolute_starttime(self):
        d = datetime.datetime.fromtimestamp(self.starttime)
        new_d = tz_ger.localize(d)
        return new_d

    def get_absolute_endtime(self):
        d = datetime.datetime.fromtimestamp(self.endtime)
        new_d = tz_ger.localize(d)
        return new_d

    def __format_date_for_xmltv(self, date):
        return date.strftime("%Y%m%d%H%M%S %z")


    def get_xml(self):
        """Erstellt das XML-Element für die Sendung
        """
        start = self.get_absolute_starttime()
        stop = self.get_absolute_endtime()

        if not self.channel_id:
            self.channel_id = defaults.channel_map[self.broadcaster_id]

        programme = Element('programme',
                            {
                                'start': self.__format_date_for_xmltv(start),
                                'stop': self.__format_date_for_xmltv(stop),
                                'channel': self.channel_id
                            })

        programme.append(Comment(' pid = {0} '.format(self.programme_id)))

        tmp = SubElement(programme, "title", {'lang': 'de'})
        tmp.text = self.title_de

        if self.title_orig:
            tmp = SubElement(programme, "title")
            tmp.text = self.title_orig

        # Folgentitel oder Untertitel
        if self.episode_title:
            tmp = SubElement(programme, 'sub-title')
            tmp.text = self.episode_title
        elif self.subline:
            tmp = SubElement(programme, 'sub-title')
            tmp.text = self.subline

        if self.text:
            tmp = SubElement(programme, "desc", {'lang': 'de'})
            tmp.text = self.text

        if self.actors or self.director or self.anchorman:
            programme.append(self.__generate_credits())

        if self.year:
            tmp = SubElement(programme, 'date')
            tmp.text = str(self.year)

        tmp = SubElement(programme, 'category', {'lang': 'de'})
        tmp.text = self.genre

        if defaults.sart_map.has_key(self.sart_id):
            tmp = SubElement(programme, 'category')
            tmp.text = defaults.sart_map[self.sart_id]

        if defaults.thumb_id_map.has_key(self.star_rating):
            tmp = SubElement(programme, 'star-rating')
            tmp.text = '{0} / 3'.format(defaults.thumb_id_map[self.star_rating])

        if self.programme_length and len(self.programme_length.split('/')) > 0:
            tmp = SubElement(programme, 'length', {'units': 'minutes'})
            tmp.text = self.programme_length.split('/')[1]

        if self.loadPictures and self.images:
            # Add images if available
            picLoader = pictureLoader.PictureLoader(self)
            iconTags = picLoader.get_xml()

            if len(iconTags) > 0:
                for icon in iconTags:
                    programme.append(icon)

        if self.country:
            tmp = SubElement(programme, 'country')
            tmp.text = self.country

        try:
            if self.epsiode_number:
                text = self.__generate_xmltv_ns()
                tmp = SubElement(programme, 'episode-num', {'system': 'xmltv_ns'})
                tmp.text = text
        except ValueError:
            tmp = SubElement(programme, 'episode-num', {'system': 'onscreen'})
            tmp.text = self.epsiode_number
            pass

        if self.sz_hdtv:
            tmp = SubElement(programme, 'video')
            tmp = SubElement(tmp, 'quality')
            tmp.text = 'HDTV'

        if self.sz_neu:
            SubElement(programme, 'new')

        if self.rating:
            rating = SubElement(programme, 'rating', {'system': 'FSK'})
            tmp = SubElement(rating, 'value')
            tmp.text = str(self.rating)

        if self.review:
            tmp = SubElement(programme, 'review', {'type': 'text'})
            tmp.text = self.review

        return programme


    def __generate_xmltv_ns(self):
        # ToDo: folgen mit 111;112 & 1-3 behandeln (Doppelfolgen?) Prüfen ob nur Zahlen im String sind
        if self.epsiode_number:
            ep = int(self.epsiode_number) - 1
        else:
            ep = ""

        if self.season_number:
            st = int(self.season_number) - 1
        else:
            st = ""

        ns = "{0}.{1}.".format(st, ep)
        return ns

    def __generate_credits(self):
        credits_element = Element("credits")
        if self.director:
            tmp = SubElement(credits_element, "director")
            tmp.text = self.director

        if self.actors:
            for entry in self.actors:
                pair = entry.items()[0]
                tmp = SubElement(credits_element, "actor", {'role': pair[0]})
                tmp.text = pair[1]

        if self.anchorman:
            tmp = SubElement(credits_element, 'presenter')
            tmp.text = self.anchorman

        if self.studio_guests:
            for d in self.studio_guests:
                tmp = SubElement(credits_element, "guest")
                tmp.text = d

        return credits_element


class Channel(object):
    def __init__(self, chanid, name):
        self.channel_id = chanid
        self.display_name = name

    def get_xml(self):
        chan = Element('channel', {'id': self.channel_id})
        tmp = SubElement(chan, 'display-name', {'lang': 'de'})
        tmp.text = self.display_name
        return chan


class XmltvRoot(object):
    def __init__(self):
        self.root = Element('tv', {'generator-info-name': 'tvspielfilm2xmltv grabber'})

    def append_element(self, xml):
        self.root.append(xml.get_xml())

    def get_xml(self):
        return self.root

    def write_xml(self, filename):
        # Delete first because user have no permission to change attrib from files other users own
        if os.path.exists(filename):
            os.remove(filename)
        file = open(filename, 'wb')
        # Set filemode for every written file!
        os.fchmod(file.fileno(), defaults.file_mode)

        # Create an ElementTree object from the root element
        ElementTree(self.root).write(file, encoding="UTF-8", xml_declaration=True)
        file.close()
