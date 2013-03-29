#from rankyourfavs.rankfavs.models import *
# coding=utf-8
import urllib, urllib2, lxml.html, gzip, httplib2
import json
import freebase
import time
import requests
from lxml import etree

from sgmllib import SGMLParser
import urllib2
import urllib

# Define the class that will parse the suggestion XML
class PullSuggestions(SGMLParser):

   def reset(self):
      SGMLParser.reset(self)
      self.suggestions = []
      self.queries = []

   def start_suggestion(self, attrs):
      for a in attrs:
         if a[0] == 'data': self.suggestions.append(a[1])

   def start_num_queries(self, attrs):
      for a in attrs:
         if a[0] == 'int': self.queries.append(a[1])



def getBingPopularity(name):
	name = "\"" + name + "\""
	name = name.encode('utf-8')
		
	query = str(urllib.urlencode({'': name}))
	
	#URLL = 'https://api.datamarket.azure.com/Data.ashx/Bing/SearchWeb/Web?Query=&$top=50&$format=json'
	#URLLL = 'https://api.datamarket.azure.com/Data.ashx/Bing/SearchWeb/v1/Web?Query=%27%22Megan%20Fox%22%27&$top=2&$format=Json'
	URL = 'https://api.datamarket.azure.com/Data.ashx/Bing/Search/v1/Composite?Sources=%27web%2bimage%27&Query=%27' + query + '%27&$top=1&$format=Json'
	
	API_KEY = 'IjEHP77j9n71v8xlb1FOK+S32M0o8jKoaZ0OgU0ypJs='
	
	r = requests.get(URL, auth=('', API_KEY))
	
	#r = requests.get(URL % {'query': query}, auth=('', API_KEY))
	#print json.loads(r.text)
	#r_json = r.json['d']['results']
	return r.json['d']['results'][0]['WebTotal']



def getGoogleSearchVolume(name):
	
	if isinstance(name, str):
		#name = name.encode('utf-8')
		print "str"
		name = unicode(name)
		name = s.decode( 'unicode-escape' )
	query = urllib.urlencode({'q' : name.encode('utf-8')})
	URL = 'http://google.com/complete/search?output=toolbar&%s' % query 
	r = requests.get(URL)
	
	parser = PullSuggestions()
	parser.feed(r.text)
	parser.close()
	time.sleep(1)
	highest = 0
	
	if len(parser.suggestions) == 0:
		return None
	
	for i in range(0,len(parser.suggestions)):
		
		if i in range(0,len(parser.queries)):#try:
			print "%s\t%s" % (parser.suggestions[i], parser.queries[i])
		#	print "%s %s" % (name.lower(),name.lower())
			p = parser.suggestions[i]
			if name.lower() == parser.suggestions[i]:
				return int(parser.queries[i])
				print "%s\t%s" % (parser.suggestions[i], parser.queries[i])
			else:
				if name.lower() in parser.suggestions[i]:#unicode(parser.suggestions[i],errors="replace"):#.encode('utf-8'):#.endcode('utf-8') or name.lower() in parser.suggestions[i]:
					if int(parser.queries[i]) > highest:
						highest = int(parser.queries[i])
		#except:
		#	if highest > 0:
		#		return highest
		#	return None
	if highest > 0:
		return highest
	return None
	


def getTwitterInformation(usernames):
	
	url = 'https://api.twitter.com/1/users/lookup.json?screen_name=%s' % usernames
	
	request = urllib2.Request(url)
	request.add_header('User-Agent',
	                       'Mozilla/5.1 (compatible; MSIE 8.0; Windows NT 6.0)')
	
	search_response = urllib2.urlopen(url)
	search_results = search_response.read()
	results = json.loads(search_results)
	data = {}
	for i in range(0,len(results)):
		data[results[i]['screen_name']] = {}
		data[results[i]['screen_name']]['id'] = results[i]['id']
		data[results[i]['screen_name']]['followers_count'] = results[i]['followers_count']
		data[results[i]['screen_name']]['verified'] = results[i]['verified']
	return data


