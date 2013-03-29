
from django.template import Context, loader, RequestContext
from django.core.context_processors import csrf
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.core.exceptions import ObjectDoesNotExist
from django.core import serializers
from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render_to_response
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import auth
from django.utils import simplejson
from django.db.models import Q, Max, Sum, Avg
from django.db import transaction, connection, IntegrityError
from django.shortcuts import redirect

from django.utils import simplejson
from django.utils.encoding import smart_str, smart_unicode
from endless_pagination.decorators import page_template, page_templates

from datetime import datetime, timedelta
from Queue import Queue
from threading import Thread
from StringIO import StringIO
from exceptions import IOError
from lxml import html, etree
from lxml.etree import tostring
import cStringIO, pickle, string, random, math, csv, types
import re, htmlentitydefs
import urllib, urllib2, lxml.html, gzip, httplib2
import time, os.path, re, shutil
import Image
import operator
from rankyourfavs.rankfavs.models import *
from datetime import date, datetime
import Posters, Netflix, TVUtlities, Scraper
import sys
import freebase
import movieviews
import MovieUtilities
from imdb import IMDb
import re




def unquotekey(key, encoding=None):
    """
    unquote a namespace key and turn it into a unicode string
    """
    valid_always = string.ascii_letters + string.digits
    output = []
    i = 0
    while i < len(key):
        if key[i] in valid_always:
            output.append(key[i])
            i += 1
        elif key[i] in '_-' and i != 0 and i != len(key):
            output.append(key[i])
            i += 1
        elif key[i] == '$' and i+4 < len(key):
            # may raise ValueError if there are invalid characters
            output.append(unichr(int(key[i+1:i+5],16)))
            i += 5
        else:
            raise ValueError, "unquote key saw invalid character '%s' at position %d" % (key[i], i)
    ustr = u''.join(output)
   
    if encoding is None:
        return ustr
    return ustr.encode(encoding)

##
# Removes HTML or XML character references and entities from a text string.
#
# @param text The HTML (or XML) source text.
# @return The plain text, as a Unicode string, if necessary.

def unescape(text):
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text # leave as is
    return re.sub("&#?\w+;", fixup, text)
	


def LogoutHandler(request):
    auth.logout(request)
    # Redirect to a success page.
    return HttpResponse("logged out")


def LoginPageHandler(request):
    args = dict()
    t = loader.get_template('index.html')
    c = RequestContext(request,{})
    message = render_to_response('index.html', c,context_instance=RequestContext(request))
    return HttpResponse(message)


def RegisterFormHandler(request):
	t = loader.get_template('register.html')
	c = RequestContext(request,{})
	return HttpResponse(t.render(c))


def SubmitRegisterHandler(request):
	params = {}
	if request.method=='GET':
		params = request.GET
	elif request.method=='POST':
		params = request.POST
	un=str(params["user"])
	em=str(params["email"])
	pw=str(params["password"])
	ht=str(params["hometown"])
	u = User.objects.create_user(un,em,pw)
	us = UserProfile(user=u)
	us.save()
	c={}  
	c['m'] = "Thanks for registering"
	
	message = render_to_response('post-submit.html', c,context_instance=RequestContext(request))
	return HttpResponse(message)


def LoginHandler(request):
    user = authenticate(username=request.POST['username'], password=request.POST['password'])
    if user is not None:
        auth.login(request, user)
        c = RequestContext(request,{})
        message = render_to_response('index.html', c,context_instance=RequestContext(request))
        return HttpResponse(message)
    else:
        return HttpResponse("Your username and password didn't match.")


def HomeHandler(request,template="index.html",extra_context=None):
	params= request.GET	
#	today = date.today()
	context = {}
	#freeOnesScraper()
	#TVUtlities.getPosters()
 	#netflix(60025061)
	#netflix(60000523)
	#netflix(5670479)	
	#ratings()
	#net2imdb()
	#matchupNetflixIMDb()	
	#storeAllNetFlix()
	#getImageNumbers()
	#storeNetflixRatings(request.user.get_profile())
	
	#moviePosterGetter()
	#chickipediaPage()
	#peopleInformationGetter()
	#baseballAlmanac()
	persons = Person.objects.all()
	changed = 0
	if False:
	#for i in persons:
		if False:#i.wikipedia_link != None:
			try:
				i.wikipedia_link = unquotekey(i.wikipedia_link)
				changed +=1
				i.save()
			except:
				print "ERROR"
			
		if i.bio != None:
			i.bio = unescape(i.bio).encode("utf-8")
		
			try:
				i.bio = i.bio.decode('unicode-escape')
			except:
				print "error {}".format(i.pid)
				changed += 1
			
			i.save()
		if False:#i.wikipedia_link != None and i.bio == None:
			
			results = getDOBandBiofromWikipedia(i.wikipedia_link)
			s_dob = results['dob']
			bio = results['bio']
			redirect = results['redirect']
			if len(bio)>1:
				if redirect != None:
					oldwiki = i.wikipedia_link
					i.wikipedia_link = redirect
					#print "Changed to {} to this {}".format(oldwiki,redirect)
				i.bio = bio
				changed +=1
				i.save()
				
			"""if s_dob != 0 and s_dob != "" and len(s_dob)>1:
				
				try:
					dob = datetime.strptime(s_dob,"%Y-%m-%d")
				except:
					try:
						dob = datetime.strptime(s_dob.replace(' ',''),"%Y-%m-%d")
						s_dob = s_dob.replace(' ','')
					except:
						break
				
				stored_dob = datetime.strptime(str(i.dob),"%Y-%m-%d")
				if dob == stored_dob:
					print "MATCH IN DA HOUSE"
				else:
					print "WE GOT AN IMPOSTER"
					#print "stored {} wiki {} name {} id {}".format(i.dob,dob,i.name,i.pid)
					i.dob = s_dob
					changed += 1
					i.save()
					print changed
					"""
					
	print "changed {}".format(changed)
	
	#getTwitterInformation()
	#getSearchAmounts()
	#getPersonRanks()
	#getPersonRankings()
	
	#getExtendedMovieInfo()
	#getMovieRankings()
	#getTagProfessions()
	#getNationality()
	#getThumbs()
	#recalculateELO()
	#processList()
	#refreshRanks()
	#processIMDbList('http://www.imdb.com/list/export?list_id=lUjAiWeHDQg&author_id=ur20576713')
	#processIMDbList('http://www.imdb.com/list/export?list_id=KSy4WT-HgTk&author_id=ur14092243')
	#processIMDbList('http://www.imdb.com/list/export?list_id=y6fFBKlGjFw&author_id=ur29264691')
	#getMissingNames()
	
	#getWikiIdsFromCategoryName("American_Idol_participants")
	#getWikiIdsFromCategoryName("Olympic_gymnasts_of_the_United_States","Gymnast")
	#getMobi()
	if request.user.is_authenticated():
		return movieviews.MovieMatchHandler(request)
	if False:#request.user.is_authenticated():
		f = {'year__gte': 2000}
		movie1 = Movie.objects.filter(**f).order_by('?')[0]
		movie2 = Movie.objects.filter(**f).order_by('?')[0]
		count = 0
		while (MovieMatchup.objects.filter(winner = movie1, loser = movie2).exists() 
				or MovieMatchup.objects.filter(winner = movie2, loser = movie1).exists()
				or movie1 == movie2):
			movie1 = Movie.objects.filter(**f).order_by('?')[0]
			movie2 = Movie.objects.filter(**f).order_by('?')[0]
			count += 1
			if count > 1000:
				return HttpResponse("No Movies")
	
		pt = "index_page.html"
	
		try:
			movie1mat = UserMovieScore.objects.get(uid = request.user.get_profile(),mid = movie1)
		except:
			movie1mat = UserMovieScore(uid = request.user.get_profile(), mid = movie1, elorating = 1000,numratings =0,wins=0,losses=0)
			movie1mat.save()
		try:
			movie2mat = UserMovieScore.objects.get(uid = request.user.get_profile(),mid = movie2)
		except:
			movie2mat = UserMovieScore(uid =request.user.get_profile(), mid = movie2, elorating = 1000,numratings =0,wins=0,losses=0)
			movie2mat.save()
	
		top20 = UserMovieScore.objects.filter(uid=request.user.get_profile()).order_by('elorating').reverse()[:25]
		print context
		context = {
				'moviebar':True,
		        'movie1': movie1,
				'movie1mat': movie1mat,
				'movie2': movie2,
				'movie2mat': movie2mat,
				'movie1ran':random.randint(1,movie1.images),
				'movie2ran':random.randint(1,movie2.images),
				'top20': top20,
		}
		print context
	
	return render_to_response(template, context,
		context_instance=RequestContext(request))


def AjaxSearchHandler(request):
	params = request.POST
	
	queries = request.POST.get('search').split()
	qset1 =  reduce(operator.__or__, [Q(name__icontains=query) | Q(chickipedia_id__icontains=query) for query in queries])
	
	results = Person.objects.filter(qset1).distinct()
	context = {}
	context['results'] =  results
	
	template = 'ajaxsearchresults.html'
	
	message = render_to_response(template, context,
		context_instance=RequestContext(request))
	return HttpResponse(message)


def AddEntityPageHandler(request):
	if request.method=='GET':
		params = request.GET
		if 'temp_id' in params:
			
			temp = TemporaryPerson.objects.get(temp_id = int(params['temp_id']))
			if 'pics' in params:
				temp.images = Posters.getPersonTemporaryPicture(temp.name,temp.temp_id)
				Posters.makeTemporaryThumbByPic(temp.temp_id,1)
			temp.save()
			context = {}
			context['person'] = temp
			context['range'] = range(1,temp.images+1)
			
			context['dob'] = "{}/{}/{}".format(temp.dob.year,temp.dob.month,temp.dob.day)
			
			message = render_to_response('confirmadd.html',context,context_instance=RequestContext(request))
			return HttpResponse(message)
	context={}
	message = render_to_response('addentity.html',context,context_instance=RequestContext(request))
	return HttpResponse(message)


def TopListHandler(request):
	userprofile = request.user.get_profile()
	f = {}
	f['uid'] = userprofile
	f['pid__gender'] = 'Female'
	persons = UserPersonScore.objects.filter(**f).order_by('elorating').reverse()[:250]
	context = {}
	context['persons'] = persons
	message = render_to_response('toplist.html',context,context_instance=RequestContext(request))
	return HttpResponse(message)
	


def AddEntityHandler(request):
	context = {}
	if request.method=='GET':
		params = request.GET
	if request.method=='POST':
		params = request.POST
	print params
	
	links = sanitizeLinks(params)
	
	
	if 'type' in params and params['type'] == "Person":
		print "PERSON IN THE HOUSE"
		freebase = None
		if links['imdb_id'] != None:
			freebase = getFreebaseData("imdb",links['imdb_id'])
		if links['twitter'] != None and freebase == None:
			freebase = getFreebaseData("twitter",links['twitter'])
		if links['wikipedia_link'] != None and freebase == None:
			freebase = getFreebaseData('wikipedia',links['wikipedia_link'])
		else:	
			freebase = getFreebaseData('name',params['name'])
				
		
		if freebase != None:
			person = addTemporaryFromFreebase(freebase)
			if person != None:
				pid = person.temp_id
			
				person.images = Posters.getPersonTemporaryPicture(person.name,person.temp_id)
				person.save()
				try:
					person.save()
				except:
					print person.imdb_id
					try:
						person = TemporaryPerson.objects.get(imdb_id = person.imdb_id)
					except:
						print "NONE"
						return "NONE"
		
				url = '/addentity/?temp_id=' + str(person.temp_id)
				return redirect(url)
			else:
				print "there was an error"
		else:
			if 'gender' in params:
				gender = params['gender']
			else:
				gender = "Female"
			if params['imdb_id'] != "":
				imdb_id = int(links['imdb_id'])
			else:
				imdb_id = None
			if params['twitter'] != "":
				twitter = links['twitter']
			else:
				twitter = None
			if params['wikipedia_link'] != "":
				wikipedia_link = links['wikipedia_link']
			else:
				wikipedia_link = None
			
			
			temp = TemporaryPerson(name = params['name'],gender=gender,imdb_id=imdb_id,twitter=twitter,wikipedia_link=wikipedia_link)
			
			if params['dob'] != "":
				d = params['dob'].split("/")
				temp.dob = date(int(d[0]),int(d[1]),int(d[2]))
			
			
			temp.save()
			
			temp.images = Posters.getPersonTemporaryPicture(temp.name,temp.temp_id)
			
			Posters.makeTemporaryThumbByPic(temp.temp_id,1)
			
			temp.save()
						
			context['person'] = temp
			context['range'] = range(1,temp.images+1)
			
			context['dob'] = "{}/{}/{}".format(temp.dob.year,temp.dob.month,temp.dob.day)
			
			print context
			message = render_to_response('confirmadd.html',context,context_instance=RequestContext(request))
			return HttpResponse(message)
	
	
	
	message = render_to_response('addentity.html',context,context_instance=RequestContext(request))
	return HttpResponse(message)


def sanitizeLinks(params):
	links={}
	
	if params['imdb_id'] != "":
		links['imdb_id'] = re.sub(r'[^\d]', '', params['imdb_id'])
	else:
		links['imdb_id'] = None
		
	links['twitter'] = None
	if params['twitter'] != "":
		if 'http' in params['twitter'] :
			links['twitter'] = params['twitter'].strip('http://twitter.com/')
			links['twitter'] = params['twitter'].strip('http://www.twitter.com')
			
	links['wikipedia_link'] = None
	if params['wikipedia_link'] != "" or '/wiki/' in params['wikipedia_link']:
		if 'http' in params['wikipedia_link']:
			if len(params['wikipedia_link'].split("/wiki/")) > 0:
				links['wikipedia_link'] = params['wikipedia_link'].split("/wiki/")[1]
				
	return links
	###still need to do netflix, tvrage, chickipedia		


def CalculateRating(type,winner,loser,u):
	if type == "movie":
		try:
			winnersc = UserMovieScore.objects.get(uid = u,mid = winner)
		except:
			winnersc = UserMovieScore(uid = u, mid = winner, elorating = 1000,numratings =0,wins=0,losses=0)
			winnersc.save()
		try:
			losersc = UserMovieScore.objects.get(uid = u,mid = loser)
		except:
			losersc = UserMovieScore(uid =u, mid = loser, elorating = 1000,numratings =0,wins=0,losses=0)
			losersc.save()
	
	
		matchup = MovieMatchup.objects.filter((Q(winner=winner) & Q(loser=loser)) | (Q(loser=winner) & Q(winner=loser)))
		if not (matchup.exists()):
	
			score = 200
	
			e = score - round(1 / (1 + math.pow(10, ((losersc.elorating - winnersc.elorating) / 400.0))) * score)
	
			winnersc.numratings = winnersc.numratings + 1
			winnersc.wins = winnersc.wins + 1
	
			winnersc.elorating = winnersc.elorating + e
	
			losersc.numratings = losersc.numratings + 1
			losersc.losses = losersc.losses + 1
	
			losersc.elorating = losersc.elorating - e
	
			matchup = MovieMatchup(winner = winner, loser = loser, uid = u, elo = e)
	
			matchup.save()
	
			winnersc.save()
			losersc.save()
			print winnersc.elorating
			print losersc.elorating
	if type == "person":
			try:
				winnersc = UserPersonScore.objects.get(uid = u,pid = winner)
			except:
				winnersc = UserPersonScore(uid = u, pid = winner, elorating = 1000,numratings =0,wins=0,losses=0)
				winnersc.save()
			try:
				losersc = UserPersonScore.objects.get(uid = u,pid = loser)
			except:
				losersc = UserPersonScore(uid =u, pid = loser, elorating = 1000,numratings =0,wins=0,losses=0)
				losersc.save()
				
			matchup = PersonMatchup.objects.filter((Q(winner=winner) & Q(loser=loser)) | (Q(loser=winner) & Q(winner=loser)))
			if not (matchup.exists()):
				
				score = 200
				
				e = score - round(1 / (1 + math.pow(10, ((losersc.elorating - winnersc.elorating) / 400))) * score)
				winnersc.numratings = winnersc.numratings + 1
				
				winnersc.wins = winnersc.wins + 1
				
				winnersc.elorating = winnersc.elorating + e
				
				losersc.numratings = losersc.numratings + 1
				losersc.losses = losersc.losses + 1
				
				losersc.elorating = losersc.elorating - e
				
				matchup = PersonMatchup(winner = winner, loser = loser, uid = u, elo = e)
				
				matchup.save()
				winnersc.save()
				losersc.save()
				print winnersc.elorating
				print losersc.elorating


def ProfileHandler(request):
	context = {}
	
	#recalculateELO()
	
	u = request.user.get_profile()
	
	peopleratings = PersonMatchup.objects.filter(uid=u).count()
	movieratings = MovieMatchup.objects.filter(uid=u).count()
	
	
	u.global_ratings = peopleratings + movieratings
	u.person_ratings = peopleratings
	u.movie_ratings = movieratings
	
	
	u.save()
	
	#context['user'] = u
	context['top10people'] = UserPersonScore.objects.filter(uid=request.user.get_profile()).order_by('elorating').reverse()[:10]
	context['top10movies'] = UserMovieScore.objects.filter(uid=request.user.get_profile()).order_by('elorating').reverse()[:10]
	template = 'profile.html'
	
	message = render_to_response(template, context,
		context_instance=RequestContext(request))
	return HttpResponse(message)


def GetReplacementPicsHandler(request):
	context = {}
	params= request.GET
	print params
	if 'pid' in params:
		pid = params['pid']
	person = Person.objects.get(pid=pid)
	#send pid over to getter, store in person/(pid)/tmp/1.2.3.4
	#send to browser count of tmp pics, pid, pic, num images for person
	if 'query' in params:
		query = params['query']
	else:
		query = person.name
	if 'newpics' in params:
		picinfo = Posters.getPersonPictureReplacements(query,person.pid)
		
		num_new_pics = len(picinfo)
		context['newpics'] = num_new_pics
		context['picinfo'] = picinfo
		context['tmppics'] = range(1,num_new_pics+1)
		
	context['person'] = person
		
	context['range'] = range(1,person.images+1)
	
	
	message = render_to_response('personreplacepics.html',context,context_instance=RequestContext(request))
	return HttpResponse(message)


def PickThumbnailHandler(request):
	context = {}
	params= request.GET
	print params
	if 'pid' in params:
		pid = params['pid']
	person = Person.objects.get(pid=pid)
	context['person'] = person
		
	context['range'] = range(1,person.images+1)
	
	message = render_to_response('personpickthumb.html',context,context_instance=RequestContext(request))
	return HttpResponse(message)


