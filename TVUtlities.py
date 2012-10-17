from rankyourfavs.rankfavs.models import *
from django.template import Context, loader, RequestContext
from django.shortcuts import render_to_response

from lxml import html
from lxml.etree import tostring
from lxml import objectify
import lxml.html
import urllib, urllib2
import httplib2
import os
#import simplejson
import urlparse
from exceptions import IOError
import Image
import math, operator
import math, operator
import urlparse, urllib
import pickle
import cStringIO
import ImageFile
from PIL import ImageOps
#from sets import Set

def getiMDBTopTVShows():
	tvids = set([])
	h = httplib2.Http()
	for i in range(0,1000,51):
		
		print i
		url = 'http://www.imdb.com/search/title?num_votes=1000,&title_type=tv_series&sort=num_votes&start='+str(i)#100'#'&sort=num_votesdesc&start=' + str(offset) + '&title_type=tv_series/'
		print url
		headers = {
			'User-Agent' : " Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:15.0) Gecko/20100101 Firefox/15.0.1",
			'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
			'Accept-Encoding':	'gzip, deflate',
			'Accept-Language': 'en-us,en;q=0.5',
			'Connection':	'Keep-Alive',
			'Host':	'www.imdb.com',
			'Referer':	'http://www.imdb.com/',
		}
		data=""

		response, content = h.request(url,"GET")#headers=headers)
	#	print content

		root = html.fromstring(content)
		for i in root.iterlinks():
			link = i[2].split("title/tt")
			if len(link) > 1:
				id = link[1].split("/")[0]
				if id not in tvids:
					tvids.add(id)
	print tvids
	for i in tvids:
		try:
			tvshow = TVshow.objects.get(imdb_id=i)
		except:
			url = 'http://www.thetvdb.com/api/GetSeriesByRemoteID.php?imdbid=' + str(i) + ''
			response,content = h.request(url,"GET")
			data = objectify.fromstring(content)
			try:
				tvdbid = data.Series.seriesid
				firstaired = data.Series.FirstAired
				name = data.Series.SeriesName
				try:
					zap2itid = data.Series.zap2it_id
				except:
					zap2itid = None
				tvshow = TVshow(title = name, tvdb_id = tvdbid, imdb_id = i, zap2it_id = zap2itid, first_aired = firstaired)
				tvshow.save()
			except:
				print "no data"
				print i

def getPosters():
	tvshows = TVshow.objects.all()
	h = httplib2.Http()
	for tv in tvshows:
		tv.images = getImages(tv.tid)
		tv.save()
		print "tv.tid {} images ".format(tv.tid,tv.images)
		makeTVThumb(tv.tid)
		if False:# tv.images == 0:
			
			url = "http://thetvdb.com/api/4144331619000000/series/" + str(tv.tvdb_id) + "/banners.xml"
			response,content = h.request(url,"GET")
			try:
				data = objectify.fromstring(content)
				c=1
				for Banner in data.Banner:
				
					if Banner.BannerType == "poster" and c < 5:
						url = "http://www.thetvdb.com/banners/" + Banner.BannerPath
						c += getPoster(url,tv.tid,c)
					
					
					
				tv.images = c-1
				tv.save()
			except:
				print "xml problem"
			


def makeTVThumb(id):
	dir = "/Users/Jason/tvshow/thumb"
	if not os.path.exists(dir):
	    os.makedirs(dir)
	if not (os.path.isfile(dir+str(id)+".jpg")):
		dir = "/Users/Jason/tvshow/" + str(id) + "/"
		file = dir+"1.jpg"
		count = 2
		while not (os.path.isfile(file)): 
			file = dir+str(count)+".jpg"
			count += 1
			if count>20:
				break
		if count < 20:
			image = Image.open(file)
	
			thumb = ImageOps.fit(image,(80,80),Image.ANTIALIAS,0,(0,0))
			thumb.save("/Users/Jason/tvshow/thumb/" + str(id)+".jpg","JPEG",optimize=True)





def getImages(id):
	dir = "/Users/Jason/tvshow/" + str(id) + "/"
	if not os.path.exists(dir):
	    os.makedirs(dir)
	images = 0
	for i in range(1,20):
		file = "/Users/Jason/tvshow/" + str(id) + '/' + str(i) + ".jpg"
		if not (os.path.isfile(file)):
			images = i
			break
	images -= 1
	print images
	return images

def getPoster(link,id,c):
	t=100
	dir = "/Users/Jason/tvshow/" + str(id) + "/"
	if not os.path.exists(dir):
	    os.makedirs(dir)

	file = "/Users/Jason/tvshow/" + str(id) + '/' + str(c) + ".jpg"
	print "postering"
	while (os.path.isfile(file)):
		c+=1
		file = "/Users/Jason/tvshow/" + str(id) + '/' + str(c) + ".jpg"
		print file
		
	
	if not (os.path.isfile(file)):

		print file
		image = urllib.URLopener()
		try:
			image.retrieve(link, "/Users/Jason/tmp/tmp" + str(t) +".jpg")
			im = Image.open("/Users/Jason/tmp/tmp" + str(t) + ".jpg")
			print im.size

			if im.size[1]>501:
				print "saved"
				try:
					ImageFile.MAXBLOCK = im.size[0] * im.size[1]
					im.save(file,"JPEG",optimize=True)
				except IOError:
					im.save(file, "JPEG")
				return 1		
			
		except:
			return 0
	return 0
