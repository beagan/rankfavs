from datetime import datetime, timedelta
from rankyourfavs.rankfavs.models import *
from django.template import Context, loader, RequestContext
from django.shortcuts import render_to_response
import random
import math
import operator
import time
from django.http import HttpResponse
from django.db.models import Q
from django.shortcuts import redirect
import Posters

from Calculate import calculateRating

def TVShowHandler(request, tid):
	params= request.GET
	
	if 'tid' in params:
		tid = int(params["tid"])
	else:
		tid = tid
	userprofile = request.user.get_profile()
	try:
		t = TVshow.objects.get(tid = tid)
	except:
		t = None
	try:
		tt = UserTVShowScore.objects.get(tid = tid,uid=userprofile)
	except:
		tt= None
	matchups = TVShowMatchup.objects.filter(Q(winner=tid,uid=userprofile) | Q(loser=tid,uid=userprofile)).order_by('matchupid')
	#print t.images
	context = {
			'tvshow': t,
			'tvshowscore':tt,
			'matchups':matchups,
			'range':range(1,t.images+1)
	}
	#print context
	message = render_to_response('tvshow.html',context,context_instance=RequestContext(request))
	return HttpResponse(message)


	
def TVShowMatchHandler(request):
	year = ""
	context = {}
	ftvshow = {}
	fscore = {}
	#if fscore == {}:
	#	fscore['uid'] = request.user.get_profile()
	#	fscore['neveruse'] = False
	prevvote = False
	userprofile = request.user.get_profile()
	if request.is_ajax():
		if request.method == 'GET':
			params = request.GET
			template = 'tvvotingview.html'
			print params
		elif request.method == 'POST':
			params = request.POST
			winner = TVshow.objects.get(tid=params['winner'])
			loser = TVshow.objects.get(tid=params['loser'])
			prevvote = True
			
			ranks = CalculateRating('tvshow',winner,loser,userprofile)
			template = 'tvvotingview.html'
	else:
		#TEMPORARY CHANGED FROM {}
		params = request.GET
		template = "indextvshow.html"
	
	if 'notwatched' in params:
		notwatched = params['notwatched']
		setNotWatched(notwatched,userprofile)
		print "set not watched"
	if 'clearfilters' in params:
		request.session['gametype'] = None
		request.session['list'] = None
		request.session['lockedin'] = None
		request.session['rematch'] = None
		request.session['filtdict'] = {}
	
	if 'remove' in params:
		del request.session['filtdict'][params['remove']]
		request.session[params['remove']] = None	
	
	
	
	#If there is no filter dictionary in the session need to create one to store future filters
	if 	'filtdict' not in request.session:#['filtdict'] == None:
		request.session['filtdict'] = {}
	
	
	
	#Checking to see if we are setting the gametype
	#If there is a gametype set in filter dictionary for the view
		#########NEED TO CHANGE IN HTML
	if 'gametype' in params:
		request.session['gametype'] = params['gametype']
		if request.session.get('gametype') ==  'winner':
			request.session['filtdict']['gametype'] = 'Winner Stays'
		elif request.session.get('gametype') ==  'loser':
			request.session['filtdict']['gametype'] = 'Loser Stays'
		else:
			request.session['filtdict']['gametype'] = 'Matchup Type'
		
	
	
	cat=None	
	
	
	if 'watched' in params:
		request.session['watched'] = params['watched']
		if params['watched'] == "True":
			request.session['filtdict']['watched'] = "Only Watched"
	
	#if only doing watched set in fscore to True
		#otherwise it is fine to leave it out as that will encompass true and false which is only other choice
	if request.session.get('watched') != None:
		if request.session.get('watched') == 'True':
			fscore['watched'] = True
	
	#########Currently dont have categories in tvshows
	#if 'cat' in params:
	#	request.session['cat'] = params['cat']
	#if request.session.get('cat') == "All Categories":
	#	context['cat'] = "All Categories"
	#elif request.session.get('cat') != None:
		#context['cat'] = PersonCategory.objects.get(gid=request.session.get('cat')).category
		#cat = PersonCategory.objects.get(gid=request.session.get('cat'))
		#print cat.category
	#	ftvshow['cats__category']=cat.category
		
	if 'list' in params:
		request.session['list'] = params['list']
	if request.session.get('list') == 'top25':
		request.session['filtdict']['list'] = "Your Top 25"
		topftvshow={}
		for i in ftvshow:
			index = "tid__" + str(i)
			topftvshow[index] = ftvshow[i]
		elo = UserTVShowScore.objects.filter(uid=request.user.get_profile()).filter(**topftvshow).order_by('elorating').reverse()[25].elorating
		print elo
		fscore['elorating__gte'] = elo
	elif request.session.get('list') == 'top250':
		request.session['filtdict']['list'] = "Your Top 250"
		topftvshow={}
		for i in ftvshow:
			index = "tid__" + str(i)
			topftvshow[index] = ftvshow[i]
		elo = UserTVShowScore.objects.filter(uid=request.user.get_profile()).filter(**topftvshow).order_by('elorating').reverse()[250].elorating
		
		fscore['elorating__gte'] = elo
	elif request.session.get('list') == 'undefeated':
		request.session['filtdict']['list'] = "Your Undefeated"
		fscore['losses__lte'] = 0
	elif request.session.get('list') == 'newbie':
		request.session['filtdict']['list'] = "Your Unranked"
		fscore['numratings__lte'] = 3		
	elif request.session.get('list') != 'None':
		#request.session['filtdict']['list'] = "WHAT LIST YOU GOT"
		print request.session.get('list')
		#ftvshow['plist__list'] = request.session.get('list')
	else:
		True
	
	print "ftvshow {}".format(ftvshow)
	print "fscore {}".format(fscore)
	
	
	f = {'uid':request.user.get_profile()}
	#fscore = {}
	
	print ftvshow
	print fscore
	#ftvshow = {}
	
	
	#Check if only need one show cause of previous match being set as winner or loser stays
	if (request.session.get('gametype')=='winner' or request.session.get('gametype')=='loser') and request.method == 'POST':
		if request.session['gametype'] == 'winner':
			tvshow1 = winner
		elif request.session['gametype'] == 'loser':
			tvshow1 = loser
		tvshow1mat = UserTVShowScore.objects.get(uid=request.user.get_profile(),tid = tvshow1)
		
		tvshow2 = getOneTVshow(ftvshow, fscore, tvshow1,request.user.get_profile())
		if tvshow2 == None:
			return HttpResponse("No People")
		else:
			tvshow2mat = UserTVShowScore.objects.get(uid=request.user.get_profile(),tid = tvshow2)
	#Check to see if coming from setting a show to not watched and only need one show to complement other that was said do to be watched
	elif 'notwatched' in params and 'othertvshow' in params:
		tvshow1 = TVshow.objects.get(tid=params['othertvshow'])
		tvshow1mat = UserTVShowScore.objects.get(uid=request.user.get_profile(),tid = tvshow1)
		
		tvshow2 = getOneTVshow(ftvshow, fscore, tvshow1,request.user.get_profile())
		if tvshow2 == None:
			return HttpResponse("No People")
		else:
			tvshow2mat = UserTVShowScore.objects.get(uid=request.user.get_profile(),tid = tvshow2)
	else:
		tvshows = getTwoTVshows(ftvshow,fscore,request.user.get_profile())	
		print "tried gettwo"
		print tvshows	
		if tvshows == None:
			tvshow1 = None
			tvshow2 = None
			tvshow1mat = None
			tvshow2mat = None
		else:
			tvshow1 = tvshows['1']
			tvshow2 = tvshows['2']
			tvshow1mat = tvshows['1mat']
			tvshow2mat = tvshows['2mat']
		
	topftvshow={}
	for i in ftvshow:
		index = "tid__" + str(i)
		topftvshow[index] = ftvshow[i]
	top25 = UserTVShowScore.objects.filter(uid=request.user.get_profile()).filter(**topftvshow).order_by('elorating').reverse()
	
	if (top25.count()>25):
		top25 = top25[:25]
	
	if prevvote:
		context['ranks'] = ranks
	
	
	#t1 = time.time()
	#count = 0
	
	#for i in range(1,1000):
	#	testtvshows = getTwoTVshows(ftvshow,fscore,request.user.get_profile())
	#	count += testtvshows['count']
	#t2 = time.time()
	
	#print "1000 2 tv shows was {} count was {}".format(t2-t1,count)
	
	context['filters'] = request.session.get('filtdict')
	print context
	context['tvshow1'] = tvshow1
	context['tvshow1mat'] = tvshow1mat
	context['tvshow2'] = tvshow2
	context['tvshow2mat'] = tvshow2mat
	#context['categories'] = PersonCategory.objects.all()
	#context['lists'] = PersonList.objects.all()
	context['tvshowbar'] = True
	if tvshow1 != None and tvshow1.images>0:
		context['tvshow1ran'] = random.randint(1,tvshow1.images)
	if tvshow2 != None and tvshow2.images>0:
		context['tvshow2ran'] = random.randint(1,tvshow2.images)
	context['top20'] =  top25
	
	
	message = render_to_response(template, context,
		context_instance=RequestContext(request))
	return HttpResponse(message)



