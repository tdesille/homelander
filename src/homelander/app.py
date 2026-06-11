import streamlit as st
import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion
import json
import atexit

DEFAULT_MQTT_TOPIC = "zigbee2mqtt"
DEFAULT_PRETTY_NAME = "0xf0d1b800001d0901"
DEFAULT_DIM_VALUE = 100


# ----------------------------
# MQTT CALLBACK
# ----------------------------
def on_message(client, userdata, msg):
    raw = msg.payload.decode(errors="ignore")

    # Handle empty payload safely
    if not raw:
        st.session_state.component_list = {
            "topic": msg.topic,
            "payload": None,
            "retain": msg.retain,
        }
        return

    # Try JSON parsing safely
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        parsed = raw  # fallback to raw string

    st.session_state.component_list = {
        "topic": msg.topic,
        "payload": parsed,
        "retain": msg.retain,
    }

# ----------------------------
# CLEANUP (important for Ctrl+C / reruns)
# ----------------------------
def cleanup():
    client = st.session_state.get("mqtt_client")
    if client:
        try:
            client.loop_stop()
            client.disconnect()
        except Exception:
            pass


atexit.register(cleanup)


# ----------------------------
# SESSION INIT
# ----------------------------
def init_session_state():
    if "current_light_status" not in st.session_state:
        st.session_state.current_light_status = "ON"

    if "component_list" not in st.session_state:
        st.session_state.component_list = {}

    if "mqtt_client" not in st.session_state or not st.session_state.mqtt_client.is_connected():

        # If an old client exists, clean it first
        old = st.session_state.get("mqtt_client")
        if old:
            try:
                old.loop_stop()
                old.disconnect()
            except Exception:
                pass

        client = mqtt.Client(callback_api_version=CallbackAPIVersion.VERSION2)

        client.on_message = on_message

        client.connect("localhost", 1883, 60)

        # subscribe AFTER connect + callback setup
        client.subscribe(f"{DEFAULT_MQTT_TOPIC}/bridge/devices")

        # IMPORTANT: background thread loop
        client.loop_start()

        st.session_state.mqtt_client = client

        print("MQTT client initialized and connected")


# ----------------------------
# TOPIC BUILDER
# ----------------------------
def build_topic():
    return f"{st.session_state.mqtt_topic}/{st.session_state.pretty_name}/set"


# ----------------------------
# LIGHT CONTROL
# ----------------------------
def change_light_status():
    client = st.session_state.mqtt_client
    topic = build_topic()

    if st.session_state.current_light_status == "ON":
        payload = json.dumps({"state": "OFF"})
        client.publish(topic, payload=payload, qos=0, retain=False)
        st.session_state.current_light_status = "OFF"

    else:
        payload = json.dumps({"state": "ON"})
        client.publish(topic, payload=payload, qos=0, retain=False)
        st.session_state.current_light_status = "ON"


def dim_light():
    client = st.session_state.mqtt_client
    topic = build_topic()

    brightness = int(st.session_state.dim_value * 2.55)
    payload = json.dumps({"brightness": brightness})

    client.publish(topic, payload=payload, qos=0, retain=False)


# ----------------------------
# INIT
# ----------------------------
init_session_state()

# ----------------------------
# UI
# ----------------------------
st.text_input("MQTT Topic", key="mqtt_topic", value=DEFAULT_MQTT_TOPIC)
st.text_input("Pretty Name", key="pretty_name", value=DEFAULT_PRETTY_NAME)

if st.button("Switch light on/off"):
    change_light_status()

st.slider(
    "Dim light",
    0,
    100,
    value=DEFAULT_DIM_VALUE,
    on_change=dim_light,
    key="dim_value",
)

st.divider()

st.write("Latest MQTT message:")
st.json(st.session_state.component_list)