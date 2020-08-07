from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import time
import pyttsx3
import speech_recognition as sr
import pytz
import subprocess
import webbrowser
from selenium import webdriver
import requests
from bs4 import BeautifulSoup
import json
from selenium import webdriver




SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
MONTHS = ["january", "february", "march", "april", "may", "june","july", "august", "september","october","november", "december"]
DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
DAY_EXTENTIONS = ["rd", "th", "st", "nd"]

def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def get_audio():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source)
        said = ""

        try:
            said = r.recognize_google(audio, language="en-EN")
            print(said)
        except Exception as e:
            print("Exception: " + str(e))

    return said


def authenticate_google():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    return service


def get_events(day, service):
    date = datetime.datetime.combine(day, datetime.datetime.min.time())
    end_date = datetime.datetime.combine(day, datetime.datetime.max.time())
    utc = pytz.UTC
    date = date.astimezone(utc)
    end_date = end_date.astimezone(utc)

    events_result = service.events().list(calendarId='primary', timeMin=date.isoformat(), timeMax=end_date.isoformat(),
                                        singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        speak('No upcoming events found.')
    else:
        speak(f"You have {len(events)} events on this day.")

        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start, event['summary'])
            start_time = str(start.split("T")[1].split("-")[0])
            if int(start_time.split(":")[0]) < 12:
                start_time = start_time + "am"
            else:
                start_time = str(int(start_time.split(":")[0])-12)
                start_time = start_time + "pm"

            speak(event["summary"] + " at " + start_time)


def get_date(text):
    text = text.lower()
    today = datetime.date.today()

    if text.count("today") > 0:
        return today

    day = -1
    day_of_week = -1
    month = -1
    year = today.year

    for word in text.split():
        if word in MONTHS:
            month = MONTHS.index(word) + 1
        elif word in DAYS:
            day_of_week = DAYS.index(word)
        elif word.isdigit():
            day = int(word)
        else:
            for ext in DAY_EXTENTIONS:
                found = word.find(ext)
                if found > 0:
                    try:
                        day = int(word[:found])
                    except:
                        pass

    if month < today.month and month != -1:  
        year = year+1

    
    if month == -1 and day != -1:  
        if day < today.day:
            month = today.month + 1
        else:
            month = today.month

    
    if month == -1 and day == -1 and day_of_week != -1:
        current_day_of_week = today.weekday()
        dif = day_of_week - current_day_of_week

        if dif < 0:
            dif += 7
            if text.count("next") >= 1:
                dif += 7

        return today + datetime.timedelta(dif)

    if day != -1: 
        return datetime.date(month=month, day=day, year=year)

def note(text):
    date = datetime.datetime.now()
    file_name= str(date).replace(":","-") + "-note.txt"

    with open (file_name,"w") as f:
        f.write(text)
    
    subprocess.Popen(["notepad.exe",file_name])

def search(text):

    subprocess.Popen("chrome.exe")



SERVICE = authenticate_google()
print("Start")
text = get_audio().lower()

CALENDAR_STRS = ["what do i have", "do i have plans", "am i busy"]
for phrase in CALENDAR_STRS:
    if phrase in text:
        date = get_date(text)
        if date:
            get_events(date, SERVICE)
        else:
            speak("Please Try Again")

NOTE_STRS = ["make a note", "write down"]

for phrase in NOTE_STRS:
    if phrase in text:
        speak("what do you want to write down ?")
        note_text = get_audio().lower()
        note(note_text)
        speak("I wrote down")

SEARCH_STRS = ["search on google","search on internet"]

for phrase in SEARCH_STRS:
    if phrase in text:
        speak("what do you want me to search")
        url ="https://www.google.com/search?q="
        search_text = get_audio().lower()
        search_url = url + search_text
        webbrowser.open(search_url)

SEARCH_STRS = ["search on youtube","open on youtube"]
#driver = webdriver.Chrome(r'C:\Users\Emrah\Desktop\PythonProjects\InstaBot\chromedriver.exe')
for phrase in SEARCH_STRS:
    if phrase in text:
        speak("what do you want me to search")
        url ="https://www.youtube.com/results?search_query="
        search_text = get_audio().lower()
        search_url = url + search_text  + '&pbj=1'
        
        #webbrowser.open(search_url)
        print(search_url)

        base_url ='https://www.youtube.com/watch?v='
        
        payload = {}
        headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36',
        'x-spf-referer': 'https://www.youtube.com/',
        'x-youtube-client-name': '1',
        'x-spf-previous': 'https://www.youtube.com/',
        'x-youtube-client-version': '2.20200709.03.00',
        'accept': '/',
        'referer': 'https://www.youtube.com/',
        'accept-language': 'en,tr;q=0.9',
        'Cookie': 'VISITOR_INFO1_LIVE=UR6xWTleO18; YSC=rh2goUTRStk; GPS=1'
        }

        response = requests.request("GET", search_url, headers=headers, data = payload)
        test = json.loads(response.text.encode('utf8'))
        videoID = test[1]["response"]["contents"]["twoColumnSearchResultsRenderer"]["primaryContents"]["sectionListRenderer"]["contents"][0]["itemSectionRenderer"]["contents"][0]["videoRenderer"]['videoId']
        last_url = base_url + videoID 

        webbrowser.open(last_url)

A = ["open game"]
for phrase in A:
    if phrase in text:
        subprocess.call(r'C:\Program Files (x86)\Steam\steamapps\common\eFootball PES 2020\PES2020.exe')
        
        
