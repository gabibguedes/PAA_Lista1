import requests
from os import system
import json
from tokens import API_KEY, API_SECRET_KEY
import base64
import urllib.parse

TOKEN = ''


def create_barear_token():
    global TOKEN
    OAUTH2_TOKEN = 'https://api.twitter.com/oauth2/token'
    consumer_key = urllib.parse.quote(API_KEY)
    consumer_secret = urllib.parse.quote(API_SECRET_KEY)
    bearer_token = consumer_key + ':' + consumer_secret
    base64_encoded_bearer_token = base64.b64encode(
        bearer_token.encode('utf-8'))
    headers = {
        "Authorization": "Basic " + base64_encoded_bearer_token.decode('utf-8') + "",
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
        "Content-Length": "29"}

    response = requests.post(OAUTH2_TOKEN, headers=headers, data={
                             'grant_type': 'client_credentials'})
    to_json = response.json()
    TOKEN = to_json['access_token']


def get_user_id(username):
    header = {'authorization': 'Bearer ' + TOKEN}
    url = 'https://api.twitter.com/1.1/users/show.json?screen_name=' + username
    r = requests.get(url, headers=header)
    user = json.loads(r.text)
    return user['id']


def get_list(user, relationship, cursor=-1):
    header = {'authorization': 'Bearer ' + TOKEN}
    url = 'https://api.twitter.com/1.1/' + relationship + \
        '/list.json?screen_name=' + user + '&count=200&cursor=' + str(cursor)
    r = requests.get(url, headers=header)
    response = json.loads(r.text)
    try:
        next_page = response['next_cursor']
        friends = response['users'] 
    except KeyError:
        if 'errors' in response.keys():
            print('Rate Limit Exceeded')
        else:
            print('Private Account')
        next_page = 0
        friends = []
    if next_page != 0:
        friends = [*friends, *get_list(user, relationship, next_page)]

    return friends

def get_ids(user, relationship, cursor=-1):
    header = {'authorization': 'Bearer ' + TOKEN}
    url = 'https://api.twitter.com/1.1/' + relationship + \
        '/ids.json?screen_name=' + user + '&count=200&cursor=' + str(cursor)
    r = requests.get(url, headers=header)
    response = json.loads(r.text)
    rate_limit = False
    try:
        next_page = response['next_cursor']
        friends = response['ids']  
    except KeyError:
        if 'errors' in response.keys():
            rate_limit = True
            print('Rate Limit Exceeded')
        else:
            print('Private Account')
        next_page = 0
        friends = []

    if next_page != 0:
        friends = [*friends, *get_ids(user, relationship, next_page)]

    return friends, rate_limit

        # if(G.edges[edge_x, edge_y]['layer'] == 1):
        #     width=2,
        # color="red"
        # elif(G.edges[edge_x, edge_y]['layer'] == 2):
        #     width=1.5,
        #     color="orange"
        # else:
        #     width=1, 
        #     color='#888'
        # ),