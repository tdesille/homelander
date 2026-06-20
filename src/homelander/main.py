import streamlit as st
import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion
import json
import os
from enum import Enum

# Constants
MQTT_BROKER_ADDRESS = os.getenv("MQTT_BROKER_ADDRESS", "localhost")
MQTT_BROKER_PORT = 1883
MQTT_TOPIC = "zigbee2mqtt"

# Devices
FRIENDLY_NAMES_MAPPING = {"0xf0d1b800001d0901": "droite chambre de Téo",
                          "0xf0d1b800001d0d62": "La bouuuuule"}

class LightBulbStates(Enum):
    ON = "ON"
    OFF = "OFF"

def init_mqtt_client():
    client = mqtt.Client(CallbackAPIVersion.VERSION2)
    client.connect(MQTT_BROKER_ADDRESS, MQTT_BROKER_PORT)
    st.session_state.client = client

def connect_mqtt():
    st.session_state.client.loop_start()

def build_payload(ieee_name: str) -> str:
    if st.session_state[f"{ieee_name}_actual_state"]:
        state = LightBulbStates.ON.value
    else:
        state = LightBulbStates.OFF.value
    brightness = int(st.session_state[f"{ieee_name}_brightness"] * 2.55)
    return json.dumps({"state": state, "brightness": brightness})

def send_device_update(ieee_name: str):
    payload = build_payload(ieee_name)
    connect_mqtt()
    st.session_state.client.publish(f"{MQTT_TOPIC}/{ieee_name}/set", payload)

def widget_one_light(ieee_name: str):
    st.header(f"{FRIENDLY_NAMES_MAPPING[ieee_name]}")
    st.toggle("ON/OFF", key=f"{ieee_name}_actual_state", on_change=send_device_update, args=(ieee_name,), value=True)
    st.slider("Brightness", 0, 100, key=f"{ieee_name}_brightness", on_change=send_device_update, args=(ieee_name,), value=100)
    st.divider()

def main():
    init_mqtt_client()
    for ieee_name in FRIENDLY_NAMES_MAPPING.keys():
        widget_one_light(ieee_name)

if __name__ == "__main__":
    main()