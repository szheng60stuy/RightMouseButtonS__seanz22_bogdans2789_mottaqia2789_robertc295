# Sean Zheng, Mottaqi Abedin, Bogdan Sotnikov, Robert Chen
# RightMouseButtonS
# SoftDev
# P02 -- Makers Makin' It, Act 1
# 12/22/2025

import sqlite3

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
		command = 'INSERT INTO territories VALUES (?, ?, ?, ?, ?)'
		vars = (ID, territory, str(map_info[territory][1:]), str(map_info[territory][0]), 0)
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
    c.execute("""
        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY NOT NULL, 
            armies INTEGER NOT NULL, 
            turn INTEGER NOT NULL 
        )"""
    ) # id maybe needed? armies in the format by players [23, 42, 23, 0, 0, 0] means 3 players are left, turn here if we need it
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