#JUST WORKS FOR PERSON
def PickThumbnailReturnHandler(request):
	if request.method == 'POST':
		
		params = request.POST
		print params
		pid = int(params['pid'])
		pic_id = int(params['pic_id'])
		dir = "/Users/Jason/person/" + str(pid) + "/"
		Posters.makeThumbByPic(pid,pic_id)
		if pic_id != 1:
			os.rename(dir+str(pic_id)+".jpg",dir+"tmp.jpg")
			os.rename(dir+"1.jpg",dir+str(pic_id)+".jpg")
			os.rename(dir+"tmp.jpg",dir+"1.jpg")
		
	url = '/person?pid=' + str(pid)
	return redirect(url)


#JUST WORKS FOR PERSON
def ProcessNewPicsHandler(request):
	
	
	#"/Users/Jason/person/" + str(id) + '/tmp/links.lnk', "wb" 
	if request.method == 'GET':
		params = request.GET
	elif request.method == 'POST':
		params = request.POST
		print params
		new = 0
		if params['new'] != '':
			new = int(params['new'])
		
		old = int(params['old'])
		pid = int(params['pid'])
		oldchecks = 0
		newchecks = 0
		newindex = []
		oldindex = []
		for i in range(1,new+1):
			check = "new" + str(i)
			if check in params:
				print check
				newchecks +=1
				newindex.append(i)
		for i in range(1,old+1):
			check = "old" + str(i)
			if check in params:
				print check
				oldchecks += 1
				oldindex.append(i)
		dir = "/Users/Jason/person/" + str(pid) + "/"
		if new > 0:
			big_links = pickle.load( open( "/Users/Jason/person/" + str(pid) + '/tmp/links.lnk', "rb" ))
		##remove all old, go thru and rename old 1....oldimages index, 
			##put new in place right after, reset stored images 
		##new more than old, remove old, replace with a new in place,
			##put rest of new in place after
		q = Queue()
		for i in oldindex:
			if (os.path.isfile(dir+str(i)+".jpg")):
				os.remove(dir+str(i)+".jpg")
		for i in range(1,old+1):
			if not (os.path.isfile(dir+str(i)+".jpg")):
				q.put(i)
			elif not q.empty():
				os.rename(dir+str(i)+".jpg",dir+str(q.get())+".jpg")
				q.put(i)
		last = 0
		for i in range(1,old+new+1):
			if os.path.isfile(dir+str(i)+".jpg"):
				last=i
		last+=1
		for j in newindex:
			if not (os.path.isfile(dir+str(i)+".jpg")):
				####dl pic
				print j
				try:
					req = urllib2.Request(big_links[j]['link'], headers={'User-Agent' : "Magic Browser"}) 
					resp = urllib2.urlopen(req)
				except urllib2.URLError, e:
					print "E"
					print e
					if not hasattr(e, "code"):
						print "WHOOPS"
					resp = e
				except urllib2.HTTPError, e:
					print "e"
					if not hasattr(e, "code"):
						print "WHOOPS"
					resp = e
				except urllib2.HTTPException,e:
					print "whoops"
				else:
					contenttype = resp.headers["content-type"]
					print contenttype
					if contenttype=="image/jpeg" or contenttype=="image/jpg" or contenttype=="image/gif" or contenttype=="image/JPEG" or contenttype == "image/png" or contenttype == "image/jpeg; charset=utf-8":
						file = cStringIO.StringIO(resp.read())
				
						#im = Image.open(urllib2.urlopen(big_links[i]['link']))
						im = Image.open(file)
				
						try:
							im.save(dir+str(last)+".jpg","JPEG",optimize=True)
						except IOError:
							if im.mode != "RGB":
							    im = im.convert("RGB")
							im.save(dir+str(last)+".jpg", "JPEG")
						last+=1
		last = 0
		for i in range(1,old+new+1):
			if os.path.isfile(dir+str(i)+".jpg"):
				last=i
			
		p = Person.objects.get(pid=pid)
		p.images=last
		p.image_edit = True
		p.save()
		dir = "/Users/Jason/person/" + str(pid) + "/tmp/"
		if 	os.path.exists(dir):
			shutil.rmtree(dir)
	
#	message = render_to_response('person.html',context,context_instance=RequestContext(request))
###CHANGING DURING MASS EDIT
	
	url = '/person?pid=' + str(p.pid)
#	p = Person.objects.filter(image_edit=False).order_by('?')[0]
#	url = '/editpics?pid=' + str(p.pid)
	
	return redirect(url)


def getMobi():
	for offset in range(400,1700,50):
		url = "http://www.mobygames.com/browse/games/xbox360/offset," + str(offset) + "/so,0a/list-games/"
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
	#	print htmlSource
		divs = root.cssselect("div.molist")
		for d in divs:
			tbody = d.cssselect("tbody")
			for t in tbody:
				trs = t.cssselect("tr")
				for tr in trs:
					tds = tr.cssselect("td")
					publisher = tostring(tds[2])
					if publisher == "<td/>":
						#print "INDIE"
						True
					else:
						title = tostring(tds[0])
						mobilink = title.split("<td><a href=\"")[1].split("\">")[0]
						mobifreebase = mobilink.split("/")
						mobifreebase = mobifreebase[len(mobifreebase)-1]
						#print mobifreebase
						year = tostring(tds[1])
						
						genres = tostring(tds[3]).split(",")
						genre = []
						if genres == '<td/>':
							for g in genres:
								genre.append(g.split("/sheet/")[1].split("/\"")[0])
						publisher = publisher.split("</a>")[0].split("\">")[1]
						title = title.split("</a>")[0].split("\">")[1]
						year = year.split("</a>")[0].split("\">")[1]
						data = {}
						data['title'] = title
						data['year'] = year
						data['genre'] = genre
						data['publisher'] = publisher
						data['mobiid'] = mobifreebase
						addByMobiwData(data)
						
						
						#print title
					for td in tds:
						#print tostring(tds[0])
						True
						#print tostring(td)


def netflix(netflix, id):
	return netflix.catalog.getTitle("http://api.netflix.com/catalog/titles/movies/" + str(id))


def getTwitterInformation():
	persons = Person.objects.exclude(twitter=None)
	count = 0
	list = ""
	for i in persons:
		list += i.twitter + ','
		count +=1
		if count == 95:
			data = Scraper.getTwitterInformation(list)
			#print data
			for t in data:
				try:
					
					p = Person.objects.get(twitter__iexact=t)
					p.twitter = t
					p.twitter_id = data[t]['id']
					p.twitter_followers = data[t]['followers_count']
					p.verified = data[t]['verified']
					p.save()
				except:
					print t
					print "not there"
			list = ""
			count = 0


def getPersonRanks():
	persons = Person.objects.all().order_by('google_search_volume_total').reverse()
	personcount = Person.objects.all().count()
	personsleft = personcount
	for i in persons:
		if i.google_search_volume_total == 0:
			i.google_search_volume_percentile = 0
		else:
			i.google_search_volume_percentile = int((float(personsleft)/float(personcount))*100)
		personsleft -= 1
		try:
			i.save()
		except:
			transaction.rollback()
		else:
			transaction.commit()
	persons = Person.objects.all().order_by('google_results').reverse()
	
	personsleft = personcount
	for i in persons:
		i.google_results_percentile = int((float(personsleft)/float(personcount))*100)
		personsleft -= 1
		try:
			i.save()
		except:
			transaction.rollback()
		else:
			transaction.commit()
			
	persons = Person.objects.all().order_by('bing_results').reverse()
	personsleft = personcount
	for i in persons:
		i.bing_results_percentile = int((float(personsleft)/float(personcount))*100)
		personsleft -= 1
		try:
			i.save()
		except:
			transaction.rollback()
		else:
			transaction.commit()
	persons = Person.objects.all().order_by('twitter_followers').reverse()
	personsleft = personcount
	for i in persons:
		if i.twitter_followers == 0:
			i.twitter_followers_percentile = 0
		else:
			i.twitter_followers_percentile = int((float(personsleft)/float(personcount))*100)
		personsleft -= 1
		try:
			i.save()
		except:
			transaction.rollback()
		else:
			transaction.commit()


def getPersonRankings():
	persons = Person.objects.all()
	for i in persons:
		i.popularity_rating = int(round(float((i.bing_results_percentile + i.google_results_percentile + i.google_search_volume_percentile+i.twitter_followers_percentile)/4)/10))
		try:
			i.save()
		except:
			transaction.rollback()
		else:
			transaction.commit()	


#@transaction.commit_manually
def getSearchAmounts():
	persons = Person.objects.all()
	for i in persons:
		print i.name
		if False:#i.google_search_volume_total == 0:
			g_volume = Scraper.getGoogleSearchVolumeTotal(i.name)
			print g_volume
			if g_volume != None:
				i.google_search_volume_total = g_volume
				try:
					i.save()
				except:
					transaction.rollback()
				else:
					transaction.commit()
		if False:#i.google_search_volume == 0:
			print "trying"
			g_volume = Scraper.getGoogleSearchVolume(i.name)
			print g_volume
			if g_volume != None:
				i.google_search_volume = g_volume
				try:
					i.save()
				except:
					transaction.rollback()
				else:
					transaction.commit()
		if i.google_results == 0:
			g_pop = Scraper.getGooglePopularity(i.name)
			if g_pop != None:
				i.google_results = g_pop
				try:
					i.save()
				except:
					transaction.rollback()
				else:
					transaction.commit()		
		if i.bing_results == 0:
			b_pop = Scraper.getBingPopularity(i.name)
			if b_pop != None:
				i.bing_results = b_pop
				try:
					i.save()
				except:
					transaction.rollback()
				else:
					transaction.commit()


def storeNetflixRatings(userprof):
	file = "/Users/Jason/netflixratings.txt"
	rats = csv.reader(open('/Users/Jason/netflixratings.txt', 'rb'), delimiter='	')
	
	for r in rats:
		tmp = r[1][1:]
		
		title = smart_str(tmp[0:len(tmp)-1])
		rating = int(r[3])
		genre = r[2]
		id = r[0]
		m = None
		try:
			m = Movie.objects.get(netflix_id=id)
		except:
			try:
				netimdb = NetflixIMDb.objects.filter(netflix_id = id)
			except:
				exit()
			for i in netimdb:
				try:
					m = Movie.objects.get(imdb_id = i.imdb_id)
					break;
				except:
					print id
		try:
			userscore = UserMovieScore.objects.get(uid=userprof,mid=m)
		except:
			if m != None:	
				elo = 500
				if int(rating) == 1:
					elo = 600
				elif int(rating) ==2:
					elo= 800
				elif int(rating) ==3:
					elo = 1000
				elif int(rating) ==4:
					elo = 1200
				elif int(rating) ==5:
					elo = 1400
				print elo
				
				userscore = UserMovieScore(uid =userprof, mid = m, elorating = elo, netflix_rating = rating,numratings =0,wins=0,losses=0)
				userscore.save()

				
def findPerson(netflix, arg, id):
    ######################################
    # You can search for people or retrieve
    # a specific person once you know their
    # netflix ID
    ######################################  
    print "*** Searching for %s ***" % arg
    person = netflix.catalog.searchPeople(arg)
    if isinstance(person,dict):
        print simplejson.dumps(person,indent=4)
    elif isinstance(person,list):
        print simplejson.dumps(person[0],indent=4)


def matchupNetflixIMDb():
	APP_NAME   = ''
	API_KEY    = 'smucdewbn2j8rp3rvegmp8y6'
	API_SECRET = 'DvstJpTa7f'
	CALLBACK   = ''
	verbose = False
	
	file = "/Users/Jason/netflixratings.txt"
	ia = IMDb()#'sql', uri='sqlite:/Users/Jason/imdb.db')
	infile = open(file,"r")
	rats = csv.reader(open('/Users/Jason/netflixratings.txt', 'rb'), delimiter='	')
	netflixClient = NetflixClient(APP_NAME, API_KEY, API_SECRET, CALLBACK, verbose)
	
	
	
	
	for r in rats:
		tmp = r[1][1:]
		
		title = smart_str(tmp[0:len(tmp)-1])
		rating = int(r[3])
		genre = r[2]
		id = r[0]
		
		
		
		try:
			NetflixIMDb.objects.get(netflix_id=id)
		except:
			if genre != 'TV':
				result = freebase.mqlread({ "id": None, "constraint:key": { "namespace": "/authority/netflix/movie", "value": str(id) }, 
				  								"key":  [{ "namespace": "/authority/imdb/title", "value": None }] })
				
				
				if result != None:
					imdb_id = int(result['key'][0]['value'].split("tt")[1])
					n = NetflixIMDb(netflix_id=id,imdb_id=imdb_id)
					n.save()
					print "thank heavens freebase"
				else:
					print "doing the horseshit"
				
					movie = netflix(netflixClient,id)
					time.sleep(.20)
					if 'catalog_title' in movie.keys():
						year = movie['catalog_title']['release_year']
					
						#m = Movie(netflix_id=id,title=title,year=year)
						#m.save()
					
						disc = NetflixDisc(movie['catalog_title'],netflixClient)
						try:
							netdirc = disc.getInfo('directors')
						except FieldError as e:
							netdirc = []
							print e
						
						people = []
						person = {}
						if netdirc != {} and netdirc != []:
							#If only one name listed, not a list
							if 'name' in netdirc['people']['person']:
								#print netdirc['people']['person']
								person = {}
								person['id'] = netdirc['people']['person']['id'].split('http://api.netflix.com/catalog/people/')[1]
								person['name'] = unescape(netdirc['people']['person']['name'])
								people.append(person)
							#Else comes as a list so iterate and add all directors
							else:
								for name in netdirc['people']['person']:
									person = {}
									person['id'] = name['id'].split('http://api.netflix.com/catalog/people/')[1]
									person['name'] = name['name']
									people.append(person)
					
						sp = title.split(':')
						#if "Edition" or "Collection" in sp[1]:
						#	title = sp[0]	
						title = title.split('(Widescreen)')[0]
						title = title.split('(Full-screen)')[0]
						print title
						possiblemovies = ia.search_movie(smart_str(title))
						#print possiblemovies
						havematch = False
						for i in possiblemovies:
							if 'year' in i.keys():
								ititle = smart_str(i['title'])
								#print "imdb {} net {} title {}".format(i['year'],m.year,ititle)
								if year-1<=i['year']<= year+1:
									#	Update with more info from imdb
									ia.update(i)
									iname = []
									nname = []
									netdirc = {}
									#If there is a director listed
									if 'director' in i.keys():
										#Add all imdb directors to list
										for name in i['director']:
											iname.append(str(name))
										#Update with more info from netflix
										#dircs = m.director
										print iname
										iuni = []
										for n in iname:
											iuni.append(n.decode('utf-8').lower())
										iunilast = []
										for n in iname:
											iuni.append(n.decode('utf-8').lower())
									
										for p in people:
											dname = smart_str(p['name']).lower()
											if dname.decode('utf-8') in iuni:
												havematch = True
											else:
												if dname.split(' ')[len(dname.split(' '))-1] == iuni[0].split(' ')[len(iuni[0].split(' '))-1]:
													print "last name match"
												havematch = True
											if havematch:
												print "havematch"
												imdbid = ia.get_imdbID(i)
												if imdbid == None:
													print title
													imdbid = ia.title2imdbID(smart_str(title))
												newmatch = NetflixIMDb(netflix_id = id, imdb_id = imdbid)
												#m.imdb_id = ia.get_imdbID(i)
												newmatch.save()
												#Have a match so break out of imdb list
												break
											else:
												print "NOOOOOO MAAAAAATCHHH CHECK MEEEE"
												print "stored: {} matching: {}".format(smart_str(d.name),iname)
							if havematch:
								break 					


def storeAllNetFlix():
	APP_NAME   = ''
	API_KEY    = 'smucdewbn2j8rp3rvegmp8y6'
	API_SECRET = 'DvstJpTa7f'
	CALLBACK   = ''
	verbose = False
		
	file = "/Users/Jason/netflixratings.txt"
	ia = IMDb('sql', uri='sqlite:/Users/Jason/imdb.db')
	infile = open(file,"r")
	rats = csv.reader(open('/Users/Jason/netflixratings.txt', 'rb'), delimiter='	')
	netflixClient = NetflixClient(APP_NAME, API_KEY, API_SECRET, CALLBACK, verbose)
	i=1
	movie = netflix(netflixClient,60002991) 
		
	for r in rats:
		tmp = r[1][1:]
		
		title = smart_str(tmp[0:len(tmp)-1])
		rating = int(r[3])
		genre = r[2]
		id = r[0]
		try:
		    mov = Movie.objects.get(netflix_id=id)
		except:
			if genre != 'TV':
				print ('{} {} {}').format(title,rating,id)
				movie = netflix(netflixClient,id)
				if 'catalog_title' in movie.keys():
					year = movie['catalog_title']['release_year']
				
					noimdb = False
					try:
						n = NetflixIMDb.objects.get(netflix_id=id)
					except:
						noimdb = True
					if noimdb:
						print "noimdb"
					else:
						try:
							mov = Movie.objects.get(imdb_id = n.imdb_id)
						except:
							m = Movie(netflix_id=id,title=title,year=year,imdb_id=n.imdb_id)
							number_of_images = Posters.getPosters(str(n.imdb_id))
							
							m.images = number_of_images
							m.save()
												
							nname = []
							nids = []
							people = []
							person = {}
							for i in movie['catalog_title']['link']:
								if i['title'] == "directors" and 'people' in i:
									if isinstance(i['people']['link'], types.ListType):
										for p in i['people']['link']:
											person = {}
											person['id'] = p['href'].split('http://api.netflix.com/catalog/people/')[1]
											person['name'] = unescape(p['title'])
											people.append(person)
									else:
										person = {}
										person['id'] = i['people']['link']['href'].split('http://api.netflix.com/catalog/people/')[1]
										person['name'] = unescape(i['people']['link']['title'])
										people.append(person)
										
								for i in people:
									try:
									    d = Person.objects.get(netflix_id=i['id'])
									except:
										personInformationGetter(i['id'],i['name'])
										d = Person.objects.get(netflix_id=i['id'])
									m.director.add(d)
								m.save()
							
							people = []
							person = {}
							for i in movie['catalog_title']['link']:
								if i['title'] == "cast" and 'people' in i:
									if isinstance(i['people']['link'], types.ListType):
										for p in i['people']['link']:
											person = {}
											person['id'] = p['href'].split('http://api.netflix.com/catalog/people/')[1]
											person['name'] = unescape(p['title'])
											people.append(person)
									else:
										person = {}
										person['id'] = i['people']['link']['href'].split('http://api.netflix.com/catalog/people/')[1]
										person['name'] = unescape(i['people']['link']['title'])
										people.append(person)
										
								for i in people:
									try:
									    c = Person.objects.get(netflix_id=i['id'])
									except:
										personInformationGetter(i['id'],i['name'])
										c = Person.objects.get(netflix_id=i['id'])
									m.cast.add(c)
								m.save()					
							


@transaction.commit_on_success
def recalculateELO():
	t1 = time.time()
	#ups = UserPersonScore.objects.all()
	#for u in ups:
	#	u.elorating = 1000
	#	u.numratings = 0
	#	u.wins = 0
	#	u.losses = 0
	#	u.save()
	
	userscores = UserPersonScore.objects.update(numratings=0,wins=0,losses=0,elorating=1000)
	
	match = PersonMatchup.objects.all().order_by('matchupid')
	dontcont = False
	for i in match:
		print i.matchupid
		dontcont = False
		score = 100
		#print "loser {}".format(i.loser)
		#print "winner {}".format(i.winner)
		
		try:
			winnersc = UserPersonScore.objects.get(uid = i.uid, pid = i.winner.pid)
		except:
			try:
				winnersc = UserPersonScore(uid = i.uid,pid =i.winner.pid,elorating = 1000)
				winnersc.save()
			except:
				dontcont = True
		try:
			losersc = UserPersonScore.objects.get(uid = i.uid, pid = i.loser.pid)
		except:
			try:
				losersc = UserPersonScore(uid = i.uid,pid =i.loser.pid,elorating = 1000)
				losersc.save()
			except:
				dontcont = True
		
		if dontcont == False:
			
			
			if winnersc.numratings < 10:
				win_score = 200
			elif winnersc.numratings < 50:
				win_score = 160
			else:
				win_score = 100
			if losersc.numratings < 10:
				lose_score = 200
			elif losersc.numratings < 50:
				lose_score = 160
			else:
				lose_score = 100
			
			
			prob = (1 / (1 + math.pow(10, ((losersc.elorating - winnersc.elorating) / 400.0)))) 
			
			win_e = win_score - round(prob * win_score)
			lose_e = lose_score - round(prob * lose_score)
			
			#print win_e
			#print lose_e
			#frac = prob
			#print frac
			
			e = round(prob * 1000) 
			#print e
			
			#e = score - round(1 / (1 + math.pow(10, ((losersc.elorating - winnersc.elorating) / 400.0))) * score)
		
			winnersc.elorating += win_e
			losersc.elorating -= lose_e
			winnersc.wins += 1
			losersc.losses += 1
			
			winnersc.numratings +=1
			losersc.numratings +=1
			
			winnersc.save()
			losersc.save()
			i.probability = prob
			i.w_elo = win_e
			i.l_elo = lose_e
			i.save()
	t2 = time.time()
	
	print t2-t1


def getMissingDirector(m):
	APP_NAME   = ''
	API_KEY    = 'smucdewbn2j8rp3rvegmp8y6'
	API_SECRET = 'DvstJpTa7f'
	CALLBACK   = ''
	verbose = False
		
	netflixClient = NetflixClient(APP_NAME, API_KEY, API_SECRET, CALLBACK, verbose)
	movie = netflix(netflixClient,m.netflix_id)	
	disc = NetflixDisc(movie['catalog_title'],netflixClient)
	try:
		netdirc = disc.getInfo('directors')
	except FieldError as e:
		print e
	people = []
	person = {}
	if netdirc != {} and netdirc != []:
		#If only one name listed, not a list
		if 'name' in netdirc['people']['person']:
			#print netdirc['people']['person']
			person = {}
			person['id'] = netdirc['people']['person']['id'].split('http://api.netflix.com/catalog/people/')[1]
			person['name'] = unescape(netdirc['people']['person']['name'])
			
			people.append(person)
		#Else comes as a list so iterate and add all directors
		else:
			for name in netdirc['people']['person']:
				person = {}
				person['id'] = name['id'].split('http://api.netflix.com/catalog/people/')[1]
				person['name'] = name['name']
				
				people.append(person)
				
		
		for i in people:
			try:
			    d = Director.objects.get(netflix_id=i['id'])
			except:
				d = Director(netflix_id=i['id'],name=i['name'])
				d.save()
			m.director.add(d)
		m.save()


def getImageNumbers():
	movs = Movie.objects.all()
	for i in movs:
		number_of_images = Posters.numPics(str(i.imdb_id))
		i.images = number_of_images
		i.save()


def getFreebaseData(source,value):
	if source == "twitter":
		result = freebase.mqlread({"key": [{ "namespace": "/authority/twitter", "value": value}], "name": None, "/people/person/place_of_birth": None, "/people/person/nationality": [{}], "/people/person/date_of_birth": None, "/people/person/gender": None, "ns0:key": [{}]})
	if source == 'wikipedia':
		result = freebase.mqlread({"key": [{ "namespace": "/wikipedia/en", "value": value}], "name": None, "/people/person/place_of_birth": None, "/people/person/nationality": [{}], "/people/person/date_of_birth": None, "/people/person/gender": None, "ns0:key": [{}]})
		if result == None:
			result = freebase.mqlread({"key": [{ "namespace": "/wikipedia/en_id", "value": value}], "name": None, "/people/person/place_of_birth": None, "/people/person/nationality": [{}], "/people/person/date_of_birth": None, "/people/person/gender": None, "ns0:key": [{}]})
		return result
	if source == 'imdb':
		if 'http' in value:
			value = value.split('/name/')[1].split('/')[0]
			print value
			
		return freebase.mqlread({"key": [{ "namespace": "/authority/imdb/name", "value": value}], "name": None, "/people/person/place_of_birth": None, "/people/person/nationality": [{}], "/people/person/date_of_birth": None, "/people/person/gender": None, "ns0:key": [{}]})
	#make sure it was quotekey
	if source == 'baseballalmanac':
		result = freebase.mqlread({"key": [{ "namespace": "/source/baseball_almanac/players", "value": value}], "name": None, "/people/person/place_of_birth": None, "/people/person/nationality": [{}], "/people/person/date_of_birth": None, "/people/person/profession": [{}], "/people/person/gender": None, "ns0:key": [{}] })
	###add checks to see if empty????
	if source == 'name':
		#changed nationality to have None instead of [{}]
		return freebase.mqlread({"name": value, "/people/person/place_of_birth": None, "/people/person/nationality": [{}], "/people/person/date_of_birth": None, "/people/person/profession": [{}], "/people/person/gender": None, "ns0:key": [{}], "limit":1})
		


def AddByWikiCategory(request):
	if request.method == "POST":
		params = request.POST
		
		try:
			url = re.search(r'Category:(.*)',params['wiki_cat']).group(1)
		except:
			url = params['wiki_cat']
		
		tag = params['tag']
		
		getWikiIdsFromCategoryName(url,tag)
		url = "/addpersonqueue"
		return redirect(url)


def addByMobiwData(data):
	try:
		result = freebase.mqlread({"key": [{ "namespace": "/authority/mobygames/game", "value": str(data['mobiid'])}], "name": None, "/cvg/computer_videogame/uses_game_engine": None, "ns0:key": [{}]})
	except:
		result = None
	if result != None:
		try:
			vg = VideoGame.objects.get(mobygames_id = data['mobiid'])
		except:
			vg = VideoGame(title = data['title'], publisher = data['publisher'], year = data['year'],mobygames_id = data['mobiid'])
			#mobygames_id = models.CharField(max_length=128,null=True,blank=True,unique=True)
			#giantbomb_id = models.CharField(max_length=128,null=True,blank=True,unique=True)
			#imdb_id = models.IntegerField(null=True,blank=True,unique=True)
			#steam_id = models.IntegerField(null=True,blank=True,unique=True)
			#wikipedia_link = models.CharField(max_length=256,null = True,blank = True,unique=True))
			try:
				vg.save()
			except:
				connection._rollback()
		
				print "Unexpected error:", sys.exc_info()
				print "dup"


def addTemporaryFromFreebase(freebase):
	result = freebase
	real = 0
	person = {}
	p = None
	if result != None:
		
		person['wikipedia_link'] = None
		
		#Find first instance of wiki and use that, reason being can be more than one link and the first is usually the best
		for i in result['ns0:key']:
			if i['namespace'] == '/wikipedia/en':
				person['wikipedia_link'] = str(i['value'])
				real += 1
				break
		#Find rest of links
		for i in result['ns0:key']:
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
	print "links {} person is {}".format(real,person)
	
	#If at least one link was found continue adding
	if real>=1:
		#Find if the person is in via their name
		##########Might want to switch to check via DOB to allow for multiple people of same name
		try:
			#,tvrage_id = person['tvrage_id'],netflix_id = person['netflix_id'],imdb_id=person['imdb_id'],wikipedia_link=person['wikipedia_link'],name=result['name']
			p = Person.objects.get(name=result['name'])
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
			if result['/people/person/date_of_birth'] == None:
				result['/people/person/date_of_birth'] = '1000-1-1'
			#If do not have the full dob check to see how much there is
			elif len(result['/people/person/date_of_birth'])<8:
				#Only have year
				if len(result['/people/person/date_of_birth']) <5:
					result['/people/person/date_of_birth'] += "-01-01"
				#Have month but no date
				else:
					result['/people/person/date_of_birth'] += "-01"
			if result['/people/person/gender'] == None:
				result['/people/person/gender'] = "Unknown"
			
			p = None
			p = TemporaryPerson(gender=result['/people/person/gender'],
						dob=result['/people/person/date_of_birth'],)
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
			p.name = result['name']
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
	
	
	

def addFromFreebase(freebase):
	result = freebase
	real = 0
	person = {}
	p = None
	if result != None:
		
		person['wikipedia_link'] = None
		
		#Find first instance of wiki and use that, reason being can be more than one link and the first is usually the best
		for i in result['ns0:key']:
			if i['namespace'] == '/wikipedia/en':
				person['wikipedia_link'] = str(i['value'])
				real += 1
				break
		#Find rest of links
		for i in result['ns0:key']:
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
	print "links {} person is {}".format(real,person)
	
	#If at least one link was found continue adding
	if real>=1:
		#Find if the person is in via their name
		##########Might want to switch to check via DOB to allow for multiple people of same name
		try:
			#,tvrage_id = person['tvrage_id'],netflix_id = person['netflix_id'],imdb_id=person['imdb_id'],wikipedia_link=person['wikipedia_link'],name=result['name']
			p = Person.objects.get(name=result['name'])
			print "already here"
			if 'tvrage_id' in person:
				p.tvrage_id = person['tvrage_id']
			if 'netflix_id' in person:
				p.netflix_id = person['netflix_id']
			if 'imdb_id' in person:
				p.imdb_id = person['imdb_id']
			if 'wikipedia_link' in person:
				p.wikipedia_link = person['wikipedia_link']
			if 'chickipedia_id' in person:
				p.chickipedia_id = person['chickipedia_id']
			if 'twitter' in person:
				p.twitter = person['twitter']
			p.save()
			return p
		except:
			#The name wasn't there
			#If there is no DOB intialize to really old date
			if result['/people/person/date_of_birth'] == None:
				result['/people/person/date_of_birth'] = '1000-1-1'
			#If do not have the full dob check to see how much there is
			elif len(result['/people/person/date_of_birth'])<8:
				#Only have year
				if len(result['/people/person/date_of_birth']) <5:
					result['/people/person/date_of_birth'] += "-01-01"
				#Have month but no date
				else:
					result['/people/person/date_of_birth'] += "-01"
			if result['/people/person/gender'] == None:
				result['/people/person/gender'] = "Unknown"
			
			p = None
			p = Person(gender=result['/people/person/gender'],
						dob=result['/people/person/date_of_birth'],)
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
			p.name = result['name']
			try:
				p.save()
			except:
				connection._rollback()
		
				print "Unexpected error:", sys.exc_info()
				print person
				print len(person)
				print "dup"
			return p
	
	return p


def addByTwitter(id):
	#result = freebase.mqlread({"key": [{ "namespace": "/authority/twitter", "value": id}], "name": None, "/people/person/place_of_birth": None, "/people/person/nationality": [{}], "/people/person/date_of_birth": None, "/people/person/gender": None, "ns0:key": [{}]})
	
	real = 0
	person = {}
	#print result
	if result != None:
		#print result['ns0:key']
		person['wikipedia_link'] = None
		for i in result['ns0:key']:
			if i['namespace'] == '/wikipedia/en':
				person['wikipedia_link'] = str(i['value'])
				real += 1
				break
		for i in result['ns0:key']:
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
	print "links {} person is {}".format(real,person)
	if real>1:
		try:
			#,tvrage_id = person['tvrage_id'],netflix_id = person['netflix_id'],imdb_id=person['imdb_id'],wikipedia_link=person['wikipedia_link'],name=result['name']
			p = Person.objects.get(name=result['name'])
			print "already here"
			if 'tvrage_id' in person:
				p.tvrage_id = person['tvrage_id']
			if 'netflix_id' in person:
				p.netflix_id = person['netflix_id']
			if 'imdb_id' in person:
				p.imdb_id = person['imdb_id']
			if 'wikipedia_link' in person:
				p.wikipedia_link = person['wikipedia_link']
			if 'chickipedia_id' in person:
				p.chickipedia_id = person['chickipedia_id']
			if 'twitter' in person:
				p.twitter = person['twitter']
			p.save()
			return p
		except:
			#print "I EXCEPT SIR"
			if result['/people/person/date_of_birth'] == None:
				result['/people/person/date_of_birth'] = '1000-1-1'
			elif len(result['/people/person/date_of_birth'])<8:
				if len(result['/people/person/date_of_birth']) <5:
					result['/people/person/date_of_birth'] += "-01-01"
				else:
					result['/people/person/date_of_birth'] += "-01"
			if result['/people/person/gender'] == None:
				result['/people/person/gender'] = "Unknown"
			
			p = None
			p = Person(gender=result['/people/person/gender'],
						dob=result['/people/person/date_of_birth'],)
			if 'tvrage_id' in person:
				p.tvrage_id = person['tvrage_id']
			if 'netflix_id' in person:
				p.netflix_id = person['netflix_id']
			if 'imdb_id' in person:
				p.imdb_id = person['imdb_id']
			if 'wikipedia_link' in person:
				p.wikipedia_link = person['wikipedia_link']
			p.name = result['name']
			try:
				p.save()
			except:
				connection._rollback()
		
				print "Unexpected error:", sys.exc_info()
				print person
				print len(person)
				print "dup"
			return p
	return None


def getMovieRankings():
	movies = Movie.objects.all().order_by('imdb_votes').reverse()
	moviecount = Movie.objects.all().count()
	moviesleft = moviecount
	for i in movies:
		
		rating_average = float((i.imdb_rating+i.moviedb_rating+i.rottentomatoes_critics_score+i.rottentomatoes_audience_score))/4
		i.outside_ratings_avg = rating_average
		
		if i.imdb_votes == 0:
			i.imdb_votes_percentile = 0
		else:
			i.imdb_votes_percentile = int((float(moviesleft)/float(moviecount))*100)
		moviesleft -= 1
		try:
			i.save()
		except:
			transaction.rollback()
		else:
			transaction.commit()
	movies = Movie.objects.all().order_by('moviedb_popularity').reverse()
	moviecount = Movie.objects.all().count()
	moviesleft = moviecount
	for i in movies:
		if i.moviedb_popularity == 0:
			i.moviedb_popularity_percentile = 0
		else:
			i.moviedb_popularity_percentile = int((float(moviesleft)/float(moviecount))*100)
		moviesleft -= 1
		try:
			i.save()
		except:
			transaction.rollback()
		else:
			transaction.commit()
	movies = Movie.objects.all().order_by('moviedb_votes').reverse()
	moviecount = Movie.objects.all().count()
	moviesleft = moviecount
	for i in movies:
		if i.moviedb_votes == 0:
			i.moviedb_votes_percentile = 0
		else:
			i.moviedb_votes_percentile = int((float(moviesleft)/float(moviecount))*100)
		moviesleft -= 1
		try:
			i.save()
		except:
			transaction.rollback()
		else:
			transaction.commit()
	movies = Movie.objects.all().order_by('budget').reverse()
	moviecount = Movie.objects.all().count()
	moviesleft = moviecount
	for i in movies:
		if i.revenue == 0:
			i.revenue_percentile = 0
		else:
			i.revenue_percentile = int((float(moviesleft)/float(moviecount))*100)
		moviesleft -= 1
		try:
			i.save()
		except:
			transaction.rollback()
		else:
			transaction.commit()
			
	movies = Movie.objects.all().order_by('outside_ratings_avg').reverse()
	moviecount = Movie.objects.all().count()
	moviesleft = moviecount
	for i in movies:
		if i.outside_ratings_avg == 0:
			i.rating_metric = 0
		else:
			i.rating_metric = int((float(moviesleft)/float(moviecount))*10)
		moviesleft -= 1
		
		percentile_average = float(i.imdb_votes_percentile + i.moviedb_popularity_percentile + i.moviedb_votes_percentile+i.revenue_percentile)/4
		i.popularity_metric = int(round(percentile_average/10))
		
		try:
			print "{} {} {}".format(i.title, percentile_average, i.rating_metric)
		except:
			print "unicode"
		
		try:
			i.save()
		except:
			transaction.rollback()
		else:
			transaction.commit()	


def getExtendedMovieInfo():
	movies = Movie.objects.all()
	
	for i in movies:
		
		if i.moviedb_id == None:
			d = MovieUtilities.getMovieDBInfo(i.imdb_id)
			print d
			if 'id' in d:
				i.moviedb_id = d['id']
			if 'revenue' in d:
				i.revenue = d['revenue']
			if 'budget' in d:
				i.budget = d['budget']
			if 'runtime' in d:
				i.runtime = d['runtime']
			if 'release_date' in d:
				i.release_date = d['release_date']
			if 'popularity' in d:
				print d['popularity']
				print int(round(d['popularity']))
				i.moviedb_pop = int(round(d['popularity']*1000))
			if 'vote_count' in d:
				i.moviedb_votes = d['vote_count']
			if 'vote_average' in d:
				i.moviedb_rating = int(float(d['vote_average'])*10)
			if 'genres' in d:
				for g in d['genres']:
					i.tags.add(g['name'])
					t = MovieTag.objects.get(name=g['name'])
					t.type = "Genre"
					t.save()
		if i.imdb_rating == None:
			d = MovieUtilities.getIMdBMovieInfo(i.imdb_id)
			print d
			if 'data' in d:
				data = d['data']
				if 'certificate' in data:
					i.mpaa_rating = data['certificate']['certificate']
				if 'rating' in data:
					i.imdb_rating = int(float(data['rating'])*10)
				if 'numvotes' in data:
					i.imdb_votes = int(data['numvotes'])
				if 'tagline' in data:
					i.tagline = data['tagline']
				if 'type' in data:
					i.movie_type = data['type']
				try:
					i.save()
				except:
					transaction.rollback()
				else:
					transaction.commit()
			else:
				break
		if i.rottentomatoes_id == None:
			d = MovieUtilities.getRottenTomatoesMovieInfo(i.imdb_id)
			print d
			if 'id' in d:
				i.rottentomatoes_id = d['id']
			if 'ratings' in d:
				i.rottentomatoes_audience_score = d['ratings']['audience_score']
				i.rottentomatoes_critics_score = d['ratings']['critics_score']
			if 'studio' in d:
				i.tags.add(d['studio'])
				t = MovieTag.objects.get(name=d['studio'])
				t.type = "Studio"
				t.save()
			try:
				i.save()
			except:
				transaction.rollback()
			else:
				transaction.commit()
				


def addByWikiID(data):
	id = data
	result = freebase.mqlread({"key": [{ "namespace": "/wikipedia/en_id", "value": id}], "name": None, "/people/person/place_of_birth": None, "/people/person/nationality": [{}], "/people/person/date_of_birth": None, "/people/person/gender": None, "ns0:key": [{}]})
	real = 0
	person = {}
	#print result
	if result != None:
		#print result['ns0:key']
		person['wikipedia_link'] = None
		for i in result['ns0:key']:
			if i['namespace'] == '/wikipedia/en':
				person['wikipedia_link'] = str(i['value'])
				real += 1
				break
		for i in result['ns0:key']:
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
	print "links {} person is {}".format(real,person)
	if real>1:
		try:
			#,tvrage_id = person['tvrage_id'],netflix_id = person['netflix_id'],imdb_id=person['imdb_id'],wikipedia_link=person['wikipedia_link'],name=result['name']
			p = Person.objects.get(name=result['name'])
			print "already here"
			if 'tvrage_id' in person:
				p.tvrage_id = person['tvrage_id']
			if 'netflix_id' in person:
				p.netflix_id = person['netflix_id']
			if 'imdb_id' in person:
				p.imdb_id = person['imdb_id']
			if 'wikipedia_link' in person:
				p.wikipedia_link = person['wikipedia_link']
			if 'chickipedia_id' in person:
				p.chickipedia_id = person['chickipedia_id']
			if 'twitter' in person:
				p.twitter = person['twitter']
			p.save()
			return p
		except:
			#print "I EXCEPT SIR"
			if result['/people/person/date_of_birth'] == None:
				result['/people/person/date_of_birth'] = '1000-1-1'
			elif len(result['/people/person/date_of_birth'])<8:
				if len(result['/people/person/date_of_birth']) <5:
					result['/people/person/date_of_birth'] += "-01-01"
				else:
					result['/people/person/date_of_birth'] += "-01"
			if result['/people/person/gender'] == None:
				result['/people/person/gender'] = "Unknown"
			
			p = None
			p = Person(gender=result['/people/person/gender'],
						dob=result['/people/person/date_of_birth'],)
			if 'tvrage_id' in person:
				p.tvrage_id = person['tvrage_id']
			if 'netflix_id' in person:
				p.netflix_id = person['netflix_id']
			if 'imdb_id' in person:
				p.imdb_id = person['imdb_id']
			if 'wikipedia_link' in person:
				p.wikipedia_link = person['wikipedia_link']
			p.name = result['name']
			try:
				p.save()
			except:
				connection._rollback()
		
				print "Unexpected error:", sys.exc_info()
				print person
				print len(person)
				print "dup"
			return p
	return None


def getDOBandBiofromWikipedia(wiki_link):
	
	cpurl = "http://en.wikipedia.org/w/api.php?action=parse&prop=text&page=" + wiki_link + "&format=json"
	cpurl = cpurl.replace(" ", "%20")
	headers = {
		'User-Agent' : "Magic Browser",
		'Connection':	'Keep-Alive',
	}
	#cpurl = urllib.urlencode(cpurl)
	data=""
	req = urllib2.Request(cpurl.encode('utf-8'), data, headers)
	#urlsvisited.append(cpurl)
	f = urllib2.urlopen(req)
	htmlSource = f.read()
	f.close()
	dob = ""
	redirect = None
	if len(htmlSource.split('REDIRECT'))>1:
		redirect = htmlSource.split('<a href=\\"\\/wiki\\/')[1].split('\\\"')[0]
		
		cpurl = "http://en.wikipedia.org/w/api.php?action=parse&prop=text&page=" + redirect + "&format=json"
		data = ""
		req = urllib2.Request(cpurl, data, headers)
		#urlsvisited.append(cpurl)
		f = urllib2.urlopen(req)
		htmlSource = f.read()
		f.close()
	#print len(htmlSource.split('(<span class=\"bday\">'))
	if len(htmlSource.split('<p><b>'))>1:
		bio = htmlSource.split('<p><b>')[1].split('<\/p>')[0].replace('\/','/').replace("\\\"","\"")
		
		bio = re.sub('<[^<]+?>', '', bio)
		bio = re.sub('\[\d\]','',bio)
		i.bio = unescape(i.bio).encode("utf-8")
	
		try:
			bio = bio.decode('unicode-escape')
		except:
			print "decode error"
	else:
		bio = ""
	print bio
	
	if len(htmlSource.split('<span class=\\"bday\\">'))>1:
		dob = 0
		if len(htmlSource.split('<span class=\\"bday\\">')[1].split('<\/span>'))>1:
			dob = htmlSource.split('<span class=\\"bday\\">')[1].split('<\/span>')[0]
		else:
			dob = 0
	return {'dob':dob,'bio':bio,'redirect':redirect}


def processIMDbList(lnk):
	h = httplib2.Http()
	headers, data = h.request(lnk)
	data = cStringIO.StringIO(data)
	
	list = csv.reader(data)
	
	for i in list:
		if len(i)>1:
			addByIMDb(i[1])
	
	


def addByIMDb(id):
	im = id
	result = freebase.mqlread({"key": [{ "namespace": "/authority/imdb/name", "value": id}], "name": None, "/people/person/place_of_birth": None, "/people/person/nationality": [{}], "/people/person/date_of_birth": None, "/people/person/gender": None, "ns0:key": [{}]})
	real = 0
	person = {}
	if result != None:
		#print result['ns0:key']
		person['wikipedia_link'] = None
		for i in result['ns0:key']:
			if i['namespace'] == '/wikipedia/en':
				person['wikipedia_link'] = str(i['value'])
				real += 1
				break
		for i in result['ns0:key']:
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
	#print "links {} person is {}".format(real,person)
	if real>1:
		try:
			#,tvrage_id = person['tvrage_id'],netflix_id = person['netflix_id'],imdb_id=person['imdb_id'],wikipedia_link=person['wikipedia_link'],name=result['name']
			p = Person.objects.get(name=result['name'])
			print "already here"
			if 'tvrage_id' in person:
				p.tvrage_id = person['tvrage_id']
			if 'netflix_id' in person:
				p.netflix_id = person['netflix_id']
			if 'imdb_id' in person:
				p.imdb_id = person['imdb_id']
			if 'wikipedia_link' in person:
				p.wikipedia_link = person['wikipedia_link']
			if 'chickipedia_id' in person:
				p.chickipedia_id = person['chickipedia_id']
			if 'twitter' in person:
				p.twitter = person['twitter']
			p.save()
		except:
			print "I EXCEPT SIR"
			if result['/people/person/date_of_birth'] == None:
				result['/people/person/date_of_birth'] = '1000-1-1'
			elif len(result['/people/person/date_of_birth'])<8:
				if len(result['/people/person/date_of_birth']) <5:
					result['/people/person/date_of_birth'] += "-01-01"
				else:
					result['/people/person/date_of_birth'] += "-01"
			if result['/people/person/gender'] == None:
				result['/people/person/gender'] = "Unknown"
			
			p = None
			p = Person(gender=result['/people/person/gender'],
						dob=result['/people/person/date_of_birth'],)
			if 'tvrage_id' in person:
				p.tvrage_id = person['tvrage_id']
			if 'netflix_id' in person:
				p.netflix_id = person['netflix_id']
			if 'imdb_id' in person:
				p.imdb_id = person['imdb_id']
			if 'wikipedia_link' in person:
				p.wikipedia_link = person['wikipedia_link']
			p.name = result['name']
			try:
				p.save()
			except:
				connection._rollback()
		
				print "Unexpected error:", sys.exc_info()
				print person
				print len(person)
				print "dup"
	return True


def addByName(name):
	ia = IMDb()
	id = 0
	result = {}
	try:
		result = freebase.mqlread({"name": name, "/people/person/place_of_birth": None, "/people/person/nationality": [{}], "/people/person/date_of_birth": None, "/people/person/profession": [{}], "/people/person/gender": None, "ns0:key": [{}] })
	except:
		True
	if result == {}:
		people = ia.search_person(smart_str(name))
		for p in people:
			id = 'nm' + ia.get_imdbID(p)
			try:
				result = freebase.mqlread({"key": [{ "namespace": "/authority/imdb/name", "value": id}], "name": None, "/people/person/place_of_birth": None, "/people/person/nationality": [{}], "/people/person/date_of_birth": None, "/people/person/profession": [{}], "/people/person/gender": None, "ns0:key": [{}]})
				break
			except:
				print "{} didnt have imdb".format(p.name)
	elif result == None:
		people = ia.search_person(smart_str(name))
		for p in people:
			id = 'nm' + ia.get_imdbID(p)
			try:
				result = freebase.mqlread({"key": [{ "namespace": "/authority/imdb/name", "value": id}], "name": None, "/people/person/place_of_birth": None, "/people/person/nationality": [{}], "/people/person/date_of_birth": None, "/people/person/profession": [{}], "/people/person/gender": None, "ns0:key": [{}]})
				break
			except:
				print "{} didnt have imdb".format(p.name)
		print result
		print id
	if result == None:
		return None
		
	real = 0
	person = {}
	if result != None:
		person['wikipedia_link'] = None
		for i in result['ns0:key']:
			if i['namespace'] == '/wikipedia/en':
				person['wikipedia_link'] = str(i['value'])
				real += 1
				break
		for i in result['ns0:key']:
			if i['namespace'] == '/authority/imdb/name':
				person['imdb_id'] = int(i['value'].split('nm')[1])
				real += 1
			if i['namespace'] == '/authority/tvrage/person':
				person['tvrage_id'] = int(i['value'])
				real +=1
			if i['namespace'] == '/authority/netflix/role':
				person['netflix_id'] = int(i['value'])
				real += 1
	print "links {} person is {}".format(real,person)
	if real>1:
		try:
			#,tvrage_id = person['tvrage_id'],netflix_id = person['netflix_id'],imdb_id=person['imdb_id'],wikipedia_link=person['wikipedia_link'],name=result['name']
			p = Person.objects.get(name=name)
			print "already here"
		except:
			if result['/people/person/date_of_birth'] == None:
				result['/people/person/date_of_birth'] = '1000-1-1'
			elif len(result['/people/person/date_of_birth'])<8:
				if len(result['/people/person/date_of_birth']) <5:
					result['/people/person/date_of_birth'] += "-01-01"
				else:
					result['/people/person/date_of_birth'] += "-01"
			if result['/people/person/gender'] == None:
				result['/people/person/gender'] = "Unknown"
			
			p = None
			p = Person(gender=result['/people/person/gender'],
						dob=result['/people/person/date_of_birth'],)
			if 'tvrage_id' in person:
				p.tvrage_id = person['tvrage_id']
			if 'netflix_id' in person:
				p.netflix_id = person['netflix_id']
			if 'imdb_id' in person:
				p.imdb_id = person['imdb_id']
			if 'wikipedia_link' in person:
				p.wikipedia_link = person['wikipedia_link']
			p.name = result['name']
			try:
				p.save()
			except:
				connection._rollback()
		
				print "Unexpected error:", sys.exc_info()
				print person
				print len(person)
				print "dup"
	return True


def processList():
	file = "/Users/Jason/rankyourfavs/2011maximhot100.txt"
	
	l = csv.reader(open(file, 'rb'), delimiter='	')
#	try:
		#li = PersonList.objects.get(list="2011 Maxim Hot 100")
#	except:
		#li = PersonList(list="2011 Maxim Hot 100")
		#li.save()
	count = 0
	for i in l:
		name = i[0].split('. ')[1]
		try:
			p = Person.objects.get(name=name)
			count +=1
			li.members.add(p)
		except:
			print "{} no one home".format(name)
			print  addByName(name)
			
			
	li.save()
	
	for i in li.members.all():
		print "yo {}".format(smart_str(i.name))
		
	print count
		


