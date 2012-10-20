
from lxml import html
from lxml.etree import tostring
import lxml.html
import urllib, urllib2
import os
import Image
import ImageFile
from PIL import ImageOps
import simplejson
import urlparse
import PIL
from exceptions import IOError
import math, operator
import ImageChops
import math, operator
import urlparse, urllib
import pickle
import cStringIO

def getPosters(id,t):
	url = "http://www.movieposterdb.com/movie/"+ str(id) + "/?cid=1"
	print url
	
	
	request = urllib2.Request(url)
	request.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1')
	
	#sock = urllib2.urlopen(s)
	opener = urllib2.build_opener()
	resp = opener.open(request)
	htmlSource = resp.read()
	
#	data = {}
#	headers = {
#	'Accept': 'text/html, */*',
#	'Accept-Language': 'en-us,en;q=0.5',
#	}
#	req = urllib2.Request(url, data, headers)
#	f = urllib2.urlopen(req)
#	htmlSource = f.read()
#	f.close()
	#print htmlSource
	root = html.fromstring(htmlSource)
	
	count = 1
	posters = root.cssselect("tr")
	for tr in posters:
		td = tr.cssselect("td")
		for i in td:
			img = i.cssselect("img")
			
			for ii in img:

				im = tostring(ii)
				pos = im.split('http://www.movieposterdb.com/posters/')
				if len(pos)>1:
					minusjpg = pos[1].split('.jpg')
					if len(minusjpg)>1:
						l = 'http://www.movieposterdb.com/posters/'+minusjpg[0]+'.jpg'
						if ('/s_') in l:
							l = l.replace("/s_","/l_",1)
						else:
							l = l.replace("/t_","/l_",1)
						c = getPoster(l,id,count,t)
						count += int(c)
						if count == 15:
							return count
	return count

def getPoster(link,id,c,t):
	dir = "/Users/Jason/movie2/" + str(id) + "/"
	if not os.path.exists(dir):
	    os.makedirs(dir)
	
	file = "/Users/Jason/movie2/" + str(id) + '/' + str(c) + ".jpg"
	
	if not (os.path.isfile(file)):
		
		#request = urllib2.Request(link)
		#request.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1')
		
		#sock = urllib2.urlopen(s)
		#opener = urllib2.build_opener()
		#source = open(file,"wb")
		
		
		#resp = opener.open(request)
		print file
		image = urllib.URLopener()
		image.retrieve(link, "/Users/Jason/tmp/tmp" + str(t) +".jpg")
		im = Image.open("/Users/Jason/tmp/tmp" + str(t) + ".jpg")
		#print im.size
		
		if im.size[1]<501:
			print "saved"
			im.save(file, "JPEG",optimize=True)
			return 1		
	return 0




def fixurl(url):
    # turn string into unicode
    if not isinstance(url,unicode):
        url = url.decode('utf8')
	
    # parse it
    parsed = urlparse.urlsplit(url)
	
    # divide the netloc further
    userpass,at,hostport = parsed.netloc.partition('@')
    user,colon1,pass_ = userpass.partition(':')
    host,colon2,port = hostport.partition(':')
	
    # encode each component
    scheme = parsed.scheme.encode('utf8')
    user = urllib.quote(user.encode('utf8'))
    colon1 = colon1.encode('utf8')
    pass_ = urllib.quote(pass_.encode('utf8'))
    at = at.encode('utf8')
    host = host.encode('idna')
    colon2 = colon2.encode('utf8')
    port = port.encode('utf8')
    path = '/'.join(  # could be encoded slashes!
        urllib.quote(urllib.unquote(pce).encode('utf8'),'')
        for pce in parsed.path.split('/')
    )
    query = urllib.quote(urllib.unquote(parsed.query).encode('utf8'),'=&?/')
    fragment = urllib.quote(urllib.unquote(parsed.fragment).encode('utf8'))
	
    # put it back together
    netloc = ''.join((user,colon1,pass_,at,host,colon2,port))
    return urlparse.urlunsplit((scheme,netloc,path,query,fragment))


class SmartRedirectHandler(urllib2.HTTPRedirectHandler):
	def http_error_301(self, req, fp, code, msg, headers):  
		result = urllib2.HTTPRedirectHandler.http_error_301(
			self, req, fp, code, msg, headers)              
		result.status = code
		return result                                       
	
	def http_error_302(self, req, fp, code, msg, headers):
		result = urllib2.HTTPRedirectHandler.http_error_302(
			self, req, fp, code, msg, headers)
		result.status = code
		return result
	


def compare(file1, file2):
	image1 = Image.open(file1)
	image2 = Image.open(file2)
	if image1.mode != "RGB":
		image1 = image1.convert("RGB")
	if image2.mode != "RGB":
		image2 = image2.convert("RGB")
	#print image1
	#print image2
	h = ImageChops.difference(image1, image2).histogram()
	#print image1.size[0]
	#print image1.size[1]
    # calculate rms
	
	h1 = image1.histogram()
	h2 = image2.histogram()
	rms = math.sqrt(reduce(operator.add,
	    map(lambda a,b: (a-b)**2, h1, h2))/len(h1))
	return rms


def getPersonPicture(name,id):
	dir = "/Users/Jason/person/" + str(id) + "/"
	if not os.path.exists(dir):
	    os.makedirs(dir)
	name = name.replace(' ', '%20')
	#print name
	
	url = ('https://ajax.googleapis.com/ajax/services/search/images?' +
	       'v=1.0&q=/"' + name + '/"&imgtype=face&imgsz=large&rsz=8&userip=74.184.153.68')
	
	if isinstance(name,unicode):
		url = fixurl(url)
				
	#print url
	request = urllib2.Request(url, None, {'Referer': 'http://flickchart.com'})
	response = urllib2.urlopen(request)
	
	# Process the JSON string.
	results = simplejson.load(response)
	#print results
	c=1
	sizes = []
	for i in results['responseData']['results']:
		file = "/Users/Jason/person/" + str(id) + '/' + str(c) + ".jpg"
		#print file
		if not (os.path.isfile(file)): 
			if int(i['width'])<int(i['height']):
				image = urllib2.build_opener(SmartRedirectHandler())
				request = urllib2.Request(i['unescapedUrl'], None, {'Referer': 'http://reesim.com'})
				
				try:
					resp = image.open(request,timeout=8)
				except urllib2.URLError, e:
					if not hasattr(e, "code"):
						print "WHOOPS"
					resp = e
				except urllib2.HTTPError, e:
					if not hasattr(e, "code"):
						print "WHOOPS"
					resp = e
				except urllib2.HTTPException,e:
					print "whoops"
			 	else:
					#print "got one"
					try:
						data = resp.read()
					except urllib2.URLError, e:
					    if isinstance(e.reason, socket.timeout):
					        print ("There was an error: %r" % e)
					
					contenttype = resp.headers["content-type"]
					if contenttype=="image/jpeg" or contenttype=="image/jpg" or contenttype=="image/gif" or contenttype=="image/JPEG" or contenttype == "image/png":
						size = len(data)
						if size in sizes:
							print "DUPLICATE"
						elif size <= 9000:
							print "TOO SMALL"
						else:
							f = open('tmp.jpg','wb')
							sizes.append(size)
							f.write(data)
							f.close()
							samepic = False
							diff=1000
							for i in range(1,c):
								oldf = "/Users/Jason/person/" + str(id) + '/' + str(i) + ".jpg"
								if (os.path.isfile(oldf)): 
									diff = compare(oldf, 'tmp.jpg')
									if diff < 299:
										samepic = True
							if samepic == False:
								c+=1
							
								
								im = Image.open('tmp.jpg')
								#file = "/Users/Jason/person/" + str(id) + '/' + str(c) + ".jpg"
								if im.mode != "RGB":
									im = im.convert("RGB")
								try:
									im.save(file,"JPEG",optimize=True)
								except IOError:
									#ImageFile.MAXBLOCK = im.size[0] * im.size[1]
									im.save(file, "JPEG")
							else:
								print "DUPLICATE BY RMS"
					else:
						print resp.headers["content-type"]
						print "not a pic"		
					#image.urlretrieve(i['unescapedUrl'], "tmp.jpg")
					#im = Image.open("tmp.jpg")
					#im.save(file, "JPEG")
		else:
			c+=1
			f = open(file,'r')
			sizes.append(len(f.read()))
	print sizes
	return c-1



def getPersonPictureReplacements(name,id):
	dir = "/Users/Jason/person/" + str(id) + "/tmp/"
	if not os.path.exists(dir):
	    os.makedirs(dir)
	name = name.replace(' ', '%20')
	
	#print name
	#
	url = ('https://ajax.googleapis.com/ajax/services/search/images?' +
	       'v=1.0&q=/"' + name + '/"&userip=74.184.153.68')
	#&imgtype=face&imgsz=large&rsz=8
	if isinstance(name,unicode):
		url = fixurl(url)
	
	#print url
	request = urllib2.Request(url, None, {'Referer': 'http://flickchart.com'})
	response = urllib2.urlopen(request)
	
	# Process the JSON string.
	results = simplejson.load(response)
	#print results
	c=1
	sizes = []
	#print results
	empty=True
	start=0
	
	picinfo = {}
	
	while empty:
		if not results == None:
			for i in results['responseData']['results']:
				print i.keys()
				file = "/Users/Jason/person/" + str(id) + '/tmp/' + str(c) + ".jpg"
				print file
				print sizes
				if not (os.path.isfile(file)): 
					if int(i['width'])<int(i['height']) and (not 'exposay' in i['unescapedUrl']) and (not 'topnews.in' in i['unescapedUrl']) and (not 'starpulse' in i['unescapedUrl']):
						image = urllib2.build_opener(SmartRedirectHandler())
						request = urllib2.Request(i['tbUrl'], None, {'Referer': 'http://reesim.com'})
						
						try:
							resp = image.open(request,timeout=8)
						except urllib2.URLError, e:
							if not hasattr(e, "code"):
								print "WHOOPS"
							resp = e
						except urllib2.HTTPError, e:
							if not hasattr(e, "code"):
								print "WHOOPS"
							resp = e
						except urllib2.HTTPException,e:
							print "whoops"
					 	else:
							#print "got one"
							try:
								data = resp.read()
							except urllib2.URLError, e:
							    if isinstance(e.reason, socket.timeout):
							        print ("There was an error: %r" % e)
							
							#contenttype = resp.headers["content-type"]
							#if contenttype=="image/jpeg" or contenttype=="image/jpg" or contenttype=="image/gif" or contenttype=="image/JPEG" or contenttype == "image/png" or contenttype == "image/jpeg; charset=utf-8":
							#	size = len(data)
							#	if size in sizes:
							#		print "DUPLICATE"
							#	elif size <= 9000:
							#		print "TOO SMALL"
							#	else:
							f = open('/Users/Jason/tmp/tmp.jpg','wb')
							#		sizes.append(size)
							f.write(data)
							f.close()
							#		samepic = False
							#		diff=1000
							#		for i in range(1,20):
							#			oldf = "/Users/Jason/person/" + str(id) + '/' + str(i) + ".jpg"
							#			if (os.path.isfile(oldf)): 
							#				diff = compare(oldf,'/Users/Jason/tmp/tmp.jpg')
							#				if diff < 299:
							#					samepic = True
							#		for i in range(1,c):
							#			oldf = "/Users/Jason/person/" + str(id) + '/tmp/' + str(i) + ".jpg"
							#			if (os.path.isfile(oldf)): 
							#				diff = compare(oldf,'/Users/Jason/tmp/tmp.jpg')
							#				if diff < 299:
							#					samepic = True
							#		if samepic == False:
							#			c+=1
							#			im = Image.open('/Users/Jason/tmp/tmp.jpg')
							#			if im.mode != "RGB":
							#				im = im.convert("RGB")
							#			try:
							#				im.save(file,"JPEG",optimize=True)
							#			except IOError:
							#				#ImageFile.MAXBLOCK = im.size[0] * im.size[1]
							#				im.save(file, "JPEG")
							#		else:
							#			print "DUPLICATE BY RMS"
							#else:
							#	print resp.headers["content-type"]
							#	print "not a pic"		
							#image.urlretrieve(i['tbUrl'], "tmp.jpg")
							
							im = Image.open('/Users/Jason/tmp/tmp.jpg')
							im.save(file, "JPEG")
							
							picinfo[c]={}
							picinfo[c]['link'] = i['unescapedUrl']
							
							parsed_uri = urlparse.urlparse( i['unescapedUrl'] )
							domain = '{}'.format( parsed_uri[ 1 ] )
							
							picinfo[c]['domain'] = domain
							
							picinfo[c]['height'] = i['height']
							picinfo[c]['width'] = i['width']
							picinfo[c]['title'] = i['title']
							c+=1
				else:
					c+=1
					f = open(file,'r')
					sizes.append(len(f.read()))
				if c > 25:
					empty = False
			if empty:
				
				#print results['responseData']['cursor']['pages'][1]['start']
				#if (results['responseData']['cursor']['pages']) >0:
					#str(results['responseData']['cursor']['pages'][1]['start'])
				start +=8
				print start
				if start >36:
					empty = False
					break
				url = ('https://ajax.googleapis.com/ajax/services/search/images?' +
				       'v=1.0&q=/"' + name + '/"&imgsz=large&imgtype=face&rsz=8&start=' + str(start) + '&userip=74.184.153.68')
				
				if isinstance(name,unicode):
					url = fixurl(url)
					
				#print url
				request = urllib2.Request(url, None, {'Referer': 'http://flickchart.com'})
				response = urllib2.urlopen(request)
				
				# Process the JSON string.
				results = simplejson.load(response)
				#print results
	pickle.dump(picinfo,open("/Users/Jason/person/" + str(id) + '/tmp/links.lnk', "wb" ))
	
	print empty
	print sizes
	print c
	#return c-1
	print picinfo
	return picinfo




