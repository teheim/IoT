import paho.mqtt.client as mqtt
import sqlite3
import json
import datetime
from flask import Flask, render_template, request

app = Flask(__name__)

# MQTT Settings
MQTT_BROKER = "192.168.244.128"
MQTT_PORT = 1883
MQTT_TOPIC = "weather/temperature"

# SQLite Connection
db = sqlite3.connect('weather_data.db', check_same_thread=False)
cursor = db.cursor()

# Initialize SQLite Database
def init_db():
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS weather_data (
            id INTEGER PRIMARY KEY,
            topic TEXT,
            temperature REAL,
            timestamp DATETIME
        )
    ''')
    db.commit()

# MQTT Callback Functions
def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT Broker!")
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
    log_to_db(msg.topic, msg.payload.decode())

def log_to_db(topic, temperature):
    try:
        # Format the timestamp to exclude seconds and milliseconds
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        query = "INSERT INTO weather_data (topic, temperature, timestamp) VALUES (?, ?, ?)"
        values = (topic, temperature, current_time)
        cursor.execute(query, values)
        db.commit()
    except Exception as e:
        print(f"Error: {str(e)}")

# Web Server Routes
@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    limit = 10  # Number of records per page
    offset = (page - 1) * limit

    date_filter = request.args.get('date')
    if date_filter:
        query = "SELECT * FROM weather_data WHERE DATE(timestamp) = ? LIMIT ? OFFSET ?"
        total_query = "SELECT COUNT(*) FROM weather_data WHERE DATE(timestamp) = ?"
        cursor.execute(total_query, (date_filter,))
        total_pages = (cursor.fetchone()[0] + limit - 1) // limit  # Calculate total pages
        cursor.execute(query, (date_filter, limit, offset))
    else:
        cursor.execute("SELECT COUNT(*) FROM weather_data")
        total_pages = (cursor.fetchone()[0] + limit - 1) // limit  # Calculate total pages
        cursor.execute("SELECT * FROM weather_data LIMIT ? OFFSET ?", (limit, offset))

    data = cursor.fetchall()

    # Fetch data for today's graph
    today = datetime.date.today().strftime("%Y-%m-%d")
    cursor.execute("SELECT timestamp, temperature FROM weather_data WHERE DATE(timestamp) = ?", (today,))
    graph_data = cursor.fetchall()

    return render_template('index.html', data=data, page=page, total_pages=total_pages, date_filter=date_filter, graph_data=graph_data)

# MQTT Client Setup
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# Initialize the database
init_db()

# Start the MQTT client loop
client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_start()

# Start Flask App
if __name__ == '__main__':
    try:
        app.run(debug=True)
    except Exception as e:
        print(f"Flask Server Error: {str(e)}")
        client.loop_stop()