def getMissingNames():
	twitter = {'Leonard Nimoy': 'TheRealNimoy', 'Norm MacDonald': 'normmacdonald', 'Bret Michaels': 'bretmichaels', 'David Faustino': 'DavidFaustino', 'Kat Von D': 'thekatvond', 'Reba McEntire': 'reba', 'Eden Riegel': 'edenriegel', 'Tyra Banks': 'tyrabanks', 'Carlos Mencia': 'carlosmencia', 'Beyonce Knowles': 'beyonce', 'Pamela Anderson': 'PamelaDAnderson', 'Lauren Conrad': 'LaurenConrad','Tyrese Gibson': 'Tyrese4ReaL', 'Haylie Duff': 'HaylieK', 'Kellan Lutz': 'kellanlutz', 'Chilli': 'officialchilli', 'Billy Ray Cyrus': 'billyraycyrus', 'Diane Farr': 'GetDianeFarr', 'Omar Epps': 'omarepps', 'Austin Butler': 'Austin_Butler', 'Rev Run': 'RevRunWisdom', 'Meagan Good': 'MeaganGood', 'Sharon Lawrence': 'sharonlawrence', 'Eva Longoria': 'EvaLongoria', 'Daniel Tosh': 'danieltosh', 'Jonah Hill': 'JonahHill', 'Stephen Colbert': 'StephenAtHome', 'Tyler Hilton': 'tylerhilton', 'Kevin Smith': 'ThatKevinSmith', 'Demetria Lovato': 'ddlovato', 'Busta Rhymes': 'BusaBusss', 'Wes Craven': 'wescraven', 'Tom Felton': 'TomFelton', 'Queen Latifah': 'IAMQUEENLATIFAH', 'Ellen DeGeneres': 'TheEllenShow', 'Mariel Hemingway': 'MarielHemingway', 'Elizabeth Taylor': 'DameElizabeth', 'COMMON': 'common', 'Elizabeth Hurley': 'ElizabethHurley', 'CedEntertainer': 'CedEntertainer', 'Breckin Meyer': 'breckinmeyer', 'JoAnna Garcia': 'JoAnnaLGarcia', 'Charlie Sheen': 'charliesheen', 'Zach Galifianakis': 'galifianakisz', '50cent': '50cent', 'Ashley Tisdale': 'ashleytisdale', 'Adam Carolla': 'adamcarolla', 'Jerry Ferrara': 'jerrycferrara', 'Missy Peregrym': 'mperegrym', 'Kiefer Sutherland': 'RealKiefer', 'Frank Caliendo': 'FrankCaliendo', 'Tichina Arnold': 'TichinaArnold', 'Shannon Elizabeth': 'ShannonElizab', 'Bill Cosby': 'BillCosby', 'Jeffrey Donovan': 'Jeffrey_Donovan', 'Hill Harper': 'hillharper', 'Ming-Na ': 'MingNa', 'Soleil Moon Frye': 'moonfrye', 'MichelleTrachtenberg': 'RealMichelleT', 'Milla Jovovich': 'MillaJovovich', 'Ali Landry': 'alilandry', 'Hugh Hefner': 'hughhefner', 'Eve': 'TheRealEve', 'Blair Underwood': 'BlairUnderwood', 'Sara Rue': 'SARARUEFORREAL', 'Amanda Bynes': 'chicky', 'Ashlee Simpson Wentz': 'ashsimpsonwentz', 'Chad Michael Murray': 'ChadMMurray', 'Ludacris': 'ludajuice', 'Arsenio Hall': 'ArsenioOFFICIAL', 'Mandy Moore': 'TheMandyMoore', 'Goldie Hawn': 'goldiehawn', 'Jennifer Love Hewitt': 'TheReal_Jlh', 'Dwayne Johnson': 'TheRock', 'Chris Colfer': 'chriscolfer', 'Mark-Paul Gosselaar': 'MP_Gosselaar', 'Jeri Ryan': 'JeriLRyan', 'Sophia Bush': 'SophiaBush', 'Margaret Cho': 'margaretcho', 'Tina Fey': 'tinafey', 'Mitchel Musso': 'mitchelmusso', 'Eric Stonestreet': 'ericstonestreet', 'Autumn Reeser': 'autumnreeser', 'Patricia Heaton': 'PatriciaHeaton', 'Larry The Cable Guy': 'GitRDoneLarry', 'Allison Munn': 'allisonmunn', 'Hal Sparks': 'HalSparks', 'John Cusack': 'johncusack', 'Chanel': 'chanelwestcoast', 'TomCruise.com ': 'TomCruise', 'Kelsey Grammer': 'Kelsey_Grammer', 'Tom Hanks': 'tomhanks', 'Austin Nichols': 'AUS10NICHOLS', 'Tiffani Thiessen': 'TAThiessen', 'Hugh Jackman': 'RealHughJackman', 'Gabrielle Union': 'itsgabrielleu', 'Danny Masterson': 'dannymasterson', 'Selena Gomez': 'selenagomez', 'Shayne Lamas': 'ShayneDahlLamas', 'Peter Facinelli': 'peterfacinelli', 
				'Stacy Keibler': 'StacyKeibler', 'olivia wilde': 'oliviawilde', 'Sarah Shahi': 'onlysarahshahi', 'Ashley Benson': 'AshBenzo', 'Elisa Donovan': 'RedDonovan', 'Dave Foley': 'DaveSFoley', 'Steve Martin': 'SteveMartinToGo', ' Vanessa Williams': 'vwofficial', 'MR OMARION ': '1Omarion', 'Donnie Wahlberg': 'DonnieWahlberg', 'James Franco': 'jamesfranco', 'Bam Margera': 'BAM__MARGERA', 'Ralph Macchio': 'ralphmacchio', 'Brody Jenner': 'BrodyJenner', 'Janet Jackson': 'JanetJackson', 'jennettemccurdy': 'jennettemccurdy', 'Kelly Ripa': 'KellyRipa', 'Greg Behrendt': 'gregbehrendt', 'Jessica Stroup': 'JessicaLStroup', 'Brittany Snow': 'Brittanysnow', 'Jared Leto': 'jaredleto', 'Jennifer Morrison': 'jenmorrisonlive', 'Jessica Lowndes': 'realjlowndes', 'Carter Jenkins': 'CarterJenkins', 'Ethan Suplee': 'EthanSuplee', 'Kristen Bell ': 'IMKristenBell', 'Kevin Nealon': 'kevin_nealon', 'Jack Osbourne': 'MrJackO', 'David Hasselhoff': 'DavidHasselhoff', 'Stephen Colletti': 'StephenColletti', 'Emmanuelle Chriqui': 'echriqui', 'Sasha Grey': 'SashaGrey', 'Stephanie Pratt': 'stephaniepratt', 'Jenna Dewan-Tatum': 'jennaldewan', 'Kristin Chenoweth': 'KChenoweth', 'Hilary Duff': 'HilaryDuff', 'Julie Benz': 'juliebenz', 'Constance Marie': 'goconstance', 'Kourtney Kardashian': 'KourtneyKardash', 'Jesse Tyler Ferguson': 'jessetyler', 'Ivanka Trump': 'IvankaTrump', 'Rob Dyrdek': 'robdyrdek', 'William Shatner': 'WilliamShatner', 'Kendra Wilkinson': 'KendraWilkinson',
				 'Antwon Tanner': 'antwon_tanner', 'Adam Savage': 'donttrythis', 'Lea Michele': 'msleamichele', 'James Van Der Beek': 'vanderjames', 'Tahj Mowry': 'Tahj_Mowry', 'Kim Kardashian': 'KimKardashian', 'Paul Reiser': 'PaulReiser', 'Emmy Rossum': 'emmyrossum', 'Dane Cook': 'danecook', 'Tori Spelling': 'torianddean', 'Miracle Laurie': 'miraclelaurie', 'Chris Rock': 'chrisrock', 'Denise Richards': 'DENISE_RICHARDS', 'Dawn Richard': 'DawnRichard', 'Joe Pantoliano': 'NKMToo', 'Katie Cassidy': 'MzKatieCassidy', 'Mallika Sherawat': 'MallikaLA', 'Snoop Dogg': 'snoopdogg', 'Donny Osmond': 'donnyosmond', 'Dana Delany': 'DanaDelany', 'schwim': 'DavidSchwimmer', 'David Blue': 'DavidBlue', 'Paris Hilton': 'ParisHilton', 'Jim Carrey': 'JimCarrey', 'Marcia Cross': 'ReallyMarcia', 'Brande Roderick': 'brandenroderick', 'Britney Spears': 'britneyspears', 'Michael Madsen': 'MichaelMadsen', 'Joe Rogan': 'joerogan', 'David Arquette': 'davidarquette', 'Busy Philipps': 'Busyphilipps25', 'Pam Grier': 'PamGrier', 'Chrishell Stause': 'Chrishell7', 'Melanie Brown': 'OfficialMelB', 'Ben Stiller': 'RedHourBen', 'Kate Walsh': 'katewalsh', 'Penn Jillette': 'pennjillette', 'Sasha Alexander': 'SashaAlexander1', 'Elizabeth Banks': 'ElizabethBanks', 'David Boreanaz': 'David_Boreanaz', 'Debi Mazar': 'debimazar', 'Marie Osmond': 'marieosmond', 'Shanna Moakler': 'ShannaMoakler', 'Nia Vardalos': 'NiaVardalos', 'Cher': 'cher', 'Fran Drescher': 'frandrescher', 'Zachary Levi': 'ZacharyLevi', 'Drew Carey': 'TPIRhost', 'Demi Moore': 'mrskutcher', 'Mena  Suvari': 'mena13suvari', 'Padma Lakshmi': 'PadmaLakshmi', 'India de Beaufort': 'Indiadebeaufort', 'Kevin Pollak': 'kevinpollak', 'Russell Crowe': 'russellcrowe', 'Amber Patrice Riley': 'MsAmberPRiley', 'Holly Marie Combs': 'HDonoho', 'Seth Green': 'SethGreen', 'Elizabeth Berkley': 'ElizBerkley', 'Ryan Cabrera': 'ryan_cabrera', 'Travis Barker': 'travisbarker', 'Channing Tatum': 'channingtatum', 'Jeremy Piven': 'jeremypiven', 'Ashley Jones': 'AshleyAJones', 'Jason Biggs': 'biggsjason', 'Bridget Marquardt': 'BunnyBridget', 'Michael Ian Black': 'michaelianblack', 'Khloe Kardashian': 'KhloeKardashian', 'Angela Renee Simmons': 'AngelaSimmons', 'Minka Kelly': 'minkakelly', 'Leslie Grossman': 'MissLeslieG', 'Vivica A. Fox': 'MsVivicaFox', 'P. Diddy': 'iamdiddy', 'Kelly Rowland': 'KELLYROWLAND', 'Emily Osment': 'EmilyOsment', 'Marlee Matlin': 'MarleeMatlin', 'Seth Meyers': 'sethmeyers21', 'Dianna Agron': 'alittlelamb', 'Nick Cannon': 'NickCannon', 'Kirstie Alley': 'kirstiealley', 'Rebecca Mader': 'bexmader', 'Kellie Martin': 'Kellie_Martin', 'George Lopez': 'georgelopez', 'Peter Andre': 'MrPeterAndre', 'Dolly Parton': 'Dolly_Parton', 'Greg Grunberg': 'greggrunberg', 'Frankie Muniz': 'frankiemuniz', 'Holly Robinson Peete': 'hollyrpeete', 'Shannon Tweed': 'shannonleetweed', 'Raven-Symone`': 'MissRavenSymone', 'Michelle Rodriguez': 'MRodOfficial', 'Jon Favreau': 'Jon_Favreau', 'Ron Howard': 'RealRonHoward', 'Zachary Quinto': 'ZacharyQuinto', 'T.I.': 'Tip', 'Hank Azaria': 'HankAzaria', 'Ryan Sheckler': 'RyanSheckler', 'Bill Goldberg': 'therealgoldberg', 'Ne-Yo': 'NeYoCompound', 'Whitney Port': 'WhitneyEVE', 'Christian Serratos': 'cserratos', 'Dina Meyer': 'DinaMeyer', 'ICE T': 'FINALLEVEL', 'Kathy Najimy': 'kathynajimy', 'Taylor Momsen': 'taylormomsen', 'Lou Diamond Phillips': 'LouDPhillips', 'Rob Kardashian': 'RobKardashian', 'LL Cool J': 'llcoolj', 'oliviamunn': 'oliviamunn', 'Jackie Collins': 'jackiejcollins', 'Ken Jeong': 'kenjeong', 'Wilmer Valderrama': 'WillyVille', 'Jason Bateman': 'batemanjason', 'Pauley Perrette': 'PauleyP', 'Nathan Fillion': 'NathanFillion', 'Eliza Dushku': 'elizadushku', 'andy dick': 'andydick', 'Kyra Sedgwick': 'kyrasedgwick', 'Alyssa Milano': 'Alyssa_Milano', 'Mariah Carey': 'MariahCarey', 'Carrie Fisher': 'CarrieFFisher', 'Amy Brenneman': 'TheAmyBrenneman', 'Jessica Alba': 'jessicaalba', 'Stacey Dash': 'REALStaceyDash', 'David Spade': 'davidspade', 'Boris Kodjoe': 'BorisKodjoe', 'spencer pratt ': 'spencerpratt', 'Shenae Grimes': 'shenaeSG', 'Aziz Ansari': 'azizansari', 'Marlon Wayans': 'MARLONLWAYANS', 'Bruce Jenner': 'BruceJennerFans', 'Mario Lopez': 'MarioLopezExtra', 'Miley Cyrus': 'mileycyrus', 'Ricki Lake': 'Msrickilake', 'Jennie Garth': 'jenniegarth', 'Verne Troyer': 'VerneTroyer', 'Fred Savage': 'thefredsavage', 'Jennifer Lopez': 'JLo', 'Minnie Driver': 'driverminnie', 'Maria Menounos': 'mariamenounos', 'Dog The Bounty Hunter': 'DogBountyHunter', 'Brooklyn Decker': 'BrooklynDDecker', 'Michael Chiklis': 'MichaelChiklis', 'Tracy Morgan': 'RealTracyMorgan', 'Pee-wee Herman': 'peeweeherman', 'John Stamos': 'JohnStamos', 'Marshall Mathers': 'Eminem', 'christina applegate': '1capplegate', 'Katt Williams': 'KattPackAllDay', 'Christopher Gorham': 'Chris_Gorham', 'Dax Shepard': 'daxshepard1', 'Neil Patrick Harris': 'ActuallyNPH', 'Rachael Leigh Cook': 'RachaelLCook', 'Allison Mack': 'allisonmack', 'RayJ': 'RayJ', 'Anthony Edwards': 'anthonyedwards', 'Kaley Cuoco': 'KaleyCuoco', 'Jessica Karen Szohr': 'JessicaKSzohr', 'Zach Braff': 'zachbraff', 'Rainn Wilson': 'rainnwilson', 'Bill Engvall': 'billengvall', 'Matthew Perry': 'langfordperry', 'Jessica Simpson': 'JessicaSimpson', 'Edward Norton': 'EdwardNorton', 'Michael Steger': 'MichaelStegerJr', 'Tristan Wilds': 'tristanwilds', 'Gene Simmons': 'genesimmons', 'Adrian Grenier': 'adriangrenier', 'Zoe Saldana': 'zoesaldana', 'Virginia Madsen': 'madlyv', 'Lauren London': 'MsLaurenLondon', 'Alison Sweeney': 'Ali_Sweeney', 'Jamie Kennedy': 'jamiekennedy', 'Danneel Harris': 'DanneelHarris', 'Tisha Campbell': 'TishaCampblMrtn', 'Nick Lachey': 'NickSLachey', 'Alyson Hannigan': 'alydenisof', 'Kristin Davis': 'KristinDavis', 'Matt Lanter': 'MattLanter', 'Lisa Kudrow': 'LisaKudrow', 'Jake T. Austin': 'JakeTAustin', 'Alicia Silverstone': 'AliciaSilv', 'Leah Remini': 'LeahRemini', 'Jason Mewes': 'JayMewes', 'Jana Kramer': 'kramergirl', 'Shannen Doherty': 'DohertyShannen', 'Rosario Dawson': 'rosariodawson', 'Kelly osbourne': 'MissKellyO', 'Rita Wilson': 'RitaWilson', 'Stephen Baldwin': 'FREAKSB', 'Alanis Morissette': 'morissette', 'Kristin Cavallari': 'KristinCav', 'Audrina Patridge': 'OfficialAudrina', 'Angie Harmon': 'Angie_Harmon', 'Sofia Vergara': 'SofiaVergara', 'AnnaLynne McCord': 'IAMannalynnemcc', 'Bob Saget': 'bobsaget', 'Nicole Richie': 'nicolerichie', 'Leonardo DiCaprio': 'LeoDiCaprio', 'Shaq': 'THE_REAL_SHAQ', 'Colin Hanks': 'Colin_Hanks', 'Brooke Hogan': 'MizzHogan', 'Shiri Appleby': 'ShiriAppleby', 'Melissa Joan Hart': 'MellyJHart', 'Tony Danza': 'TonyDanza', 'Jenna  Ushkowitz': 'IJennaUsh', 'Ashley Greene': 'AshleyMGreene', 'Sara Gilbert': 'THEsaragilbert', 'Denise Vasi': 'denisevasi', 'Tia Mowry': 'TiaMowry', 'Aiden Turner': 'aidenturner', 'Nick Zano': 'NICKZANO', 'Aisha Tyler': 'aishatyler', 'Lindsay Lohan': 'sevinnyne6126', 'Jimmy Fallon': 'jimmyfallon', 'John Cleese': 'JohnCleese', 'Sarah Silverman': 'SarahKSilverman', 'Frankie Delgado': 'frankiedelgado', 'Daniela Ruah': 'DanielaRuah', 'Tatyana Ali': 'OfficialTatyana', 'Holly Madison': 'hollymadison123',  'Candace Cameron Bure': 'candacecbure', 'Kathy Ireland': 'kathyireland', 'Mark Salling': 'Mark_Salling', 'Justin Timberlake ': 'jtimberlake', 'Tyler Perry': 'tylerperry', 'Adrienne Bailon': 'Adrienne_Bailon', 'Jason Ritter': 'JasonRitter', 'Marisa Tomei': 'marisatomei', 'Jamie Foxx': 'iamjamiefoxx', 'Ice Cube': 'icecube', 'Lo Bosworth': 'LoBosworth', 'Rose McGowan': 'rosemcgowan', 'Gary Sinise': 'GarySinise', 'Kevin Spacey': 'KevinSpacey', 'Leighton Meester': 'itsmeleighton', 'Bethany Joy Galeotti': 'BethanyGaleotti', 'Ashton Kutcher': 'aplusk', 'Al Yankovic': 'alyankovic', 'Henry Winkler': 'hwinkler4real', 'David Charvet': 'davidcharvet', 'Lisa Rinna': 'lisarinna', 'Jaime King': 'Jaime_King', 'Ellen Page': 'EllenPage', 'Valerie Bertinelli': 'Wolfiesmom', 'Billy Crystal': 'BillyCrystal', 'Joan Rivers': 'Joan_Rivers', 'Wesley Jonathan': 'WesleyJonathan', 'Kunal Nayyar': 'kunalnayyar', 'Helen Hunt': 'HelenHunt', 'Dr. Drew': 'drdrew', 'Donald Faison': 'donald_faison', 'Tamera Mowry': 'TameraMowryTwo', 'Steven Weber': 'TheStevenWeber', 'Joshua Malina': 'JoshMalina', 'Jenny McCarthy': 'JennyfromMTV', 'Ozzy Osbourne': 'OfficialOzzy', 'Heidi Montag': 'heidimontag', 'Michael Strahan': 'michaelstrahan'}
	twitter2 = {'Jessica Drake': 'thejessicadrake', 'Brittney Skye': 'brittneyskye69', 'Alexis Golden': 'AlexisGoldenXXX', 'Jayla Starr': 'JaylaStarr', 'Paris Hilton': 'ParisHilton', 'Charlee Chase': 'charlee_chase', 'Ricki White': 'RealRickiWhite', 'Phoenix Marie': 'PMarizzle', 'Kendra Jade Rossi': 'kendrajaderossi', 'Savanna Samson': 'therealsavanna', 'isis taylor': 'isistaylor', 'Kristina Rose': 'KristinaRosexxx', 'Abbey Brooks': 'AbbeyBrooksXXX', 'Kim Kardashian': 'KimKardashian', 'Amber Rayne': 'Amber_Raynexxx', 'Dakota Rae Patrick': 'DakotaRae', 'Monique Alexander': 'moniquealexande', 'Mariah Milano': 'mariahmilanoxxx', 'Brooke Haven ': 'brookehavenxxx', 'Amber Chase': 'amberchase', 'Flower Tucci': 'flowertucci', 'Dylan Ryder': 'dylanryderxxx', 'Lisa Ann': 'thereallisaann', 'Lexi Love': 'TheLexiLove', 'Sandee Westgate': 'sandeewestgate', 'Raven Alexis': 'ravenalexis', 'Taylor Wane': 'taylorwane69', 'Eva Angelina': 'evaangelinaxxx', 'Carly Parker': 'CarlyParkerXXX', 'Tara Lynn Foxx': 'TaraLynnFoxx', 'Sasha Grey': 'SashaGrey', 'Teagan Presley': 'MsTeagan', 'Mercedes Ashley': 'mercedesashley', 'Lacey Duvalle': 'LaceyDuvalleXXX', 'Pamela Anderson': 'PamelaDAnderson', 'TJ Cummings': 'XXXTJCummings', 'Angela Aspen': 'angelaaspenxxx', 'Jenny Hendrix': 'jennyhendrix', 'Madison Mitchell ': 'MadisonMitchell', 'Courtney Cummz': 'CourtneyCummz', 'Kerry Louise': 'kerrylouisexxx', 'Gina Lynn ': 'theginalynn', 'Kiara Diane': 'kiaradianexxx', 'Tyler Faith': 'tylerfaith', 'Kelly Divine': 'KellyDivine', 'Rachel Starr': 'RachelStarrxxx', 'Nina Mercedez': 'nina_mercedez', 'Sara Jay': 'SaraJayXXX', 'Bridgette B.': 'spanishdollxxx', 'Alexis Amore': 'alexisamore', 'Diamond Foxxx': 'DiamondFoxxx', 'Nikki Benz': 'NikkiBenz', 'Trina Michaels': 'trinamichaels', 'Bree Olson': 'BreeOlson', 'Devon Lee': 'Devonleexxx', 'Alexis': 'Alexis_Texas', 'Dana DeArmond': 'danadearmond', 'Angelina Armani': 'xxxSupermodel', 'jessejanerocks': 'jessejane', 'Lisa Sparxxx': 'Lisa_Sparxxx', 'Raylene': 'RayleneXXX', 'Nicki Hunter': 'NickiHunter', 'derrick pierce': 'dpiercexxx', 'alanaevansxxx': 'alanaevansxxx', 'Sunny Leone': 'SunnyLeone', 'Stormy Daniels': 'StormyDaniels', 'Mary Carey': 'realmarycarey', 'Marie Luv': 'MarieLuv', 'rileysteele': 'rileysteele', 'Jessica Jaymes': 'jessicajaymes1', 'Sophie Dee': 'sophiedee', 'Jenna Jameson': 'jennajameson', 'Kelly Madison': 'Imkellymadison', 'Shyla Stylez': 'ShylaXXX', 'Bobbi Starr': 'Bobbistarr', 'Jenna Haze': 'jenxstudios', 'Catalina Cruz': 'CatalinaCruz', 'Kayden Kross': 'kayden_kross', 'Alexis Ford': 'alexisford', 'Brooke Banner': 'BrookeBannerXXX', 'Delilah Strong': 'delilahstrong', 'Krissy Lynn': 'KrissyLynnxxx', 'Savannah Stern': 'savannahstern', 'Mr. Marcus': 'BeDaddy', 'Puma Swede': 'PumaSwede'}
	twitter3 = {'Alessandra Ambrosio': 'AngelAlessandra', 'Paris Hilton': 'ParisHilton', 'Stacy Keibler': 'StacyKeibler', 'Brande Roderick': 'brandenroderick', 'Kayla Collins': 'kaylacollins', 'Kim Kardashian': 'KimKardashian', 'Ana Beatriz Barros': 'abeatriz', 'ShannonTwins': 'ShannonTwins', 'Kendra Wilkinson': 'KendraWilkinson', 'Nicky Hilton': 'NickyHilton', 'Tyra Banks': 'tyrabanks', 'Bridget Marquardt': 'BunnyBridget', 'Jo Garcia': 'gamernextdoor', 'Cristal Camden': 'cristalcamden', 'Pamela Anderson': 'PamelaDAnderson', 'Miranda Kerr': 'MirandaKerr', 'Laura Croft': 'lauracroft83', 'Elizabeth Hurley': 'ElizabethHurley', 'Shannon Tweed': 'shannonleetweed', 'Sara Jean Underwood': 'SaraUnderwood', 'Crystal Harris': 'CrystalHarris', 'Joanna Krupa': 'joannakrupa', 'Selita Ebanks': 'MsSelitaEbanks', 'Holly Madison': 'hollymadison123', 'Brittany Binger': 'BrittanyBinger', 'Brooke Burke': 'brookeburke', 'Marisa Miller': 'marisamiller', 'Ivanka Trump': 'IvankaTrump', 'Kate Upton': 'KateUpton', 'Christy Turlington': 'CTurlington', 'Kimora Lee Simmons': 'OfficialKimora', 'Shanna Moakler': 'ShannaMoakler', 'Kathy Ireland': 'kathyireland', 'christine teigen': 'chrissyteigen', 'Jenny McCarthy': 'JennyfromMTV', 'Jayde Nicole': 'Jayde_Nicole', 'Brooklyn Decker': 'BrooklynDDecker', 'Brandie Moses': 'BrandieMoses', 'Vida Guerra ': 'Iamvidaguerra', 'Cindy Crawford': 'CindyCrawford', 'Justin Gaston': 'JustinMGaston', 'Leeann Tweeden': 'LeeannTweeden1'}
	twitter4 = {'Nicki Minaj': 'NICKIMINAJ', 'Adam Levine': 'adamlevine', 'Chris Daughtry': 'CHRIS_Daughtry', 'Marshall Mathers': 'Eminem', 'Rihanna': 'rihanna', 'Flo Rida': 'official_flo', 'Bret Michaels': 'bretmichaels', 'Trent Reznor': 'trent_reznor', 'Brandy Norwood': '4everBrandy', 'ICE T': 'FINALLEVEL', 'Billy Corgan': 'Billy', 'QTip': 'QtipTheAbstract', 'Jason Mraz': 'jason_mraz', 'Jesse McCartney': 'JesseMcCartney', 'Kristinia DeBarge': 'Kristinia', 'Reba McEntire': 'reba', 'Samantha Ronson': 'samantharonson', 'Axl Rose': 'axlrose', 'Beyonce Knowles': 'beyonce', 'Beck': 'beck', 'Josh Groban': 'joshgroban', 'Travis Barker': 'travisbarker', 'Nine Inch Nails': 'nineinchnails', 'Nicole Scherzinger': 'NicoleScherzy', 'Darius Rucker': 'dariusrucker', 'Clinton Sparks': 'ClintonSparks', 'Pete Wentz': 'petewentz', 'Chilli': 'officialchilli', 'Perry Farrell': 'perryfarrell', 'Billy Ray Cyrus': 'billyraycyrus', 'Avril Lavigne': 'AvrilLavigne', 'Janet Jackson': 'JanetJackson', 'Wale Folarin ': 'Wale', 'THE GAME': 'thegame', 'Rev Run': 'RevRunWisdom', 'P. Diddy': 'iamdiddy', 'TRINA ': 'TRINArockstarr', 'Lance Bass': 'LanceBass', 'Kelly Clarkson': 'kelly_clarkson', 'Kate Voegele': 'katevoegele', 'Jessica Simpson': 'JessicaSimpson', 'Dave Matthews': 'DaveJMatthews', 'Kenny Chesney': 'kennychesney', 'Jordan Knight': 'jordanknight', 'Kelly Rowland': 'KELLYROWLAND', 'Gene Simmons': 'genesimmons', 'TEFLON DON': 'rickyrozay', 'Tyler Hilton': 'tylerhilton', 'Travie McCoy': 'TravieMcCoy', 'Jimmy Buffett': 'jimmybuffett', 'Jonathan Knight': 'JonathanRKnight', 'Shakira': 'shakira', 'Demetria Lovato': 'ddlovato', 'Melanie Brown': 'OfficialMelB', 'Busta Rhymes': 'BusaBusss', 'Nick Cannon': 'NickCannon', 'JADAKISS': 'Therealkiss', 'Katy Perry': 'katyperry', 'Fabolous': 'myfabolouslife', 'Paula Abdul': 'PaulaAbdul', 'OLIVIA ': '1andonlyOlivia', 'Nick Lachey': 'NickSLachey', 'Adrienne Bailon': 'Adrienne_Bailon', 'Chamillionaire': 'chamillionaire', 'Ryan Adams': 'TheRyanAdams', 'Chris Cornell': 'chriscornell', 'Simple Plan': 'simpleplan', 'Michelle Branch': 'michellebranch', 'Soulja Boy': 'souljaboytellem', 'Aly &amp; AJ Michalk': None, 'David Hasselhoff': 'DavidHasselhoff', 'Shwayze': 'shwayze', 'Neil Diamond': 'NeilDiamond', 'Victoria Beckham': 'victoriabeckham', 'Nick Jonas ': 'nickjonas', 'Dolly Parton': 'Dolly_Parton', 'ASHANTI': 'ashanti', 'COMMON': 'common', 'OneRepublic': 'OneRepublic', 'Robin Thicke': 'robinthicke', 'Hilary Duff': 'HilaryDuff', 'Jared Leto': 'jaredleto', 'Missy Elliott': 'MissyElliott', 'Katharine McPhee ': 'katharinemcphee', 'Faith Hill': 'FaithHill', 'Jewel': 'jeweljk', 'Estelle': 'EstelleDarlings', 'Christina Aguilera': 'TheRealXtina', 'Kelly osbourne': 'MissKellyO', 'Robbie Williams': 'robbiewilliams', 'T.I.': 'Tip', 'Alanis Morissette': 'morissette', 'Weezer': 'Weezer', '50cent': '50cent', 'Lupe Fiasco': 'LupeFiasco', 'Ashley Tisdale': 'ashleytisdale', 'Ne-Yo': 'NeYoCompound', 'Enrique Iglesias': 'enrique305', 'Joel Madden': 'JoelMadden', 'Jennifer Hudson': 'IAMJHUD', 'Sara Evans': 'saraevansmusic', 'Christina Milian': 'CMilianOfficial', 'FAT JOE': 'JOEYCRACKTS', 'Julianne Hough': 'juliannehough', 'Lenny Kravitz': 'LennyKravitz', 'Kellie Pickler': 'kelliepickler', 'Lloyd Banks': 'Lloydbanks', 'Kenny Loggins': 'kennyloggins', 'Toni Braxton': 'tonibraxton', 'Taylor Momsen': 'taylormomsen', 'Martina McBride': 'martinamcbride', 'Brooke Hogan': 'MizzHogan', 'LL Cool J': 'llcoolj', 'Donnie Wahlberg': 'DonnieWahlberg', 'Ricky Martin': 'ricky_martin', 'Warren G': 'regulator', 'MR OMARION ': '1Omarion', 'Lindsay Lohan': 'sevinnyne6126', 'Paulina Rubio': 'paurubio', 'Wyclef Jean': 'wyclef', 'Tori Amos': 'therealtoriamos', 'LIL JON': 'LilJon', 'E-40': 'E40', 'Dawn Richard': 'DawnRichard', ' SWIZZ BEATZ': 'THEREALSWIZZZ', 'Eve': 'TheRealEve', 'AKON': 'Akon', 'Questo of The Roots': 'questlove', 'Moby': 'thelittleidiot', 'MYA ': 'MISSMYA', 'Dierks Bentley': 'DierksBentley', 'The Backstreet Boys': 'backstreetboys', 'RayJ': 'RayJ', 'Snoop Dogg': 'snoopdogg', 'Donny Osmond': 'donnyosmond', 'Mariah Carey': 'MariahCarey', 'Kanye West': 'kanyewest', 'Leighton Meester': 'itsmeleighton', 'Justin Timberlake ': 'jtimberlake', 'will.i.am': 'iamwill', 'Nasir Jones': 'Nas', 'Queen Latifah': 'IAMQUEENLATIFAH', 'Peter Andre': 'MrPeterAndre', 'Usher': 'UsherRaymondIV', 'ke$ha ': 'keshasuxx', 'Mandy Moore': 'TheMandyMoore', 'Ice Cube': 'icecube', 'Tommy Lee': 'MrTommyLand', 'Wes Borland': 'wesborland', 'solange knowles': 'solangeknowles', 'Natasha Bedingfield': 'natashabdnfield', 'Steven Tyler': 'IamStevenT', 'Paris Hilton': 'ParisHilton', 'Vanilla Ice': 'vanillaice', 'Britney Spears': 'britneyspears', 'BIRDMAN': 'BIRDMAN5STAR', 'Fred Durst': 'freddurst', 'Coldplay': 'coldplay', 'Slash': 'Slash', 'Taylor Swift': 'taylorswift13', 'Cee Lo Green': 'CeeLoGreen', 'LeAnn Rimes': 'leannrimes', 'Amy Winehouse': 'amywinehouse', 'Jonas Brothers': 'Jonasbrothers', 'Al Yankovic': 'alyankovic', 'Rob Thomas': 'ThisIsRobThomas', 'Bruno Mars': 'BrunoMars', 'Alicia': 'aliciakeys', 'Keith Urban': 'KeithUrban', 'Miranda Lambert': 'Miranda_Lambert', 'Justin Bieber': 'justinbieber', 'Sean Paul': 'duttypaul', 'Miley Cyrus': 'mileycyrus', 'P!nk': 'Pink', 'John Legend': 'johnlegend', 'DAVID BANNER': 'THEREALBANNER', 'Nikki Sixx': 'NikkiSixx', 'Sean Kingston': 'seankingston', 'Nelly Furtado': 'NellyFurtado', 'Bjork': 'bjork', 'Jennifer Lopez': 'JLo', 'TraceAdkins': 'TraceAdkins', 'Lady Gaga': 'ladygaga', 'Big Boi of OUTKAST': 'BigBoi', 'Mark Hoppus': 'markhoppus', 'BT': 'BT', 'Lil Wayne WEEZY F': 'liltunechi', 'Marie Osmond': 'marieosmond', 'Erykah Badu': 'fatbellybella', 'Joe Jonas': 'joejonas', 'Cher': 'cher', 'Joey McIntyre': 'joeymcintyre', 'Jay-Z': 'Jayz', 'marqueshouston': 'marqueshouston', 'Ozzy Osbourne': 'OfficialOzzy', 'Kevin Jonas': 'kevinjonas', 'Brad Paisley': 'BradPaisley', 'Danny Wood': 'dannywood', 'Kylie Minogue': 'kylieminogue', 'Asher Roth': 'asherroth', 'Jamie Foxx': 'iamjamiefoxx', 'Hammer': 'MCHammer', 'Mary J. Blige': 'maryjblige', 'Adam Lambert': 'adamlambert'}
	people = Person.objects.all()
	for p in people:
		if p.name in twitter:
			p.twitter = twitter[p.name]
			p.save()
		if p.name in twitter2:
			p.tiwtter = twitter2[p.name]
			p.save()
		if p.name in twitter3:
			p.tiwtter = twitter3[p.name]
			p.save()
		if p.name in twitter4:
			p.tiwtter = twitter4[p.name]
			p.save()
		#if p.name == "":
		#	result = freebase.mqlread({"key": [{ "namespace": "/authority/imdb/name", "value": id}], "name": None, "/people/person/place_of_birth": None, "/people/person/nationality": [{}], "/people/person/date_of_birth": None, "/people/person/gender": None, "ns0:key": [{}]})
		#	p.name = result['name']
		#	p.save()
	for key, value in twitter.items():
		try:
			p = Person.objects.get(twitter=value)
		except:
			addByTwitter(value)