def getPersonTemporaryPicture(name,id):
	dir = "/Users/Jason/person/temp/" + str(id) + "/"
	if not os.path.exists(dir):
	    os.makedirs(dir)
	name = name.replace(' ', '%20')
	ImageFile.MAXBLOCK = 1024*1024
	#print name
	#
	url = ('https://ajax.googleapis.com/ajax/services/search/images?' +
	       'v=1.0&q=/"' + name + '/"&imgsz=large&imgtype=face&rsz=8&userip=74.184.153.68')
	
	if isinstance(name,unicode):
		url = fixurl(url)
	
	#print url
	request = urllib2.Request(url, None, {'Referer': 'http://flickchart.com'})
	response = urllib2.urlopen(request)
	
	# Process the JSON string.
	results = simplejson.load(response)
	#print results
	c=1
	sizes = []
	#print results
	empty=True
	start=0
	while empty:
		if not results == None:
			for i in results['responseData']['results']:
				#print i.keys()
				file = "/Users/Jason/person/temp/" + str(id) + '/' + str(c) + ".jpg"
				#print file
				if not (os.path.isfile(file)): 
					if int(i['width'])<int(i['height']) and int(i['width'])>150 and (not 'exposay' in i['unescapedUrl']) and (not 'topnews.in' in i['unescapedUrl']):
						image = urllib2.build_opener(SmartRedirectHandler())
						request = urllib2.Request(i['unescapedUrl'], None, {'Referer': 'http://reesim.com'})
						
						try:
							resp = image.open(request,timeout=8)
						except urllib2.URLError, e:
							if not hasattr(e, "code"):
								print "WHOOPS"
							resp = e
						except urllib2.HTTPError, e:
							if not hasattr(e, "code"):
								print "WHOOPS"
							resp = e
						except Exception,e:
							print "whoops"
					 	else:
							#print "got one"
							try:
								data = resp.read()
							except urllib2.URLError, e:
							    if isinstance(e.reason, socket.timeout):
							        print ("There was an error: %r" % e)
							
							try:
								contenttype = resp.headers["content-type"]
								if contenttype=="image/jpeg" or contenttype=="image/jpg" or contenttype=="image/gif" or contenttype=="image/JPEG" or contenttype == "image/png" or contenttype == "image/jpeg; charset=utf-8" or contenttype == "image/jpeg;charset=UTF-8":
									size = len(data)
									if size in sizes:
										print "DUPLICATE"
									elif size <= 9000:
										print "TOO SMALL"
									else:
										f = open('/Users/Jason/tmp/tmp'+str(11)+'.jpg','wb')
										sizes.append(size)
										f.write(data)
										f.close()
										samepic = False
										diff=1000
										for i in range(1,c):
											oldf = "/Users/Jason/person/temp" + str(id) + '/' + str(i) + ".jpg"
											if (os.path.isfile(oldf)): 
												diff = compare(oldf,'/Users/Jason/tmp/tmp'+str(11)+'.jpg')
												if diff < 299:
													samepic = True
										if samepic == False:
											c+=1
											im = Image.open('/Users/Jason/tmp/tmp'+str(11)+'.jpg')
											if im.mode != "RGB":
												im = im.convert("RGB")
											try:
												im.save(file,"JPEG",optimize=True)
											except IOError:
												#ImageFile.MAXBLOCK = im.size[0] * im.size[1]
												im.save(file, "JPEG")
										else:
											print "DUPLICATE BY RMS"
								else:
									print resp.headers["content-type"]
							except:
								print "not a pic"		
							#image.urlretrieve(i['unescapedUrl'], "tmp.jpg")
							#im = Image.open("tmp.jpg")
							#im.save(file, "JPEG")
				else:
					c+=1
					f = open(file,'r')
					sizes.append(len(f.read()))
				if not sizes == []:
					empty = False
			if empty:
				
				#print results['responseData']['cursor']['pages'][1]['start']
				str(results['responseData']['cursor']['pages'][1]['start'])
				start +=8
				print start
				if start >200:
					empty = False
				url = ('https://ajax.googleapis.com/ajax/services/search/images?' +
				       'v=1.0&q=/"' + name + '/"&imgsz=large&imgtype=face&rsz=8&start=' + str(start) + '&userip=74.184.153.68')
				
				if isinstance(name,unicode):
					url = fixurl(url)
					
				#print url
				request = urllib2.Request(url, None, {'Referer': 'http://flickchart.com'})
				response = urllib2.urlopen(request)
				
				# Process the JSON string.
				results = simplejson.load(response)
				#print results
	print sizes
	return c-1


