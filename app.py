# Import Dependencies
import numpy as np
import datetime as dt
from flask import Flask, jsonify

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# We can view all of the classes that automap found
Base.classes.keys()

# Save references to each table
Measure = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

# Route Definations
# Home route
@app.route("/")
def Home():
    """List all available api routes."""
    return (
        f"<h1> Welcome to Climate App Homepage </h1>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation <==== Date & Precipitation data <br/>"
        f"/api/v1.0/stations <==== Station information <br/>"
        f"/api/v1.0/tobs <==== Temperature observation data <br/>"
        f"/api/v1.0/<start> <==== Min Temperature,  Max Temperature, Avg Temperature data based on start date<br/>"
        f"/api/v1.0/<start>/<end> <==== Min Temperature,  Max Temperature, Avg Temperature data for given start and end date range"
    )

# Error handling route:
# This route will handle errors registered for an exception or HTTP status code that would be raised while trying to handle a request.
@app.errorhandler(404)
def resource_not_found(e):
    return jsonify(error=str(e)), 404

# Precipitation route: 
# This route will return query results converted to a dictionary using `date` as the key and `prcp` as the value.
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of date and prcp"""
    # Query date and prcp from mearue db
    Precp_data = session.query(Measure.date, Measure.prcp).all()

    session.close()

    # Create a dictionary from the row data and append to a list of date and prcp.
    Precp_data_list = []
    for date, prcp in Precp_data:
        Precp_dict = {}
        Precp_dict["Date"] = date
        Precp_dict["Prcp"] = prcp
        Precp_data_list.append(Precp_dict)

    return jsonify(Precp_data_list)

# Station route: 
# This route will return list of stations from Station dataset.
@app.route("/api/v1.0/stations")
def station():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all Station"""
    # Query all stations
    Stations = session.query(Station.station, Station.name).all()
   
    session.close()

    # Convert list of tuples into normal list
    Station_names = list(np.ravel(Stations))

    return jsonify(Station_names)

# Tobs route:
# This route will return dates and temperature observations of the most active station for the last year of data.
@app.route("/api/v1.0/tobs")
def temperature():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all Station"""
    # Query all tobs
    Last_date = session.query(Measure.date).order_by(Measure.date.desc()).first()

    Last_date_fmt = dt.datetime.strptime(Last_date[0], "%Y-%m-%d")
    year = Last_date_fmt.year
    month = Last_date_fmt.month
    day = Last_date_fmt.day
    Year_ago_date = dt.date(year,month,day) - dt.timedelta(days=365)

    Max_Station_count = session.query(Measure.station).\
                     group_by(Measure.station).\
                     order_by(func.count(Measure.station).desc()).first()

    Display_tobs = session.query(Measure.date, Measure.tobs).\
                   filter(Measure.date >= Year_ago_date).\
                   filter(Measure.station == Max_Station_count[0]).all()

    session.close()

    # Convert list of tuples into normal list
    Tobs_data = list(np.ravel(Display_tobs))

    return jsonify(Tobs_data)

# Start date route:
# This route will return Return a JSON list of the minimum, average and the max temperature for a given start date.  
@app.route("/api/v1.0/<start>")
def start_date(start):
    
    # Check if the string entered is a date. if string is other than date then return the error message.
    Date_check = start.isalpha()
    
    if Date_check:
        return({"404 error": f"Invalid route or invalid date foramt."})

    # Create our session (link) from Python to the DB
    session = Session(engine)
    First_date = session.query(Measure.date).order_by(Measure.date).first()
    Last_date  = session.query(Measure.date).order_by(Measure.date.desc()).first()

    if start >= First_date[0] and start <= Last_date[0]:
      
        Min_Temp = session.query(func.min(Measure.tobs)).\
                   filter(Measure.date >= start).scalar()
        Max_Temp = session.query(func.max(Measure.tobs)).\
                   filter(Measure.date >= start).scalar()
        Avg_Temp = session.query(func.avg(Measure.tobs)).\
                    filter(Measure.date >= start).scalar()

        session.close()

        return(f'Minimum Temperature recored for start date {start} is {Min_Temp}</br>'
               f'Maximun Temperature recored for start date {start} is {Max_Temp}</br>'
               f'Average Temperature recored for start date {start} is {Avg_Temp}')

    # If the entered start date is out of range then below error will be displayed.
    else:
        return({"404 error": f"Start date {start} not found."})  

# Start and end date route:
# This route will return Return a JSON list of the minimum, average and the max temperature for a given start and end date.  
@app.route("/api/v1.0/<start>/<end>")
def start_end(start,end):
    if end <= start:
       return({"Date error: Start date should always be less than end date.</br> Correct route format is start date/end date"})  
  
    # Create our session (link) from Python to the DB
    session = Session(engine)
    First_date = session.query(Measure.date).order_by(Measure.date).first()
    Last_date  = session.query(Measure.date).order_by(Measure.date.desc()).first()

    if (start >= First_date[0] and start <= Last_date[0]) and (end >= First_date[0] and end <= Last_date[0]):

        Min_Temp = session.query(func.min(Measure.tobs)).\
                   filter(Measure.date >= start).\
                   filter(Measure.date <= end).scalar()
        Max_Temp = session.query(func.max(Measure.tobs)).\
                   filter(Measure.date >= start).\
                   filter(Measure.date <= end).scalar()   
        Avg_Temp = session.query(func.avg(Measure.tobs)).\
                   filter(Measure.date >= start).\
                   filter(Measure.date <= end).scalar()   

        session.close()

        return(f'Minimum Temperature recored for start date {start} and end date {end} is {Min_Temp}</br>'
               f'Maximun Temperature recored for start date {start} and end date {end} is {Max_Temp}</br>'
               f'Average Temperature recored for start date {start} and end date {end} is {Avg_Temp}')
               
    # If the entered start or end date is out of range then below error will be displayed.
    else:
        return({"404 error": f"Start date {start} or end date {end} not found."})  


if __name__ == '__main__':
    app.run(debug=True)
    