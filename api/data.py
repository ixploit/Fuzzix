import os.path
from api import LOGGER


class Wordlist:
    """represents a wordlist"""

    def __init__(self, name, path):
        """
        initializes a new wordlist
        attribute name: the name of the wordlist
        attribute path: the path to the wordlist, it is an error if the path isn't poiniting to an existing file
        return: None
        """
        #attribute check
        if not isinstance(name, str) or not isinstance(path, str):
            raise ValueError("expected type str for attributes name and path")
        if not os.path.isfile(path):
            raise ValueError("there is no file at " + path)

        self.name = name
        self.path = path
        self.content = []

        #read the wordlist into memory
        self.__read_from_file__(path)

    def __read_from_file__(self, path):
        """
        reads the content of a file into the memory; clears any old data.
        attribute path: the path of the wordlist as str
        return: None
        """
        self.content.clear()
        with open(path) as f:
            lines = f.readlines()
            self.content.extend(lines)

    def get_content(self):
        """
        returns the content of the wordlist
        return: The content of the wordlist
        """
        return self.content

    def get_name(self):
        """
        returns the name of the wordlist
        return: Name of the wordlist
        """
        return self.name


class File:
    """stores some general information about a spotted file"""

    def __init__(self, name, size):
        self.name = name
        self.size = size

    def get_name(self):
        """
        returns the name of the file
        return: Name of the file
        """
        return self.name

    def get_size(self):
        """
        returns the size of the file
        return: The size of the file
        """
        return self.size


NONE_FILE = File("", -1)


class Dir:
    """stores some general information about a spotted dir"""

    def __init__(self, dirName, rootDir):
        """
        creates a new Dir
        attribute dirName: the name of the new dir
        attribute rootDir: the root directory of the dir, can be None
        return: None
        """
        self.dirName = dirName
        self.childDirs = []
        self.spottedFiles = []
        self.rootDir = rootDir

    def __fileKnown__(self, name):
        """
        checks, weither a file with this name is already known
        attribute name: the name of the file to check
        return: True if the file is already known, otherwise False
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

        dir = Dir(name, self)
        self.childDirs.append(dir)
        return dir

    def getName(self):
        return self.dirName

    def appendPath(self, path, contentLength):
        """
        appends the spotted dirs and files to the dir
        attribute path: a path of type str containing dirs and probably a file, must already be extracted out of the URL and start with a '/'
        attribute contentLength: the length of the content, that has been retreived on the remote host with the given path
        return: None
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

            if pathName.startswith('/..'):
                if self.rootDir is None:
                    LOGGER.wtf('website browsing out of webroot')
                    return
                else:
                    pathName = path[3:]
                    self.rootDir.appendPath(pathName, contentLength)
                    return
            if pathName.startswith('/./'):
                pathName = path[3:]
                self.appendPath(pathName, contentLength)

            # continue recursively
            dir = self.__appendDir__(pathName)
            dir.appendPath(path[endIndex:], contentLength)

    def __printDirs__(self, path):
        path = path + self.dirName
        ostr = '[D] ' + path + '\n'
        for file in self.spottedFiles:
            ostr = ostr + '[F] ' + path + '/' + file.getName() + '\n'

        for dir in self.childDirs:
            ostr = ostr + dir.__printDirs__(path)

        return ostr

    def __str__(self):
        return self.__printDirs__('')


class __Protocol__:
    supportedProtocols = []

    def __init__(self, name, defaultPort):
        self.name = name
        self.defaultPort = defaultPort

    def getName(self):
        return self.name

    def getDefaultPort(self):
        return self.defaultPort

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

    @staticmethod
    def isValidProtocol(name):
        try:
            __Protocol__.getProtocol(name)
            return True
        except ValueError:
            return False


HTTPS = __Protocol__("HTTPS", 443)
HTTP = __Protocol__("HTTP", 80)

import re
from urllib.parse import urlparse, urljoin, urlunparse


