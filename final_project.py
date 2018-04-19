#!/usr/bin/env python3
# SI507 Winter 2018 Final project
from bs4 import BeautifulSoup
import csv
import os
import requests
import sqlite3
import secrets
import json
import plotly.plotly as py
from plotly.graph_objs import *

DBNAME = 'NBA_stats.db'
team_name={
	"ATL": "Atlanta Hawks",
	"BOS": "Boston Celtics",
	"BKN": "Brooklyn Nets",
	"NJ": "Brooklyn Nets",
	"CHA": "Charlotte Hornets",
	"CHI": "Chicago Bulls",
	"CLE": "Cleveland Cavaliers",
	"DAL": "Dallas Mavericks",
	"DEN": "Denver Nuggets",
	"DET": "Detroit Pistons",
	"GS": "Golden State Warriors",
	"HOU": "Houston Rockets",
	"IND": "Indiana Pacers",
	"LAC": "Los Angeles Clippers",
	"LAL": "Los Angeles Lakers",
	"MEM": "Memphis Grizzlies",
	"MIA": "Miami Heat",
	"MIL": "Milwaukee Bucks",
	"MIN": "Minnesota Timberwolves",
	"NO": "New Orleans Pelicans",
	"NY": "New York Knicks",
	"OKC": "Oklahoma City Thunder",
	"SEA": "Oklahoma City Thunder",
	"ORL": "Orlando Magic",
	"PHI": "Philadelphia 76ers",
	"PHX": "Phoenix Suns",
	"POR": "Portland Trail Blazers",
	"SAC": "Sacramento Kings",
	"SAS": "San Antonio Spurs",
	"TOR": "Toronto Raptors",
	"UTAH": "Utah Jazz",
	"WAS": "Washington Wizards"    
  }

playoff=["Boston Celtics",
		"Cleveland Cavaliers",
		"Golden State Warriors",
		"Houston Rockets",
		"Indiana Pacers",
		"Miami Heat",
		"Milwaukee Bucks",
		"Minnesota Timberwolves",
		"New Orleans Pelicans",
		"Oklahoma City Thunder",
		"Philadelphia 76ers",
		"Portland Trail Blazers",
		"San Antonio Spurs",
		"Toronto Raptors",
		"Utah Jazz",
		"Washington Wizards"]

# team class with team name, team arena lat and team arena lng 
class nbaTeam():
	def __init__(self, name, lat, lng):
		self.name = name
		self.lat = lat
		self.lng = lng

	def __str__(self):
		return self.name+' ('+str(self.lat)+', '+str(self.lng)+')'

class nbaPlayer():
	def __init__(self, name, url=None):
		self.name = name
		self.url = url

	def __str__(self):
		return self.name+' ('+self.url+')'
		
# Create database and tables
def createDatabase():
	try:
		conn = sqlite3.connect(DBNAME)
		cur = conn.cursor()
	except:
		print('Unable to connect the database.')

	createTeams = '''
			CREATE TABLE 'Teams' (
				'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
				'Name' TEXT NOT NULL,
				'ArenaLocation_lat' TEXT NOT NULL,
				'ArenaLocation_lng' TEXT NOT NULL,
				'url' TEXT NOT NULL
				);
			'''
			
	createPlayers = '''
			CREATE TABLE 'Players' (
				'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
				'No' INTEGER NOT NULL,
				'url' TEXT NOT NULL,
				'Name' TEXT NOT NULL,
				'Position' TEXT,
				'Age' TEXT,
				'Height' TEXT,
				'Weight' TEXT,
				'College' TEXT,
				'TeamId' TEXT NOT NULL,
				'TeamPlayed' TEXT,
				FOREIGN KEY('TeamId') REFERENCES Teams(Id)
			);
		'''

	createRoutes = '''
			CREATE TABLE 'Routes' (
				'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
				'TeamId' TEXT NOT NULL,
				'Team1' TEXT NOT NULL,
				'Team2' TEXT NOT NULL,
				'Team3' TEXT NOT NULL,
				'Team4' TEXT NOT NULL,
				'Team5' TEXT NOT NULL,
				FOREIGN KEY('TeamId') REFERENCES Teams(Id)
			);
		'''

	createPoints = '''
			CREATE TABLE 'Points' (
				'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
				'PlayerId' TEXT NOT NULL,
				'Score1' TEXT,
				'Score2' TEXT,
				'Score3' TEXT,
				'Score4' TEXT,
				'Score5' TEXT,
				FOREIGN KEY('PlayerId') REFERENCES Players(Id)
			);
		'''
	cur.execute("DROP TABLE IF EXISTS 'Teams';")
	cur.execute("DROP TABLE IF EXISTS 'Players';")
	cur.execute("DROP TABLE IF EXISTS 'Routes';")
	cur.execute("DROP TABLE IF EXISTS 'Points';")
	cur.execute(createTeams)
	cur.execute(createPlayers)
	cur.execute(createRoutes)
	cur.execute(createPoints)
	conn.commit()
	conn.close()

