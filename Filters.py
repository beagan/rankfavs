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


def setFromParams(request,params,src_type):
#	request.session['filtvalues']['rematch'] = False
	print params
	if 'filtdict' not in request.session:#['filtdict'] == None:
		request.session['filtdict'] = {}
	if 'filtvalues' not in request.session:
		request.session['filtvalues'] = {}
		request.session['filtvalues']['rematch'] = False
	if 'clearfilters' in params:
		request.session['filtdict'] = {}
		request.session['filtvalues'] = {}
	if 'remove' in params:
		if params['remove'] == "rematch":
			request.session['filtvalues']['rematch'] = False
		elif params['remove'] in request.session['filtvalues']:
			del request.session['filtvalues'][params['remove']]
		if params['remove'] in request.session['filtdict']:
			del request.session['filtdict'][params['remove']]	
	if 'gametype' in params:
		if params['gametype'] == "winner":
			request.session['filtdict']['gametype'] = "Winner Stays"
		if params['gametype'] == "loser":
			request.session['filtdict']['gametype'] = "Loser Stays"
		if params['gametype'] == "close":
			request.session['filtdict']['gametype'] = "Close Matchup"
		if params['gametype'] == "randoms":
			del request.session['filtdict']['gametype']
			#request.session['filtdict']['l1']['gametype'] = "Winner Stays"
	if 'rematch' in params:
		if params['rematch'] == "Yes":
			request.session['filtdict']['rematch'] = "Allow Rematches"
			request.session['filtvalues']['rematch'] = True
		if params['rematch'] == "No":
			request.session['filtdict']['rematch'] = None
			request.session['filtvalues']['rematch'] = False
	if 'list' in params:
		if params['list'] == "top25":
			request.session['filtdict']['list'] = "Top 25"
		if params['list'] == "top250":
			request.session['filtdict']['list'] = "Top 250"
		if params['list'] == "undefeated":
			request.session['filtdict']['list'] = "Undefeated"
		if params['list'] == 'newbie':
			request.session['filtdict']['list'] = "Newbie"
	
	if src_type == 'person':
		if 'p_lockedin' in params:
			p = Person.objects.get(pid=params['p_lockedin'])
			request.session['filtvalues']['p_lockedin'] = p#params['lockedin']
			request.session['filtdict']['p_lockedin'] = p.name#params['lockedin']
			
			#If you are locking someone in the gametype will not be enforced as it does not make logical sense
			if 'gametype' in request.session['filtdict'] and (request.session['filtdict']['gametype'] == 'Winner Stays' or request.session['filtdict']['gametype'] == 'Loser Stays'):
				del request.session['filtdict']['gametype']
		if 'gender' in params:
			if params['gender'] == "Female":
				request.session['filtdict']['gender'] = "Female"
			if params['gender'] == "Male":
				request.session['filtdict']['gender'] = "Male"
			if params['gender'] == "everyone":
				del request.session['filtdict']['gender']
		if 'age' in params:
			if params['age'] == "20":
				request.session['filtdict']['age'] = "Under 20"
				request.session['filtvalues']['age'] = 20
			if params['age'] == "30":
				request.session['filtdict']['age'] = "Under 30"
				request.session['filtvalues']['age'] = 30
				print "30"
			if params['age'] == "40":
				request.session['filtdict']['age'] = "Under 40"
				request.session['filtvalues']['age'] = 40
			if params['age'] == "50":
				request.session['filtdict']['age'] = "Under 50"
				request.session['filtvalues']['age'] = 50
			if params['age'] == "51":
				request.session['filtdict']['age'] = "Over 50"
				request.session['filtvalues']['age'] = 51

	
	if src_type == "movie":
		if 'm_lockedin' in params:
			m = Movie.objects.get(pid=params['m_lockedin'])
			request.session['m_lockedin'] = m
			request.session['filtdict']['m_lockedin'] = m.title
			
			if 'gametype' in request.session['filtdict'] and (request.session['filtdict']['gametype'] == "Winner Stays" or request.session['filtdict']['gametype'] == 'Loser Stays'):
				del request.session['filtdict']['gametype']
		if 'imdbrating' in params:
			if params['imdbr'] == "10":
				request.session['filtdict']['imdbrating'] = "Perfect 10s"
				request.session['filtvalues']['imdbrating'] = 10
			if params['imdbr'] == "8":
				request.session['filtdict']['imdbrating'] = "Over 8"
				request.session['filtvalues']['imdbrating'] = 8
			if params['imdbr'] == "6":
				request.session['filtdict']['imdbrating'] = "Over 6"
				request.session['filtvalues']['imdbrating'] = 6
			if params['imdbr'] == "4":
				request.session['filtdict']['imdbrating'] = "Over 4"
				request.session['filtvalues']['imdbrating'] = 4
			if params['imdbr'] == "2":
				request.session['filtdict']['imdbrating'] = "Over 2"
				request.session['filtvalues']['imdbrating'] = 2	
		if 'decade' in params:
			if params['decade'] == "2010":
				request.session['filtdict']['decade'] = "2010s"
				request.session['filtvalues']['decade'] = 2010			
			if params['decade'] == "2000":
				request.session['filtdict']['decade'] = "2000s"
				request.session['filtvalues']['decade'] = 2000
			if params['decade'] == "1990":
				request.session['filtdict']['decade'] = "1990s"
				request.session['filtvalues']['decade'] = 1990
			if params['decade'] == "1980":
				request.session['filtdict']['decade'] = "1980s"
				request.session['filtvalues']['decade'] = 1980
			if params['decade'] == "1970":
				request.session['filtdict']['decade'] = "1970s"
				request.session['filtvalues']['decade'] = 1970
			if params['decade'] == "1960":
				request.session['filtdict']['decade'] = "1960s"
				request.session['filtvalues']['decade'] = 1960
			if params['decade'] == "1950":
				request.session['filtdict']['decade'] = "Before 1950"
				request.session['filtvalues']['decade'] = 1900
	
	###Might want to change these to all and false
	if 'played' in params:
		if params['played'] == "True":
			request.session['filtdict']['played'] = "Only Played"
			request.session['filtvalues']['played'] = True
		if params['played'] == "False":
			del request.session['filtdict']['played']
			request.session['filtvalues']['played'] = False
	if 'watched' in params:
		if params['watched'] == 'True':
			request.session['filtdict']['watched'] = "Only Watched"
			request.session['filtvalues']['watched'] = True
		if params['watched'] == 'False':
			del request.session['filtdict']['gametype']
			request.session['filtvalues']['watched'] = False
	results = {'filtdict':request.session['filtdict'],'filtvalues':request.session['filtvalues']}
	return results
			
