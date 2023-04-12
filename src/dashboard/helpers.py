import json
import requests

API_ENDPOINT = 'https://discord.com/api/v10'
CLIENT_ID = '898563823420735558'
CLIENT_SECRET = 'jq_spTianPsoVymdNKe8bO9u_5Unufpy'
REDIRECT_URI = 'http://127.0.0.1:8000/oauth/discord'

def getToken(code):
    data = {
    'client_id': CLIENT_ID,
    'client_secret': CLIENT_SECRET,
    'grant_type': 'authorization_code',
    'code': code,
    'redirect_uri': REDIRECT_URI
    }
    headers = {
    'Content-Type': 'application/x-www-form-urlencoded'
    }
    r = requests.post('%s/oauth2/token' % API_ENDPOINT, data=data, headers=headers)
    r.raise_for_status()
    return r.json()['access_token']

def getTokenGuilds(token):
    resp = requests.get(
        API_ENDPOINT + "/users/@me/guilds", 
        headers={"Authorization": f'Bearer {token}'}
        )
    resp.raise_for_status()
    return resp.json()

def getBotCommonGuilds(bot_token, user_token):
    user_guilds = getTokenGuilds(user_token)
    bot_guilds = requests.get('http://localhost:5001/bot/guilds').json()

    common_guilds = []
    for guild in user_guilds:
        if guild['owner'] == True and guild['id'] in bot_guilds:
            common_guilds.append(guild)

    return common_guilds

def getUserData(token):
  resp = requests.get(
    API_ENDPOINT + '/users/@me',
    headers={"Authorization": f'Bearer {token}'}
  )
  resp.raise_for_status()
  return resp.json()