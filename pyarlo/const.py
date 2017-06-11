"""Constants used by Python Arlo."""

# API Endpoints
API_URL = "https://arlo.netgear.com/hmsweb"

DEVICES_ENDPOINT = API_URL + "/users/devices"
LIBRARY_ENDPOINT = API_URL + "/users/library"
LOGIN_ENDPOINT = API_URL + "/login"
LOGOUT_ENDPOINT = API_URL + "/logout"
NOTIFY_ENDPOINT = API_URL + "/users/devices/notify/{0}"
STREAM_ENDPOINT = API_URL + "/users/devices/startStream"
SNAPSHOT_ENDPOINT = API_URL + "/users/devices/takeSnapshot"

FILTER_VIDEO_ONLY = "video/mp4";
FILTER_SNAPSHOT_ONLY = "image/jpg";

# define action modes
ACTION_MODES = {
    'armed': 'mode1',
    'disarmed': 'mode0',
    'home': 'mode2',
    'schedule': 'true',
}

# define body used when executing an action
RUN_ACTION_BODY = {
    'action': 'set',
    'from': None,
    'properties': None,
    'publishResponse': 'true',
    'resource': 'modes',
    'to': None
}

STREAMING_BODY = {
    'action': 'set',
    'from': None,
    'properties': {'activityState': 'startPositionStream'},
    'publishResponse': 'true',
    'resource': None,
    'to': None,
    'transId': "",
}

SNAPSHOT_BODY = {
    "parentId": "4R03737AA3842", 
    "deviceId": None, 
    "olsonTimeZone": "America/New_York",
}

# vim:sw=4:ts=4:et:
