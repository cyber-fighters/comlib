"""Class for managing data exchange between pods."""
import json
import os
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
    """Class for managing data exchange between pods."""

    __id = ""
    __base_url = None
    __config = None
    __debug = False

    def __init__(self):
        """Initialize the class instance."""
        self.__debug = bool(os.environ.get('DEBUG_MODE', False))

        self.__id = os.environ.get('JOB_ID')
        if self.__id is None:
            raise Unconfigured('No JOB_ID environment variable found!')

        dependencies_str = os.environ.get('DEPENDENCIES')
        if dependencies_str is None:
            raise Unconfigured('No DEPENDENCIES environment variable found!')
        dependencies = json.loads(dependencies_str)

        status_url = os.environ.get('STATUS_URL')
        if status_url is None:
            raise Unconfigured('No STATUS_URL environment variable found!')

        config = os.environ.get('PARAMETER')
        if config is None:
            raise Unconfigured('No PARAMETER environment variable found!')

        module_info_str = os.environ.get('MODULE_RESULTS')
        if module_info_str is None:
            raise Unconfigured('No MODULE_RESULTS environment variable found!')

        self.__moduleInfo = json.loads(module_info_str)
        self.__config = json.loads(config)

        self.__base_url = os.path.join(status_url, self.__id)
        if not self.__debug:
            res = requests.patch(self.__base_url, data={'progress': 0, 'message': 'initializing'})
            if res.status_code != 200:
                raise StatusFailed('Failed to update status: %d [%s]' % (res.status_code, res.text))

        self.module_results = {}
        for dep in dependencies:
            self.module_results[dep] = self.download_module_result_file(dep)

    def download_module_result_file(self, module_name):
        """Get the result file name and download it if necessary."""
        module = self.__moduleInfo.get(module_name)
        if module is None:
            raise ModuleNotFound('Failed to find module %s' % module_name)
        if module['status'] != 'COMPLETED':
            raise ModuleNotReady('Failed to find result for module %s' % module_name)
        result_ref = module['result']
        if self.__debug:
            return result_ref
        res = requests.get(result_ref)
        if res.status_code != 200:
            raise DownloadFailed('Failed to download: %d [%s]' % (res.status_code, res.text))
        tmp = tempfile.NamedTemporaryFile(delete=False)
        with tmp as f:
            for chunk in res.iter_content(chunk_size=1024):
                f.write(chunk)
        return tmp.name

    def is_debug(self):
        """Return environmental variable for debug mode."""
        return self.__debug

    def get_unique_module_string(self):
        """Get a unique descriptor of this instance. Can be used for collision-free filenames."""
        return self.__id.replace("/", "_")

    def get(self, key):
        """Get value from customer dictionary."""
        return self.__config[key] or None

    def status(self, progress, message=""):
        """Post a job completion status."""
        if self.__debug:
            return
        res = requests.patch(self.__base_url, data={'progress': progress, 'message': message})
        if res.status_code != 200:
            raise StatusFailed('Failed to update status: %d [%s]' % (res.status_code, res.text))

    def done(self, filename):
        """Finish up and register result file name for later modules."""
        if self.__debug:
            return
        self.status(100, 'uploading')

        files = {'file': ('result.json', open(filename, 'rb'), 'application/json', {'Expires': '0'})}
        res = requests.post(os.path.join(self.__base_url, 'result'), files=files)
        if res.status_code != 200:
            raise StatusFailed('Failed to upload result: %d [%s]' % (res.status_code, res.text))
