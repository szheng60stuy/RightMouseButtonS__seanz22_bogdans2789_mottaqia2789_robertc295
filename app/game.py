# Sean Zheng, Mottaqi Abedin, Bogdan Sotnikov, Robert Chen
# RightMouseButtonS
# SoftDev
# P02 -- Makers Makin' It, Act 1
# 12/22/2025

import sqlite3
import random
import math

####################################### SETUP ###################################

def set_game():
	DB_FILE="conquest.db"
	db = sqlite3.connect(DB_FILE)
	c = db.cursor()
	command = 'INSERT INTO games VALUES (?, ?, ?, ?, ?, ?, ?, ?)'
	vars = (0, '', '', '', '', '', '', 0)
	c.execute(command, vars)
	db.commit()
	db.close()

def set_territories():
	map_info = {
    # --- North America ---
    "Alaska": ["North America", "Northwest Territory", "Alberta", "Kamchatka"],
    "Northwest Territory": ["North America", "Alaska", "Alberta", "Ontario", "Greenland"],
    "Greenland": ["North America", "Northwest Territory", "Ontario", "Quebec", "Iceland"],
    "Alberta": ["North America", "Alaska", "Northwest Territory", "Ontario", "Western United States"],
    "Ontario": ["North America", "Northwest Territory", "Greenland", "Quebec", "Eastern United States", "Western United States", "Alberta"],
    "Quebec": ["North America", "Ontario", "Greenland", "Eastern United States"],
    "Western United States": ["North America", "Alberta", "Ontario", "Eastern United States", "Central America"],
    "Eastern United States": ["North America", "Ontario", "Quebec", "Western United States", "Central America"],
    "Central America": ["North America", "Western United States", "Eastern United States", "Venezuela"],

    # --- South America ---
    "Venezuela": ["South America", "Central America", "Brazil", "Peru"],
    "Peru": ["South America", "Venezuela", "Brazil", "Argentina"],
    "Brazil": ["South America", "Venezuela", "Peru", "Argentina", "North Africa"],
    "Argentina": ["South America", "Peru", "Brazil"],

    # --- Europe ---
    "Iceland": ["Europe", "Greenland", "Great Britain", "Scandinavia"],
    "Scandinavia": ["Europe", "Iceland", "Northern Europe", "Ukraine"],
    "Great Britain": ["Europe", "Iceland", "Scandinavia", "Northern Europe", "Western Europe"],
    "Northern Europe": ["Europe", "Great Britain", "Scandinavia", "Ukraine", "Southern Europe", "Western Europe"],
    "Western Europe": ["Europe", "Great Britain", "Northern Europe", "Southern Europe", "North Africa"],
    "Southern Europe": ["Europe", "Western Europe", "Northern Europe", "Ukraine", "Middle East", "Egypt"],

    # --- Africa ---
    "North Africa": ["Africa", "Brazil", "Western Europe", "Southern Europe", "Egypt", "East Africa", "Congo"],
    "Egypt": ["Africa", "North Africa", "Southern Europe", "Middle East", "East Africa"],
    "East Africa": ["Africa", "Egypt", "North Africa", "Congo", "South Africa", "Madagascar", "Middle East"],
    "Congo": ["Africa", "North Africa", "East Africa", "South Africa"],
    "South Africa": ["Africa", "Congo", "East Africa", "Madagascar"],
    "Madagascar": ["Africa", "South Africa", "East Africa"],

    # --- Asia ---
    "Ural": ["Asia", "Ukraine", "Siberia", "China", "Afghanistan"],
    "Siberia": ["Asia", "Ural", "Yakutsk", "Irkutsk", "Mongolia", "China"],
    "Yakutsk": ["Asia", "Siberia", "Irkutsk", "Kamchatka"],
    "Kamchatka": ["Asia", "Yakutsk", "Irkutsk", "Mongolia", "Japan", "Alaska"],
    "Irkutsk": ["Asia", "Siberia", "Yakutsk", "Kamchatka", "Mongolia"],
    "Mongolia": ["Asia", "Siberia", "Irkutsk", "Kamchatka", "Japan", "China"],
    "Japan": ["Asia", "Kamchatka", "Mongolia"],
    "Afghanistan": ["Asia", "Ukraine", "Ural", "China", "India", "Middle East"],
    "Middle East": ["Asia", "Southern Europe", "Egypt", "East Africa", "Afghanistan", "India"],
    "India": ["Asia", "Middle East", "Afghanistan", "China", "Siam"],
    "China": ["Asia", "Ural", "Siberia", "Mongolia", "India", "Siam", "Afghanistan"],
    "Siam": ["Asia", "India", "China", "Indonesia"],
    "Ukraine": ["Asia", "Scandinavia", "Northern Europe", "Southern Europe", "Ural", "Afghanistan"],

    # --- Australia ---
    "Indonesia": ["Australia", "Siam", "New Guinea", "Western Australia"],
    "New Guinea": ["Australia", "Indonesia", "Western Australia", "Eastern Australia"],
    "Western Australia": ["Australia", "Indonesia", "New Guinea", "Eastern Australia"],
    "Eastern Australia": ["Australia", "Western Australia", "New Guinea"]
	}

	DB_FILE="conquest.db"
	db = sqlite3.connect(DB_FILE)
	c = db.cursor()
	ID = 0
	for territory in map_info:
		connected = map_info[territory][1:]
		connectedstr = ""
		for plot in connected:
			connectedstr += plot + ", "
		command = 'INSERT INTO territories VALUES (?, ?, ?, ?, ?)'
		vars = (ID, territory, connectedstr[0:len(connectedstr) - 2], str(map_info[territory][0]), 0)
		c.execute(command, vars)
		ID += 1
	db.commit()
	db.close()

