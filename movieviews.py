from datetime import datetime, timedelta
from rankyourfavs.rankfavs.models import *
from django.template import Context, loader, RequestContext
from django.shortcuts import render_to_response
import random
import math
import operator
from django.http import HttpResponse
from django.db.models import Q
import simplejson
import httplib2
import cStringIO
import csv
import Filters

def IMDBUserCSVHandler(request):
	lnk = request.POST['imdblink']
	h = httplib2.Http()
	headers, data = h.request(lnk)
	data = cStringIO.StringIO(data)
	
	list = csv.reader(data)
	count = 0
	
	u = request.user.get_profile()
	for i in list:
		if len(i)>1:
			if i[6] == "Feature Film":
				try:
					m = Movie.objects.get(imdb_id = i[1].split('tt')[1])
					print "stored: {} imdb: {}".format(m.title,i[5])
					try:
						mov = UserMovieScore.objects.get(uid = u,mid = m.mid)
						mov.imdb_rating=i[8]
						mov.seen=True
						mov.save()
					except:
						mov = UserMovieScore(uid = u, mid = m.mid, elorating = 1000,seen=True,imdb_rating=i[8],numratings =0,wins=0,losses=0)
						mov.save()
				except:
					print "none {}".format(i[5])
	print count
	data = "poop"
	return HttpResponse(data, mimetype='application/javascript')


def ReverseMovieVoteHandler(request):
	if request.is_ajax():
		if request.method == 'POST':
			message = "This is an XHR POST request"
			
			prevwinner = Movie.objects.get(mid=request.POST['winner'])
			prevloser = Movie.objects.get(mid=request.POST['loser'])
			elo = int(request.POST['elo'])
			
	else:
		if request.method == 'POST':
			prevwinner = Movie.objects.get(mid=request.POST['winner'])
			prevloser = Movie.objects.get(mid=request.POST['loser'])
			elo = int(request.POST['elo'])
	
	u = request.user.get_profile()
	print prevwinner
	print prevloser
	matchup = MovieMatchup.objects.get(winner=prevwinner,loser=prevloser, uid=u)
	
	matchup.winner = prevloser
	matchup.loser = prevwinner
	
	winnersc = UserMovieScore.objects.get(uid = u,mid = prevloser)
	winnersc.elorating = winnersc.elorating + elo
	
	losersc = UserMovieScore.objects.get(uid = u,mid = prevwinner)
	losersc.elorating = losersc.elorating - elo
	
	score = 200
	
	e = score - round(1 / (1 + math.pow(10, ((losersc.elorating - winnersc.elorating) / 400.0))) * score)
	
	matchup.elo = e
	matchup.save()
	
	winnersc.wins = winnersc.wins + 1
	winnersc.losses = winnersc.losses-1
	
	winnersc.elorating = winnersc.elorating + e
	
	losersc.losses = losersc.losses + 1
	losersc.wins = losersc.wins - 1
	
	losersc.elorating = losersc.elorating - e
	
	winnersc.save()
	losersc.save()
	
	data = {'matchupid':int(matchup.matchupid),'winner':{'mid':int(winnersc.mid.mid),'title':winnersc.mid.title},'loser':{'mid':int(losersc.mid.mid),'title':losersc.mid.title},'elo':e}
	
	data = simplejson.dumps(data)
	
	return HttpResponse(data, mimetype='application/javascript')

		
def MovieMatchHandler(request):
	fmovie = {}
	fscore = {}
	context= {}
	if request.is_ajax():
		if request.method == 'GET':
			params = request.GET
			template = "movievotingview.html"
		elif request.method == 'POST':
			params = request.POST
			winner = Movie.objects.get(mid=params['winner'])
			loser = Movie.objects.get(mid=params['loser'])
			if params['year']:
				year = params['year']
			userprofile = request.user.get_profile()
			CalculateRating('movie',winner,loser,userprofile)
			template = "movievotingview.html"
	else:
		params = {}
		template = "indexmovie.html"
	
	results = Filters.setFromParams(request,params,'movie')
	request.session['filtdict'] = results['filtdict']
	request.session['filtvalues'] = results['filtvalues']
	
	results = Filters.getMovieAndScoreFilters(request)
	fmovie = results['fmovie']
	fscore = results['fscore']
	topfmovie = results['topfmovie']
	
	if request.session.get('rematch') == 'Yes':
		rematch = True
		context['rematch'] = "Rematches Allowed"
		request.session['filtdict']['rematch'] = 'Rematches Allowed'
	else:
		rematch = False
		context['rematch'] = "No Rematches"
		if 'rematch' in request.session['filtdict']:
			del request.session['filtdict']['rematch']
	
	print fscore
	print fmovie
	
	if 'gametype' in request.session['filtvalues'] and (request.session['filtvalues']['gametype']=='winner' or request.session['filtvalues']['gametype']=='loser') and request.method == 'POST':
		print "it was a post bitch"
		if request.session['filtvalues']['gametype'] == 'winner':
			movie1 = winner
		elif request.session['filtvalues']['gametype'] == 'loser':
			movie1 = loser
		movie1mat = UserMovieScore.objects.get(uid=request.user.get_profile(),mid= movie1)
		results = getOneMovie(fmovie, fscore, rematch, movie1,request.user.get_profile())
		movie2 = results['Movie']
		movie2mat = results['matchup']

	elif request.session.get('m_lockedin') != None:
		movie1 = request.session['p_lockedin']#Movie.objects.get(mid= request.session['lockedin'])
		try:
			movie1mat = UserMovieScore.objects.get(uid = request.user.get_profile(),mid=movie1)
		except:
			movie1mat = UserMovieScore(uid = request.user.get_profile(), mid=movie1, elorating = 1000,numratings =0,wins=0,losses=0)
			movie1mat.save()
		if close_matchup:
			results = None#getCloseOneMovie(fmovie,fscore,rematch,movie1,movie1mat,request.user.get_profile())
		else:
			results = getOneMovie(fmovie, fscore, rematch, movie1, request.user.get_profile())
		movie2 = results['Movie']
		movie2mat = results['matchup']
	else:
		people = getTwoMovies(fmovie,fscore,rematch,request.user.get_profile())		
		if people == None:
			movie1 = None
			movie2 = None
			movie1mat = None
			movie2mat = None
		else:
			movie1 = people['1']
			movie2 = people['2']
			movie1mat = people['1mat']
			movie2mat = people['2mat']
	if movie1 == None or movie2 == None:
		movie1 = None
		movie2 = None
		movie1mat = None
		movie1mat = None
		#return HttpResponse("NO PEOPLE")
	
	
	top25 = UserMovieScore.objects.filter(uid=request.user.get_profile()).order_by('elorating').reverse()
	if (top25.count()>25):
		top25 = top25[:25]
	
	context['moviebar']= True
	context['movie1'] = movie1
	context['movie1mat'] = movie1mat
	context['movie2'] = movie2
	context['movie2mat'] = movie2mat
	if movie1 != None and movie1.images>0:
		#print movie1.images
		context['movie1ran'] = random.randint(1,movie1.images)
	if movie2 != None and movie2.images>0:
		context['movie2ran'] = random.randint(1,movie2.images)
	context['top20'] =  top25
	
	context['top20'] = top25
	context['filters'] = request.session.get('filtdict')
	
	#return_str = render_block_to_string('subtemplate.html', 'results', context)
	
	message = render_to_response(template, context,context_instance=RequestContext(request))
	return HttpResponse(message)	


def MovieListHandler(request):
	context = {}
	userprof = request.user.get_profile()
	context['movies'] = Movie.objects.all().order_by('title')
	context['umovies'] = UserMovieScore.objects.filter(uid = userprof)
	
	ugames = UserMovieScore.objects.filter(uid = userprof)
	context['umovie'] = {}
	for i in ugames:
		context['umovie'][i.mid.mid] = i.seen
	
	
	template = "movielist.html"
	message = render_to_response(template, context,
		context_instance=RequestContext(request))
	return HttpResponse(message)


def MovieWatchedHandler(request):
	if request.is_ajax():
		if request.method == 'GET':
			params = request.GET
			#print params
		elif request.method == 'POST':
			params = request.POST
			print params
			userprof = request.user.get_profile()
			movie = Movie.objects.get(mid = params['movie'])
			try:
				moviemat = UserMovieScore.objects.get(mid=movie,uid=userprof)
				moviemat.seen = True
				moviemat.save()
			except:
				moviemat = UserMovieScore(uid =userprof, mid = movie, seen = True, elorating = 1000,numratings =0,wins=0,losses=0)
				moviemat.save()
	data = [0]
	return HttpResponse(data, mimetype='application/javascript')


def getRandomImage(images):
	if (images == 0):
		return 0
	else:
		return random.randint(1,images)


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


def MovieHandler(request):
	params= request.GET
	
	if 'id' in params:
		mid = params["id"]
		
	userprofile = request.user.get_profile()
	
	m = Movie.objects.get(mid = mid)
	mm = UserMovieScore.objects.get(mid = mid)
	matchups = MovieMatchup.objects.filter(Q(winner=mid) | Q(loser=mid)).order_by('matchupid')
	
	context = {
			'movie': m,
			'moviemat':mm,
			'matchups':matchups,
	}
	
	message = render_to_response('movie.html',context,context_instance=RequestContext(request))
	return HttpResponse(message)
	