# Get names, arena location, webpage url for all NBA teams
# Return a list of team names
def get_all_teams():
	teams = []
	try:
		conn = sqlite3.connect(DBNAME)
		cur = conn.cursor()
	except:
		print('Unable to connect the database.')
	
	data = {}
	CACHE_FNAME = 'NBA_teams.json'
	try:
		cache_file = open(CACHE_FNAME, 'r')
		cache_contents = cache_file.read()
		data = json.loads(cache_contents)
		cache_file.close()
	except:
		pass
		
	teams = []
	if len(data) == 0:
		createDatabase()
		print("Making a request for new data for all NBA teams...")

		url = "http://www.espn.com/nba/teams"
		page = requests.get(url)
		soup = BeautifulSoup(page.text,'html.parser')
		head = soup.find_all(class_='bi')
		for t in head:
			lat = 0
			lng = 0
			name = t.text
			url = t['href']
			data[name] = {}

			key = secrets.google_places_key
			search_url = 'https://maps.googleapis.com/maps/api/place/textsearch/json?query='+name+'+arena'+'&key='+key

			search = requests.get(search_url)
			loc_res = json.loads(search.text)
			
			if len(loc_res['results'])>0:
				lat = loc_res['results'][0]['geometry']['location']['lat']
				lng = loc_res['results'][0]['geometry']['location']['lng']
				data[name]['lat']=lat
				data[name]['lng']=lng
				data[name]['url']=url
			else:
				data[name]['lat']=0
				data[name]['lng']=0
				data[name]['url']=url
			team.append(nbaTeam(name,lat,lng))

			insertion = (name,lat,lng,url)
			statement = 'INSERT INTO Teams '
			statement += 'VALUES (NULL, ?, ?, ?, ?)'

			cur.execute(statement, insertion)
			conn.commit()

			fw = open(CACHE_FNAME,"w")
			json.dump(data,fw, indent=4)
			fw.close()
	else:
		print("Getting cached data for all NBA teams...")
		for r in data:
			teams.append(nbaTeam(r,data[r]['lat'],data[r]['lng']))
	
	conn.close()	
	return teams

# Get all players for a team
def get_players(team):
	name = []
	try:
		conn = sqlite3.connect(DBNAME)
		cur = conn.cursor()
	except:
		print('Unable to connect the database.')

	data = {}
	CACHE_FNAME = 'players.json'
	try:
		cache_file = open(CACHE_FNAME, 'r')
		cache_contents = cache_file.read()
		data = json.loads(cache_contents)
		cache_file.close()
	except:
		
		print('No cached file!')

	if team in data:
		for p in data[team]:
			name.append(p) 
	else:
		
		data[team] = {}
		statement = 'SELECT Id, url FROM Teams WHERE Name="'+team+'"'
		tmp=cur.execute(statement)
		res=tmp.fetchone()
		teamId = res[0]
		url = res[1].split('_')[0]+'roster/_'+res[1].split('_')[1]
		page = requests.get(url)
		soup = BeautifulSoup(page.text,'html.parser')
		head = soup.find(class_="tablehead")
		player = head.find_all('tr')
	
		for i,t in enumerate(player):
			pl = []
			if i >= 2:
				td=t.find_all('td')
				for j,c in enumerate(td):
					if j<=6:
						if j==1:
							pl.append(c.find('a')['href'])
							pl.append(c.text)

						else:				
							pl.append(c.text)
				insertion = (pl[0],pl[1],pl[2],pl[3],pl[4],pl[5],pl[6],pl[7],teamId)
				statement = 'INSERT INTO Players '
				statement += 'VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL)'

				cur.execute(statement, insertion)
				conn.commit()

				name.append(pl[2])
				data[team][pl[2]]={}
				data[team][pl[2]]['url']=pl[1]
				data[team][pl[2]]['position']=pl[3]
				data[team][pl[2]]['age']=pl[4]
				data[team][pl[2]]['height']=pl[5]
				data[team][pl[2]]['weight']=pl[6]
				data[team][pl[2]]['college']=pl[7]
				fw = open(CACHE_FNAME,"w")
				json.dump(data,fw, indent=4)
				fw.close()

	conn.close()
	return name

# Get previous 5 games results for a team
def get_team_route(team):
	try:
		conn = sqlite3.connect(DBNAME)
		cur = conn.cursor()
	except:
		print('Unable to connect the database.')

	data = {}
	CACHE_FNAME = 'routes.json'
	try:
		cache_file = open(CACHE_FNAME, 'r')
		cache_contents = cache_file.read()
		data = json.loads(cache_contents)
		cache_file.close()
	except:
		pass

	statement = 'SELECT Id, url FROM Teams WHERE Name="'+team+'"'
	tmp=cur.execute(statement)
	res=tmp.fetchone()
	teamId = res[0]
	url = res[1]
	page = requests.get(url)
	soup = BeautifulSoup(page.text,'html.parser')
	head = soup.find(class_="club-schedule")
	game = head.find_all('li')
	rival = [team]
	count=0
	for li in game:
		if count != 0 and count < 6:
			against=li.find(class_="game-info").text
			score=li.find(class_="score").text
			res=li.find(class_="game-result").text
			rival.append(against+' '+res+' '+score)		
		count+=1

	if team in data:
		update = (rival[1],rival[2],rival[3],rival[4],rival[5],teamId)
		statement = '''
			UPDATE Routes
			SET Team1=?,
				Team2=?,
				Team3=?,
				Team4=?,
				Team5=?
			WHERE teamId=?
		'''
		cur.execute(statement, update)
		conn.commit()

		data[team]['team1']=rival[1]
		data[team]['team2']=rival[2]
		data[team]['team3']=rival[3]
		data[team]['team4']=rival[4]
		data[team]['team5']=rival[5]

	else:
		insertion = (teamId,rival[1],rival[2],rival[3],rival[4],rival[5])
		statement = 'INSERT INTO Routes '
		statement += 'VALUES (NULL, ?, ?, ?, ?, ?, ?)'

		cur.execute(statement, insertion)
		conn.commit()

		data[team]={}
		data[team]['team1']=rival[1]
		data[team]['team2']=rival[2]
		data[team]['team3']=rival[3]
		data[team]['team4']=rival[4]
		data[team]['team5']=rival[5]

	fw = open(CACHE_FNAME,"w")
	json.dump(data,fw, indent=4)
	fw.close()

	conn.close()
	return rival

# Get points of a player in previous 5 games
def get_points(player):
	try:
		conn = sqlite3.connect(DBNAME)
		cur = conn.cursor()
	except:
		print('Unable to connect the database.')

	data = {}
	CACHE_FNAME = 'points.json'
	try:
		cache_file = open(CACHE_FNAME, 'r')
		cache_contents = cache_file.read()
		data = json.loads(cache_contents)
		cache_file.close()
	except:
		pass

	statement = '''
			SELECT p.url, t.Name 
			FROM Players as p
				JOIN Teams as t
				ON t.Id=p.TeamId
			WHERE p.Name=?
		'''
	params = (player,)
	result = cur.execute(statement,params)
	res = result.fetchone()
	url = res[0]
	tm = res[1]
	if tm in playoff:
		tableId = 2
	else:
		tableId = 1

	points = [player]
	page = requests.get(url)
	soup = BeautifulSoup(page.text,'html.parser')
	head = soup.find_all(class_="tablehead")
	for i,t in enumerate(head):
		if i == tableId:
			table=t.find_all('tr')
			for k,tr in enumerate(table):
				if k < 6:
					against=''
					td = tr.find_all('td')
					for j,d in enumerate(td):
						
						if j == 1:
							against=d.text
						if j == len(td)-1:
							p=d.text
					if against:
						points.append(against+' '+p)						
	if player in data:
		statement = '''
			SELECT p.Id 
			FROM Players as p
				JOIN Points as o
				ON p.Id=o.PlayerId
			WHERE p.Name=?
		'''
		params = (player,)
		res = cur.execute(statement,params)
		playerId=res.fetchone()[0]
		update = (points[1],points[2],points[3],points[4],points[5],playerId)
		statement = '''
			UPDATE Points
			SET Score1=?,
				Score2=?,
				Score3=?,
				Score4=?,
				Score5=?
			WHERE PlayerId=?
		'''
		cur.execute(statement, update)
		conn.commit()

		data[player]['score1']=points[1]
		data[player]['score2']=points[2]
		data[player]['score3']=points[3]
		data[player]['score4']=points[4]
		data[player]['score5']=points[5]

	else:
		statement = '''
			SELECT Id FROM Players
			WHERE Name=?
		'''
		params = (player,)
		res = cur.execute(statement,params)
		playerId=res.fetchone()[0]

		insertion = (playerId,points[1],points[2],points[3],points[4],points[5])
		statement = 'INSERT INTO Points '
		statement += 'VALUES (NULL, ?, ?, ?, ?, ?, ?)'

		cur.execute(statement, insertion)
		conn.commit()

		data[player]={}
		data[player]['score1']=points[1]
		data[player]['score2']=points[2]
		data[player]['score3']=points[3]
		data[player]['score4']=points[4]
		data[player]['score5']=points[5]

	fw = open(CACHE_FNAME,"w")
	json.dump(data,fw, indent=4)
	fw.close()

	conn.close()
	return points

# Get teams a player've ever played for
def get_preteam(player):
	try:
		conn = sqlite3.connect(DBNAME)
		cur = conn.cursor()
	except:
		print('Unable to connect the database.')

	statement = '''
			SELECT url FROM Players 
			WHERE Name=?
		'''
	params = (player,)
	result = cur.execute(statement,params)
	res = result.fetchone()
	url = res[0].split('_')[0]+'stats/_'+res[0].split('_')[1]

	team = [player]
	page = requests.get(url)
	soup = BeautifulSoup(page.text,'html.parser')
	head = soup.find_all(class_="team-name")
	for li in head:
		if li.text not in team:
			team.append(li.text)
	
	update = ('_'.join(team[1:]),player)
	statement = '''
		UPDATE Players
		SET TeamPlayed=?
		WHERE Name=?
	'''
	cur.execute(statement, update)
	conn.commit()
	conn.close()
	return team

# Plot the location for all NBA teams
def plot_all_teams(res):
	lat_vals = []
	lon_vals = []
	text_vals = []

	for t in res:
		lat_vals.append(t.lat)
		lon_vals.append(t.lng)
		text_vals.append(t.name)

	team_loc = [dict(
			type = 'scattergeo',
			locationmode = 'USA-states',
			lon = lon_vals,
			lat = lat_vals,
			text = text_vals,
			mode = 'markers',
			marker = dict(
				size = 8,
				symbol = 'circle',
				color = 'red'
			))]

	layout = dict(
			title = 'Arena Locations of all NBA teams',
			geo = dict(
				scope='usa',
				projection=dict( type='albers usa' ),
				showland = True,
				landcolor = "rgb(250, 208, 89)",
				subunitcolor = "rgb(234, 236, 235)",
				countrycolor = "rgb(0, 208, 89)",
				countrywidth = 3,
				subunitwidth = 3
			),
		)

	fig = dict(data=team_loc, layout=layout )
	py.plot( fig, validate=False, filename='all_teams')       

# Plot game route for a team
def plot_game_route(rival):
	try:
		conn = sqlite3.connect(DBNAME)
		cur = conn.cursor()
	except:
		print('Unable to connect the database.')

	lat_vals_win = []
	lon_vals_win = []
	lat_vals_lose = []
	lon_vals_lose = []
	text_vals_win = []
	text_vals_lose = []

	for i in range(1,len(rival)):
		home = False
		if rival[i].startswith('vs'):
			team=rival[0]
			home =True
		else:
			team=rival[i].split(' ')[2]
		statement = 'SELECT Name, ArenaLocation_lat, ArenaLocation_lng FROM Teams WHERE Name LIKE "%'+team+'%"'
		tmp=cur.execute(statement)
		res=tmp.fetchone()
		
		if home:
			lat = str(float(res[1])+i*0.1)
			lon = str(float(res[2])+i*0.1)
		else:
			lat = res[1]
			lon = res[2]
		
		if rival[i].split(' ')[3] == 'W' or rival[i].split(' ')[4] == 'W':
			lat_vals_win.append(lat)
			lon_vals_win.append(lon)
			text_vals_win.append(rival[i])

		else:
			lat_vals_lose.append(lat)
			lon_vals_lose.append(lon)
			text_vals_lose.append(rival[i])

	win_trace = dict(
				type = 'scattergeo',
				locationmode = 'USA-states',
				lon = lon_vals_win,
				lat = lat_vals_win,
				text = text_vals_win,
				mode = 'markers',
				marker = dict(
					size = 20,
					symbol = 'star',
					color = 'green'
				))

	lose_trace = dict(
			type = 'scattergeo',
			locationmode = 'USA-states',
			lon = lon_vals_lose,
			lat = lat_vals_lose,
			text = text_vals_lose,
			mode = 'markers',
			marker = dict(
				size = 8,
				symbol = 'circle',
				color = 'red'
			))
	plot_data = [win_trace, lose_trace]

	layout = dict(
			title = 'Past 5 game routes for '+rival[0],
			geo = dict(
				scope='usa',
				projection=dict( type='albers usa' ),
				showland = True,
				landcolor = "rgb(250, 208, 89)",
				subunitcolor = "rgb(234, 236, 235)",
				countrycolor = "rgb(0, 208, 89)",
				countrywidth = 3,
				subunitwidth = 3
			),
		)

	fig = dict(data=plot_data, layout=layout )
	py.plot( fig, validate=False, filename='team_route')       

	conn.close()

