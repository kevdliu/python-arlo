# coding: utf-8
"""Base Python Class file for Netgear Arlo camera module."""
import requests

from pyarlo.base_station import ArloBaseStation
from pyarlo.camera import ArloCamera
from pyarlo.media import ArloMediaLibrary
from pyarlo.const import (
    DEVICES_ENDPOINT, LOGIN_ENDPOINT, LOGOUT_ENDPOINT)
    
class PyArlo(object):
    """Base object for Netgar Arlo camera."""

    def __init__(self, username=None, password=None):
        """Create a PyArlo object.

        :param username: Arlo user email
        :param password: Arlo user password

        :returns PyArlo base object
        """
        self.authenticated = None
        self.country_code = None
        self.date_created = None
        self.userid = None
        self.__token = None
        self.__headers = None
        self.__params = None

        # set username and password
        self.__password = password
        self.__username = username
        self.session = requests.Session()

        # login user
        if self.login() == False:
            raise ValueError('Failed to login to Arlo');

        # pylint: disable=invalid-name
        self.ArloMediaLibrary = ArloMediaLibrary(self)

    def __repr__(self):
        """Object representation."""
        return "<{0}: {1}>".format(self.__class__.__name__, self.userid)

    def login(self):
        """Login to the Arlo account."""
        return self._authenticate()

    def _authenticate(self):
        """Authenticate user and generate token."""
        self.cleanup_headers()
        url = LOGIN_ENDPOINT
        data = self.query(url, method='POST')

        if isinstance(data, dict) and data.get('success') == True:
            data = data.get('data')
            self.authenticated = data.get('authenticated')
            self.country_code = data.get('countryCode')
            self.date_created = data.get('dateCreated')
            self.__token = data.get('token')
            self.userid = data.get('userId')

            # update header with the generated token
            self.__headers['Authorization'] = self.__token
            return True;
        else:
            return False;

    def cleanup_headers(self):
        """Reset the headers and params."""
        headers = {'Content-Type': 'application/json'}
        headers['Authorization'] = self.__token
        self.__headers = headers

        params = {'email': self.__username, 'password': self.__password}
        self.__params = params
        
    def logout(self):
        data = self.query(LOGOUT_ENDPOINT, method='PUT');
        if data.get('success') != True:
            raise ValueError('Failed to logout of Arlo');

    def query(self,
              url,
              method='GET',
              extra_params=None,
              extra_headers=None,
              retry=3,
              raw=False):
        """
        Return a JSON object or raw session.

        :param url:  Arlo API URL
        :param method: Specify the method GET, POST or PUT. Default is GET.
        :param extra_params: Dictionary to be appended on request.body
        :param extra_headers: Dictionary to be apppended on request.headers
        :param retry: Attempts to retry a query. Default is 3.
        :param raw: Boolean if query() will return request object instead JSON.
        """
        response = None
        loop = 0

        # always make sure the headers and params are clean
        self.cleanup_headers()

        while loop <= retry:

            # override request.body or request.headers dictionary
            if extra_params:
                params = self.__params
                params.update(extra_params)
            else:
                params = self.__params

            if extra_headers:
                headers = self.__headers
                headers.update(extra_headers)
            else:
                headers = self.__headers

            loop += 1

            # define connection method
            if method == 'GET':
                req = self.session.get(url, headers=headers)
            elif method == 'PUT':
                req = self.session.put(url, json=params, headers=headers)
            elif method == 'POST':
                req = self.session.post(url, json=params, headers=headers)

            req.raise_for_status()
            if req.status_code == 200:
                if raw:
                    response = req
                else:
                    response = req.json()

                # leave if everything worked fine
                break
        return response

    @property
    def cameras(self):
        """Return all cameras linked on Arlo account."""
        return self.devices['cameras']

    @property
    def base_stations(self):
        """Return all base stations linked on Arlo account."""
        return self.devices['base_station']
        
    @property
    def base(self):
        bases = self.devices['base_station'];
        count = len(bases);
        
        if (count != 1):
            raise ValueError('Wrong number of Arlo base stations: ' + count);
        else:
            return bases[0];

    @property
    def devices(self):
        """Return all devices on Arlo account."""
        devices = {}
        devices['cameras'] = []
        devices['base_station'] = []

        url = DEVICES_ENDPOINT
        data = self.query(url)

        for device in data.get('data'):
            name = device.get('deviceName')
            if ((device.get('deviceType') == 'camera' or
                 device.get('deviceType') == 'arloq' or
                 device.get('deviceType') == 'arloqs') and
                    device.get('state') == 'provisioned'):
                devices['cameras'].append(ArloCamera(name, device, self))

            if device.get('deviceType') == 'basestation' and \
               device.get('state') == 'provisioned':
                devices['base_station'].append(ArloBaseStation(name,
                                                               device,
                                                               self))
        return devices

    def lookup_camera_by_id(self, device_id):
        """Return camera object by device_id."""
        camera = list(filter(
            lambda cam: cam.device_id == device_id, self.cameras))[0]
        if camera:
            return camera

    def refresh_attributes(self, name):
        """Refresh attributes from a given Arlo object."""
        url = DEVICES_ENDPOINT
        data = self.query(url).get('data')
        for device in data:
            if device.get('deviceName') == name:
                return device

    @property
    def is_connected(self):
        """Return connection status."""
        return bool(self.authenticated)

    def update(self):
        """Refresh object."""
        self._authenticate();

# vim:sw=4:ts=4:et:
