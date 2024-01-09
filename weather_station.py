import paho.mqtt.client as mqtt
import time
import random

# MQTT settings
MQTT_BROKER = "192.168.244.128"
MQTT_PORT = 1884
MQTT_TOPIC = "weather/temperature"

def main():
    client = mqtt.Client()
    client.connect(MQTT_BROKER, MQTT_PORT, 60)

    while True:
        temperature = random.uniform(20.0, 25.0)
        client.publish(MQTT_TOPIC, temperature)
        time.sleep(5)

if __name__ == "__main__":
    main()
