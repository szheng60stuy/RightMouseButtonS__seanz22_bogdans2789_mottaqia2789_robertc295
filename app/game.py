# Sean Zheng, Mottaqi Abedin, Bogdan Sotnikov, Robert Chen
# RightMouseButtonS
# SoftDev
# P02 -- Makers Makin' It, Act 1
# 12/22/2025

import sqlite3

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
    db.commit()
    db.close()

def set_territories():
	DB_FILE="risk.db"
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    c.execute("""

    	)"""
    )
    db.commit()
    db.close()