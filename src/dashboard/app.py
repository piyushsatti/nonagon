from datetime import timedelta
from os import getlogin
from flask import Flask, redirect, render_template, request, session
import requests
from helpers import getToken, getUserData, getBotCommonGuilds

app = Flask(__name__)
app.secret_key = "hi"
bot = ""
# app.permanent_session_lifetime = timedelta(seconds=60)

def getLoginStatus(): 
  return False if 'token' not in session else True

@app.route('/')
def home():
  if getLoginStatus():
    user_data = getUserData(session['token'])
    data = {
      'username': f"{user_data['username']}",
      'avatar': f"https://cdn.discordapp.com/avatars/{user_data['id']}/{user_data['avatar']}.png"
    }
    session['user_data'] = data
    return render_template("home/index.jinja", data=data)
  else:
    return render_template("home/index.jinja")

@app.route("/oauth/discord")
def oauth():
    if 'token' not in session:
        code = request.args.get('code')
        token = getToken(code)
        session["token"] = token
    return redirect('/')

@app.route("/dashboard")
def dashboard():
    if getLoginStatus():
        args = request.args
        if 'guild_id' in args:
            guild_state = requests.get(f"http://127.0.0.1:5001/guild/{args['guild_id']}/state" )
            guild_custom = requests.get(f"http://127.0.0.1:5001/guild/{args['guild_id']}/customcommands")
            guild_timed = requests.get(f"http://127.0.0.1:5001/guild/{args['guild_id']}/timedmessages")
            
            guild_state.raise_for_status()
            guild_custom.raise_for_status()
            guild_timed.raise_for_status()
            
            guild = {
                'state': guild_state.json(),
                'customcommands': guild_custom.json(),
                'timedmsgs': guild_timed.json()
            }

            return guild
        else:
            global bot
            common_guilds = getBotCommonGuilds(bot_token = bot, user_token = session['token'])
            return render_template(
                "home/dashboard.jinja", 
                guilds=common_guilds, 
                data=session['user_data']
                )
    else:
        return redirect('/')

@app.route("/dashboard/{guild_id}")
def guildDashboard(guild_id):
    if getLoginStatus():
        return guild_id
    else:
        return redirect('/')

@app.route("/logout")
def logout():
    if getLoginStatus():
        session.pop('token')
    
    return redirect('/')


if __name__ == '__main__':
	app.run(debug=True, port=8000)