def getNationality():
	
	#"/people/person/nationality"
	#"/people/person/place_of_birth"
	#"/people/person/ethnicity"
	nationalities = {}
	people = Person.objects.all()
	
	csvfile = open('/Users/Jason/rankyourfavs/rankfavs/cianat2012.csv', 'rb')
	dialect = csv.Sniffer().sniff(csvfile.read(1024))
	csvfile.seek(0)
	reader= csv.reader(csvfile,dialect)
	convert = {}
	for row in reader:
		r = row
		if len(r)>0:
			t = r[0].strip('\t')
			if 'noun' in t:
				r = r
			elif 'adjective' in t:
				convert[prevcountry] = t.split('adjective: ')[1]
			else:
				prevcountry = t	
	for person in people:
		if person.chickipedia_id != None:
			result = freebase.mqlread({"/people/person/place_of_birth": [{}],"/people/person/ethnicity": [{}],"/people/person/nationality": [{}], "/people/person/profession": [{}], "key": [{ "namespace": "/base/chickipedia/chickipedia_id", "value": person.chickipedia_id}]})
		elif person.imdb_id != None:
			imdb_id = 'nm' + str(person.imdb_id).zfill(7)
			result = freebase.mqlread({"/people/person/place_of_birth": [{}],"/people/person/ethnicity": [{}],"/people/person/nationality": [{}], "/people/person/profession": [{}], "key": [{ "namespace": "/authority/imdb/name", "value": imdb_id}]})
		elif person.sid != None:
			if person.sid.almanac_id != None:
				result = freebase.mqlread({"/people/person/place_of_birth": [{}],"/people/person/ethnicity": [{}],"/people/person/nationality": [{}], "/people/person/profession": [{}],  "key": [{ "namespace": "/source/baseball_almanac/players", "value": person.sid.almanac_id}]})
			elif person.sid.sportsdb_id != None:
				print person.sid.sportsdb_id
			else:
				print "NOTHING"
		else:
			print "NOTHING"
		
		if result != None:
			for i in result['/people/person/nationality']:
				try:
					print convert[i['name']]
					person.tags.add(convert[i['name']])
				except:
					print "Not Present"
				if i['name'] not in nationalities:
					nationalities[i['name']] = 1 
				else:	
					nationalities[i['name']] += 1 
		person.save()
	print nationalities

		
def getTagProfessions():
	d = {"Actor":['Actor','Character actor','Film actress','Voice actor','Theater Actress'],"Adult Actor": ['Pornographic actor'], "Adult Model":['Adult model','Nude Glamour Model','Pin-up girl','Fetish model','Gravure idol','Neo-Burlesque'],"Artist": ['Painter','Artist' ,'Tattoo artist','Makeup Artist','Cartoonist','Sculptor'], "Athlete":['Baseball player','Basketball player','American football player','Golfer','Soccer Player','Tennis player','Alpine Skier','Athlete','Bodybuilder','Figure Skater','Gymnast','Ice skating','Martial artist','Mixed Martial Artist','Professional Boxer','Softball Player','Swimmer','Wrestler','Martial Artist','Ice dancer'],"Baseball Player": ['Baseball player'],"Basketball Player":['Basketball player'],"American Football Player": ['American football player'],"Golfer": ['Golfer'],"Soccer Player":['Soccer Player'],"Tennis Player":['Tennis player'],"Olympian":['Alpine skier','Figure Skater','Gymnast','Ice Skating','Swimmer','Ice Dancer'],"Businessperson":['Businessperson','Entrepreneur','Philanthropist','Spokesman','Chief Executive Officer','Real estate developer'],"Chef":['Chef','Cook','TV chef'],"Coach":['Manager','Coach','Coaching'],"Comedian":['Comedian','Stand-up comedian','Humorist'],"Dancer":['Ballroom Dancer','Choreographer','Dance','Dancer','Exotic dancer','Showgirl','Stripper'],"Director":['Film Director','Music video director','Television Director','Theatre Director'],"Fashion Designer":['Costume Designer','Designer','Fashion Designer'],"Humanitarian":['Activism','Humanitarian','philantropist','Political activist','Social activist'],"Model":['Supermodel','Art Model','Fashion Model','Model','Child model'],"Supermodel":['Supermodel'],"Musician":['Bassist','Composer','Drummer','Fiddler','Guitarist','Keyboard player','Multi-instrumentalist','Musician','Pianist','Playback singer','Rapper','Rapping','Singer-songwriter','Singer','Violinist','Jazz Pianist','Backing vocalist','Film Score Composer','Disc jockey'],"Photographer":['Photographer','Photojournalist'],"Producer":['Producer','Film Producer','Record producer','Television Producer','Hip hop production'],"Racecar Driver":['Racecar driver'],"Royalty":['Duchess','Princess','First Lady'],"TV Personality":['Announcer','Commentator','Host','News Presenter','Newscaster','Presenter','Radio personality','Reporter','Sports commentator','Talk show host','Television Show Host','TV Anchor','TV Journalist','TV Personality','VJ','Broadcaster','Game Show Host'],"Writer":['Author','Blogger','Columnist','Journalist','Novelist','Playwright','Poet','Screenwriter','Writer','Film critic','Lyricist','Songwriter']}
	people = Person.objects.all()
	profs={}
	count = 1
	for person in people:
		count +=1
		print count
		if count>-1:
			if person.chickipedia_id != None:
				result = freebase.mqlread({"/people/person/profession": [{}], "key": [{ "namespace": "/base/chickipedia/chickipedia_id", "value": person.chickipedia_id}]})
			elif person.imdb_id != None:
				imdb_id = 'nm' + str(person.imdb_id).zfill(7)
				result = freebase.mqlread({"/people/person/profession": [{}], "key": [{ "namespace": "/authority/imdb/name", "value": imdb_id}]})
			elif person.sid != None:
				if person.sid.almanac_id != None:
					result = freebase.mqlread({"/people/person/profession": [{}], "key": [{ "namespace": "/source/baseball_almanac/players", "value": person.sid.almanac_id}]})
				elif person.sid.sportsdb_id != None:
					print person.sid.sportsdb_id
				else:
					print "NOTHING"
			else:
				print "NOTHING"
			#result = freebase.mqlread({"name": None, "/people/person/place_of_birth": None, "/people/person/nationality": [{}], "/people/person/date_of_birth": None, "/people/person/profession": [{}], "/people/person/gender": None, "key": [{ "namespace": "/base/chickipedia/chickipedia_id", "value": person.chickipedia_id}], "ns0:key": [{}] })
			#print result
			#print result['/people/person/date_of_birth']
			#print result['/people/person/profession']
			if result != None:
				for i in result['/people/person/profession']:
					#print i['name']
					for entry in d:
						if i['name'] in d[entry]:
							print i['name']
							person.tags.add(entry)
			person.save()
	print profs
	sorted_x = sorted(profs.iteritems(), key=operator.itemgetter(1))
	print sorted_x

		
