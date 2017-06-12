# coding: utf-8

from pyarlo.const import (
    STREAM_ENDPOINT, SNAPSHOT_ENDPOINT, STREAMING_BODY, SNAPSHOT_BODY, FILTER_VIDEO_ONLY, FILTER_SNAPSHOT_ONLY)
from pyarlo.media import ArloMediaLibrary

class ArloCamera(object):

    def __init__(self, name, attrs, arlo_session):
        self.name = name
        self._attrs = attrs
        self._session = arlo_session

    def __repr__(self):
        return "<{0}: {1}>".format(self.__class__.__name__, self.name)

    # pylint: disable=invalid-name
    @property
    def device_id(self):
        return self._attrs.get('deviceId')

    @property
    def device_type(self):
        return self._attrs.get('deviceType')

    @property
    def model_id(self):
        return self._attrs.get('modelId')

    @property
    def hw_version(self):
        return self._attrs.get('properties').get('hwVersion')

    @property
    def timezone(self):
        return self._attrs.get('properties').get('olsonTimeZone')

    @property
    def unique_id(self):
        return self._attrs.get('uniqueId')

    @property
    def user_id(self):
        return self._attrs.get('userId')

    @property
    def unseen_videos(self):
        self.update()
        return self._attrs.get('mediaObjectCount')

    @property
    def user_role(self):
        return self._attrs.get('userRole')

    @property
    def last_image_url(self):
        self.update();
        return self._attrs.get('presignedLastImageUrl');

    @property
    def last_video(self):
        library = ArloMediaLibrary(self._session);
        return library.load(self, 1, latest = True, filter = FILTER_VIDEO_ONLY);
            
    @property
    def last_snapshot(self):
        library = ArloMediaLibrary(self._session);
        return library.load(self, 1, latest = True, filter = FILTER_SNAPSHOT_ONLY);

    @property
    def medias(self, days = 7):
        library = ArloMediaLibrary(self._session);
        
        try:
            return library.load(self, days);
        except (AttributeError, IndexError):
            return [];

    @property
    def xcloud_id(self):
        return self._attrs.get('xCloudId');
        
    def take_snapshot(self):
        stream = self.start_stream();
        if stream != True:
            raise ValueError('Failed to start stream for ' + self.name);
    
        url = SNAPSHOT_ENDPOINT;

        params = SNAPSHOT_BODY;
        params['deviceId'] = self.device_id;

        headers = {'xCloudId': self.xcloud_id};

        ret = self._session.query(url,
                                  method='POST',
                                  extra_params = params,
                                  extra_headers = headers);

        if ret.get('success') != True:
            raise ValueError('Failed to take snapshot from ' + self.name);
        
    def start_stream(self):
        url = STREAM_ENDPOINT

        # override params
        params = STREAMING_BODY
        params['from'] = "{0}_web".format(self.user_id)
        params['to'] = self.device_id
        params['resource'] = "cameras/{0}".format(self.device_id)
        params['transId'] = "web!{0}".format(self.xcloud_id)

        # override headers
        headers = {'xCloudId': self.xcloud_id}

        ret = self._session.query(url,
                                  method='POST',
                                  extra_params=params,
                                  extra_headers=headers)

        return ret.get('success') == True;

    def update(self):
        self._attrs = self._session.refresh_attributes(self.name);

# vim:sw=4:ts=4:et:
