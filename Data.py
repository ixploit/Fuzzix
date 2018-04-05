
class Dir:
    """stores some general information about a spotted dir"""

    def __init__(self, dirName, childDirs, spottedFiles):
        self.dirName = dirName
        self.childDirs = childDirs
        self.spottedFiles = spottedFiles

    def getName(self):
        return self.dirName



class File:
    """stores some general information about a spotted file"""

    def __init__(self,name,size):
        self.name = name
        self.size = size

    def getName(self):
        return self.name

NONE_FILE=File("",0)

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

    def __init__(self, url):

       if re.match('(http[s]?)://((?:[a-zA-Z]|[0-9]|[$\-_\.&+])+)(?::((?:[0-9]){1,5})){0,1}',url):
           #url is valid -> parsing
           
          matches = re.findall('(http[s]?)://((?:[a-zA-Z]|[0-9]|[$\-_\.&+])+)(?::((?:[0-9]){1,5})){0,1}',url)[0]
          self.proto = matches[0]

          if self.proto.lower() == HTTP.getName().lower():
                self.port = 80
          elif self.proto.lower() == HTTPS.getName().lower():
                self.port = 443
          else:
             raise ValueError('unsopported protocol given!')

          self.host = matches[1]

          if len(matches[2]) >= 1:
              self.port = matches[2]

       else:
           #url is invalid
           raise ValueError("the given url " + url + " is not valid")

    def getURL(self):
        return self.proto + "://" + self.host + ":" + str(self.port)
    
    def getPort(self):
        return self.port

    def getHost(self):
        return self.host

    def getProto(self):
        return self.proto

    def __str__(self, **kwargs):
        return self.getURL()

    @staticmethod
    def buildURL(proto,host,port,dir,file):
        return proto + "://" + host + ("/" + dir + "/" + file + ":" + str(port) if len((dir+file).replace('/',''))>0 else ":" +str(port) )        


class Host:

    """represents a webhost"""
    def __init__(self, url, rootDir):
        
        #typecheck
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

class Settings:

    def __init__(self, spider, fuzz, url, verifyCert ):
        if type(spider) is not bool:
            raise ValueError("attribute spider must be of type bool")
        if type(fuzz) is not bool:
            raise ValueError("attribute fuzz must be of type bool")
        if type(url) is not str:
            raise ValueError("attribute url must be of type str")
        if type(verifyCert) is not bool:
            raise ValueError("attribute verifyCert must be of type bool")
        
        try:
            self.url = URL(url)
        except ValueError as e:
            raise e
        self.spider = spider
        self.fuzz = fuzz
        self.verifyCert = verifyCert

    def getSpider(self):
        return self.spider
    
    def getFuzz(self):
        return self.fuzz

    def getURL(self):
        return self.url

    def getVerifyCert(self):
        return self.verifyCert

    """warning, not yet supported!"""
    def getRootDir(self):
        """
        return: returns an empty root dir
        """
        return Dir("",[],[])
