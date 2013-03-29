#
# Library for accessing the REST API from Netflix
# Represents each resource in an object-oriented way
#

import sys
import os.path
import re
import oauth.oauth as oauth
import httplib
import time
from xml.dom.minidom import parseString
import simplejson
from urlparse import urlparse

HOST              = 'api-public.netflix.com.com'
PORT              = '80'
REQUEST_TOKEN_URL = 'http://api-public.netflix.com/oauth/request_token'
ACCESS_TOKEN_URL  = 'http://api-public.netflix.com/oauth/access_token'
AUTHORIZATION_URL = 'https://api-user.netflix.com/oauth/login'

		
class NetflixError(Exception):
    pass


class FieldError(NetflixError):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)


class NetflixCatalog():

    def __init__(self,client):
        self.client = client
    
    def searchTitles(self, term,startIndex=None,maxResults=None):
        requestUrl = '/catalog/titles/dvd'
        parameters = {'term': term}
        if startIndex:
            parameters['start_index'] = startIndex
        if maxResults:
            parameters['max_results'] = maxResults
        info = simplejson.loads( self.client._getResource( 
                                    requestUrl,
                                    parameters=parameters))

        return info['catalog_titles']['catalog_title']

    def searchStringTitles(self, term,startIndex=None,maxResults=None):
        requestUrl = '/catalog/titles/autocomplete'
        parameters = {'term': term}
        if startIndex:
            parameters['start_index'] = startIndex
        if maxResults:
            parameters['max_results'] = maxResults

        info = simplejson.loads( self.client._getResource( 
                                    requestUrl,
                                    parameters=parameters))
        print simplejson.dumps(info)
        return info['autocomplete']['autocomplete_item']
    
    def getTitle(self, url):
        requestUrl = url
        parameters = {}
        parameters['expand'] = 'cast,directors'
        data = self.client._getResource( requestUrl,None,parameters)
        #print data
        info = simplejson.loads( data )
        return info

    def searchPeople(self, term,startIndex=None,maxResults=None):
        requestUrl = '/catalog/people'
        parameters = {'term': term}
        if startIndex:
            parameters['start_index'] = startIndex
        if maxResults:
            parameters['max_results'] = maxResults

        try:
            info = simplejson.loads( self.client._getResource( 
                                    requestUrl,
                                    parameters=parameters))
        except:
            return []

        return info['people']['person']

    def getPerson(self,url):
        requestUrl = url
        try:
            info = simplejson.loads( self.client._getResource( requestUrl ))
        except:
            return {}
        return info


 


class NetflixDisc:

    def __init__(self,discInfo,client):
        self.info = discInfo
        self.client = client
    
    def getInfo(self,field):
        fields = []
        url = ''
        for link in self.info['link']:
            fields.append(link['title'])
            if link['title'] == field:
                url = link['href']
        if not url:
            errorString =          "Invalid or missing field.  " + \
                                    "Acceptable fields for this object are:" + \
                                    "\n\n".join(fields)
            raise FieldError(errorString)
        try:
            info = simplejson.loads(self.client._getResource( url ))
        except:
            return []
        else:
            return info
 
           
class NetflixClient:

    def __init__(self, name, key, secret, callback='',verbose=False):
        self.connection = httplib.HTTPConnection("%s:%s" % (HOST, PORT))
        self.server = HOST
        self.verbose = verbose
        self.user = None
        self.catalog = NetflixCatalog(self)
        
        self.CONSUMER_NAME=name
        self.CONSUMER_KEY=key
        self.CONSUMER_SECRET=secret
        self.CONSUMER_CALLBACK=callback
        self.consumer = oauth.OAuthConsumer(
                                    self.CONSUMER_KEY,
                                    self.CONSUMER_SECRET)
        self.signature_method_hmac_sha1 = \
                                    oauth.OAuthSignatureMethod_HMAC_SHA1()
    
    def _getResource(self, url, token=None, parameters={}):
        if not re.match('http',url):
            url = "http://%s%s" % (HOST, url)
        parameters['output'] = 'json'
        
        oauthRequest = oauth.OAuthRequest.from_consumer_and_token(
                                    self.consumer,
                                    http_url=url,
                                    parameters=parameters,
                                    token=token)
        oauthRequest.sign_request(  
                                    self.signature_method_hmac_sha1,
                                    self.consumer,
                                    token)
        if (self.verbose):
            print oauthRequest.to_url()
        self.connection.request('GET', oauthRequest.to_url())
        response = self.connection.getresponse()
        return response.read()
    
    def _postResource(self, url, token=None, parameters=None):
        if not re.match('http',url):
            url = "http://%s%s" % (HOST, url)
        
        oauthRequest = oauth.OAuthRequest.from_consumer_and_token(  
                                    self.consumer,
                                    http_url=url,
                                    parameters=parameters,
                                    token=token,
                                    http_method='POST')
        oauthRequest.sign_request(
                                    self.signature_method_hmac_sha1, 
                                    self.consumer, 
                                    token)
        
        if (self.verbose):
            print "POSTING TO" + oauthRequest.to_url()
        
        headers = {'Content-Type':'application/x-www-form-urlencoded'}
        self.connection.request('POST', url, 
                                    body=oauthRequest.to_postdata(), 
                                    headers=headers)
        response = self.connection.getresponse()
        return response.read()
        
    def _deleteResource(self, url, token=None, parameters=None):
        if not re.match('http',url):
            url = "http://%s%s" % (HOST, url)
        
        oauthRequest = oauth.OAuthRequest.from_consumer_and_token(  
                                    self.consumer,
                                    http_url=url,
                                    parameters=parameters,
                                    token=token,
                                    http_method='DELETE')
        oauthRequest.sign_request(
                                    self.signature_method_hmac_sha1, 
                                    self.consumer, 
                                    token)

        if (self.verbose):
            print "DELETING FROM" + oauthRequest.to_url()

        self.connection.request('DELETE', oauthRequest.to_url())
        response = self.connection.getresponse()
        return response.read()
