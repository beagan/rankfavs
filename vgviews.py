from datetime import datetime, timedelta
from rankyourfavs.rankfavs.models import *
from django.template import Context, loader, RequestContext
from django.shortcuts import render_to_response
import random
import math
import operator
from django.http import HttpResponse
from django.db.models import Q
from django.shortcuts import redirect
import Posters

def VideoGameHandler(request):
	params= request.GET
	
	if 'vid' in params:
		vid = params["vid"]
		
	userprofile = request.user.get_profile()
	
	v = VideoGame.objects.get(vid = vid)
	
	try:
		vv = UserVideoGameScore.objects.get(vid = vid)
	except:
		vv = None
	matchups = VideoGameMatchup.objects.filter(Q(winner=vid) | Q(loser=vid)).order_by('matchupid')
	
	context = {
			'videogame': v,
			'videogamemat':vv,
			'matchups':matchups,
	}
	
	message = render_to_response('videogame.html',context,context_instance=RequestContext(request))
	return HttpResponse(message)
	
def VideoGameMatchHandler(request):
	
	#vg = VideoGame.objects.all()
	#for v in vg:
	#	vid = v.vid
	#	moby = v.mobygames_id
	#	if v.images < 1:
	#		Posters.getMobiCover(v.vid,v.mobygames_id)
	#	v.images = Posters.numVidPics(v.vid)
	#	v.save()
	#vg = VideoGame.objects.all()
	#for v in vg:
	#	Posters.makeVGThumb(v.vid)
	year = ""
	context = {}
	fvideogame = {}
	fscore = {}
	if fscore == {}:
		fscore['uid'] = request.user.get_profile()
		fscore['neveruse'] = False
	prevvote = False
	if request.is_ajax():
		if request.method == 'GET':
			params = request.GET
			template = 'vgvotingview.html'
			print params
		elif request.method == 'POST':
			params = request.POST
			winner = VideoGame.objects.get(vid=params['winner'])
			loser = VideoGame.objects.get(vid=params['loser'])
			prevvote = True
			
			userprofile = request.user.get_profile()
			ranks = CalculateRating('videogame',winner,loser,userprofile)
			template = 'vgvotingview.html'
	else:
		params = {}
		template = "indexvideogame.html"
	
	
	if 'gametype' in params:
		request.session['gametype'] = params['gametype']
	if request.session.get('gametype') != None:
		if request.session.get('gametype') ==  'winner':
			context['gametype'] = 'Winner Stays'
		elif request.session.get('gametype') ==  'loser':
			context['gametype'] = 'Loser Stays'
		else:
			context['gametype'] = 'Matchup Type'
	
	
	cat=None	
	
	if 'played' in params:
		request.session['played'] = params['played']
	if request.session.get('played') != None:
		print "session played {}".format(request.session.get('played'))
		if request.session.get('played') == 'True':
			fscore['played'] = True
	
	if 'cat' in params:
		request.session['cat'] = params['cat']
	if request.session.get('cat') == "All Categories":
		context['cat'] = "All Categories"
	#elif request.session.get('cat') != None:
		#context['cat'] = PersonCategory.objects.get(gid=request.session.get('cat')).category
		#cat = PersonCategory.objects.get(gid=request.session.get('cat'))
		#print cat.category
	#	fvideogame['cats__category']=cat.category
		
	if 'list' in params:
		request.session['list'] = params['list']
	if request.session.get('list') == 'top25':
		topfvideogame={}
		for i in fvideogame:
			index = "vid__" + str(i)
			topfvideogame[index] = fvideogame[i]
		elo = UserVideoGameScore.objects.filter(uid=request.user.get_profile()).filter(**topfvideogame).order_by('elorating').reverse()[25].elorating
		
		fscore['elorating__gte'] = elo
	elif request.session.get('list') == 'top250':
		topfvideogame={}
		for i in fvideogame:
			index = "vid__" + str(i)
			topfvideogame[index] = fvideogame[i]
		elo = UserVideoGameScore.objects.filter(uid=request.user.get_profile()).filter(**topfvideogame).order_by('elorating').reverse()[250].elorating
		
		fscore['elorating__gte'] = elo
	elif request.session.get('list') == 'undefeated':
		fscore['losses__lte'] = 0
	elif request.session.get('list') == 'newbie':
		fscore['numratings__lte'] = 3		
	elif request.session.get('list') != 'None':
		print request.session.get('list')
		#fvideogame['plist__list'] = request.session.get('list')
	else:
		True
	print fvideogame
					
	
	
	f = {'uid':request.user.get_profile()}
	#fscore = {}
	
	print fvideogame
	print fscore
	#fvideogame = {}
	
	
	
	if (request.session.get('gametype')=='winner' or request.session.get('gametype')=='loser') and request.method == 'POST':
		print "it was a post bitch"
		if request.session['gametype'] == 'winner':
			videogame1 = winner
		elif request.session['gametype'] == 'loser':
			videogame1 = loser
		videogame1mat = UserVideoGameScore.objects.get(uid=request.user.get_profile(),vid = videogame1)
		
		videogame2 = getOneVideoGame(fvideogame, fscore, videogame1,request.user.get_profile())
		if videogame2 == None:
			return HttpResponse("No People")
		else:
			videogame2mat = UserVideoGameScore.objects.get(uid=request.user.get_profile(),vid = videogame2)
	else:
		videogames = getTwoVideoGames(fvideogame,fscore,request.user.get_profile())		
		if videogames == None:
			videogame1 = None
			videogame2 = None
			videogame1mat = None
			videogame2mat = None
		else:
			videogame1 = videogames['1']
			videogame2 = videogames['2']
			videogame1mat = videogames['1mat']
			videogame2mat = videogames['2mat']
		
	topfvideogame={}
	for i in fvideogame:
		index = "vid__" + str(i)
		topfvideogame[index] = fvideogame[i]
	top25 = UserVideoGameScore.objects.filter(uid=request.user.get_profile()).filter(**topfvideogame).order_by('elorating').reverse()
	
	if (top25.count()>25):
		top25 = top25[:25]
	
	if prevvote:
		context['ranks'] = ranks
	
	context['videogame1'] = videogame1
	context['videogame1mat'] = videogame1mat
	context['videogame2'] = videogame2
	context['videogame2mat'] = videogame2mat
	#context['categories'] = PersonCategory.objects.all()
	#context['lists'] = PersonList.objects.all()
	context['videogamebar'] = True
	if videogame1 != None and videogame1.images>0:
		context['videogame1ran'] = random.randint(1,videogame1.images)
	if videogame2 != None and videogame2.images>0:
		context['videogame2ran'] = random.randint(1,videogame2.images)
	context['top20'] =  top25
	
	
	message = render_to_response(template, context,
		context_instance=RequestContext(request))
	return HttpResponse(message)



