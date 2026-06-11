import streamlit as st
import paho.mqtt.client as mqtt
import json
from enum import Enum

# Constants
MQTT_BROKER_ADDRESS = "localhost"
MQTT_BROKER_PORT = 1883
MQTT_TOPIC = "zigbee2mqtt"

# Devices
FRIENDLY_NAMES_MAPPING = {"0xf0d1b800001d0901" : "droite chambre de Téo"}

# Devices architectures

class LightBulbStates(Enum):
    ON = "ON"
    OFF = "OFF"

# MQTT Client Setup
def init_mqtt_client():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.connect(MQTT_BROKER_ADDRESS, MQTT_BROKER_PORT)
    st.session_state.client = client

def connect_mqtt():
    st.session_state.client.loop_start()

def build_payload(ieee_name: str) -> str:
    #define which state to send
    if st.session_state[f"{ieee_name}_actual_state"] :
        state = LightBulbStates.ON.value
    else :
        state = LightBulbStates.OFF.value
    
    # define brightness to send
    brightness = int(st.session_state[f"{ieee_name}_brightness"]*2.55)

    return json.dumps({"state": state, "brightness": brightness})

def send_device_update(ieee_name: str):
    payload = build_payload(ieee_name)
    connect_mqtt()
    print(f"Sending update for {ieee_name}: {payload}")
    st.session_state.client.publish(f"{MQTT_TOPIC}/{ieee_name}/set", payload)

def widget_one_light (ieee_name: str) :
    st.header(f"{FRIENDLY_NAMES_MAPPING[ieee_name]}")
    st.toggle("ON/OFF", key=f"{ieee_name}_actual_state", on_change=send_device_update, args=(ieee_name, ), value = True)
    st.slider("Brightness", 0, 100, key=f"{ieee_name}_brightness", on_change=send_device_update, args=(ieee_name, ), value = 100)    
    st.divider()


init_mqtt_client()
for ieee_name in FRIENDLY_NAMES_MAPPING.keys():
    widget_one_light(ieee_name)
