from dash import Dash, html, dcc, Input, Output, callback
import dash_daq as daq

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization

import json
import base64
from threading import Event, Thread
import paho.mqtt.client as mqtt
import time
import os

broker_hostname = "localhost"
port = 1883

global public_key
global collision_info
global forecast_data
global public_key_received_event

forecast_data = ""
collision_info = ""
public_key_received_event = Event()

def on_connect(client, userdata, flags, return_code):
    if return_code == 0:
        print('Connected!')
        client.subscribe("PublicKey")
        client.subscribe("MotionCollision")
        client.subscribe("WeatherForecast")
    else:
        print("Could not connect. Return code " + return_code)

def on_message(client, userdata, message):
    global public_key, collision_info, forecast_data, public_key_received_event
    if message.topic == "WeatherForecast":
        forecast_data = json.loads(message.payload.decode('utf-8'))
    elif message.topic == "MotionCollision":
        collision_info = json.loads(message.payload.decode('utf-8'))
    elif message.topic == "PublicKey":
        public_key_data = json.loads(message.payload.decode('utf-8'))
        public_key_bytes = base64.b64decode(public_key_data.get('publickey'))
        public_key = serialization.load_pem_public_key(public_key_bytes)
        public_key_received_event.set()
        os.system('clear')
        print('Public Key Recieved. You may access at http://0.0.0.0:8050/')
        
def connect():
    os.system('clear')
    client = mqtt.Client("Client3")
    client.username_pw_set(username="user3", password="pass3")
    client.on_connect = on_connect
    client.on_message = on_message
    
    client.connect(broker_hostname, port)
    client.loop_start()
    
    try:
        time.sleep(999)
    finally:
        client.loop_stop()

app = Dash(__name__)
value = 1

def generate_weather_stub(obj):
    if obj.get('intensity') == "n/a":
        return str(obj.get('type'))
    return f"{obj.get('intensity')} {obj.get('type')}"

def generate_traffic_stub(obj):
    if obj.get('detection').get('type') == 'motion':
        if obj.get('detection').get('value'):
            return f"Motion Detected at {obj.get('postalCode')} on {obj.get('date')}"
        return 'No motion detected'
    elif obj.get('detection').get('type') == 'collision':
        if obj.get('detection').get('value'):
            return f"Collision Detected at {obj.get('postalCode')} on {obj.get('date')}"
        return "No collision detected"
    
def show_photo(value):
    if value != "":
        return f'data:image/jpg;base64,{collision_info.get("image")}'
    return 'No evidence taken.'

def is_signature_valid(signature, message, pk):
    try:
        pk.verify(
            signature,
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except InvalidSignature:
        return False
    
def remove_key(dict, keys):
    return {
        x: dict[x] for x in dict if x not in keys
    }

@callback(
    Output('temp', 'value'),
    Output('temp', 'label'),
    Output('weather-stub', 'children'),
    Output('weather-title', 'children'),
    Input('interval-component', 'n_intervals')
)
def set_temp(value):
    global public_key, public_key_received_event, forecast_data
    public_key_received_event.wait()

    if forecast_data == "":
        return 0, 0, 0, 'No data found'
    elif public_key is not None and is_signature_valid(bytes.fromhex(forecast_data.get('signature')), str.encode(json.dumps(remove_key(forecast_data, 'signature'))), public_key):
        return forecast_data.get('temperature'), f"{forecast_data.get('temperature')}°C", generate_weather_stub(forecast_data.get('condition')), f"Weather Data at {forecast_data.get('postalCode')} on {forecast_data.get('date')}"
    return 0, 0, 0, 'No data found'

@callback(
    Output('traffic-title', 'children'),
    Output('traffic-evidence', 'src'),
    Input('interval-component', 'n_intervals')
)
def set_collision(value):
    global public_key, public_key_received_event, collision_info
    public_key_received_event.wait()
    
    if collision_info == "":
        return 'No data found', 'No photo taken'
    elif public_key is not None and is_signature_valid(bytes.fromhex(collision_info.get('signature')), str.encode(json.dumps(remove_key(collision_info, 'signature'))), public_key):
        return generate_traffic_stub(collision_info), show_photo(collision_info.get('image'))
    return 'No data found', 'No photo taken'

app.layout = html.Div([
    html.H1('Weather Forecast', id='weather-title'),
    daq.Thermometer(
        id="temp",
        min=-40,
        max=40,
    ),
    html.H2(id="weather-stub"),
    html.Hr(style={
        'width': '100%'    
    }),
    ################
    html.H1('Motion Collision', id='traffic-title'),
    html.Img(id='traffic-evidence'),
    dcc.Interval(
        id='interval-component',
        interval=2*1000,
        n_intervals=0
    ),
], style={
    'font-family': '"Comic Sans MS"',
    'display': 'flex',
    'justify-content': 'center',
    'flex-direction': 'column',
    'align-items': 'center',
    'width': '100%'
})

if __name__ == '__main__':
    thread = Thread(target=connect, daemon=False)
    os.system('clear')
    thread.start()
    app.run(debug=True, host='0.0.0.0')