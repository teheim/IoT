FROM python:3.8-slim

RUN pip install paho-mqtt

COPY weather_station.py /weather_station.py

CMD ["python", "/weather_station.py"]
