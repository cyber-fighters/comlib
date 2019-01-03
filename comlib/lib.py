class BackyardCom:
    __id = ""

    def __init__(self, id):
        self.__id = id
        self.status(0, "initializing")

    def status(self, progress, message=""):
        print("sending progress %d" % progress)

    def done(self, filename):
        self.status(100, "uploading")
        print("sending data to whatever")
        self.status(100, "done")