def VideoGameListHandler(request):
	context = {}
	userprof = request.user.get_profile()
	context['games'] = VideoGame.objects.all().order_by('title')
	context['vgames'] = UserVideoGameScore.objects.filter(uid = userprof)
	
	ugames = UserVideoGameScore.objects.filter(uid = userprof)
	context['game'] = {}
	for i in ugames:
		context['game'][i.vid.vid] = i.played
	
	
	template = "videogamelist.html"
	message = render_to_response(template, context,
		context_instance=RequestContext(request))
	return HttpResponse(message)


def VideoGamePlayedHandler(request):
	if request.is_ajax():
		if request.method == 'GET':
			params = request.GET
			#print params
		elif request.method == 'POST':
			params = request.POST
			print params
			userprof = request.user.get_profile()
			videogame = VideoGame.objects.get(vid = params['vgame'])
			try:
				videogamemat = UserVideoGameScore.objects.get(vid=videogame,uid=userprof)
				videogamemat.played = True
				videogamemat.save()
			except:
				videogamemat = UserVideoGameScore(uid =userprof, vid = videogame, played = True, elorating = 1000,numratings =0,wins=0,losses=0)
				videogamemat.save()

	data = [0]

	return HttpResponse(data, mimetype='application/javascript')
	


def getTwoVideoGames(fvideogame, fscore, userprof):
	#print "fvideogame {} fscore {}".format(fvideogame,fscore)
	if fscore != {}:
		for i in fvideogame:
			index = "vid__" + str(i)
			fscore[index] = fvideogame[i]
		print "fscore {}".format(fscore)
		randvideogames = UserVideoGameScore.objects.filter(**fscore).order_by('?')
		videogame1=None
		videogame2=None
		novideogame=True
		print len(randvideogames)
		for i in range(0,len(randvideogames)-1):
			for j in range(0,len(randvideogames)-1):
#				print "i {} len i {}".format(i,len(randvideogames)-1-i)
				if i!=j:
					videogame1 = randvideogames[i].vid
					videogame2 = randvideogames[j].vid
					videogame1mat = randvideogames[i]
					videogame2mat = randvideogames[j]
					if not (VideoGameMatchup.objects.filter(Q(winner = videogame1) | Q(winner = videogame2), 
														 Q(loser = videogame1) | Q(loser = videogame2), 
														 uid = userprof).exists()):
						videogames = {}
						videogames['1'] = videogame1
						videogames['1mat'] = videogame1mat
						videogames['2'] = videogame2
						videogames['2mat'] = videogame2mat
						return videogames
					else:
						novideogame=True
			
	else:	
		randvideogames = VideoGame.objects.filter(**fvideogame).order_by('?')
		videogame1=None
		videogame2=None
		novideogame = True
		for i in range(0,len(randvideogames)-1):
			for j in range(0,len(randvideogames)-1):
				if i!=j:
					videogame1 = randvideogames[i]
			
					videogame2 = randvideogames[j]
					try:
						videogame1mat = UserVideoGameScore.objects.get(vid=videogame1,uid=userprof)
					except:
						videogame1mat = UserVideoGameScore(uid =userprof, vid = videogame1, elorating = 1000,numratings =0,wins=0,losses=0)
						videogame1mat.save()
					try:
						videogame2mat = UserVideoGameScore.objects.get(vid=videogame2,uid=userprof)
					except:
						videogame2mat = UserVideoGameScore(uid =userprof, vid = videogame2, elorating = 1000,numratings =0,wins=0,losses=0)
						videogame2mat.save()
					if not (videogame1mat.neveruse == True
						or videogame2mat.neveruse == True
						or VideoGameMatchup.objects.filter(Q(winner = videogame1) | Q(winner = videogame2), Q(loser = videogame1) | Q(loser = videogame2), uid = userprof).exists()):
						videogames = {}
						videogames['1'] = videogame1
						videogames['1mat'] = videogame1mat
						videogames['2'] = videogame2
						videogames['2mat'] = videogame2mat
						return videogames
					else:
						novideogame = True
	
	if novideogame == True:
		print videogame1
		print videogame2
		return None
	
	videogames = {}
	videogames['1'] = videogame1
	videogames['1mat'] = videogame1mat
	videogames['2'] = videogame2
	videogames['2mat'] = videogame2mat
	return videogames