def getGoogleSearchVolumeTotal(name):
	if isinstance(name, str):
		#name = name.encode('utf-8')
		print "str"
		name = unicode(name)
		name = s.decode( 'unicode-escape' )
	query = urllib.urlencode({'q' : name.encode('utf-8')})
	URL = 'http://google.com/complete/search?output=toolbar&%s' % query 
	r = requests.get(URL)
	
	parser = PullSuggestions()
	parser.feed(r.text)
	parser.close()
	time.sleep(1)
	sum = 0
	
	if len(parser.suggestions) == 0:
		return None
	
	for i in range(0,len(parser.suggestions)):
		
		if i in range(0,len(parser.queries)):#try:
			print "%s\t%s" % (parser.suggestions[i], parser.queries[i])
		#	print "%s %s" % (name.lower(),name.lower())
			p = parser.suggestions[i]
			if name.lower() == parser.suggestions[i]:
				sum += int(parser.queries[i])
				print "%s\t%s" % (parser.suggestions[i], parser.queries[i])
			else:
				if name.lower() in parser.suggestions[i]:#unicode(parser.suggestions[i],errors="replace"):#.encode('utf-8'):#.endcode('utf-8') or name.lower() in parser.suggestions[i]:
					sum += int(parser.queries[i])
		#except:
		#	if highest > 0:
		#		return highest
		#	return None
	if sum > 0:
		return sum
	return None


def getGooglePopularityDepricated(name):
	name = "\"" + name + "\""
	name = name.encode('utf-8')
	query = urllib.urlencode({'q': name, 'userip': "98.118.85.4"})
	
	url = 'http://ajax.googleapis.com/ajax/services/search/web?v=1.0&%s' % query
	request = urllib2.Request(url)
	request.add_header('User-Agent',
	                       'Mozilla/5.1 (compatible; MSIE 8.0; Windows NT 6.0)')
	request.add_header('Referer', 'http://flickchart.com')
	
	search_response = urllib2.urlopen(url)
	search_results = search_response.read()
	results = json.loads(search_results)
	data = results['responseData']
	time.sleep(45)
	try: 
		return data['cursor']['estimatedResultCount']
	except:
		time.sleep(90)
		return None	


def getGooglePopularity(name):
	name = "\"" + name + "\""
	
	name = name.encode('utf-8')
	
	query = urllib.urlencode({'q': name})
	#url = 'http://ajax.googleapis.com/ajax/services/search/web?v=1.0&%s' % query
	url = "http://www.google.com/search?" + query
	
	request = urllib2.Request(url)
	request.add_header('User-Agent',
	                       'Mozilla/5.1 (compatible; MSIE 8.0; Windows NT 6.0)')
	#cookie_jar.add_cookie_header(request)
	time.sleep(8)
	try:
		search_response = urllib2.urlopen(request)
		search_results = search_response.read()
		results = search_results
		
		results = results.split("About")[1].split("results")[0]
		results = results.strip(" ")
		results = results.replace(",", "")
		
		return results
	except urllib2.URLError, e:
		if not hasattr(e, "code"):
			raise
		resp = e
		print "e {} url {}".format(e,url)
		time.sleep(30)
		return None
	#urlsvisited.append(cpurl)	


def getWikipediaLinkFromWikipediaID(id):
	url = "http://en.wikipedia.org/w/api.php?action=query&pageids=" + str(id) + "&format=json"
	headers = {
		'User-Agent' : "Magic Browser",
		'Connection':	'Keep-Alive',
	}
	data=""
	req = urllib2.Request(url, data, headers)
	#urlsvisited.append(cpurl)
	f = urllib2.urlopen(req)
	htmlSource = f.read()
	f.close()
	
	j = json.loads(htmlSource)
	
	wikipedia_link =  j['query']['pages'][str(id)]['title']		
	
	return wikipedia_link