def TVShowListHandler(request):
	
	if request.is_ajax():
		if request.method == 'GET':
			params = request.GET
			template = 'tvshowlistpage.html'
		elif request.method == 'POST':
			params = request.POST
			template = 'tvshowlistpage.html'
	else:
		params = request.GET
		if 'page' in params:
			page = int(params['page'])
		else:
			page = 1
		template = "tvshowlist.html"
	
	
	
	
	context = {}
	userprof = request.user.get_profile()
	start = page * 25
	end = page * 25 + 25
	context['tvshows'] = TVshow.objects.all().order_by('title')[start:end]
	#context['utvshows'] = UserTVShowScore.objects.filter(uid = userprof)
	
	
	##CHange to only look up the ones that it needs with a try statement, see if its faster, probably will be for a much larger dataset
	utv = UserTVShowScore.objects.filter(uid = userprof)
	context['tvshow'] = {}
	for i in utv:
		context['tvshow'][i.tid.tid] = i.watched
	
	lastpage = 1000
	if page < lastpage:
		context['nextpage'] = page + 1
	if page > 1:
		context['prevpage'] = page -1
	
	#template = "tvshowlist.html"
	message = render_to_response(template, context,
		context_instance=RequestContext(request))
	return HttpResponse(message)


def TVShowWatchedHandler(request):
	
	if request.is_ajax():
		if request.method == 'GET':
			params = request.GET
			#print params
			
			######POSSIBLY SIMPLIFY TO ONE
			if 'reverse' in params:
				notwatched = True
			else:
				notwatched = False
			userprof = request.user.get_profile()
			tvshow = TVshow.objects.get(tid = params['tvshow'])
			print "notwatched {}".format(notwatched)
			try:
				tvshowmat = UserTVShowScore.objects.get(tid=tvshow,uid=userprof)
				if notwatched:
					tvshowmat.watched = False
				else:	
					tvshowmat.watched = True
				tvshowmat.save()
			except:
				if notwatched:
					tvshowmat = UserTVShowScore(uid =userprof, tid = tvshow, watched = True, elorating = 1000,numratings =0,wins=0,losses=0)
				else:
					tvshowmat = UserTVShowScore(uid =userprof, tid = tvshow, watched = False, elorating = 1000,numratings =0,wins=0,losses=0)
				tvshowmat.save()
			print "REDIRECT"			
			url = '/tvshows'
			return redirect(url)	
			
		elif request.method == 'POST':
			params = request.POST
			print params
			if 'reverse' in params:
				notwatched = True
			else:
				notwatched = False
			userprof = request.user.get_profile()
			tvshow = TVshow.objects.get(tid = params['tvshow'])
			try:
				tvshowmat = UserTVShowScore.objects.get(tid=tvshow,uid=userprof)
				if notwatched:
					tvshowmat.watched = False
				else:	
					tvshowmat.watched = True
				tvshowmat.save()
			except:
				if notwatched:
					tvshowmat = UserTVShowScore(uid =userprof, tid = tvshow, watched = True, elorating = 1000,numratings =0,wins=0,losses=0)
				else:
					tvshowmat = UserTVShowScore(uid =userprof, tid = tvshow, watched = False, elorating = 1000,numratings =0,wins=0,losses=0)
				tvshowmat.save()
			data = [0]
			return HttpResponse(data, mimetype='application/javascript')
	else:
		if request.method == 'GET':
			params = request.GET
			#print params
			
			######POSSIBLY SIMPLIFY TO ONE
			if 'reverse' in params:
				notwatched = True
			else:
				notwatched = False
			userprof = request.user.get_profile()
			tvshow = TVshow.objects.get(tid = params['tvshow'])
			print "notwatched {}".format(notwatched)
			try:
				tvshowmat = UserTVShowScore.objects.get(tid=tvshow,uid=userprof)
				if notwatched:
					tvshowmat.watched = False
				else:	
					tvshowmat.watched = True
				tvshowmat.save()
			except:
				if notwatched:
					tvshowmat = UserTVShowScore(uid =userprof, tid = tvshow, watched = True, elorating = 1000,numratings =0,wins=0,losses=0)
				else:
					tvshowmat = UserTVShowScore(uid =userprof, tid = tvshow, watched = False, elorating = 1000,numratings =0,wins=0,losses=0)
				tvshowmat.save()
	data = TVShowMatchHandler(request)
	
	return data	


def setNotWatched(notwatched_id,userprofile):
	try:
		tvshowmat = UserTVShowScore.objects.get(tid=notwatched_id,uid=userprofile)
		tvshowmat.watched = False
		tvshowmat.save()
	except:
		tvshowmat = UserTVShowScore(uid =userprofile, tid = tvshow, watched = False, elorating = 1000,numratings =0,wins=0,losses=0)
		tvshowmat.save()

def getTwoTVshows(ftvshow, fscore, userprof):
	print "ftvshow {} fscore {}".format(ftvshow,fscore)
	if fscore != {}:
		fscore['uid'] = userprof
		for i in ftvshow:
			index = "tid__" + str(i)
			fscore[index] = ftvshow[i]
		print "fscore IN LOOP {}".format(fscore)
		randtvshows = UserTVShowScore.objects.filter(**fscore).order_by('?')
		tvshow1=None
		tvshow2=None
		notvshow=True
		print len(randtvshows)
		for i in range(0,len(randtvshows)-1):
			for j in range(0,len(randtvshows)-1):
#				print "i {} len i {}".format(i,len(randtvshows)-1-i)
				if i!=j:
					tvshow1 = randtvshows[i].tid
					tvshow2 = randtvshows[j].tid
					tvshow1mat = randtvshows[i]
					tvshow2mat = randtvshows[j]
					if not (TVShowMatchup.objects.filter(Q(winner = tvshow1) | Q(winner = tvshow2), 
														 Q(loser = tvshow1) | Q(loser = tvshow2), 
														 uid = userprof).exists()):
						tvshows = {}
						tvshows['1'] = tvshow1
						tvshows['1mat'] = tvshow1mat
						tvshows['2'] = tvshow2
						tvshows['2mat'] = tvshow2mat
						return tvshows
					else:
						notvshow=True
			
	else:
		randtvshows = TVshow.objects.filter(**ftvshow).order_by('?')
		#print randtvshows
		tvshow1=None
		tvshow2=None
		notvshow = True
		
		##TEMPORARY
		count = 0
		
		for i in range(0,len(randtvshows)-1):
			count += 1
			
			tvshow1 = randtvshows[i]
			
			havntused1 = False
			lookatsecond=True
			
			try:
				tvshow1mat = UserTVShowScore.objects.get(tid=tvshow1,uid=userprof)
				if tvshow1mat.watched == False:
					lookatsecond = False
			except:
				havntused1 = True
			#Dont continue only if first was marked not watched
			if lookatsecond:
				for j in range(0,len(randtvshows)-1):
					if i!=j:
						tvshow2 = randtvshows[j]
						havntused2 = False
						lookpastsecond = True
						try:
							tvshow2mat = UserTVShowScore.objects.get(tid=tvshow2,uid=userprof)
							if tvshow2mat.watched == False:
								lookpastsecond = False
						except:
							havntused2 = True
						#Dont continue only if first was marked not watched	
						if lookpastsecond:
							#Create if not there for both 1 and 2
							if havntused1:
								tvshow1mat = UserTVShowScore(uid =userprof, tid = tvshow1, elorating = 1000,numratings =0,wins=0,losses=0,watched=True)
								print "made from 1 {}".format(tvshow1.title)
								tvshow1mat.save()
							if havntused2:
								tvshow2mat = UserTVShowScore(uid =userprof, tid = tvshow2, elorating = 1000,numratings =0,wins=0,losses=0,watched=True)
								tvshow2mat.save()
								print "made from 2 {}".format(tvshow2.title)
							
							#taking out the checking for watched as already accomplished before....leaving as comment just in case
								#not (tvshow1mat.watched == False
								#	or tvshow2mat.watched == False
								#	or TVShowMatchup.objects.filter(Q(winner = tvshow1) | Q(winner = tvshow2), Q(loser = tvshow1) | Q(loser = tvshow2), uid = userprof).exists()):
								
							if not (TVShowMatchup.objects.filter(Q(winner = tvshow1) | Q(winner = tvshow2), Q(loser = tvshow1) | Q(loser = tvshow2), uid = userprof).exists()):
								tvshows = {}
								tvshows['1'] = tvshow1
								tvshows['1mat'] = tvshow1mat
								tvshows['2'] = tvshow2
								tvshows['2mat'] = tvshow2mat
								#TEMPORARY
								tvshows['count'] = count
								
								return tvshows
							else:
								#As didnt use the objects delete to not create unecessary data
								if tvshow1mat.numratings == 0:
									tvshow1mat.delete()
								if tvshow2mat.numratings == 0:
									tvshow2mat.delete()
								notvshow = True
						else:
							notvshow = True
	
	if notvshow == True:
		print "tvshow 1 {} tvshow2 {} returned none".format(tvshow1,tvshow2)
		return None
	
	tvshows = {}
	tvshows['1'] = tvshow1
	tvshows['1mat'] = tvshow1mat
	tvshows['2'] = tvshow2
	tvshows['2mat'] = tvshow2mat
	
	#TEMPORARY
	tvshows['count'] = count
	return tvshows

