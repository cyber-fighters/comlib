import os
import requests


class Unconfigured(Exception):
    """Inidicate that the communication is unconfigured."""
    pass


class StatusFailed(Exception):
    """Inidicate that the status communication failed."""
    pass


class BackyardCom:
    __id = ""
    __base_url = None

    def __init__(self, id):
        self.__id = id

        status_url = os.environ.get('STATUS_URL')
        if status_url == None:
            raise Unconfigured('No STATUS_URL environment variable found!')
        
        self.__base_url = os.path.join(status_url, self.__id)
        self.status(0, 'initializing')

    def status(self, progress, message=""):
        res = requests.patch(self.__base_url, data = {'id': self.__id, 'progress': progress, 'message': message})
        if res.status_code != 200:
            raise StatusFailed('Failed to update status: %s [%d]' % (res.status_code, res.text))

    def done(self, filename):
        self.status(100, 'uploading')

        files = {'file': ('result.json', open(filename, 'rb'), 'application/json', {'Expires': '0'})}
        res = requests.post(self.__base_url, files=files)
        if res.status_code != 200:
            raise StatusFailed('Failed to upload result: %s [%d]' % (res.status_code, res.text))

        self.status(100, 'done')