def getFreebaseData(source,value):
	if source == "twitter":
		result = freebase.mqlread({"key": [{ "namespace": "/authority/twitter", "value": value}], 
											 "name": None, 
											 "/people/person/place_of_birth": None, 
											 "/people/person/nationality": [{}], 
											 "/people/person/date_of_birth": None, 
											 "/people/person/gender": None, 
											 "ns0:key": [{}]})
	elif source == 'wikipedia':
		result = freebase.mqlread({"key": [{ "namespace": "/wikipedia/en", "value": value}], 
											 "name": None, 
											 "/people/person/place_of_birth": None, 
											 "/people/person/nationality": [{}], 
											 "/people/person/date_of_birth": None, 
											 "/people/person/gender": None, 
											 "ns0:key": [{}]})
		if result == None:
			result = freebase.mqlread({"key": [{ "namespace": "/wikipedia/en_id", "value": value}], 
												 "name": None, 
												 "/people/person/place_of_birth": None, 
												 "/people/person/nationality": [{}], 
												 "/people/person/date_of_birth": None, 
												 "/people/person/gender": None, 
												 "ns0:key": [{}]})
		return result
	elif source == 'imdb':
		if 'http' in value:
			value = value.split('/name/')[1].split('/')[0]
		return freebase.mqlread({"key": [{ "namespace": "/authority/imdb/name", "value": value}], 
								 "name": None, 
								 "/people/person/place_of_birth": None, 
								 "/people/person/nationality": [{}], 
								 "/people/person/date_of_birth": None, 
								 "/people/person/gender": None, 
								 "ns0:key": [{}]})
	#make sure it was quotekey
	elif source == 'baseballalmanac':
		result = freebase.mqlread({"key": [{ "namespace": "/source/baseball_almanac/players", "value": value}], "name": None, "/people/person/place_of_birth": None, "/people/person/nationality": [{}], "/people/person/date_of_birth": None, "/people/person/profession": [{}], "/people/person/gender": None, "ns0:key": [{}] })
	###add checks to see if empty????
	elif source == 'name':
		return freebase.mqlread({"name": value, "/people/person/place_of_birth": None, "/people/person/nationality": [{}], "/people/person/date_of_birth": None, "/people/person/profession": [{}], "/people/person/gender": None, "ns0:key": [{}] })
	else:
		return None	


def addFromFreebase(freebase):
	real = 0
	person = {}
	p = None
	if freebase != None:
		person['wikipedia_link'] = None
		#Find first instance of wiki and use that, reason being can be more than one link and the first is usually the best
		for i in freebase['ns0:key']:
			if i['namespace'] == '/wikipedia/en':
				person['wikipedia_link'] = str(i['value'])
				real += 1
				break
		#Find rest of links
		for i in freebase['ns0:key']:
			if i['namespace'] == '/authority/imdb/name':
				person['imdb_id'] = int(i['value'].split('nm')[1])
				real += 1
			if i['namespace'] == '/authority/tvrage/person':
				person['tvrage_id'] = int(i['value'])
				real +=1
			if i['namespace'] == '/authority/netflix/role':
				person['netflix_id'] = int(i['value'])
				real += 1
			if i['namespace'] == '/authority/twitter':
				person['twitter'] = str(i['value'])
			if i['namespace'] == '/base/chickipedia/chickipedia_id':
				person['chickipedia_id'] = str(i['value'])
			if i['namespace'] == '/wikipedia/en_id':
				person['wikipedia_id'] = str(i['value'])
	else:
		return None
	print "links {} person is {}".format(real,person)
	
	#If at least one link was found continue adding
	if real>=1 or freebase['/people/person/date_of_birth'] != None:
		#Find if the person is in via their name
		##########Might want to switch to check via DOB to allow for multiple people of same name
		try:
			#,tvrage_id = person['tvrage_id'],netflix_id = person['netflix_id'],imdb_id=person['imdb_id'],wikipedia_link=person['wikipedia_link'],name=freebase['name']
			if 'wikipedia_link' in person:
				p = Person.objects.get(wikipedia_link=person['wikipedia_link'])
			elif 'netflix_id' in person:
				p = Person.objects.get(netflix_id=person['netflix_id'])
			elif 'imdb_id' in person:
				p = Person.objects.get(imdb_id = person['imdb_id'])
			elif 'twitter' in person:
				p = Person.objects.get(twitter=person['twitter'])
			elif 'chickipedia_id' in person:
				p = Person.objects.get(chickipedia_id=person['chickipedia_id'])
			else:
				p = Person.objects.get(name=freebase['name'])
			print "already here"
			
			if 'tvrage_id' in person:
				p.tvrage_id = person['tvrage_id']
			if 'netflix_id' in person:
				p.netflix_id = person['netflix_id']
			if 'imdb_id' in person:
				p.imdb_id = person['imdb_id']
			if 'wikipedia_link' in person:
				p.wikipedia_link = person['wikipedia_link']
			if 'wikipedia_id' in person:
				p.wikipedia_id = person['wikipedia_id']
			if 'chickipedia_id' in person:
				p.chickipedia_id = person['chickipedia_id']
			if 'twitter' in person:
				p.twitter = person['twitter']
			
			p.save()
			return p
		except:
			#The name wasn't there
			#If there is no DOB intialize to really old date
			if freebase['/people/person/date_of_birth'] == None:
				freebase['/people/person/date_of_birth'] = '1000-1-1'
			#If do not have the full dob check to see how much there is
			elif len(freebase['/people/person/date_of_birth'])<8:
				#Only have year
				if len(freebase['/people/person/date_of_birth']) <5:
					freebase['/people/person/date_of_birth'] += "-01-01"
				#Have month but no date
				else:
					freebase['/people/person/date_of_birth'] += "-01"
			if freebase['/people/person/gender'] == None:
				freebase['/people/person/gender'] = "Unknown"
			
			p = None
			p = Person(name=freebase['name'],gender=freebase['/people/person/gender'],
						dob=freebase['/people/person/date_of_birth'],)
			if 'tvrage_id' in person:
				p.tvrage_id = person['tvrage_id']
			if 'netflix_id' in person:
				p.netflix_id = person['netflix_id']
			if 'imdb_id' in person:
				p.imdb_id = person['imdb_id']
			if 'wikipedia_link' in person:
				p.wikipedia_link = person['wikipedia_link']
			if 'twitter' in person:
				p.twitter = person['twitter']
			if 'chickipedia_id' in person:
				p.chickipedia_id = person['chickipedia_id']
			try:
				p.save()
			except IntegrityError, error:
				connection._rollback()
				if str(error).split('Key (')[1].split(')=')[0] == 'imdb_id':
					return Person.objects.get(imdb_id = person[str(error).split('Key (')[1].split(')=')[0]])
				elif str(error).split('Key (')[1].split(')=')[0] == 'wikipedia_link':
					return Person.objects.get(wikipedia_link = person[str(error).split('Key (')[1].split(')=')[0]])
				else:
					return None
				print len(person)
				print "dup"
			return p
	return p