def getMovieAndScoreFilters(request):
	fmovie = {}
	fscore = {}
	topfmovie = {}
	
	if 'imdbrating' in request.session['filtvalues']:
		fscore['imdb_rating__gte'] = request.session['filtvalues']['imdbrating']
	if 'decade' in request.session['filtvalues']:
		fmovie['year__gte'] = request.session['filtvalues']['decade']
		if request.session['filtvalues']['decade'] == 1900:
			fmovie['year__lte'] = request.session['filtvalues']['decade']+50
		else:
			fmovie['year__lte'] = request.session['filtvalues']['decade']+10
	if 'list' in request.session['filtdict']: 
		if request.session['filtdict']['list'] == 'Top 25':
			topfmovie = {}
			for i in fmovie:
				index = "mid__" + str(i)
				topfmovie[index] = fmovie[i]
			elo = UserMovieScore.objects.filter(uid=request.user.get_profile()).filter(**topfmovie).order_by('elorating').reverse()
			if (elo.count()>25):
				elo = elo[25].elorating
			else:
				elo = 0
			fscore['elorating__gte'] = elo		
		elif request.session['filtdict']['list']  == 'Top 250':
			topfperson={}
			for i in fmovie:
				index = "mid__" + str(i)
				topfmovie[index] = fmovie[i]
	
			c = UserMovieScore.objects.filter(uid=request.user.get_profile()).filter(**topfmovie).count()
			if c>249:
				elo = UserPersonScore.objects.filter(uid=request.user.get_profile()).filter(**topfmovie).order_by('elorating').reverse()[250].elorating
			else:
				elo = UserPersonScore.objects.filter(uid=request.user.get_profile()).filter(**topfmovie).order_by('elorating')[0].elorating
			fscore['elorating__gte'] = elo
		elif request.session['filtdict']['list']  == 'Undefeated':
			fscore['losses__lte'] = 0
		elif request.session['filtdict']['list'] == 'Newbie':
			fscore['numratings__lte'] = 3
	
	results = {'fmovie':fmovie,'fscore':fscore,'topfmovie':topfmovie}
	print results
	return results




def getPersonAndScoreFilters(request):
	fperson = {}
	fscore = {}
	topfperson = {}
	if 'age' in request.session['filtvalues']: 
		if request.session['filtvalues']['age'] < 51:
			year = 2012 - int(request.session['filtvalues']['age'])
			##TODO: real date
			age = datetime(year,1,1)
			fperson['dob__gte'] = age
		elif request.session['filtvalues']['age'] == 51:
			year = 2012 - int(request.session['filtvalues']['age'])
			##TODO: real date
			age = datetime(year,1,1)
			fperson['dob__lte'] = age
					
	if 'gender' in request.session['filtdict']:
		fperson["gender"] = request.session['filtdict']['gender']
	
	if 'list' in request.session['filtdict']:
		if request.session['filtdict']['list'] == 'Top 25':
			topfperson={}
			for i in fperson:
				index = "pid__" + str(i)
				topfperson[index] = fperson[i]
			elo = UserPersonScore.objects.filter(uid=request.user.get_profile()).filter(**topfperson).order_by('elorating').reverse()
			if (elo.count()>25):
				elo = elo[25].elorating
			else:
				elo = 0
			fscore['elorating__gte'] = elo
		
		elif request.session['filtdict']['list']  == 'Top 250':
			topfperson={}
			for i in fperson:
				index = "pid__" + str(i)
				topfperson[index] = fperson[i]
		
			c = UserPersonScore.objects.filter(uid=request.user.get_profile()).filter(**topfperson).count()
			if c>249:
				elo = UserPersonScore.objects.filter(uid=request.user.get_profile()).filter(**topfperson).order_by('elorating').reverse()[250].elorating
			else:
				elo = UserPersonScore.objects.filter(uid=request.user.get_profile()).filter(**topfperson).order_by('elorating')[0].elorating
			fscore['elorating__gte'] = elo
		
		elif request.session['filtdict']['list']  == 'Undefeated':
			fscore['losses__lte'] = 0
		elif request.session.get('list') == 'Newbie':
			fscore['numratings__lte'] = 3
		elif request.session.get('list') == 'notedit':
			fperson['image_edit'] = False
		elif request.session.get('list') != None:
			#print "session list is {}".format(request.session.get('list'))
			fperson['plist__list'] = request.session.get('list')
			request.session['filtdict']['list'] = request.session.get('list')	
	
	
	results = {'fperson':fperson,'fscore':fscore,'topfperson':topfperson}
	return results
	