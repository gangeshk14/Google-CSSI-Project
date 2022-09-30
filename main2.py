import json
import os
import urllib.parse
#from urlparse import urlparse
from datetime import datetime
import pytz
from flask import Flask, render_template, request
import urlfetch


app = Flask(__name__)



@app.route('/', methods=['GET', 'POST'])
def welcome():
    return render_template("homepage.html")

@app.route('/welcome', methods=['GET', 'POST'])
def MainHandler():
    return render_template("website.html")

@app.route('/sm', methods=['GET', 'POST'])
def SocialMedia():
    return render_template("socialmedia.html")
@app.route('/traffic', methods=['GET', 'POST'])
def Traffic():
    return render_template("trafficimages.html")

@app.route('/weather', methods=['GET', 'POST'])
def WeatherHandler():
    if request.method == 'GET':
        return render_template("welcome.html")
    if request.method == 'POST' :
            date = request.form.get("date")
            time = request.form.get("time")
            time_change = urllib.parse.quote(time, safe='')
            print(time_change)
            datetime = date+'T'+time_change+'%3A00'
            location = request.form.get("location")
            #print(location)
            #print(time)
            #print(date)

            endpointUrl = "https://api.data.gov.sg/v1/environment/2-hour-weather-forecast?date_time="+datetime
            print(endpointUrl)

            response = urlfetch.fetch(endpointUrl)

            content = response.content

            response_as_json = json.loads(content)
            print(len(response_as_json['area_metadata']))
            details = ""
            if len(response_as_json['area_metadata']) == 0:
                details = "The weather forecast only predicts for the next 24h! Please try again!"
                info = {'details':details
                }
            else:
                forecasts = response_as_json['items'][0]['forecasts']
                forecast = ''
                for data in forecasts:
                    if data['area'] == location:
                        forecast = data['forecast']
                        break

                info = {
                    "forecast":"Forecast at "+location+' on '+date+' '+time+' shows '+ forecast +' weather',
                    "location": location,
                    "time": time,
                    "date": date,
                }
                print(forecast)
            return render_template("welcome.html", forecast=forecast,details=details,location=location,time=time,date=date)
@app.route('/bus', methods=['GET', 'POST'])
def BusTimingsHandler():
    if request.method == 'GET':
          headers = { 'AccountKey' : 'Your Key', #Input your API Key
          'accept' : 'application/json'} #this is by default

          #API parameters
          endpointUrl1 = 'http://datamall2.mytransport.sg/ltaodataservice/TrainServiceAlerts' #Resource URL
          #Build query string & specify type of API call
          response1 = urlfetch.fetch(endpointUrl1,headers=headers)

          content1 = response1.content

          response_as_json1 = json.loads(content1)
          print(response_as_json1)
          print(response_as_json1['value']['Status'])
          if response_as_json1['value']['Status'] == 1:
              train_message = 'Train service is as per normal now.'
          else:
              train_message = response_as_json1['value']['Message']
          train = {'train_message':train_message}
          return render_template("bustimings.html", train_message=train_message)

    else:

          with open('busstops_new.json') as data_file:
              data = json.load(data_file)

          stopName = request.form.get("stopid")
          stopId = data[stopName]
          #Authentication parameters
          headers = { 'AccountKey' : 'Your API Key', #Input your unique API Key
          'accept' : 'application/json'} #this is by default

          #API parameters
          endpointUrl = 'http://datamall2.mytransport.sg/ltaodataservice/BusArrivalv2?BusStopCode='+stopId #Resource URL
          #Build query string & specify type of API call
          response = urlfetch.fetch(endpointUrl,headers=headers)

          content = response.content

          response_as_json = json.loads(content)



          #print(response_as_json)
          time_zone = pytz.timezone('Asia/Singapore')

          timings = response_as_json['Services']
          busno_arr = []

          time_arr = []

          for service in timings:
              bustime1 = service['NextBus']["EstimatedArrival"]
              if bustime1 == '':
                  continue
              bustime2 = service['NextBus2']["EstimatedArrival"]
              if bustime2 == '':
                  continue
              standorseat1 = ''
              standorseat2 = ''
              if service['NextBus']["Load"] == 'SEA':
                  standorseat1 = 'seating available!'
              else:
                  standorseat1 = 'standing available.'

              if service['NextBus2']["Load"] == 'SEA':
                  standorseat2 = 'seating available!'
              else:
                  standorseat2 = 'standing available.'

              bustime1 = datetime.strptime(bustime1,"%Y-%m-%dT%H:%M:%S+08:00")
              bustime2 = datetime.strptime(bustime2,"%Y-%m-%dT%H:%M:%S+08:00")
              time_zone = pytz.timezone('Asia/Singapore')
              sgtime = datetime.now(time_zone)
              sgtime = sgtime.strftime("%Y-%m-%d %H:%M:%S")
              sgtime = datetime.strptime(sgtime,"%Y-%m-%d %H:%M:%S")
              timediff1 = bustime1 - sgtime
              timediff2 = bustime2 - sgtime
              timeinmin1 = divmod(timediff1.total_seconds(), 60)[0]
              time1 = str(timeinmin1)+' minutes. and there is '+standorseat1
              timeinmin2 = divmod(timediff2.total_seconds(), 60)[0]
              time2 = str(timeinmin2)+' minutes. and there is '+standorseat2
              if timeinmin1<=0:
                  time1 = 'Arriving!'
              x = ''
              x = ' will be coming in: '+time1+' Subsequent timing: '+time2
              time_arr.append(x)
              busno_arr.append(service['ServiceNo'])
          print(time_arr)



          info = {
             "timings":time_arr,
             "busno": busno_arr,
             "stopid": stopName
          }
          return render_template("bustimings.html", timings = time_arr,busno=busno_arr,stopid=stopName)
          busno_arr = []
          time_arr = []