def addTemporaryFromFreebase(freebase):
	real = 0
	person = {}
	p = None
	if freebase != None:
		person['wikipedia_link'] = None
		#Find first instance of wiki and use that, reason being can be more than one link and the first is usually the best
		for i in freebase['ns0:key']:
			if i['namespace'] == '/wikipedia/en':
				person['wikipedia_link'] = str(i['value'])
				real += 1
				break
		#Find rest of links
		for i in freebase['ns0:key']:
			if i['namespace'] == '/authority/imdb/name':
				person['imdb_id'] = int(i['value'].split('nm')[1])
				real += 1
			if i['namespace'] == '/authority/tvrage/person':
				person['tvrage_id'] = int(i['value'])
				real +=1
			if i['namespace'] == '/authority/netflix/role':
				person['netflix_id'] = int(i['value'])
				real += 1
			if i['namespace'] == '/authority/twitter':
				person['twitter'] = str(i['value'])
			if i['namespace'] == '/base/chickipedia/chickipedia_id':
				person['chickipedia_id'] = str(i['value'])
			if i['namespace'] == '/wikipedia/en_id':
				person['wikipedia_id'] = str(i['value'])
	else:
		return None
	print "links {} person is {}".format(real,person)
	
	#If at least one link was found continue adding
	if real>=1 or freebase['/people/person/date_of_birth'] != None:
		#Find if the person is in via their name
		##########Might want to switch to check via DOB to allow for multiple people of same name
		try:
			#,tvrage_id = person['tvrage_id'],netflix_id = person['netflix_id'],imdb_id=person['imdb_id'],wikipedia_link=person['wikipedia_link'],name=freebase['name']
			if 'wikipedia_link' in person:
				TemporaryPerson.objects.get(wikipedia_link=person['wikipedia_link'])
			elif 'netflix_id' in person:
				TemporaryPerson.objects.get(netflix_id=person['netflix_id'])
			elif 'imdb_id' in person:
				TemporaryPerson.objects.get(imdb_id = person['imdb_id'])
			elif 'twitter' in person:
				TemporaryPerson.objects.get(twitter=person['twitter'])
			elif 'chickipedia_id' in person:
				TemporaryPerson.objects.get(chickipedia_id=person['chickipedia_id'])
			else:
				p = TemporaryPerson.objects.get(name=freebase['name'])
			print "already here"
			
			if 'tvrage_id' in person:
				p.tvrage_id = person['tvrage_id']
			if 'netflix_id' in person:
				p.netflix_id = person['netflix_id']
			if 'imdb_id' in person:
				p.imdb_id = person['imdb_id']
			if 'wikipedia_link' in person:
				p.wikipedia_link = person['wikipedia_link']
			if 'wikipedia_id' in person:
				p.wikipedia_id = person['wikipedia_id']
			if 'chickipedia_id' in person:
				p.chickipedia_id = person['chickipedia_id']
			if 'twitter' in person:
				p.twitter = person['twitter']
			
			p.save()
			return p
		except:
			#The name wasn't there
			#If there is no DOB intialize to really old date
			if freebase['/people/person/date_of_birth'] == None:
				freebase['/people/person/date_of_birth'] = '1000-1-1'
			#If do not have the full dob check to see how much there is
			elif len(freebase['/people/person/date_of_birth'])<8:
				#Only have year
				if len(freebase['/people/person/date_of_birth']) <5:
					freebase['/people/person/date_of_birth'] += "-01-01"
				#Have month but no date
				else:
					freebase['/people/person/date_of_birth'] += "-01"
			if freebase['/people/person/gender'] == None:
				freebase['/people/person/gender'] = "Unknown"
			
			p = None
			p = TemporaryPerson(name=freebase['name'],gender=freebase['/people/person/gender'],
						dob=freebase['/people/person/date_of_birth'],)
			if 'tvrage_id' in person:
				p.tvrage_id = person['tvrage_id']
			if 'netflix_id' in person:
				p.netflix_id = person['netflix_id']
			if 'imdb_id' in person:
				p.imdb_id = person['imdb_id']
			if 'wikipedia_link' in person:
				p.wikipedia_link = person['wikipedia_link']
			if 'twitter' in person:
				p.twitter = person['twitter']
			if 'chickipedia_id' in person:
				p.chickipedia_id = person['chickipedia_id']
			try:
				p.save()
			except IntegrityError, error:
				connection._rollback()
				if str(error).split('Key (')[1].split(')=')[0] == 'imdb_id':
					return TemporaryPerson.objects.get(imdb_id = person[str(error).split('Key (')[1].split(')=')[0]])
				elif str(error).split('Key (')[1].split(')=')[0] == 'wikipedia_link':
					return TemporaryPerson.objects.get(wikipedia_link = person[str(error).split('Key (')[1].split(')=')[0]])
				else:
					return None
				print len(person)
				print "dup"
			return p
	return p


