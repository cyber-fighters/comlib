import os
import json
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
    __config = None

    def __init__(self):
        self.__id = os.environ.get('JOB_ID')
        if self.__id == None:
            raise Unconfigured('No JOB_ID environment variable found!')

        status_url = os.environ.get('STATUS_URL')
        if status_url == None:
            raise Unconfigured('No STATUS_URL environment variable found!')
        
        config = os.environ.get('PARAMETER')
        if config == None:
            raise Unconfigured('No PARAMETER environment variable found!')

        self.__config = json.loads(config)
        
        self.__base_url = os.path.join(status_url, self.__id)
        res = requests.post(self.__base_url, data = {'progress': 0, 'message': 'initializing'})
        if res.status_code != 200:
            raise StatusFailed('Failed to update status: %d [%s]' % (res.status_code, res.text))

    def get(self, key):
        return __config[key] or None

    def status(self, progress, message=""):
        res = requests.patch(self.__base_url, data = {'progress': progress, 'message': message})
        if res.status_code != 200:
            raise StatusFailed('Failed to update status: %d [%s]' % (res.status_code, res.text))

    def done(self, filename):
        self.status(100, 'uploading')

        files = {'file': ('result.json', open(filename, 'rb'), 'application/json', {'Expires': '0'})}
        res = requests.post(os.path.join(self.__base_url, 'result'), files=files)
        if res.status_code != 200:
            raise StatusFailed('Failed to upload result: %d [%s]' % (res.status_code, res.text))