# Plot teams a player've ever played for
def plot_team_played(team):
	try:
		conn = sqlite3.connect(DBNAME)
		cur = conn.cursor()
	except:
		print('Unable to connect the database.')

	lat_vals_old = []
	lon_vals_old = []
	text_vals_old = []
	lat_vals_now = []
	lon_vals_now = []
	text_vals_now = []

	for i,t in enumerate(team):
		if i == 0:
			continue

		name = team_name[t]
		statement = '''
			SELECT Name, ArenaLocation_lat, ArenaLocation_lng 
			FROM Teams
			WHERE Name=?
		'''
		params = (name,)
		tmp=cur.execute(statement,params)
		res=tmp.fetchone()

		if i == len(team)-1:
			lat_vals_now.append(res[1])
			lon_vals_now.append(res[2])
			text_vals_now.append(res[0])
		else:
			lat_vals_old.append(res[1])
			lon_vals_old.append(res[2])
			text_vals_old.append(res[0])

	now_trace = dict(
				type = 'scattergeo',
				locationmode = 'USA-states',
				lon = lon_vals_now,
				lat = lat_vals_now,
				text = text_vals_now,
				mode = 'markers',
				marker = dict(
					size = 20,
					symbol = 'star',
					color = 'green'
				))

	old_trace = dict(
			type = 'scattergeo',
			locationmode = 'USA-states',
			lon = lon_vals_old,
			lat = lat_vals_old,
			text = text_vals_old,
			mode = 'markers',
			marker = dict(
				size = 8,
				symbol = 'circle',
				color = 'red'
			))
	plot_data = [now_trace, old_trace]

	layout = dict(
			title = 'Teams '+team[0]+' ever played for ',
			geo = dict(
				scope='usa',
				projection=dict( type='albers usa' ),
				showland = True,
				landcolor = "rgb(250, 208, 89)",
				subunitcolor = "rgb(234, 236, 235)",
				countrycolor = "rgb(0, 208, 89)",
				countrywidth = 3,
				subunitwidth = 3
			),
		)

	fig = dict(data=plot_data, layout=layout )
	py.plot( fig, validate=False, filename='team_played')       
  
# Plot histogram for points in last 5 game
def plot_point(point):
	points=[]
	team=[]
	for i,r in enumerate(point):
		if i == 0:
			continue
		if r.startswith('vs'):
			points.append(r.split(' ')[1])
			if r.split(' ')[0] not in team:
				team.append(r.split(' ')[0])
			else:
				team.append(r.split(' ')[0]+str(i))
		else:
			points.append(r.split(' ')[2])
			if r.split(' ')[0]+' '+r.split(' ')[1] not in team:
				team.append(r.split(' ')[0]+' '+r.split(' ')[1])
			else:
				team.append(r.split(' ')[0]+' '+r.split(' ')[1]+str(i))
	
	data=Data([{'y':points,
				'x':team,
				"marker": {"color": "blue", "size": 12},
				"mode": "markers",
				"type": "scatter"}])
	layout = {"title": "Points for "+point[0]+" in past 5 games", 
		  "xaxis": {"title": "Games", }, 
		  "yaxis": {"title": "Points"},
		  "rangemode": 'nonnegative'}

	fig = dict(data=data, layout=layout)
	py.plot( fig, validate=False, filename='point')       
		