def getProfessions():
	
	try:
		actor = PersonCategory.objects.get(category="Actor")
	except:
		actor = PersonCategory.objects.create(category="Actor")
	try:
		adultactor = PersonCategory.objects.get(category="Adult Actor")
	except:
		adultactor = PersonCategory.objects.create(category="Adult Actor")
	try:
		adultmodel = PersonCategory.objects.get(category="Adult Model")
	except:
		adultmodel = PersonCategory.objects.create(category="Adult Model")
	try:		
		artist = PersonCategory.objects.get(category="Artist")
	except:
		artist = PersonCategory.objects.create(category="Artist")
	try:	
		athlete = PersonCategory.objects.get(category="Athlete")
	except:
		athlete = PersonCategory.objects.create(category="Athlete")
	try:
		buisnessperson = PersonCategory.objects.get(category="Buisnessperson")
	except:
		buisnessperson = PersonCategory.objects.create(category="Buisnessperson")
	try:
		chef = PersonCategory.objects.get(category="Chef")
	except:
		chef = PersonCategory.objects.create(category="Chef")
	try:
		coach = PersonCategory.objects.get(category="Coach")
	except:
		coach = PersonCategory.objects.create(category="Coach")
	try:
		comedian = PersonCategory.objects.get(category="Comedian")
	except:
		comedian = PersonCategory.objects.create(category="Comedian")
	try:
		dancer = PersonCategory.objects.get(category="Dancer")
	except:
		dancer = PersonCategory.objects.create(category="Dancer")
	try:
		director = PersonCategory.objects.get(category="Director")
	except:
		director = PersonCategory.objects.create(category="Director")
	try:
		fashiondesigner = PersonCategory.objects.get(category="Fashion Designer")
	except:
		fashiondesigner = PersonCategory.objects.create(category="Fashion Designer")
	try:
		humanitarian = PersonCategory.objects.get(category="Humanitarian")
	except:
		humanitarian = PersonCategory.objects.create(category="Humanitarian")
	try:
		model = PersonCategory.objects.get(category="Model")
	except:
		model = PersonCategory.objects.create(category="Model")
	try:
		musician = PersonCategory.objects.get(category="Musician")
	except:
		musician = PersonCategory.objects.create(category="Musician")
	try:
		photographer = PersonCategory.objects.get(category="Photographer")
	except:
		photographer = PersonCategory.objects.create(category="Photographer")
	try:
		producer = PersonCategory.objects.get(category="Producer")
	except:
		producer = PersonCategory.objects.create(category="Producer")
	try:
		racecardriver = PersonCategory.objects.get(category="Racecar Driver")
	except:
		racecardriver = PersonCategory.objects.create(category="Racecar Driver")
	try:
		royalty = PersonCategory.objects.get(category="Royalty")
	except:
		royalty = PersonCategory.objects.create(category="Royalty")
	try:
		tvpersonality = PersonCategory.objects.get(category="TV Personality")
	except:
		tvpersonality = PersonCategory.objects.create(category="TV Personality")
	try:
		writer = PersonCategory.objects.get(category="Writer")
	except:
		writer = PersonCategory.objects.create(category="Writer")
	
	try:
		baseballplayer = PersonCategory.objects.get(category="Baseball Player")	
	except:
		baseballplayer = PersonCategory.objects.create(category="Baseball Player")
	try:
		basketballplayer = PersonCategory.objects.get(category="Basketball Player")	
	except:
		basketballplayer = PersonCategory.objects.create(category="Basketball Player")
	try:
		footballplayer = PersonCategory.objects.get(category="Football Player")	
	except:
		footballplayer = PersonCategory.objects.create(category="Football Player")
	try:
		golfer = PersonCategory.objects.get(category="Golfer")	
	except:
		golfer = PersonCategory.objects.create(category="Golfer")
	try:
		soccerplayer = PersonCategory.objects.get(category="Soccer Player")	
	except:
		soccerplayer = PersonCategory.objects.create(category="Soccer Player")
	try:
		tennisplayer = PersonCategory.objects.get(category="Tennis Player")	
	except:
		tennisplayer = PersonCategory.objects.create(category="Tennis Player")
	
	try:
		olympian = PersonCategory.objects.get(category="Olympian")	
	except:
		olympian = PersonCategory.objects.create(category="Olympian")
	try:
		supermodel = PersonCategory.objects.get(category="Supermodel")	
	except:
		supermodel = PersonCategory.objects.create(category="Supermodel")
	
	
	
	
	
	actor_l = ['Actor','Character actor','Film actress','Voice actor','Theater Actress']
	adultactor_l = ['Pornographic actor']
	adultmodel_l = ['Adult model','Nude Glamour Model','Pin-up girl','Fetish model','Gravure idol','Neo-Burlesque']
	artist_l = ['Painter','Artist' ,'Tattoo artist','Makeup Artist','Cartoonist','Sculptor']
	athlete_l = ['Baseball player','Basketball player','American football player','Golfer','Soccer Player','Tennis player','Alpine Skier','Athlete','Bodybuilder','Figure Skater','Gymnast','Ice skating','Martial artist','Mixed Martial Artist','Professional Boxer','Softball Player','Swimmer','Wrestler','Martial Artist','Ice dancer']	
	baseballplayer_l = ['Baseball player']
	baseketballplayer_l = ['Basketball player']
	footballplayer_l = ['American football player']
	golfer_l = ['Golfer']
	soccerplayer_l = ['Soccer Player']
	tennisplayer_l = ['Tennis player']
	olympian_l = ['Alpine skier','Figure Skater','Gymnast','Ice Skating','Swimmer','Ice Dancer']
	buisnessperson_l = ['Businessperson','Entrepreneur','Philanthropist','Spokesman','Chief Executive Officer','Real estate developer']
	chef_l = ['Chef','Cook','TV chef']
	coach_l = ['Manager','Coach','Coaching']
	comedian_l = ['Comedian','Stand-up comedian','Humorist']
	dancer_l = ['Ballroom Dancer','Choreographer','Dance','Dancer','Exotic dancer','Showgirl','Stripper']
	director_l = ['Film Director','Music video director','Television Director','Theatre Director']
	fashiondesigner_l = ['Costume Designer','Designer','Fashion Designer']
	humanitarian_l = ['Activism','Humanitarian','philantropist','Political activist','Social activist']
	model_l = ['Supermodel','Art Model','Fashion Model','Model','Child model']
	supermodel_l = ['Supermodel']
	musician_l = ['Bassist','Composer','Drummer','Fiddler','Guitarist','Keyboard player','Multi-instrumentalist','Musician','Pianist','Playback singer','Rapper','Rapping','Singer-songwriter','Singer','Violinist','Jazz Pianist','Backing vocalist','Film Score Composer','Disc jockey']
	photographer_l = ['Photographer','Photojournalist']
	producer_l = ['Producer','Film Producer','Record producer','Television Producer','Hip hop production']
	racecardriver_l = ['Racecar driver']
	royalty_l = ['Duchess','Princess','First Lady']
	tvpersonality_l = ['Announcer','Commentator','Host','News Presenter','Newscaster','Presenter','Radio personality','Reporter','Sports commentator','Talk show host','Television Show Host','TV Anchor','TV Journalist','TV Personality','VJ','Broadcaster','Game Show Host']
	writer_l = ['Author','Blogger','Columnist','Journalist','Novelist','Playwright','Poet','Screenwriter','Writer','Film critic','Lyricist','Songwriter']
	
	
	people = Person.objects.all()
	profs={}
	count = 1
	for person in people:
		count +=1
		print count
		if count>3500:
			if person.chickipedia_id != None:
				result = freebase.mqlread({"/people/person/profession": [{}], "key": [{ "namespace": "/base/chickipedia/chickipedia_id", "value": person.chickipedia_id}]})
			elif person.imdb_id != None:
				imdb_id = 'nm' + str(person.imdb_id).zfill(7)
			
				result = freebase.mqlread({"/people/person/profession": [{}], "key": [{ "namespace": "/authority/imdb/name", "value": imdb_id}]})
			elif person.sid != None:
				if person.sid.almanac_id != None:
					result = freebase.mqlread({"/people/person/profession": [{}], "key": [{ "namespace": "/source/baseball_almanac/players", "value": person.sid.almanac_id}]})
				elif person.sid.sportsdb_id != None:
					print person.sid.sportsdb_id
				else:
					print "NOTHING"
			else:
				print "NOTHING"
			#result = freebase.mqlread({"name": None, "/people/person/place_of_birth": None, "/people/person/nationality": [{}], "/people/person/date_of_birth": None, "/people/person/profession": [{}], "/people/person/gender": None, "key": [{ "namespace": "/base/chickipedia/chickipedia_id", "value": person.chickipedia_id}], "ns0:key": [{}] })
			#print result
			#print result['/people/person/date_of_birth']
			#print result['/people/person/profession']
			if result != None:
				for i in result['/people/person/profession']:
					if i['name'] in actor_l:
						actor.members.add(person)
					elif i['name'] in adultactor_l:
						adultactor.members.add(person)
					elif i['name'] in adultmodel_l:
						adultmodel.members.add(person)
					elif i['name'] in artist_l:
						artist.members.add(person)
					elif i['name'] in athlete_l:
						athlete.members.add(person)
						if i['name'] in baseballplayer_l:
							baseballplayer.members.add(person)
						elif i['name'] in baseketballplayer_l:
							basketballplayer.members.add(person)
						elif i['name'] in footballplayer_l:
							footballplayer.members.add(person)
						elif i['name'] in golfer_l:
							golfer.members.add(person)
						elif i['name'] in soccerplayer_l:
							soccerplayer.members.add(person)
						elif i['name'] in tennisplayer_l:
							tennisplayer.members.add(person)
						elif i['name'] in olympian_l:
							olympian.members.add(person)
					elif i['name'] in buisnessperson_l:
						buisnessperson.members.add(person)
					elif i['name'] in chef_l:
						chef.members.add(person)
					elif i['name'] in coach_l:
						coach.members.add(person)
					elif i['name'] in comedian_l:
						comedian.members.add(person)
					elif i['name'] in dancer_l:
						dancer.members.add(person)
					elif i['name'] in director_l:
						director.members.add(person)
					elif i['name'] in fashiondesigner_l:
						fashiondesigner.members.add(person)
					elif i['name'] in humanitarian_l:
						humanitarian.members.add(person)
					elif i['name'] in model_l:
						model.members.add(person)
						if i['name'] in supermodel_l:
							supermodel.members.add(person)
					elif i['name'] in musician_l:
						musician.members.add(person)
					elif i['name'] in photographer_l:
						photographer.members.add(person)
					elif i['name'] in producer_l:
						producer.members.add(person)
					elif i['name'] in racecardriver_l:
						racecardriver.members.add(person)
					elif i['name'] in royalty_l:
						royalty.members.add(person)
					elif i['name'] in tvpersonality_l:
						tvpersonality.members.add(person)
					elif i['name'] in writer_l:
						writer.members.add(person)
					else:
						print i['name']
					if i['name'] in profs:
						profs[i['name']] +=1
					else:
						profs[i['name']] = 1
				if count %100 == 0:
					actor.save()
					adultactor.save()			
					adultmodel.save()
					artist.save()
					athlete.save()
					baseballplayer.save()
					basketballplayer.save()
					footballplayer.save()
					golfer.save()
					soccerplayer.save()
					tennisplayer.save()
					olympian.save()
					buisnessperson.save()
					chef.save()
					coach.save()
					comedian.save()
					dancer.save()
					director.save()
					fashiondesigner.save()
					humanitarian.save()
					model.save()
					supermodel.save()
					musician.save()
					photographer.save()
					producer.save()
					racecardriver.save()
					royalty.save()
					tvpersonality.save()
					writer.save()		
	
	
	actor.save()
	adultactor.save()			
	adultmodel.save()
	artist.save()
	athlete.save()
	baseballplayer.save()
	basketballplayer.save()
	footballplayer.save()
	golfer.save()
	soccerplayer.save()
	tennisplayer.save()
	olympian.save()
	buisnessperson.save()
	chef.save()
	coach.save()
	comedian.save()
	dancer.save()
	director.save()
	fashiondesigner.save()
	humanitarian.save()
	model.save()
	supermodel.save()
	musician.save()
	photographer.save()
	producer.save()
	racecardriver.save()
	royalty.save()
	tvpersonality.save()
	writer.save()
	a = actor.members.all()
	for i in a:
		print i
	print profs
	sorted_x = sorted(profs.iteritems(), key=operator.itemgetter(1))
	print sorted_x


def personInformationGetter(netflix_id,name):
	result = freebase.mqlread({ "id": None, "key": [{ "namespace": "/authority/netflix/role", "value": str(netflix_id) }], "ns0:key": [{}] })
	wikipedia_link = ""
	imdb_id = 0
	tvrage_id = 0
	chickipedia_id = ""
	if result != None:
		for i in result['ns0:key']:
			if i['namespace'] == '/wikipedia/en':
				wikipedia_link = str(i['value'])
				break
		for i in result['ns0:key']:
			if i['namespace'] == '/authority/imdb/name':
				imdb_id = int(i['value'].split('nm')[1])
			if i['namespace'] == '/authority/tvrage/person':
				tvrage_id = int(i['value'])
			if i['namespace'] == '/base/chickipedia/chickipedia_id':
				chickipedia_id = str(i['value'])
	p = Person(netflix_id=netflix_id,name=name,wikipedia_link=wikipedia_link,imdb_id=imdb_id,tvrage_id=tvrage_id,chickipedia_id=chickipedia_id)
	p.save()


def peopleInformationGetter():
	#movs = Movie.objects.all()
	#for m in movs:
	#	for p in m.dictor.all():
	#		c.members.add(p)
	#c.save()
	
	
	
	
	
	people = Person.objects.all()
	
	#for person in people:
	#	result = freebase.mqlread({ "id": None, "key": [{ "namespace": "/authority/netflix/role", "value": str(person.netflix_id) }], "ns0:key": [{}] })
	#	if result != None:
	#		for i in result['ns0:key']:
	#			if i['namespace'] == '/wikipedia/en':
	#				person.wikipedia_link = str(i['value'])
	#				break
	#		for i in result['ns0:key']:
	#			if i['namespace'] == '/authority/imdb/name':
	#				person.imdb_id = int(i['value'].split('nm')[1])
	#			if i['namespace'] == '/authority/tvrage/person':
	#				person.tvrage_id = int(i['value'])
	#			if i['namespace'] == '/base/chickipedia/chickipedia_id':
	#				person.chickipedia_id = str(i['value'])
	#	person.save()
	
	#profs={}
	#for person in people:
	#	result = freebase.mqlread({"name": None, "/people/person/place_of_birth": None, "/people/person/nationality": [{}], "/people/person/date_of_birth": None, "/people/person/profession": [{}], "/people/person/gender": None, "key": [{ "namespace": "/base/chickipedia/chickipedia_id", "value": person.chickipedia_id}], "ns0:key": [{}] })
		#print result
		#print result['/people/person/date_of_birth']
		#if len(result['/people/person/nationality'])>0:
		#	print result['/people/person/nationality'][0]['name']
		#if result['/people/person/gender'] == None:
		#	print "NO GENDER1111111111111111111111111111111111"
		#print result['/people/person/profession']
	#	for i in result['/people/person/profession']:
			#print i['name']
	#		if i['name'] in profs:
	#			profs[i['name']] +=1
	#		else:
	#			profs[i['name']] = 1
	#print profs
	#sorted_x = sorted(profs.iteritems(), key=operator.itemgetter(1))
	#print sorted_x
	
	
	pers = Person.objects.all()
	
	count =1
	pool = ThreadPool(20)	
	for p in pers:
	#		print p.pid
			#pics = Posters.numPics(p.pid)
		if p.images>0:# or p.images ==4:
			True#	print "nothing to see here fella"
		else:
			pool.add_task(Posters.getPersonPictureThread,p.name,p.pid,count)
			count+=1
	pool.wait_completion()
		
	pers = Person.objects.all()
	for p in pers:
		pics = Posters.numPersonPics(p.pid)
		p.images = pics
		p.save()


def getTagTypes():
	d = {"Actor":['Actor','Character actor','Film actress','Voice actor','Theater Actress'],"Adult Actor": ['Pornographic actor'], "Adult Model":['Adult model','Nude Glamour Model','Pin-up girl','Fetish model','Gravure idol','Neo-Burlesque'],"Artist": ['Painter','Artist' ,'Tattoo artist','Makeup Artist','Cartoonist','Sculptor'], "Athlete":['Baseball player','Basketball player','American football player','Golfer','Soccer Player','Tennis player','Alpine Skier','Athlete','Bodybuilder','Figure Skater','Gymnast','Ice skating','Martial artist','Mixed Martial Artist','Professional Boxer','Softball Player','Swimmer','Wrestler','Martial Artist','Ice dancer'],"Baseball Player": ['Baseball player'],"Basketball Player":['Basketball player'],"American Football Player": ['American football player'],"Golfer": ['Golfer'],"Soccer Player":['Soccer Player'],"Tennis Player":['Tennis player'],"Olympian":['Alpine skier','Figure Skater','Gymnast','Ice Skating','Swimmer','Ice Dancer'],"Businessperson":['Businessperson','Entrepreneur','Philanthropist','Spokesman','Chief Executive Officer','Real estate developer'],"Chef":['Chef','Cook','TV chef'],"Coach":['Manager','Coach','Coaching'],"Comedian":['Comedian','Stand-up comedian','Humorist'],"Dancer":['Ballroom Dancer','Choreographer','Dance','Dancer','Exotic dancer','Showgirl','Stripper'],"Director":['Film Director','Music video director','Television Director','Theatre Director'],"Fashion Designer":['Costume Designer','Designer','Fashion Designer'],"Humanitarian":['Activism','Humanitarian','philantropist','Political activist','Social activist'],"Model":['Supermodel','Art Model','Fashion Model','Model','Child model'],"Supermodel":['Supermodel'],"Musician":['Bassist','Composer','Drummer','Fiddler','Guitarist','Keyboard player','Multi-instrumentalist','Musician','Pianist','Playback singer','Rapper','Rapping','Singer-songwriter','Singer','Violinist','Jazz Pianist','Backing vocalist','Film Score Composer','Disc jockey'],"Photographer":['Photographer','Photojournalist'],"Producer":['Producer','Film Producer','Record producer','Television Producer','Hip hop production'],"Racecar Driver":['Racecar driver'],"Royalty":['Duchess','Princess','First Lady'],"TV Personality":['Announcer','Commentator','Host','News Presenter','Newscaster','Presenter','Radio personality','Reporter','Sports commentator','Talk show host','Television Show Host','TV Anchor','TV Journalist','TV Personality','VJ','Broadcaster','Game Show Host'],"Writer":['Author','Blogger','Columnist','Journalist','Novelist','Playwright','Poet','Screenwriter','Writer','Film critic','Lyricist','Songwriter']}
	for i in d:
		print i
		t = PersonTag.objects.get(name=i)
		t.type = "Profession"
		t.save()
	
	
	nationalities = {}
	
	csvfile = open('/Users/Jason/rankyourfavs/rankfavs/cianat2012.csv', 'rb')
	dialect = csv.Sniffer().sniff(csvfile.read(1024))
	csvfile.seek(0)
	reader= csv.reader(csvfile,dialect)
	convert = {}
	
	for row in reader:
		r = row
		if len(r)>0:
			t = r[0].strip('\t')
			if 'noun' in t:
				r = r
			elif 'adjective' in t:
				convert[prevcountry] = t.split('adjective: ')[1]
			else:
				prevcountry = t
	
	for i in convert:
		try:
			t = PersonTag.objects.get(name=convert[i])
			t.type = "Nationality"
			t.save()
		except:
			print "a"	


def getThumbs():
	people = Person.objects.all()
	for person in people:
		Posters.makeThumb(person.pid)


def quotekey(ustr):
    """
    quote a unicode string to turn it into a valid namespace key
    
    """
    valid_always = string.ascii_letters + string.digits
    valid_interior_only = valid_always + '_-'
	
    if isinstance(ustr, str):
        s = unicode(ustr,'utf-8')        
    elif isinstance(ustr, unicode):
        s = ustr
    else:
        raise ValueError, 'quotekey() expects utf-8 string or unicode'
		
    output = []
    if s[0] in valid_always:
        output.append(s[0])
    else:
        output.append('$%04X' % ord(s[0]))
		
    for c in s[1:-1]:
        if c in valid_interior_only:
            output.append(c)
        else:
            output.append('$%04X' % ord(c))
			
    if len(s) > 1:
        if s[-1] in valid_always:
            output.append(s[-1])
        else:
            output.append('$%04X' % ord(s[-1]))
			
    return str(''.join(output))


