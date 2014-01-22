from datetime import datetime, timedelta
from rankyourfavs.rankfavs.models import *
from django.template import Context, loader, RequestContext
from django.shortcuts import render_to_response
from django.db import connection
import random
import math
import operator
from django.http import HttpResponse,HttpResponseRedirect
from django.db.models import Q
from django.db.models import Avg
from django.shortcuts import redirect
import simplejson
import os
import shutil
import time
from datetime import date
from Queue import Queue
import Posters
import Filters
from django import forms
from django.forms import ModelForm, Textarea
from django.contrib.auth.decorators import login_required
from taggit.models import Tag

from Calculate import calculateRating

class PersonForm(ModelForm):
	def clean(self):
		cleaned_data = self.cleaned_data
		for k in self.cleaned_data:
			if self.cleaned_data[k] == '':
				cleaned_data[k] = None
		return cleaned_data
		
	class Meta:
		model = Person
		exclude = ('sid','images','image_edit','twitter_verified','twitter_followers','twitter_followers_percentile','google_results',
					'google_results_percentile','google_search_volume','google_search_volume_total','google_search_volume_percentile',
					'bing_results','bing_results_percentile','popularity_rating')
		widgets = 	{
						'bio': Textarea(attrs={'cols': 80, 'rows': 20}),
					}
				





def PersonSearchHandler(request):
	context = {}
	if 'ranked' in request.GET:
		ranked = True
	else:
		ranked = False
	if 'tag' in request.GET:
		key = request.GET['tag']
		if ranked:
			f={}
			f['pid__tags__slug'] = key
			f['uid'] = request.user.get_profile()
			sresults = UserPersonScore.objects.filter(**f).order_by('elorating').reverse()[:100]
			context['sresults'] = sresults
		else:
			results = Person.objects.filter(Q(tags__slug__icontains=key))[:100]
			context['results'] = results
	#	print results
	else:
		queries = request.GET.get('s').split()
		qset1 =  reduce(operator.__or__, [Q(name__icontains=query) | Q(chickipedia_id__icontains=query) for query in queries])
			
		results = Person.objects.filter(qset1).distinct()
		context['results'] =  results
		
	
	template = 'htmlresults.html'
	message = render_to_response(template, context,
		context_instance=RequestContext(request))
	return HttpResponse(message)
	


def PersonTagAverages(request):
	
	tags = Person.tags.most_common()
	f={}
	average={}
	context={}
	for i in tags:
		f['pid__tags__slug'] = i.slug
		f['uid'] = request.user.get_profile()
		a = UserPersonScore.objects.filter(**f).order_by('elorating').reverse()[0:25].annotate()
		print a
		a = a.aggregate(Avg('elorating'))
		if a['elorating__avg'] != None:
			a = round(a['elorating__avg'])
			average[i.name] = a
	
	sorted_x = sorted(average.iteritems(), key=operator.itemgetter(1),reverse=True)
	#sorted_x = sorted_x.reverse()
	print sorted_x
	context['taglist'] = sorted_x
	template='htmlresults.html'
	message = render_to_response(template, context,
		context_instance=RequestContext(request))
	return HttpResponse(message)



@login_required(login_url="/")
def PersonMatchHandler(request):
	year = ""
	context = {}
	#fperson = {}
	#fscore = {'uid':request.user.get_profile(),'neveruse':False}
	fscore = {}
	prevvote = False
	if request.is_ajax():
		if request.method == 'GET':
			params = request.GET
			template = 'personvotingview.html'
			print params
		elif request.method == 'POST':
			params = request.POST
			winner = Person.objects.get(pid=params['winner'])
			loser = Person.objects.get(pid=params['loser'])
			prevvote = True
			
			userprofile = request.user.get_profile()
			ranks = CalculateRating('person',winner,loser,userprofile)
			template = 'personvotingview.html'
	else:
		params = request.GET
		template = "indexperson.html"
	
	results = Filters.setFromParams(request,params,'person')
	request.session['filtdict'] = results['filtdict']
	request.session['filtvalues'] = results['filtvalues']
	
	results = Filters.getPersonAndScoreFilters(request)
	fperson = results['fperson']
	fscore = results['fscore']
	topfperson = results['topfperson']
	
	
	if 'Food.objects.filter(tags__name__in=["delicious"])' in params:
		request.session['filtdict']['search'] = Person.objects.get(pid=params['search']).name
		request.session['search'] = params['search']
		
	##########################################
	#TEMPORARY UNTIL TAGGING GETS IMPLEMENTED
