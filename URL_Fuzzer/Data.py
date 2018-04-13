class File:
    """stores some general information about a spotted file"""

    def __init__(self, name, size):
        self.name = name
        self.size = size

    def getName(self):
        return self.name


NONE_FILE = File("", 0)


class Dir:
    """stores some general information about a spotted dir"""

    def __init__(self, dirName, childDirs, spottedFiles):
        self.dirName = dirName
        self.childDirs = childDirs
        self.spottedFiles = spottedFiles

    def __fileKnown__(self, name):
        """
        checks, weither a file with this name is already known
        attribute name: the name of the file to check
        return: true if the file is already known, otherwise False
        """
        for file in self.spottedFiles:
            if file.getName() == name:
                return True
        return False

    def __appendFile__(self, name, fileSize):
        """
        appends a file with given name to self.spottedFiles. Will not add a file twice.
        attribute name: the name of the spotted file
        attribute fileSize: the size of the given file
        """
        if self.__fileKnown__(name):
            return

        file = File(name, fileSize)
        self.spottedFiles.append(file)

    def __dirKnown__(self, name):
        """
        checks, weither a dir with this name is already known
        attribute name: the name of the dir to check
        return: the dir if already known, otherwise None
        """
        for dir in self.childDirs:
            if dir.getName() == name:
                return dir
        return None

    def __appendDir__(self, name):
        """
        appends a file with given name to self.spottedFiles. Will not add a file twice.
        attribute name: the name of the spotted file
        attribute fileSize: the size of the given file
        return: an instance of an existing dir with the name, or an instance of the newly created dir
        """
        alKnwonDir = self.__dirKnown__(name)
        if alKnwonDir is not None:
            return alKnwonDir

        dir = Dir(name, [], [])
        self.childDirs.append(dir)
        return dir

    def getName(self):
        return self.dirName

    def appendPath(self, path, contentLength):
        """
        appends the spotted dirs and files to the dir
        attribute path: a path of type str containing dirs and probably a file, must already be extracted out of the URL and start with a '/'
        attribute contentLength: the length of the content, that has been retreived on the remote host with the given path
        """
        startIndex = path.find('/')
        if startIndex == -1:
            # not valid
            raise ValueError('invalid path given!', path)

        endIndex = path.find('/', startIndex + 1)
        if endIndex == -1:
            # not a dir but a file
            pathName = path[startIndex + 1:]
            self.__appendFile__(pathName, contentLength)
        else:
            # content of type dir
            pathName = path[startIndex:endIndex]

            # continue recursively
            dir = self.__appendDir__(pathName)
            dir.appendPath(path[endIndex:], contentLength)

    def __printDirs__(self, str, indentation):
        for dir in self.childDirs:
            print("[D]" + (" " * indentation) + "`-" + dir.getName())
            dir.__printDirs__(str, indentation + 1)
        for file in self.spottedFiles:
            print("[F]" + ("  " * indentation) + "`-" + file.getName())

        return str

    def printDirs(self):
        return self.__printDirs__("", 0)


class __Protocol__:
    supportedProtocols = []

    def __init__(self, name):
        self.name = name

    def getName(self):
        return self.name

    def __str__(self):
        return getName()

    @staticmethod
    def getProtocol(name):
        if name.lower() == "https":
            return HTTPS
        elif name.lower() == "http":
            return HTTP
        else:
            raise ValueError("unsopported protocol")


HTTPS = __Protocol__("HTTPS")
HTTP = __Protocol__("HTTP")

import re


