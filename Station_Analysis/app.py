# Import the dependencies.
import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker

from flask import Flask, jsonify, request

#################################################
# Database Setup
#################################################

# Create engine using the `hawaii.sqlite` database file
engine = create_engine("sqlite:///../Resources/hawaii.sqlite", echo=False)

# Declare a Base using `automap_base()`
Base = automap_base()

# Use the Base class to reflect the database tables
Base.prepare(engine, reflect=True)

# Assign the measurement class to a variable called `Measurement` and
# the station class to a variable called `Station`
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create a session
Session = sessionmaker(bind=engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
# Homepage Route
@app.route('/')
def homepage():
    return (
        f"Available Routes: <br/>"
        f"Precipitation: /api/v1.0/precipitation<br/>"
        f"Stations List: /api/v1.0/stations<br/>"
        f"Temperature for the Last 365 Days: /api/v1.0/tobs<br/>"
        f"Temperature from Start Date (yyyy-mm-dd): /api/v1.0/<start><br/>"
        f"Temperature from Start Date to End Date (yyyy-mm-dd): /api/v1.0/<start>/<end><br/>"
    )

# Function to find the start date for a one-year date range
def start_date():
    session = Session()
    try:
        end_date = session.query(func.max(Measurement.date)).first()[0]
        start_date = dt.datetime.strptime(end_date, "%Y-%m-%d") - dt.timedelta(days=365)
    finally:
        session.close()  # Ensure the session is closed
    return start_date.strftime("%Y-%m-%d")

def end_date():
    session = Session()
    try:
        end_date = session.query(func.max(Measurement.date)).first()[0]
    finally:
        session.close()  # Ensure the session is closed
    return end_date.strftime("%Y-%m-%d")

# Precipitation Route
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session()
    try:
        results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= start_date).all()
        precipitation = {date: prcp for date, prcp in results}
    finally:
        session.close()  # Ensure the session is closed
    return jsonify(precipitation)

# Stations Route
@app.route('/api/v1.0/stations')
def stations():
    session = Session()
    try:
        results = session.query(Station.station, Station.id).all()
        stations_list = [{'station': station, 'id': id} for station, id in results]
    finally:
        session.close()  # Ensure the session is closed
    return jsonify(stations_list)

# Temperature Observations Route
@app.route('/api/v1.0/tobs')
def tobs():
    session = Session()
    try:
        top_station = session.query(Measurement.station).group_by(Measurement.station).\
            order_by(func.count().desc()).first().station
        results = session.query(Measurement.date, Measurement.tobs).\
            filter(Measurement.station == top_station).filter(Measurement.date >= start_date).all()
        tobs_list = [{'date': date, 'tobs': tobs} for date, tobs in results]
    finally:
        session.close()  # Ensure the session is closed
    return jsonify(tobs_list)

# Temperature Statistics Route (Start Date)
@app.route('/api/v1.0/<start>')
def start_temps(start):
    session = Session()
    try:
        start_date = dt.datetime.strptime(start, '%Y-%m-%d')
        results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start_date).all()
        temp_stats = {'min_temp': results[0][0], 'avg_temp': results[0][1], 'max_temp': results[0][2]}
    finally:
        session.close()  # Ensure the session is closed
    return jsonify(temp_stats)

# Temperature Statistics Route (Start Date to End Date)
@app.route('/api/v1.0/<start>/<end>')
def start_end_temps(start, end):
    session = Session()
    try:
        start_date = dt.datetime.strptime(start, '%Y-%m-%d')
        end_date = dt.datetime.strptime(end, '%Y-%m-%d')
        results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
        temp_stats = {'min_temp': results[0][0], 'avg_temp': results[0][1], 'max_temp': results[0][2]}
    finally:
        session.close()  # Ensure the session is closed
    return jsonify(temp_stats)

if __name__ == '__main__':
    app.run(debug=True)

