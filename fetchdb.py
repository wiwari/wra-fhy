#!/usr/bin/env python
from ast import FormattedValue
from mimetypes import init
import sqlite3
import urllib.request, json 


class fetchdb:	
	def __init__(self,file) -> None:
		self.connection=sqlite3.connect(file)
		self.initDbStation()
		self.iniDbDaily()
	
	def close(self):
		self.connection.close()

	def initDbStation(self):
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
		self.connection.cursor().execute(commandInitStation)

	def iniDbDaily(self):
		commandInitDaily = """
		CREATE TABLE IF NOT EXISTS
		"daily" (
			"StationNo"	INTEGER NOT NULL,
			"Time"	TEXT NOT NULL,
			"InflowTotal"	REAL,
			"OutflowTotal"	REAL,
			PRIMARY KEY("StationNo","Time")
		);"""
		self.connection.cursor().execute(commandInitDaily)
	def replaceStation(self,data):
		commandReplaceStation="""
		INSERT OR REPLACE INTO station("StationNo","StationName","Latitude"	,"Longitude"	,"BasinNo"	,"BasinName"	,"HydraulicConstruction"	,"CityCode","FullWaterHeight","DeadWaterHeight","Storage","ProtectionFlood","Importance")
		VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?);
		"""
		self.connection.cursor().execute(commandReplaceStation,data)
		self.connection.commit()
	def replaceDaily(self,data):
		commandReplaceDaily="""
		INSERT OR REPLACE INTO daily(StationNo,Time,InflowTotal,OutflowTotal)
		VALUES(?,?,?,?);
		"""
		self.connection.cursor().execute(commandReplaceDaily,data)
		self.connection.commit()

def fhyDaily():
	with urllib.request.urlopen("https://fhy.wra.gov.tw/WraApi/v1/Reservoir/Daily?") as url:
		data = json.loads(url.read().decode())
		print("Daily總站數: " , len(data))
		data.sort(key=lambda x: x["StationNo"])
		return data

def fhyStation():
	with urllib.request.urlopen("https://fhy.wra.gov.tw/WraApi/v1/Reservoir/Station?") as url:
		data = json.loads(url.read().decode())
		print("Station總站數: " , len(data))
		data.sort(key=lambda x: x["StationNo"])
		return data
	
if __name__=='__main__':
	
	fd=fetchdb('data/fhy-reservoir.db')	
	daily=fhyDaily()
	station=fhyStation()
	for element in daily:
		vls = [element['StationNo'], element['Time'] ]
		vls.append(element['InflowTotal'] if ("InflowTotal" in element) else None)
		vls.append(element['OutflowTotal'] if ("OutflowTotal" in element) else None)
		fd.replaceDaily(vls)
	for element in station:
		vl = [element['StationNo']]
		vl.append(element['StationName'])
		vl.append(element['Latitude'] if ("Latitude" in element) else None)
		vl.append(element['Longitude'] if ("Longitude" in element) else None)
		vl.append(element['BasinNo'] if ("BasinNo" in element) else None)
		vl.append(element['BasinName'] if ("BasinName" in element) else None)
		vl.append(element['HydraulicConstruction'] if ("HydraulicConstruction" in element) else None)
		vl.append(element['CityCode'] if ("CityCode" in element) else None)
		vl.append(element['FullWaterHeight'] if ("FullWaterHeight" in element) else None)
		vl.append(element['DeadWaterHeight'] if ("DeadWaterHeight" in element) else None)
		vl.append(element['Storage'] if ("Storage" in element) else None)
		vl.append(element['ProtectionFlood'] if ("ProtectionFlood" in element) else None)
		vl.append(element['Importance'] if ("Importance" in element) else None)
		fd.replaceStation(vl)
	fd.close()