###TO DO FILTER ON FSCORE

def getOneTVshow(ftvshow, fscore, tvshow1,userprof):
	if fscore != {}:
		fscore['uid'] = userprof
		print "fscore in tvone {}".format(fscore)
		for i in ftvshow:
			index = "tid__" + str(i)
			fscore[index] = ftvshow[i]
		randtvshows = UserTVShowScore.objects.filter(**fscore).order_by('?')
		tvshow2 = None
		notvshow = True
		for i in range(0,len(randtvshows)):
			tvshow2 = randtvshows[i].tid
			tvshow2mat = randtvshows[i]
			print "2mat watched {} {}".format(tvshow2mat.watched,tvshow2.title)
			if not (TVShowMatchup.objects.filter(Q(winner = tvshow1) | Q(winner = tvshow2), Q(loser = tvshow1) | Q(loser = tvshow2), uid = userprof).exists() 
				or tvshow1 == tvshow2):
				notvshow = False
				break
			else:
				notvshow=True
			
	else:	
		randtvshows = TVshow.objects.filter(**ftvshow).order_by('?')
		
		tvshow2=None
		notvshow = True
		for i in range(0,len(randtvshows)):
			tvshow2 = randtvshows[i]
			try:
				tvshow2mat = UserTVShowScore.objects.get(tid=tvshow2,uid=userprof)
			except:
				tvshow2mat = UserTVShowScore(uid =userprof, tid = tvshow2, elorating = 1000,numratings =0,wins=0,losses=0,watched=True)
				tvshow2mat.save()
			if not (tvshow2mat.watched == False
				or TVShowMatchup.objects.filter(Q(winner = tvshow1) | Q(winner = tvshow2), Q(loser = tvshow1) | Q(loser = tvshow2), uid = userprof).exists() 
				or tvshow1 == tvshow2):
				notvshow = False
				break
			else:
				tvshow2mat.delete()
				notvshow = True
	
	if notvshow == True:
		return None
	
	return tvshow2	


