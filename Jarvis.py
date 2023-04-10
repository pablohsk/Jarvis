import speech_recognition as sr
import playsound
from gtts import gTTS
import random
import webbrowser
import os
import pyttsx3
import datetime
import schedule
import time
import json
import pyowm
import requests
from bs4 import BeautifulSoup
import spotipy
from spotipy.oauth2 import SpotifyOAuth

class Weather:
    def __init__(self, api_key):
        self.owm = pyowm.OWM(api_key)
        
    def get_weather_at_place(self, place):
        observation = self.owm.weather_at_place(place)
        w = observation.get_weather()
        return w.get_detailed_status(), w.get_temperature('celsius')['temp']
        
    def speak_weather(self, place):
        try:
            status, temperature = self.get_weather_at_place(place)
            self.engine_speak(f"Current weather in {place} is {status} with a temperature of {temperature} degrees Celsius.")
        except pyowm.exceptions.api_response_error.NotFoundError:
            self.engine_speak(f"Sorry, I couldn't find the weather for {place}.")

class Spotify:
    def __init__(self, client_id, client_secret, redirect_uri):
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri, scope='playlist-modify-public,user-library-modify,user-library-read,user-read-playback-state,user-modify-playback-state'))
    
    def search_song(self, query):
        results = self.sp.search(q=query, type='track', limit=1)
        if results['tracks']['items']:
            track = results['tracks']['items'][0]
            return track['uri']
        else:
            return None
    
    def create_playlist(self, playlist_name):
        self.sp.user_playlist_create(user=self.sp.me()['id'], name=playlist_name, public=True)
        
    def add_song_to_playlist(self, playlist_id, song_uri):
        self.sp.playlist_add_items(playlist_id, [song_uri])
        
    def play_song(self, song_uri):
        self.sp.start_playback(uris=[song_uri])
        
    def pause_song(self):
        self.sp.pause_playback()
        
    def skip_song(self):
        self.sp.next_track()
        
    def previous_song(self):
        self.sp.previous_track()

#Here we need to define you client_id and client_secret from spotify developers
client_id = os.environ['SPOTIPY_CLIENT_ID']
client_secret = os.environ['SPOTIPY_CLIENT_SECRET']

# Set the redirect_uri variable to your app's redirect URL
redirect_uri = 'http://localhost:8000/callback/'

# Create instance of SpotifyOAuth class with credentials and value of redirect_uri
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id='CLIENT_ID', client_secret='CLIENT_SECRET', redirect_uri=redirect_uri))

# Use the newly created Spotify object to make Spotify API calls
results = sp.search(q='Muse', limit=20)

spotify = Spotify(client_id, client_secret, redirect_uri)
song_uri = spotify.search_song("Nome da música")
spotipy.play_song(song_uri)

class Reminder:
    def __init__(self):
        self.events = {}
        
    def load_reminders(self):
        with open('reminders.json', 'r') as file:
            self.events = json.load(file)
            
    def save_reminders(self):
        with open('reminders.json', 'w') as file:
            json.dump(self.events, file)
            
    def add_event(self, event_name, event_date):
        self.events[event_name] = event_date
        self.save_reminders()
        
    def remove_event(self, event_name):
        if event_name in self.events:
            del self.events[event_name]
            self.save_reminders()
            
    def get_event_date(self, event_name):
        if event_name in self.events:
            return self.events[event_name]
        else:
            return None
        
    def get_events(self):
        return self.events
        
    def speak_events(self):
        events = self.get_events()
        if len(events) == 0:
            self.engine_speak("You have no reminders.")
        else:
            self.engine_speak("Your reminders are:")
            for event in events:
                event_date = datetime.datetime.strptime(events[event], '%Y-%m-%d')
                assistent.engine_speak(f"{event} on {event_date.strftime('%B %d, %Y')}")
                
reminder = Reminder()
reminder.load_reminders()

class News:
    def __init__(self):
        self.url = "https://www.reuters.com/"
        self.articles = []

    def fetch_headlines(self):
        response = requests.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        headlines = soup.find_all("h3", class_="article-heading")
        for headline in headlines:
            self.articles.append(headline.text)

    def speak_headlines(self):
        self.fetch_headlines()
        if len(self.articles) == 0:
            assistent.engine_speak("Sorry, I couldn't find any news.")
        else:
            assistent.engine_speak("Here are the latest headlines:")
            for i, article in enumerate(self.articles):
                assistent.engine_speak(f"Headline {i+1}: {article}")

news = News()

class Virtual_assist():
  def __init__(self, assist_name, person):
        self.person = person
        self.assist_name = assist_name

        self.engine = pyttsx3.init()
        self.r = sr.Recognizer()

        self.voice_data = ''

  def _engine_speak(self, text):
    text = str(text)
    self.engine.say(text)
    self.engine.runAndWait()

  def record_audio(self, ask=""):
    with sr.Microphone() as source:
      if ask:
        self._engine_speak(ask)
        print("Recording")

      audio = self.r.listen(source, 4, 4)
      print('looking at the data base')

      try:
        self.voice_data = self.r.recognize_google(audio)
      except sr.UnknownValueError:
        self._engine_speak(f"Sorry {self.person}, I can't understand what did u say, pleas repeat")
      except sr.RequestError:
        self._engine_speak("Sorry, i can't connect to the server")

      print(">>", self.voice_data.lower())
      self.voice_data = self.voice_data.lower()

      return self.voice_data.lower()

  def engine_speak(self, audio_string):
    audio_string = str(audio_string)
    tts = gTTS(text=audio_string, lang='en')
    r = random.randint(1,2000)
    audio_file = 'audio' + str(r) +'.mp3'
    tts.save(audio_file)
    playsound.playsound(audio_file)
    print(self.assist_name + ':', audio_string)
    os.remove(audio_file)

  def there_exist(self,terms):
    for term in terms:
      if term in self.voice_data:
        return True

  def respond(self):
    if self.there_exist(['hey', 'hi','hello', 'oi', 'holla']):
      greetings = [f'Hi {self.person}, how can i help you?',
                  'Hi, what do you want to do now?',
                  'I am here to you!']
      greet = greetings[random.randint(0,len(greetings)-1)]
      self.engine_speak(greet)

  #Create playlist on spotify
  def create_playlist(self):
        if self.there_exist(['create playlist']):
          try:
            sp = spotipy.Spotify()
            sp.track(song_id)
          except spotipy.SpotifyException:
            # Caso não exista, solicita o client_id e client_secret do usuário
            client_id = input("Por favor, informe o client_id da sua aplicação: ")
            client_secret = input("Por favor, informe o client_secret da sua aplicação: ")
            sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))
            self.engine_speak('What should be the name of the playlist?')
            playlist_name = self.record_audio()
            spotify.create_playlist(playlist_name)
            self.engine_speak(f'Playlist {playlist_name} has been created!')

  #Add song to playlist on spotify
  def add_song_to_playlist(self):
    if self.there_exist(['add song to playlist']):
      self.engine_speak('What is the name of the song you want to add?')
      song_name = self.record_audio()
      song_uri = spotify.search_song(song_name)
      if song_uri:
        self.engine_speak(f'Adding {song_name} to the playlist')
        playlist_id = self.get_playlist_id()
        spotify.add_song_to_playlist(playlist_id, song_uri)
        self.engine_speak(f'{song_name} has been added to the playlist!')
    else:
        self.engine_speak(f"Sorry {self.person}, I couldn't find the song you were looking for.")

    #Search for playlist to add a song
    def get_playlist_id(self):
        playlists = spotify.sp.current_user_playlists()
        playlist_names = [playlist['name'] for playlist in playlists['items']]
        self.engine_speak('What is the name of the playlist you want to add the song to?')
        playlist_name = self.record_audio()
        while playlist_name not in playlist_names:
            self.engine_speak('I could not find any playlist with that name. Please try again')
            playlist_name = self.record_audio()
        playlist_id = playlists['items'][playlist_names.index(playlist_name)]['id']
        return playlist_id

    #Play a playlist from Spotify
    def play_playlist(self):
        if self.there_exist(['play playlist']):
            playlist_id = self.get_playlist_id()
            playlist_tracks = spotify.sp.playlist_items(playlist_id)
            track_uris = [track['track']['uri'] for track in playlist_tracks['items']]
            self.engine_speak(f'Playing {playlist_tracks["name"]} playlist')
            spotify.sp.start_playback(uris=track_uris)
          
    #Play a song from Spotify
    def play_song(self):
      if self.there_exist(['play song']):
        self.engine_speak('What is the name of the song you want to play?')
        song_name = self.record_audio()
        song_uri = spotify.search_song(song_name)
        if song_uri:
            self.engine_speak(f'Playing {song_name}')
            spotify.sp.start_playback(uris=[song_uri])
        else:
            self.engine_speak(f"Sorry {self.person}, I couldn't find the song you were looking for.")

    #google
    if self.there_exist(['search for']) and ('youtube' not in self.voice_data) and ('Hours' not in self.voice_data) and ('Time' not in self.voice_data):
      search_term = self.voice_data.split("for")[-1]
      url = "http://google.com/search?q=" + search_term
      webbrowser.get().open(url)
      self.engine_speak("here is what i found for " + search_term + 'on google')

    #youtube
    if self.there_exist(['search youtube for']) and 'Hours' or 'Time' not in self.voice_data:
      search_term = self.voice_data.split("for")[-1]
      url = "http://www.youtube.com/results?search_query=" + search_term
      webbrowser.get().open(url)
      self.engine_speak("here is what i found for " + search_term + 'on youtube')

    #hours
    if self.there_exist(['Hours', 'What time is it?']):
      search_term = datetime.datetime.now().strftime('%H:%M')
      self.engine_speak('Now it is ' + search_term)

    elif self.there_exist(['what can you do', 'what are your abilities', 'what are your features']):
      abilities = ['I can set reminders for you', 'I can search the web for you', 'I can tell you the time and date']
      self.engine_speak(random.choice(abilities))
      
    #Reminder
    elif self.there_exist(['set a reminder', 'create a reminder']):
      self.engine_speak("What do you want me to remind you of?")
      event_name = self.record_audio()
      self.engine_speak("When do you want to be reminded?")
      event_date = self.record_audio()
      reminder.add_event(event_name, event_date)
      self.engine_speak(f"{event_name} on {event_date} has been added to your reminders.")

    #Remove a reminder
    elif self.there_exist(['remove a reminder', 'delete a reminder']):
      self.engine_speak("Which reminder do you want to remove?")
      event_name = self.record_audio()
      reminder.remove_event(event_name)
      self.engine_speak(f"{event_name} has been removed from your reminders.")

    #Show the reminder(s)
    elif self.there_exist(['what are my reminders', 'show my reminders']):
      reminder.speak_events()

    #News
    elif assistent.there_exist(['news', 'headlines']):
      news.speak_headlines()

    #Finish the conversation
    elif self.there_exist(['thank you', 'thanks', 'bye', 'goodbye']):
      self.engine_speak(f"You're welcome {self.person}. Goodbye!")
      exit()

    #Weather
    elif self.there_exist(['weather']):
      self.engine_speak("Sure, where?")
      place = self.record_audio()
      weather = Weather('HERE YOU NEED TO PUT YOUR KEY FROM PYOWM!!!!!')
      weather.speak_weather(place)

    else:
      self.engine_speak("Sorry, I didn't understand. Can you repeat that?")

assistent = Virtual_assist('Jarvis', 'Pablo')

while True:

    voice_data = assistent.record_audio('listening...')
    assistent.respond()

    if assistent.there_exist(['bye', 'goodbye', 'seeyou', 'see you later', 'see you']):
        assistent.engine_speak("Have a nice day! Good bye!")
        break