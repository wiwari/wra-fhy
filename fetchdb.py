#!/usr/bin/env python
import sqlite3



if __name__=='__main__':
	print("MAIN")

	connection = sqlite3.connect('data/fhy-reservoir.db')

	cursor = connection.cursor()

	commandInitDaily = """
	CREATE TABLE IF NOT EXISTS
	"daily" (
		"StationNo"	INTEGER NOT NULL,
		"Time"	TEXT NOT NULL,
		"InflowTotal"	REAL,
		"OutflowTotal"	REAL,
		PRIMARY KEY("StationNo","Time")
	);"""

	cursor.execute(commandInitDaily)

	commandInitStation = """
	CREATE TABLE IF NOT EXISTS
	"station" (
		"StationNo"	INTEGER NOT NULL,
		"StationName"	TEXT NOT NULL,
		"Latitude"	REAL,
		"Longitude"	REAL,
		"BasinNo"	TEXT,
		"BasinName"	TEXT,
		"HydraulicConstruction"	INTEGER,
		"CityCode"	TEXT,
		"FullWaterHeight"	REAL,
		"DeadWaterHeight"	REAL,
		"Storage"	REAL,
		"ProtectionFlood"	INTEGER,
		"Importance"	INTEGER,
		PRIMARY KEY("StationNo")
	);
	"""

	cursor.execute(commandInitStation)


	connection.close()