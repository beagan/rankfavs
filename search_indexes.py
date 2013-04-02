import datetime
from haystack.indexes import *
from haystack import site
from rankyourfavs.rankfavs.models import Person, Movie, VideoGame, TVshow


class PersonIndex(SearchIndex):
    text = CharField(document=True, use_template=True)
    #name = indexes.CharField(model_attr='name')
	
    def get_model(self):
        return Person

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()


class MovieIndex(SearchIndex):
    text = CharField(document=True, use_template=True)
    #name = indexes.CharField(model_attr='name')
	
    def get_model(self):
        return Movie

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()

class VideoGameIndex(SearchIndex):
    text = CharField(document=True, use_template=True)
    #name = indexes.CharField(model_attr='name')
	
    def get_model(self):
        return VideoGame

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()


class TVshowIndex(SearchIndex):
    text = CharField(document=True, use_template=True)
    #name = indexes.CharField(model_attr='name')
	
    def get_model(self):
        return TVshow

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()



site.register(Person, PersonIndex)
site.register(Movie, MovieIndex)
site.register(VideoGame, VideoGameIndex)
site.register(TVshow, TVshowIndex)