if __name__ == '__main__':
	try:
		conn = sqlite3.connect(DBNAME)
		cur = conn.cursor()
	except:
		print('Unable to connect the database.')
	print('\n########################################################')
	print('Welcome to NBA stats search and visualization program!')
	print('For SI507, Winter 2018')
	print('########################################################')

	try:
		statement = 'SELECT * FROM Teams'
		result = cur.execute(statement)
		res = result.fetchall()
		if len(res) > 0:
			choice = str(input('\nDo you want to remove existing data? (yes/no) '))
			if choice == 'yes':
				os.remove('NBA_teams.json')
				os.remove('players.json')
				os.remove('routes.json')
				os.remove('points.json')
				createDatabase()
				print('\nExisting data removed.')

	except:
		createDatabase()

	team = []
	player = []
	route = []
	point = []
	preteam = []

	user_input = str(input('\nEnter command (or "help" for options): '))
	while user_input != 'exit':
		
		if 'help' in user_input: 
			print('''
	list 
		available anytime
		lists all teams in the NBA league
		inputs: no input needed
	route <result_number> 
		available only if there is an active team list set
		lists routes for that team in past 5 games
		valid inputs: an integer 1-len(result_set_size)
	player <result_number>
		available only if there is an active team list set
		lists all players in that NBA team
		valid inputs: an integer 1-len(result_set_size)
	point <result_number> 
		available only if there is an active player list set
		lists points for that player in past 5 games
		valid inputs: an integer 1-len(result_set_size)
	preteam <result_number>
		available only if there is an active player list set
		lists teams a player've ever played for
		valid inputs: an integer 1-len(result_set_size)
	map <data_type>
		available only if there is an active result set
		displays the current results of choosen data type on a map
		valid inputs: team, route, point, preteam
	exit
		exits the program 
	help
		lists available commands (these instructions)''')  
		elif user_input == 'list':
			teamCla = get_all_teams()
			for i,t in enumerate(teamCla):
				print(i+1, t.name)
				team.append(t.name)

		elif user_input.startswith('route'):
			route = []
			try:
				idx = int(user_input.split()[1])
				if len(team)>0 and idx>0 and idx<=len(team):
					target = team[idx-1]
					print('\nRoutes for '+target+' in past 5 games:')
					route = get_team_route(target)
					if len(route)>0:
						for i,r in enumerate(route):
							if i > 0:
								print(i,r)
				else:
					print('No route result for team '+target+'!')
			except:
				print('Please enter an int for a team!')

		elif user_input.startswith('player'):
			player = []
			try:            
				idx = int(user_input.split()[1])
				if len(team)>0 and idx>0 and idx<=len(team):
					target = team[idx-1]
					print('\nPlayers in '+target)
					player = get_players(target)
					if len(player)>0:
						for i,p in enumerate(player):
							print(i+1,p)
				else:
					print('No player result for team '+target+'!')
			except:
				print('Please enter an int for the team!')

		elif user_input.startswith('point'):
			point = []
			try:
				idx = int(user_input.split()[1])
				if len(player)>0 and idx>0 and idx<=len(player):
					pla = player[idx-1]
					print('\nPoints for '+pla+' in past 5 games:')
					point = get_points(pla)
					if len(point)>0:
						for i,p in enumerate(point):
							if i != 0:
								print(i,p)
				else:
					print('No point result for player '+pla+'!')
			except:
				print('Please enter an int for a player!')

		elif user_input.startswith('preteam'):
			preteam = []
			try:
				idx = int(user_input.split()[1])
				if len(player)>0 and idx>0 and idx<=len(player):
					pla = player[idx-1]
					print('\nTeams '+pla+' ever played for:')
					preteam = get_preteam(pla)
					if len(preteam)>0:
						for i,t in enumerate(preteam):
							if i != 0:
								print(i,t)
				else:
					print('No point result for player '+pla+'!')
			except:
				print('Please enter an int for a player!')

		elif user_input.startswith('map'):
			try:
				choosenType = str(user_input.split()[1])
				if len(team)>0 and choosenType=='team':
					plot_all_teams(teamCla)
					print('\nOpened a web page for '+choosenType+'!')
				elif len(route)>0 and choosenType=='route':
					plot_game_route(route)
					print('\nOpened a web page for '+choosenType+'!')
				elif len(point)>0 and choosenType=='point':
					plot_point(point)
					print('\nOpened a web page for '+choosenType+'!')
				elif len(preteam)>0 and choosenType=='preteam':
					plot_team_played(preteam)
					print('\nOpened a web page for '+choosenType+'!')
				else:
					print('No map result for data '+choosenType+'!')
			except:
				print('Please enter a valid data for a visualization!')
		else:
			print('Invalid user input!')

		user_input = str(input('\nEnter command (or "help" for options): '))

	print('\nBye!')