class URL:
    """stores some general information about the used URL"""

    GOOD_STATUS = [200, 203, 302, 304, 401, 402, 403, 405, 407, 500, 502, 503]

    def __init__(self, url):
        """
        initializes the object with a given URL 
        attribute url: the url the object is meant to store
        return: None
        raises: ValueError if no valid URL is passed
        """
        if URL.isValidURL(url):
            # url is valid -> parsing

            urlparts = urlparse(url)

            #Protocol
            proto = urlparts.scheme
            if __Protocol__.isValidProtocol(proto):
                self.proto = proto
            else:
                # url is invalid
                raise ValueError("the given url " + url + " is not valid!")

            #host and port
            netloc = urlparts.netloc
            if ':' in netloc:
                self.host, self.port = netloc.split(':')
            else:
                self.host = netloc
                self.port = __Protocol__.getProtocol(
                    self.proto).getDefaultPort()

            #others
            self.path = urlparts.path
            self.query = urlparts.query
            self.params = urlparts.params
            self.fragments = urlparts.fragment
            self.username = urlparts.username
            self.password = urlparts.password

        else:
            # url is invalid
            raise ValueError("the given url " + url + " is not valid!")

    def getPort(self):
        return self.port

    def getHost(self):
        return self.host

    def getProto(self):
        return self.proto

    def getPath(self):
        return self.path

    def getParams(self):
        return self.params

    def getQuery(self):
        return self.query

    def getFragments(self):
        return self.fragments

    def getUsername(self):
        return self.username

    def getPassword(self):
        return self.password

    def __str__(self, **kwargs):
        return self.getURL()

    def getURL(self):
        return URL.buildURL(self.getProto(), self.getHost(), self.getPort(),
                            self.getPath(), self.getParams(), self.getQuery(),
                            self.getFragments())

    @staticmethod
    def buildPath(dir, file):
        """
        builds a path out of the given dir and the given file
        attribute dir: the specified dir as str
        attribute file: the specified file as str
        """
        path = dir + '/' + file
        path = path.replace('//', '/')
        return path

    @staticmethod
    def buildURL(proto, host, port, path, params, query, fragments):
        """
        builds an URL out of the given parameters
        attribute proto: the used protocol as str
        attribute host: the target host as str
        attribute port: the target port as int -> warning, currently not supported!
        attribute dir: the target dir as str, must start with a leading /
        attribute file: the target file as str
        return: the crafted URL of type str
        """
        netloc = host + ':' + str(port)
        urlparts = [proto, netloc, path, params, query, fragments]
        url = urlunparse(urlparts)
        return url

    @staticmethod
    def prettifyURL(rootURL, url):
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

        #guess it's a relative URL
        absURL = urljoin(rootURL.getURL(), url)

        try:
            return URL(absURL)
        except ValueError as _e:
            raise ValueError('couldn\'t prettify URL ' + url)

    @staticmethod
    def isValidURL(url):
        """
        checks weither a given URL is valid
        attribute url: the url to check as str
        return: True if URL is valid, otherwise False
        """
        urlparts = urlparse(url)
        proto = urlparts.scheme
        if urlparts.netloc and urlparts.scheme and __Protocol__.isValidProtocol(
                proto):
            return True
        return False


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
        if type(url) is not URL:
            raise ValueError('type URL required for attribute url')

        if self.getURL().getHost() == url.getHost():
            return False
        else:
            return True


import configparser


class __Settings__:
    """a class to store settings"""

    def __init__(self):
        self.config = {}

    def readConfig(self, path):
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
                self.config[section + "/" + key] = configFile[section][key]

    def writeAttribute(self, key, value):
        """
        writes an given attribute to the config file
        attribute key: the key for the attribute
        attribute value: the value to store
        return: None
        """
        self.config[key] = value

    def readAttribute(self, key, default):
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
            LOGGER.wtf("key " + key +
                       " couldn't be found, returning default value " +
                       default + " instead")
            return default

    def print_config(self):
        """
        prints the actual config
        return: None
        """
        for key in self.config:
            print(key + " : " + self.config[key])


Settings = __Settings__()
