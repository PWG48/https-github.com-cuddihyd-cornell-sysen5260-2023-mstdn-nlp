import time
import requests
import json
import uuid
import os

def convert_to_path(timestamp):
    # returns path as year/month/day/hour/minute/second/
    # ex: 2023-04-26T03:49:18.830Z -> 2023/04/26/03/49/18/
    return timestamp.replace("-","/").replace("T","/").replace(":","/")[:-5] #removes last 5 chars
    

while True: 
    response = requests.get('https://mastodon.social/api/v1/timelines/public') #pull data from mastodon API
    toots = response.json() #store data in json
    for toot in toots: #for each toot in json of multiple toots
        path = convert_to_path(toot["created_at"]) #create path based on 'created_at' field for each toot
        file_path = '/opt/data/'+path+'/' # store data in datalake
        if not os.path.exists(file_path):
            os.makedirs(file_path) #create directory for json file
        with open(file_path+str(uuid.uuid1())+'.json', 'w') as f: #save json file
            json.dump(toot,f)
    
    time.sleep(30) # repeat every 30 seconds