#	if 'cat' in params:
#		if params['cat'] == 'All Categories':
#			request.session['cat'] = None
#		else:
#			request.session['cat'] = params['cat']	
#	cat=None	
#	if request.session.get('cat') != None:
#		cat = PersonCategory.objects.get(gid=request.session.get('cat'))
#		context['cat'] = PersonTag.objects.get(slug=request.session.get('cat'))
#		request.session['filtdict']['cat'] = context['cat']
#		fperson['tags__slug'] = request.session.get('cat')
#		#fperson['cats__category']=cat.category
#	else:
#		context['cat'] = "All Categories"
	#############################################
	
	rematch = request.session['filtvalues']['rematch']
	if 'gametype' in request.session['filtdict'] and request.session['filtdict']['gametype'] == 'Close Matchup':
		close_matchup = True
	else:
		close_matchup = False
	
	if fscore != {}:
		fscore['uid'] = request.user.get_profile()
		fscore['neveruse'] = False
	
	print "fperson {} fscore {}".format(fperson, fscore)
	
	
	if 'gametype' in request.session['filtvalues'] and (request.session['filtvalues']['gametype']=='winner' or request.session['filtvalues']['gametype']=='loser') and request.method == 'POST':
		print "it was a post bitch"
		if request.session['filtvalues']['gametype'] == 'winner':
			person1 = winner
		elif request.session['filtvalues']['gametype'] == 'loser':
			person1 = loser
		person1mat = UserPersonScore.objects.get(uid=request.user.get_profile(),pid = person1)
		results = getOnePerson(fperson, fscore, rematch, person1,request.user.get_profile(),25)
		person2 = results['person']
		person2mat = results['matchup']
	elif 'p_lockedin' in request.session['filtvalues'] and request.session['filtvalues']['p_lockedin'] != None:
		print "lockedin"
		person1 = request.session['filtvalues']['p_lockedin']#Person.objects.get(pid = request.session['lockedin'])
		try:
			person1mat = UserPersonScore.objects.get(uid = request.user.get_profile(),pid=person1)
		except:
			person1mat = UserPersonScore(uid = request.user.get_profile(), pid=person1, elorating = 1000,numratings =0,wins=0,losses=0)
			person1mat.save()
		if close_matchup:
			results = getCloseOnePerson(fperson,fscore,rematch,person1,person1mat,request.user.get_profile())
		else:
			results = getOnePerson(fperson, fscore, rematch, person1, request.user.get_profile(),25)
		person2 = results['person']
		person2mat = results['matchup']
	else:
		print request.session['filtvalues']
		print "two people"
		people = getTwoPeople(fperson,fscore,rematch,request.user.get_profile(),25)		
		if people == None:
			person1 = None
			person2 = None
			person1mat = None
			person2mat = None
		else:
			person1 = people['1']
			person2 = people['2']
			person1mat = people['1mat']
			person2mat = people['2mat']
	if person1 == None or person2 == None:
		person1 = None
		person2 = None
		person1mat = None
		person1mat = None
		#return HttpResponse("NO PEOPLE")
	topfperson={}
	
	if 'popularity_rating__gte' in fperson:
		del fperson['popularity_rating__gte']
	
	for i in fperson:
		index = "pid__" + str(i)
		topfperson[index] = fperson[i]
	print topfperson
	top25 = UserPersonScore.objects.filter(uid=request.user.get_profile()).filter(**topfperson).order_by('elorating').reverse()
	if (top25.count()>25):
		top25 = top25[:25]
	
	if prevvote:
		context['ranks'] = ranks
	
	#t1 = time.time()
	
	#for i in range(1,1000):
	#	testtvshows = getTwoPeople(fperson,fscore,rematch,request.user.get_profile(),25)
	#t2 = time.time()
	
	#print "1000 2 people was {}".format(t2-t1)
	
	
	context['filters'] = request.session.get('filtdict')
	context['person1'] = person1
	context['person1mat'] = person1mat
	context['person2'] = person2
	context['person2mat'] = person2mat
	context['p_tag'] = Person.tags.most_common()
	context['lists'] = PersonList.objects.all()
	context['peoplebar'] = True
	
	if person1 != None and person1.images>0:
		print person1.images
		context['person1ran'] = random.randint(1,person1.images)
	if person2 != None and person2.images>0:
		context['person2ran'] = random.randint(1,person2.images)
	context['top20'] =  top25
	
	
	message = render_to_response(template, context,
		context_instance=RequestContext(request))
	return HttpResponse(message)


