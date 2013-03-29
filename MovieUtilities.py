from imdb import IMDb
#from Netflix import *
import urllib2
import requests
import json
import freebase
import Netflix
import Posters
from rankyourfavs.rankfavs.models import *
from django.db import transaction, connection, IntegrityError
from pyflix2 import *
from difflib import SequenceMatcher
import time
APP_NAME   = ''
API_KEY    = 'smucdewbn2j8rp3rvegmp8y6'
API_SECRET = 'DvstJpTa7f'
CALLBACK   = ''
verbose = False

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



#def getIMDBInfo(id):
	#http://app.imdb.com/title/maindetails?tconst=tt0137523

def getRottenTomatoesMovieInfo(imdb_id):
	imdb_id = str(imdb_id)
	
	if 'tt' in imdb_id:
		imdb_id = str(int(imdb_id.split('tt')[1])).zfill(7)
	else:
		imdb_id = str(int(imdb_id)).zfill(7)
	print imdb_id
	url = "http://api.rottentomatoes.com/api/public/v1.0/movie_alias.json?id=" + imdb_id + "&type=imdb&apikey=u9eem3xqbntrnmkty34kv7hc"
	print url	
	r = requests.get(url)
	
	data = json.loads(r.text)
	return data	


#print getRottenTomatoesMovieInfo("0137523")

def getIMdBMovieInfo(imdb_id):
	imdb_id = str(imdb_id)
	if 'tt' not in imdb_id:
		imdb_id = "tt" + imdb_id.zfill(7)
	else:
		imdb_id = "tt" + imdb_id.split("tt")[1].zfill(7)
	url = "http://app.imdb.com/title/maindetails?tconst=" + imdb_id
	
	print url
	r = requests.get(url)
	data = json.loads(r.text)
	return data


def getMovieDBInfo(imdb_id):
	imdb_id = str(imdb_id)
	if 'tt' not in imdb_id:
		imdb_id = "tt" + imdb_id.zfill(7)
	else:
		imdb_id = "tt" + imdb_id.split("tt")[1].zfill(7)
	url = "http://api.themoviedb.org/3/movie/" + imdb_id + "?api_key=e488bb93f7fe843bac1df144c663f941"
	
	print url
	r = requests.get(url)
	
	data = json.loads(r.text)
	return data


def Netflix2IMDb(netflixClient,id):
	
	ia = IMDb()
	
	movie = netflix(netflixClient,id)
	
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
							return imdbid

def netflix(netflix, id):
	return netflix.catalog.getTitle("http://api.netflix.com/catalog/titles/movies/" + str(id))


def getTitles():
	APP_NAME   = 'rankyourfavs'
	API_KEY    = 'smucdewbn2j8rp3rvegmp8y6'
	API_SECRET = 'DvstJpTa7f'
	CALLBACK   = ''
	verbose = False
	
	netflix = NetflixAPIV2( APP_NAME, API_KEY , API_SECRET)
	
	ia = IMDb()
	
	movies = Movie.objects.all()
	
	count = 0
	
	for movie in movies:
		print movie.imdb_title
		if movie.imdb_title == "":		
			imdb_info = ia.get_movie(movie.imdb_id)
			movie.imdb_title = imdb_info['title']
		if movie.netflix_title == "":
			id = "http://api-public.netflix.com/catalog/titles/movies/" + str(movie.netflix_id)
			try:
				netflix_info = netflix.get_title(id)
				movie.netflix_title = netflix_info['catalog_title']['title']['title_short']
			except:
				time.sleep(10)
		movie.save()
		count +=1

			
			

