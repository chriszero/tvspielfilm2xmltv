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
        details = json['details']

        self.sendungs_id = details['sendungs_id']
        self.sender_id = details['sender_id']
        self.sendername = details['sendername']
        self.sendungstag = details['sendungstag']
        self.starttime = details['starttime']
        self.endtime = details['endtime']
        self.jahr = details['jahr']
        self.filmlaenge = details['filmlaenge']

        self.title_de = details['titel']
        self.title_orig = details['originaltitel']
        self.vorspann = details['vorspann']
        self.land = details['land']
        self.genre = details['genre']
        self.text = details['text']
        self.fazit = details['fazit']

        self.regisseur = details['regisseur']  # Kommagetrennt
        self.darsteller = details['darsteller']  # Semikolongetrennte Liste
        self.moderator = details['moderator']  # Kommagetrennt
        self.studio_gaeste = details['studio_gaeste']  # Kommagetrennt

        self.untertitel = details['untertitel']
        self.folgentitel = details['folgentitel']
        self.staffel_nr = details['staffel_nr']
        self.folge = details['folge']

        self.sart_id = details['sart_id']  # SendungsArt  SE, RE, ... ?
        self.wiederhol_hinweis = details['wiederhol_hinweis']  # Wiederholungshinweis

        self.sz_neu = details['sz_neu'] == 'J'
        self.sz_hdtv = details['sz_hdtv'] == 'J'

        self.gallery_lo = json['gallery']
        self.gallery_hi = json['gallery_hi']

    # self.parse_json(json)


    def to_string(self):
        print(self.folgentitel)
        print(self.title_de)

    def get_absolute_starttime(self):
        d = datetime.datetime.strptime(self.sendungstag + ' ' + self.starttime, '%Y-%m-%d %H:%M')
        new_d = tz_ger.localize(d)
        return new_d

    def get_absolute_endtime(self):
        d = datetime.datetime.strptime(self.sendungstag + ' ' + self.endtime, '%Y-%m-%d %H:%M')
        new_d = tz_ger.localize(d)
        return new_d

    def __format_date_for_xmltv(self, date):
        return date.strftime("%Y%m%d%H%M%S %z")


    def get_xml(self):
        """Erstellt das XML-Element für die Sendung
        """
        start = self.get_absolute_starttime()
        stop = self.get_absolute_endtime()

        # Tagesgrenze überschritten...
        if stop < start:
            stop = stop + datetime.timedelta(days=1)

        if not self.channel_id:
            self.channel_id = defaults.channel_map[self.sender_id]

        programme = Element('programme',
                            {
                                'start': self.__format_date_for_xmltv(start),
                                'stop': self.__format_date_for_xmltv(stop),
                                'channel': self.channel_id
                            })

        programme.append(Comment(' pid = {0} '.format(self.sendungs_id)))

        tmp = SubElement(programme, "title", {'lang': 'de'})
        tmp.text = self.title_de

        if self.title_orig:
            tmp = SubElement(programme, "title")
            tmp.text = self.title_orig

        # Folgentitel oder Untertitel
        if self.folgentitel:
            tmp = SubElement(programme, 'sub-title')
            tmp.text = self.folgentitel
        elif self.untertitel:
            tmp = SubElement(programme, 'sub-title')
            tmp.text = self.untertitel

        if self.text:
            tmp = SubElement(programme, "desc", {'lang': 'de'})
            tmp.text = self.text

        if self.darsteller or self.regisseur or self.moderator:
            programme.append(self.__generate_credits())

        if self.jahr:
            tmp = SubElement(programme, 'date')
            tmp.text = self.jahr

        tmp = SubElement(programme, 'category', {'lang': 'de'})
        tmp.text = self.genre

        if defaults.sart_map.has_key(self.sart_id):
            tmp = SubElement(programme, 'category')
            tmp.text = defaults.sart_map[self.sart_id]

        if self.filmlaenge and len(self.filmlaenge.split('/')) > 0:
            tmp = SubElement(programme, 'length', {'units': 'minutes'})
            tmp.text = self.filmlaenge.split('/')[1]

        if self.loadPictures:
            # Add images if available
            picLoader = pictureLoader.PictureLoader(self)
            iconTags = picLoader.get_xml()

            if len(iconTags) > 0:
                for icon in iconTags:
                    programme.append(icon)


        if self.land:
            tmp = SubElement(programme, 'country')
            tmp.text = self.land

        try:
            if self.folge:
                tmp = SubElement(programme, 'episode-num', {'system': 'xmltv_ns'})
                tmp.text = self.__generate_xmltv_ns()
        except ValueError:
            pass

        if self.sz_hdtv:
            tmp = SubElement(programme, 'video')
            tmp = SubElement(tmp, 'quality')
            tmp.text = 'HDTV'

        if self.sz_neu:
            SubElement(programme, 'new')

        if self.fazit:
            tmp = SubElement(programme, 'review', {'type': 'text'})
            tmp.text = self.fazit

        return programme


    def __generate_xmltv_ns(self):
        # ToDo: folgen mit 111;112 behandeln (Doppelfolgen?) Prüfen ob nur Zahlen im String sind
        if self.folge:
            ep = int(self.folge) - 1
        else:
            ep = ""

        if self.staffel_nr:
            st = int(self.staffel_nr) - 1
        else:
            st = ""

        ns = "{0}.{1}.".format(st, ep)
        return ns

    def __generate_credits(self):
        credits_element = Element("credits")
        if self.regisseur:
            tmp = SubElement(credits_element, "director")
            tmp.text = self.regisseur

        if self.darsteller:
            td = self.darsteller.split(';')
            for d in td:
                try:
                    x = d.split('(')
                    if len(x) >= 1:
                        tmp = SubElement(credits_element, "actor", {'role': x[1].strip(' )')})
                        tmp.text = x[0].strip()
                    # keine Rolle angegeben
                    else:
                        tmp = SubElement(credits_element, "actor")
                        tmp.text = d.strip()
                except IndexError:
                    pass

        if self.moderator:
            tmp = SubElement(credits_element, 'presenter')
            tmp.text = self.moderator

        #if self.studio_gaeste:
        #	td = self.studio_gaeste.split(',')
        #	for d in td:
        #		tmp = SubElement(credits_element, "guest")
        #		tmp.text = d.strip()

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
