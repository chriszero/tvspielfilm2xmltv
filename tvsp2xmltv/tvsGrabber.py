# -*- coding: utf-8 -*-
import requests
import datetime
import json

from . import model
from . import defaults
from . import logger

class TvsGrabber(object):
	
	def __init__(self):
		self.channel_list = []
		self.grab_days = 1
		self.xmltv_doc = model.XmltvRoot()
		
	
	def _get_update(self):
		"""liefert Infos mit Sender, Senderlogos
	
		"""
	
		url = "http://tvsapi.cellmp.de/getUpdate.php"
		r = requests.get(url)
		r.encoding='utf-8'
		return json.JSONDecoder(strict=False).decode(r.text)
	
	
	def _get_detail(self, prog_id):
		"""Holt die Sendungsdetails für die id ab
	
		"""
	
		payload = {'id': prog_id}
		url = "http://tvsapi.cellmp.de/getDetails.php"
		r = requests.get(url, params=payload)
		r.encoding='utf-8'
		return json.JSONDecoder(strict=False).decode(r.text)
	
	
	def _get_category(self, date, sender=[]):
		"""Holt verfügbare Sendungen
		
		date: das Datum für welche wir die Daten wollen
		sender: Eine Liste mit Sender ID's als string
		wird der Parameter weggelassen werden alle verfügbaren Sender Daten abgeholt
	
		"""
		
		# Build channel array for request
		sender_len = len(sender)
		channel = '['
		for i in range(sender_len):
			channel = channel + '"' + sender[i] + '"'
			if i < sender_len - 1:
				channel = channel + ','
	
		channel = channel + ']'
	
		logger.log('Grabbing Channel "'+channel+'" for date '+date.isoformat())
	
		payload = {'name': 'day', 'channel': channel, 'date': date.isoformat()}
		url = "http://tvsapi.cellmp.de/getCategory_1_3.php"
		try:
			r = requests.get(url, params=payload)
			#print(r.url)
		except requests.exceptions.RequestException:
			logger.log("Failed to request", logger.MESSAGE)
			return []
		r.encoding='utf-8'
		## r.json() wollte bei mir so überhaupt nicht
		## es gab:
		## 18:24:40 ERROR::tvspielfilm2xmltv.py: TypeError('str() argument 2 must be str, not None',)
		try:
			return json.JSONDecoder(strict=False).decode(r.text)
		except TypeError:
			logger.log("Failed to decode json", logger.MESSAGE)
			return []
	
	def start_grab(self):
		
		#for name, channel_id in defaults.channel_map.items():
		for chan_id in self.channel_list:
			tvsp_id = defaults.get_channel_key(chan_id)
			chan = model.Channel(chan_id, tvsp_id)
			self.xmltv_doc.append_element(chan)
	
		#for name, channel_id in defaults.channel_map.items():
		for chan_id in self.channel_list:
			tvsp_id = defaults.get_channel_key(chan_id)
			
			date = datetime.date.today()
			if not defaults.grab_today:
				date = date + datetime.timedelta(days=1)
			
			for i in range(self.grab_days):
				day = date + datetime.timedelta(days=i)
				self.__grab_day(day, tvsp_id)
				
		#print("Finished")
	
	def add_channel(self, channel):
		self.channel_list.append(channel)
		
	
	def save(self):
		self.xmltv_doc.write_xml(defaults.destination_file)
	
	def __grab_day(self, date, channel):
		retry = 0
		data = self._get_category(date, [channel])
		for s in data:
			# Im Falle eines Fehlers beim grabben
			try:			
				progData = self._get_detail(s['sendungs_id'])
				prog = model.Programme(progData)
				self.xmltv_doc.append_element(prog)
			except Exception as e:
				logger.log("Failed to fetch Details for " + s['sendungs_id'] + " on Channel " + channel, logger.MESSAGE)
				logger.log("Pausing for 30 seconds.", logger.MESSAGE)
				from time import sleep
				sleep(30)
	
