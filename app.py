from flask import Flask, redirect, request, session, url_for
from spotify_control import SpotifyControl
import os
import threading

# Inicializar Flask
app = Flask(__name__)
app.secret_key = os.urandom(24)

# Inicializar control de Spotify
spotify = SpotifyControl()

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login')
def login():
    auth_url = spotify.sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/callback')
def callback():
    if 'code' not in request.args:
        return "Código de autorización no encontrado", 400
    
    token_info = spotify.sp_oauth.get_access_token(request.args['code'])
    session['token'] = token_info['access_token']
    
    return redirect(url_for('control'))

@app.route('/control')
def control():
    if 'token' not in session:
        return redirect(url_for('login'))

    try:
        playback_status = spotify.start_playback()
        return playback_status
    except Exception as e:
        return f"Error al reproducir música: {str(e)}", 500

# Función para ejecutar Flask en un hilo separado
def run_flask():
    app.run(port=8080, debug=False, use_reloader=False)

# Iniciar Flask en un hilo separado
flask_thread = threading.Thread(target=run_flask)
flask_thread.start()
