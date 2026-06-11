import time as time
import json as json
from homelander.utils.schemas import ControllableDeviceInfos

def on_message_update_list(client, userdata, msg):
    json_device_list = json.loads(msg.payload.decode())
    controllable_devices = parse_json_to_get_controllable_devices_infos(json_device_list)
    update_db_with_device_list(controllable_devices)

