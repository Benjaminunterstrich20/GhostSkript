from flask import Flask, render_template, request
from flask_socketio import SocketIO, join_room, leave_room, emit
import base64

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Chats im RAM: {raumcode: [ {user, msg, img} ]}
rooms = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat')
def chat():
    room = request.args.get('room')
    username = request.args.get('username')
    if not room or not username:
        return "Room and username required!", 400
    if room not in rooms:
        rooms[room] = []
    return render_template('chat.html', room=room, username=username, messages=rooms[room])

@socketio.on('join')
def on_join(data):
    username = data['username']
    room = data['room']
    join_room(room)
    emit('status', {'msg': f'{username} ist dem Raum beigetreten.'}, room=room)

@socketio.on('message')
def handle_message(data):
    room = data['room']
    username = data['username']
    msg = data.get('msg')
    img = data.get('img')  # base64 encoded image string or None
    
    message = {'user': username, 'msg': msg, 'img': img}
    rooms.setdefault(room, []).append(message)
    emit('message', message, room=room)

if __name__ == '__main__':
    socketio.run(app, debug=True)
