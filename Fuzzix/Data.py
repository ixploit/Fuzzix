
#logger for this file
from coloredlogger import ColoredLogger
data_logger = ColoredLogger(name="Data")


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
        return self.getName()

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
    urlRegex = r"(http[s]?)://((?:[a-zA-Z]|[0-9]|[$\-_\.&+])+)((?:[a-zA-Z]|[0-9]|[$\?=\-_\.\/&+#])*)(?::((?:[0-9]){1,5})){0,1}"

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
        attribute port: the target port as int -> warning, currently not supported!
        attribute dir: the target dir as str
        attribute file: the target file as str
        return: the crafted URL of type str
        """
        if dir.startswith('/'):
            dir = dir[1:]
        if dir.endswith('/'):
            dir = dir[:-1]
        file = file.replace('/','')
        
        path = ''
        if (dir+file).endswith('/'):
            if not file:
                path = '/' + dir[:-1]
            else:
                if not dir:
                    path = '/' + file[:-1]
                else:
                    path = '/' + dir + '/' + file[:-1]
        else:
            if not dir:
                if not file:
                    path = ''
                else:
                    path = '/' + file
            else:
                if not file:
                    path = '/' + dir
                else:
                    path = '/' + dir + '/' + file
        
        return proto + "://" + host + path

    @staticmethod
    def prettifyURL(host, rootURL, url):
        """
        prettifies a given url
        attribute host: an instance of the root host
        attribute rootURL: the url of the file, where the given url has been discoverd as URL
        attribute url: a str containing the URL wich is supposed to be prettified
        return: the prettified URL as URL
        """
        #check weither URL is already absolute and valid
        if URL.isValidURL(url):
            return URL(url)

        if url.startswith('//'):
            url = url.replace('//', host.getURL().getProto() + "://", 1)
        
        if url.startswith('#'):
            url = rootURL.getURL() + url

        relativeURLRegex = r"^([\/|\.\/|\.\.\/]+.*)"
        relativeToRootURLRegex = r"^(.*[\/|\.\/|\.\.\/]+.*)"
        if re.match(relativeURLRegex, url):
            url = URL.buildURL(rootURL.getProto(), rootURL.getHost(), rootURL.getPort(), rootURL.getPath(), url)
        else:
            if re.match(relativeToRootURLRegex,url):
                url = URL.buildURL(rootURL.getProto(),rootURL.getHost(),rootURL.getPort(),url,"")
        try:
            return URL(url)
        except ValueError:
            raise ValueError('couldn\'t prettify URL ' + url + ' found in ' + rootURL.getURL() + ' it is not valid')

    @staticmethod
    def isValidURL(url):
        """
        checks weither a given URL is valid
        attribute url: the url to check as str
        return: True if URL is valid, otherwise False
        """
        return re.match(URL.urlRegex,url)

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

class __Settings__:
    """a class to store settings"""

    def __init__(self):
        self.config = {}
        

    def readConfig(self,path):
        """
        reads the config file located on the given locaton using configparser
        attribute path: the path to the config file as str
        raises: ValueError, if no config settings could be found at the given location
        return: None
        """
        configFile = configparser.ConfigParser()
        configFile.read(path)
        if len(configFile.sections()) <= 0:
            raise ValueError("given config empty or not existend")
        for section in configFile.sections():
            for key in configFile[section]:
                self.config[section + "/" + key]=configFile[section][key]
        

    def writeAttribute(self,key,value):
        """
        writes an given attribute to the config file
        attribute key: the key for the attribute
        attribute value: the value to store
        return: None
        """
        self.config[key] = value

    def readAttribute(self,key,default):
        """
        reads an attribute from the config
        attribute key: the key to read
        attribute default: the default value, which will be returned, if the key couldn't be found in the config
        return: either the default-value or the value of the key in the config
        """
        if key in self.config:
            return self.config[key]
        else:
            #logging waring
            data_logger.wtf("key " + key + " couldn't be found, returning default value " + default + " instead")
            return default
    
    def printConfig(self):
        for key in self.config:
            print(key + " : " + self.config[key])
Settings = __Settings__()