def PersonListHandler(request):
	context = {}
	
	userprof = request.user.get_profile()
	fperson = {}
	
	if request.session.get('gender') != None and request.session.get('gender') != 'everyone':
		fperson["gender"] = request.session.get('gender')
	
	if request.session.get('age') != None: 
		if request.session.get('age')!='all':
			if int(request.session.get('age')) < 51:
				year = 2012 - int(request.session.get('age'))
				##TODO: real date
				age = datetime(year,1,1)
				fperson['dob__gte'] = age
			elif int(request.session.get('age')) == 51:
				year = 2012 - int(request.session.get('age'))
				##TODO: real date
				age = datetime(1500,1,1)
				fperson['dob__lte'] = age
	
	
	context['people'] = Person.objects.filter(**fperson).order_by('name')[:100]
	context['upeople'] = UserPersonScore.objects.filter(uid = userprof)
	
	ugames = UserPersonScore.objects.filter(uid = userprof)
	context['upeople'] = {}
	for i in ugames:
		context['upeople'][i.pid.pid] = i.neveruse
	
	
	template = "peoplelist.html"
	message = render_to_response(template, context,
		context_instance=RequestContext(request))
	return HttpResponse(message)	


def NeverUsePersonHandler(request):
	context={}
	if request.method == 'GET':
		params = request.GET
		print params
	elif request.method == 'POST':
		params = request.POST
	if 'neveruse' in params:
		print params
		person = UserPersonScore.objects.get(uid=request.user.get_profile(),pid=params['neveruse'])
		person.neveruse = True
		person.eloscore = 0
		person.save()
	
	
	
	#TODO
	fperson={}
	fscore={}
	person1 = Person.objects.get(pid=params['otherperson'])
	person1mat = UserPersonScore.objects.get(uid=request.user.get_profile(),pid = person1)
	
	
	top20 = UserPersonScore.objects.filter(uid=request.user.get_profile()).order_by('elorating').reverse()[:100]
	print person1
	
	
	##########SHOULD BE ABLE TO SIMPLIFY THIS TO USE SAME AS MATCH HANDLER
	
	if request.session.get('rematch') == 'Yes':
		rematch = True
		context['rematch'] = "Rematches Allowed"
		request.session['filtdict']['rematch'] = 'Rematches Allowed'
	else:
		rematch = False
		context['rematch'] = "No Rematches"
		if 'rematch' in request.session['filtdict']:
			del request.session['filtdict']['rematch']
	
	person2 = getOnePerson(fperson, fscore, rematch, person1,request.user.get_profile(),25)
	print person2
	if person2 == None:
		return HttpRespone("No People")
	else:
		try:
			person2mat = UserPersonScore.objects.get(uid=request.user.get_profile(),pid = person2)
		except:
			person1mat = UserPersonScore(uid = request.user.get_profile(), pid = person2, elorating = 1000,numratings =0,wins=0,losses=0,neveruse=False)
		context['person1'] = person1
		context['person2'] = person2
		if person1.images>0:
			context['person1ran'] = random.randint(1,person1.images)
		if person2.images>0:
			context['person2ran'] = random.randint(1,person2.images)
		context['top20'] =  top20
		if 'gametype' in params:
			if params['gametype'] == 'winner':
				request.session['gametype'] = 'winner'
				context['gametype'] = 'winner'
			elif params['gametype'] == 'loser':
				request.session['gametype'] = 'loser'
				print request.session['gametype']
				context['gametype'] = 'loser'
		elif request.session.get('gametype','winner'):
			context['gametype'] = 'winner'
		elif request.session.get('gametype','loser'):
			context['gametype'] = 'loser'
	
	if request.is_ajax():		
		template = 'personvotingview.html'
	else:
		template = 'indexperson.html'
	print template
	#message = render_to_response(template, context,
#		context_instance=RequestContext(request))
	#return HttpResponse(message)
	url = '/people'
	return redirect(url)	




def PersonEditHandler(request):
	context = {}
	if request.method == 'GET':
		params = request.GET
	else:
		params = request.POST
		
	if 'pid' in params:
		pid = params['pid']
		p = Person.objects.get(pid = pid)
	else:
		p=None
	
	
	if request.method == 'GET':
		
		params = request.GET
		print params
		context['person'] = p
		context['dob'] = "{}/{}/{}".format(p.dob.year,p.dob.month,p.dob.day)
		context['form'] = PersonForm(instance=p)
		print context
		message = render_to_response('personedit.html',context,context_instance=RequestContext(request))
		return HttpResponse(message)
		
	elif request.method == 'POST':
		#pid = request.POST['pid']
		person = p#Person.objects.get(pid=pid)
		params = request.POST
		form = PersonForm(request.POST,instance=p)
		print form.errors
		if form.is_valid():
			person = form.save()
			person.save()
			url = reverse('person',args=(person.pid,))
			return redirect(url)
		else:
			print form.is_valid()
			return HttpResponse()
		



def PersonEditSubmitHandler(request):
	if request.method == "POST":
		params = request.POST
		
		p = Person.objects.get(pid = params['pid'])
		
		p.name = params['name']
		
		p.gender = params['Gender']
		
		if params['chickipedia_id'] == "None":
			p.chickipedia_id = None
		else:
			p.chickipedia_id = params['chickipedia_id']
		if params['imdb_id'] == "None":
			p.imdb_id = None
		else:
			p.imdb_id = params['imdb_id']
		if params['netflix_id'] == "None":
			p.netflix_id = None
		else:
			p.netflix_id = params['netflix_id']
		if params['tvrage_id'] == "None":
			p.tvrage_id = None
		else:
			p.tvrage_id = params['tvrage_id']
		if params['twitter'] == "None":
			p.twitter = None
		else:
			p.twitter = params['twitter']
		if params['wikipedia_link'] == "None":
			p.wikipedia_link = None
		else:
			p.wikipedia_link = params['wikipedia_link']
		if 'thumb' in params:
			Posters.makeThumbByPic(p.pid,1)
		
		d = params['dob'].split("/")
		p.dob = date(int(d[0]),int(d[1]),int(d[2]))
		
		p.save()
	#p = Person.objects.filter(gender="Unknown").order_by('?')[0]
	#url = '/editperson?pid='+str(p.pid)
	
	
	url = '/person?pid='+params['pid']
	return redirect(url)



def TemporaryPersonListHandler(request):
	persons = TemporaryPerson.objects.all().order_by('freeones_rank')[:100]
	context={}
	context['people'] = persons
	
	message = render_to_response('temporarypersonlist.html',context,context_instance=RequestContext(request))
	return HttpResponse(message)



def TemporaryPersonEditSubmitHandler(request):
	if request.method == "GET":
		params = request.GET
	if request.method == "POST":
		params = request.POST
		print params
		p = TemporaryPerson.objects.get(temp_id = params['pid'])
		
		p.name = params['name']
		
		p.gender = params['Gender']
		
		if params['chickipedia_id'] == "None":
			p.chickipedia_id = None
		else:
			p.chickipedia_id = params['chickipedia_id']
		if params['imdb_id'] == "None":
			p.imdb_id = None
		else:
			p.imdb_id = params['imdb_id']
		if params['netflix_id'] == "None":
			p.netflix_id = None
		else:
			p.netflix_id = params['netflix_id']
		if params['tvrage_id'] == "None":
			p.tvrage_id = None
		else:
			p.tvrage_id = params['tvrage_id']
		if params['twitter'] == "None":
			p.twitter = None
		else:
			p.twitter = params['twitter']
		if params['wikipedia_link'] == "None":
			p.wikipedia_link = None
		else:
			p.wikipedia_link = params['wikipedia_link']
		
		dir="/Users/Jason/person/temp/"+str(p.temp_id)+"/"
		oldchecks=0
		oldindex = []
		old = p.images
		for i in range(1,old+1):
			check = "old" + str(i)
			if check in params:
				print check
				oldchecks += 1
				oldindex.append(i)
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
		for i in range(1,old+1):
			if os.path.isfile(dir+str(i)+".jpg"):
				last=i
		
		p.images = last
		
		d = params['dob'].split("/")
		p.dob = date(int(d[0]),int(d[1]),int(d[2]))
		
		p.save()
		context={}
		context['person'] = p
		context['range'] = range(1,p.images+1)
		
		context['dob'] = "{}/{}/{}".format(p.dob.year,p.dob.month,p.dob.day)
		
		context['time'] = time.time()
		
		print context
		
	#########Add picture saving
	#########Add redirection to edittemporary person page, also add there the ability to load via param
	if 'commit' in params and params['commit'] == "on":
		temp = TemporaryPerson.objects.get(temp_id = params['pid'])
		old_id = temp.temp_id
		p = Person(name = temp.name,gender=temp.gender,imdb_id=temp.imdb_id,twitter=temp.twitter,wikipedia_link=temp.wikipedia_link,images=temp.images)
		p.save()
		temp.delete()
		if p.wikipedia_link != None:
			getDOBandBiofromWikipedia(p.wikipedia_link)
		#make thumbnail
		new_id = p.pid
		
		src = "/Users/Jason/person/temp/" + str(old_id)
		dst = "/Users/Jason/person/" + str(new_id)
		try:
			shutil.move(src,dst)
		except:
			print "directory missing"
		
		src = "/Users/Jason/person/thumb/temp/" + str(old_id) + ".jpg"
		dst = "/Users/Jason/person/thumb/" + str(new_id) + ".jpg"
		
		try:
			shutil.move(src,dst)
		except:
			print "directory missing"
		
		###Delete old picture folder and transition to new picture folder based on id of the newly saved person		
		
		
		url = '/person?pid='+str(new_id)
		return redirect(url)
		
	message = render_to_response('confirmadd.html',context,context_instance=RequestContext(request))
	return HttpResponse(message)
	#p = Person.objects.filter(gender="Unknown").order_by('?')[0]
	#url = '/editperson?pid='+str(p.pid)
	
	
def RemoveTemporaryPersonHandler(request):
	if request.method == "POST":
		if 'removeall' in request.POST:
			p = TemporaryPerson.objects.all()
			for i in p:
				i.delete()
				dir = "/Users/Jason/person/temp/"+str(i.temp_id)+"/"
				if os.path.exists(dir):
					shutil.rmtree(dir)
		else:
			params = request.POST.getlist('temp')
			print params
			for i in params:

				temp = TemporaryPerson.objects.get(temp_id=i)
				temp.delete()
				dir = "/Users/Jason/person/temp/"+str(temp.temp_id)+"/"
				if 	os.path.exists(dir):
					shutil.rmtree(dir)
	
	url = "/addpersonqueue"
	return redirect(url)
	
	


def eloChart(request):
	
	params= request.GET
	pid = params["pid"]
	p = Person.objects.get(pid=pid)
	userprofile = request.user.get_profile()
	objects = PersonMatchup.objects.filter((Q(winner = pid) | Q(loser = pid)), uid=userprofile)
	week=0;weektotal=0;weektotals=[]
	data ='['
	count =0
	total = 1000
	for o in objects:
		if o.winner == p:
			total += o.w_elo
			data += simplejson.dumps( [count, total] )
		else:
			total -= o.l_elo
			data += simplejson.dumps( [count, total] )
		count +=1
		data += ", "
			
	data = data[0:len(data)-2]
	data += ']'
	ret = simplejson.dumps({'label' : p.name, 'data' : "{replaceme}",
	}, indent = 4)
	return HttpResponse(ret.replace('"{replaceme}"', data), mimetype='application/javascript')


def RefreshPersonRanksHandler(request):
	t1 = time.time()
	
	f={}
	userprofile = request.user.get_profile()
	persons = UserPersonScore.objects.filter(uid=userprofile)
	for p in persons:
		f = {}
		f['elorating__gt'] = p.elorating
		
		p.rank = UserPersonScore.objects.filter(**f).count()+1
		try:
			f['pid__gender'] = p.pid.gender
			p.genderrank = UserPersonScore.objects.filter(**f).count()+1
			p.save()
		except:
			p.delete()
			print "WTF"
		
		
	t2 = time.time()
	
	print "rank refresher took {}".format(t2-t1)
	
	url = '/toplist'
	return redirect(url)
	


def getTwoPeople(fperson, fscore, rematch, userprof,recurse):
	#print "fperson {} fscore {}".format(fperson,fscore)
	
	r = int(round(math.log(random.uniform(1,10),10)*10))
	fperson['popularity_rating__gte'] = r
	print "pop rating threshold {}".format(r)
	if recurse == 0:
		return None
	
	if fscore != {}:
		for i in fperson:
			index = "pid__" + str(i)
			fscore[index] = fperson[i]
		print "fscore {}".format(fscore)
		randpeople = UserPersonScore.objects.filter(**fscore).order_by('?')
		person1=None
		person2=None
		noperson=True
		print len(randpeople)
		for i in range(0,len(randpeople)-1):
			print i
			for j in range(i+1,len(randpeople)-1):