def CalculateRating(type,winner,loser,u):
	if type == "tvshow":
			try:
				winnersc = UserTVShowScore.objects.get(uid = u,tid = winner)
			except:
				winnersc = UserTVShowScore(uid = u, tid = winner, elorating = 1000,numratings =0,wins=0,losses=0)
				winnersc.save()
			try:
				losersc = UserTVShowScore.objects.get(uid = u,tid = loser)
			except:
				losersc = UserTVShowScore(uid =u, tid = loser, elorating = 1000,numratings =0,wins=0,losses=0)
				losersc.save()
			fwinner = {}
			floser = {}
			fwinner['elorating__gte'] = winnersc.elorating
			floser['elorating__gte'] = losersc.elorating
			oldwinnerrank = winnersc.rank
			oldloserrank = losersc.rank
			
			matchup = TVShowMatchup.objects.filter((Q(winner=winner) & Q(loser=loser)) | (Q(loser=winner) & Q(winner=loser)),uid = u)
			if not (matchup.exists()):
				
				score = 200
				
				e = score - round(1 / (1 + math.pow(10, ((losersc.elorating - winnersc.elorating) / 400.0))) * score)
				winnersc.numratings = winnersc.numratings + 1
				
				winnersc.wins = winnersc.wins + 1
				
				winnersc.elorating = winnersc.elorating + e
				
				losersc.numratings = losersc.numratings + 1
				losersc.losses = losersc.losses + 1
				
				losersc.elorating = losersc.elorating - e
				
				matchup = TVShowMatchup(winner = winner, loser = loser, uid = u, elo = e)
				
				matchup.save()
				#print winnersc.elorating
				#print losersc.elorating
			else:
				#print matchup[0]
				m = matchup[0]
				#print m.winner
				#print m.loser
				print m.elo
				
			#		print "same"
				winnersc.elorating = winnersc.elorating-m.elo
				losersc.elorating = losersc.elorating+m.elo
				score = 200
				
				e = score - round(1 / (1 + math.pow(10, ((losersc.elorating - winnersc.elorating) / 400.0))) * score)
				
				print "old {} new {}".format(m.elo,e)
				
				winnersc.elorating = winnersc.elorating + e
				losersc.elorating = losersc.elorating - e
				m.delete()
				matchup = TVShowMatchup(winner = winner, loser = loser, uid = u, elo = e)
				matchup.save()
				#else:
				#	print "diff"
					
			fwinner['elorating__gt'] = winnersc.elorating
			floser['elorating__gt'] = losersc.elorating
			
			newwinnerrank = UserTVShowScore.objects.filter(**fwinner).count()+1
			newloserrank = UserTVShowScore.objects.filter(**floser).count()+1
			
			winnersc.rank = newwinnerrank
			losersc.rank = newloserrank
			
			winnersc.save()
			losersc.save()
			
			ranks = {}
			ranks['oldwinner'] = oldwinnerrank
			ranks['newwinner'] = newwinnerrank
			ranks['winnerchange'] = oldwinnerrank-newwinnerrank 
			ranks['oldloser'] = oldloserrank
			ranks['newloser'] = newloserrank
			ranks['loserchange'] = oldloserrank - newloserrank
			return ranks

