from imdb import IMDb
from Netflix import *

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