def getPersonPictureThread(name,id,t):
	dir = "/Users/Jason/person/" + str(id) + "/"
	if not os.path.exists(dir):
	    os.makedirs(dir)
	name = name.replace(' ', '%20')
	ImageFile.MAXBLOCK = 1024*1024
	#print name
	#
	url = ('https://ajax.googleapis.com/ajax/services/search/images?' +
	       'v=1.0&q=/"' + name + '/"&imgsz=large&imgtype=face&rsz=8&userip=74.184.153.68')
	
	if isinstance(name,unicode):
		url = fixurl(url)
	
	#print url
	request = urllib2.Request(url, None, {'Referer': 'http://flickchart.com'})
	response = urllib2.urlopen(request)
	
	# Process the JSON string.
	results = simplejson.load(response)
	#print results
	c=1
	sizes = []
	#print results
	empty=True
	start=0
	while empty:
		if not results == None:
			for i in results['responseData']['results']:
				#print i.keys()
				file = "/Users/Jason/person/" + str(id) + '/' + str(c) + ".jpg"
				#print file
				if not (os.path.isfile(file)): 
					if int(i['width'])<int(i['height']) and int(i['width'])>150 and (not 'exposay' in i['unescapedUrl']) and (not 'topnews.in' in i['unescapedUrl']):
						image = urllib2.build_opener(SmartRedirectHandler())
						request = urllib2.Request(i['unescapedUrl'], None, {'Referer': 'http://reesim.com'})
						
						try:
							resp = image.open(request,timeout=8)
						except urllib2.URLError, e:
							if not hasattr(e, "code"):
								print "WHOOPS"
							resp = e
						except urllib2.HTTPError, e:
							if not hasattr(e, "code"):
								print "WHOOPS"
							resp = e
						except Exception,e:
							print "whoops"
					 	else:
							#print "got one"
							try:
								data = resp.read()
							except urllib2.URLError, e:
							    if isinstance(e.reason, socket.timeout):
							        print ("There was an error: %r" % e)
							
							contenttype = resp.headers["content-type"]
							if contenttype=="image/jpeg" or contenttype=="image/jpg" or contenttype=="image/gif" or contenttype=="image/JPEG" or contenttype == "image/png" or contenttype == "image/jpeg; charset=utf-8" or contenttype == "image/jpeg;charset=UTF-8":
								size = len(data)
								if size in sizes:
									print "DUPLICATE"
								elif size <= 9000:
									print "TOO SMALL"
								else:
									f = open('/Users/Jason/tmp/tmp'+str(t)+'.jpg','wb')
									sizes.append(size)
									f.write(data)
									f.close()
									samepic = False
									diff=1000
									for i in range(1,c):
										oldf = "/Users/Jason/person/" + str(id) + '/' + str(i) + ".jpg"
										if (os.path.isfile(oldf)): 
											diff = compare(oldf,'/Users/Jason/tmp/tmp'+str(t)+'.jpg')
											if diff < 299:
												samepic = True
									if samepic == False:
										c+=1
										im = Image.open('/Users/Jason/tmp/tmp'+str(t)+'.jpg')
										if im.mode != "RGB":
											im = im.convert("RGB")
										try:
											im.save(file,"JPEG",optimize=True)
										except IOError:
											#ImageFile.MAXBLOCK = im.size[0] * im.size[1]
											im.save(file, "JPEG")
									else:
										print "DUPLICATE BY RMS"
							else:
								print resp.headers["content-type"]
								print "not a pic"		
							#image.urlretrieve(i['unescapedUrl'], "tmp.jpg")
							#im = Image.open("tmp.jpg")
							#im.save(file, "JPEG")
				else:
					c+=1
					f = open(file,'r')
					sizes.append(len(f.read()))
				if not sizes == []:
					empty = False
			if empty:
				
				#print results['responseData']['cursor']['pages'][1]['start']
				str(results['responseData']['cursor']['pages'][1]['start'])
				start +=8
				print start
				if start >200:
					empty = False
				url = ('https://ajax.googleapis.com/ajax/services/search/images?' +
				       'v=1.0&q=/"' + name + '/"&imgsz=large&imgtype=face&rsz=8&start=' + str(start) + '&userip=74.184.153.68')
				
				if isinstance(name,unicode):
					url = fixurl(url)
					
				#print url
				request = urllib2.Request(url, None, {'Referer': 'http://flickchart.com'})
				response = urllib2.urlopen(request)
				
				# Process the JSON string.
				results = simplejson.load(response)
				#print results
	print sizes
	return c-1