class URL:
    """stores some general information about the used URL"""

    GOOD_STATUS = [200, 203, 302, 304, 401, 402, 403, 405, 407, 500, 502, 503]
    urlRegex = r"(http[s]?)://((?:[a-zA-Z]|[0-9]|[$\-_\.&+])+)((?:[a-zA-Z]|[0-9]|[$\?=\-_\.\/&+])*)(?::((?:[0-9]){1,5})){0,1}"

    def __init__(self, url):
        """
        initializes the object with a given URL 
        attribute url: the url the object is meant to store
        return: None
        raises: ValueError if no valid URL is passed
        """
        if re.match(URL.urlRegex, url):
            # url is valid -> parsing

            matches = re.findall(URL.urlRegex, url)[0]
            self.proto = matches[0]

            if self.proto.lower() == HTTP.getName().lower():
                self.port = 80
            elif self.proto.lower() == HTTPS.getName().lower():
                self.port = 443
            else:
                raise ValueError('unsopported protocol given!')

            self.host = matches[1]
            self.path = matches[2]
            if len(matches[3]) >= 1:
                self.port = matches[3]

        else:
            # url is invalid
            raise ValueError("the given url " + url + " is not valid!")

    def getURL(self):
        return URL.buildURL(self.getProto(), self.getHost(), self.getPort(), self.getPath(), "")

    def getPort(self):
        return self.port

    def getHost(self):
        return self.host

    def getProto(self):
        return self.proto

    def getPath(self):
        return self.path

    def __str__(self, **kwargs):
        return self.getURL()

    @staticmethod
    def buildURL(proto, host, port, dir, file):
        """
        builds an URL out of the given parameters
        attribute proto: the used protocol as str
        attribute host: the target host as str
        attribute port: the target port as int
        attribute dir: the target dir as str
        attribute file: the target file as str
        return: the crafted URL of type str
        """
        return proto + "://" + host + (
            "/" + dir + "/" + file + ":" + str(port) if len((dir + file).replace('/', '')) > 0 else ":" + str(port))

    @staticmethod
    def prettifyURL(host, rootURL, url):
        """
        prettifies a given url
        attribute host: an instance of the root host
        attribute rootURL: the url of the file, where the given url has been discoverd as URL
        attribute url: a str containing the URL wich is supposed to be prettified
        return: the prettified URL as URL
        """
        if re.match(URL.urlRegex, url):
            return URL(url)

        if url.startswith('//'):
            url = url.replace('//', host.getURL().getProto() + "://", 1)

        relativeURLRegex = r"([\/|\.\/|\.\.\/]*)\b([-a-zA-Z0-9@:%_\+.~#&//=]*)(?:[\/|.])([-a-zA-Z0-9@:%_\+.~#&//=]*)\?{0,1}(?:[-a-zA-Z0-9@:%_\+.~#&//=]*)"
        if re.match(relativeURLRegex, url):
            url = URL.buildURL(rootURL.getProto(), rootURL.getHost(), rootURL.getPort(), rootURL.getPath() + url, "")
        try:
            return URL(url)
        except ValueError as e:
            raise ValueError('couldn\'t prettify URL', url, ' it is not valid')


class Host:
    """represents a webhost"""

    def __init__(self, url, rootDir):

        # typecheck
        if type(url) is not URL:
            raise ValueError("wrong type for attribute url")
        if type(rootDir) is not Dir:
            raise ValueError("wrong type for attribute rootDir")

        self.url = url
        self.rootDir = rootDir

    def getURL(self):
        return self.url

    def getRootdir(self):
        return self.rootDir

    def isExternal(self, url):
        """
        checks weither a given url is referencing an external host
        attribute url: the url to check as URL
        return: True if the url is pointing on an external host, otherwise False
        """
        try:
            if self.getURL().getHost() == url.getHost():
                return False
            else:
                return True

        except ValueError as e:
            raise ValueError('invalid url given', e)

import configparser

class Settings:

    def __init__(self, spider, fuzz, url, verifyCert, threads, recursion):
        if type(spider) is not bool:
            raise ValueError("attribute spider must be of type bool")
        if type(fuzz) is not bool:
            raise ValueError("attribute fuzz must be of type bool")
        if type(url) is not str:
            raise ValueError("attribute url must be of type str")
        if type(verifyCert) is not bool:
            raise ValueError("attribute verifyCert must be of type bool")
        if type(threads) is not int:
            raise ValueError("attribute threads must be of type int")
        if type(recursion) is not int:
            raise ValueError("attribute recursion must be of type int")

        try:
            self.url = URL(url)
        except ValueError as e:
            raise e
        self.spider = spider
        self.fuzz = fuzz
        self.verifyCert = verifyCert
        self.threads = threads
        self.recursion = recursion

    def readConfig(self,path):
        """
        reads the config file located on the given locaton
        attribute path: the path to the config file as str
        raises: ValueError, if no config settings could be found at the given location
        return: None
        """
        config = configparser.ConfigParser()
        config.read(path)
        if config.sections() <= 0:
            raise ValueError("given config empty or not existend")
        
        

    def getSpider(self):
        return self.spider

    def getFuzz(self):
        return self.fuzz

    def getURL(self):
        return self.url

    def getVerifyCert(self):
        return self.verifyCert

    def getThreads(self):
        return self.threads

    def getRecursion(self):
        return self.recursion

    """warning, not yet supported!"""

    def getRootDir(self):
        """
        return: returns an empty root dir
        """
        return Dir("", [], [])