def fixurl(url):
    # turn string into unicode
    if not isinstance(url,unicode):
        url = url.decode('utf8')
		
    # parse it
    parsed = urlparse.urlsplit(url)
	
    # divide the netloc further
    userpass,at,hostport = parsed.netloc.rpartition('@')
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


def unescape(text):
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text # leave as is
    return re.sub("&#?\w+;", fixup, text)


#@transaction.commit_manually
def freeOnesScraper():
	#url = "http://www.freeones.com/html/a_links/?&profession=t"
	#url = "http://www.freeones.com/html/index_prof.shtml?country=211&profession=m"
	#url = "http://www.freeones.com/html/index_prof.shtml?"
	url = "http://www.freeones.com/html/index_prof.shtml?&country=211"
	#first_letter_base = "/a_links"
	
	#to get paging span class "paging" in div class "contentblockheader"
	
	
	h = httplib2.Http()
	data = ""
	headers = {
		'Accept': 'text/html, */*',
		'Accept-Language': 'en-us,en;q=0.5',
		'Connection':	'Keep-Alive',
	}
	req = urllib2.Request(url, data, headers)
	f = urllib2.urlopen(req)
	htmlSource = f.read()
	f.close()
	#print htmlSource

	root = html.fromstring(htmlSource)
	last_page = 0
	last_page_check = root.cssselect('span.LastPage')
	if len(last_page_check) > 0:
		try:
			last_page = tostring(last_page_check[0]).split("a href=\"?page_w=")[1]
			last_page = int(re.split("[A-Za-z&?\"]",last_page)[0])
		except:
			last_page = 0
	if last_page == 0:
		pages = root.cssselect('span.PageNumber')
	#print test
		for p in pages:
			try:
				page_num = int(p.text)
				if page_num > 0 and page_num > last_page:
					last_page = page_num
			except:
				False
	print "LAST_PAGE = {}".format(last_page)
	for i in range(1,last_page):
		url = "http://www.freeones.com/html/index_prof.shtml?&country=211&page_w=" + str(i)
		
		h = httplib2.Http()
		data = ""
		headers = {
			'Accept': 'text/html, */*',
			'Accept-Language': 'en-us,en;q=0.5',
			'Connection':	'Keep-Alive',
		}
		req = urllib2.Request(url, data, headers)
		f = urllib2.urlopen(req)
		htmlSource = f.read()
		f.close()
		#print htmlSource

		root = html.fromstring(htmlSource)
		
		people = root.cssselect('div.babeInfoBlock_thumb')

		for i in people:
			p = tostring(i)
			try:
				name = p.split("<a class=\"name\" href=\"")[1].split("\"")[0].split("_links/")[1].strip("/")
			except:
				name = None
			#print name
			if name != None:
				first_letter_base = "/a_links"
				url = "http://www.freeones.com/html" + first_letter_base + "/bio_" + name + ".php"
				print url
				try:
					temp = TemporaryPerson.objects.get(freeones_link = url)
				except:
					try:
						req = urllib2.Request(url, data, headers)
						f = urllib2.urlopen(req)
						htmlSource = f.read()
						f.close()
			
						root = html.fromstring(htmlSource)
						table = root.cssselect('table#biographyTable')
						#print table
						entries = table[0].cssselect("tr")
						person = {}
						person['freeones_link'] = url
						for tr in entries:
							tds = tr.cssselect("td")
							fact = re.sub('<[^<]+?>', '', tostring(tds[1])).strip().strip("&#160;")
							facttype = re.sub('<[^<]+?>', '', tostring(tds[0])).strip().strip("&#160;").strip(":")
							if facttype == "Babe Name":
								#print "type: {} fact {}".format(facttype,fact)
								person['name'] = fact
							elif facttype == "Profession":
								#print "type: {} fact {}".format(facttype,fact)
								person['profession'] = fact
							elif facttype == "Ethnicity":
								#print "type: {} fact {}".format(facttype,fact)
								person['ethnicity'] = fact
							elif facttype == "Country of Origin":
								#print "type: {} fact {}".format(facttype,fact)
								person['nationality'] = fact
							elif facttype == "Province / State":
								#print "type: {} fact {}".format(facttype,fact)
								person['state'] = fact
							elif facttype == "Place of Birth":
								#print "type: {} fact {}".format(facttype,fact)
								person['placeofbirth'] = fact
							elif facttype == "Date of Birth":
								#print "type: {} fact {}".format(facttype,fact)
								if fact == "Unknown":
									person['dob'] = None
								else:
									try:
										person['dob'] = datetime.strptime(fact.split(" (")[0], "%B %d, %Y")
									except:
										person['dob'] = None
										print "COULDNT PROCESS: {}".format(fact)
							elif facttype == "Eye Color":
								#print "type: {} fact {}".format(facttype,fact)
								person['eye_color'] = fact
							elif facttype == "Hair Color":
								#print "type: {} fact {}".format(facttype,fact)
								person['hair_color'] = fact
							elif facttype == "Measurements":
								#print "type: {} fact {}".format(facttype,fact)
								person['measurements'] = fact
							elif facttype == "Fake Boobs":
								#print "type: {} fact {}".format(facttype,fact)
								person['implants'] = fact
							elif facttype == "Piercings":
								#print "type: {} fact {}".format(facttype,fact)
								person['piercings'] = fact
							elif facttype == "Tattoos":
								#print "type: {} fact {}".format(facttype,fact)
								person['tattoos'] = fact
							elif facttype == "Social Network Links":
								#print "type: {} fact {}".format(facttype,fact)
								person['sociallinks'] = fact
								lis = tr.cssselect("li")
								for li in lis:
									lnk = tostring(li)
									#print lnk
									if "twitter" in lnk.lower():
										person['twitter'] = lnk.split("twitter.com/")[1].split("\"")[0]
									if "facebook" in lnk.lower():
										person['facebook'] = lnk.split("facebook.com/")[1].split("\"")[0]
							elif facttype == "Babe Rank on Freeones":
								#print "type: {} fact {}".format(facttype,fact)
								person['freeones_rank'] = fact
							elif facttype == "Height":
								try:
									heightcm = int(fact.split("heightcm = \"")[1].split("\"")[0])
									person['height'] = int(round(heightcm * .39370))
								except:
									print "height problem"
							elif facttype == "Weight":
								try:
									weightkg = int(fact.split("weightkg = \"")[1].split("\"")[0])
									person['weight'] = int(round(weightkg / .4545))
								except:
									print "weight problem"
					
							else:
								True
								#print facttype
					except:
						True
					if 'dob' not in person:
						person['dob'] = None
					if 'nationality' not in person:
						person['nationality'] = None
					if 'hair_color' not in person:
						person['hair_color'] = None
					if 'eye_color' not in person:
						person['eye_color'] = None
					if 'measurements' not in person:
						person['measurements'] = None
					if 'tattoos' not in person:
						person['tattoos'] = False
					else:
						person['tattoos'] = True
					if 'implants' not in person or person['implants'] == "No":
						person['implants'] = False
					else:
						person['implants'] = True
					if 'piercings' not in person or person['piercings'] == "None":
						person['piercings'] = False
					else:
						person['piercings'] = True
					if 'twitter' not in person:
						person['twitter'] = None
					if 'facebook' not in person:
						person['facebook'] = None
					if 'freeones_rank' not in person:
						person['freeones_rank'] = 100000
					if person['freeones_rank'] == "" or person['freeones_rank'] == None:
						person['freeones_rank'] = 100000
					try:
						temp_person = TemporaryPerson.objects.get(name=person['name'])
					except:
						temp_person = None
					try:
						real_person = Person.objects.get(name=person['name'])
						print "found {} {} {}".format(person['name'],person['dob'],real_person.dob)
						if datetime.strptime(str(real_person.dob),"%Y-%m-%d") == person['dob']:
							print "WE FOUND A MATCH"
							temp_person = "Don't need"
						else:
							real_person = None
					except:
						real_person = None
						
					if real_person != None:
						real_person.height = person['height']
						real_person.weight = person['weight']
						real_person.hair_color = person['hair_color']
						real_person.eye_color = person['eye_color']
						real_person.measurements = person['measurements']
						real_person.implants = person['implants']
						real_person.piercings = person['piercings']
						real_person.tattoos = person['tattoos']
						if real_person.twitter == None and person['twitter'] != None:
							real_person.twitter = person['twitter']
						if real_person.facebook == None and person['facebook'] != None:
							real_person.facebook = person['facebook']
						try:
							real_person.save()
						except:
							transaction.rollback()
						else:
							transaction.commit()
						print "real person updated"				
					elif temp_person == None and real_person == None:# and int(person['freeones_rank']) < 5000:
						temp_person = TemporaryPerson(	name=person['name'],
														dob=person['dob'],
														height=person['height'],
														weight=person['weight'],
														hair_color = person['hair_color'],
														eye_color = person['eye_color'],
														measurements = person['measurements'],
														implants = person['implants'],
														piercings = person['piercings'],
														tattoos = person['tattoos'],
														nationality = person['nationality'],
														twitter = person['twitter'],
														facebook = person['facebook'],
														freeones_link = person['freeones_link'],
														freeones_rank = person['freeones_rank'])
						
						try:
							temp_person.save()
						except:
							transaction.rollback()
						else:
							transaction.commit()
					
					#print person
		

					
	
	
	

	
	
	

def chickipediaPage():
	count = 0
	url = 'http://www.mademan.com/chickipedia/chicks-by-category/'
	categories = ['tv-actresses/','movie-actresses/','music/','sports/','models/','politics/','buisness/','tv-radio-personality/','porn-stars/','misc/']
	for c in categories:
		curl = url + c
		for i in range(1,100):
			
			data = ""
			h = httplib2.Http()
			cpurl = curl + str(i) + "/"
			headers = {
				'Accept': 'text/html, */*',
				'Accept-Language': 'en-us,en;q=0.5',
				'Connection':	'Keep-Alive',
			}
			req = urllib2.Request(cpurl, data, headers)
			f = urllib2.urlopen(req)
			htmlSource = f.read()
			f.close()
			#print htmlSource
		
			root = html.fromstring(htmlSource)
			data = root.cssselect('div.block-f')
		
			for i in data:
				entry = tostring(i)
				#print entry
				id = entry.split("<a href=\"/chickipedia/")[1].split('/')[0]
				views = entry.split(" Views")[0].split("<div>")[1]
				img = entry.split("<img")[1].split("src=\"")[1].split("_thumb")[0]
				#print views
				if int(views) > 600:
					person = {}
					person['esid'] = unescape(id)
					try:
						p = Person.objects.get(chickipedia_id=person['esid'])
					except:
						#print "chicki {}".format(id)
						#print img
						count +=1
						result = freebase.mqlread({"name": None, "/people/person/place_of_birth": None, "/people/person/nationality": [{}], "/people/person/date_of_birth": None, "/people/person/profession": [{}], "/people/person/gender": None, "key": [{ "namespace": "/base/chickipedia/chickipedia_id", "value": quotekey(id)}], "ns0:key": [{}] })
						real = 0
						if result != None:
							person['wikipedia_link'] = None
							for i in result['ns0:key']:
								if i['namespace'] == '/wikipedia/en':
									person['wikipedia_link'] = str(i['value'])
									real += 1
									break
							for i in result['ns0:key']:
								if i['namespace'] == '/authority/imdb/name':
									person['imdb_id'] = int(i['value'].split('nm')[1])
									real += 1
								if i['namespace'] == '/authority/tvrage/person':
									person['tvrage_id'] = int(i['value'])
									real +=1
								if i['namespace'] == '/authority/netflix/role':
									person['netflix_id'] = int(i['value'])
									real += 1
						print "links {} person is {}".format(real,person)
						if real>1:
							try:
								#,tvrage_id = person['tvrage_id'],netflix_id = person['netflix_id'],imdb_id=person['imdb_id'],wikipedia_link=person['wikipedia_link'],name=result['name']
								p = Person.objects.get(chickipedia_id=person['esid'])
								print "already here"
							except:
								if result['/people/person/date_of_birth'] == None:
									result['/people/person/date_of_birth'] = '1000-1-1'
								elif len(result['/people/person/date_of_birth'])<8:
									if len(result['/people/person/date_of_birth']) <5:
										result['/people/person/date_of_birth'] += "-01-01"
									else:
										result['/people/person/date_of_birth'] += "-01"
								if result['/people/person/gender'] == None:
									result['/people/person/gender'] = "Unknown"
								
								p = None
								p = Person(chickipedia_id=person['esid'],
											gender=result['/people/person/gender'],
											dob=result['/people/person/date_of_birth'],)
								if 'tvrage_id' in person:
									p.tvrage_id = person['tvrage_id']
								if 'netflix_id' in person:
									p.netflix_id = person['netflix_id']
								if 'imdb_id' in person:
									p.imdb_id = person['imdb_id']
								if 'wikipedia_link' in person:
									p.wikipedia_link = person['wikipedia_link']
								p.name = result['name']
								try:
									p.save()
								except:
									connection._rollback()
							
									print "Unexpected error:", sys.exc_info()
									print person
									print len(person)
									print "dup"
						
						
			print count


def baseballAlmanac():
 	url = 'http://www.baseball-almanac.com/players/ballplayer.shtml'
	h = httplib2.Http()
	headers = {
		'Accept': 'text/html, */*',
		'Accept-Language': 'en-us,en;q=0.5',
		'Connection':	'Keep-Alive',
	}
	req = urllib2.Request(url, '', headers)
	f = urllib2.urlopen(req)
	htmlSource = f.read()
	f.close()
	#print htmlSource
		
	root = html.fromstring(htmlSource)
	url = "http://www.baseball-almanac.com/players/player-"
	
	active = False
	veteran = False
	
	count = 0
	data = root.cssselect('td.datacolBoxYellowC')
	data2 = root.cssselect('td.datacolBoxC')
	
	data.extend(data2)
	ids=[]
	for i in data:
		link = tostring(i).split('player-')
		if len(link)>1:
			ids.append(link[1].split('.shtml')[0])
	ids.sort()
	
	for id in ids:	
		
		final = url + id + '.shtml'
		print final
		
		headers = {
			'Accept': 'text/html, */*',
			'Accept-Language': 'en-us,en;q=0.5',
			'Connection':	'Keep-Alive',
		}
		req = urllib2.Request(final, '', headers)
		f = urllib2.urlopen(req)
		htmlSource = f.read()
		f.close()
		
		root = html.fromstring(htmlSource)
		data = root.cssselect('table.boxed')[0].cssselect('tr')
	
		for i in data:
			tr = tostring(i)
			if 'href' in tr:
				if '<b>' in tr:
					active = True
				else:
					active = False
				almanac_id = tr.split('href=\"player.php?p=')[1].split('\" title')[0]
				years = tr.split("class=\"datacolBoxC\">")[1].split("</td>")[0]
				years = years.split(" - ")
				year1 = int(years[0])
				year2 = int(years[1])
				
				if year2-year1>8:
					veteran = True
				else:
					veteran = False
				if veteran or active:
					count +=1
					#print "almanc {} year {} {} CURRENT: {}".format(almanac_id,year1,year2,current)	
					result = freebase.mqlread({"name": None, "/people/person/place_of_birth": None, "/people/person/nationality": [{}], "/people/person/date_of_birth": None, "/people/person/profession": [{}], "/people/person/gender": None, "key": [{ "namespace": "/source/baseball_almanac/players", "value": quotekey(almanac_id)}], "ns0:key": [{}] })
					person = {}
					real=0
					if result != None:
						person['wikipedia_link'] = None
						for i in result['ns0:key']:
							if i['namespace'] == '/wikipedia/en':
								person['wikipedia_link'] = str(i['value'])
								real += 1
								break
						for i in result['ns0:key']:
							if i['namespace'] == '/authority/imdb/name':
								person['imdb_id'] = int(i['value'].split('nm')[1])
								real += 1
							if i['namespace'] == '/authority/tvrage/person':
								person['tvrage_id'] = int(i['value'])
								real +=1
							if i['namespace'] == '/authority/netflix/role':
								person['netflix_id'] = int(i['value'])
								real += 1
					if not 'tvrage_id' in person:
						person['tvrage_id'] = None
					if not 'netflix_id' in person:
						person['netflix_id'] = None
					if not 'imdb_id' in person:
						person['imdb_id'] = None
					if not 'wikipedia_link' in person:
						person['wikipedia_link'] = None
					if real>1:
						try:
							p = Person.objects.get(name=result['name'])
						except:
							try:
								sp = SportsPerson.objects.get(almanac_id=almanac_id)
							except:
								sp = SportsPerson(almanac_id=almanac_id,yearsactive=year2-year1,active=active)
								try:
									sp.save()
								except:
									connection._rollback()
									print "Unexpected error:", sys.exc_info()
							if result['/people/person/gender'] == 'null' or result['/people/person/gender'] == None:
								result['/people/person/gender'] = 'Unknown'
							if len(result['/people/person/date_of_birth'])<8:
								if len(result['/people/person/date_of_birth']) <5:
									result['/people/person/date_of_birth'] += "-01-01"
								else:
									result['/people/person/date_of_birth'] += "-01"
							p = Person(		sid=sp,
											name=result['name'],
											wikipedia_link = person['wikipedia_link'],
											gender=result['/people/person/gender'],
											dob=result['/people/person/date_of_birth'],
											imdb_id = person['imdb_id'],
											tvrage_id = person['tvrage_id'],
											netflix_id = person['netflix_id']
									  ) 
										
							try:
								p.save()
							except:
								connection._rollback()					
								print "Unexpected error:", sys.exc_info()
					else:
						if result!=None:
							True
							#print "name: {} almanac: {} person: {} real: {}".format(result['name'],almanac_id,person,real)
	print count


	
def databaseFootball():
	print "bob"

def moviePosterGetter():
	movs = Movie.objects.all()
	pool = ThreadPool(20)
	count = 1
	for m in movs:
	#		print p.pid
			#pics = Posters.numPics(p.pid)
			if m.images>20:# or p.images ==4:
				True#	print "nothing to see here fella"
			else:
				#if p.Cast.filter(mid=1):
				#print p.Cast.all().count()
				#for i in p.Cast.all():
				#	print i.title
				pool.add_task(Posters.getPosters,m.imdb_id,count)
				count+=1
	pool.wait_completion()

class Worker(Thread):
    """Thread executing tasks from a given tasks queue"""
    def __init__(self, tasks):
        Thread.__init__(self)
        self.tasks = tasks
        self.daemon = True
        self.start()
    
    def run(self):
        while True:
            func, args, kargs = self.tasks.get()
            try: func(*args, **kargs)
            except Exception, e: print e
            self.tasks.task_done()

class ThreadPool:
    """Pool of threads consuming tasks from a queue"""
    def __init__(self, num_threads):
        self.tasks = Queue(num_threads)
        for _ in range(num_threads): Worker(self.tasks)
	
    def add_task(self, func, *args, **kargs):
        """Add a task to the queue"""
        self.tasks.put((func, args, kargs))
	
    def wait_completion(self):
        """Wait for completion of all the tasks in the queue"""
        self.tasks.join()
	

	