def getMobiCover(id,mid):
	dir = "/Users/Jason/vgame/" + str(id) + "/"
	if not os.path.exists(dir):
	    os.makedirs(dir)
	outfile = dir + "1.jpg"
	if not os.path.isfile(outfile):
		url = "http://www.mobygames.com/game/" + str(mid)
		headers = {
			'User-Agent' : "Magic Browser",
			'Accept': 'text/html, */*',
			'Accept-Language': 'en-us,en;q=0.5',
			'Connection':	'Keep-Alive',
		}
		data=""
		req = urllib2.Request(url, data, headers)
		#urlsvisited.append(cpurl)
		f = urllib2.urlopen(req)
		htmlSource = f.read()
		f.close()
		root = html.fromstring(htmlSource)
	
		div = root.cssselect("div#coreGameCover")
		print div
		for i in div:
			img = tostring(i).split("src=\"")[1].split(".jpg")[0]
			img = img + ".jpg"
			img = img.replace("small","large")
			if not 'notonfile' in img:
				file = urllib2.urlopen(img)
		
				img = cStringIO.StringIO(file.read()) # constructs a StringIO holding the image

				im = Image.open(img)
		
				size = 500,500
				if im.size[0]>500 or im.size[1]>500:
					print "BIG"
					im.thumbnail(size, Image.ANTIALIAS)
			
				if not os.path.isfile(outfile):
					im.save(outfile, "JPEG",optimize=True)