#				print "i {} len i {}".format(i,len(randpeople)-1-i)
				if i!=j:
					person1 = randpeople[i].pid
					person2 = randpeople[j].pid
					person1mat = randpeople[i]
					person2mat = randpeople[j]
					if rematch:
						people = {}
						people['1'] = person1
						people['1mat'] = person1mat
						people['2'] = person2
						people['2mat'] = person2mat
						return people
						
					else:
						if not (PersonMatchup.objects.filter(Q(winner = person1) | Q(winner = person2), 
															 Q(loser = person1) | Q(loser = person2), 
															 uid = userprof).exists()):
							people = {}
							people['1'] = person1
							people['1mat'] = person1mat
							people['2'] = person2
							people['2mat'] = person2mat
							return people
						else:
							noperson=True
			
	else:	
		randpeople = Person.objects.filter(**fperson).order_by('?')
		person1=None
		person2=None
		noperson = True
		for i in range(0,len(randpeople)-1):
			print i
			for j in range(i+1,len(randpeople)-1):
				#check if same person
				if i!=j:
					person1 = randpeople[i]
			
					person2 = randpeople[j]
					try:
						person1mat = UserPersonScore.objects.get(pid=person1,uid=userprof)
					except:
						person1mat = UserPersonScore(uid =userprof, pid = person1, elorating = 1000,numratings =0,wins=0,losses=0)
						person1mat.save()
					try:
						person2mat = UserPersonScore.objects.get(pid=person2,uid=userprof)
					except:
						person2mat = UserPersonScore(uid =userprof, pid = person2, elorating = 1000,numratings =0,wins=0,losses=0)
						person2mat.save()
					if rematch:
						if not (person1mat.neveruse == True
							or person2mat.neveruse == True):
							people = {}
							people['1'] = person1
							people['1mat'] = person1mat
							people['2'] = person2
							people['2mat'] = person2mat
							return people						
					else:
						if not (person1mat.neveruse == True
							or person2mat.neveruse == True
							or PersonMatchup.objects.filter(Q(winner = person1) | Q(winner = person2), Q(loser = person1) | Q(loser = person2), uid = userprof).exists()):
							people = {}
							people['1'] = person1
							people['1mat'] = person1mat
							people['2'] = person2
							people['2mat'] = person2mat
							return people
						else:
							noperson = True
	
	if noperson == True:
		recurse -= 1
		return getTwoPeople(fperson, fscore, rematch, userprof,recurse)
	
	
	
	people = {}
	people['1'] = person1
	people['1mat'] = person1mat
	people['2'] = person2
	people['2mat'] = person2mat
	return people
	

###TO DO FILTER ON FSCORE
def getOnePerson(fperson, fscore, rematch, person1,userprof,recurse):
	if recurse == 0:
		return {'person':None,'matchup':None}
	
	r = int(round(math.log(random.uniform(1,10),10)*10))
	fperson['popularity_rating__gte'] = r
	print "pop rating threshold {}".format(r)
	
	
	
	print "rematch {}".format(rematch)
	
	if fscore != {}:
		for i in fperson:
			index = "pid__" + str(i)
			fscore[index] = fperson[i]
		randpeople = UserPersonScore.objects.filter(**fscore).order_by('?')
		person2 = None
		noperson = True
		for i in range(0,len(randpeople)):
			person2 = randpeople[i].pid
			person2mat = randpeople[i]
			if rematch:
				if person1 != person2:
					noperson = False
					break
			else:
				if not (PersonMatchup.objects.filter(Q(winner = person1) | Q(winner = person2), Q(loser = person1) | Q(loser = person2), uid = userprof).exists() 
					or person1 == person2):
					noperson = False
					break
				else:
					noperson=True
			
	else:	
		randpeople = Person.objects.filter(**fperson).order_by('?')
		
		person2=None
		noperson = True
		for i in range(0,len(randpeople)):
			person2 = randpeople[i]
			try:
				person2mat = UserPersonScore.objects.get(pid=person2,uid=userprof)
			except:
				person2mat = UserPersonScore(uid =userprof, pid = person2, elorating = 1000,numratings =0,wins=0,losses=0)
				person2mat.save()
			if rematch:
				if person1 != person2:
					noperson = False
					break
			else:
				if not (person2mat.neveruse == True
					or PersonMatchup.objects.filter(Q(winner = person1) | Q(winner = person2), Q(loser = person1) | Q(loser = person2), uid = userprof).exists() 
					or person1 == person2):
					noperson = False
					break
				else:
					noperson = True
	
	if noperson == True:
		recurse -= 1
		return getOnePerson(fperson, fscore, rematch, person1,userprof,recurse)
		#return {'person':None,'matchup':None}
	
	try:
		person2mat = UserPersonScore.objects.get(pid=person2,uid=userprof)
	except:
		person2mat = UserPersonScore(uid =userprof, pid = person2, elorating = 1000,numratings =0,wins=0,losses=0)
		person2mat.save()
		
	results = {}
	results['person'] = person2
	results['matchup'] = person2mat
	return {'person':person2,'matchup':person2mat}


