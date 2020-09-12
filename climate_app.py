import datetime as dt
import pandas as pd
from flask import Flask, jsonify
import numpy as np
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import create_engine, func, inspect
from sqlalchemy.orm import Session

#####################################
# create engine and reflect database
#####################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect = True)

#####################################
# assign table into variable
#####################################
Measurement = Base.classes.measurement


# set up flask
app = Flask(__name__)

@app.route("/")
def welcome():
    """welcome page, list out the routes
    """
    return(
        f"Available Routes: <br>"
        f"--------------------------<br>"
        f"/api/v1.0/precipitation<br>"
        f"/api/v1.0/stations<br>"
        f"/api/v1.0/tobs<br>"
        f"/api/v1.0/2012-01-01<br>"
        f"/api/v1.0/2012-01-01/2013-01-01<br>"
    )    

@app.route("/api/v1.0/precipitation")
def prcp():
    """return dates and precipitation
    """
    # create session
    session = Session(engine)
    # query results and change to list
    results = session.query(Measurement.date, Measurement.prcp).all()
    # create dict and append to list
    prcp_list = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        prcp_list.append(prcp_dict)
    
    session.close()

    return jsonify(prcp_list)

@app.route("/api/v1.0/stations")
def station():
    """Return a JSON list of stations from the dataset
    """
    # create session
    session = Session(engine)
    # query date
    station = session.query(Measurement.station).distinct().all()
    session.close()
    # convert to list
    station_list =  list(np.ravel(station))

    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    """return the dates and temperature observations of the most active station for the last year of data
    """
    # create session
    session = Session(engine)
    # query data
    results = session.query(Measurement.date, Measurement.prcp).\
            filter(Measurement.station =="USC00519281").all()
    session.close()
    # convert to dict
    tobs_list = []
    for date, temps in results:
        temp_dict={}
        temp_dict["date"] = date
        temp_dict["tobs"] = temps
        tobs_list.append(temp_dict)
    
    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def temp_date(start):
    """return min, avg and max temperature after start date
    """
    # create session
    session = Session(engine)

    content = [func.min(Measurement.tobs),
               func.avg(Measurement.tobs),
               func.max(Measurement.tobs)]
    # query the content
    temps_results = session.query(*content).filter(Measurement.date >= start).all()
    session.close()

    # create a list to store tobs dict
    temp_stats = []
    for min_temp, avg_temp, max_temp in temps_results:
        tobs_dict = {}
        tobs_dict["min_temp"] = min_temp
        tobs_dict["avg_temp"] = round(avg_temp,2)
        tobs_dict["max_temp"] = max_temp
        temp_stats.append(tobs_dict)

    return jsonify(temp_stats)
    
@app.route("/api/v1.0/<start>/<end>")
def temp_date_start_end(start, end):
    """return min, avg and max within a date range
    """
    # create session
    session = Session(engine)

    content = [func.min(Measurement.tobs),
               func.avg(Measurement.tobs),
               func.max(Measurement.tobs)]
    # query date
    temps_results = session.query(*content).filter(Measurement.date>=start).\
                filter(Measurement.date<= end).all()

    session.close()

    # create a list to store tobs dict
    temp_stats = []
    for min_temp, avg_temp, max_temp in temps_results:
        tobs_dict = {}
        tobs_dict["min_temp"] = min_temp
        tobs_dict["avg_temp"] = round(avg_temp,2)
        tobs_dict["max_temp"] = max_temp
        temp_stats.append(tobs_dict)

    return jsonify(temp_stats)



if __name__ == "__main__":
    app.run(debug=True)