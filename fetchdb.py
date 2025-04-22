#!/usr/bin/env python
from array import array
from ast import FormattedValue, arg
# from mimetypes import init
import sqlite3
import ssl
import urllib.request, json 
# import collections
import argparse

class fetchdb:	
	def __init__(self,file) -> None:
		self.connection=sqlite3.connect(file)
		self.initDbStation()
		self.initDbDaily()
	
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
		self.connection.commit()

	def initDbDaily(self):
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
		self.connection.commit()

	def replaceStation(self,data):
		"""update station from data"""
		commandReplaceStation="""
		INSERT OR REPLACE INTO station(StationNo,StationName,Latitude,Longitude,BasinNo,BasinName,HydraulicConstruction	,CityCode,FullWaterHeight,DeadWaterHeight,Storage,ProtectionFlood,Importance)
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

	def qeuryDailyJSON(self):		
		commandQueryDaily="""
		select  station.StationName, daily.StationNo, max(daily.Time) as Time, daily.InflowTotal, daily.OutflowTotal from daily join station on  daily.StationNo = station.StationNo 
		group by daily.StationNo ORDER by daily.StationNo
		;
		"""
		cur=self.connection.cursor()
		rows = cur.execute(commandQueryDaily).fetchall()
		objects_list = []	
		# -----------------	
		# for row in rows:
		# 	d = collections.OrderedDict()
		# 	d["StationName"] = row[0]
		# 	d["StationNo"] = row[1]
		# 	d["Time"] = row[2]
		# 	d["InflowTotal"] = row[3]
		# 	d["OutflowTotal"] = row[4]
		# 	objects_list.append(d)
		# -----------------
		# self.connection.commit()
		
		# for i, element in enumerate(rows[0]):
		# 	print(i, element)
		
		
		objects_list = [dict((cur.description[i][0], value) \
			for i, value in enumerate(row)) for row in rows]

		return json.dumps(objects_list, ensure_ascii=False)

	def qeuryDailyStationList(self):
		# get most updating StationNo		
		commandQueryDaily="""
		SELECT r.StationNo 
		from (select  StationNo ,max(julianday(Time)) as d from daily 
 		group by StationNo ORDER by StationNo ) as r  where d > julianday('now','-7 days');
		
		"""
		cur=self.connection.cursor()
		rows = cur.execute(commandQueryDaily).fetchall()
		objects_list = []	
		# -----------------	
		# for row in rows:
		# 	d = collections.OrderedDict()
		# 	d["StationName"] = row[0]
		# 	d["StationNo"] = row[1]
		# 	d["Time"] = row[2]
		# 	d["InflowTotal"] = row[3]
		# 	d["OutflowTotal"] = row[4]
		# 	objects_list.append(d)
		# -----------------
		# self.connection.commit()
		
		# for i, element in enumerate(rows[0]):
		# 	print(i, element)
		
		objects_list = [{"StationNoList":[row[0] for row in rows]}]

		return json.dumps(objects_list, ensure_ascii=False)		

	def fhyStation(self):
		ctx = ssl.create_default_context(cafile="certs/fhy-wra-gov-tw-chain.pem")
		with urllib.request.urlopen("https://fhy.wra.gov.tw/WraApi/v1/Reservoir/Station?$orderby=StationNo%20asc", context=ctx) as url:
			data = json.loads(url.read().decode())
			print("Station總站數: " , len(data))
			# data.sort(key=lambda x: x["StationNo"])
			return data

	def fhyDaily(self):
		ctx = ssl.create_default_context(cafile="certs/fhy-wra-gov-tw-chain.pem")
		with urllib.request.urlopen("https://fhy.wra.gov.tw/WraApi/v1/Reservoir/Daily?$orderby=StationNo%20asc", context=ctx) as url:
			data = json.loads(url.read().decode())
			print("Daily總站數: " , len(data))
			# data.sort(key=lambda x: x["StationNo"])
			return data

	def dailyUpdate(self):		
		daily=self.fhyDaily()
		# update fhy daily data
		for element in daily:
			vls = [element['StationNo'], element['Time'] ]
			vls.append(element['InflowTotal'] if ("InflowTotal" in element) else None)
			vls.append(element['OutflowTotal'] if ("OutflowTotal" in element) else None)
			self.replaceDaily(vls)

	def stationUpdate(self):
		station=self.fhyStation()
		# update fhy station info
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
			self.replaceStation(vl)

	def daily2json(self):
		res=self.qeuryDailyJSON()
		# print(res)
		print(res)

	def dailyStaList2json(self):
		res=self.qeuryDailyStationList()
		# print(res)
		print(res)


	def update(self):
		self.dailyUpdate()
		self.stationUpdate()

if __name__=='__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument("--db", help='sqlite database path', default='data/fhy-reservoir.db')
	parser.add_argument("--update", help="fetch data with WRA FHY API and update database ", action='store_true')
	parser.add_argument("--json", help="write latest daily data into JSON file", action='store_true')
	parser.add_argument("--stalist", help="write active StationNo list of JSON file", action='store_true')
	# parser.add_argument("--test", help="test", action='store_true')
	args = parser.parse_args()
	
	fd=fetchdb(args.db)	 # default SQLite3 DB path: "data/fhy-reservoir.db"
	if args.update:
		print("updating...")
		fd.update()
	if args.json:
		fd.daily2json()
	if args.stalist:
		fd.dailyStaList2json()
	# if args.test:	
	# 	print(fd.fhyDaily())	
	# 	print("test")	
		
	fd.close()


