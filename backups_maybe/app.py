# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt

# from matplotlib import style
# style.use('fivethirtyeight')
# import matplotlib.pyplot as plt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurements = Base.classes.measurement
Stations = Base.classes.station

# Create our session (link) from Python to the DB



#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f'Enter a "(start date)" or a "(start date) / (end date)" for temps during those dates <br/>'
        f'/api/v1.0/   "(start date)/(end date)"'
    )
@app.route("/api/v1.0/precipitation")
def precip():
    session = Session(bind=engine)

    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    OneYearPrcp = session.query(Measurements.date, Measurements.prcp).\
        filter(Measurements.date >= query_date).order_by(Measurements.date).all()
    
    session.close()

    prcp_dict = {date: prcp for date, prcp in OneYearPrcp}

    return jsonify(prcp_dict)

@app.route("/api/v1.0/stations")
def station():
    session = Session(bind=engine)

    wx_stations = session.query(Stations.station, Stations.name, Stations.latitude, Stations.longitude, Stations.elevation).all()
    all_stations = []
    for row in wx_stations:
        wx_stations_dict = {}
        wx_stations_dict["ID"] = row.station
        wx_stations_dict["Name"] = row.name
        wx_stations_dict["Lat"] = row.latitude
        wx_stations_dict["Long"] = row.longitude
        wx_stations_dict["Elevation"] = row.elevation
        all_stations.append(wx_stations_dict)

    # wx_stations = session.query(Stations.station, Stations.name).all()
    # wx_stations_dict = {}
    # for row in wx_stations:
    #     wx_stations_dict[row.station] = row.name
    session.close()

    json_wx_station = jsonify(all_stations)
    return (json_wx_station)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(bind=engine)

    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    OneYearTemp = session.query(Measurements.date, Measurements.tobs).filter(Measurements.date >= query_date).\
    filter(Measurements.station == 'USC00519281').all()

    OneYearTemp_dict = {}

    for row in OneYearTemp:
        OneYearTemp_dict[row.date] = row.tobs

    session.close()

    json_OneYearTemp = jsonify(OneYearTemp_dict)
    return (json_OneYearTemp)

@app.route("/api/v1.0/<start>")
def temps_station(start):
    session = Session(bind=engine)

    min_max_avg = session.query(Stations.station, Stations.name, func.min(Measurements.tobs), \
            func.max(Measurements.tobs), func.round(func.avg(Measurements.tobs))).group_by(Stations.station).\
            filter(Measurements.station == Stations.station).filter(Measurements.date >= start).all()

    session.close()
    # station_list_temp = [(*result,) for result in min_max_avg]
    station_dict_temp = {result[0]: {"name": result[1], "min_temp": result[2], "max_temp": result[3],\
                         "avg_temp": result[4]} for result in min_max_avg}

    json_station_list_temp = jsonify(station_dict_temp)
    return(json_station_list_temp)

@app.route("/api/v1.0/<start>/<end>")
def temps_station_enddate(start, end):
    session = Session(bind=engine)

    min_max_avg = session.query(Stations.station, Stations.name, func.min(Measurements.tobs), \
            func.max(Measurements.tobs), func.round(func.avg(Measurements.tobs))).group_by(Stations.station).\
            filter(Measurements.station == Stations.station).\
            filter(Measurements.date >= start).filter(Measurements.date <= end).all()

    session.close()
    # station_list_temp = [(*result,) for result in min_max_avg]
    station_dict_temp = {result[0]: {"name": result[1], "min_temp": result[2], "max_temp": result[3],\
                         "avg_temp": result[4]} for result in min_max_avg}

    json_station_list_temp = jsonify(station_dict_temp)
    return(json_station_list_temp)

if __name__ == '__main__':
    app.run(debug=True)