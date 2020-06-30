from flask import escape
from azure.cosmos import exceptions, CosmosClient, PartitionKey
import azure.cosmos.exceptions as exceptions
import json
import logging
import pickle
import os.path
import ast 
import numpy as np
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
#from google.auth.transport.requests import Request
from google.oauth2 import service_account
from ortools.algorithms import pywrapknapsack_solver
import pandas as pd
from datetime import timedelta  
from datetime import datetime


# Festlegen mit welchem Service-User auf die Google-Apis zugegriffen werden soll. 
SCOPES = ['https://www.googleapis.com/auth/calendar']
SUBJECT = 'pdissd@quickstart-1592463381049.iam.gserviceaccount.com'
SERVICE_ACCOUNT_FILE = 'service-account.json'

HTTP_USER = 'pdissd@quickstart-1592463381049.iam.gserviceaccount.com'
HTTP_KEY =  '6853c54195cc2d04b890f786bb7b3373ac5d8568'


def get_events(request,calendarId="aqp0pv2uivgeqlk95vp60fbl3k@group.calendar.google.com" ):
    # Generiert ein Serviceobjekt und holt zu einer Kalenderid alle Events bis max. 500 
    
    user = request.headers.get('user')
    private_key_id = request.headers.get('private_key_id')

    if user == HTTP_USER and private_key_id == HTTP_KEY:

        service = generate_service_object()
        result = service.events().list(calendarId = 'aqp0pv2uivgeqlk95vp60fbl3k@group.calendar.google.com', maxResults = 500).execute() 

        app_json = json.dumps(result)
        

        return app_json
    else: 
        return json.dumps("401 Unauthorized ")

# Funktion die einen Cosmos_Client erzeugt, welcher dann mit der Datenbank kommunizieren kann 
def create_cosmos_client(request):
     # Initialize the Cosmos client
    endpoint = "https://ssdpdi.documents.azure.com:443/"
    key = 'iEBKSwezFAfsNGGROPJNv3qdjc4PAQfWBc5TEw57tqhjFd44V6xzAispXq9kGvtN1oTlB4qRHwGCKvzEDLf91g=='
    # <create_cosmos_client>
    client = CosmosClient(endpoint, key)
    # </create_cosmos_client>
    return client

# Funktion die einen Container erzeugt 
def create_cosmos_container(request):
    client = create_cosmos_client(request=request)
    # Create a database
    # <create_database_if_not_exists>
    database_name = 'SSD'
    container_name = 'Elemente'
    #database = client.create_database_if_not_exists(id=database_name)
    # </create_database_if_not_exists> 
    database = client.get_database_client(database_name)
    container = database.get_container_client(container_name) 
    return container

# Funktion welche initial die Priotitäten eines Users in der Datenbank hinterlegt 
def create_priorities(request): 

    request_json = request.get_json(silent=True)
    # Erzeuge einen Container client 
    
    container = create_cosmos_container(request=request) 

    # Priotitäten in Datenbank anlegen 
    container.create_item(body=request_json)

# Funktion welche die Informatione zu einem User aus der Datenbank zieht 
def get_userinfo(request,user_id="100"): 


    user = request.headers.get('user')
    private_key_id = request.headers.get('private_key_id')

    if user == HTTP_USER and private_key_id == HTTP_KEY:

    
        if request.headers.get('user_id'): 
            user_id = request.headers.get('user')
            
        else: 
            user_id="100"

        container = create_cosmos_container(request=request) 

        for item in container.query_items(query='SELECT * FROM Elemente c WHERE c.id=\"'+  user_id +  '\"', enable_cross_partition_query=True):
            user_info = json.dumps(item, indent=True)
    
        return user_info

    else:
        return ("401 unauthorized")

def delete_userinfo(request): 

    user = request.headers.get('user')
    private_key_id = request.headers.get('private_key_id')

    if user == HTTP_USER and private_key_id == HTTP_KEY:
        return("success")
        #for item in client.QueryItems("dbs/" + database_id + "/colls/" + container_id,'SELECT * FROM products p WHERE p.productModel = "DISCONTINUED"',{'enableCrossPartitionQuery': True})
        
        #client.DeleteItem("dbs/" + database_id + "/colls/" + container_id + "/docs/" + item['id'],{'partitionKey': 'Pager'})

    else: 
        return ("401 unauthorized")