def getOneMovie(fmovie, fscore, movie1,userprof):
	if fscore != {}:
		for i in fmovie:
			index = "mid__" + str(i)
			fscore[index] = fmovie[i]
		randmovies = UserMovieScore.objects.filter(**fscore).order_by('?')
		movie2 = None
		nomovie = True
		for i in range(0,len(randmovies)):
			movie2 = randmovies[i].mid
			movie2mat = randmovies[i]
			if not (MovieMatchup.objects.filter(Q(winner = movie1) | Q(winner = movie2), Q(loser = movie1) | Q(loser = movie2), uid = userprof).exists() 
				or movie1 == movie2):
				nomovie = False
				break
			else:
				nomovie=True
			
	else:	
		randmovies = Movie.objects.filter(**fmovie).order_by('?')
		
		movie2=None
		nomovie = True
		for i in range(0,len(randmovies)):
			movie2 = randmovies[i]
			try:
				movie2mat = UserMovieScore.objects.get(mid=movie2,uid=userprof)
			except:
				movie2mat = UserMovieScore(uid =userprof, mid = movie2, elorating = 1000,numratings =0,wins=0,losses=0)
				movie2mat.save()
			if not (movie2mat.notseen == True
				or MovieMatchup.objects.filter(Q(winner = movie1) | Q(winner = movie2), Q(loser = movie1) | Q(loser = movie2), uid = userprof).exists() 
				or movie1 == movie2):
				nomovie = False
				break
			else:
				nomovie = True
	
	if nomovie == True:
		return None
	
	
	return movie2


def getTwoMovies(fmovie, fscore, rematch, userprof):
	#print fscore
	if fscore != {}:
		for i in fmovie:
			index = "mid__" + str(i)
			fscore[index] = fmovie[i]
		randmovies = UserMovieScore.objects.filter(**fscore).order_by('?')
		movie1=None
		movie2=None
		nomovie=True
		for i in range(0,len(randmovies)-1):
			movie1 = randmovies[i].mid
			movie2 = randmovies[len(randmovies)-1-i].mid
			movie1mat = randmovies[i]
			movie2mat = randmovies[len(randmovies)-1-i]
			if not (MovieMatchup.objects.filter(Q(winner = movie1) | Q(winner = movie2), Q(loser = movie1) | Q(loser = movie2), uid = userprof).exists() 
				#or MovieMatchup.objects.filter(winner = movie1, loser = movie2).exists() 
				#or MovieMatchup.objects.filter(winner = movie2, loser = movie1).exists()
				or movie1 == movie2):
				nomovie = False
				movies = {}
				movies['1'] = movie1
				movies['1mat'] = movie1mat
				movies['2'] = movie2
				movies['2mat'] = movie2mat
				return movies
			else:
				nomovie=True
			
	else:	
		randmovies = Movie.objects.filter(**fmovie).order_by('?')
		
		#print randtvshows
		movie1=None
		movie2=None
		nomovie = True
		for i in range(0,len(randmovies)-1):
			movie1 = randmovies[i]
			
			havntused1 = False
			lookatsecond=True
			
			try:
				movie1mat = UserMovieScore.objects.get(mid=movie1,uid=userprof)
				if movie1mat.seen == False:
					lookatsecond = False
			except:
				havntused1 = True
			#Dont continue only if first was marked not watched
			if lookatsecond:
				for j in range(0,len(randmovies)-1):
					if i!=j:
						movie2 = randmovies[j]
						havntused2 = False
						lookpastsecond = True
						try:
							movie2mat = UserMovieScore.objects.get(mid=movie2,uid=userprof)
							if movie2mat.seen == False:
								lookpastsecond = False
						except:
							havntused2 = True
						#Dont continue only if first was marked not watched	
						if lookpastsecond:
							#Create if not there for both 1 and 2
							if havntused1:
								movie1mat = UserMovieScore(uid =userprof, mid = movie1, elorating = 1000,numratings =0,wins=0,losses=0,seen=True)
								print "made from 1 {}".format(movie1.title)
								movie1mat.save()
							if havntused2:
								movie2mat = UserMovieScore(uid =userprof, mid = movie2, elorating = 1000,numratings =0,wins=0,losses=0,seen=True)
								movie2mat.save()
								print "made from 2 {}".format(movie2.title)
							
							#taking out the checking for watched as already accomplished before....leaving as comment just in case
								#not (tvshow1mat.watched == False
								#	or tvshow2mat.watched == False
								#	or TVShowMatchup.objects.filter(Q(winner = tvshow1) | Q(winner = tvshow2), Q(loser = tvshow1) | Q(loser = tvshow2), uid = userprof).exists()):
								
							if not (MovieMatchup.objects.filter(Q(winner = movie1) | Q(winner = movie2), Q(loser = movie1) | Q(loser = movie2), uid = userprof).exists()):
								movies = {}
								movies['1'] = movie1
								movies['1mat'] = movie1mat
								movies['2'] = movie2
								movies['2mat'] = movie2mat
								return movies
							else:
								#As didnt use the objects delete to not create unecessary data
									##Possibly move movie1mat deletion outside the loop????????????
								if movie1mat.numratings == 0 and movie1mat.seen == True:
									movie1mat.delete()
								if movie2mat.numratings == 0 and movie2mat.seen == True:
									movie2mat.delete()
								nomovie = True
						else:
							nomovie = True
	if nomovie == True:
		return None
	
	movies = {}
	movies['1'] = None
	movies['1mat'] = None
	movies['2'] = None
	movies['2mat'] = None
	return movies




