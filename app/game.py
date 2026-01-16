# Sean Zheng, Mottaqi Abedin, Bogdan Sotnikov, Robert Chen
# RightMouseButtonS
# SoftDev
# P02 -- Makers Makin' It, Act 1
# 12/22/2025

import sqlite3
import random
import math

####################################### SETUP ###################################

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
    "Middle East": ["Asia", "Southern Europe", "Egypt", "East Africa", "Afghanistan", "India", "Ukraine"],
    "India": ["Asia", "Middle East", "Afghanistan", "China", "Siam"],
    "China": ["Asia", "Ural", "Siberia", "Mongolia", "India", "Siam", "Afghanistan"],
    "Siam": ["Asia", "India", "China", "Indonesia"],
    "Ukraine": ["Asia", "Scandinavia", "Northern Europe", "Southern Europe", "Ural", "Afghanistan", "Middle East"],

    # --- Australia ---
    "Indonesia": ["Australia", "Siam", "New Guinea", "Western Australia"],
    "New Guinea": ["Australia", "Indonesia", "Western Australia", "Eastern Australia"],
    "Western Australia": ["Australia", "Indonesia", "New Guinea", "Eastern Australia"],
    "Eastern Australia": ["Australia", "Western Australia", "New Guinea"]
}


def set_game():
	DB_FILE="conquest.db"
	db = sqlite3.connect(DB_FILE)
	c = db.cursor()
	command = 'INSERT INTO games VALUES (?, ?, ?, ?, ?, ?, ?, ?)'
	vars = ('0, 0, 0, 0, 0, 0', '', '', '', '', '', '', 0)
	c.execute(command, vars)
	db.commit()
	db.close()