def getCloseOnePerson(fperson, fscore, rematch, person1,person1mat,userprof):
	
	fscore['elorating__gte'] = person1mat.elorating-50
	fscore['elorating__lte'] = person1mat.elorating+50
	
	fscore['uid'] = userprof
	fscore['neveruse'] = False
	
	for i in fperson:
		index = "pid__" + str(i)
		fscore[index] = fperson[i]
	randpeople = UserPersonScore.objects.filter(**fscore).order_by('?')
	person2 = None
	noperson = True
	print fscore
	print rematch
	for i in range(0,len(randpeople)):
		person2 = randpeople[i].pid
		person2mat = randpeople[i]
		if rematch:
			if person1 != person2:
				noperson = False
				break
		else:
			if not (PersonMatchup.objects.filter(Q(winner = person1) | Q(winner = person2), Q(loser = person1) | Q(loser = person2), uid = userprof).exists() 
				or person1 == person2):
				noperson = False
				break
			else:
				noperson=True
		
	if noperson == True:
		return {'person':None,'matchup':None}
	
	try:
		person2mat = UserPersonScore.objects.get(pid=person2,uid=userprof)
	except:
		person2mat = UserPersonScore(uid =userprof, pid = person2, elorating = 1000,numratings =0,wins=0,losses=0)
		person2mat.save()
		
	results = {}
	results['person'] = person2
	results['matchup'] = person2mat
	return {'person':person2,'matchup':person2mat}


def PersonHandler(request, pid):
	params= request.GET
	
	if 'pid' in params:
		pid = params["pid"]
	else:
		pid = pid
	userprofile = request.user.get_profile()
	try:
		p = Person.objects.get(pid = pid)
	except:
		p = None
	try:
		pp = UserPersonScore.objects.get(pid = pid,uid=userprofile)
	except:
		pp= None
	matchups = PersonMatchup.objects.filter(Q(winner=pid,uid=userprofile) | Q(loser=pid,uid=userprofile)).order_by('matchupid')
	print p.images
	context = {
			'person': p,
			'personscore':pp,
			'matchups':matchups,
			'range':range(1,p.images+1)
	}
	print context
	message = render_to_response('person.html',context,context_instance=RequestContext(request))
	return HttpResponse(message)


def ReversePersonVoteHandler(request):
	if request.is_ajax():
		if request.method == 'POST':
			message = "This is an XHR POST request"
			
			prevwinner = Person.objects.get(pid=request.POST['winner'])
			prevloser = Person.objects.get(pid=request.POST['loser'])
			elo = int(request.POST['elo'])
			
	else:
		if request.method == 'POST':
			prevwinner = Person.objects.get(pid=request.POST['winner'])
			prevloser = Person.objects.get(pid=request.POST['loser'])
			elo = int(request.POST['elo'])
	
	u = request.user.get_profile()
	
	matchup = PersonMatchup.objects.get(winner=prevwinner,loser=prevloser,uid=u)
	
	matchup.winner = prevloser
	matchup.loser = prevwinner
	
	winnersc = UserPersonScore.objects.get(uid = u,pid = prevloser)
	winnersc.elorating = winnersc.elorating + elo
	
	losersc = UserPersonScore.objects.get(uid = u,pid = prevwinner)
	losersc.elorating = losersc.elorating - elo
	
	score = 24
	
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
	
	data = {'matchupid':int(matchup.matchupid),'winner':{'pid':int(winnersc.pid.pid),'name':winnersc.pid.name},'loser':{'pid':int(losersc.pid.pid),'name':losersc.pid.name},'elo':e}
	
	data = simplejson.dumps(data)
	
	return HttpResponse(data, mimetype='application/javascript')


def IgnoredPeopleHandler(request):
	context = {}
	
	userprofile = request.user.get_profile()
	
	context['ignored'] = UserPersonScore.objects.filter(uid = request.user.get_profile(),neveruse=True)
	print context	
	template = 'ignoredperson.html'
	
	message = render_to_response(template, context,
		context_instance=RequestContext(request))
	return HttpResponse(message)
	


