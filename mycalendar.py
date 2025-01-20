import os.path
import datetime
import streamlit as st
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

class AttrDictForJson(dict):

    def __init__(self, attrdict):
        super().__init__()
        self.items = attrdict.items
        self._len = attrdict.__len__
        # key creation necessary for json.dump to work with CPython 
        # This is because optimised json bypasses __len__ on CPython
        if self._len() != 0:
            self[None] = None

    def __len__(self):
        return self._len()
    
def as_attrdict(val):
    return AttrDictForJson(val)

class calendar():
  
  def __init__(self):
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
      creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
      if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
      else:
        dic = dict(st.secrets['credentials'])
        user_encode_data = json.dumps(dic, indent=2).encode('utf-8')
        flow = InstalledAppFlow.from_client_config(
           user_encode_data.encode('utf-8'), SCOPES
        )
        creds = flow.run_local_server(port=0)
      # Save the credentials for the next run
      with open("token.json", "w") as token:
        token.write(creds.to_json())

    self.creds = creds

  def CreateEvent(self, calendarID, dataframe):    

    if dataframe['Departamento']: 
      instituicao = f'{dataframe.Departamento}/{dataframe.Instituição}'
    else: instituicao = dataframe['Instituição']
    titulo = dataframe['Serviço']
    detalhes = f'''
{dataframe['Nome']}
{instituicao}
{dataframe['Email']}
{dataframe['Instrumento']}
'''
    data_inicial = datetime.datetime.strptime(dataframe['Data de Coleta']+'T09:00:00').isoformat()
    data_final = datetime.datetime.strptime(dataframe['Data de Coleta']+'T16:00:00').isoformat()

    try:
      
      service = build('calendar', 'v3', credentials=self.creds)
      evento ={
        'summary' : titulo,
        'location' : 'LTAP',
        'description' : detalhes,
        'color' : 'Peacock',
        'start' : {
          'datetime': data_inicial
          },
        'end' : {
          'datetime': data_final
          },
      }
      criar_evento = service.events().insert(calendarID=calendarID, 
                                             body = evento).execute()
    except HttpError as error:
        print(f"An error occurred: {error}")

    return self

  def GetBusy(self, calendarID, timeMin, timeMax, timeZone = '-03:00'):
    try:
      
      service = build("calendar", "v3", credentials=self.creds)
      check = {
          'items' : [{
              'id': calendarID,
          }],
          'timeMax' : timeMax,
          'timeMin' : timeMin,
          'timeZone' : timeZone
      }

      response = service.freebusy().query(body=check).execute()
      lst = response['calendars'][calendarID]['busy']
      return lst
  
    except HttpError as error:
        print(f"An error occurred: {error}")