def set_territories():
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
    c.execute("DROP TABLE IF EXISTS territories")
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
            armies TEXT NOT NULL,
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
    		password TEXT NOT NULL
    	)"""
    )

    count = c.execute('SELECT COUNT(id) FROM territories').fetchone()[0]

    db.commit()
    db.close()

    if count != 42:
    	print("territories info made!")
    	set_territories()

####################### GAME LOGIC HELPER FUNCTIONS ####################################

def addTerritory(home, territory, player, army): #adds # of army to a territory and updates it to the player in games db, home is the territory moving armies from
	DB_FILE="conquest.db"
	db = sqlite3.connect(DB_FILE)
	c = db.cursor()
	adding = True
	if home != None:
		current = c.execute("SELECT armies FROM territories WHERE name = ?", (home, )).fetchone()[0]
		if current > 1:
			print(home)
			print(territory)
			c.execute("UPDATE territories SET armies = ? WHERE name = ?", (current - army, home))
			current = c.execute("SELECT armies FROM territories WHERE name = ?", (territory, )).fetchone()[0]
			print(current)
			c.execute("UPDATE territories SET armies = ? WHERE name = ?", (current + army, territory))
		else:
			adding = False
	if home == None:
		current = c.execute("SELECT armies FROM territories WHERE name = ?", (territory, )).fetchone()[0]
		c.execute("UPDATE territories SET armies = ? WHERE name = ?", (current + army, territory))
		armies = c.execute('SELECT armies FROM games').fetchone()[0].split(', ')
		armies[player - 1] = str(int(armies[player - 1]) - army)
		update = ""
		for army in armies:
			update += army
			update += ", "
		c.execute("UPDATE games SET armies = ?", (update, ))
	if adding:
		if player == 1:
			current = c.execute('SELECT p1 FROM games').fetchone()[0].split(', ')
			if current[0] == '':
				current[0] = territory.strip()
			elif territory not in current:
				current.append(territory.strip())
			ownedplot = ""
			for plot in current:
				ownedplot += plot + ", "
			c.execute("UPDATE games SET p1 = ?", (ownedplot[0: len(ownedplot) - 2], ))
		if player == 2:
			current = c.execute('SELECT p2 FROM games').fetchone()[0].split(', ')
			if current[0] == '':
				current[0] = territory.strip()
			elif territory not in current:
				current.append(territory.strip())
			ownedplot = ""
			for plot in current:
				ownedplot += plot + ", "
			c.execute("UPDATE games SET p2 = ?", (ownedplot[0: len(ownedplot) - 2], ))
		if player == 3:
			current = c.execute('SELECT p3 FROM games').fetchone()[0].split(', ')
			if current[0] == '':
				current[0] = territory.strip()
			elif territory not in current:
				current.append(territory.strip())
			ownedplot = ""
			for plot in current:
				ownedplot += plot + ", "
			c.execute("UPDATE games SET p3 = ?", (ownedplot[0: len(ownedplot) - 2], ))
		if player == 4:
			current = c.execute('SELECT p4 FROM games').fetchone()[0].split(', ')
			if current[0] == '':
				current[0] = territory.strip()
			elif territory not in current:
				current.append(territory.strip())
			ownedplot = ""
			for plot in current:
				ownedplot += plot + ", "
			c.execute("UPDATE games SET p4 = ?", (ownedplot[0: len(ownedplot) - 2], ))
		if player == 5:
			current = c.execute('SELECT p5 FROM games').fetchone()[0].split(', ')
			if current[0] == '':
				current[0] = territory.strip()
			elif territory not in current:
				current.append(territory.strip())
			ownedplot = ""
			for plot in current:
				ownedplot += plot + ", "
			c.execute("UPDATE games SET p5 = ?", (ownedplot[0: len(ownedplot) - 2], ))
		if player == 6:
			current = c.execute('SELECT p6 FROM games').fetchone()[0].split(', ')
			if current[0] == '':
				current[0] = territory.strip()
			elif territory not in current:
				current.append(territory.strip())
			ownedplot = ""
			for plot in current:
				ownedplot += plot + ", "
			c.execute("UPDATE games SET p6 = ?", (ownedplot[0: len(ownedplot) - 2], ))
		db.commit()
		db.close()
		print("territory added")


def availableSet(): #returns list of territories still unoccupied
	DB_FILE="conquest.db"
	db = sqlite3.connect(DB_FILE)
	c = db.cursor()
	result = []
	unoccupied= c.execute('SELECT name FROM territories WHERE armies = 0').fetchall()
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
	connects = c.execute('SELECT connected FROM territories WHERE name = ?', (territory, )).fetchone()[0].split(', ')
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
	return flatten(nestedList[1:])

def attackTerritory(territory, attacker, origin):
    DB_FILE="conquest.db"
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()

    def get_player_list(p):
        s = c.execute(f"SELECT p{p} FROM games").fetchone()[0]
        return [x.strip() for x in s.split(",") if x.strip()]

    def set_player_list(p, lst):
        c.execute(f"UPDATE games SET p{p} = ?", (", ".join(lst),))

    defender = 0
    outcome = False
    captured = False

    for i in range(6):
        if check(territory, i + 1):
            defender = i + 1

    # if not attackable, just return
    if territory not in availableAttack(origin, attacker) or defender == 0:
        db.commit()
        db.close()
        return {"outcome": False, "captured": False}

    defendArmy = c.execute("SELECT armies FROM territories WHERE name = ?", (territory,)).fetchone()[0]
    attackArmy = c.execute("SELECT armies FROM territories WHERE name = ?", (origin,)).fetchone()[0]

    if attackArmy < 2:
        db.commit()
        db.close()
        return {"outcome": False, "captured": False}

    if random.randint(0,10) > 4:  # success
        outcome = True
        defendArmy -= 1

        if defendArmy == 0:
            captured = True

            # transfer ownership
            att_list = get_player_list(attacker)
            if territory not in att_list:
                att_list.append(territory)
            set_player_list(attacker, att_list)

            def_list = get_player_list(defender)
            if territory in def_list:
                def_list.remove(territory)
            set_player_list(defender, def_list)

            # move 1 troop in
            c.execute("UPDATE territories SET armies = ? WHERE name = ?", (1, territory))
            attackArmy -= 1
            c.execute("UPDATE territories SET armies = ? WHERE name = ?", (attackArmy, origin))
        else:
            # defender survives
            c.execute("UPDATE territories SET armies = ? WHERE name = ?", (defendArmy, territory))

    else:  # fail
        attackArmy -= 1
        c.execute("UPDATE territories SET armies = ? WHERE name = ?", (attackArmy, origin))

    db.commit()
    db.close()
    return {"outcome": outcome, "captured": captured}



def check(territory, player): #checks if given player owns that territory
	DB_FILE="conquest.db"
	db = sqlite3.connect(DB_FILE)
	c = db.cursor()
	if player == 1:
		check = c.execute('SELECT p1 FROM games').fetchone()[0].split(', ')
	if player == 2:
		check = c.execute('SELECT p2 FROM games').fetchone()[0].split(', ')
	if player == 3:
		check = c.execute('SELECT p3 FROM games').fetchone()[0].split(', ')
	if player == 4:
		check = c.execute('SELECT p4 FROM games').fetchone()[0].split(', ')
	if player == 5:
		check = c.execute('SELECT p5 FROM games').fetchone()[0].split(', ')
	if player == 6:
		check = c.execute('SELECT p6 FROM games').fetchone()[0].split(', ')
	db.commit()
	db.close()
	if territory in check:
		return True
	else:
		return False

def availableAttack(territory, player): #returns list of territories the player can attack
	DB_FILE="conquest.db"
	db = sqlite3.connect(DB_FILE)
	c = db.cursor()
	result = []
	tried = []
	if player == 1:
		owned = c.execute('SELECT p1 FROM games').fetchone()[0].split(', ')
	if player == 2:
		owned = c.execute('SELECT p2 FROM games').fetchone()[0].split(', ')
	if player == 3:
		owned = c.execute('SELECT p3 FROM games').fetchone()[0].split(', ')
	if player == 4:
		owned = c.execute('SELECT p4 FROM games').fetchone()[0].split(', ')
	if player == 5:
		owned = c.execute('SELECT p5 FROM games').fetchone()[0].split(', ')
	if player == 6:
		owned = c.execute('SELECT p6 FROM games').fetchone()[0].split(', ')
	army = c.execute("SELECT armies FROM territories WHERE name = ?", (territory, )).fetchone()[0]
	if army > 1:
		connects = c.execute('SELECT connected FROM territories WHERE name = ?', (territory, )).fetchone()[0].split(', ')
		for connect in connects:
			if connect not in tried and connect not in result and connect not in owned:
				result.append(connect)
			if connect not in tried:
				tried.append(connect)
	db.commit()
	db.close()
	return result

def addArmy(player):  # adds reinforcements to that player's pool
    DB_FILE = "conquest.db"
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()

    # territories owned by player (stored as ", " separated)
    owned_str = c.execute(f"SELECT p{player} FROM games").fetchone()[0]
    owned = [x.strip() for x in owned_str.split(",") if x.strip()]

    # base reinforcements: floor(n/3), minimum 3 if player owns anything
    base = (len(owned) // 3)
    if len(owned) > 0 and base < 3:
        base = 3

    # continent bonuses
    bonuses = {
        "North America": 5,
        "South America": 2,
        "Europe": 5,
        "Africa": 3,
        "Asia": 7,
        "Australia": 2,
    }

    bonus = 0
    for cont, val in bonuses.items():
        rows = c.execute("SELECT name FROM territories WHERE Cgroup = ?", (cont,)).fetchall()
        terrs = [r[0] for r in rows]
        if terrs and all(t in owned for t in terrs):
            bonus += val

    added = base + bonus

    # update games.armies pool string
    armies_str = c.execute("SELECT armies FROM games").fetchone()[0]
    pools = [int(x.strip()) for x in armies_str.split(",") if x.strip() != ""]
    while len(pools) < 6:
        pools.append(0)

    pools[player - 1] += added

    c.execute("UPDATE games SET armies = ?", (", ".join(str(x) for x in pools),))
    db.commit()
    db.close()

    return added

def getMapInfo() -> dict:
	out = {}
	for territory, info in map_info.items():
		if not info:
			continue
		out[territory] = {"continent": info[0], "neighbors": info[1:]}
	return out

def getNeighbors(territory):
	info = map_info.get(territory, [])
	return info[1:]  # return neighbors excluding the continent name

def getPlayers():
	DB_FILE="conquest.db"
	db = sqlite3.connect(DB_FILE)
	c = db.cursor()
	result = c.execute('SELECT armies FROM games').fetchone()[0].split(', ')
	return result

