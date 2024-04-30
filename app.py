# Import the dependencies.
from flask import Flask, jsonify
import numpy as np
import pandas as pd
import datetime as dt
app = Flask(__name__)

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
#################################################
# Database Setup
#################################################


# reflect an existing database into a new model
engine = create_engine("sqlite:///Resources/hawaii.sqlite", echo = False)
# reflect the tables
Base = automap_base()
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
@app.route("/")
def home():
    ##Display all routes
    return (
       f"Available Routes: <br/>"
       f"<a href='/api/v1.0/precipitation'  >/api/v1.0/precipitation </a><br/>"
       f"<a href = '/api/v1.0/stations' >/ /api/v1.0/stations  </a><br/>"
       f"<a href = '/api/v1.0/tobs' >/ /api/v1.0/tobs </a><br/>"
       f"/api/v1.0/[start]<br/>"
       f"/api/v1.0/[start]/[end]"
    )


#################################################
# Flask Routes
#################################################
@app.route("/api/v1.0/precipitation")
def precipitation():
   
    # Calculate the date one year from the last date in data set.
    year_ago = dt.datetime(2017, 8, 22) - dt.timedelta(days = 365)

    # Perform a query to retrieve the date and precipitation scores
    query = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= year_ago).all()

    # Create empty Dictionary
    precip_dict = {} 

    # Use a for loop to add data to dictionary
    for element in query:
        date = element[0]
        prcp = element[1]
        precip_dict[date] = prcp

    session.close()

    return jsonify(precip_dict)



@app.route("/api/v1.0/stations")
def stations():
    stats = session.query(Station.station).all()

    stat_list = []

    for station in stats:
        stat = station[0]
        stat_list.append(stat)

    stat_list

    session.close()

    return jsonify(stat_list)

@app.route("/api/v1.0/tobs")
def tobs():
        # Design a query to find the most active stations (i.e. which stations have the most rows?)
    # List the stations and their counts in descending order.
    year_ago = dt.datetime(2017, 8, 22) - dt.timedelta(days = 365)
    station_ids = session.query(Measurement.station, func.count(Measurement.station)).\
    group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).\
    all()

    #Isolate most active station
    first_station = station_ids[0][0]
    session.close()
    #Return results for date and precipitation data for the most active station
    results = session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.station == first_station).\
        filter(Measurement.date >= year_ago).\
        all()

    results
    #Create data display
    df = pd.DataFrame(results).to_dict('records')

    session.close()

    return jsonify(df)

@app.route("/api/v1.0/<start>")
def begin(start):
    meas = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
    filter(Measurement.date >= start).first()

    session.close()

    return jsonify(list(meas))

@app.route("/api/v1.0/<start>/<end>")
def begin_and_end(start, end): 
    meas = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
    filter(Measurement.date >= start).filter(Measurement.date<= end).first()

    session.close()

    return jsonify(list(meas))


if __name__=='__main__':
    app.run(debug = True)