def generate_service_object():

    # Erzeugen der Loginwerte 
    credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    #credentials = service_account.Credentials.(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    delegated_credentials = credentials.with_subject(SUBJECT)
    # Erstelle ein Objekt, welches mit der Api kommunizieren kann 
    service = build('calendar', 'v3', credentials=delegated_credentials)
    return service 


# Funktion die den Kalender auf Basis des B&B-Verfahrens optimiert 
def optimize(request):

    

    user = request.headers.get('user')
    private_key_id = request.headers.get('private_key_id')
    
    if user == HTTP_USER and private_key_id == HTTP_KEY:
    
        values = []
        
        user_info = get_userinfo(request=request)
        user_info = json.loads(user_info) 
        #user_info = ast.literal_eval(user_info)
        
    
        # Relevante Parameter dem Userprofil entnehmen 
    
        index = [] 
        values = []
        inbound_dict = {}
        for p,j in user_info["priorities"].items(): 
            values.append(j)
            index.append(p)
        
        inbound_dict["value"] = values
                
        # # Die nächsten Events aus dem Kalender holen und Gewichte entnehmen 
        user_events = get_events(request=request)
        # # In Python Objekt konvertieren 
        user_events = json.loads(user_events)
        
        response_list = []
        for i in user_events: 
            if "items" in i:
            #create dict 
                
                for j in user_events["items"]:
                    #print(j)
                    dict ={}
                    element =  j["description"].split(",")
                    dict["id"] = j["id"]
                    dict["weight"] = element[0]
                    dict["category"] = element[1]   
                    response_list.append(dict)

        
        # DataFrame für die Events generieren  
        df_events = pd.DataFrame(response_list)
        # DataFrame für das Userprofil generieren 
        df_values =  pd.DataFrame(inbound_dict,index)


        # Join über das Attribut category 
        df_to_solve = df_events.set_index('category').join(df_values)
        
        
        # Create the solver.
        solver = pywrapknapsack_solver.KnapsackSolver(
            pywrapknapsack_solver.KnapsackSolver.
            KNAPSACK_MULTIDIMENSION_BRANCH_AND_BOUND_SOLVER, 'KnapsackExample')

            
        
        
        values = list(df_to_solve.value)
        weights = [list(map(int,df_to_solve.weight))]
        
        print(values)
        print(weights)
        
        capacities = [50]

        solver.Init(values, weights, capacities)
        computed_value = solver.Solve()
        
        packed_items = []
        packed_weights = []
        total_weight = 0
        #print('Total value =', computed_value)
        for i in range(len(values)):
            if solver.BestSolutionContains(i):
                packed_items.append(i)
                packed_weights.append(weights[0][i])
                total_weight += weights[0][i]
        
        #print('Packed items:', packed_items)
        #print('Packed_weights:', packed_weights)
    

        

        # # jetzt müssen die Elemente ausgesucht werden, die verschoben werden
        bereinitge_optimierung = clear_optimization(list(df_to_solve.id),packed_items) 
        
        # # Jetzt müssen die zurückgelieferten Elemente neu geplant werden  
        # # Dafür müssen alle Events aus dem Kalender gezogen werden das liefert die Funktion dann zurück. 
        optimierungs_ergebnis = get_elements_by_ID(request,bereinitge_optimierung)
        return json.dumps(optimierungs_ergebnis)

    else: 
        return json.dumps("401 Unauthorized ") 

# Funktion, welche eine Liste um Elemente bereinigt am Ende kommen die Elemente raus, die umgeplant werden müssen 
def clear_optimization(list_events,packed_items):
    # schlimm mehr muss man dazu nicht sagen..... 
    bearbeitet = []
    i = 0 
    for e in list_events: 
        
        if i not in packed_items:
            bearbeitet.append(e)
        i = i + 1   
    return bearbeitet

# Funktion die Elemente basirend auf der ID aus einem Kalender holt 
def get_elements_by_ID(request,elements):
    # Erzeuge ein Service Objekt 
    service = generate_service_object()
    # Event liste 
    event_list = []
    for i in elements: 
        str(i)
        # Rufe die Api auf und speicher das Element in einer Liste 
        event = service.events().get(calendarId = 'aqp0pv2uivgeqlk95vp60fbl3k@group.calendar.google.com', eventId = i ).execute()
        event_list.append(event)         

    return event_list

# Funktion die belegte Zeiten für einen User zurückliefert 
def get_free_times(request,calendarId = 'aqp0pv2uivgeqlk95vp60fbl3k@group.calendar.google.com'): 
    # Erzeuge ein Service Objekt 
    service = generate_service_object() 
    # Api ansprechen 
    request_body = {
  "calendarExpansionMax": 10,
  "items": [
    {
      "id": "7a5dq767oegsavhuhv81cf5rebetukv7@import.calendar.google.com"
    },
    {
      "id": "aqp0pv2uivgeqlk95vp60fbl3k@group.calendar.google.com"
    }
  ],
  "timeMax": "2020-07-30T18:00:00+02:00",
  "timeMin": "2020-05-30T18:00:00+02:00",
  "groupExpansionMax": 10,
  "timeZone": "UTC"
}

    # Hole die Zeiten aus den Kalendern, in denen keine Zeit vorhanden ist. 
    busy_time = service.freebusy().query(body=request_body).execute()    

    #jetzt müssen die Elemente in eine Matrix geschrieben und sortiert werden. 
    print(type(busy_time))
    for i in busy_time["calendars"]:
         print(i)
    return json.dumps(busy_time)

    

# Funktion, welche die Elemente einer Liste nach Datum/Uhrzeit aufsteigend ordnet 
def sort_busy_times(busy_time): 
    pass

    


# Funktion welche events für einen Nutzer neu plant 
def replan_events(request): 


    user = request.headers.get('user')
    private_key_id = request.headers.get('private_key_id')
    # ID aus dem Request holen. 
    
    if user == HTTP_USER and private_key_id == HTTP_KEY:

        #Service Objekt erzeugen 
        service = generate_service_object()

        request_json = request.get_json(silent=True)
        for i in request_json: 

            # Speicher die Beschreibungen und die Descriptions des Events 
            id_to_delete = i['id']
            summary_for_event = i['summary']
            description_for_event = i["description"]
            alt_start = i['start']["dateTime"]
            alt_start = alt_start[:19]
            alte_zeit_start = datetime.strptime(alt_start,'%Y-%m-%dT%H:%M:%S') 
            neue_zeit_start = alte_zeit_start + timedelta(hours=2)
            
            alt_end = i['end']["dateTime"]
            alt_end = alt_end[:19]
            alte_zeit_end = datetime.strptime(alt_end,'%Y-%m-%dT%H:%M:%S') 
            neue_zeit_end = alte_zeit_end + timedelta(hours=2)

            neue_zeit_start = str(neue_zeit_start)
            neue_zeit_end = str(neue_zeit_end)

            neue_zeit_start = neue_zeit_start.replace(" ","T")
            neue_zeit_end = neue_zeit_end.replace(" ","T")

            print(type(neue_zeit_start))
            print(neue_zeit_start)

            post_body = {
                'summary': ""+summary_for_event+"",
                'location': '800 Howard St., San Francisco, CA 94103',
                'description': ""+description_for_event+"",
                'start': {
                'dateTime': ""+neue_zeit_start+"",
                'timeZone': 'Europe/Berlin',
                },
                'end': {
                'dateTime': ""+neue_zeit_end+"",
                'timeZone': 'Europe/Berlin',
                }
                }
                

            service.events().insert(calendarId="aqp0pv2uivgeqlk95vp60fbl3k@group.calendar.google.com",body = post_body).execute() 
            
            # Alten Termin löschen 
            service.events().delete(calendarId='aqp0pv2uivgeqlk95vp60fbl3k@group.calendar.google.com', eventId=i['id']).execute()

        return("erfolgreich")
    else:
        return("401 unauthorized")   

     


    """HTTP Cloud Function.
    Args:
        request (flask.Request): The request object.
        <http://flask.pocoo.org/docs/1.0/api/#flask.Request>
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>.

    """