###TO DO FILTER ON FSCORE

def getOneVideoGame(fvideogame, fscore, videogame1,userprof):
	if fscore != {}:
		for i in fvideogame:
			index = "vid__" + str(i)
			fscore[index] = fvideogame[i]
		randvideogames = UserVideoGameScore.objects.filter(**fscore).order_by('?')
		videogame2 = None
		novideogame = True
		for i in range(0,len(randvideogames)):
			videogame2 = randvideogames[i].vid
			videogame2mat = randvideogames[i]
			if not (VideoGameMatchup.objects.filter(Q(winner = videogame1) | Q(winner = videogame2), Q(loser = videogame1) | Q(loser = videogame2), uid = userprof).exists() 
				or videogame1 == videogame2):
				novideogame = False
				break
			else:
				novideogame=True
			
	else:	
		randvideogames = VideoGame.objects.filter(**fvideogame).order_by('?')
		
		videogame2=None
		novideogame = True
		for i in range(0,len(randvideogames)):
			videogame2 = randvideogames[i]
			try:
				videogame2mat = UserVideoGameScore.objects.get(vid=videogame2,uid=userprof)
			except:
				videogame2mat = UserVideoGameScore(uid =userprof, vid = videogame2, elorating = 1000,numratings =0,wins=0,losses=0)
				videogame2mat.save()
			if not (videogame2mat.neveruse == True
				or VideoGameMatchup.objects.filter(Q(winner = videogame1) | Q(winner = videogame2), Q(loser = videogame1) | Q(loser = videogame2), uid = userprof).exists() 
				or videogame1 == videogame2):
				novideogame = False
				break
			else:
				novideogame = True
	
	if novideogame == True:
		return None
	
	
	return videogame2
	




def CalculateRating(type,winner,loser,u):
	if type == "videogame":
			try:
				winnersc = UserVideoGameScore.objects.get(uid = u,vid = winner)
			except:
				winnersc = UserVideoGameScore(uid = u, vid = winner, elorating = 1000,numratings =0,wins=0,losses=0)
				winnersc.save()
			try:
				losersc = UserVideoGameScore.objects.get(uid = u,vid = loser)
			except:
				losersc = UserVideoGameScore(uid =u, vid = loser, elorating = 1000,numratings =0,wins=0,losses=0)
				losersc.save()
			fwinner = {}
			floser = {}
			fwinner['elorating__gte'] = winnersc.elorating
			floser['elorating__gte'] = losersc.elorating
			oldwinnerrank = winnersc.rank
			oldloserrank = losersc.rank
			
			matchup = VideoGameMatchup.objects.filter((Q(winner=winner) & Q(loser=loser)) | (Q(loser=winner) & Q(winner=loser)),uid = u)
			if not (matchup.exists()):
				
				score = 200
				
				e = score - round(1 / (1 + math.pow(10, ((losersc.elorating - winnersc.elorating) / 400.0))) * score)
				winnersc.numratings = winnersc.numratings + 1
				
				winnersc.wins = winnersc.wins + 1
				
				winnersc.elorating = winnersc.elorating + e
				
				losersc.numratings = losersc.numratings + 1
				losersc.losses = losersc.losses + 1
				
				losersc.elorating = losersc.elorating - e
				
				matchup = VideoGameMatchup(winner = winner, loser = loser, uid = u, elo = e)
				
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
				matchup = VideoGameMatchup(winner = winner, loser = loser, uid = u, elo = e)
				matchup.save()
				#else:
				#	print "diff"
					
			fwinner['elorating__gt'] = winnersc.elorating
			floser['elorating__gt'] = losersc.elorating
			
			newwinnerrank = UserVideoGameScore.objects.filter(**fwinner).count()+1
			newloserrank = UserVideoGameScore.objects.filter(**floser).count()+1
			
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