def IMDb2Netflix(id):
	ia = IMDb()
	if 'tt' in str(id):
		imdb_id = int(id.split("tt")[1])
	else:
		imdb_id = id
	try:
		n = NetflixIMDb.objects.get(imdb_id=imdb_id)
		return n.netflix_id
	except:
		result = freebase.mqlread({ "id": None, "constraint:key": { "namespace": "/authority/imdb/title", "value": str(id) }, 
		  								"key":  [{ "namespace": "/authority/netflix/movie", "value": None }] })
		
		
		if result != None:
			netflix_id = int(result['key'][0]['value'])#.split("tt")[1])
			n = NetflixIMDb(netflix_id=netflix_id,imdb_id=int(id.split("tt")[1]))
			n.save()
			print "thank heavens freebase"
		else:
			print "SHIT"
	#	if False:#else:
			print "doing the horseshit"
		
			APP_NAME   = 'rankyourfavs'
			API_KEY    = 'smucdewbn2j8rp3rvegmp8y6'
			API_SECRET = 'DvstJpTa7f'
			CALLBACK   = ''
			verbose = False
			
			imdb_info = ia.get_movie(imdb_id)
			
			#imdb_info.update()
			
			print imdb_info['title']
			
			imdb_directors = imdb_info['director']
			
			netflix = NetflixAPIV2( APP_NAME, API_KEY , API_SECRET)
			movies = netflix.search_titles(imdb_info['title'], filter='disc')
			#print movies
			
			netflix_directors = []
			person = {}
			
			for movie in movies['catalog']:
				netflix_directors = []
				
				netflix_info = netflix.get_title(movie['id'])
				
				netflix_release_year = netflix_info['catalog_title']['release_year']
				
				try:
					netflix_id = netflix_info['catalog_title']['id'].split('http://api-public.netflix.com/catalog/titles/movies/')[1]
				except:
					netflix_id = 0
					netflix_release_year = 0
				
				#print imdb_info['year']
				#print netflix_release_year
				
				if int(netflix_release_year) == int(imdb_info['year']):
					
					d = netflix.get_title(movie['id'],'directors')
				
					for i in d['directors']:
						person = {}
						#################catch with a try eventually
						try:
							person['id'] = i['id'].split('http://api-public.netflix.com/catalog/people/')[1]
							#################add unescape
							person['name'] = i['name']
							netflix_directors.append(person)
						except:
							print "no name"
					
					
					for netflix_director in netflix_directors:
						for imdb_director in imdb_directors:
							m = SequenceMatcher(None, netflix_director['name'], imdb_director['name'])
							try:
								print "netflix {} imdb {} similar {}".format(netflix_director['name'], imdb_director['name'],m.ratio())
							except:
								print "unicode {}".format(m.ratio())
							#if netflix_director['name'] in imdb_director:
							if m.ratio() > .95:
								print "we have a match"
								try:
									#netflix_id = movie['id'].split('http://api-public.netflix.com/catalog/titles/movies/')[1]
									newmatch = NetflixIMDb(netflix_id = netflix_id, imdb_id = imdb_id)
									newmatch.save()
									return netflix_id
								except:
									print "no id"
	return 0
			
def oldNetflixCode():
	if True:
		if True:
			
			#netflixClient = NetflixClient(APP_NAME, API_KEY, API_SECRET, CALLBACK, verbose)
		
			#list = NetflixCatalog
		
			#movie = netflix(netflixClient,"")
			time.sleep(.20)
			#print movie
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
										#break
										return True
									else:
										print "NOOOOOO MAAAAAATCHHH CHECK MEEEE"
										print "stored: {} matching: {}".format(smart_str(d.name),iname)
					if havematch:
						break
		




def addMovie(id,type):
	connection._rollback()
	if type == "imdb":
		#if not in database search for it
			#if true get netflix_id from database
			#if false break out
		
		have_flix = IMDb2Netflix(id)
		if not have_flix:
			netflix_id = None
		
		#check for netflix
		
		else:
			netflix_id = NetflixIMDb.objects.get(imdb_id=int(id.split("tt")[1])).netflix_id
		
		
		d = getIMdBMovieInfo(id)
		
		d = d['data']
		
		imdb_id = int(id.split("tt")[1])
		try:
			i = Movie.objects.get(imdb_id = imdb_id)
		except:
			i = Movie(imdb_id = imdb_id,netflix_id=netflix_id)
		
	#	i.save()
	#	try:
	#		True
	#	except:
	#		print "couldnt first save"
	#		transaction.rollback()
	#	else:
	#		transaction.commit()
		
		if True:
			if i.imdb_rating == None:
				d = getIMdBMovieInfo(i.imdb_id)
				#print d
				if 'data' in d:
					data = d['data']
					if 'title' in data:
						i.title = data['title']
					if 'year' in data:
						i.year = data['year']
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
			if i.moviedb_id == None:
				d = getMovieDBInfo(i.imdb_id)
				#print d
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
						try:
							i.tags.add(g['name'])
							t = MovieTag.objects.get(name=g['name'])
							t.type = "Genre"
							t.save()
						except:
							print "cant do tags"
			if i.rottentomatoes_id == None:
				d = getRottenTomatoesMovieInfo(i.imdb_id)
				#print d
				if 'id' in d:
					i.rottentomatoes_id = d['id']
				if 'ratings' in d:
					i.rottentomatoes_audience_score = d['ratings']['audience_score']
					i.rottentomatoes_critics_score = d['ratings']['critics_score']
				if 'studio' in d:
					try:
						i.tags.add(d['studio'])
						t = MovieTag.objects.get(name=d['studio'])
						t.type = "Studio"
						t.save()
					except:
						print "cant do tags"
				try:
					i.save()
				except:
					transaction.rollback()
				else:
					transaction.commit()
		
			i.images = Posters.getPosters(imdb_id,1)
		
			try:
				i.save()
			except:
				transaction.rollback()
			else:
				transaction.commit()
		
		
		
			#get info from imdb, title
		
			#save movie
		
			#get extended info from function
		return 

		
		
		
		
		
		