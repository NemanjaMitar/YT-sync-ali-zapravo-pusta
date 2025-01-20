from flask import Flask, render_template, request, redirect, session
from flask_socketio import SocketIO, emit
from urllib.parse import urlparse, parse_qs
import time


def extract_video_id(url):
    query = urlparse(url).query
    params = parse_qs(query)
    return params.get('v', [None])[0]

app = Flask(__name__)
#app.secret_key = 'your_secret_key'  # Replace with a secure random string
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

current_video = {"id": None, "time": 0, "paused": True}

# Home route
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        # Get the submitted YouTube URL and extract the video ID
        formName = request.form.get("name")
        video_id = extract_video_id(formName)
        
        # Store the video ID in the session
        session['video_id'] = video_id
        current_video["id"] = video_id
        current_video["time"] = 0
        current_video["paused"] = False
        socketio.emit('sync_video', current_video, to="broadcast")
        return render_template("link.html", name=video_id, start_time=0)  # Redirect to the link page

    # Check if a video ID is already stored in the session
    video_id = session.get('video_id', None)
    return render_template("index.html", name=video_id)

# Link route
@app.route("/link", methods=["GET"])
def link():
    # Retrieve the video ID from the session
    video_id = session.get('video_id', None)
    global current_video
    return render_template("link.html", name=video_id, start_time=current_video["time"])

@socketio.on("sync_request")
def sync_request():
    # Send the current video state to the requesting client
    global current_video
    emit("sync_video", current_video)

@socketio.on("update_time")
def update_time(data):
    # Update the global video time based on the client
    global current_video
    current_video["time"] = data["time"]

def extract_video_id(url):
    from urllib.parse import urlparse, parse_qs
    query = urlparse(url).query
    params = parse_qs(query)
    return params.get("v", [None])[0]

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)