def makeTemporaryThumbByPic(id,pic_id):
	dir = "/Users/Jason/person/thumb/temp/"
	if not os.path.exists(dir):
	    os.makedirs(dir)
	if not (os.path.isfile(dir+str(id)+".jpg")):
		dir = "/Users/Jason/person/temp/" + str(id) + "/"
		pic_ids = str(pic_id)
		file = dir + str(pic_id) + ".jpg"
	#	count = 2
		#while not (os.path.isfile(file)): 
		#	file = dir+str(count)+".jpg"
		#	count += 1
		#	if count>20:
		#		break
		
		image = Image.open(file)
		thumb = ImageOps.fit(image,(80,80),Image.ANTIALIAS,0,(0,0))
		
		thumb.save("/Users/Jason/person/thumb/temp/" + str(id)+".jpg","JPEG",optimize=True)


def makeThumbByPic(id,pic_id):
	dir = "/Users/Jason/person/thumb"
	if not os.path.exists(dir):
	    os.makedirs(dir)
	if not (os.path.isfile(dir+str(id)+".jpg")):
		dir = "/Users/Jason/person/" + str(id) + "/"
		pic_ids = str(pic_id)
		file = dir + str(pic_id) + ".jpg"
	#	count = 2
		#while not (os.path.isfile(file)): 
		#	file = dir+str(count)+".jpg"
		#	count += 1
		#	if count>20:
		#		break
		
		image = Image.open(file)
		thumb = ImageOps.fit(image,(80,80),Image.ANTIALIAS,0,(0,0))
		
		thumb.save("/Users/Jason/person/thumb/" + str(id)+".jpg","JPEG",optimize=True)
	
def makeThumb(id):
	dir = "/Users/Jason/person/thumb"
	if not os.path.exists(dir):
	    os.makedirs(dir)
	if not (os.path.isfile(dir+str(id)+".jpg")):
		dir = "/Users/Jason/person/" + str(id) + "/"
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
			thumb.save("/Users/Jason/person/thumb/" + str(id)+".jpg","JPEG",optimize=True)




def makeVGThumb(id):
	dir = "/Users/Jason/vgame/thumb"
	if not os.path.exists(dir):
	    os.makedirs(dir)
	if not (os.path.isfile(dir+str(id)+".jpg")):
		dir = "/Users/Jason/vgame/" + str(id) + "/"
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
			thumb.save("/Users/Jason/vgame/thumb/" + str(id)+".jpg","JPEG",optimize=True)




def numPics(id):
	for i in range(1,20):
		file = "/Users/Jason/Movie/" + str(id) + '/' + str(i) + ".jpg"
		if not (os.path.isfile(file)):
			return i-1
	return i



def numPersonPics(id):
	for i in range(1,25):
		file = "/Users/Jason/Person/" + str(id) + '/' + str(i) + ".jpg"
		if not (os.path.isfile(file)):
			return i-1
	return i

def numVidPics(id):
	for i in range(1,25):
		file = "/Users/Jason/vgame/" + str(id) + '/' + str(i) + ".jpg"
		if not (os.path.isfile(file)):
			return i-1
	return i