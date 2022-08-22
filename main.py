
import json 
import requests
import time
import os
import random
from datetime import datetime
from pytz import timezone

"""Pleae enter your webhook url, canvas token and course id"""
webhook="URL FOR DISCORD WEBHOOK" #https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks
canvas_token = "ENTER YOUR CANVAS TOKEN" #https://community.canvaslms.com/t5/Student-Guide/How-do-I-manage-API-access-tokens-as-a-student/ta-p/273
courseID = 000000 #enter course id https://www.youtube.com/watch?v=DbwwLqSHe30

#grab the json file from canvas
def fetchinfo():
    headers = {'Authorization': 'Bearer '+canvas_token}
    try:
        response = requests.get('https://canvas.asu.edu/api/v1/planner/items?start_date=2022-08-21&per_page=100', headers=headers)
    except requests.exceptions.Timeout:
    # Maybe set up for a retry, or continue in a retry loop
        e = "connection not established in 3sec and data not recived in 6sec"
        send_Error("Timeout error", e)
        print("retying...")
    except requests.exceptions.TooManyRedirects:
    # Tell the user their URL was bad and try a different one
        e = "redirecting?"
        send_Error("Too many redirects", e)
        print("Retrying....")
    except requests.exceptions.RequestException as e:
    # catastrophic error. bail.
        send_Error("Error occured!", "Please check on ur bot ")
        print("Retrying")
    
    with open("updates.json","wb") as f:
        f.write(response.content)

#send error message to discord
def send_Error(message, e):
    data = {"embeds":[]}
    embed = {}
    
    embed["title"]=message
    embed["description"] = str(e)
    embed['color']= 0xff0000
    #for all params, see https://discordapp.com/developers/docs/resources/channel#embed-object
    data["embeds"].append(embed)
    requests.post(webhook,data=json.dumps(data), headers={"Content-Type": "application/json"})

#send notification to discord
def send_notification(title,description):
    data = {"embeds":[]}
    embed = {}
    embed["title"]=title
    embed['color']= 65301
    embed["description"] = description
    #for all params, see https://discordapp.com/developers/docs/resources/channel#embed-object
    data["embeds"].append(embed)
    requests.post(webhook,data=json.dumps(data), headers={"Content-Type": "application/json"})
    #print(product["title"])
    time.sleep(1.5)

#main function
def main():
    awake = False #change to False
    while(True):
        #check if the bot is awake which is usally after 24 hours
        while(awake):
            print("inside main loop")
            already_set = False #initialize the variable
            fetchinfo() #fetch the json file from canvas
            data = json.load(open("updates.json")) #load the json file

            #parse the json file and check if there is any new update
            for item in data:
                if(item["course_id"] == courseID):
                    title = item["plannable"]["title"] #get the title of the update
                    assignment_id = str(item["plannable_id"]) #get the id of the update
                    if("due_at" in item["plannable"]):
                        due_at = "Due Date: "+ item["plannable"]["due_at"] #get the due date of the update

                        #check if assignment has already been posted to discord
                        with open('postedassignments.txt', 'r') as li:
                            newline = li.readline()
                            while newline:
                                if newline.strip() == assignment_id:
                                    already_set = True
                                newline = li.readline()
                        li.close()  

                        #setup dates to see how long until due date
                        mst = timezone('MST') 
                        current = int(datetime.now(mst).strftime("%Y%m%d"))
                        due_date = int("".join(item["plannable"]["due_at"].split("T")[0].split("-")))
                        #if not posted then post it
                        if(not already_set and due_date-current < 3):
                            send_notification(title, due_at)
                            file1 = open("postedassignments.txt","a")
                            file1.write("\n"+assignment_id)
                            file1.close()
                        already_set = False

            print("done")
            awake = False
        #refresh every 24hours    
        print("sleeping 24 hours")
        time.sleep(86400)
        awake = True #change to True to restart the loop

if __name__ == "__main__":
    main()