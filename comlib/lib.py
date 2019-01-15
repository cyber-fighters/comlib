import os
import json
import requests
import tempfile

class ModuleNotFound(Exception):
    """Indicate that no such module is found."""
    pass


class ModuleNotReady(Exception):
    """Indicate that module was not completed yet."""
    pass


class DownloadFailed(Exception):
    """Indicate that the download of module results failed."""
    pass


class Unconfigured(Exception):
    """Indicate that the communication is unconfigured."""
    pass


class StatusFailed(Exception):
    """Indicate that the status communication failed."""
    pass


class BackyardCom:
    __id = ""
    __base_url = None
    __config = None

    def __init__(self):
        self.__id = os.environ.get('JOB_ID')
        if self.__id == None:
            raise Unconfigured('No JOB_ID environment variable found!')

        dependenciesStr = os.environ.get('DEPENDENCIES')
        if dependenciesStr == None:
            raise Unconfigured('No DEPENDENCIES environment variable found!')
        dependencies = json.loads(dependenciesStr)

        status_url = os.environ.get('STATUS_URL')
        if status_url == None:
            raise Unconfigured('No STATUS_URL environment variable found!')
        
        config = os.environ.get('PARAMETER')
        if config == None:
            raise Unconfigured('No PARAMETER environment variable found!')

        moduleInfoStr = os.environ.get('MODULE_RESULTS')
        if moduleInfoStr == None:
            raise Unconfigured('No MODULE_RESULTS environment variable found!')

        self.__moduleInfo = json.loads(moduleInfoStr)
        self.__config = json.loads(config)
        
        self.__base_url = os.path.join(status_url, self.__id)
        res = requests.patch(self.__base_url, data = {'progress': 0, 'message': 'initializing'})
        if res.status_code != 200:
            raise StatusFailed('Failed to update status: %d [%s]' % (res.status_code, res.text))

        self.module_results = {}
        for dep in dependencies:
            self.module_results[dep] = self.downloadModuleResultFile(dep)

    def downloadModuleResultFile(moduleName):
        module = self.__moduleInfo.get(moduleName)
        if module == None:
            raise ModuleNotFound('Failed to find module %s' % moduleName)
        if module['status'] != 'COMPLETED':
            raise ModuleNotReady('Failed to find result for module %s' % moduleName)
        res = requests.get(module['result'])
        if res.status_code != 200:
            raise DownloadFailed('Failed to download: %d [%s]' % (res.status_code, res.text))
        tmp = tempfile.NamedTemporaryFile(delete=False)
        with tmp as f:
            for chunk in res.iter_content(chunk_size=1024):
                f.write(chunk)
        return tmp.name

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