@app.route('/incident', methods=['GET', 'POST'])
def TrafficIncidents():
    headers = { 'AccountKey' : 'Your API Key', #Input Your API Key
    'accept' : 'application/json'} #this is by default

    #API parameters
    endpointUrl = 'http://datamall2.mytransport.sg/ltaodataservice/TrafficIncidents' #Resource URL
    #Build query string & specify type of API call
    response = urlfetch.fetch(endpointUrl,headers=headers)

    content = response.content

    response_as_json = json.loads(content)
    type = []
    details = []
    # print(response_as_json)
    incidents = response_as_json['value']
    for data in incidents:
        if data['Type'] == 'Roadwork':
            continue
        else:
            type.append(str(data['Type']))
            details.append(str(data['Message']))
    if len(type) == 0:
        x = 'There are no traffic accidents currently!'
        details.append(x)

    info = {'type': type,
            'details': details
            }

    return render_template("traffic.html",type=type,details=details)

@app.route('/car', methods=['GET', 'POST'])
def CarParkHandler():
    if request.method == 'GET':
        return render_template("carpark.html")
    else:
        with open('carparks_new.json') as data_file:
            data = json.load(data_file)
        parkName = request.form.get("carpark")
        parkName_new = data[parkName]
        #Authentication parameters
        headers = { 'AccountKey' : 'Your API Key', #Input your API Key
        'accept' : 'application/json'} #this is by default

        #API parameters
        endpointUrl = 'http://datamall2.mytransport.sg/ltaodataservice/CarParkAvailabilityv2' #Resource URL
        #Build query string & specify type of API call
        response = urlfetch.fetch(endpointUrl,headers=headers)

        content = response.content

        response_as_json = json.loads(content)



        #print(response_as_json)
        lots = ''

        details = response_as_json['value']
        for data in details:
            if data['Development'].lower() == parkName_new.lower():
                lots = str(data["AvailableLots"])
                content = 'Number of lots available at '+parkName+' : '
        print(lots)



        info = {
           "lots":lots,
           "parkName":parkName,
           "content": content
        }
        return render_template("carpark.html",lots=lots,parkName=parkName,content=content)

@app.route('/hi', methods=['GET', 'POST'])
def Hello():
    if request.method == 'GET':
        return render_template(" hi.html")

if __name__ == '__main__':
    # application on Google App Engine. See entrypoint in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
