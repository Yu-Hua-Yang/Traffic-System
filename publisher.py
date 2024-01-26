import base64
import time
import paho.mqtt.client as mqtt
from picamera2 import Picamera2
import requests
import json
import datetime
from keys.asymetric_keys import sign
import jwt
from threading import Thread
from pathlib import Path
from cryptography.hazmat.primitives import serialization

SECRET = "MY SECRET"

def initialize_camera():
    picam2 = Picamera2()
    camera_config = picam2.create_preview_configuration()
    picam2.configure(camera_config)
    picam2.start()
    return picam2

def capture_picture(picam2, picture_name, log_string):
    picam2.capture_file(picture_name)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d|%H:%M:%S")
    with open("logs.txt", "a") as file:
        file.write(f"{log_string} {timestamp}\n")

def motion_collision_detection(picam2, client, private_key):
    traffic_lights = ["Green", "Yellow", "Red"]
    while True:
        for light in traffic_lights:
            print(f"Light is {light}")
            time.sleep(2)
            handle_light(picam2, client, private_key, light)

def handle_light(picam2, client, private_key, light):
    response_data = get_motion_data(f"http://localhost:5080/MotionCollision?token={client.token.decode('utf-8')}")
    if response_data['detection']['type'] == 'collision' and response_data['detection']['value']:
        capture_picture(picam2, "traffic_photo.jpg", "Investigate evidence traffic_photo.jpg")
        handle_broken_law(client, response_data, private_key)
    else:
        if light == "Red":
            if response_data["detection"]["value"]:
                capture_picture(picam2, "traffic_photo.jpg", "Investigate evidence traffic_photo.jpg")
                handle_broken_law(client, response_data, private_key)
            else:
                response_data["image"] = ""
                sign_motion(client, response_data, private_key)      
        else:
            response_data["image"] = ""
            sign_motion(client, response_data, private_key)

def handle_broken_law(client, response_data, private_key):
    filename = './traffic_photo.jpg'
    with open(filename, mode='rb') as file:
        img_data = file.read()
    encoded_img = base64.b64encode(img_data).decode('utf-8')
    response_data["image"] = encoded_img
    sign_motion(client, response_data, private_key)
    
def sign_motion(client, response_data, private_key):
    motion_signature = sign(str.encode(json.dumps(response_data)), private_key)
    response_data['signature'] = motion_signature.hex()

    publish_message(client, 'MotionCollision', response_data)

def publish_message(client, topic, data):
    result = client.publish(topic=topic, payload=json.dumps(data))
    status = result[0]
    if status == 0:
        print(f"Message has been published on {topic} topic")
    else:
        print(f"Publishing of message to topic {topic} has failed")

def weather_detection(client, private_key):
    while True:
        response_data = get_weather_data(f"http://localhost:5080/WeatherForecast?token={client.token.decode('utf-8')}")
        handle_weather_data(client, response_data, private_key)
        time.sleep(2.5)

def handle_weather_data(client, response_data, private_key):
    weather_signature = sign(str.encode(json.dumps(response_data)), private_key)
    response_data["signature"] = weather_signature.hex()
    publish_message(client, 'WeatherForecast', response_data)

def on_connect(client, userdata, flags, return_code):
    print("CONNACK received with code %s." % return_code)
    if return_code == 0:
        print(f"${client._client_id.decode('utf-8')} connected to broker.")
        headers = {
          "alg": "HS256",
          "typ": "JWT"
        }
        expire_on = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        payload = {
          "sub": "client",
          "client": f"{client._client_id.decode('utf-8')}",
          "exp": expire_on.timestamp()
        }
        client.token = jwt.encode(payload=payload, key=SECRET, headers=headers)
    else:
        print(f"Could not connect. Return code: {return_code}")

def get_weather_data(weather_api_url):
    response = requests.get(weather_api_url)
    return json.loads(response.text)

def get_motion_data(motion_api_url):
    response = requests.get(motion_api_url)
    return json.loads(response.text)

if __name__ == '__main__':
    print('Publisher is starting up . . .')

    broker_hostname = "localhost"
    port = 1883

    client1 = mqtt.Client(client_id="Client1", userdata=None)
    client2 = mqtt.Client(client_id="Client2", userdata=None)
    client1.on_connect = on_connect
    client2.on_connect = on_connect

    client1.username_pw_set(username="user1", password="pass1")
    client2.username_pw_set(username="user2", password="pass2")


    client1.connect(broker_hostname, port, 60)
    client2.connect(broker_hostname, port, 60)

    client1.loop_start()
    client2.loop_start()

    private_key_pem_in_bytes = Path("./keys/private_key.pem").read_bytes()
    public_key_pem_in_bytes = Path("./keys/public_key.pem").read_bytes()
    private_key_from_pem = None

    try:
        private_key_from_pem = serialization.load_pem_private_key(
            private_key_pem_in_bytes,
            password=b"my secret",
        )
        public_key_from_pem = serialization.load_pem_public_key(public_key_pem_in_bytes)
        print("Keys Correctly Loaded")
    except ValueError:
        print("Incorrect Password")

    picam2 = initialize_camera()
    weather_thread = Thread(target=weather_detection, args=[client1, private_key_from_pem])
    collision_thread = Thread(target=motion_collision_detection, args=[picam2, client2, private_key_from_pem])

    try:
        public_key_pem_data = base64.b64encode(public_key_pem_in_bytes).decode('utf-8')
        publish_message(client1, 'PublicKey', {'publickey': public_key_pem_data})

        weather_thread.start()
        collision_thread.start()

    except KeyboardInterrupt:
        picam2.stop()
        client1.loop_stop()
        client2.loop_stop()
    except Exception:
        picam2.stop()
        client1.loop_stop()
        client2.loop_stop()
