from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

class UserProfile(models.Model):
    # This field is required.
    user = models.OneToOneField(User)
	
    # Other fields here
    uid = models.AutoField(primary_key=True)
	
    global_ratings = models.IntegerField(default=0)
    movie_ratings = models.IntegerField(default=0)
    person_ratings = models.IntegerField(default=0)
    videogame_ratings = models.IntegerField(default=0)


#def create_user_profile(sender, instance, created, **kwargs):
#	if created:
#		UserProfile.objects.create(user=instance)

#	post_save.connect(create_user_profile, sender=User)

class Movie(models.Model):
	mid = models.AutoField(primary_key=True)
	imdb_id = models.IntegerField(unique=True)
	netflix_id = models.IntegerField(unique=True)
	director = models.ManyToManyField('Person',related_name="Director")
	cast = models.ManyToManyField('Person',related_name="Cast")
	#genre = models.ManyToManyField(Genre)
	title = models.CharField(max_length=128)
	year = models.IntegerField()
	images = models.IntegerField(null = True, blank = True)


class UserMovieScore(models.Model):
	mid = models.ForeignKey('Movie')
	uid = models.ForeignKey('UserProfile')
	netflix_rating = models.IntegerField(null=True)
	imdb_rating = models.IntegerField(null=True)
	numratings = models.IntegerField(null=True)
	wins = models.IntegerField(null=True)
	losses = models.IntegerField(null=True)
	elorating = models.IntegerField(null=True)
	seen = models.BooleanField(default=False)
	#notseen = models.BooleanField(default=False)
	listofshame = models.BooleanField(default=False)
	class Meta:
	    unique_together = ('mid', 'uid',)
	


class MovieMatchup(models.Model):
	matchupid = models.AutoField(primary_key=True)
	uid = models.ForeignKey(UserProfile)
	winner = models.ForeignKey('Movie',related_name="winner")
	loser = models.ForeignKey('Movie',related_name="loser")
	elo = models.IntegerField()
	class Meta:
	    unique_together = ('winner', 'loser',)
	



class VideoGame(models.Model):
	vid = models.AutoField(primary_key=True)
	title = models.CharField(max_length=128,unique=True)
	developer = models.CharField(max_length=128,blank=True,null=True)
	publisher = models.CharField(max_length=128,blank=True,null=True)
	year = models.IntegerField(null=True,blank=True)
	release_date = models.DateField(null=True,blank =True,default="1900-1-1")
	esrb_rating = models.CharField(max_length=16)
	
	mobygames_id = models.CharField(max_length=128,null=True,blank=True,unique=True)
	giantbomb_id = models.CharField(max_length=128,null=True,blank=True,unique=True)
	imdb_id = models.IntegerField(null=True,blank=True,unique=True)
	steam_id = models.IntegerField(null=True,blank=True,unique=True)
	wikipedia_link = models.CharField(max_length=256,null = True,blank = True,unique=True)
	
	images = models.IntegerField(default=0)
	

class VideoGamePlatform(models.Model):
	vgpid = models.AutoField(primary_key=True)
	name = models.CharField(max_length=128,unique=True)
	games = models.ManyToManyField('VideoGame',related_name="platforms")
	

class VideoGameMatchup(models.Model):
	matchupid = models.AutoField(primary_key=True)
	uid = models.ForeignKey(UserProfile)
	winner = models.ForeignKey('VideoGame',related_name="winner")
	loser = models.ForeignKey('VideoGame',related_name="loser")
	elo = models.IntegerField()
	class Meta:
	    unique_together = ('winner', 'loser',)


class UserVideoGameScore(models.Model):
	vid = models.ForeignKey('VideoGame')
	uid = models.ForeignKey('UserProfile')
	numratings = models.IntegerField(default=0)
	wins = models.IntegerField(default=0)
	losses = models.IntegerField(default=0)
	elorating = models.IntegerField(default=1000)
	neveruse = models.BooleanField(default=False)
	played = models.BooleanField(default=False)
	
	
	rank = models.IntegerField(default=10000)
	class Meta:
	    unique_together = ('vid', 'uid',)


class PersonCategory(models.Model):
	gid = models.AutoField(primary_key=True)
	category = models.CharField(max_length=28)
	members = models.ManyToManyField('Person',related_name="cats")
	def __unicode__(self):
		return self.category

class PersonList(models.Model):
	lid = models.AutoField(primary_key=True)
	list = models.CharField(max_length=128)
	members = models.ManyToManyField('Person',related_name="plist")


class Person(models.Model):
	pid = models.AutoField(primary_key=True)
	netflix_id = models.IntegerField(null = True, blank = True,unique=True)
	imdb_id = models.IntegerField(null = True, blank = True,unique=True)
	tvrage_id = models.IntegerField(null = True, blank = True,unique=True)
	chickipedia_id = models.CharField(max_length=128,null = True,blank = True,unique=True)
	twitter = models.CharField(max_length=128,null=True,blank=True,unique=True)
	
	gender = models.CharField(max_length=10,blank=True)
	dob = models.DateField(null=True,blank =True,default="1900-1-1")
	nationality = models.CharField(max_length=128)
	
	sid = models.ForeignKey('SportsPerson',blank=True,null=True)
	
	wikipedia_link = models.CharField(max_length=256,null = True,blank = True,unique=True)
	
	image_edit = models.BooleanField(default=False)
	
	name = models.CharField(max_length=128)
	maiden_name = models.CharField(max_length=128,blank=True,null=True)
	
	images = models.IntegerField(null = True, blank = True)
	def __unicode__(self):
		return self.name
	


class TemporaryPerson(models.Model):
	temp_id = models.AutoField(primary_key=True)
	
	name = models.CharField(max_length=128)
	maiden_name = models.CharField(max_length=128,blank=True,null=True)
	
	gender = models.CharField(max_length=10,blank=True)
	
	tvrage_id = models.IntegerField(null = True, blank = True,unique=True)
	chickipedia_id = models.CharField(max_length=128,null = True,blank = True,unique=True)
	
	dob = models.DateField(null=True,blank =True,default="1900-1-1")
	nationality = models.CharField(max_length=128)
	
	imdb_id = models.IntegerField(null = True, blank = True,unique=True)
	wikipedia_link = models.CharField(max_length=256,null = True,blank = True,unique=True)
	twitter = models.CharField(max_length=128,null = True,blank = True,unique=True)
	
	images = models.IntegerField(null = True, blank = True, default = 0)
	


class SportsPerson(models.Model):
	sid = models.AutoField(primary_key=True)
	team = models.CharField(max_length=64,blank=True)
	
	almanac_id = models.CharField(max_length=32,blank=True,unique=True)
	sportsdb_id = models.CharField(max_length=32,blank=True)
	
	yearsactive = models.IntegerField(blank=True)
	
	active = models.BooleanField(default=False)
	halloffame = models.BooleanField(default=False)
	

class PersonMatchup(models.Model):
	matchupid = models.AutoField(primary_key=True)
	uid = models.ForeignKey(UserProfile)
	winner = models.ForeignKey('Person',related_name="winner")
	loser = models.ForeignKey('Person',related_name="loser")
	
	probabilty = models.IntegerField(default=0)
	w_elo = models.IntegerField(default=0)
	l_elo = models.IntegerField(default=0)
	#winnerrankchange = models.IntegerField()
	#loserrankchange = models.IntegerField()
	class Meta:
	    unique_together = ('winner', 'loser', 'uid',)


class UserPersonScore(models.Model):
	pid = models.ForeignKey('Person')
	uid = models.ForeignKey('UserProfile')
	numratings = models.IntegerField(default=0)
	wins = models.IntegerField(default=0)
	losses = models.IntegerField(default=0)
	elorating = models.IntegerField(default=1000)
	neveruse = models.BooleanField(default=False)
	rank = models.IntegerField(default=10000)
	genderrank = models.IntegerField(default=10000)
	class Meta:
	    unique_together = ('pid', 'uid',)


class TVshow(models.Model):
	tid = models.AutoField(primary_key=True)
	imdb_id = models.IntegerField(unique=True)
	netflix_id = models.IntegerField(unique=True,blank=True,null=True)
	tvdb_id = models.IntegerField(unique=True)
	zap2it_id = models.CharField(unique=True,null=True,blank=True,max_length=24,default="0")
	cast = models.ManyToManyField('Person',related_name="TVCast")
	title = models.CharField(max_length=128)
	first_aired = models.DateField(null=True,blank =True,default="1900-1-1")
	images = models.IntegerField(null = True, blank = True)
	


class TVShowMatchup(models.Model):
	matchupid = models.AutoField(primary_key=True)
	uid = models.ForeignKey(UserProfile)
	winner = models.ForeignKey('TVShow',related_name="winner")
	loser = models.ForeignKey('TVShow',related_name="loser")
	elo = models.IntegerField()
	class Meta:
	    unique_together = ('winner', 'loser','uid',)


class UserTVShowScore(models.Model):
	tid = models.ForeignKey('TVShow')
	uid = models.ForeignKey('UserProfile')
	numratings = models.IntegerField(default=0)
	wins = models.IntegerField(default=0)
	losses = models.IntegerField(default=0)
	elorating = models.IntegerField(default=1000)
	watched = models.BooleanField(default=True)
#	played = models.BooleanField(default=False)
	
	
	rank = models.IntegerField(default=10000)
	class Meta:
	    unique_together = ('tid', 'uid',)



class NetflixIMDb(models.Model):
	netflix_id = models.IntegerField(primary_key=True)
	imdb_id = models.IntegerField()


