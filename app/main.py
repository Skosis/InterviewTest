from fastapi import FastAPI
import datetime
from fastapi import responses, requests

from typing import List
from pydantic import BaseModel

# Simple application that recieves POST and GET requests
#   Implmented as a FastAPI application
# 
# Author: Jacob Nardone
# Version: 1.0
# Date: 1/10/2022


app = FastAPI()
measurementList = []        # List of All Measurements

# Template Class that outlines the structure of a measurement
# 
# Name is the name of the sensor the measurement is from
# Timestamp is the time the measurement was taken
# Value is the value of the measurement
class Measurements:
    def __init__(self, name, timestamp, value):
        self.name = name
        self.timestamp = timestamp
        self.value = value

# Model that describes the JSON style a measurement will be POSTed in
# 
# Sensor is the name of sensor the measurement is from
# Timestamp is the time measurement was taken
# Value is the value of measurement
class Sensor(BaseModel):
    sensor: str
    timestamp: datetime.datetime
    value: float

# For testing Purposes, will print out the list of measurements and all 
#   of their stored values
def printOut():
    for measurement in measurementList:
        print(measurement.name, measurement.timestamp, measurement.value)

# Helper method to get the total value of all measurements recived by the server
# 
# Returns the total value of all measurements
def get_Total_Value():
    total = 0.0
    for measurement in measurementList:
        total += measurement.value
    return total

# Helper method that extracts all measurements of a given sensor from MeasurementList
# 
# Returns nothing
def remove_All_Instances_Of_Sensor_In_MeasurementList(sensorName):
    global measurementList
    tempList = [x for x in measurementList if x.name != sensorName]
    measurementList = tempList
    return

# Recives Data from POST requests and adds it to the measurementList
# JSON will be in the format of Sensor Class
# 
# Returns nothing
@app.post("/data")
async def recievedData(data:List[Sensor]):
    global measurementList
    for element in data:
        measurementList.append(Measurements(element.sensor, element.timestamp, element.value))
    return

# Gets the statistics for a given sensor
# 
# Returns the last measurement, the total number of measurements passed to the 
#   server, and the avg of all values passed to server, 
#   if no measurement exist return default values
@app.get("/statistics/{sensor_id}")
async def GetStatsForGivenSensor(sensor_id: str):
    global measurementList
    if (len(measurementList) > 0):  # There are measurements
        holder = measurementList[-1]
        count = len(measurementList)
        total = get_Total_Value()
        avg = total/count
        
        results = {"last_measurement": holder.timestamp, "count": count, "avg": avg}
        return results 

    else:                           # No measurements exist
        results = {"last_measurement": None, "count": 0, "avg": 0.0}
        return results
    
# Will remove all measurements from MeasurementList of a given sensor
# 
# Returns nothing
@app.delete("/statistics/{sensor_id}")
async def deleteSensor(sensor_id: str):
    remove_All_Instances_Of_Sensor_In_MeasurementList(sensor_id)
    return

# If server is ready to receive data, will return a 204 code
# Otherwise will return a 400 code
# 
# Returns nothing with a status code of either 204 or 400
@app.get("/healthz", status_code=204)
async def healthz():
    try:        # Check to see if server is ready to receive data
        response = requests.get("http://localhost:8080/healthz")
        if (response.status_code == 204):
            return    
                 
    except:
        raise responses.HTTPException(status_code=400, detail="Server is not ready to receive data")
    return
