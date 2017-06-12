# coding: utf-8

from datetime import datetime
from datetime import timedelta
from pyarlo.const import LIBRARY_ENDPOINT, FILTER_VIDEO_ONLY, FILTER_SNAPSHOT_ONLY

class ArloMediaLibrary(object):

    def __init__(self, arlo_session):
        self._session = arlo_session;

    def __repr__(self):
        return "<{0}: {1}>".format(self.__class__.__name__, self._session.userid);

    def load(self, cam, days, latest = False, filter = None):
        medias = [];
        url = LIBRARY_ENDPOINT;
        
        now = datetime.today();
        date_from = (now - timedelta(days=days)).strftime('%Y%m%d');
        date_to = now.strftime('%Y%m%d');

        params = {'dateFrom': date_from, 'dateTo': date_to};
        data = self._session.query(url,
                                   method = 'POST',
                                   extra_params = params).get('data');

        for media in data:
            src_cam_id = media.get('deviceId');

            if (cam.device_id == src_cam_id) and ((filter and media.get('contentType') == filter) or filter == None):
                medias.append(ArloMedia(media, cam, self._session)); 

        if latest:
            if len(medias) > 0:
                return medias[0];
            else:
                raise ValueError('No media available for ' + cam.name);
            
        return medias

class ArloMedia(object):

    def __init__(self, attrs, camera, arlo_session):
        self._attrs = attrs
        self._camera = camera
        self._session = arlo_session

    def __repr__(self):
        return "<{0}: {1}>".format(self.__class__.__name__, self._name)

    @property
    def _name(self):
        return "{0} {1}".format(
            self._camera.name,
            self.timestamp)

    # pylint: disable=invalid-name
    @property
    def id(self):
        return self._attrs.get('name')

    @property
    def timestamp(self):
        return self._attrs.get('utcCreatedDate');

    @property
    def content_type(self):
        return self._attrs.get('contentType')

    @property
    def camera(self):
        return self._camera

    @property
    def media_duration_seconds(self):
        return self._attrs.get('mediaDurationSecond')

    @property
    def triggered_by(self):
        return self._attrs.get('reason')

    @property
    def thumbnail_url(self):
        return self._attrs.get('presignedThumbnailUrl')

    @property
    def content_url(self):
        return self._attrs.get('presignedContentUrl')

# vim:sw=4:ts=4:et:
