import MySQLdb
import sqlite3
import httplib2
import time
import os.path
import teams
endgame = 180
import statTools as stat
maxgamegl = 180
from lxml import html
from lxml.etree import tostring
import urllib, urllib2
import gzip
import operator

import threading
import multiprocessing

def getNameFromESPNID(id):
	file = "/Users/Jason/bbcdata/player/" + str(id)
	if not (os.path.isfile(file)):
		s = "http://m.espn.go.com/mlb/playercard?playerId=" + str(id) + "&wjb"
		
		request = urllib2.Request(s)
		request.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1')
		
		sock = urllib2.urlopen(s)
		opener = urllib2.build_opener()
		source = open(file,"wb")
		source.writelines(opener.open(request).read())
		source.close()
	infile = open(file,"r")
	htmlsource = infile.read()
	title = htmlsource.split("<div class=\"sub bold\">")[1].split("<")[0].split(" ")
	i={}
	i['num'] = title[0]
	i['FN'] = title[1]
	i['LN'] = title[2]
	if len(title)>3:
		i['suffix'] = title[3]
	else:
		i['suffix'] = None
	return i


def parserSQL(id,c,h):
	t1 = time.time()
	#print id
	for day in range (120,maxgamegl):
		file = "/Users/Jason/bbcdata/entry/" + str(id) + "/" + "spid=" + str(day) + ".html.gz"
		if (day == 10000):
			c.execute('''create table if not exists player
			  (id integer primary key, day integer, pos text, fn text , ln text , espnid text , bbcid integer , teamid integer , salary numeric , location text , ab integer , bb integer , r integer , rbi integer , sb integer , tb integer , dh integer , oppteamid integer , nogame text, gameresult1 text, gameresult2 text)''')
			c.execute('''create table if not exists entry
			  (id integer primary key, userid integer, day integer, rosterset text, catcher integer, catchersalary text, firstbase integer, firstbasesalary text, secondbase integer, secondbasesalary text, thirdbase integer, thirdbasesalary text, shortstop integer, shortstopsalary text, leftfield integer, leftfieldsalary text, centerfield integer, centerfieldsalary text, rightfield integer, rightfieldsalary text, dh integer, dhsalary text, ps integer, pssalary)''')
			c.execute('''create table if not exists ps
			  (id integer primary key, day integer, p1fn text , p1ln text , p1suff text, p2fn text, p2ln text, p2suff text, espnid text , espnid2 text, teamid integer , salary numeric , location text , ip text, h text, er text, bb text, k text, w text, dh integer , oppteamid integer , nogame text, gameresult1 text, gameresult2 text)''')
		key = int(id) * 1000000 + day
		c.execute("SELECT * FROM entry WHERE id = ?", (key,))
		data = c.fetchone()
		#print day
		#print data
		if data == None:
			#print "data none"
			file = "/Users/Jason/bbcdata/entry/" + str(id) + "/" + "spid=" + str(day) + ".html.gz"
			#print file
			#path = "/Users/Jason/bbcdata/entry/" + str(id) + "/"
			#if not os.path.exists(path): os.makedirs(path)
			content = None
			if not (os.path.isfile(file)):
				print "need to dl " + str(file)
				s = "http://games.espn.go.com/baseball-challenge/en/format/ajax/getBoxscoreSnapshot?entryID=" + str(id) + "&spid=" + str(day)
				headers = {
				'Accept': 'text/html, */*',
				'Accept-Language': 'en-us,en;q=0.5',
				'Accept-Encoding':	'gzip, deflate',
				'Connection':	'Keep-Alive',
				}
				#request = urllib2.Request(s,{},headers)
				#response = urllib2.urlopen(request)
				response, content = h.request(s,headers=headers)
				#print content
				#if response.info().get('Content-Encoding') == 'gzip':
				#output = gzip.open(file, 'wb')
				#output.write(content)
				#output.close()
			#t3 = time.time()
			if content == None:		
				infile = open(file,"r")
				gzipper = gzip.GzipFile(fileobj=infile)
				htmlsource = gzipper.read()
			else:
				htmlsource = content
			if htmlsource == "No set roster for entry<input type=hidden id=\"setInterval\" value=\"0\">" or htmlsource == '':
				c.execute("insert into entry values\
				           (?,?,?,?,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL)", (key,id,day,"False"))
			else:
				#print id
				#print day
				root = html.fromstring(htmlsource)
				data = root.cssselect('tbody')
				pl = data[0].cssselect('tr')	
				t4 = time.time()
				#print t4 - t3
				player = [{},{},{},{},{},{},{},{},{},{}]
				stat={5:"AB",6:"R",7:"TB",8:"RBI",9:"BB",10:"SB"}
				i = 0
				for s in pl:
					l1 = s.cssselect("td")
					player[i]['pos'] = l1[0].text
					l12 = tostring(l1[2])
					player[i]['FN'] = l12.split('pFN\">')[1].split('<')[0]
					player[i]['LN'] = l12.split('pLN\">')[1].split('<')[0]
					player[i]['id'] = l12.split('player_id=\"')[1].split('\"')[0]
					gr = tostring(l1[4]).split('\">')
					if len(gr)>2:
						if len(gr)>5:
							player[i]['gameresult1'] = gr[3].split("</a>")[0]
							player[i]['gameresult2'] = gr[len(gr)-1].split("</a>")[0]
						else:
							player[i]['gameresult1'] = gr[len(gr)-1].split("</a>")[0]
							player[i]['gameresult2'] = "--"
					else:
						player[i]['gameresult1'] = gr[1].split('</td>')[0]
						player[i]['gameresult2'] = "--"
					player[i]['espnid'] = l12.split('player_eid=\"')[1].split('\"')[0]
					player[i]['teamid'] = l12.split('tid=\"')[1].split('\"')[0]
					player[i]['salary'] = tostring(l1[12]).strip('<>td  = clasnobr///"')
					player[i]['dh'] = False
					if(l1[3].text != "--"):
						player[i]['nogame'] = False
						player[i]['oppteamid'] = tostring(l1[3]).split('teamId=')[1].split('\"')[0]
						if l1[5].text == None:
							player[i]['dh'] = True
							for j in range(5,11):
								s1 = l1[j].cssselect('span')[0]
								s2 = l1[j].cssselect('span')[1]
								player[i][stat[j]] = int(s1.text)+int(s2.text)
						else:
							for j in range(5,11):
								player[i][stat[j]] = l1[j].text
					else:
						player[i]['nogame'] = True
						player[i]['oppteamid'] = "NULL"
						for j in range(5,11):
							player[i][stat[j]] = 0
					if "@" in str(l1[3]):
						player[i]['loc'] = "Away"
					else:
						player[i]['loc'] = "Home"
					l=0
					i+=1
				p = data[1].cssselect("td")
				player[9]['pos'] = "PS"
				p2 = tostring(p[2])
				player[9]['id'] = 0
				player[9]['id2'] = 0
				player[9]['teamid'] = p2.split('tid=\"')[1].split('\"')[0]
				player[9]['dh'] = False
				gr = tostring(l1[4]).split('\">')
				if len(gr)>2:
					if len(gr)>5:
						player[9]['gameresult1'] = gr[3].split("</a>")[0]
						player[9]['gameresult2'] = gr[len(gr)-1].split("</a>")[0]
					else:
						player[9]['gameresult1'] = gr[len(gr)-1].split("</a>")[0]
						player[i]['gameresult2'] = "None"
				else:
					player[9]['gameresult1'] = gr[1].split('</td>')[0]
					player[9]['gameresult2'] = "None"
				statps={5:"IP",6:"H",7:"ER",8:"BB",9:"K",10:"W"}
				if p[3].text != "--":
					player[9]['nogame'] = False
					if "\"roster-plyr\"" in p2:
						player[9]['id'] = p2.split('playerId=')[1].split('\"')[0]
						arr = getNameFromESPNID(player[9]['id'])
						player[9]['p1FN'] = arr['FN']
						player[9]['p1LN'] = arr['LN']
						player[9]['p1SUF'] = arr['suffix']
					else:
						player[9]['p1FN'] = "None"
						player[9]['p1LN'] = "None"
						player[9]['p1SUF'] = "None"
					player[9]['oppteamid'] = tostring(p[3]).split('teamId=')[1].split('\"')[0]
					if p[5].text == None:
						if len(p2.split('playerId='))>2:
							player[9]['id2'] = p2.split('playerId=')[2].split('\"')[0]	
							arr = getNameFromESPNID(player[9]['id2'])
							player[9]['p2FN'] = arr['FN']
							player[9]['p2LN'] = arr['LN']
							player[9]['p2SUF'] = arr['suffix']
						else:
							player[9]['id2'] = 0
							player[9]['p2FN'] = ""
							player[9]['p2LN'] = ""
							player[9]['p2SUF'] = ""
						player[9]['dh'] = True
						s1 = p[5].cssselect('span')[0]
						s2 = p[5].cssselect('span')[1]
						player[9][statps[5]] = stat.addIP(s1.text,s2.text)
						for j in range(6,11):
							s1 = p[j].cssselect('span')[0]
							s2 = p[j].cssselect('span')[1]
							player[9][statps[j]] = int(s1.text)+ int(s2.text)					
					else:
						player[9]['p2FN'] = "None"
						player[9]['p2LN'] = "None"
						player[9]['p2SUF'] = "None"
						for j in range(5,11):
							player[9][statps[j]] = p[j].text
					if "@" in str(l1[3]):
						player[9]['loc'] = "Away"
					else:
						player[9]['loc'] = "Home"
				else:
					player[9]['p1FN'] = "None"
					player[9]['p1LN'] = "None"
					player[9]['p1SUF'] = "None"
					player[9]['p2FN'] = "None"
					player[9]['p2LN'] = "None"
					player[9]['p2SUF'] = "None"
					player[9]['loc'] = "None"
					player[9]['oppteamid'] = "None"
					player[9]['nogame'] = True
					for j in range(5,11):
						player[9][statps[j]] = 0
				player[9]['salary'] = tostring(p[12]).strip('<>td  = clasnobr///"')
				t2 = time.time()
				#print str(t2 - t1) + " day " + str(day)
				#print player[9]
				key = id *1000000 + day
				
				c.execute("insert into entry values\
					(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (key,id,day,"True",player[0]['espnid'],player[0]['salary'],player[1]['espnid'],player[1]['salary'],player[2]['espnid'],player[2]['salary'],player[3]['espnid'],player[3]['salary'],player[4]['espnid'],player[4]['salary'],player[5]['espnid'],player[5]['salary'],player[6]['espnid'],player[6]['salary'],player[7]['espnid'],player[7]['salary'],player[8]['espnid'],player[8]['salary'],player[9]['teamid'],player[9]['salary']))
				#c.execute("SELECT * FROM entry WHERE id = ?", (key,))
				#data = c.fetchone()
				#print day
				#print data
				
				for i in range(0,9):
					key = int(player[i]['espnid']) * 1000000 + day
					c.execute("SELECT * FROM player WHERE id = ?", (key,))
					data = c.fetchone()
					if data == None:
						c.execute("insert into player values\
				           	(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (key,day,player[i]['pos'],player[i]['FN'],player[i]['LN'],player[i]['espnid'],player[i]['id'],player[i]['teamid'],player[i]['salary'],player[i]['loc'],player[i]['AB'],player[i]['BB'],player[i]['R'],player[i]['RBI'],player[i]['SB'],player[i]['TB'],player[i]['dh'],player[i]['oppteamid'],player[i]['nogame'],player[i]['gameresult1'],player[i]['gameresult2']))
				key = int(player[9]['teamid']) * 1000000 + day
				c.execute("SELECT * FROM ps WHERE id = ?", (key,))
				data = c.fetchone()
				if data == None:
					#print "inserting new pitcher"
					c.execute("insert into ps values\
				           (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (key,day,player[9]['p1FN'],player[9]['p1LN'],player[9]['p1SUF'],player[9]['p2FN'],player[9]['p2LN'],player[9]['p2SUF'],player[9]['id'],player[9]['id2'],player[9]['teamid'],player[9]['salary'],player[9]['loc'],player[9]['IP'],player[9]['H'],player[9]['ER'],player[9]['BB'],player[9]['K'],player[9]['W'],player[9]['dh'],player[9]['oppteamid'],player[9]['nogame'],player[9]['gameresult1'],player[9]['gameresult2']))
				
				try:
					os.remove(file)
					#print "removed {0}".format(file)
				except:
					print "not there"
	#c.execute("SELECT * FROM catcher")
	#data=c.fetchall()
	#print data
	t2 = time.time()
	#print t2-t1



def parserSQLv2(id,day,c,h):
	t1 = time.time()
	#print id
	
	file = "/Users/Jason/bbcdata/entry/" + str(id) + "/" + "spid=" + str(day) + ".html.gz"
	s = "http://games.espn.go.com/baseball-challenge/en/format/ajax/getBoxscoreSnapshot?entryID=" + str(id) + "&spid=" + str(day)
	headers = {
		'Accept': 'text/html, */*',
		'Accept-Language': 'en-us,en;q=0.5',
		'Accept-Encoding':	'gzip, deflate',
		'Connection':	'Keep-Alive',
	}
	response, content = h.request(s,headers=headers)
	htmlsource = content
	if htmlsource == "No set roster for entry<input type=hidden id=\"setInterval\" value=\"0\">" or htmlsource == '':
		return 0
	else:
		root = html.fromstring(htmlsource)
		data = root.cssselect('tbody')
		pl = data[0].cssselect('tr')	
		t4 = time.time()
		player = [{},{},{},{},{},{},{},{},{},{}]
		statli={5:"AB",6:"R",7:"TB",8:"RBI",9:"BB",10:"SB"}
		i = 0
		for s in pl:
			l1 = s.cssselect("td")
			player[i]['pos'] = l1[0].text
			l12 = tostring(l1[2])
			player[i]['FN'] = l12.split('pFN\">')[1].split('<')[0]
			player[i]['LN'] = l12.split('pLN\">')[1].split('<')[0]
			player[i]['id'] = l12.split('player_id=\"')[1].split('\"')[0]
			gr = tostring(l1[4]).split('\">')
			if len(gr)>2:
				if len(gr)>5:
					player[i]['gameresult1'] = gr[3].split("</a>")[0]
					player[i]['gameresult2'] = gr[len(gr)-1].split("</a>")[0]
				else:
					player[i]['gameresult1'] = gr[len(gr)-1].split("</a>")[0]
					player[i]['gameresult2'] = "--"
			else:
				player[i]['gameresult1'] = gr[1].split('</td>')[0]
				player[i]['gameresult2'] = "--"
			player[i]['espnid'] = l12.split('player_eid=\"')[1].split('\"')[0]
			player[i]['teamid'] = l12.split('tid=\"')[1].split('\"')[0]
			player[i]['salary'] = tostring(l1[12]).strip('<>td  = clasnobr///"')
			player[i]['dh'] = 0
			if(l1[3].text != "--"):
				player[i]['nogame'] = 0
				player[i]['oppteamid'] = tostring(l1[3]).split('teamId=')[1].split('\"')[0]
				if l1[5].text == None:
					player[i]['dh'] = 1
					for j in range(5,11):
						s1 = l1[j].cssselect('span')[0]
						s2 = l1[j].cssselect('span')[1]
						player[i][statli[j]] = int(s1.text)+int(s2.text)
				else:
					for j in range(5,11):
						player[i][statli[j]] = l1[j].text
			else:
				player[i]['nogame'] = 1
				player[i]['oppteamid'] = "NULL"
				for j in range(5,11):
					player[i][statli[j]] = 0
			if "@" in str(l1[3]):
				player[i]['loc'] = "Away"
			else:
				player[i]['loc'] = "Home"
			l=0
			i+=1
		p = data[1].cssselect("td")
		player[9]['pos'] = "PS"
		p2 = tostring(p[2])
		player[9]['id'] = 0
		player[9]['id2'] = 0
		player[9]['teamid'] = p2.split('tid=\"')[1].split('\"')[0]
		player[9]['dh'] = False
		gr = tostring(l1[4]).split('\">')
		if len(gr)>2:
			if len(gr)>5:
				player[9]['gameresult1'] = gr[3].split("</a>")[0]
				player[9]['gameresult2'] = gr[len(gr)-1].split("</a>")[0]
			else:
				player[9]['gameresult1'] = gr[len(gr)-1].split("</a>")[0]
				player[i]['gameresult2'] = "None"
		else:
			player[9]['gameresult1'] = gr[1].split('</td>')[0]
			player[9]['gameresult2'] = "None"
		statps={5:"IP",6:"H",7:"ER",8:"BB",9:"K",10:"W"}
		if p[3].text != "--":
			player[9]['nogame'] = 0
			if "\"roster-plyr\"" in p2:
				player[9]['id'] = p2.split('playerId=')[1].split('\"')[0]
				arr = getNameFromESPNID(player[9]['id'])
				player[9]['p1FN'] = arr['FN']
				player[9]['p1LN'] = arr['LN']
				player[9]['p1SUF'] = arr['suffix']
			else:
				player[9]['p1FN'] = "None"
				player[9]['p1LN'] = "None"
				player[9]['p1SUF'] = "None"
			player[9]['oppteamid'] = tostring(p[3]).split('teamId=')[1].split('\"')[0]
			if p[5].text == None:
				if len(p2.split('playerId='))>2:
					player[9]['id2'] = p2.split('playerId=')[2].split('\"')[0]	
					arr = getNameFromESPNID(player[9]['id2'])
					player[9]['p2FN'] = arr['FN']
					player[9]['p2LN'] = arr['LN']
					player[9]['p2SUF'] = arr['suffix']
				else:
					player[9]['id2'] = 0
					player[9]['p2FN'] = ""
					player[9]['p2LN'] = ""
					player[9]['p2SUF'] = ""
				player[9]['dh'] = 1
				s1 = p[5].cssselect('span')[0]
				s2 = p[5].cssselect('span')[1]
				player[9][statps[5]] = stat.addIP(s1.text,s2.text)
				for j in range(6,11):
					s1 = p[j].cssselect('span')[0]
					s2 = p[j].cssselect('span')[1]
					player[9][statps[j]] = int(s1.text)+ int(s2.text)					
			else:
				player[9]['p2FN'] = "None"
				player[9]['p2LN'] = "None"
				player[9]['p2SUF'] = "None"
				for j in range(5,11):
					player[9][statps[j]] = p[j].text
			if "@" in str(l1[3]):
				player[9]['loc'] = "Away"
			else:
				player[9]['loc'] = "Home"
		else:
			player[9]['p1FN'] = "None"
			player[9]['p1LN'] = "None"
			player[9]['p1SUF'] = "None"
			player[9]['p2FN'] = "None"
			player[9]['p2LN'] = "None"
			player[9]['p2SUF'] = "None"
			player[9]['loc'] = "None"
			player[9]['oppteamid'] = "None"
			player[9]['nogame'] = 1
			for j in range(5,11):
				player[9][statps[j]] = 0
		player[9]['salary'] = tostring(p[12]).strip('<>td  = clasnobr///"')
		t2 = time.time()
		
		return player
			
	#c.execute("SELECT * FROM catcher")
	#data=c.fetchall()
	#print data
	t2 = time.time()
	#print t2-t1




def getUserName(id,h):
	s = "http://games.espn.go.com/baseball-challenge/en/entry?entryID=" + str(id)
	file = "/Users/Jason/bbcdata/usernames/" + str(id) + ".txt"
	path = "/Users/Jason/bbcdata/usernames/"
	#if not os.path.exists(path): os.makedirs(path)
	if not (os.path.isfile(file)):
		s = "http://games.espn.go.com/baseball-challenge/en/entry?entryID=" + str(id)
		headers = {
		'Accept': 'text/html, */*',
		'Accept-Language': 'en-us,en;q=0.5',
		'Accept-Encoding':	'gzip, deflate',
		'Connection':	'Keep-Alive',
		}
		response, content = h.request(s,headers=headers)
		source = open(file,"w")
		
		ss = content.split("<h1 style=\"display:inline;\">")[1].split("</h1>")[0]
		print "id = " + str(id) + " " + str(ss)
		source.write(ss)
		source.close()
	infile = open(file,"r")
	return infile.read()



def daySQLLoopv2(id,c,conn,h,connmy,cmy):
	tt = time.time()
	tsqlite = 0
	tplayers = 0
	tpitchers = 0
	tentry = 0
	tmany = 0
	tplayersql = 0
	tnoplayer = 0
	utpts = 0
	
	cmy.execute("SELECT * FROM bbc_user WHERE espnid = %s",id)
	user = cmy.fetchone()
	
	if user == None:
		espnid = id
		name = getUserName(espnid,h)
		values = (name,espnid,0,1)
		query = """INSERT INTO bbc_user (name,espnid,totalpoints,maxgame)
		    		VALUES (%s, %s, %s, %s )"""
		cmy.execute(query,values)
		cmy.execute("SELECT * FROM bbc_user WHERE espnid = %s",id)
		user = cmy.fetchone()
		connmy.commit()
		#print user
		maxgame = 1
		uid = user[0]
		utpts = 0
	else:
		#utpts = user[3]
		maxgame = user[4]
		uid = user[0]
		
	for day in range(maxgame,endgame):
		
		if day != 104 and day != 105:
			totalabs=0;totaltbs=0;totalrbis=0;totalbbs=0;totalbbs=0;totalsbs=0;totalruns=0;tpts=0
			runwin=0;runtie=0;runloss=0;rbiwin=0;rbitie=0;rbiloss=0;
			
			players = []
			playerssal = []
			pitcher = 0
			tday1 = time.time()
			key = int(id) * 1000000 + day
			ts = time.time()
			
			d = parserSQLv2(int(id),day,c,h)
				#conn.commit()
			
			tsf = time.time()
			tsqlite += (tsf-ts)
			
			
			if d == 0:
				x=1
				#print "NONE {0}".format(day)
			else:
				tpl = time.time()
				for i in range(0,9):
					#print d[i]['espnid']
					tpts = 0
					abs = int(d[i]['AB'])
					tbs = int(d[i]['TB'])
					runs = int(d[i]['R'])
					rbis = int(d[i]['RBI'])
					bbs = int(d[i]['BB'])
					sbs = int(d[i]['SB'])
					
					
					pts = stat.calculatePlayerPTs(bbs,sbs,rbis,runs)
					
					totalabs += abs
					totaltbs += tbs
					totalruns += runs
					totalrbis += rbis
					totalbbs += bbs
					totalsbs += sbs
					tpts += pts
					
					name = d[i]['FN'] + " " + d[i]['LN']
					
					double = d[i]['dh']
					nogame = d[i]['nogame']
						
					pid = int(d[i]['id']) * 10000 + day
					
					players.append(pid)
					playerssal.append(d[i]['salary'])
					
					espnid=d[i]['espnid'];game = int(day);pos=d[i]['pos'];bbcid=d[i]['id'];doubleheader=double;
					teamid=d[i]['teamid']
					teamname=teams.team[int(teamid)]
					
							#query = "INSERT DELAYED IGNORE INTO bbc_playerentry (pid,espnid,gamenumber,pos,bbcid,doubleheader,nogame,abs,runs,tbs,rbis,bbs,sbs,pts,teamid,teamname,name)
							#    		VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s )"
							
							#values = (pid,espnid,int(day),pos,bbcid,doubleheader,nogame,abs,runs,tbs,rbis,bbs,sbs,pts,teamid,teamname,name)
							#cmy.execute(query,values)
							
				p1salary=playerssal[0];p2salary=playerssal[1];p3salary=playerssal[2]
				p4salary=playerssal[3];p5salary=playerssal[4];p6salary=playerssal[5]
				p7salary=playerssal[6];p8salary=playerssal[7];p9salary=playerssal[8]
				pssalary=d[9]['salary']
				#print players
				p1 = players[0];p2 = players[1];p3 = players[2];
				p4 = players[3];p5 = players[4];p6 = players[5];
				p7 = players[6];p8 = players[7];p9 = players[8]
				
				tplf = time.time()
				tplayers += tplf-tpl
				
				#key = e[22] * 1000000 + day
				
				ts =  time.time()
				#c.execute("SELECT * FROM ps WHERE id = ?", (key,))
				#ps = c.fetchone()
				tsf = time.time()
				#tsqlite += tsf-ts
				
				statps={5:"IP",6:"H",7:"ER",8:"BB",9:"K",10:"W"}
				
				phits = int(d[9]['H'])
				pbbs = int(d[9]['BB'])
				ers = int(d[9]['ER'])
				ks = int(d[9]['K'])
				ws = int(d[9]['W'])
				ip = float(d[9]['IP'])
				ipouts = stat.ipToOuts(ip)
				
				espnid = int(d[9]['id'])
				espnid2 = int(d[9]['id2'])
				doubleheader = int(d[9]['dh'])
				gamenumber= int(day)
				nogame = int(d[9]['nogame'])
				teamid = int(d[9]['teamid'])
				teamname = teams.team[teamid]

				
				pts = ipouts-phits-3*ers-pbbs+ks+5*ws
				tpts += pts
				
				pid = int(d[9]['id']) * 10000 + day
				pname = ""
				if d[9]['p1SUF'] != None:
					pname = d[9]['p1FN'] + " " + d[9]['p1LN'] + " " + d[9]['p1SUF']
				elif d[9]['p1FN'] == "None":
					pname = "None"
				else:
					pname = d[9]['p1FN'] + " " + d[9]['p1LN']
					
					
				#query = "INSERT IGNORE INTO bbc_pitcherentry (pid,name,gamenumber,espnid,espnid2,teamid,teamname,doubleheader,nogame,ip,hits,ers,bbs,ks,w,pts)
				#    		VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s  )"
				
				#values = (pid,pname,gamenumber,espnid,espnid2,teamid,teamname,doubleheader,nogame,ipouts,phits,ers,pbbs,ks,ws,pts)
				
				#cmy.execute(query,values)
				
				pitcher = pid
				te = time.time()
				
				whip = stat.calculateWHIP(phits,pbbs,ipouts)
				
				era = stat.calculateERA(ers,ipouts)
				
				slug = stat.calculateSlug(abs,tbs)
				
				ptsabs = stat.calculatePtsABs(tbs,runs,rbis,bbs,sbs,abs)
				
				if runs > ers:
					runwin = 1
				elif runs == ers:
					runtie = 1
				else:
					runloss = 1
				stat
				if rbis > ers:
					rbiwin = 1
				elif rbis == ers:
					rbitie = 1
				else:
					rbiloss = 1
					
				points = tpts
				utpts += tpts
				
				eid = int(uid) * 10000 + day
				
				query = """INSERT IGNORE INTO bbc_entry (uid_id,eid,gamenumber,points,p1salary,p1_id,p2salary,p2_id,p3salary,p3_id,p4salary,p4_id,p5salary,p5_id,p6salary,p6_id,p7salary,p7_id,p8salary,p8_id,p9salary,p9_id,pssalary,ps_id,abs,tbs,rbis,bbs,sbs,runs,ips,phits,pbbs,ers,ks,ws,slug,era,whip,runwin,runloss,runtie,rbiwin,rbiloss,rbitie,ptsabs)
				    		VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s , %s, %s  )"""
				#45                   1  2  3    4  5    6   7  8    9  10  11   12  13  14  15  16 17  18  19  20   21  22 23  24  25  26  27 28   29  30  31  32  33  34  35  36 37   38  39  40  41  42   43  44
				#		  1    2     3         4      5       6   7       8    9     10   11       12  13    14   15      16  17      18  19      20  21     22   23      24  25  26   27  28  29  30   31  32    33  34   35 36 37  38   39    40    41       42     43     44      45     46
				values = (uid,eid,gamenumber,points,p1salary,p1,p2salary,p2,p3salary,p3,p4salary,p4,p5salary,p5,p6salary,p6,p7salary,p7,p8salary,p8,p9salary,p9,pssalary,pid,abs,tbs,rbis,bbs,sbs,runs,ipouts,phits,pbbs,ers,ks,ws,slug,era,whip,runwin,runloss,runtie,rbiwin,rbiloss,rbitie,ptsabs)
				#print values
				cmy.execute(query,values)
				
				tef = time.time()
				
				tentry = tef - te
			if day==endgame-1:
				#print "maxgame"
				tdayf = time.time()
				values = (endgame,utpts,uid)
				query = "UPDATE bbc_user set maxgame = %s, totalpoints = %s where uid = %s"
				cmy.execute(query,values)
				
			tday2 = time.time()	
	tf = time.time()
	#print 'sqlite {0}'.format(tsqlite)
	#print tf-tt"""



def daySQLLoop(id,c,conn,h,connmy,cmy):
	tt = time.time()
	tsqlite = 0
	tplayers = 0
	tpitchers = 0
	tentry = 0
	tmany = 0
	tplayersql = 0
	tnoplayer = 0
	utpts = 0
	
	cmy.execute("SELECT * FROM bbc_user WHERE espnid = %s",id)
	user = cmy.fetchone()
	
	
	if user == None:
		espnid = id
		name = getUserName(espnid)
		values = (name,espnid,0,1)
		query = """INSERT INTO bbc_user (name,espnid,totalpoints,maxgame)
		    		VALUES (%s, %s, %s, %s )"""
		cmy.execute(query,values)
		cmy.execute("SELECT * FROM bbc_user WHERE espnid = %s",id)
		user = cmy.fetchone()
		connmy.commit()
		#print user
		maxgame = 1
		uid = user[0]
		utpts = 0
	else:
		#utpts = user[3]
		maxgame = user[4]
		uid = user[0]
	
	for day in range(maxgame,endgame):
		
		if day != 104 and day != 105:
			totalabs=0;totaltbs=0;totalrbis=0;totalbbs=0;totalbbs=0;totalsbs=0;totalruns=0;tpts=0
			runwin=0;runtie=0;runloss=0;rbiwin=0;rbitie=0;rbiloss=0;
			
			players = []
			pitcher = 0
			tday1 = time.time()
			key = int(id) * 1000000 + day
			ts = time.time()
			c.execute("SELECT * FROM entry WHERE id = ?", (key,))
			e = c.fetchone()
			if e == None:
				#print "NONE {0} {1}".format(id, day)
				parserSQL(int(id),c,h)
				#conn.commit()
				c.execute("SELECT * FROM entry WHERE id = ?", (key,))
				e = c.fetchone()
			tsf = time.time()
			tsqlite += (tsf-ts)
			
			if e[3]=="True":
				tpl = time.time()
				
				tpts = 0
				abs = 0;tbs = 0;runs = 0;rbis = 0;bbs = 0;sbs = 0
				ip = 0;phits = 0;pbbs = 0;ers = 0;ks = 0;ws = 0
				pp=list()
				sal=list()
				for i in range(4,21):
					if  i%2==0:			
						key = e[i] * 1000000 + day
						pid = key
						ts = time.time()
						c.execute("SELECT * FROM player WHERE id = ?", (key,))
						p = c.fetchone()
						tsf = time.time()
						#tsqlite += tsf-ts
						
						#players.append(key)
						
						pts = int(p[11]) + int(p[12]) + int(p[13]) + int(p[14]) + int(p[15])
						
						totalabs += int(p[10])
						totaltbs += int(p[15])
						totalruns += int(p[12])
						totalrbis += int(p[13])
						totalbbs += int(p[11])
						totalsbs += int(p[14])
						tpts += pts
						
						name = p[3] + " " + p[4]
						double = 0
						if p[16] == 'True':
							double = 1
						else:
							double = 0
						
						pid = p[6] * 10000 + day
						
						players.append(pid)
						
						espnid=p[5];game = int(day);pos=p[2];bbcid=p[6];doubleheader=double;nogame=p[18];abs=p[10];runs=p[12];tbs=p[15];rbis=p[13];bbs=p[11];sbs=p[14];teamid=p[7];teamname=teams.team[int(p[7])]
						
						#query = """INSERT DELAYED IGNORE INTO bbc_playerentry (pid,espnid,gamenumber,pos,bbcid,doubleheader,nogame,abs,runs,tbs,rbis,bbs,sbs,pts,teamid,teamname,name)
						#    		VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s )"""
						
						#values = (pid,espnid,int(day),pos,bbcid,doubleheader,nogame,abs,runs,tbs,rbis,bbs,sbs,pts,teamid,teamname,name)
						#cmy.execute(query,values)
						
				p1salary=e[5];p2salary=e[7];p3salary=e[9]
				p4salary=e[11];p5salary=e[13];p6salary=e[15]
				p7salary=e[17];p8salary=e[19];p9salary=e[21]
				pssalary=e[23]
				#print players
				p1 = players[0];p2 = players[1];p3 = players[2];
				p4 = players[3];p5 = players[4];p6 = players[5];
				p7 = players[6];p8 = players[7];p9 = players[8]
				
				tplf = time.time()
				tplayers += tplf-tpl
			
				key = e[22] * 1000000 + day
				
				ts =  time.time()
				c.execute("SELECT * FROM ps WHERE id = ?", (key,))
				ps = c.fetchone()
				tsf = time.time()
				#tsqlite += tsf-ts
				
				phits = int(ps[14]);pbbs = int(ps[16])
				ers = int(ps[15]);ks = int(ps[17])
				ws = int(ps[18]);ip = ps[13]
				ipouts = stat.ipToOuts(ip)
				
				espnid = ps[8]
				espnid2 = ps[9]
				doubleheader = ps[19]
				gamenumber=int(day)
				nogame = ps[21]
				teamname = teams.team[int(ps[10])]
				teamid = ps[10]
				
				pts = stat.ipToOuts(ps[13]) + int(ps[17]) - int(ps[14]) - (3*int(ps[15])) - int(ps[16]) + (5*(int(ps[18])))
				tpts += pts
				
				pid = e[22] * 10000 + day
				pname = ""
				if ps[4] != None:
					pname = ps[2]+ " " + ps[3]+ " " + ps[4]
				elif ps[2] == "None":
					pname = "None"
				else:
					pname = ps[2]+ " " + ps[3]
				
					
				#query = """INSERT IGNORE INTO bbc_pitcherentry (pid,name,gamenumber,espnid,espnid2,teamid,teamname,doubleheader,nogame,ip,hits,ers,bbs,ks,w,pts)
				#    		VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s  )"""
				
				#values = (pid,pname,gamenumber,espnid,espnid2,teamid,teamname,doubleheader,nogame,ipouts,phits,ers,pbbs,ks,ws,pts)
				
				#cmy.execute(query,values)
				
				pitcher = pid
				te = time.time()
				
				whip = stat.calculateWHIP(phits,pbbs,ipouts)
				
				era = stat.calculateERA(ers,ipouts)
				
				slug = stat.calculateSlug(abs,tbs)
				
				ptsabs = stat.calculatePtsABs(tbs,runs,rbis,bbs,sbs,abs)
				
				if runs > ers:
					runwin = 1
				elif runs == ers:
					runtie = 1
				else:
					runloss = 1
				stat
				if rbis > ers:
					rbiwin = 1
				elif rbis == ers:
					rbitie = 1
				else:
					rbiloss = 1
				
				points = tpts
				utpts += tpts
				
				eid = int(uid) * 10000 + day
				
				query = """INSERT IGNORE INTO bbc_entry (uid_id,eid,gamenumber,points,p1salary,p1_id,p2salary,p2_id,p3salary,p3_id,p4salary,p4_id,p5salary,p5_id,p6salary,p6_id,p7salary,p7_id,p8salary,p8_id,p9salary,p9_id,pssalary,ps_id,abs,tbs,rbis,bbs,sbs,runs,ips,phits,pbbs,ers,ks,ws,slug,era,whip,runwin,runloss,runtie,rbiwin,rbiloss,rbitie,ptsabs)
				    		VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s , %s, %s  )"""
				#45                   1  2  3    4  5    6   7  8    9  10  11   12  13  14  15  16 17  18  19  20   21  22 23  24  25  26  27 28   29  30  31  32  33  34  35  36 37   38  39  40  41  42   43  44
				#		  1    2     3         4      5       6   7       8    9     10   11       12  13    14   15      16  17      18  19      20  21     22   23      24  25  26   27  28  29  30   31  32    33  34   35 36 37  38   39    40    41       42     43     44      45     46
				values = (uid,eid,gamenumber,points,p1salary,p1,p2salary,p2,p3salary,p3,p4salary,p4,p5salary,p5,p6salary,p6,p7salary,p7,p8salary,p8,p9salary,p9,pssalary,pid,abs,tbs,rbis,bbs,sbs,runs,ipouts,phits,pbbs,ers,ks,ws,slug,era,whip,runwin,runloss,runtie,rbiwin,rbiloss,rbitie,ptsabs)
				#print values
				cmy.execute(query,values)
				
				
				
				tef = time.time()
				
				tentry = tef - te
			if day==endgame-1:
				tdayf = time.time()
				values = (endgame,utpts,uid)
				query = """UPDATE bbc_user set maxgame = %s, totalpoints = %s where uid = %s"""
				cmy.execute(query,values)
				
			tday2 = time.time()	
	tf = time.time()
	#print 'sqlite {0}'.format(tsqlite)
	#print tf-tt


def playerAdd():
	connmy = MySQLdb.connect (host = "localhost",
	                           user = "root",
	                           passwd = "new-password",
	                           db = "bbcuni")
	connmy.autocommit(False) 
	cmy = connmy.cursor ()
	
	file = "/Users/Jason/bbcdata/entrysqlnew" + ".db"
	conn = sqlite3.connect(file)
	
	c = conn.cursor()
	h = httplib2.Http()
	ts = time.time()
	
	c.execute("SELECT * FROM player")
	play = c.fetchall()
	for p in play:
	
		pts = int(p[11]) + int(p[12]) + int(p[13]) + int(p[14]) + int(p[15])
	
		name = p[3] + " " + p[4]
		double = 0
		if p[16] == 1:
			double = 1
		else:
			double = 0
		pid = int(p[6]) * 10000 + int(p[1])
	
		espnid=p[5];game = p[1];pos=p[2];bbcid=p[6];doubleheader=double;nogame=p[18];abs=p[10];runs=p[12];tbs=p[15];rbis=p[13];bbs=p[11];sbs=p[14];teamid=p[7];teamname=teams.team[int(p[7])]
	
		query = """INSERT DELAYED IGNORE INTO bbc_playerentry (pid,espnid,gamenumber,pos,bbcid,doubleheader,nogame,abs,runs,tbs,rbis,bbs,sbs,pts,teamid,teamname,name)
		    		VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s )"""
	
		values = (pid,espnid,game,pos,bbcid,double,nogame,abs,runs,tbs,rbis,bbs,sbs,pts,teamid,teamname,name)
		cmy.execute(query,values)
	tf = time.time()
	print tf-ts


def pitcherAdd():
	connmy = MySQLdb.connect (host = "localhost",
	                           user = "root",
	                           passwd = "new-password",
	                           db = "bbcuni")
	connmy.autocommit(False) 
	cmy = connmy.cursor ()
	
	file = "/Users/Jason/bbcdata/entrysqlnew" + ".db"
	conn = sqlite3.connect(file)
	
	c = conn.cursor()
	h = httplib2.Http()
	ts = time.time()
	
	c.execute("SELECT * FROM ps")
	pit = c.fetchall()
	
	for ps in pit:
		phits = int(ps[14]);pbbs = int(ps[16])
		ers = int(ps[15]);ks = int(ps[17])
		ws = int(ps[18]);ip = ps[13]
		ipouts = stat.ipToOuts(ip)
	
		day = int(ps[1])
	
		espnid = ps[8]
		espnid2 = ps[9]
		doubleheader = ps[19]
		gamenumber=int(day)
		nogame = ps[21]
		teamname = teams.team[int(ps[10])]
		teamid = ps[10]
	
		pts = stat.ipToOuts(ps[13]) + int(ps[17]) - int(ps[14]) - (3*int(ps[15])) - int(ps[16]) + (5*(int(ps[18])))
		
		pid = ps[10] * 10000 + day
		pname = ""
		pname2 = ""
		if ps[4] != None:
			pname = ps[2]+ " " + ps[3]+ " " + ps[4]
		elif ps[2] == "None":
			pname = "None"
		else:
			pname = ps[2]+ " " + ps[3]
		if ps[19] == True:
			if ps[7] != None:
				pname2 = ps[5]+ " " + ps[6] + " " + ps[7]
			elif ps[5] == "None":
				pname2 = "None"
			else:
				pname2 = ps[5] + " " + ps[6]
		query = """INSERT IGNORE INTO bbc_pitcherentry (pid,name,name2,gamenumber,espnid,espnid2,teamid,teamname,doubleheader,nogame,ip,hits,ers,bbs,ks,w,pts)
		    		VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s  )"""
	
		values = (pid,pname,pname2,gamenumber,espnid,espnid2,teamid,teamname,doubleheader,nogame,ipouts,phits,ers,pbbs,ks,ws,pts)
		cmy.execute(query,values)
	tf = time.time()
	print tf-ts


def startScrape():
	connmy = MySQLdb.connect (host = "localhost",
	                           user = "root",
	                           passwd = "new-password",
	                           db = "bbctesting")
	connmy.autocommit(False) 
	cmy = connmy.cursor ()
	
	file = "/Users/Jason/newentriesdone.txt"
	infile = open(file,"r")
	
	file = "/Users/Jason/bbcdata/entrysqlnew" + ".db"
	conn = sqlite3.connect(file)
	
	c = conn.cursor()
	h = httplib2.Http()
	
	t5=time.time()
	
	i = infile.readlines()
	
	percommit=100;count = 0
	
#	daySQLLoop(90973,c,conn,h,connmy,cmy)
	
	for x in i:
		#print x
		count+=1
		id = int(x.split("\n")[0])
		if count > 0:
			#parserSQL(id,c,h)
			daySQLLoopv2(id,c,conn,h,connmy,cmy)
			
			if count % percommit == 0:
				tf = time.time()
				timeperc = tf-t5
				pereach = timeperc/percommit
				#print 'count {0} per each {1}'.format(count,pereach)
				t5=time.time()
			#if count == 300:
			#	break


def teamStatsUpdate(id):
	connmy = MySQLdb.connect (host = "localhost",
	                           user = "root",
	                           passwd = "new-password",
	                           db = "bbcuni")
	connmy.autocommit(False) 
	cmy = connmy.cursor ()
	
	ts = time.time()
	
	cmy.execute("SELECT * FROM bbc_user WHERE espnid = %s",id)
	user = cmy.fetchone()
	maxgame = user[4]
	uid = user[0]
	
	team = {}
	
	positions = ["C","1B","2B","3B","SS","LF","CF","RF","DH"]
	stats = ["abs","runs","tbs","rbis","bbs","sbs"]
	pstats = ["ips","phits","pbbs","ers","ks","ws"]
	players = {}
	
	for i in positions:
		players[i] = {}
		players[i]['players'] = {}
		for j in stats:
			players[i][j] = 0
	
	for i in range (1,31):
		team[i] = {}
		for j in stats:
			team[i][j]=0
		for j in pstats:
			team[i][j]=0
	
	count = 0
	
	cmy.execute("SELECT maxgame from bbc_totalteamstats where uid_id = %s",id)
	max = cmy.fetchone()
	if max != None:
		cmy.execute("SELECT p1_id,p2_id,p3_id,p4_id,p5_id,p6_id,p7_id,p8_id,p9_id from bbc_entry where uid_id = %s",uid)
		ents = cmy.fetchall()
	else:
		cmy.execute("SELECT p1_id,p2_id,p3_id,p4_id,p5_id,p6_id,p7_id,p8_id,p9_id from bbc_entry where uid_id = %s",uid)
		ents = cmy.fetchall()
	
	
	#cmy.execute("SELECT p1_id,p2_id,p3_id,p4_id,p5_id,p6_id,p7_id,p8_id,p9_id from bbc_entry where uid_id = %s",uid)
	#ents = cmy.fetchall()
	
	for plays in ents:
		for p in plays:
			#print "i"
			count += 1
			cmy.execute("SELECT pos,espnid,teamid,abs,runs,tbs,rbis,bbs,sbs,name,bbcid,doubleheader from bbc_playerentry where pid = %s",p) 
			
			pl = cmy.fetchone()
			if pl!=None:
				team[pl[2]]['abs'] += pl[3]
				team[pl[2]]['runs'] += pl[4]
				team[pl[2]]['tbs'] += pl[5]
				team[pl[2]]['rbis'] += pl[6]
				team[pl[2]]['bbs'] += pl[7]
				team[pl[2]]['sbs'] += pl[8]
				if pl[1] not in players[pl[0]]['players']:
					players[pl[0]]['players'][pl[1]] = {}
					
					players[pl[0]]['players'][pl[1]]['teamid'] = pl[2]
					players[pl[0]]['players'][pl[1]]['name'] = pl[9]
					players[pl[0]]['players'][pl[1]]['bbcid'] = pl[10]
					if pl[11] ==1:
						#print pl[11]
						players[pl[0]]['players'][pl[1]]['games'] = 2
					else:
						players[pl[0]]['players'][pl[1]]['games'] = 1
					players[pl[0]]['players'][pl[1]]['abs'] = pl[3]
					players[pl[0]]['players'][pl[1]]['runs'] = pl[4]	
					players[pl[0]]['players'][pl[1]]['tbs'] = pl[5]
					players[pl[0]]['players'][pl[1]]['rbis'] = pl[6]
					players[pl[0]]['players'][pl[1]]['bbs'] = pl[7]
					players[pl[0]]['players'][pl[1]]['sbs'] = pl[8]
				else:
					if pl[11] ==1:
						#print pl[11]
						players[pl[0]]['players'][pl[1]]['games'] += 2
					else:
						players[pl[0]]['players'][pl[1]]['games'] += 1
					players[pl[0]]['players'][pl[1]]['abs'] += pl[3]
					players[pl[0]]['players'][pl[1]]['runs'] += pl[4]	
					players[pl[0]]['players'][pl[1]]['tbs'] += pl[5]
					players[pl[0]]['players'][pl[1]]['rbis'] += pl[6]
					players[pl[0]]['players'][pl[1]]['bbs'] += pl[7]
					players[pl[0]]['players'][pl[1]]['sbs'] += pl[8]
				players[pl[0]]['abs'] += pl[3]
				players[pl[0]]['runs'] += pl[4]
				players[pl[0]]['tbs'] += pl[5]
				players[pl[0]]['rbis'] += pl[6]
				players[pl[0]]['bbs'] += pl[7]
				players[pl[0]]['sbs'] += pl[8]
	
	query = ("SELECT ps_id from bbc_entry where uid_id = %s")
	values = (uid)
	cmy.execute(query,values)
	ents = cmy.fetchall()
	
	for e in ents:
		pit = e[0]
		
		
		cmy.execute("SELECT teamid,ip,hits,ers,bbs,ks,w from bbc_pitcherentry where pid = %s",pit)
		#values = (pit)
		
		pstat = cmy.fetchone()
		
		team[pstat[0]]['ips'] += pstat[1]
		team[pstat[0]]['phits'] += pstat[2]
		team[pstat[0]]['pbbs'] += pstat[4]
		team[pstat[0]]['ers'] += pstat[3]
		team[pstat[0]]['ks'] += pstat[5]
		team[pstat[0]]['ws'] += pstat[6]
	
	
	#Handle position entry
	pos2posstr={'C':"Catcher",'1B':"First Base",'2B':"Second Base",'3B':"Third Base",'SS':"Shortstop",'LF':"Left Field",'CF':"Center Field",'RF':"Right Field",'DH':"Designated Hitter"}
	pos2int={'C':0,'1B':1,'2B':3,'3B':4,'SS':5,'LF':6,'CF':7,'RF':8,'DH':9}
	for i in positions:
		#Get position and position string for use
		pos = pos2int[i]
		posstr = pos2posstr[i]
		
		totalabs=0;totaltbs=0;totalrbis=0;totalbbs=0;totalsbs=0;totalruns=0;totalgames=0
		for j in players[i]['players']:
			
			query = """INSERT IGNORE INTO bbc_playerstat (uid_id,name,pos,posstr,espnid,bbcid,teamid,teamname,abs,tbs,rbis,bbs,sbs,runs,slug,ptsabs,games,maxgame,pts)
			    		VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s )"""
			
			name = players[i]['players'][j]['name']
			
			espnid = j
			bbcid = players[i]['players'][j]['bbcid']
			teamid = players[i]['players'][j]['teamid']
			teamname = teams.team[teamid]
			abs = players[i]['players'][j]['abs']
			tbs = players[i]['players'][j]['tbs']
			rbis = players[i]['players'][j]['rbis']
			bbs = players[i]['players'][j]['bbs']
			sbs = players[i]['players'][j]['sbs']
			runs = players[i]['players'][j]['runs']
			
			#Tabulate totals for total stats for the position
			totalabs+=abs;totaltbs+=tbs;totalrbis+=rbis;totalbbs+=bbs;totalsbs+=sbs;totalruns+=runs;
			
			slug = stat.calculateSlug(abs,tbs)
			ptsabs = stat.calculatePtsABs(tbs,runs,rbis,bbs,sbs,abs)
			maxgame = maxgame
			pts = stat.calculatePlayerPTs(bbs,sbs,rbis,runs)
			games = players[i]['players'][j]['games']
			totalgames += games
			
			values = (uid,name,pos,posstr,espnid,bbcid,teamid,teamname,abs,tbs,rbis,bbs,sbs,runs,slug,ptsabs,games,maxgame,pts)
			cmy.execute(query,values)
		totalslug = stat.calculateSlug(totalabs,totaltbs)
		totalptsabs = stat.calculatePtsABs(totaltbs,totalruns,totalrbis,totalbbs,totalsbs,totalabs)
		totalpts = stat.calculatePlayerPTs(totalbbs,totalsbs,totalrbis,totalruns)
		
		query = """INSERT IGNORE INTO bbc_positionplayerstats (uid_id,pos,posstr,posfullstr,abs,tbs,rbis,bbs,sbs,runs,slug,ptsabs,pts,games,maxgame)
		    		VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
		
		values = (uid,pos,i,posstr,totalabs,totaltbs,totalrbis,totalbbs,totalsbs,totalruns,totalslug,totalptsabs,totalpts,totalgames,maxgame)
		cmy.execute(query,values)
	
	#Handle teams		
	for i in range (1,31):
		query = """INSERT IGNORE INTO bbc_totalteamstats (uid_id,tid,teamid,teamname,maxgame,abs,tbs,rbis,bbs,sbs,slug,runs,ips,phits,pbbs,ers,ks,ws,era,whip,playpoints,pitchpoints,points,playspresent,pitspresent,ptsabs)
		    		VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s )"""
		tid = uid*10000 +i
		
		playpoints = 0;pitchpoints = 0;playpresent = 0;pitspresent = 0;
		ptsabs = 0;era= 0;whip = 0;slug=0;
		
		
		teamname=teams.team[i]
		playpoints = team[i]['tbs']+team[i]['bbs']+team[i]['rbis']+team[i]['runs']+team[i]['sbs']
		pitchpoints = team[i]['ips']-team[i]['phits']-team[i]['pbbs']-3*team[i]['ers']+team[i]['ks']+5*team[i]['ws']
		points = playpoints + pitchpoints
		
		if team[i]['abs'] > 0 or team[i]['bbs'] > 0:
			playpresent = 1
		if team[i]['ips'] > 0 or team[i]['phits'] > 0 or team[i]['pbbs'] > 0:
			pitspresent = 1
		if playpresent:
			if team[i]['abs'] > 0:
				slug = round(float(team[i]['tbs'])/float(team[i]['abs']),3)
				ptsabs = round(float(team[i]['tbs']+team[i]['bbs']+team[i]['rbis']+team[i]['runs']+team[i]['sbs'])/float(team[i]['abs']),3)
			else:
				slug = 0
				ptsabs = 0
		if pitspresent:
			if team[i]['ips'] >0:
				era = round(float(team[i]['ers']*9)/float(team[i]['ips']/3),3)
				whip = round(float(team[i]['phits']+team[i]['pbbs'])/float(team[i]['ips']/3),3)
		
	
		values = (uid,tid,i,teamname,maxgame,team[i]['abs'],team[i]['tbs'],team[i]['rbis'],team[i]['bbs'],team[i]['sbs'],slug,team[i]['runs'],team[i]['ips'],team[i]['phits'],team[i]['pbbs'],team[i]['ers'],team[i]['ks'],team[i]['ws'],era,whip,playpoints,pitchpoints,points,playpresent,pitspresent,ptsabs)
		cmy.execute(query,values)
	#print count
	tf = time.time()
	
	
	print tf-ts

def rankoverallcalc():
	ts = time.time()
	connmy = MySQLdb.connect (host = "localhost",
	                           user = "root",
	                           passwd = "new-password",
	                           db = "bbcuni")
	connmy.autocommit(False) 
	cmy = connmy.cursor ()
	values = []
	pts = {}	
	for g in range(1,170):
		cmy.execute("SELECT uid_id,points,gamenumber from bbc_entry where gamenumber = %s",g)
		
		ents = cmy.fetchall()
		count = 0
		for i in ents:
			if i[0] not in pts:
				pts[i[0]] = i[1]
			else:
				pts[i[0]] += i[1]
			count+=1 
		print pts[48141]
		
	sorted_x = sorted(pts.iteritems(), key=operator.itemgetter(1),reverse=True)
	count = len(sorted_x)
	rank = 0
	nextrank = 0
	prev = 100000
	ranks = {}
	equals= []
	numequal = 0
	for i in sorted_x:
		nextrank += 1
		if i[1] < prev:
			if numequal>0:
				for p in equals:
					values.append((p,g,rank,round(float((count-rank)+.5*numequal)/count*100,2)))
				equals = []		
			rank += nextrank
			nextrank = 0
			prev =  i[1]
			numequal = 1
			equals.append(i[0])
			#values.append((i[0],g,rank,round(float(count-rank)/count*100,2)))
		else:
			ranks[i[0]] = rank
			numequal+=1
			equals.append(i[0])
	#print "rank {0} game {1}".format(rank,g)
	query = """INSERT IGNORE INTO bbc_useroverallrank (uid_id,maxgame,rank,pct)
	   		VALUES (%s, %s, %s, %s )"""
	
	cmy.executemany(query,values)
	tf = time.time()
	print tf-ts


def rankcalc():
		
	for g in range(100,170):
		values = []
		pts = {}
		cmy.execute("SELECT uid_id,points,gamenumber from bbc_entry where gamenumber = %s",g)
		
		ents = cmy.fetchall()
		count = 0
		for i in ents:
			count+=1 
			pts[i[0]] = i[1]
		print count
		sorted_x = sorted(pts.iteritems(), key=operator.itemgetter(1),reverse=True)
		rank = 0
		nextrank = 0
		prev = 1000
		ranks = {}
		equals= []
		numequal = 0
		for i in sorted_x:
			nextrank += 1
			if i[1] < prev:
				if numequal>0:
					for p in equals:
						values.append((p,g,rank,round(float((count-rank)+.5*numequal)/count*100,2)))
					equals = []		
				rank += nextrank
				nextrank = 0
				prev =  i[1]
				numequal = 1
				equals.append(i[0])
				#values.append((i[0],g,rank,round(float(count-rank)/count*100,2)))
			else:
				ranks[i[0]] = rank
				numequal+=1
				equals.append(i[0])
		#print "rank {0} game {1}".format(rank,g)
		query = """INSERT IGNORE INTO bbc_userrank (uid_id,game,rank,pct)
		   		VALUES (%s, %s, %s, %s )"""
		cmy.executemany(query,values)
	tf = time.time()
	print tf-ts

def teamScrape():
	connmy = MySQLdb.connect (host = "localhost",
	                           user = "root",
	                           passwd = "new-password",
	                           db = "bbcuni")
	connmy.autocommit(False) 
	cmy = connmy.cursor ()
	
	cmy.execute("SELECT espnid FROM bbc_user where espnid = %s",90973)
	
	user = cmy.fetchall()
	
	for u in user:
		teamStatsUpdate(u)
		break


def getMoreUsers():
	connmy = MySQLdb.connect (host = "localhost",
	                           user = "root",
	                           passwd = "new-password",
	                           db = "bbcuni")
	connmy.autocommit(False) 
	cmy = connmy.cursor ()
	h = httplib2.Http()
	
	file = "/Users/Jason/newentries.txt"
	
	count = 0
	ts = time.time()
	for i in range(1,250000):
		cmy.execute("SELECT uid from bbc_user where espnid = %s ",i)
		user = cmy.fetchone()
		if user == None:		
			s = "http://games.espn.go.com/baseball-challenge/en/format/ajax/getBoxscoreSnapshot?entryID=" + str(i) + "&spid=" + str(8)
			headers = {
			'Accept': 'text/html, */*',
			'Accept-Language': 'en-us,en;q=0.5',
			'Accept-Encoding':	'gzip, deflate',
			'Connection':	'Keep-Alive',
			}
			response, content = h.request(s,headers=headers)
			if content == "No set roster for entry<input type=hidden id=\"setInterval\" value=\"0\">" or content == '':
				x=1
			else:
				root = html.fromstring(content)
				data = root.cssselect('thead')
				pl = data[0].cssselect('td')
				
				if "-" in tostring(pl[1]).split("games-colh2\">")[1]:
					x=1
				else:
					count +=1
					print "id {0} count {1}".format(i,count)
					out = "{0}\n".format(i)
					outfile = open(file,"a")
					
					outfile.write(out)
					if i % 100 ==0:
						tf=time.time()
						print tf-ts
						ts = time.time()
						


class Scrape(multiprocessing.Process):
	def run(self):
		t = self._kwargs['file']
		connmy = MySQLdb.connect (host = "localhost",
		                           user = "root",
		                           passwd = "new-password",
		                           db = "bbctesting")
		connmy.autocommit(False) 
		cmy = connmy.cursor ()

		file = "/Users/Jason/newentriesdone.txt"
		infile = open(file,"r")
		
		file = "/Users/Jason/bbcdata/entrysqlnew" + ".db"
		conn = sqlite3.connect(file)

		c = conn.cursor()
		h = httplib2.Http()

		t5=time.time()

		i = infile.readlines()

		percommit=100;count = 0

	#	daySQLLoop(90973,c,conn,h,connmy,cmy)

		for x in i:
			#print x
			count+=1
			if count % 50 == t:
				id = int(x.split("\n")[0])
				#print "{0} {1}".format(count,t)
				#parserSQL(id,c,h)
				daySQLLoopv2(id,c,conn,h,connmy,cmy)

				#if count % percommit == 0:
				#	tf = time.time()
				#	timeperc = tf-t5
				#	pereach = timeperc/percommit
					#print 'count {0} per each {1}'.format(count,pereach)
				#	t5=time.time()
				#if count == 300:
				#	break


class MoreUsers(multiprocessing.Process):
	def run(self):
		t = self._kwargs['file']
		
		connmy = MySQLdb.connect (host = "localhost",
		                           user = "root",
		                           passwd = "new-password",
		                           db = "bbcuni")
		connmy.autocommit(False) 
		cmy = connmy.cursor ()
		h = httplib2.Http()
		
		file = "/Users/Jason/newentries2" + str(t) + ".txt"
		
		count = 0
		ts = time.time()
		for a in range(140000,400000,80):
			i = a + t
			# print "{0} {1}".format(i,t)
			cmy.execute("SELECT uid from bbc_user where espnid = %s ",i)
			user = cmy.fetchone()
			if user == None:		
				s = "http://games.espn.go.com/baseball-challenge/en/format/ajax/getBoxscoreSnapshot?entryID=" + str(i) + "&spid=" + str(8)
				headers = {
				'Accept': 'text/html, */*',
				'Accept-Language': 'en-us,en;q=0.5',
				'Accept-Encoding':	'gzip, deflate',
				'Connection':	'Keep-Alive',
				}
				response, content = h.request(s,headers=headers)
				if content == "No set roster for entry<input type=hidden id=\"setInterval\" value=\"0\">" or content == '':
					x=1
				else:
					root = html.fromstring(content)
					data = root.cssselect('thead')
					pl = data[0].cssselect('td')
					
					if "-" in tostring(pl[1]).split("games-colh2\">")[1]:
						x=1
					else:
						count +=1
						
						out = "{0}\n".format(i)
						outfile = open(file,"a")
						
						outfile.write(out)
						if count % 100 ==0:
							if self.name == "MoreUsers-1":
								#print t
								print "id {0} count {1}".format(i,count)
								tf=time.time()
								print tf-ts
								ts = time.time()
							

"""count =0
l = []
for ff in range(1,81):
	file = "/Users/Jason/newentries" + str(ff) + ".txt"
	infile = open(file,"r")
	i = infile.readlines()
	l
	for x in i:
		count +=1
		l.append(int(x))
l = sorted(l)
file = file = "/Users/Jason/newentriesdone.txt"
for dd in l:
	out = "{0}\n".format(dd)
	outfile = open(file,"a")
	outfile.write(out)
	#example = MoreUsers(kwargs={'file': i})
	#example.start()"""
	
for ff in range(1,50):
	example = Scrape(kwargs={'file': ff})
	example.start()


#playerAdd()
#pitcherAdd()		
#startScrape()

#teamScrape()
#rankoverallcalc()
#getMoreUsers()
#teamStatsUpdate(90973)