def RemovePersonHandler(request):
	if request.method == 'POST':
		params = request.POST
	
		p = Person.objects.get(pid=params['pid'])
		
		matchups = PersonMatchup.objects.filter(Q(winner=p) | Q(loser=p))
		count =0
		for s in matchups:
			if s.winner == p:
				print "winner"
				other = UserPersonScore.objects.get(pid=s.loser.pid,uid=s.uid)
				
				other.elorating += s.w_elo
				
				other.losses -= 1
				other.numratings -=1
				
				other.save()
			if s.loser == p:
				print "loser"
				other = UserPersonScore.objects.get(pid=s.winner.pid,uid=s.uid)
				other.elorating -= s.l_elo
				other.wins -= 1
				other.numratings -= 1
				
				other.save()
			count += 1
			s.delete()	
		dir = "/Users/Jason/person/" + str(p.pid)
		if 	os.path.exists(dir):
			shutil.rmtree(dir)
		p.delete()
		
	return HttpResponse(count)


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
			
			
			score = 24
	
			e = score - round(1 / (1 + math.pow(10, ((losersc.elorating - winnersc.elorating) / 400))) * score)
	
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
					
			fwinner = {}
			floser = {}
			fwinner['elorating__gt'] = winnersc.elorating
			floser['elorating__gt'] = losersc.elorating
			
			oldwinnerrank = UserPersonScore.objects.filter(**fwinner).count()+1
			oldloserrank = UserPersonScore.objects.filter(**floser).count()+1
			
			
			matchup = PersonMatchup.objects.filter((Q(winner=winner) & Q(loser=loser)) | (Q(loser=winner) & Q(winner=loser)),uid = u)
			if not (matchup.exists()):
								
				calc = calculateRating(winnersc.elorating, losersc.elorating, winnersc.numratings, losersc.numratings)
				
				winnersc.numratings = winnersc.numratings + 1
				
				winnersc.wins = winnersc.wins + 1
				
				winnersc.elorating = winnersc.elorating + calc['winner_change']#win_e
				losersc.numratings = losersc.numratings + 1
				losersc.losses = losersc.losses + 1
				
				losersc.elorating = losersc.elorating - calc['loser_change']#lose_e
				
				matchup = PersonMatchup(winner = winner, loser = loser, uid = u, probabilty = calc['probability'], w_elo=calc['winner_change'], l_elo=calc['loser_change'])
				
				matchup.save()
				#print winnersc.elorating
				#print losersc.elorating
			else:
				m = matchup[0]
				#print m.elo
				#roll back previous
				if (m.winner == winnersc.pid):
					winnersc.elorating = winnersc.elorating-m.w_elo
					losersc.elorating = losersc.elorating+m.l_elo
				else:
					winnersc.elorating = winnersc.elorating+m.l_elo
					losersc.elorating = losersc.elorating-m.w_elo
					winnersc.losses = winnersc.losses - 1
					winnersc.wins = winnersc.wins + 1
					
					losersc.wins = losersc.wins - 1
					losersc.losses = losersc.losses + 1
				
				
				calc = calculateRating(winnersc.elorating, losersc.elorating, winnersc.numratings, losersc.numratings)
								
				winnersc.elorating = winnersc.elorating + calc['winner_change']
				
				losersc.elorating = losersc.elorating - calc['loser_change']
				
				m.delete()
				
				matchup = PersonMatchup(winner = winner, loser = loser, uid = u, probabilty = calc['probability'], w_elo=calc['winner_change'], l_elo=calc['loser_change'])
				matchup.save()
					
			fwinner['elorating__gt'] = winnersc.elorating
			floser['elorating__gt'] = losersc.elorating
			
			newwinnerrank = UserPersonScore.objects.filter(**fwinner).count()+1
			newloserrank = UserPersonScore.objects.filter(**floser).count()+1
			
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


def calculateRating(winner_elo, loser_elo, winner_ratings, loser_ratings):
	
	if winner_ratings < 10:
		win_score = 240
	else:
		win_score = 100
	if loser_ratings < 10:
		lose_score = 240
	else:
		lose_score = 100
	
	
	prob = (1 / (1 + math.pow(10, ((loser_elo - winner_elo) / 400.0)))) 
	
	
	win_e = win_score - round(prob * win_score)
	lose_e = lose_score - round(prob * lose_score)
	
	e = round(prob * 1000) 
	calculation = {}
	calculation['winner_change'] = win_e
	calculation['loser_change'] = lose_e
	calculation['probability'] = e
	return calculation


