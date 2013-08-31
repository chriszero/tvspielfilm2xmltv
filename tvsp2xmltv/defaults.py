# -*- coding: utf-8 -*-
import operator
import os
import stat
import configparser

# ugo+rw because may different user work with this file
file_mode = stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH | stat.S_IWOTH

def find_in_path(file_name, path=None):
    """
    Search for file in the defined pathes
    """
    path = path or '/etc/tvspielfilm2xmltv:/etc/vdr/plugins/tvspielfilm2xmltv'
    for directory in path.split(os.pathsep):
        file_path = os.path.abspath(os.path.join(directory, file_name))
        if os.path.exists(file_path):
            return file_path
    return file_name


config = configparser.ConfigParser()
config.read(find_in_path('tvspielfilm2xmltv.ini'))

destination_file = config['DEFAULT']['destination_file']
control_file = config['DEFAULT']['control_file']
grab_today = config['DEFAULT']['grab_today']

sart_map = {
	'SE':'serie', 
	'SP':'movie', 
	'RE':'news', 
	'AND': 'and',
	'U':'undefined'}

channel_map = {
	'ARD':'ard.de',
	'ZDF':'zdf.de',
	'RTL':'rtl.de',
	'SAT1':'sat1.de',
	'PRO7':'prosieben.de',
	'K1':'kabel1.de',
	'RTL2':'rtl2.de',
	'VOX':'vox.de',
	'3SAT':'3sat.de',
	'ARTE':'arte.de',
	'TELE5':'tele5.de',
	'DVIER':'das-vierte.de',
	'CC':'comedy-central.de',
	'DMAX':'dmax.de',
	'SIXX':'sixx.de',
	'RTL-N':'rtl-nitro.de',
	'SAT1G':'sat1-gold.de',
	'SUPER':'superrtl.de',
	'KIKA':'kika.de',
	'NICK':'nickelodeon.de',
	'RIC':'ric.de',
	'WDR':'wdr.de',
	'N3':'ndr.de',
	'BR':'bayern3.de',
	'SWR':'swr.de',
	'HR':'hessen3.de',
	'MDR':'mdr.de',
	'RBB':'rbb.de',
	'PHOEN':'phoenix.de',
	'BRALP':'br-alpha.de',
	'TAG24':'tagesschau24.de',
	'FES':'einsfestival.de',
	'MUX':'einsplus.de',
	'2NEO':'zdfneo.de',
	'2KULT':'zdfkultur.de',
	'ZINFO':'zdfinfo.de',
	'ANIXE':'anixe.de',
	'SKLAR':'sonnenklartv.de',
	'BIBEL':'bibeltv.de',
	'TIMM':'timm.de',
	'CNN':'cnn.de',
	'N24':'n24.de',
	'NTV':'ntv.de',
	'SPORT':'sport1.de',
	'S1PLU':'sport1plus.de',
	'EURO':'eurosport.de',
	'EURO2':'eurosport-2.de',
	'ESPN':'espn-classic-sport.com',
	'NASN':'espn-america.com',
	'SPO-D':'sportdigitaltv.de',
	'DMC':'deluxe-music.de',
	'IMT':'imusic1.de',
	'MTV':'mtv.de',
	'VIVA':'viva.de',
	'VH1':'vh1-classic.uk',
	'ATV':'atv.at',
	'ATV2':'atv2.at',
	'ORF1':'orf1.at',
	'ORF2':'orf2.at',
	'ORF3':'orf3.at',
	'ORFSP':'orf-sport.at',
	'PULS4':'puls4.at',
	'SERVU':'servustv.at',
	'SF1':'sf1.ch',
	'STTV':'star-tv.ch',
	'SF2':'sf2.ch',
	'3PLUS':'3plus.ch',
	'CIN':'sky-cinema.de',
	'CIN1':'sky-cinema-1.de',
	'CIN24':'sky-cinema-24.de',
	'SKY-H':'sky-cinema-hits.de',
	'SKY-A':'sky-action.de',
	'SKY-C':'sky-comedy.de',
	'SKY-E':'sky-emotion.de',
	'SKY-N':'sky-nostalgie.de',
	'MGM':'mgm.de',
	'DCM':'disney-cinemagic.de',
	'SKY3D':'sky-3d.de',
	'SKYAT':'sky-atlantic-hd.de',
	'N-GHD':'national-geographic.de',
	'HDDIS':'discovery-channel.de',
	'HISHD':'history-hd.de',
	'SNHD':'sky-sport-news-hd.de',
	'BULI':'sky-fussball-bundesliga.de',
	'SPO1':'sky-sport-1.de',
	'SPO2':'sky-sport-2.de',
	'SPO-A':'sky-sport-austria.at',
	'HDSPO':'sky-sport-1-hd.de',
	'SHD2':'sky-sport-2-hd.de',
	'SHDE':'sky-sport-extra-hd.de',
	'13TH':'13th-street.de',
	'CLASS':'classica.de',
	'DISNE':'disney-channel.de',
	'DXD':'disney-xd.de',
	'DJUN':'disney-junior.de',
	'FOX':'fox-channel.de',
	'GOLD':'goldstar-tv.de',
	'HEIMA':'heimatkanal.de',
	'MOVTV':'motorvision-tv.de',
	'JUNIO':'junior.de',
	'N-GW':'national-geographic-wild.de',
	'PASS':'rtl-passion.de',
	'RTL-C':'rtl-crime.de',
	'SCIFI':'sci-fi.de',
	'SP-GE':'spiegel-geschichte.de',
	'SKY-K':'sky-krimi.de',
	'TNT-S':'tnt-serie.de',
	'AXN':'axntv.de',
	'AMAX':'animax.de',
	'BIO':'the-biography-channel.de',
	'BOOM':'boomerang-tv.de',
	'C-NET':'cartoon-network.de',
	'HISTO':'history-channel.de',
	'K1CLA':'kabel-eins-classics.de',
	'KINOW':'kinowelt-tv.de',
	'NICKT':'nicktoons.de',
	'ROM':'romance-tv.de',
	'RTL-L':'rtl-living.de',
	'SAT1E':'sat1-emotions.de',
	'TNT-F':'tnt-film.de',
	'SKY-S':'sky-select.de',
	'APLAN':'animal-planet.de',
	'GUSTO':'bongusto.de',
	'E!':'e-entertainment-television.de',
	'GLITZ':'glitz.de',
	'PLANE':'planet.de',
	'PBOY':'playboy.de',
	'PRO7F':'prosieben-fun.de',
	'SILVE':'silverline-tv.de',
	'SPTVW':'spiegel-tv-wissen.de'
}

def get_channel_key(value):
	for name, val in channel_map.items():
		if val == value:
			return name


def write_controlfile(grab_time, grab_days):
	print('Writing Controlfile [{0}, {1}, {2}]'.format(control_file, grab_time, grab_days))
	sorted_x = sorted(channel_map.values(), key=operator.itemgetter(1))
	try:
		f = open(control_file, "w")
		# Set filemode for every written file!
		os.fchmod(f.fileno(), file_mode)
		f.write('file;{0};0;0\n'.format(grab_time))	
		f.write('{0}\n'.format(grab_days))
		for val in sorted_x:
			f.write(val)
			f.write('\n')
			
	finally:
		f.close()
	