def make_tables():
    DB_FILE="conquest.db"
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS territories (
            id INTEGER PRIMARY KEY NOT NULL,
            name TEXT NOT NULL,
            connected TEXT NOT NULL,
            Cgroup TEXT NOT NULL,
            armies INTEGER NOT NULL
        )"""
    )
    c.execute("DROP TABLE IF EXISTS games")
    c.execute("""
        CREATE TABLE IF NOT EXISTS games (
            armies INTEGER NOT NULL,
            p1 TEXT NOT NULL,
            p2 TEXT NOT NULL,
            p3 TEXT NOT NULL,
            p4 TEXT NOT NULL,
            p5 TEXT NOT NULL,
            p6 TEXT NOT NULL,
            turn INTEGER NOT NULL
        )"""
    ) # id maybe needed? armies in the format by players 23, 42, 23, 0, 0, 0 means 3 players are left, turn here if we need it
      # p1, p2, ... are just the territories each player owns
    c.execute("""
    	CREATE TABLE IF NOT EXISTS users(
    		username TEXT PRIMARY KEY NOT NULL,
    		password TEXT NOT NULL,
    		games INTEGER
    	)"""
    )

    count = c.execute(f'SELECT COUNT(id) FROM territories').fetchone()[0]

    db.commit()
    db.close()

    if count != 42:
    	print("territories info made!")
    	set_territories()

####################### GAME LOGIC HELPER FUNCTIONS ####################################

def addTerritory(territory, player, army): #adds # of army to a territory and updates it to the player in games db
	DB_FILE="conquest.db"
	db = sqlite3.connect(DB_FILE)
	c = db.cursor()
	current = c.execute("SELECT armies FROM territories WHERE name = ?", (territory, )).fetchone()[0]
	c.execute("UPDATE territories SET armies = ? WHERE name = ?", (current + army, territory))
	if player == 1:
		current = c.execute(f'SELECT p1 FROM games').fetchone()[0].split(', ')
		if current[0] == '':
			current[0] = territory.strip()
		else:
			current.append(territory.strip())
		ownedplot = ""
		for plot in current:
			ownedplot += plot + ", "
		c.execute("UPDATE games SET p1 = ?", (ownedplot[0: len(ownedplot) - 2], ))
	if player == 2:
		current = c.execute(f'SELECT p2 FROM games').fetchone()[0].split(', ')
		if current[0] == '':
			current[0] = territory
		ownedplot = ""
		for plot in current:
			ownedplot += plot + ", "
		c.execute("UPDATE games SET p2 = ?", (current[0: len(ownedplot) - 2]))
	if player == 3:
		current = c.execute(f'SELECT p3 FROM games').fetchone()[0].split(', ')
		if current[0] == '':
			current[0] = territory
		ownedplot = ""
		for plot in current:
			ownedplot += plot + ", "
		c.execute("UPDATE games SET p3 = ?", (current[0: len(ownedplot) - 2]))
	if player == 4:
		current = c.execute(f'SELECT p4 FROM games').fetchone()[0].split(', ')
		if current[0] == '':
			current[0] = territory
		ownedplot = ""
		for plot in current:
			ownedplot += plot + ", "
		c.execute("UPDATE games SET p4 = ?", (current[0: len(ownedplot) - 2]))
	if player == 5:
		current = c.execute(f'SELECT p5 FROM games').fetchone()[0].split(', ')
		if current[0] == '':
			current[0] = territory
		ownedplot = ""
		for plot in current:
			ownedplot += plot + ", "
		c.execute("UPDATE games SET p5 = ?", (current[0: len(ownedplot) - 2]))
	if player == 6:
		current = c.execute(f'SELECT p6 FROM games').fetchone()[0].split(', ')
		if current[0] == '':
			current[0] = territory
		ownedplot = ""
		for plot in current:
			ownedplot += plot + ", "
		c.execute("UPDATE games SET p6 = ?", (current[0: len(ownedplot) - 2]))
	db.commit()
	db.close()


def availableSet(): #returns list of territories still unoccupied
	DB_FILE="conquest.db"
	db = sqlite3.connect(DB_FILE)
	c = db.cursor()
	result = []
	unoccupied= c.execute(f'SELECT name FROM territories WHERE armies = 0').fetchall()
	for name in unoccupied:
		result.append(name[0])
	db.commit()
	db.close()
	return result

def flatten(nestList):
	lst = []
	for thing in nestList:
		if isinstance(thing, list): #checks if thing is a list
			lst.extend(flatten(thing)) #extend just connects two lists together
		else:
			lst.append(thing)
	return lst

def aMoveHelp(territory, player, tried): #helper function for availableMove
	DB_FILE="conquest.db"
	db = sqlite3.connect(DB_FILE)
	c = db.cursor()
	if check(territory, player) == False:
		print("this territory doesnt belong to this player")
		return None
	result = [territory]
	connects = c.execute(f'SELECT connected FROM territories WHERE name = ?', (territory, )).fetchone()[0].split(', ')
	#print("possible: ")
	#print(connects)
	#print("tried: ")
	#print(tried)
	for connect in connects:
		if connect in tried:
			connects.remove(connect)
	for connect in connects:
		if connect not in tried:
			tried.append(connect)
			#print(connect)
			if check(connect, player):
				#print(connect + " made it")
				result.append(aMoveHelp(connect, player, tried))
	db.commit()
	db.close()
	return result

def availableMove(territory, player): #returns list of territories available for movement given a chosen territory and player
	nestedList = aMoveHelp(territory, player, [territory]) #this returns a nested list like ['Northwest Territory', ['Alaska'], ['Ontario', ['Greenland', ['Iceland']], ['Western United States']]]
	return flatten(nestedListcontBonus)

def attackTerritory(territory, player, origin):
	DB_FILE="conquest.db"
	db = sqlite3.connect(DB_FILE)
	c = db.cursor()
	if (origin in c.execute(f'SLECT connected FROM territories WHERE name = {territory}')):
		if (random.randint(0,1) == 1): #attack success
			armiesOrig = c.execute(f'SELECT armies FROM territories WHERE name = {origin}')-1
			if (armiesOrig<1):
				armiesOrig = c.execute(f'SELECT armies FROM territories WHERE name = {origin}')-1
				c.execute(f'UPDATE territories SET armies = 1 WHERE name = {origin}')
				#SEAN ADD CODE TO CHANGE OWNERSHIP OF TARGET TERRITORY
			c.execute(f'UPDATE territories SET armies = {armiesOrig} WHERE name = {territory}')
		else: #attack fail
			c.execute(f"UPDATE territories SET armies = {c.execute(f'SELECT armies FROM territories WHERE name = {origin}')-1} WHERE name = {origin}")


def check(territory, player): #checks if given player owns that territory
	DB_FILE="conquest.db"
	db = sqlite3.connect(DB_FILE)
	c = db.cursor()
	if player == 1:
		check = c.execute(f'SELECT p1 FROM games').fetchone()[0].split(', ')
	if player == 2:
		check = c.execute(f'SELECT p2 FROM games').fetchone()[0].split(', ')
	if player == 3:
		check = c.execute(f'SELECT p3 FROM games').fetchone()[0].split(', ')
	if player == 4:
		check = c.execute(f'SELECT p4 FROM games').fetchone()[0].split(', ')
	if player == 5:
		check = c.execute(f'SELECT p5 FROM games').fetchone()[0].split(', ')
	if player == 6:
		check = c.execute(f'SELECT p6 FROM games').fetchone()[0].split(', ')
	db.commit()
	db.close()
	if territory in check:
		return True
	else:
		return False

def availableAttack(player): #returns list of territories the player can attack
	DB_FILE="conquest.db"
	db = sqlite3.connect(DB_FILE)
	c = db.cursor()
	result = []
	tried = []
	owned = c.execute(f'SELECT p1 FROM games').fetchone()[0].split(', ')
	for plot in owned:
		army = c.execute("SELECT armies FROM territories WHERE name = ?", (plot, )).fetchone()[0]
		if army > 1:
			connects = c.execute(f'SELECT connected FROM territories WHERE name = ?', (plot, )).fetchone()[0].split(', ')
			for connect in connects:
				if connect not in tried and connect not in result and connect not in owned:
					result.append(connect)
				if connect not in tried:
					tried.append(connect)
		if plot not in tried:
			tried.append(plot)
	db.commit()
	db.close()
	return result

def addArmy(player): #adds army
	DB_FILE="conquest.db"
	db = sqlite3.connect(DB_FILE)
	c = db.cursor()
	if player == 1:
		owned = c.execute("SELECT p1 FROM games").fetchone()[0].split(', ')
	if player == 2:
		owned = c.execute(f'SELECT p2 FROM games').fetchone()[0].split(', ')
	if player == 3:
		owned = c.execute(f'SELECT p3 FROM games').fetchone()[0].split(', ')
	if player == 4:
		owned = c.execute(f'SELECT p4 FROM games').fetchone()[0].split(', ')
	if player == 5:
		owned = c.execute(f'SELECT p5 FROM games').fetchone()[0].split(', ')
	if player == 6:
		owned = c.execute(f'SELECT p6 FROM games').fetchone()[0].split(', ')
	added = math.floor(len(owned) / 3);
	# bonus groups
	northA = c.execute(f'SELECT name FROM territories WHERE group = ?', ("North America", )).fetchone()[0].split(', ')
	southA = c.execute(f'SELECT name FROM territories WHERE group = ?', ("South America", )).fetchone()[0].split(', ')
	eu = c.execute(f'SELECT name FROM territories WHERE group = ?', ("Europe", )).fetchone()[0].split(', ')
	africa = c.execute(f'SELECT name FROM territories WHERE group = ?', ("Africa", )).fetchone()[0].split(', ')
	asia = c.execute(f'SELECT name FROM territories WHERE group = ?', ("Asia", )).fetchone()[0].split(', ')
	aus = c.execute(f'SELECT name FROM territories WHERE group = ?', ("Australia", )).fetchone()[0].split(', ')
	groups = [northA, southA, eu, africa, asia, aus]
#print(contBonus(1))
#print(availableMove("Northwest Territory", 1))
#print(availableAttack(1))
#print(check("Greenland", 1))
#print(availableSet())
