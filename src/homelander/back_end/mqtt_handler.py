from homelander.back_end.back_end_api import ControllableDeviceInfos
from paho.mqtt import client as mqtt
from paho.mqtt.enums import CallbackAPIVersion
import json
from homelander.back_end.database_handler import sync_db_with_new_devices

def parse_json_to_get_controllable_devices_infos(json_device_list:list) -> list[ControllableDeviceInfos]:
    controllable_devices = []
    for json_device in json_device_list:
        if json_device["type"] == "Router":
            controllable_devices.append(ControllableDeviceInfos(friendly_name=json_device["friendly_name"], ieee_name=json_device["ieee_address"]))
    return controllable_devices

def on_message_update_list_devices(client, userdata, msg):
    json_device_list = json.loads(msg.payload.decode())
    controllable_devices = parse_json_to_get_controllable_devices_infos(json_device_list)
    sync_db_with_new_devices(controllable_devices)


client = mqtt.Client(callback_api_version=CallbackAPIVersion.VERSION2)
client.on_message = on_message_update_list_devices
client.connect("localhost", 1883, 60)
client.subscribe(f"zigbee2mqtt/bridge/devices")
client.loop_start()
client.loop_stop()